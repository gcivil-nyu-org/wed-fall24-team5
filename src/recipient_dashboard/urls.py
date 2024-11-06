from django.urls import path
from . import views

urlpatterns = [
    path(
        "reserve/<uuid:donation_id>/", views.reserve_donation, name="reserve_donation"
    ),
    path("", views.recipient_dashboard, name="recipient_dashboard"),
    path("recipient_stats/", views.recipient_stats, name="recipient_stats"),
    path(
        "user_orders_chart/",
        views.statistics_user_orders,
        name="statistics_user_orders",
    ),
    path(
        "user_donations_chart/",
        views.statistics_user_donations,
        name="statistics_user_donations",
    ),
]
