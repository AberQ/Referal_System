from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    
    list_display = ("phone_number", "is_staff", "is_active", "date_joined")
   
    search_fields = ("phone_number",)
  
    list_filter = ("is_staff", "is_active", "date_joined")

   
    fieldsets = (
        (None, {"fields": ("phone_number", "password")}),
        (_("Personal info"), {"fields": ()}),  
        (_("Permissions"), {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("phone_number", "password1", "password2", "is_staff", "is_active"),
        }),
    )
    ordering = ("phone_number",)



admin.site.register(CustomUser, CustomUserAdmin)
