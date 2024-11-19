from django.shortcuts import render, redirect, get_object_or_404  # noqa
from django.db.models import Prefetch
from database.models import (
    DietaryRestriction,
    Organization,
    OrganizationAdmin,
    User,
    Donation,
    Order,
    UserReview,
)
from django.contrib import messages
from donor_dashboard.forms import AddOrganizationForm, AddDonationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.http import HttpResponse, JsonResponse
from django.db.models import Avg, Count, F, Value
from django.db.models.functions import ExtractMonth, TruncDate, Coalesce
from .helpers import validate_donation
import csv
from itertools import chain
from operator import attrgetter
import json


@login_required
def get_org_info(request, organization_id):
    organization = Organization.objects.get(organization_id=organization_id)
    donations = Donation.objects.filter(
        organization_id=organization.organization_id, active=True
    )
    orders = Order.objects.filter(donation__organization=organization).prefetch_related(
        "donation"
    )
    reviews = (
        UserReview.objects.filter(donation__organization=organization)
        .order_by("modified_at")
        .values("rating", "comment")
    )
    rating = reviews.aggregate(avg=Avg("rating"))["avg"]
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
            # Handle errors using Django messages
            if form.errors.get("organization_name"):
                messages.warning(
                    request, "Organization Name is invalid. Please try again."
                )
            if form.errors.get("address"):
                messages.warning(request, "Address is not valid. Please try again.")
            if form.errors.get("zipcode"):
                messages.warning(request, "Zipcode is not valid. Please try again.")
            if form.errors.get("contact_number"):
                messages.warning(
                    request, "Contact Number is not valid. Please try again."
                )
            if form.errors.get("email"):
                messages.warning(request, "Email is not valid. Please try again.")
            if form.errors.get("website"):
                messages.warning(request, "Website is not valid. Please try again.")

            # Fallback error message
            if not any(form.errors):
                messages.warning(
                    request, "Registration failed. Please check the form for errors."
                )

            # Pass the form with errors back to the template
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
    try:
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

        # Fetch donations with related reviews
        donations = Donation.objects.filter(
            organization_id=organization.organization_id, active=True
        ).prefetch_related(
            Prefetch(
                "userreview_set",
                queryset=UserReview.objects.filter(active=True).order_by("modified_at"),
            )
        )

        # Prefetch orders and dietary restrictions for each user
        orders = (
            Order.objects.filter(donation__organization=organization, active=True)
            .prefetch_related(
                "donation",
                "user",
                Prefetch(
                    "user__dietaryrestriction_set",
                    queryset=DietaryRestriction.objects.all(),
                    to_attr="dietary_restrictions",
                ),
            )
            .order_by(
                "-donation__pickup_by", "donation__donation_id"
            )  # Sort by pickup date descending, then by donation ID
        )

        # Process dietary restrictions to replace underscores and apply title case
        for order in orders:
            if hasattr(order.user, "dietary_restrictions"):
                for restriction in order.user.dietary_restrictions:
                    restriction.restriction = restriction.restriction.replace(
                        "_", " "
                    ).title()

        status = organization.active
        reviews = (
            UserReview.objects.filter(donation__organization=organization)
            .order_by("modified_at")
            .values("rating", "comment")
        )
        rating = reviews.aggregate(avg=Avg("rating"))["avg"]
        num_users = orders.values("user").distinct().count()
        form = AddDonationForm()
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
                "form": form,
            },
        )
    except Exception:
        messages.warning(request, "You Don't have permission to do this action")
        return redirect(
            "donor_dashboard:org_list",
        )


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
            ).order_by("-access_level")

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
                org_user = organization_admin.user
                if org_user != current_user:
                    if org_user.first_name and org_user.last_name:
                        name = org_user.first_name + " " + org_user.last_name
                    else:
                        name = org_user.email.split("@")[0]
                    admins.append(
                        {
                            "name": name,
                            "email": organization_admin.user.email,
                            "access_level": organization_admin.access_level,
                            "created_at": organization_admin.created_at,
                        }
                    )

            owner_count = organization_admins.filter(access_level="owner").count()
            multiple_owners = owner_count > 1

            return render(
                request,
                "donor_dashboard/organization_details.html",
                {
                    "organization": organization,
                    "form": form,
                    "current_org_admin": current_org_admin,
                    "admins": admins,
                    "multiple_owners": multiple_owners,
                },
            )
        else:
            messages.warning(request, "You don't have permission to do this action")
            return redirect(
                "donor_dashboard:manage_organization", organization_id=organization_id
            )
    except Exception:
        messages.warning(request, "You don't have permission to do this action")
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
    grouped_donations = (
        donations.annotate(month=ExtractMonth("created_at"))
        .values("month")
        .order_by("-month")
        .distinct()
    )
    options = [donation["month"] for donation in grouped_donations]
    return JsonResponse(
        {
            "options": options,
        }
    )


@login_required
def statistics_orders(request, organization_id):
    organization = Organization.objects.get(organization_id=organization_id)
    orders = Order.objects.filter(donation__organization=organization).prefetch_related(
        "donation"
    )
    orders_data = (
        orders.annotate(date=TruncDate("order_created_at"))
        .values("date")
        .annotate(order_count=Count("order_id"))
        .order_by("date")
    )
    dates = [entry["date"].strftime("%b %d") for entry in orders_data]
    orders_counts = [entry["order_count"] for entry in orders_data]

    return JsonResponse(
        data={
            "labels": dates,
            "data": orders_counts,
        }
    )


