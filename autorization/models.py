from random import randint
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.core.mail import send_mail
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class CustomBaseUserManager(models.Manager):
    @classmethod
    def normalize_phone_number(cls, phone_number):
        """
        Normalize the phone number by removing unnecessary characters.
        """
        return phone_number.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")

    def get_by_natural_key(self, phone_number):
        return self.get(**{self.model.USERNAME_FIELD: phone_number})


class CustomUserManager(CustomBaseUserManager):
    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError("Пользователь должен указать номер телефона.")
        phone_number = self.normalize_phone_number(phone_number)
        
        # Генерация 4-значного кода
        confirmation_code = f"{randint(1000, 9999)}"
        extra_fields.setdefault("confirmation_code", confirmation_code)

        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Суперпользователь должен иметь is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Суперпользователь должен иметь is_superuser=True.")

        phone_number = self.normalize_phone_number(phone_number)
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user


class CustomAbstractUser(AbstractBaseUser, PermissionsMixin):
    """
    An abstract base class implementing a fully featured User model with
    admin-compliant permissions.

    Phone number and password are required. Other fields are optional.
    """

    phone_number = models.CharField(
        _("номер телефона"), max_length=15, unique=True, blank=False
    )
    is_staff = models.BooleanField(
        _("статус персонала"),
        default=False,
        help_text=_("Обозначает, может ли пользователь входить в административный сайт."),
    )
    is_active = models.BooleanField(
        _("активный"),
        default=True,
        help_text=_(
            "Обозначает, должен ли пользователь считаться активным. "
            "Снимите этот флажок вместо удаления учетных записей."
        ),
    )
    date_joined = models.DateTimeField(_("дата регистрации"), default=timezone.now)

    objects = CustomUserManager()

    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _("пользователь")
        verbose_name_plural = _("пользователи")
        abstract = True

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Отправить email пользователю (если нужно оставить функционал)."""
        send_mail(subject, message, from_email, [self.phone_number], **kwargs)


class CustomUser(CustomAbstractUser):
    """
    Пользователи внутри системы аутентификации Django представлены этой моделью.
    """
    confirmation_code = models.CharField(
        _("код подтверждения"),
        max_length=4,
        blank=True,
        null=True,
        help_text=_("4-значный код подтверждения для регистрации."),
    )

    class Meta(CustomAbstractUser.Meta):
        swappable = "AUTH_USER_MODEL"
