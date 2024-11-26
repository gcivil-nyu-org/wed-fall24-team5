from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.db.models.functions import Coalesce
from database.models import (
    CommunityDrive,
    DriveOrganization,
    User,
    Organization,
)


@login_required
def get_drive_list(request):
    user = User.objects.get(email=request.user.email)
    organizations = Organization.objects.filter(organizationadmin__user=user)

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
            "drives": drives,
            "drive_orgs": drive_orgs,
            "my_drives": my_drives,
        },
    )
