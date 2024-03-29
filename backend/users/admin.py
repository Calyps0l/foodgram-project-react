from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Subscribe, User


@admin.register(User)
class UserAdmin(UserAdmin):
    """
    Модель редактирования списка
    пользователей в зоне администратора.
    """
    list_display = ('username', 'id', 'first_name',
                    'last_name', 'email')
    list_filter = ('email', 'first_name')
    empty_value_display = '-пусто-'


@admin.register(Subscribe)
class SubscribeAdmin(admin.ModelAdmin):
    """
    Модель редактирования подписок
    в зоне администратора.
    """
    list_display = ('user', 'author')
    empty_value_display = '-пусто-'
