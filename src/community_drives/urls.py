from django.urls import path
from . import views

app_name = "community_drives"  # pylint: disable=invalid-name

urlpatterns = [
    path("", views.get_drive_list, name="drive_list"),
]
