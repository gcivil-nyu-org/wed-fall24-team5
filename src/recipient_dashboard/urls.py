from django.urls import path
from .views import recipient_dashboard

urlpatterns = [
    path("", recipient_dashboard, name="recipient-dashboard"),
]
