from django.contrib import admin
from django.shortcuts import render
from django.utils.safestring import mark_safe
from .models import *
from modeltranslation.admin import TranslationAdmin


# Register your models here.
class GalleryInline(admin.TabularInline):
    fk_name = 'product'
    model = Gallery
    extra = 4


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_select_related = ('parent',)
    list_display = (
        'title',
        'parent',
        'get_products_count',
    )
    prepopulated_fields = {'slug': ('title',)}

    def get_products_count(self, obj):
        if obj.product:
            return str(len(obj.product.all()))
        else:
            return '0'

    get_products_count.short_description = 'Quantity of products'


@admin.register(Product)
# class ProductAdmin(TranslationAdmin):
class ProductAdmin(admin.ModelAdmin):
    list_display = ['pk',
                    'title',
                    'category',
                    'price',
                    'quantity',
                    'color',
                    'material',
                    'get_photo',
                    'status',
                    'created_at',
                    ]
    list_display_links = ['title']
    list_editable = ['price', 'quantity', 'color', 'material']
    list_filter = ['title', 'price', 'quantity', 'color', 'material', 'category']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [GalleryInline]

    def get_photo(self, obj):
        if obj.images:
            try:
                return mark_safe(f'<img src="{obj.images.all()[0].image.url}"width= "50">')
            except:
                return '-'
        else:
            return '-'

    get_photo.short_description = 'Miniature'


# admin.site.register(Product, ProductAdmin)
admin.site.register(Gallery)
admin.site.register(Customer)
admin.site.register(Order)
admin.site.register(OrderProduct)
admin.site.register(ShippingAddress)
admin.site.register(ProductType)
admin.site.register(ProductSpecification)
admin.site.register(ProductSpecificationValue)
