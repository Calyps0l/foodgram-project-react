from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from foodgram.models import (Favorite, Ingredient, IngredientInRecipe, Recipe,
                             ShoppingCart, Tag)
from rest_framework import status, viewsets, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from users.models import Subscribe, User
from .filters import IngredientFilter, RecipeFilter
from .permissions import AuthorOrReadOnly
from .serializers import (CustomUserSerializer,
                          SubscribeSerializer, TagSerializer,
                          FavoriteSerializer, IngredientSerializer,
                          RecipeReadSerializer, RecipeWriteSerializer)
from .pagination import PagePagination


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_class = IngredientFilter
    search_fields = ('^name',)
    pagination_class = None


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer

    @action(detail=False,
            methods=['GET'],
            permission_classes=(IsAuthenticated,))
    def subscriptions(self, request):
        user = self.request.user
        queryset = Subscribe.objects.filter(user=user)
        pages = self.paginate_queryset(queryset)
        serializer = SubscribeSerializer(
            pages,
            many=True,
            context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(detail=True,
            methods=['POST', 'DELETE'],
            permission_classes=(IsAuthenticated,))
    def subscribe(self, request, id):
        author = get_object_or_404(User, id=id)
        if request.method == 'POST':
            if request.user.id == author.id:
                raise serializers.ValidationError(
                    detail='Нельзя подписаться на самого себя')
            else:
                serializer = SubscribeSerializer(
                    Subscribe.objects.create(user=request.user, author=author),
                    context={'request': request})
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            if Subscribe.objects.filter(user=request.user, author=author).exists():
                Subscribe.objects.filter(
                    user=request.user,
                    author=author).delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all().order_by('-id')
    permission_classes = (AuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_class = RecipeFilter
    pagination_class = PagePagination

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeReadSerializer
        return RecipeWriteSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def add_recipe(self, model, user, pk):
        if model.objects.filter(user=user, recipe__id=pk).exists():
            return Response({
                'Рецепт уже добавлен'
            }, status=status.HTTP_400_BAD_REQUEST)
        recipe = get_object_or_404(Recipe, id=pk)
        model.objects.create(user=user, recipe=recipe)
        serializer = FavoriteSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_recipe(self, model, user, pk):
        obj = model.objects.filter(user=user, recipe__id=pk)
        if obj.exists():
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({
            'Рецепт уже удален'
        }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True,
            methods=['POST', 'DELETE'],
            url_path='favorite',
            permission_classes=(IsAuthenticated,))
    def favorite(self, request, pk=None):
        if request.method == 'POST':
            return self.add_recipe(Favorite, request.user, pk)
        else:
            return self.delete_recipe(Favorite, request.user, pk)

    @action(detail=True,
            methods=['POST', 'DELETE'],
            url_path='shopping_cart',
            permission_classes=(IsAuthenticated,))
    def shopping_cart(self, request, pk=None):
        if request.method == 'POST':
            return self.add_recipe(ShoppingCart, request.user, pk)
        else:
            return self.delete_recipe(ShoppingCart, request.user, pk)

    @staticmethod
    def report(ingredients):
        shopping = 'Необходимо приобрести:'
        for ingredient in ingredients:
            shopping += (
                f"{ingredient['ingredient__name']} - "
                f"{ingredient['ingredient_total']} "
                f"({ingredient['ingredient__measurement_unit']}) \n")
        file = 'shopping.txt'
        response = HttpResponse(shopping, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={file}'
        return response


