from django.urls import path
from .views_auth import register

urlpatterns = [
    path('', register, name='register'),
]
