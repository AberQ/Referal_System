from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from random import randint
from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    
    list_display = ("phone_number", "is_staff", "is_active", "date_joined", "confirmation_code")
    search_fields = ("phone_number",)
    list_filter = ("is_staff", "is_active", "date_joined")

    # Отображение полей в форме редактирования пользователя
    fieldsets = (
        (None, {"fields": ("phone_number", "password")}),
        (_("Personal info"), {"fields": ()}),
        (_("Permissions"), {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
        (_("Confirmation"), {"fields": ("confirmation_code",)}),  # Добавляем confirmation_code
    )
    
    # Формы для добавления нового пользователя
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("phone_number", "password1", "password2", "is_staff", "is_active", "confirmation_code"),
        }),
    )
    
    ordering = ("phone_number",)

    # Генерация кода подтверждения при добавлении нового пользователя
    def save_model(self, request, obj, form, change):
        if not obj.pk:  # Это новый пользователь
            obj.confirmation_code = f"{randint(1000, 9999)}"  # Генерация кода подтверждения
        super().save_model(request, obj, form, change)


admin.site.register(CustomUser, CustomUserAdmin)
