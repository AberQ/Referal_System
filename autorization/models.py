from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import *
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.validators import *
from django.core.mail import send_mail
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
import unicodedata
from django.core.exceptions import ValidationError

import random
from django.conf import settings
from django.contrib.auth import password_validation
from django.contrib.auth.hashers import (
    acheck_password,
    check_password,
    is_password_usable,
    make_password,
)
from django.db import models
from django.utils.crypto import salted_hmac
from django.utils.translation import gettext_lazy as _

class CustomUserManagerForAdmin(BaseUserManager):


    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Суперпользователь должен иметь is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Суперпользователь должен иметь is_superuser=True.")

       

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user


class CustomAbstractUserForAdmin(AbstractBaseUser, PermissionsMixin):
    """
    An abstract base class implementing a fully featured User model with
    admin-compliant permissions.

    Username and password are required. Other fields are optional.
    """

    email = models.EmailField(_("email address"), blank=False, unique=True)
    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into this admin site."),
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)

    objects = CustomUserManagerForAdmin()
    USERNAME_FIELD = "email"  
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _("Админ")
        verbose_name_plural = _("Админы")
        abstract = True

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)


class Admin(CustomAbstractUserForAdmin):
    """
    Users within the Django authentication system are represented by this
    model.

    Username and password are required. Other fields are optional.
    """

    class Meta(CustomAbstractUserForAdmin.Meta):
        swappable = "AUTH_USER_MODEL"

class CustomAbstractBaseUser_Clients(models.Model):
    last_login = models.DateTimeField(_("last login"), blank=True, null=True)

    is_active = True

    REQUIRED_FIELDS = []

    # Stores the raw password if set_password() is called so that it can
    # be passed to password_changed() after the model is saved.
    

    class Meta:
        abstract = True

    def __str__(self):
        return self.get_username()

    # RemovedInDjango60Warning: When the deprecation ends, replace with:
    # def save(self, **kwargs):
    #   super().save(**kwargs)
 

    def get_username(self):
        """Return the username for this User."""
        return getattr(self, self.USERNAME_FIELD)

    def clean(self):
        setattr(self, self.USERNAME_FIELD, self.normalize_username(self.get_username()))

    def natural_key(self):
        return (self.get_username(),)

    @property
    def is_anonymous(self):
        """
        Always return False. This is a way of comparing User objects to
        anonymous users.
        """
        return False

    @property
    def is_authenticated(self):
        """
        Always return True. This is a way to tell if the user has been
        authenticated in templates.
        """
        return True






    


  




    def get_session_auth_hash(self):
        """
        Return an HMAC of the password field.
        """
        return self._get_session_auth_hash()

    def get_session_auth_fallback_hash(self):
        for fallback_secret in settings.SECRET_KEY_FALLBACKS:
            yield self._get_session_auth_hash(secret=fallback_secret)

    def _get_session_auth_hash(self, secret=None):
        key_salt = "django.contrib.auth.models.AbstractBaseUser.get_session_auth_hash"
        return salted_hmac(
            key_salt,
      
            secret=secret,
            algorithm="sha256",
        ).hexdigest()

    @classmethod
    def get_email_field_name(cls):
        try:
            return cls.EMAIL_FIELD
        except AttributeError:
            return "email"

    @classmethod
    def normalize_username(cls, username):
        return (
            unicodedata.normalize("NFKC", username)
            if isinstance(username, str)
            else username
        )



class CustomUserManagerForClients(BaseUserManager):
    """
    Менеджер для создания обычных пользователей.
    """
    def create_user(self, phone_number, **extra_fields):
        if not phone_number:
            raise ValueError(_("Номер телефона обязателен"))
        verification_code = str(random.randint(1000, 9999))
        user = self.model(phone_number=phone_number, **extra_fields)
        user.save(using=self._db)
        return user
    

class ClientUser(CustomAbstractBaseUser_Clients):
    phone_number = models.CharField(_("номер телефона"), max_length=15, unique=True)
    is_active = models.BooleanField(_("активен"), default=True)
    date_joined = models.DateTimeField(_("дата регистрации"), default=timezone.now)
    verification_code = models.CharField(_("код подтверждения"), max_length=4, null=True, blank=True)
    referral_code = models.CharField(_("реферальный код"), max_length=6, null=True, blank=True, unique=True)

    referred_by = models.ForeignKey(
        'self', 
        null=True, 
        blank=True, 
        related_name='referrals', 
        on_delete=models.SET_NULL
    )

    objects = CustomUserManagerForClients()

    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _("Обычный пользователь")
        verbose_name_plural = _("Обычные пользователи")

    def __str__(self):
        return self.phone_number

    def generate_unique_referral_code(self):
        """Генерирует уникальный 6-значный реферальный код."""
        while True:
            referral_code = str(random.randint(100000, 999999))
            if not ClientUser.objects.filter(referral_code=referral_code).exists():
                return referral_code

    def clean(self):
        """
        Добавляем проверки для поля `referred_by`:
        - Пользователь не может указать себя как пригласившего.
        - Один пользователь может быть приглашен только одним другим пользователем.
        """
        super().clean()

        # Проверка: пользователь не может указать себя как пригласившего
        if self.referred_by and self.referred_by == self:
            raise ValidationError(_("Пользователь не может быть указан как пригласивший сам себя."))

        # Проверка: уже существует пользователь, который указал данный `referral_code`
        if self.referred_by and ClientUser.objects.filter(referred_by=self).exists():
            raise ValidationError(_("Пользователь уже имеет пригласившего. Нельзя указать несколько."))

    def save(self, *args, **kwargs):
        # Дополнительная проверка на уровне сохранения
        self.clean()
        super().save(*args, **kwargs)