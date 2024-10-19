"""
URL configuration for src project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.shortcuts import redirect
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("google/accounts/", include("allauth.urls")),
    path("", include("django.contrib.auth.urls")),
    path("accounts/", include("accounts.urls", namespace="accounts")),
    path("recipient_dashboard/", include("recipient_dashboard.urls")),
    path("donor_dashboard/", include("donor_dashboard.urls")),
    # Redirect the root URL to the login page
    path("", lambda request: redirect("accounts/landing")),
    path("database/", include("database.urls")),
    path("organization/", include("donor_dashboard.urls", namespace="organization")),
    path("recipient_orders/", include("recipient_orders.urls")),
]
