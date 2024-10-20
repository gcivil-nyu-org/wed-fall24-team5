from database.models import Donation, Order
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages


@login_required
def recipient_dashboard(request):
    donations = Donation.objects.filter(active=True).order_by("created_at")
    return render(
        request, "recipient_dashboard/dashboard.html", {"donations": donations}
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
