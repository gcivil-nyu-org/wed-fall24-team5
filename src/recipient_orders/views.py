from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from database.models import Order


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
def cancel_order(request, order_id):
    # Get the order or return 404 if not found
    order = get_object_or_404(Order, order_id=order_id, user=request.user, active=True)

    if request.method == "POST":
        if order.order_status == "pending":
            # Return the quantity back to the donation
            donation = order.donation
            donation.quantity += order.order_quantity
            donation.save()

            # Update order status to canceled
            order.order_status = "canceled"
            order.save()

            messages.success(
                request, "Your reservation has been cancelled successfully."
            )
        else:
            messages.error(request, "Only pending orders can be cancelled.")

        return redirect("recipient_orders")

    messages.error(request, "Invalid request method.")
    return redirect("recipient_orders")
