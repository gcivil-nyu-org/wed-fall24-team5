from django.shortcuts import get_object_or_404, redirect, render
from database.models import Order, UserReview
from django.contrib.auth.decorators import login_required
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

    # Get reviews and map them by donation_id for easier access
    reviews = {
        review.donation_id: review
        for review in UserReview.objects.filter(user=request.user, active=True)
    }

    # Attach review to each order
    for order in pending_orders:
        order.review = reviews.get(order.donation_id)

    for order in picked_up_orders:
        order.review = reviews.get(order.donation_id)

    for order in canceled_orders:
        order.review = reviews.get(order.donation_id)

    # Pass the orders and other context to the template
    context = {
        "pending_orders": pending_orders,
        "picked_up_orders": picked_up_orders,
        "canceled_orders": canceled_orders,
    }

    return render(request, "recipient_orders/orders.html", context)


@login_required
def submit_review(request):
    if request.method == "POST":
        order_id = request.POST.get("order_id")
        rating = request.POST.get("rating")
        comment = request.POST.get("comment")

        # Fetch the order and related donation
        order = get_object_or_404(Order, pk=order_id)

        # Try to get the existing review or create a new one if it doesn't exist
        try:
            review, created = UserReview.objects.get_or_create(
                donation=order.donation,
                user=request.user,
                defaults={"rating": rating, "comment": comment},
            )

            # If the review already exists, update its rating and comment
            if not created:
                review.rating = rating
                review.comment = comment
                review.save()
            messages.success(request, "Review sent successfully. Thanks!")
        except:  # noqa <-- for bare except
            messages.warning(
                request, "Unable to provide review. Please try again later."
            )

    return redirect("recipient_orders")


def pickup_order(request, order_id):
    try:
        order = get_object_or_404(Order, pk=order_id, active=True)
        order.order_status = "picked_up"
        order.save()
        messages.success(request, "Donation marked as picked up successfully.")
        return redirect("recipient_orders")
    except Exception:
        messages.warning(
            request, "Unable to mark order as picked up. Please try again later."
        )
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
        messages.warning(
            request, "Unable to mark order as pending. Please try again later."
        )
        return redirect("recipient_orders")


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


@login_required
def modify_order(request):
    if request.method != "POST":
        messages.error(request, "Invalid request method")
        return redirect("recipient_orders")

    order_id = request.POST.get("order_id")
    new_quantity = int(request.POST.get("new_quantity", 0))
    current_quantity = int(request.POST.get("current_quantity", 0))

    try:
        order = Order.objects.get(
            order_id=order_id, user=request.user, active=True, order_status="pending"
        )

        # Calculate available quantity including current order
        total_available = order.donation.quantity + current_quantity
        max_allowed = min(3, total_available)

        if new_quantity < 1:
            messages.error(request, "Quantity must be at least 1")
            return redirect("recipient_orders")

        if new_quantity > max_allowed:
            messages.error(request, f"Maximum allowed quantity is {max_allowed}")
            return redirect("recipient_orders")

        # Calculate the difference in quantity
        quantity_difference = new_quantity - current_quantity

        # Update the order quantity
        order.order_quantity = new_quantity
        order.save()

        # Update the donation quantity
        donation = order.donation
        donation.quantity = donation.quantity - quantity_difference
        donation.save()

        messages.success(request, "Order quantity updated successfully")

    except Order.DoesNotExist:
        messages.error(request, "Order not found")
    except Exception as e:
        messages.error(request, f"Error modifying order: {str(e)}")

    return redirect("recipient_orders")
