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
    donation = get_object_or_404(Donation, pk=donation_id, active=True)
    if donation.quantity <= 0:
        messages.warning(request, "This donation is no longer available.")
        return redirect('recipient_dashboard')
    
    # Create new order
    order = Order.objects.create(
        donation=donation,
        user=request.user,
        order_quantity=1,  # In future : allow user to select quantity
        order_status="pending"
    )

    # Reduce donation quantity
    donation.quantity -= 1
    donation.save()

    messages.success(request, "Donation reserved successfully.")
    return redirect('recipient_dashboard')