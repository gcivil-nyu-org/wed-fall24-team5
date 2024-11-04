from django.shortcuts import render, redirect, get_object_or_404  # noqa
from database.models import (
    Organization,
    OrganizationAdmin,
    User,
    Donation,
    Order,
    UserReview,
)
from django.contrib import messages
from donor_dashboard.forms import AddOrganizationForm
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import HttpResponse, JsonResponse
from django.db.models import Avg, Count, F, Value
from django.db.models.functions import ExtractMonth, TruncDate
from .helpers import validate_donation
import csv
from itertools import chain
from operator import attrgetter


@login_required
def add_organization(request):
    if request.method == "POST":
        form = AddOrganizationForm(request.POST)
        if form.is_valid():
            organization = form.save()
            org_user = User.objects.get(email=request.user.email)
            OrganizationAdmin.objects.create(
                user=org_user, organization=organization, access_level="owner"
            )
            messages.success(request, "Organization successfully added.")
            return redirect("/")
    else:
        form = AddOrganizationForm()
    return render(request, "add_organization.html", {"form": form})


@login_required
def get_org_info(request, organization_id):
    organization = Organization.objects.get(organization_id=organization_id)
    donations = Donation.objects.filter(
        organization_id=organization.organization_id, active=True
    )
    orders = Order.objects.filter(
        donation__organization=organization
    ).prefetch_related("donation")
    reviews = (
        UserReview.objects.filter(donation__organization=organization)
        .order_by("modified_at")
        .values("rating", "comment")
    )
    rating = reviews.aggregate(Avg("rating"))
    num_users = orders.values("user").distinct().count()

    return donations, orders, reviews, rating, num_users


@login_required
def get_org_list(request):
    if request.method == "POST":
        form = AddOrganizationForm(request.POST)
        if form.is_valid():
            organization = form.save()
            org_user = User.objects.get(email=request.user.email)
            OrganizationAdmin.objects.create(
                user=org_user, organization=organization, access_level="owner"
            )
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
            "access_level": organization_admin.access_level,
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
    # try:
        organization = Organization.objects.get(organization_id=organization_id)
        org_user = User.objects.get(email=request.user.email)
        organization_admin = OrganizationAdmin.objects.get(
            user=org_user, organization=organization
        )
        access_level = organization_admin.access_level
        if access_level == "owner":
            owner_access = True
        else:
            owner_access = False
        status = organization.active
        
        donations, orders, reviews, rating, num_users = get_org_info(request, organization_id)

        return render(
            request,
            "donor_dashboard/manage_organization.html",
            {
                "organization": organization,
                "donations": donations,
                "status": status,
                "orders": orders,
                "owner_access": owner_access,
                "reviews": reviews,
                "rating": rating,
                "num_users": num_users,
            },
        )
    # except Exception:
    #     messages.warning(request, "You Don't have permission to do this action")
    #     return redirect(
    #         "donor_dashboard:org_list",
    #     )


