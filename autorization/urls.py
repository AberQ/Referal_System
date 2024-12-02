from django.urls import path
from . import views
from .views import *
urlpatterns = [
    path('api/verification-code/', get_verification_code, name='get_verification_code'),
]