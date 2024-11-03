from django.urls import path
from . import views

app_name = "messaging"

urlpatterns = [
    path("", views.messaging_view, name="messaging"),
    path("start-conversation/", views.start_conversation, name="start_conversation"),
]