@login_required
def organization_details(request, organization_id):
    try:
        organization = Organization.objects.get(organization_id=organization_id)
        current_user = User.objects.get(email=request.user.email)
        current_org_admin = OrganizationAdmin.objects.get(
            user=current_user, organization=organization
        )

        if current_org_admin.access_level == "owner":
            organization_admins = OrganizationAdmin.objects.filter(
                organization_id=organization_id
            )

            if request.method == "POST":
                form = AddOrganizationForm(request.POST, instance=organization)
                if form.is_valid():
                    organization = form.save()
                    messages.success(
                        request, "Organization Details Updated Succesfully."
                    )
                    return redirect(
                        "donor_dashboard:manage_organization",
                        organization_id=organization_id,
                    )
            else:
                form = AddOrganizationForm(instance=organization)

            organization_admins = OrganizationAdmin.objects.filter(
                organization_id=organization_id
            )
            admins = []
            for organization_admin in organization_admins:
                admins.append(
                    {
                        "name": organization_admin.user.first_name
                        + " "
                        + organization_admin.user.last_name,
                        "email": organization_admin.user.email,
                        "access_level": organization_admin.access_level,
                    }
                )

            return render(
                request,
                "donor_dashboard/organization_details.html",
                {"organization": organization, "form": form, "admins": admins},
            )
        else:
            messages.warning(request, "You Don't have permission to do this action")
            return redirect(
                "donor_dashboard:manage_organization", organization_id=organization_id
            )
    except Exception:
        messages.warning(request, "You Don't have permission to do this action")
        return redirect(
            "donor_dashboard:manage_organization", organization_id=organization_id
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
def filter_statistics(request, organization_id):
    organization = Organization.objects.get(organization_id=organization_id)
    donations = Donation.objects.filter(
        organization_id=organization.organization_id, active=True
    )
    orders = Order.objects.filter(
        donation__organization=organization
    ).prefetch_related("donation")
    reviews = (
        UserReview.objects.filter(donation__organization=organization)
        .order_by("modified_at")
        .values("rating", "comment")
    )
    grouped_donations = donations.annotate(month=ExtractMonth("created_at")).values("month").order_by("-month").distinct()
    options = [donation["month"] for donation in grouped_donations]
    return JsonResponse({
        "options": options,
    })


@login_required
def statistics_orders(request, organization_id):
    organization = Organization.objects.get(organization_id=organization_id)
    org_user = User.objects.get(email=request.user.email)
    donations = Donation.objects.filter(
        organization_id=organization.organization_id, active=True
    )
    orders = Order.objects.filter(
        donation__organization=organization
    ).prefetch_related("donation")
    reviews = (
        UserReview.objects.filter(donation__organization=organization)
        .order_by("modified_at")
        .values("rating", "comment")
    )
    # today = timezone.now().date()
    # days = [(today - timedelta(days=i)).strftime('%A') for i in range(6, -1, -1)]
    orders_data = orders.annotate(date=TruncDate("order_created_at")).values("date").annotate(order_count=Count("order_id")).order_by("date")
    dates = [entry["date"].strftime('%Y-%m-%d') for entry in orders_data]
    orders_counts = [entry["order_count"] for entry in orders_data]
    # for i in range(6, -1, -1):
    #     day = today - timedelta(days=i)
    #     # Orders for each day in the past week
    #     order_count = orders.filter(order_created_at=day).count()
    #     orders_data.append(order_count)

    return JsonResponse(data={
        "labels": dates,
        "data": orders_counts,
    })


@login_required
def statistics_orders_status(request, organization_id):
    organization = Organization.objects.get(organization_id=organization_id)
    orders = Order.objects.filter(
        donation__organization=organization
    ).prefetch_related("donation")
    orders_status_data = orders.values("order_status").annotate(order_count=Count("order_id")).order_by("order_status")
    statuses = [entry["order_status"] for entry in orders_status_data]
    orders_status_counts = [entry["order_count"] for entry in orders_status_data]

    return JsonResponse(data={
        "labels": statuses,
        "data": orders_status_counts,
    })


@login_required
def statistics_donations(request, organization_id):
    organization = Organization.objects.get(organization_id=organization_id)
    donations = Donation.objects.filter(
        organization_id=organization.organization_id, active=True
    )
    donations_data = donations.annotate(date=TruncDate("created_at")).values("date").annotate(order_count=Count("donation_id")).order_by("date")
    dates = [entry["date"].strftime('%Y-%m-%d') for entry in donations_data]
    donations_counts = [entry["order_count"] for entry in donations_data]

    return JsonResponse(data={
        "labels": dates,
        "data": donations_counts,
    })


@login_required
def statistics_ratings(request, organization_id):
    organization = Organization.objects.get(organization_id=organization_id)
    reviews = (
        UserReview.objects.filter(donation__organization=organization)
        .order_by("modified_at")
        .values("rating", "comment")
    )
    ratings_data = reviews.values("rating").annotate(rating_count=Count("review_id")).order_by("rating")
    ratings = [entry["rating"] for entry in ratings_data]
    ratings_counts = [entry["rating_count"] for entry in ratings_data]

    return JsonResponse(data={
        "labels": ratings,
        "data": ratings_counts,
    })


@login_required
def organization_statistics(request, organization_id):
    organization = Organization.objects.get(organization_id=organization_id)
    donations, orders, reviews, rating, num_users = get_org_info(request, organization_id)
    orders = orders.annotate(created_date=F("order_created_at"), type=Value("Order"))
    review_data = UserReview.objects.filter(donation__organization=organization).annotate(created_date=F("created_at"), type=Value("Review"))
    activity_feed = sorted(
        chain(orders, review_data),
        key=attrgetter("created_date"),
        reverse=True
    )
    return render(
            request,
            "donor_dashboard/statistics.html",
            {
                "organization": organization,
                "donations": donations,
                "orders": orders,
                "reviews": reviews,
                "rating": rating,
                "num_users": num_users,
                "activity_feed": activity_feed,
            },
        )


@login_required
def add_donation(request):
    if request.method == "POST":
        food_item = request.POST["food_item"]
        quantity = request.POST.get("quantity")
        pickup_by = request.POST.get("pickup_by")
        organization_id = request.POST.get("organization")
        organization_id = organization_id.strip()

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
        organization_id = organization_id.strip()

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
        donation.quantity = 0
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


@login_required
def manage_order(request, order_id):
    order = get_object_or_404(Order, order_id=order_id, active=True)
    donation = Donation.objects.get(donation_id=order.donation_id)

    order.order_status = "picked_up" if order.order_status == "pending" else "pending"
    order.save()

    return redirect(
        "donor_dashboard:manage_organization",
        organization_id=donation.organization_id,
    )


@login_required
def download_orders(request, organization_id):
    organization = Organization.objects.get(organization_id=organization_id)
    orders = Order.objects.filter(donation__organization=organization).prefetch_related(
        "donation"
    )
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = "attachment; filename=orders.csv"

    writer = csv.writer(response)
    writer.writerow(
        ["ID", "Donation", "User", "Quantity", "Pickup Date", "Address", "Status"]
    )

    for order in orders:
        writer.writerow(
            [
                order.order_id,
                order.donation.food_item,
                order.user,
                order.order_quantity,
                order.donation.pickup_by,
                organization.address,
                order.order_status,
            ]
        )

    return response


@login_required
def add_org_admin(request):
    try:
        organization_id = request.POST["organization_id"]
        new_admin_email = request.POST.get("email")
        organization = Organization.objects.get(organization_id=organization_id)
        current_user = User.objects.get(email=request.user.email)
        current_org_admin = OrganizationAdmin.objects.get(
            user=current_user, organization=organization
        )
        if current_org_admin.access_level == "owner":
            if request.method == "POST":
                new_admin_user = User.objects.get(email=new_admin_email)
                if (
                    len(
                        OrganizationAdmin.objects.filter(
                            user=new_admin_user, organization=organization
                        )
                    )
                    == 0
                ):

                    OrganizationAdmin.objects.create(
                        user=new_admin_user,
                        organization=organization,
                        access_level="admin",
                    )
                    messages.success(request, "Admin successfully added.")
                else:
                    messages.success(request, "Admin already associated")
            return redirect(
                "donor_dashboard:organization_details", organization_id=organization_id
            )
        else:
            messages.warning(request, "You Don't have permission to do this action")
            return redirect(
                "donor_dashboard:manage_organization", organization_id=organization_id
            )
    except Exception:
        messages.warning(request, "You Don't have permission to do this action")
        return redirect(
            "donor_dashboard:manage_organization", organization_id=organization_id
        )


@login_required
def assign_organization_access_level(
    request, organization_id, admin_email, current_access_level
):
    try:
        organization = Organization.objects.get(organization_id=organization_id)
        current_user = User.objects.get(email=request.user.email)
        current_org_admin = OrganizationAdmin.objects.get(
            user=current_user, organization=organization
        )
        if current_org_admin.access_level == "owner":
            if request.method == "POST":
                admin_user = User.objects.get(email=admin_email)
                organization_admin = OrganizationAdmin.objects.get(
                    user=admin_user, organization=organization
                )
                if current_access_level == "owner":
                    organization_admin.access_level = "admin"
                elif current_access_level == "admin":
                    organization_admin.access_level = "owner"

                organization_admin.save()

                messages.success(
                    request,
                    f"Succesfully made user with email: {admin_email} as {organization_admin.access_level}",
                )
            return redirect(
                "donor_dashboard:organization_details", organization_id=organization_id
            )
        else:
            messages.warning(request, "You Don't have permission to do this action")
            return redirect(
                "donor_dashboard:manage_organization", organization_id=organization_id
            )
    except Exception:
        messages.warning(request, "You Don't have permission to do this action")
        return redirect(
            "donor_dashboard:manage_organization", organization_id=organization_id
        )


@login_required
def remove_admin_owner(request, organization_id, admin_email):
    try:
        organization = Organization.objects.get(organization_id=organization_id)
        current_user = User.objects.get(email=request.user.email)
        current_org_admin = OrganizationAdmin.objects.get(
            user=current_user, organization=organization
        )
        if current_org_admin.access_level == "owner":
            if request.method == "POST":
                admin_user = User.objects.get(email=admin_email)
                organization_admin = OrganizationAdmin.objects.get(
                    user=admin_user, organization=organization
                )
                organization_admin.delete()

                messages.success(
                    request,
                    f"Succesfully remove this org access to email: {admin_email}",
                )
            return redirect(
                "donor_dashboard:organization_details", organization_id=organization_id
            )
        else:
            messages.warning(request, "You Don't have permission to do this action")
            return redirect(
                "donor_dashboard:manage_organization", organization_id=organization_id
            )
    except Exception:
        messages.warning(request, "You Don't have permission to do this action")
        return redirect(
            "donor_dashboard:manage_organization", organization_id=organization_id
        )
