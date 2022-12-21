from django.db import transaction
from drf_base64.fields import Base64ImageField
from rest_framework import serializers

from foodgram.models import (Favorite, Ingredient, IngredientInRecipe,
                             Recipe, ShoppingCart, Tag)
from users.models import Subscribe, User


class CustomUserSerializer(serializers.ModelSerializer):
    """
    Сериализатор модели пользователя.
    """
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed',)

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if self.context.get('request').user.is_anonymous:
            return False
        return Subscribe.objects.filter(
            user=request.user, author=obj).exists()


class IngredientSerializer(serializers.ModelSerializer):
    """
    Сериализатор модели игредиентов.
    """
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class TagSerializer(serializers.ModelSerializer):
    """
    Сериализатор модели тэгов.
    """
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug',)


class SubscribeSerializer(serializers.ModelSerializer):
    """
    Сериализатор модели подписок.
    """
    email = serializers.ReadOnlyField(source='author.email')
    id = serializers.ReadOnlyField(source='author.id')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count',)

    def get_is_subscribed(self, obj):
        return Subscribe.objects.filter(
            user=obj.user,
            author=obj.author
        ).exists()

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(
            author=obj.author
        ).count()

    def get_recipes(self, obj):
        queryset = (
            Recipe.objects.filter(
                author=obj.author).order_by('-pub_date'))
        return SubscribeRecipeSerializer(queryset, many=True).data


class SubscribeRecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор полей избранных рецептов.
    """
    image = Base64ImageField(max_length=None)

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор связи ингредиентов и рецептов.
    """
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all())
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')
    amount = serializers.IntegerField(required=True)

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount',)


class RecipeReadSerializer(serializers.ModelSerializer):
    """
    Сериализатор просмотра рецептов.
    """
    tags = TagSerializer(many=True, read_only=False)
    author = CustomUserSerializer(many=False, read_only=True)
    ingredients = IngredientInRecipeSerializer(
        many=True,
        source='ingredientrecipe')
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image',
                  'text', 'cooking_time')

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Favorite.objects.filter(
            recipe=obj,
            user=request.user
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(
            recipe=obj,
            user=request.user
        ).exists()


class RecipeWriteSerializer(serializers.ModelSerializer):
    """
    Сериализатор создания рецептов.
    """
    author = CustomUserSerializer(read_only=True, required=False)
    ingredients = IngredientInRecipeSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all())
    image = Base64ImageField(max_length=None, use_url=True)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'name',
                  'image', 'text', 'cooking_time',)

    def validate_ingredients(self, data):
        ingredients = self.initial_data.get('ingredients')
        if not ingredients:
            raise serializers.ValidationError(
                detail='Отсутствуют ингредиенты')
        for ingredient in ingredients:
            if int(ingredient.get('amount')) <= 0:
                raise serializers.ValidationError(
                    detail='Минимум один ингредиент')
            id_check = ingredient['id']
            ingr_check = Ingredient.objects.filter(id=id_check)
            if not ingr_check.exists():
                raise serializers.ValidationError(
                    detail='Данный ингредиент отсутствует в базе данных')
        return data

    def validate_cooking_time(self, data):
        cooking_time = self.initial_data.get('cooking_time')
        if int(cooking_time) < 1:
            raise serializers.ValidationError(
                detail='Время приготовления не меньше минуты')
        return data

    def validate_tags(self, data):
        tags = self.initial_data.get('tags')
        if not tags:
            raise serializers.ValidationError(
                detail='Отсутствует тэг')
        for tag in tags:
            if not Tag.objects.filter(id=tag).exists():
                raise serializers.ValidationError(
                    detail='Указанный тэг отсутствует в базе данных')
        return data

    def create_ingredients(self, ingredients, recipe):
        list_ingredient = []
        for ingredient_data in ingredients:
            list_ingredient.append(
                IngredientInRecipe(
                    ingredient=ingredient_data.pop('id'),
                    amount=ingredient_data.pop('amount'),
                    recipe=recipe,
                )
            )
        IngredientInRecipe.objects.bulk_create(list_ingredient)

    @transaction.atomic
    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(ingredients, recipe)
        return recipe

    @transaction.atomic
    def update(self, recipe, validated_data):
        if 'ingredients' in validated_data:
            ingredients = validated_data.pop('ingredients')
            recipe.ingredients.clear()
            self.create_ingredients(ingredients, recipe)
        if 'tags' in validated_data:
            tags_data = validated_data.pop('tags')
            recipe.tags.set(tags_data)
        return super().update(recipe, validated_data)

    def to_representation(self, recipe):
        serializer = RecipeReadSerializer(
            recipe,
            context=self.context)
        return serializer.data


class ShoppingCartSerializer(serializers.ModelSerializer):
    """
    Сериализатор корзины покупок.
    """
    id = serializers.CharField(read_only=True, source='recipe.id')
    name = serializers.CharField(read_only=True, source='recipe.name')
    image = serializers.CharField(read_only=True, source='recipe.image')
    cooking_time = serializers.CharField(
        read_only=True,
        source='recipe.cooking_time')

    class Meta:
        model = ShoppingCart
        fields = ('id', 'name', 'image', 'cooking_time')


class FavoriteSerializer(serializers.ModelSerializer):
    """
    Сериализатор избранных рецепртов.
    """
    id = serializers.CharField(read_only=True, source='recipe.id')
    name = serializers.CharField(read_only=True, source='recipe.name')
    image = serializers.CharField(read_only=True, source='recipe.image')
    cooking_time = serializers.CharField(
        read_only=True,
        source='recipe.cooking_time')

    def validate(self, data):
        user = data['user']
        recipe = data['recipe']
        if Favorite.objects.filter(recipe=recipe, user=user).exists():
            raise serializers.ValidationError(
                detail='Рецепт уже находится в избранном')
        if user == recipe.author:
            raise serializers.ValidationError(
                detail='Нельзя добавить свои рецепты в избранное')
        return data

    class Meta:
        model = Favorite
        fields = ('id', 'name', 'image', 'cooking_time')
