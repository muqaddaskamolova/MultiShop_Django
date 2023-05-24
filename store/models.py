from currencies.models import Currency
from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils.safestring import mark_safe
from mptt.models import MPTTModel, TreeForeignKey
from django.utils.translation import gettext_lazy as _


# Create your models here.

class Category(MPTTModel):
    title = models.CharField(max_length=50, unique=True, help_text=_("Required and unique"))
    image = models.ImageField(upload_to='photos/categories/', null=True, blank=True,
                              verbose_name='Image')
    slug = models.SlugField(unique=True, null=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, verbose_name='Category',
                               blank=True, null=True, related_name='subcategories')
    is_active = models.BooleanField(default=False)

    keywords = models.CharField(max_length=255)

    def get_image(self):
        if self.image:
            return self.image.url
        else:
            return 'https://avatars.mds.yandex.net/i?id=64a306848159675833371ba4a08fa3bb655cfd8a-6971541-images-thumbs&n=13'

    class MPTTMeta:
        order_insertion_by = ["name"]

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'categories'
        unique_together = ('slug', 'parent')

    def get_absolute_url(self):
        return reverse('category_detail', kwargs={'slug': self.slug})

    def __str__(self):
        full_path = [self.title]
        k = self.parent
        while k is not None:
            full_path.append(k.title)
            k = k.parent
        return ' -> '.join(full_path[::-1])


class ProductType(models.Model):
    title = models.CharField(max_length=255, verbose_name='Product type', help_text=("Required"))
    is_active = models.BooleanField(default=False)

    class Meta:
        verbose_name = _('Product type')
        verbose_name_plural = _('Product types')

    def __str__(self):
        return self.title


class ProductSpecification(models.Model):
    product_type = models.ForeignKey(ProductType, on_delete=models.RESTRICT)
    title = models.CharField(verbose_name=_("Title"), help_text=("Required"), max_length=255)

    class Meta:
        verbose_name = _('Product Specification')
        verbose_name_plural = _('Products Specifications')

    def __str__(self):
        return self.title


class Product(models.Model):
    CONDITION = (('New', 'New Product'), ('Last', 'Last Product'))
    STATUS = (('Published', 'Published Product'), ('Draft', 'Draft Product'))
    STOCK = (('In stock', 'In Stock Product'), ('Out of stock', 'Out of Stock Product'))
    PRICE_FILTER = (('99 $', '109 $'), ('149 $', '159 $'), ('199 $', '209 $'), ('239 $', '249 $'), ('299 $', '300 $'),
                    ('309 $', '319 $'), ('329 $', '339 $'), ('399 $', '409 $'), ('439 $', '449 $'), ('489 $', '500 $'))
    product_type = models.ForeignKey(ProductType, on_delete=models.RESTRICT)

    title = models.CharField(max_length=255, verbose_name='Product title', help_text=("Required"))
    regular_price = models.DecimalField(verbose_name=("Regular price"), help_text=_("Maximum 999.99"),
                                        error_messages={"name": {
                                            "max_length": _("Price must be between 0 and 999.99")
                                        }
                                        }, max_digits=5, decimal_places=2)
    discount_price = models.DecimalField(verbose_name=_("Discount Price"), help_text=_("Maximum 999.99"),
                                         error_messages={"name": {
                                             "max_length": _("Price must be between 0 and 999.99")
                                         }
                                         }, max_digits=5, decimal_places=2)
    price = models.CharField(choices=PRICE_FILTER, max_length=40, verbose_name='Price')
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE,
                                   related_name='product_creator')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created at')
    updated_at = models.DateTimeField(auto_now=True)
    quantity = models.CharField(choices=STOCK, max_length=200)
    description = models.TextField(default='Description coming soon', verbose_name='Description')
    category = models.ForeignKey(Category, on_delete=models.RESTRICT, verbose_name='Category',
                                 related_name='product')
    slug = models.SlugField(unique=True, null=True)
    information_size = models.CharField(max_length=255, verbose_name='Information size')
    color = models.CharField(max_length=30, default='white', verbose_name='Color')
    material = models.CharField(max_length=30, default='Leather', verbose_name='Material')
    condition = models.CharField(choices=CONDITION, max_length=100)
    status = models.CharField(choices=STATUS, max_length=200)
    author = models.CharField(max_length=255, default='admin')
    info = models.TextField(default='Information coming soon', verbose_name='Additional Information')
    is_active = models.BooleanField(default=False)

    def get_first_image(self):
        if self.images:
            try:
                return self.images.first().image.url
            except:
                return 'https://avatars.mds.yandex.net/i?id=64a306848159675833371ba4a08fa3bb655cfd8a-6971541-images-thumbs&n=13'
        else:
            return 'https://avatars.mds.yandex.net/i?id=64a306848159675833371ba4a08fa3bb655cfd8a-6971541-images-thumbs&n=13'

    def get_absolute_url(self):
        return reverse('product_detail', kwargs={'slug': self.slug})

    def __str__(self):
        return str(self.title) + ":" + str(self.price)

    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        ordering = ('-created_at',)


