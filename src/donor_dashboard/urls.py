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
]
