from django.shortcuts import render, redirect, get_object_or_404  # noqa
from database.models import Organization, OrganizationAdmin, User, Donation, Order
from django.contrib import messages
from donor_dashboard.forms import AddOrganizationForm
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .helpers import validate_donation


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
    active_org_list = []
    inactive_org_list = []

    for organization_admin in organization_admin_list:
        organization = organization_admin.organization
        obj = {
            "org_id": organization.organization_id,
            "org_name": organization.organization_name,
            "org_type": organization.type,
            "org_address": organization.address,
            "org_zipcode": organization.zipcode,
            "org_email": organization.email,
            "org_website": organization.website,
            "org_contact_number": organization.contact_number,
        }
        if organization.active:
            active_org_list.append(obj)
        else:
            inactive_org_list.append(obj)

    return render(
        request,
        "donor_dashboard/list.html",
        {
            "active_org_list": active_org_list,
            "inactive_org_list": inactive_org_list,
            "form": form,
        },
    )


@login_required
def manage_organization(request, organization_id):
    # Fetch the organization using the organization_id
    organization = Organization.objects.get(organization_id=organization_id)
    donations = Donation.objects.filter(organization=organization)
    status = organization.active
    return render(
        request,
        "donor_dashboard/manage_organization.html",
        {"organization": organization, "donations": donations, "status": status},
    )


@login_required
def organization_details(request, organization_id):

    organization = Organization.objects.get(organization_id=organization_id)

    if request.method == "POST":
        form = AddOrganizationForm(request.POST, instance=organization)
        if form.is_valid():
            organization = form.save()
            messages.success(request, "Organization Details Updated Succesfully.")
            return redirect(
                "donor_dashboard:manage_organization", organization_id=organization_id
            )
    else:
        form = AddOrganizationForm(instance=organization)

    return render(
        request,
        "donor_dashboard/organization_details.html",
        {"organization": organization, "form": form},
    )


@login_required
def delete_organization(request, organization_id):
    if request.method == "POST":
        organization = Organization.objects.get(organization_id=organization_id)

        # Set the active field in Donations to False for soft delete
        donations = Donation.objects.filter(organization=organization)
        for donation in donations:

            # Set the active field in Orders to False for soft delete
            orders = Order.objects.filter(donation=donation)
            for order in orders:
                order.active = False
                order.save()

            donation.active = False
            donation.save()

        # Set the active field in Organization to False for soft delete
        organization.active = False
        organization.save()

        organization_name = organization.organization_name

        messages.success(
            request, f'Organization "{organization_name}" made inactive successfully.'
        )
        return redirect("donor_dashboard:org_list")
    return redirect("donor_dashboard:org_list")


@login_required
def add_donation(request):
    if request.method == "POST":
        food_item = request.POST["food_item"]
        quantity = request.POST.get("quantity")
        pickup_by = request.POST.get("pickup_by")
        organization_id = request.POST.get("organization")

        # Validate Donation
        errors = validate_donation(food_item, quantity, pickup_by, organization_id)

        if errors:
            for error in errors:
                messages.warning(request, error)
            return redirect(
                "donor_dashboard:manage_organization", organization_id=organization_id
            )

        # Create new donation if all validations pass
        Donation.objects.create(
            food_item=food_item,
            quantity=int(quantity),
            pickup_by=timezone.datetime.strptime(pickup_by, "%Y-%m-%d").date(),
            organization_id=organization_id,
        )

        messages.success(request, f"Donation: {food_item} added successfully!")
        return redirect(
            "donor_dashboard:manage_organization", organization_id=organization_id
        )

    messages.warning(request, "Invalid Add Donation Request!")
    return redirect("/")


@login_required
def modify_donation(request, donation_id):
    donation = get_object_or_404(Donation, donation_id=donation_id)
    if request.method == "POST":
        food_item = request.POST["food_item"]
        quantity = request.POST.get("quantity")
        pickup_by = request.POST.get("pickup_by")
        organization_id = request.POST.get("organization")

        # Use the validation function
        errors = validate_donation(food_item, quantity, pickup_by, organization_id)

        if errors:
            for error in errors:
                messages.warning(request, error)
            return redirect(
                "donor_dashboard:manage_organization", organization_id=organization_id
            )

        # Update donation if all validations pass
        donation.food_item = food_item
        donation.quantity = int(quantity)  # Convert to integer before saving
        donation.pickup_by = timezone.datetime.strptime(pickup_by, "%Y-%m-%d").date()
        donation.organization_id = organization_id
        donation.save()

        messages.success(request, f"Donation: {food_item} modified successfully!")
        return redirect(
            "donor_dashboard:manage_organization", organization_id=organization_id
        )

    messages.warning(request, "Invalid Modify Donation Request!")
    return redirect(
        "donor_dashboard:manage_organization", organization_id=donation.organization_id
    )


@login_required
def delete_donation(request, donation_id):
    donation = get_object_or_404(Donation, donation_id=donation_id, active=True)
    if request.method == "POST":
        donation.active = False  # Set the active field to False for soft delete
        donation.save()

        messages.success(
            request, f"Donation '{donation.food_item}' has been deleted successfully!"
        )
        return redirect(
            "donor_dashboard:manage_organization",
            organization_id=donation.organization_id,
        )

    messages.error(request, "Invalid Delete Donation Request!")
    return redirect(
        "donor_dashboard:manage_organization", organization_id=donation.organization_id
    )
