from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from database.models import Order, UserReview
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
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')

        # Fetch the order and related donation
        order = get_object_or_404(Order, pk=order_id)

        # Try to get the existing review or create a new one if it doesn't exist
        try:
            review, created = UserReview.objects.get_or_create(
                donation=order.donation,
                user=request.user,
                defaults={'rating': rating, 'comment': comment}
            )
            
            # If the review already exists, update its rating and comment
            if not created:
                review.rating = rating
                review.comment = comment
                review.save()
            messages.success(request, "Review sent successfully. Thanks!")
        except:
            messages.warning(request, "Unable to provide review. Please try again later.")

        return redirect('/recipient_orders')