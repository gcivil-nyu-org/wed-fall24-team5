# Example src/subapplication_name/urls.py file
from django.urls import path
from . import views

urlpatterns = [
    path("", views.recipient_orders, name="recipient_orders"),
    path("cancel/<uuid:order_id>/", views.cancel_order, name="cancel_order"),
    path("modify/", views.modify_order, name="modify_order"),
]
