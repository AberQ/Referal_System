from .models import *
from rest_framework import serializers


class ClientUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientUser
        fields = ['id','phone_number', 'verification_code', 'referral_code', 'referred_by_id', ]