from django.urls import path
from . import views

app_name = "donor_dashboard"  # pylint: disable=invalid-name

urlpatterns = [
    path("", views.get_org_list, name="org_list"),
    path("add-organization/", views.add_organization, name="add_organization"),
    path(
        "manage-organization/<uuid:organization_id>/",
        views.manage_organization,
        name="manage_organization",
    ),
]
