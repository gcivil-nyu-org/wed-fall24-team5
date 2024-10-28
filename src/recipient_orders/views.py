from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from database.models import Donation, Order
from django.contrib import messages


@login_required
def recipient_orders(request):
    # Get orders grouped by their status
    pending_orders = (
        Order.objects.filter(user=request.user, active=True, order_status="pending")
        .select_related("donation")
        .order_by("order_created_at")
    )
    picked_up_orders = (
        Order.objects.filter(user=request.user, active=True, order_status="picked_up")
        .select_related("donation")
        .order_by("order_created_at")
    )
    canceled_orders = (
        Order.objects.filter(user=request.user, active=True, order_status="canceled")
        .select_related("donation")
        .order_by("order_created_at")
    )

    # Pass the grouped orders to the template
    context = {
        "pending_orders": pending_orders,
        "picked_up_orders": picked_up_orders,
        "canceled_orders": canceled_orders,
    }

    return render(request, "recipient_orders/orders.html", context)

@login_required
def pickup_order(request, order_id):
    try:
        order = get_object_or_404(Order, pk=order_id, active=True)
        order.order_status = "picked_up"
        order.save()
        messages.success(request, "Donation marked as picked up successfully.")
        return redirect("recipient_orders")
    except Exception:
        messages.warning(request, "Unable to mark order as picked up. Please try again later.")
        return redirect("recipient_orders")
    
@login_required
def mark_order_as_pending(request, order_id):
    try:
        order = get_object_or_404(Order, pk=order_id, active=True)
        order.order_status = "pending"
        order.save()
        messages.success(request, "Donation marked as pending successfully.")
        return redirect("recipient_orders")
    except Exception:
        messages.warning(request, "Unable to mark order as pending. Please try again later.")
        return redirect("recipient_orders")
