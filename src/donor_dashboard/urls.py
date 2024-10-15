from django.urls import path
from .views import donor_dashboard

urlpatterns = [
    path("", donor_dashboard, name="donor_dashboard"),
]
