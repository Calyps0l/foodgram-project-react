import json

from django.core.management import BaseCommand
from foodgram.models import Ingredient


class Command(BaseCommand):
    """
    Загружаем ингредиенты из файла JSON.
    """

    def handle(self, *args, **options):
        with open('data/ingredients.json', encoding='utf-8') as file:
            data = json.loads(file.read())
            for ingredient in data:
                Ingredient.objects.get_or_create(**ingredient)
        self.stdout.write(self.style.SUCCESS('Загрузка ингредиентов завершена'))
