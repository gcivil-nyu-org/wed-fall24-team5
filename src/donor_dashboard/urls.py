from django.urls import path
from . import views

app_name = "donor_dashboard"  # pylint: disable=invalid-name

urlpatterns = [
    path("", views.get_org_list, name="org_list"),
    path("add-organization/", views.add_organization, name="add_organization"),
    path(
        "manage_organization/<uuid:organization_id>/",
        views.manage_organization,
        name="manage_organization",
    ),
    path(
        "delete_organization/<uuid:organization_id>/",
        views.delete_organization,
        name="delete_organization",
    ),
    path(
        "organization_details/<uuid:organization_id>/",
        views.organization_details,
        name="organization_details",
    ),
    path(
        "add_donation/",
        views.add_donation,
        name="add_donation",
    ),
    path(
        "modify_donation/<uuid:donation_id>/",
        views.modify_donation,
        name="modify_donation",
    ),
    path(
        "delete_donation/<uuid:donation_id>/",
        views.delete_donation,
        name="delete_donation",
    ),
    path("manage_order/<uuid:order_id>/", views.manage_order, name="manage_order"),
    path(
        "download_orders/<uuid:organization_id>/",
        views.download_orders,
        name="download_orders",
    ),
    path("add_org_admin/", views.add_org_admin, name="add_org_admin"),
    path(
        "assign_organization_access_level/<uuid:organization_id>/<str:admin_email>/<str:current_access_level>",
        views.assign_organization_access_level,
        name="assign_organization_access_level",
    ),
    path(
        "remove_admin_owner/<uuid:organization_id>/<str:admin_email>",
        views.remove_admin_owner,
        name="remove_admin_owner",
    ),
    path(
        "statistics/<uuid:organization_id>/",
        views.organization_statistics,
        name="organization_statistics",
    ),
    path(
        "statistics/filter_statistics/",
        views.filter_statistics,
        name="filter_statistics",
    ),
    path(
        "orders_chart/<uuid:organization_id>/",
        views.statistics_orders,
        name="statistics_orders",
    ),
    path(
        "orders_status_chart/<uuid:organization_id>/",
        views.statistics_orders_status,
        name="statistics_orders_status",
    ),
    path(
        "donations_chart/<uuid:organization_id>/",
        views.statistics_donations,
        name="statistics_donations",
    ),
    path(
        "ratings_chart/<uuid:organization_id>/",
        views.statistics_ratings,
        name="statistics_ratings",
    ),
]
