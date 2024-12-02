from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.core.mail import send_mail
from django.core.validators import RegexValidator
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class CustomUserManager(BaseUserManager):
    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError("Пользователь должен указать номер телефона.")
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

        return self.create_user(phone_number, password, **extra_fields)


class CustomAbstractUser(AbstractBaseUser, PermissionsMixin):
    """
    Абстрактный класс для кастомной модели пользователя.
    """

    phone_number = models.CharField(
        _("номер телефона"),
        max_length=15,
        unique=True,
        validators=[
            RegexValidator(
                regex=r"^\+?1?\d{9,15}$",
                message=_(
                    "Введите корректный номер телефона. "
                    "Он должен содержать от 9 до 15 цифр."
                ),
            )
        ],
    )
    is_staff = models.BooleanField(
        _("статус персонала"),
        default=False,
        help_text=_("Определяет, может ли пользователь входить в административный сайт."),
    )
    is_active = models.BooleanField(
        _("активный"),
        default=True,
        help_text=_(
            "Определяет, следует ли считать этого пользователя активным. "
            "Снимите галочку вместо удаления учетных записей."
        ),
    )
    date_joined = models.DateTimeField(_("дата регистрации"), default=timezone.now)

    objects = CustomUserManager()
    USERNAME_FIELD = "phone_number"  
    REQUIRED_FIELDS = []  
    class Meta:
        verbose_name = _("Пользователь")
        verbose_name_plural = _("Пользователи")
        abstract = True

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Отправить письмо пользователю."""
        send_mail(subject, message, from_email, [self.phone_number], **kwargs)


class CustomUser(CustomAbstractUser):
    """
    Модель для кастомного пользователя.
    """

    class Meta(CustomAbstractUser.Meta):
        swappable = "AUTH_USER_MODEL"
