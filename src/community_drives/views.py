from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from django.db.models.functions import Coalesce
from database.models import (
    CommunityDrive,
    DriveOrganization,
    User,
    Organization,
)
from .forms import AddCommunityDriveForm
from django.http import JsonResponse
import json
import base64


@login_required
def get_drive_list(request):
    user = User.objects.get(email=request.user.email)
    organizations = Organization.objects.filter(organizationadmin__user=user)

    if request.method == "POST":
        form = AddCommunityDriveForm(request.POST, user=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Community drive successfully created.")
            return redirect("/community_drives")
    else:
        form = AddCommunityDriveForm(user=user)

    drives = (
        CommunityDrive.objects.filter(active=True)
        .annotate(
            meal_progress=Coalesce(Sum("driveorganization__meal_pledge"), 0),
            volunteer_progress=Coalesce(Sum("driveorganization__volunteer_pledge"), 0),
        )
        .order_by("-end_date")
    )

    drive_orgs = DriveOrganization.objects.filter(drive__in=drives)
    my_drives = drives.filter(lead_organization_id__in=organizations)

    return render(
        request,
        "community_drives/list.html",
        {
            "form": form,
            "drives": drives,
            "drive_orgs": drive_orgs,
            "my_drives": my_drives,
        },
    )


def drive_dashboard(request, drive_id):
    drive = get_object_or_404(CommunityDrive, pk=drive_id)
    participating_organizations = DriveOrganization.objects.filter(drive=drive)
    active_user_orgs = request.user.organizationadmin_set.filter(
        organization__active=True
    )
    context = {
        "drive": drive,
        "participating_organizations": participating_organizations,
        "active_user_orgs": active_user_orgs,
    }
    return render(request, "community_drives/drive_dashboard.html", context)


def contribute_to_drive(request, drive_id):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            meals = data.get("meals")
            volunteers = data.get("volunteers")
            donor_organization_id = data.get("donor_organization")

            if int(meals) == 0 and int(volunteers) == 0:
                error_message = "Meals and volunteers both cannot be 0!"
                return JsonResponse({"success": False, "error": error_message})

            # Get the drive instance
            drive = get_object_or_404(CommunityDrive, drive_id=drive_id)

            # Get the donor organization
            donor_organization = get_object_or_404(
                Organization, organization_id=donor_organization_id
            )

            # Create or update the DriveOrganization record with the contribution
            drive_org, created = DriveOrganization.objects.get_or_create(
                drive=drive, organization=donor_organization
            )

            target_meals = (
                drive.meal_target
            )  # Assuming the drive has a 'target_meals' field
            target_volunteers = drive.volunteer_target

            # Check if the updated pledge exceeds the target
            total_meals_pledged = (
                DriveOrganization.objects.filter(drive=drive).aggregate(
                    total_meals=Sum("meal_pledge")
                )["total_meals"]
                or 0
            )

            # Calculate the sum of all existing volunteer pledges for the drive
            total_volunteers_pledged = (
                DriveOrganization.objects.filter(drive=drive).aggregate(
                    total_volunteers=Sum("volunteer_pledge")
                )["total_volunteers"]
                or 0
            )

            new_meal_pledge = total_meals_pledged + int(meals)
            new_volunteer_pledge = total_volunteers_pledged + int(volunteers)

            if new_meal_pledge > target_meals:
                max_contributable_meals = target_meals - total_meals_pledged
                error_message = f"Meal contribution exceeds target meals. \
                    Maximum of {max_contributable_meals} meal(s) can be contributed right now!"
                return JsonResponse({"success": False, "error": error_message})

            if new_volunteer_pledge > target_volunteers:
                max_contributable_volunteers = (
                    target_volunteers - total_volunteers_pledged
                )
                error_message = f"Volunteer contribution exceeds target volunteers. \
                    Maximum of {max_contributable_volunteers} volunteer(s) can be contributed right now!"
                return JsonResponse({"success": False, "error": error_message})

            # Update the DriveOrganization with the new pledges
            drive_org.meal_pledge = drive_org.meal_pledge + int(meals)
            drive_org.volunteer_pledge = drive_org.volunteer_pledge + int(volunteers)
            drive_org.save()

            # Fetch all the DriveOrganization records for the drive
            drive_organizations = DriveOrganization.objects.filter(drive=drive)

            # Prepare the response data, including updated table data
            contributions = [
                {
                    "organization_name": org.organization.organization_name,
                    "meals_contributed": org.meal_pledge,
                    "volunteers_contributed": org.volunteer_pledge,
                }
                for org in drive_organizations
            ]

            return JsonResponse({"success": True, "contributions": contributions})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "error": "Invalid request"})


@login_required
def upload_drive_image(request):
    if request.method == "POST":
        drive_id = request.POST.get("drive_id")
        image = request.FILES.get("image")

        if not drive_id or not image:
            return JsonResponse({"success": False, "error": "Invalid data."})

        try:
            # Convert image to base64 string
            image_data = base64.b64encode(image.read()).decode("utf-8")

            # Update the donation object with the image string
            drive = CommunityDrive.objects.get(drive_id=drive_id)
            drive.image_data = (
                image_data  # Assuming `image_data` is a TextField in the model
            )
            drive.save()

            return JsonResponse({"success": True, "image_data": image_data})
        except CommunityDrive.DoesNotExist:
            return JsonResponse(
                {"success": False, "error": "Community Drive not found."}
            )
    return JsonResponse({"success": False, "error": "Invalid request method."})


@login_required
def delete_drive_image(request):
    if request.method == "POST":
        drive_id = request.POST.get("drive_id")

        if not drive_id:
            return JsonResponse({"success": False, "error": "Invalid data."})

        try:
            drive = CommunityDrive.objects.get(drive_id=drive_id)
            drive.image_data = None
            drive.save()

            return JsonResponse({"success": True})
        except CommunityDrive.DoesNotExist:
            return JsonResponse(
                {"success": False, "error": "Community Drive not found."}
            )
    return JsonResponse({"success": False, "error": "Invalid request method."})
