from database.models import (
    Donation,
    Order,
    User,
    Organization,
    UserReview,
    OrganizationAdmin,
)
from django.shortcuts import get_object_or_404, render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Avg, Sum, Count
from django.db.models.functions import TruncDate
from django.utils import timezone
from .forms import SearchDonationForm
from .utils import get_coordinates, calculate_distance
from django.core.cache import cache  # noqa


@login_required
def recipient_dashboard(request):
    currdate = timezone.now().date()
    form = SearchDonationForm(request.GET)
    donations = Donation.objects.filter(
        Q(active=True) & Q(quantity__gt=0) & Q(pickup_by__gte=currdate)
    ).select_related("organization")

    # Annotate each donation with the average rating
    donations = donations.annotate(
        avg_rating=Avg("organization__donation__userreview__rating")
    ).order_by("pickup_by")

    if form.is_valid():
        keyword = form.cleaned_data.get("keyword")
        category = form.cleaned_data.get("category")
        type = form.cleaned_data.get("type")
        date = form.cleaned_data.get("date")
        min_quantity = form.cleaned_data.get("min_quantity")
        address = form.cleaned_data.get("address")

        try:
            radius = float(form.cleaned_data.get("radius") or 5)
        except (TypeError, ValueError):
            radius = 5.0

        # Apply non-location filters first
        if keyword:
            if type == "food":
                donations = donations.filter(food_item__icontains=keyword)
            elif type == "org":
                donations = donations.filter(
                    organization_id__organization_name__icontains=keyword
                )
            else:
                donations = donations.filter(
                    Q(food_item__icontains=keyword)
                    | Q(organization_id__organization_name__icontains=keyword)
                )
        if category:
            donations = donations.filter(organization_id__type=category)
        if date:
            donations = donations.filter(pickup_by__gte=date)
        if min_quantity:
            donations = donations.filter(quantity__gte=min_quantity)

        # Handle location-based filtering
        if address:
            try:
                # Get coordinates for the search address
                coords = get_coordinates(address)
                if coords:
                    # Prepare address info for each donation
                    donation_distances = []
                    for donation in donations:
                        org = donation.organization
                        addr_coords = get_coordinates(org.address)
                        if addr_coords:
                            distance = calculate_distance(coords, addr_coords)
                            if distance is not None and distance <= radius:
                                donation_distances.append(
                                    {
                                        "donation": donation,
                                        "distance": distance,
                                        "organization": org,
                                    }
                                )

                    # Sort by distance
                    donation_distances.sort(key=lambda x: x["distance"])

                    if not donation_distances:
                        messages.info(
                            request, f"No donations found within {radius} miles."
                        )
                        return render(
                            request,
                            "recipient_dashboard/dashboard.html",
                            {"form": form, "donations": []},
                        )

                    # Create sorted list of donations and distances dictionary
                    sorted_donations = [item["donation"] for item in donation_distances]
                    org_count = len(set(item.organization for item in sorted_donations))
                    total_items = sum(item.quantity for item in sorted_donations)
                    distances = {
                        str(item["organization"].organization_id): item["distance"]
                        for item in donation_distances
                    }

                    # Add everything to context
                    context = {
                        "form": form,
                        "donations": sorted_donations,
                        "distances": distances,
                        "org_count": org_count,
                        "total_items": total_items,
                    }
                    return render(
                        request, "recipient_dashboard/dashboard.html", context
                    )
                else:
                    messages.warning(request, "Could not find the specified address.")
            except Exception as e:
                messages.warning(request, f"Error processing location search: {str(e)}")
                print(f"Location search error details: {str(e)}")  # For debugging

    org_count = donations.values("organization_id").distinct().count()
    total_items = donations.aggregate(total=Sum("quantity"))["total"]

    return render(
        request,
        "recipient_dashboard/dashboard.html",
        {
            "form": form,
            "donations": donations,
            "org_count": org_count,
            "total_items": total_items,
        },
    )


@login_required
def reserve_donation(request, donation_id):
    try:
        donation = get_object_or_404(Donation, pk=donation_id, active=True)
        if donation.quantity <= 0:
            messages.warning(request, "This donation is no longer available.")
            return redirect("recipient_dashboard")

        # Check if the user has already reserved this donation
        existing_order = Order.objects.filter(
            donation=donation, user=request.user, active=True, order_status="pending"
        ).first()

        if existing_order:
            # Increment order quantity if an order exists
            existing_order.order_quantity += 1
            existing_order.save()
            messages.success(request, "Donation reserved successfully.")
        else:
            # Create a new order if no existing order is found
            Order.objects.create(
                donation=donation,
                user=request.user,
                order_quantity=1,  # In the future: allow user to select quantity
                order_status="pending",
            )
            messages.success(request, "Donation reserved successfully.")

        # Reduce donation quantity
        donation.quantity -= 1
        donation.save()

        return redirect("recipient_dashboard")
    except Exception:
        messages.warning(request, "Unable to reserve donation. Try again later.")
        return redirect("recipient_dashboard")


@login_required
def recipient_stats(request):
    user = User.objects.get(email=request.user.email)
    organizations = Organization.objects.filter(organizationadmin__user=user)
    reviews = UserReview.objects.filter(user=user)
    donations = Donation.objects.filter(organization__in=organizations)
    orders = Order.objects.filter(user=user)
    rating = reviews.aggregate(avg=Avg("rating"))["avg"]
    return render(
        request,
        "recipient_dashboard/recipient_statistics.html",
        {
            "organizations": organizations,
            "donations": donations,
            "orders": orders,
            "reviews": reviews,
            "rating": rating,
        },
    )


@login_required
def statistics_user_orders(request):
    user = User.objects.get(email=request.user.email)
    orders = Order.objects.filter(user=user)
    orders_data = (
        orders.annotate(date=TruncDate("order_created_at"))
        .values("date")
        .annotate(order_count=Count("order_id"))
        .order_by("date")
    )
    dates = [entry["date"].strftime("%Y-%m-%d") for entry in orders_data]
    orders_counts = [entry["order_count"] for entry in orders_data]

    return JsonResponse(
        data={
            "labels": dates,
            "data": orders_counts,
        }
    )


@login_required
def statistics_user_donations(request):
    user = User.objects.get(email=request.user.email)
    org_admins = OrganizationAdmin.objects.filter(user=user).values_list(
        "organization", flat=True
    )
    organizations = Organization.objects.filter(organization_id__in=org_admins)
    donations = Donation.objects.filter(organization__in=organizations)
    donations_data = (
        donations.annotate(date=TruncDate("created_at"))
        .values("date")
        .annotate(donation_count=Count("donation_id"))
        .order_by("date")
    )
    dates = [entry["date"].strftime("%Y-%m-%d") for entry in donations_data]
    donations_counts = [entry["donation_count"] for entry in donations_data]

    return JsonResponse(
        data={
            "labels": dates,
            "data": donations_counts,
        }
    )
