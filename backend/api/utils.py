from django.http import HttpResponse


def create_shopping_cart(ingredients):
    shopping = 'Необходимо приобрести:'
    shopping += '\n'.join([
        f"{ingredient['ingredient__name']}-{ingredient['ingredient_total']}/"
        f"{ingredient['ingredient__measurement_unit']}"
        for ingredient in ingredients
    ])
    file = 'shopping.txt'
    response = HttpResponse(shopping, content_type='text/plain')
    response['Content-Disposition'] = f'attachment; filename={file}'
    return response
