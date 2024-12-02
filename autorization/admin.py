from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import Admin


class CustomUserAdmin(UserAdmin):
    # Поля, отображаемые в списке пользователей
    list_display = ("email", "is_staff", "is_active", "date_joined")
    list_filter = ("is_staff", "is_active", "is_superuser", "date_joined")
    ordering = ("email",)
    search_fields = ("email",)

    # Поля для редактирования пользователя
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Personal info"), {"fields": ()}),  # Дополнительные персональные поля можно добавить здесь
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )

    # Поля для создания нового пользователя
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2", "is_staff", "is_active"),
            },
        ),
    )


# Регистрация модели и кастомного UserAdmin
admin.site.register(Admin, CustomUserAdmin)
