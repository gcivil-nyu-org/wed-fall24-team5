from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from database.models import Order

# Create your views here.
@login_required
def recipient_orders(request):
    # Select all donations that the logged-in user has reserved
    orders = Order.objects\
        .filter(user=request.user, active=True)\
        .select_related('donation')\
        .order_by('order_created_at')
    
    return render(
        request, "recipient_orders/orders.html", {'orders': orders}
    )