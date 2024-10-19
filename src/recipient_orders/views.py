from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from database.models import Order

@login_required
def recipient_orders(request):
    # Get orders grouped by their status
    pending_orders = Order.objects.filter(user=request.user,
                                          active=True,
                                          order_status="pending")\
        .select_related('donation')\
        .order_by('order_created_at')
    picked_up_orders = Order.objects.filter(user=request.user,
                                            active=True,
                                            order_status="picked_up")\
        .select_related('donation')\
        .order_by('order_created_at')
    canceled_orders = Order.objects.filter(user=request.user,
                                           active=True,
                                           order_status="canceled")\
        .select_related('donation')\
        .order_by('order_created_at')

    # Pass the grouped orders to the template
    context = {
        'pending_orders': pending_orders,
        'picked_up_orders': picked_up_orders,
        'canceled_orders': canceled_orders,
    }

    return render(request, "recipient_orders/orders.html", context)
