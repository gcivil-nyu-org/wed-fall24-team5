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
    path(
        "room/<str:room_id>/get_new_messages/",
        views.get_new_messages,
        name="get_new_messages",
    ),
    path("room/<str:room_id>/send_message/", views.send_message, name="send_message"),
    path(
        "org/<str:organization_id>/room/<str:room_id>/get_new_messages/",
        views.org_get_new_messages,
        name="org_get_new_messages",
    ),
    path(
        "org/<str:organization_id>/room/<str:room_id>/send_message/",
        views.org_send_message,
        name="org_send_message",
    ),
]
