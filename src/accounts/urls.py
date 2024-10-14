from django.urls import path
from . import views

app_name = "accounts"  # pylint: disable=invalid-name

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("profile/", views.profile_view, name="profile"),
    path("logout/", views.logout_view, name="logout"),
    path("landing/", views.landing_view, name="landing"),
]
