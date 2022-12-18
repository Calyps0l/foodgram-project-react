from django_filters import rest_framework as filters
from foodgram.models import Ingredient, Recipe


class IngredientFilter(filters.FilterSet):
    """
    Класс для фильтрации списка ингредиентов.
    """
    name = filters.CharFilter(
        field_name='name',
        lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(filters.FilterSet):
    """
    Класс для фильтрации списка
    рецептов по тэгам, нахождению
    в корзине и избранных рецептах.
    """
    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')
    is_in_shopping_cart = filters.BooleanFilter(
        field_name='is_in_shopping_cart',
        method='filter')
    is_favorited = filters.BooleanFilter(
        field_name='is_favorited',
        method='filter')

    def filter(self, queryset, name, value):
        if name == 'is_favorited' and value:
            queryset = queryset.filter(
                favorite_recipe__user=self.request.user)
        if name == 'is_in_shopping_cart' and value:
            queryset = queryset.filter(
                shopping_cart_recipe__user=self.request.user)
        return queryset

    class Meta:
        model = Recipe
        fields = ('is_favorited', 'is_in_shopping_cart', 'author', 'tags',)
