from django.urls import path
from . import views

urlpatterns = [
    path('test-database/', views.test_database_view, name='test_database'), 
]
