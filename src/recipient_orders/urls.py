# Example src/subapplication_name/urls.py file
from django.urls import path
from . import views

urlpatterns = [
    path("", views.recipient_orders, name="recipient_orders"),
    path("pickup/<uuid:order_id>/", views.pickup_order, name="pickup_order"),
    path(
        "move_to_pending/<uuid:order_id>/",
        views.mark_order_as_pending,
        name="mark_order_as_pending",
    ),
    path("cancel/<uuid:order_id>/", views.cancel_order, name="cancel_order"),
    path("modify/", views.modify_order, name="modify_order"),
]
