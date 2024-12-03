from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from .models import ClientUser
from .serializers import *
import random
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from .models import ClientUser
from .serializers import ClientUserSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model






@api_view(['POST'])
@permission_classes([AllowAny]) 
def input_phone_number(request):
    phone_number = request.data.get('phone_number')

    if not phone_number:
        return Response({'error': 'Номер телефона обязателен'}, status=400)

    try:
        # Пытаемся найти пользователя с этим номером
        user = ClientUser.objects.get(phone_number=phone_number)
        
        # Если у пользователя нет реферального кода, генерируем его
        if not user.referral_code:
            user.referral_code = generate_unique_referral_code()
            user.save()
    
    except ClientUser.DoesNotExist:
        # Если такого пользователя нет, создаем нового с уникальным кодом
        verification_code = str(random.randint(1000, 9999))
        referral_code = generate_unique_referral_code()

        # Создаем пользователя с verification_code и referral_code
        user = ClientUser.objects.create(
            phone_number=phone_number,
            verification_code=verification_code,
            referral_code=referral_code
        )

    # Сериализуем пользователя и возвращаем verification_code и referral_code
    serializer = ClientUserSerializer(user)
    return Response(serializer.data)


def generate_unique_referral_code():
    """
    Генерирует уникальный 6-значный реферальный код.
    """
    while True:
        referral_code = str(random.randint(100000, 999999))
        
        # Проверяем, существует ли уже такой код в базе данных
        if not ClientUser.objects.filter(referral_code=referral_code).exists():
            return referral_code





@api_view(['POST'])
@permission_classes([AllowAny]) 
def verify_code_and_login(request):
    verification_code = request.data.get('verification_code')

    if not verification_code:
        return Response({'error': 'Код подтверждения обязателен'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Пытаемся найти пользователя с данным verification_code
        user = ClientUser.objects.get(verification_code=verification_code)
    except ClientUser.DoesNotExist:
        return Response({'error': 'Неверный код подтверждения'}, status=status.HTTP_400_BAD_REQUEST)

    # Используем кастомный сериализатор для генерации токенов
    refresh = RefreshToken.for_user(user)
    access_token = refresh.access_token

    # Добавляем phone_number в payload токена
    access_token['phone_number'] = user.phone_number

    return Response({
        'access': str(access_token),
        'refresh': str(refresh),
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def refer_user(request):
    phone_number = request.data.get('phone_number')
    referral_code = request.data.get('referral_code')

    if not phone_number or not referral_code:
        return Response({'error': 'Номер телефона и реферальный код обязательны'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Найти пользователя по номеру телефона
        user = ClientUser.objects.get(phone_number=phone_number)
    except ClientUser.DoesNotExist:
        return Response({'error': 'Пользователь с таким номером телефона не существует'}, status=status.HTTP_404_NOT_FOUND)

    try:
        # Найти пользователя по реферальному коду
        referrer = ClientUser.objects.get(referral_code=referral_code)
    except ClientUser.DoesNotExist:
        return Response({'error': 'Реферальный код не существует'}, status=status.HTTP_404_NOT_FOUND)

    # Проверяем, чтобы пользователь не указал себя как реферала
    if user == referrer:
        return Response({'error': 'Нельзя указать себя как реферала'}, status=status.HTTP_400_BAD_REQUEST)

    # Обновляем поле `referred_by`
    user.referred_by = referrer
    user.save()

    # Сериализуем и возвращаем данные пользователя
    serializer = ClientUserSerializer(user)
    return Response(serializer.data, status=status.HTTP_200_OK)