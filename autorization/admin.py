from django.contrib import admin
from .models import Admin, ClientUser

# Админка для модели Admin
class AdminAdmin(admin.ModelAdmin):
    list_display = ('email', 'is_active', 'is_staff', 'date_joined')  # Какие поля будут отображаться в списке
    search_fields = ('email',)  # По каким полям можно будет искать
    list_filter = ('is_active', 'is_staff')  # Фильтры для списка
    ordering = ('date_joined',)  # Сортировка по умолчанию

# Админка для модели ClientUser
class ClientUserAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'is_active', 'date_joined')  # Поля, отображаемые в списке
    search_fields = ('phone_number',)  # Поиск по номеру телефона
    list_filter = ('is_active',)  # Фильтры для списка
    ordering = ('date_joined',)  # Сортировка по дате регистрации

# Регистрация моделей и их админок
admin.site.register(Admin, AdminAdmin)
admin.site.register(ClientUser, ClientUserAdmin)
