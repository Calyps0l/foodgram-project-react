import json

from django.core.management import BaseCommand

from foodgram.models import Tag


class Command(BaseCommand):
    """
    Загружаем тэги из файла JSON.
    """

    def handle(self, *args, **options):
        with open('data/tag.json', encoding='utf-8') as file:
            data = json.loads(file.read())
            for tag in data:
                Tag.objects.get_or_create(**tag)
        self.stdout.write(self.style.SUCCESS('Загрузка тэгов завершена'))
