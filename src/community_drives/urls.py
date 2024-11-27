from django.urls import path
from . import views

app_name = "community_drives"  # pylint: disable=invalid-name

urlpatterns = [
    path("", views.get_drive_list, name="drive_list"),
    path("drive/<uuid:drive_id>/", views.drive_dashboard, name="drive_dashboard"),
    path(
        "drives/<uuid:drive_id>/contribute/",
        views.contribute_to_drive,
        name="contribute_to_drive",
    ),
]
