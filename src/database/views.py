from django.shortcuts import render
from database.models import Organization, Donation

def test_database_view(request):
    organizations = Organization.objects.all()
    donations = Donation.objects.all()  # Fetch donations instead of orders
    context = {
        'organizations': organizations,
        'donations': donations  # Pass donations to the template
    }
    return render(request, 'test_database.html', context)
