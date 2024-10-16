from django.shortcuts import render, redirect  # noqa
from database.models import Organization, OrganizationAdmin, User
from django.contrib import messages
from .forms import AddOrganizationForm
from django.contrib.auth.decorators import login_required


@login_required
def add_organization(request):
    if request.method == "POST":
        form = AddOrganizationForm(request.POST)
        if form.is_valid():
            organization = form.save()
            org_user = User.objects.get(email=request.user.email)
            OrganizationAdmin.objects.create(user=org_user, organization=organization)
            messages.success(request, "Organization successfully added.")
            return redirect("/")
    else:
        form = AddOrganizationForm()
    return render(request, "add_organization.html", {"form": form})


@login_required
def get_org_list(request):

    if request.method == "POST":
        form = AddOrganizationForm(request.POST)
        if form.is_valid():
            organization = form.save()
            org_user = User.objects.get(email=request.user.email)
            OrganizationAdmin.objects.create(user=org_user, organization=organization)
            messages.success(request, "Organization successfully added.")
            return redirect("/donor_dashboard")
    else:
        form = AddOrganizationForm()

    org_user = User.objects.get(email=request.user.email)
    organization_admin_list = OrganizationAdmin.objects.filter(user=org_user)
    org_list = []

    for organization_admin in organization_admin_list:
        organization = organization_admin.organization
        org_list.append(
            {
                "org_id": organization.organization_id,
                "org_name": organization.organization_name,
                "org_type": organization.type,
                "org_address": organization.address,
                "org_zipcode": organization.zipcode,
                "org_email": organization.email,
                "org_website": organization.website,
                "org_contact_number": organization.contact_number,
            }
        )

    return render(
        request, "donor_dashboard/list.html", {"org_list": org_list, "form": form}
    )


def manage_organization(request, organization_id):
    # Fetch the organization using the organization_id
    organization = Organization.objects.get(organization_id=organization_id)

    return render(
        request,
        "donor_dashboard/manage_organization.html",
        {"organization": organization},
    )
