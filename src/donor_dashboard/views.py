from django.shortcuts import render  # noqa
from database.models import OrganizationAdmin, Organization
from django.contrib.auth.decorators import login_required

# Create your views here.


@login_required
def get_org_list(request):

    user_email = request.user.email
    organization_admin_list = OrganizationAdmin.objects.filter(user_email=user_email)

    org_list = []

    for organization in organization_admin_list:
        organization_details = Organization.objects.get(
            organization_id=organization.organization_id
        )
        org_list.append(
            {
                "org_name": organization_details.organization_name,
                "org_type": organization_details.type,
                "org_address": organization_details.address,
                "org_zipcode": organization_details.zipcode,
                "org_email": organization_details.email,
                "org_website": organization_details.website,
                "org_contact_number": organization_details.contact_number,
            }
        )

    return render(request, "donor_dashboard/list.html", {"org_list": org_list})
