from .models import *
from modeltranslation.translator import translator, TranslationOptions, register


#@register(Product)
class ProductTranslationOptions(TranslationOptions):
    fields = ['title', 'description', 'color']


translator.register(Product, ProductTranslationOptions)
