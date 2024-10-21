from django.urls import path
from .views import recipient_dashboard, reserve_donation

urlpatterns = [
    path("reserve/<uuid:donation_id>/", reserve_donation, name="reserve_donation"),
    path("", recipient_dashboard, name="recipient_dashboard"),
]
