from database.models import Donation, Order, Organization
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone


@login_required
def recipient_dashboard(request):
    currdate = timezone.now().date()
    donations = Donation.objects.filter(
        Q(active=True) & Q(quantity__gt=0) & Q(pickup_by__gte=currdate)
    ).order_by("created_at")
    categories = Organization.objects.values_list("type", flat=True).distinct()
    if request.method == "GET":
        keyword = request.GET.get("keyword")
        category = request.GET.get("category")
        type = request.GET.get("type")
        quantity = request.GET.get("quantity")
        filter_food = Q(food_item__icontains=keyword)
        filter_org = Q(organization_id__organization_name__icontains=keyword)
        if keyword:
            if type == "food":
                donations = donations.filter(filter_food)
            elif type == "org":
                donations = donations.filter(filter_org)
            else:
                donations = donations.filter(filter_food | filter_org)
        if category:
            donations = donations.filter(organization_id__type=category)
        if quantity:
            donations = donations.filter(quantity__gte=quantity)

    context = {
        "donations": donations,
        "categories": categories,
        "keyword": keyword,
        "category": category,
        "type": type,
        "quantity": quantity,
    }
    return render(request, "recipient_dashboard/dashboard.html", context)


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
