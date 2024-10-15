from django.urls import path
from . import views

app_name = "donor_dashboard"  # pylint: disable=invalid-name

urlpatterns = [
    path("org_list/", views.get_org_list, name="org_list"),
]