@login_required
def statistics_orders_status(request, organization_id):
    organization = Organization.objects.get(organization_id=organization_id)
    orders = Order.objects.filter(donation__organization=organization).prefetch_related(
        "donation"
    )
    statuses = {
        "picked_up": "Picked Up",
        "pending": "Pending",
        "canceled": "Canceled",
    }
    orders_status_data = orders.values("order_status").annotate(
        order_count=Count("order_id")
    )

    status_counts_dict = {
        item["order_status"]: item["order_count"] for item in orders_status_data
    }
    order_statuses = [statuses[status] for status in statuses.keys()]
    data = [status_counts_dict.get(order_status, 0) for order_status in statuses.keys()]

    return JsonResponse(
        data={
            "labels": order_statuses,
            "data": data,
        }
    )


@login_required
def statistics_donations(request, organization_id):
    organization = Organization.objects.get(organization_id=organization_id)
    donations = Donation.objects.filter(
        organization_id=organization.organization_id, active=True
    )
    donations_data = (
        donations.annotate(date=TruncDate("created_at"))
        .values("date")
        .annotate(order_count=Count("donation_id"))
        .order_by("date")
    )
    dates = [entry["date"].strftime("%b %d") for entry in donations_data]
    donations_counts = [entry["order_count"] for entry in donations_data]

    return JsonResponse(
        data={
            "labels": dates,
            "data": donations_counts,
        }
    )


@login_required
def statistics_ratings(request, organization_id):
    organization = Organization.objects.get(organization_id=organization_id)
    reviews = (
        UserReview.objects.filter(donation__organization=organization)
        .order_by("modified_at")
        .values("rating", "comment")
    )
    ratings_data = (
        reviews.values("rating")
        .annotate(rating_count=Coalesce(Count("review_id"), Value(0)))
        .order_by("rating")
    )
    # ratings = [entry["rating"] for entry in ratings_data]
    # ratings_counts = [entry["rating_count"] for entry in ratings_data]
    all_ratings = {i: 0 for i in range(1, 6)}
    for entry in ratings_data:
        rating = entry["rating"]
        count = entry["rating_count"]
        all_ratings[rating] = count

    return JsonResponse(
        data={
            "labels": list(all_ratings.keys()),
            "data": list(all_ratings.values()),
        }
    )


@login_required
def organization_statistics(request, organization_id):
    organization = Organization.objects.get(organization_id=organization_id)
    donations, orders, reviews, rating, num_users = get_org_info(
        request, organization_id
    )
    orders = orders.annotate(created_date=F("order_created_at"), type=Value("Order"))
    review_data = UserReview.objects.filter(
        donation__organization=organization
    ).annotate(created_date=F("created_at"), type=Value("Review"))
    activity_feed = sorted(
        chain(orders, review_data), key=attrgetter("created_date"), reverse=True
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
        organization_id = request.POST.get("organization")
        organization_id = organization_id.strip()
        form = AddDonationForm(request.POST)

        if form.is_valid():
            donation = form.save(commit=False)
            food_item = form.cleaned_data["food_item"]
            organization = Organization.objects.get(organization_id=organization_id)
            donation.organization = organization
            donation.save()
            messages.success(request, f"Donation: {food_item} added successfully!")

        else:
            messages.error(request, "Unable to add donation.")

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
    orders = (
        Order.objects.filter(donation__organization=organization)
        .prefetch_related("donation")
        .order_by("order_created_at")
    )
    current_date = timezone.datetime.now().strftime("%Y%m%d")

    response = HttpResponse(content_type="text/csv")
    filename = f"{organization.organization_name}_orders_{current_date}.csv"
    response["Content-Disposition"] = f'attachment; filename="{filename}"'

    writer = csv.writer(response)
    writer.writerow(
        [
            "Donation",
            "User",
            "Quantity",
            "Pickup Date",
            "Status",
            "Created On",
            "Modified On",
        ]
    )

    for order in orders:
        writer.writerow(
            [
                order.donation.food_item,
                order.user,
                order.order_quantity,
                order.donation.pickup_by,
                order.order_status,
                order.order_created_at,
                order.order_modified_at,
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
                new_admin_user, created = User.objects.get_or_create(
                    email=new_admin_email
                )
                if created:
                    new_admin_user.username = new_admin_email  # Set username as email
                    default_password = get_random_string(8)
                    new_admin_user.password = make_password(default_password)
                    new_admin_user.save()  # Save the user object
                if (
                    len(
                        OrganizationAdmin.objects.filter(
                            user=new_admin_user, organization=organization
                        )
                    )
                    == 0
                    or created
                ):
                    OrganizationAdmin.objects.create(
                        user=new_admin_user,
                        organization=organization,
                        access_level="admin",
                    )
                    if created:
                        messages.add_message(
                            request,
                            messages.INFO,
                            f"Admin successfully created with default password: {default_password}",
                            extra_tags="temp_password",
                        )
                    else:
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
def check_user(request):
    if request.method == "POST":
        data = json.loads(request.body)
        email = data.get("email")
        exists = User.objects.filter(email=email).exists()
        return JsonResponse({"exists": exists})


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

        # Check if current user is the only owner
        owner_count = OrganizationAdmin.objects.filter(
            organization=organization, access_level="owner"
        ).count()

        if current_org_admin.access_level == "owner":
            if current_access_level == "owner" and owner_count == 1:
                # Prevent downgrading the only owner
                messages.warning(request, "You cannot remove the only owner.")
                return redirect(
                    "donor_dashboard:organization_details",
                    organization_id=organization_id,
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
