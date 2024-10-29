from database.models import Donation, Order
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from .forms import SearchDonationForm
from django.db.models import Avg


@login_required
def recipient_dashboard(request):
    currdate = timezone.now().date()
    form = SearchDonationForm(request.GET)
    donations = Donation.objects.filter(
        Q(active=True) & Q(quantity__gt=0) & Q(pickup_by__gte=currdate)
    ).select_related("organization")

    # Annotate each donation with the average rating of its organization by joining UserReview through Donation
    donations = donations.annotate(
        avg_rating=Avg("organization__donation__userreview__rating")
    ).order_by("created_at")

    if form.is_valid():
        keyword = form.cleaned_data.get("keyword")
        category = form.cleaned_data.get("category")
        type = form.cleaned_data.get("type")
        date = form.cleaned_data.get("date")
        min_quantity = form.cleaned_data.get("min_quantity")
        address = form.cleaned_data.get("address")
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
        if address:
            donations = donations.filter(organization_id__address__icontains=address)

    return render(
        request,
        "recipient_dashboard/dashboard.html",
        {"form": form, "donations": donations},
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
