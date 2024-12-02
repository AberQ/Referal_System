from django.urls import path
from . import views
from .views import *
urlpatterns = [
    path('api/input_phone_number/', input_phone_number, name='get_verification_code'),
]