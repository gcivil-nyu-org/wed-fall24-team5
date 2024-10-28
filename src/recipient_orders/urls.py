# Example src/subapplication_name/urls.py file
from django.urls import path
from . import views

urlpatterns = [
    path("", views.recipient_orders, name="recipient_orders"),
    path('submit-review/', views.submit_review, name='submit_review'),
]
