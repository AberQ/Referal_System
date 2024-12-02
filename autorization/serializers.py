from .models import *
from rest_framework import serializers


class ClientUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientUser
        fields = ['phone_number', 'verification_code', 'referral_code']