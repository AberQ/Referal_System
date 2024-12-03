from django.contrib import admin
from django.core.exceptions import ValidationError
from django.contrib import messages
from .models import Admin, ClientUser

# Админка для модели Admin
class AdminAdmin(admin.ModelAdmin):
    list_display = ('email', 'is_active', 'is_staff', 'date_joined')  # Поля, отображаемые в списке
    search_fields = ('email',)  # Поиск по email
    list_filter = ('is_active', 'is_staff')  # Фильтры для списка
    ordering = ('date_joined',)  # Сортировка по дате регистрации

# Админка для модели ClientUser
class ClientUserAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'referred_by', 'is_active', 'date_joined')  # Поля для отображения в списке
    search_fields = ('phone_number', 'referred_by__phone_number')  # Поиск по номеру телефона и пригласителю
    list_filter = ('is_active',)  # Фильтр по активности
    ordering = ('date_joined',)  # Сортировка по дате регистрации
    autocomplete_fields = ('referred_by',)  # Автозаполнение для поля пригласителя

    def save_model(self, request, obj, form, change):
        """
        Переопределение сохранения объекта для проверки валидации.
        """
        try:
            obj.clean()  # Вызываем метод clean для проверки
            super().save_model(request, obj, form, change)
        except ValidationError as e:
            self.message_user(request, f"Ошибка: {e.message}", level=messages.ERROR)

# Регистрация моделей и их админок
admin.site.register(Admin, AdminAdmin)
admin.site.register(ClientUser, ClientUserAdmin)
