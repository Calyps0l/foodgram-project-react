from django.contrib import admin

from .models import (Favorite, Ingredient, IngredientInRecipe, Recipe,
                     ShoppingCart, Tag)


class IngredientInline(admin.TabularInline):
    model = IngredientInRecipe
    extra = 3
    min_num = 1


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """
    Модель редактирования ингредиентов
    в зоне администратора.
    """
    list_display = ('name', 'measurement_unit',)
    list_filter = ('name', )
    empty_value_display = '-пусто-'


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """
    Модель редактирования рецептов
    в зоне администратора.
    """
    inlines = (IngredientInline, )
    list_display = ('name', 'author', 'add_favorites')
    readonly_fields = ('add_favorites',)
    list_filter = ('name', 'author', 'tags')
    empty_value_display = '-пусто-'

    def add_favorites(self, obj):
        return obj.favorite_recipe.count()


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """
    Модель редактирования тэгов
    в зоне администратора.
    """
    list_display = ('name', 'color', 'slug',)
    list_filter = ('name', )
    empty_value_display = '-пусто-'


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """
    Модель редактирования корзины
    покупок в зоне администратора.
    """
    list_display = ('user', 'recipe',)
    list_filter = ('user', )
    empty_value_display = '-пусто-'


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """
    Модель редактирования избранных
    рецептов в зоне администратора.
    """
    list_display = ('user', 'recipe',)
    list_filter = ('user', 'recipe',)
    empty_value_display = '-пусто-'


@admin.register(IngredientInRecipe)
class IngredientInRecipeAdmin(admin.ModelAdmin):
    """
    Модель редактирования ингредиентов
    в рецептах в зоне администратора.
    """
    list_display = ('ingredient', 'amount')
    empty_value_display = '-пусто-'
