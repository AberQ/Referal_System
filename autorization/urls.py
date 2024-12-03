from django.urls import path
from . import views
from .views import *
urlpatterns = [
    path('api/input_phone_number/', input_phone_number, name='get_verification_code'),
    path('api/verify_code', verify_code_and_login, name='verify_code_and_login'),
    #path('api/input_refferal_code', input_referral_code, name='input_referral_code'),
]