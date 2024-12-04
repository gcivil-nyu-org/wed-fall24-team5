from datetime import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Q
from django.db.models.functions import Coalesce
from database.models import CommunityDrive, DriveOrganization, User, Organization
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
    drives = CommunityDrive.objects.annotate(
        meal_progress=Coalesce(Sum("driveorganization__meal_pledge"), 0),
        volunteer_progress=Coalesce(Sum("driveorganization__volunteer_pledge"), 0),
    )
    drive = get_object_or_404(drives, pk=drive_id)
    participating_organizations = DriveOrganization.objects.filter(drive=drive)
    participating_organizations = DriveOrganization.objects.filter(drive=drive).filter(
        Q(meal_pledge__gte=1) | Q(volunteer_pledge__gte=1)
    )
    active_user_orgs = request.user.organizationadmin_set.filter(
        organization__active=True
    )
    can_edit = any(
        org_admin.organization_id == drive.lead_organization.organization_id
        for org_admin in active_user_orgs
    )
    meals_percentage = (
        (drive.meal_progress / drive.meal_target) * 100 if drive.meal_progress else 0
    )
    volunteers_percentage = (
        (drive.volunteer_progress / drive.volunteer_target) * 100
        if drive.volunteer_progress
        else 0
    )

    context = {
        "drive": drive,
        "meals_percentage": meals_percentage,
        "volunteers_percentage": volunteers_percentage,
        "participating_organizations": participating_organizations,
        "active_user_orgs": active_user_orgs,
        "can_edit": can_edit,
    }
    return render(request, "community_drives/drive_dashboard.html", context)


def fetch_contributions(request, drive_id):
    if request.method == "GET":
        drive = get_object_or_404(CommunityDrive, pk=drive_id)

        # Fetch all the DriveOrganization records for the drive
        drive_organizations = DriveOrganization.objects.filter(drive=drive).filter(
            Q(meal_pledge__gte=1) | Q(volunteer_pledge__gte=1)
        )
        # Prepare the response data, including updated table data
        contributions = [
            {
                "organization_name": org.organization.organization_name,
                "meals_contributed": org.meal_pledge,
                "volunteers_contributed": org.volunteer_pledge,
                "created_at": org.created_at,
            }
            for org in drive_organizations
        ]

        return JsonResponse({"contributions": contributions})


def contribute_to_drive(request, drive_id):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            meals = data.get("meals")
            volunteers = data.get("volunteers")
            donor_organization_id = data.get("donor_organization")

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

            if int(meals) == 0 and int(volunteers) == 0:
                error_message = "Meals and volunteers both cannot be 0! Click on 'Delete' to take back your contribution"
                return JsonResponse({"success": False, "error": error_message})

            # Update the DriveOrganization with the new pledges
            drive_org.meal_pledge = int(meals)
            drive_org.volunteer_pledge = int(volunteers)
            drive_org.save()

            # Fetch all the DriveOrganization records for the drive
            drive_organizations = DriveOrganization.objects.filter(drive=drive).filter(
                Q(meal_pledge__gte=1) | Q(volunteer_pledge__gte=1)
            )

            # Prepare the response data, including updated table data
            contributions = [
                {
                    "organization_name": org.organization.organization_name,
                    "meals_contributed": org.meal_pledge,
                    "volunteers_contributed": org.volunteer_pledge,
                    "created_at": org.created_at,
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


def get_participation_details(request, organization_id, drive_id):
    if request.method == "GET":
        # Fetch details based on organization and drive
        drive_org = get_object_or_404(
            DriveOrganization,
            organization__organization_id=organization_id,
            drive_id=drive_id,
        )
        data = {
            "meals": drive_org.meal_pledge,
            "volunteers": drive_org.volunteer_pledge,
        }
        return JsonResponse(data)


def delete_participation(request, organization_id, drive_id):
    if request.method == "DELETE":
        try:
            participation = DriveOrganization.objects.get(
                organization_id=organization_id, drive_id=drive_id
            )
            participation.delete()

            # Fetch all the DriveOrganization records for the drive
            drive_organizations = DriveOrganization.objects.filter(
                drive_id=drive_id
            ).filter(Q(meal_pledge__gte=1) | Q(volunteer_pledge__gte=1))

            # Prepare the response data, including updated table data
            contributions = [
                {
                    "organization_name": org.organization.organization_name,
                    "meals_contributed": org.meal_pledge,
                    "volunteers_contributed": org.volunteer_pledge,
                    "created_at": org.created_at,
                }
                for org in drive_organizations
            ]

            return JsonResponse({"success": True, "contributions": contributions})
        except DriveOrganization.DoesNotExist:
            return JsonResponse({"success": False, "error": "Participation not found"})
    return JsonResponse(
        {"success": False, "error": "Invalid request method"}, status=405
    )


def delete_drive(request, drive_id):
    if request.method == "POST":
        try:
            drive = CommunityDrive.objects.get(drive_id=drive_id)
            drive.active = False
            drive.save()
            for drive_org in DriveOrganization.objects.filter(drive=drive):
                drive_org.meal_pledge = 0
                drive_org.volunteer_pledge = 0
                drive_org.modified_at = timezone.now()
                drive_org.save()

            messages.success(
                request, f"Community drive '{drive}' successfully deleted."
            )
            return redirect("/community_drives")
        except CommunityDrive.DoesNotExist:
            messages.error(
                request, "Failed to delete community drive. Couldn't find the drive."
            )
            return redirect("/community_drives")