class ProductSpecificationValue(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    specification = models.ForeignKey(ProductSpecification, on_delete=models.RESTRICT)
    value = models.CharField(max_length=255, verbose_name=_("value"),
                             help_text=_("Product specification value(maximum 255 value)"))

    class Meta:
        verbose_name = _('Product Specification Value')
        verbose_name_plural = _('Products Specification Values')

    def __str__(self):
        return self.value


class Gallery(models.Model):
    image = models.ImageField(upload_to='photos/products/', verbose_name='Image')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')

    class Meta:
        verbose_name = 'Image'
        verbose_name_plural = 'Images'


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, blank=True, null=True)
    first_name = models.CharField(max_length=255, default='', verbose_name='Firstname')
    last_name = models.CharField(max_length=255, default='', verbose_name='Lastname')

    def __str__(self):
        return self.first_name

    class Meta:
        verbose_name = 'Customer'
        verbose_name_plural = 'Customers'


class Order(models.Model):
    # each individual status
    SUBMITTED = 1
    PROCESSED = 2
    SHIPPED = 3
    CANCELLED = 4
    # set of possible order statuses
    ORDER_STATUSES = (
        (SUBMITTED, 'Submitted'), (PROCESSED, 'Processed'), (SHIPPED, 'Shipped'), (CANCELLED, 'Cancelled'))
    status = models.IntegerField(choices=ORDER_STATUSES, default=SUBMITTED)
    # ip_address = models.IPAddressField(max_length=255)
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    is_completed = models.BooleanField(default=False)
    shipping = models.BooleanField(default=True)
    transaction_id = models.CharField(max_length=20)

    def __str__(self):
        return str(self.pk) + ''

    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'

    @property
    def get_cart_total_price(self):
        order_products = self.orderproduct_set.all()
        total_price = sum([product.get_total_price for product in order_products])
        return total_price

    @property
    def get_cart_total_quantity(self):
        order_products = self.orderproduct_set.all()
        total_quantity = sum([product.quantity for product in order_products])
        return total_quantity


class OrderProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    price = models.DecimalField(max_digits=9, decimal_places=2)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Product in order'
        verbose_name_plural = 'Products in order'

    @property
    def get_total_price(self):
        total_price = self.product.price * self.quantity
        return total_price

    @property
    def name(self):
        return self.product.name

    def get_absolute_url(self):
        return self.product.get_absolute_url()


class City(models.Model):
    city_name = models.CharField(max_length=255, verbose_name="Cities")

    def __str__(self):
        return self.city_name

    class Meta:
        verbose_name = 'City'
        verbose_name_plural = 'Cities'


class ShippingAddress(models.Model):
    shipping_name = models.CharField(max_length=50, null=True)
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, blank=True, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    address = models.CharField(max_length=255)
    city = models.ForeignKey(City, on_delete=models.CASCADE, max_length=255, verbose_name='City')
    state = models.CharField(max_length=255)
    shipping_zip = models.CharField(max_length=10)
    phone = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Delivery address'
        verbose_name_plural = 'Delivery addresses'


class BillingAddress(models.Model):
    billing_name = models.CharField(max_length=50)
    billing_address_1 = models.CharField(max_length=50)
    billing_address_2 = models.CharField(max_length=50, blank=True)
    billing_city = models.ForeignKey(City, on_delete=models.CASCADE, max_length=50, verbose_name='City')
    billing_state = models.CharField(max_length=2)
    billing_country = models.CharField(max_length=50)
    billing_zip = models.CharField(max_length=10)

    def __unicode__(self):
        return 'Order #' + str(self.id)


# class Language(models.Model):


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=255, blank=True)
    address = models.CharField(max_length=255, blank=True)
    city = models.ForeignKey(City, on_delete=models.CASCADE, max_length=255, blank=True, verbose_name='City')
    country = models.CharField(max_length=50, blank=True)
    image = models.ImageField(default='default.jpg', upload_to='profile_images')
    bio = models.TextField(blank=True, null=True, max_length=500)
    #  language = models.ForeignKey(Language, default=LANGUAGE_CODE, on_delete=models.CASCADE, blank=True, null=True)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.user.username

    def user_name(self):
        return self.user.first_name + '' + self.user.last_name + ['+ self.user.username +']

    def image_tag(self):
        return mark_safe('<img src="{}" height="50"/>'.format(self.image.url))

    image_tag.short_description = 'Image'
