from django.urls import path
from . import views

app_name = "messaging"

urlpatterns = [
    path("", views.messaging_view, name="messaging"),
    path(
        "org/<uuid:organization_id>/",
        views.org_messaging_view,
        name="org_messaging_view",
    ),
    path("start-conversation/", views.start_conversation, name="start_conversation"),
    path("room/<str:room_id>/", views.get_messages, name="get_messages"),
    path(
        "org/<str:organization_id>/room/<str:room_id>/",
        views.org_get_messages,
        name="org_get_messages",
    ),
]
