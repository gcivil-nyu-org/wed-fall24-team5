from django.urls import path
from . import views

app_name = "messaging"

urlpatterns = [
    path("", views.messaging_view, name="messaging"),
    path("start-conversation/", views.start_conversation, name="start_conversation"),
    path("chat/<str:room_name>/", views.chat_room, name="chat_room"),
    # path('', views.create_room, name='create-room'),
    path("<str:room_name>/<str:username>/", views.message_view, name="room"),
]
