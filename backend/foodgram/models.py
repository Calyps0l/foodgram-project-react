from colorfield.fields import ColorField
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()


class Tag(models.Model):
    """
    Модель добавления тэгов.
    """
    name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Тэг',
        help_text='Введите наименование тэга'
    )
    color = ColorField(
        max_length=7,
        unique=True,
        verbose_name='Цвет',
        help_text='Выберите цвет'
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='Индентификатор страницы',
        help_text='Укажите индентификатор страницы'
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """
    Модель добавления ингредиентов.
    """
    name = models.CharField(
        max_length=200,
        verbose_name='Ингредиент',
        help_text='Введите название ингредиента'
    )
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='Единица измерения',
        help_text='Укажите единицу измерения'
    )

    class Meta:
        verbose_name = 'Ингредиент',
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class IngredientInRecipe(models.Model):
    """
    Модель добавления ингредиентов в рецепт.
    """
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredientrecipe',
        verbose_name='Ингредиент'
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        validators=[
            MinValueValidator(1, 'Укажите более 1 ингредиента')
        ],
        help_text='Укажите количество ингредиентов'
    )

    class Meta:
        verbose_name = 'Количество ингредиентов'
        verbose_name_plural = 'Количество ингредиентов'
        ordering = ('id',)
        constraints = [
            models.UniqueConstraint(
                fields=('ingredient', 'amount'),
                name='unique_ingredient_in_recipe')]

    def __str__(self):
        return (
            f'{self.ingredient.name} - {self.amount}'
            f' ({self.ingredient.measurement_unit})'
        )


class Recipe(models.Model):
    """
    Модель добавления новых рецептов.
    """
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        null=True,
        verbose_name='Автор'
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Рецепт',
        help_text='Введите название рецепта'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Тэг',
        help_text='Добавьте тэги'
    )
    ingredients = models.ManyToManyField(
        IngredientInRecipe,
        related_name='recipes',
        verbose_name='Ингредиенты',
        help_text='Добавьте ингредиенты'
    )
    image = models.ImageField(
        verbose_name='Картинка',
        blank=True,
        null=True,
        help_text='Загрузите картинку рецепта',
        upload_to='recipes/'
    )
    text = models.TextField(
        verbose_name='Описание',
        help_text='Введите описание рецепта'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления (минуты)',
        validators=[
            MinValueValidator(1, 'Укажите время больше 1 минуты')
        ],
        help_text='Укажите время приготовления (минуты)'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.name


class Favorite(models.Model):
    """
    Модель добавления рецепта в избранное.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite_user',
        verbose_name='Подписчик'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorite_recipe',
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_favorite')]

    def __str__(self):
        return f'{self.user} добавил {self.recipe} в избранное'


class ShoppingCart(models.Model):
    """
    Модель добавления рецепта в корзину покупок.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart_user',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_cart_recipe',
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'Корзина покупок'
        verbose_name_plural = 'Корзины покупок'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_shopping_cart')]

    def __str__(self):
        return f'{self.user} добавил {self.recipe} в корзину покупок'
