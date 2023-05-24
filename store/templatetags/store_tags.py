from django import template
from store.models import Category

register = template.Library()


@register.simple_tag()
def get_categories():
    return Category.objects.filter(parent=None)


@register.simple_tag()
def get_sorted():
    sorters = [
        {
            'title': 'By Price',
            'sorters': [
                ('price', 'Ascending'),
                ('-price', 'Descending')
            ]

        },
        {
            'title': 'By Color',
            'sorters': [
                ('color', 'From A to Z'),
                ('-color', 'From Z to A')
            ]

        },
        {
            'title': 'By Size',
            'sorters': [
                ('size', 'Ascending'),
                ('-size', 'Descending')
            ]

        },
    ]

    return sorters


@register.simple_tag()
def get_subcategories(category):
    return Category.objects.filter(parent=category)

