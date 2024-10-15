from django.urls import path
from . import views

app_name = "organization"  # pylint: disable=invalid-name

urlpatterns = [
    path("add-organization/", views.add_organization, name="add_organization"),
]
