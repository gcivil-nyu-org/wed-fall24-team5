from database.models import Donation
from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def recipient_dashboard(request):
    donations = Donation.objects.filter(active=True).order_by("created_at")
    return render(
        request, "recipient_dashboard/dashboard.html", {"donations": donations}
    )


def search_donation(request, keyword):
    donations = Donation.objects.filter(food_item__icontains=keyword)
    return render(
        request, "recipient_dashboard/dashboard.html", {"donations": donations}
    )
