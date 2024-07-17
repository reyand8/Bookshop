from django.utils.translation import gettext_lazy as _
from mptt.models import MPTTModel, TreeForeignKey
from django.urls import reverse
from django.db import models

from django.conf import settings


class Category(MPTTModel):
    name = models.CharField(
        verbose_name='Category',
        help_text='Required',
        max_length=100,
        unique=True)
    slug = models.SlugField(unique=True, max_length=40, db_index=True)
    parent = TreeForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children')
    is_active = models.BooleanField(default=True)

    def get_absolute_url(self):
        return reverse('shop:category_list', args=[self.slug])

    class MPTTMet:
        order_insertion_by = ['name']

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class ProductType(models.Model):
    name = models.CharField(
        verbose_name='Product Name',
        help_text='Required',
        max_length=150,
        unique=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Product Type'
        verbose_name_plural = 'Product Types'

    def __str__(self):
        return self.name


class ProductSpecification(models.Model):
    product_type = models.ForeignKey(ProductType, on_delete=models.RESTRICT)
    name = models.CharField(
        verbose_name= 'Product Name',
        help_text= 'Required',
        max_length=150)

    class Meta:
        verbose_name = 'Product Specification'
        verbose_name_plural = 'Product Specifications'

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.RESTRICT)
    product_type = models.ForeignKey(ProductType, on_delete=models.RESTRICT)
    title = models.CharField(
        verbose_name='title',
        help_text='Required',
        max_length=150)
    description = models.TextField(
        verbose_name='description',
        help_text='Not Required',
        blank=True)
    slug = models.SlugField(max_length=255)
    regular_price = models.DecimalField(
        verbose_name='Regular price',
        help_text='Maximum 999.99',
        error_messages={
            'name': {
                'max_length': _('The price must be between 0 and 999.99.'),
                    },
                        },
        max_digits=5,
        decimal_places=2)
    discount_price = models.DecimalField(
        verbose_name='Discount price',
        help_text='Maximum 999.99',
        error_messages={
            'name': {
                'max_length': 'The price must be between 0 and 999.99.',
                    },
                        },
        max_digits=5,
        decimal_places=2)
    is_active = models.BooleanField(
        verbose_name='Product visibility',
        help_text='Change product visibility',
        default=True)
    created = models.DateTimeField(_('Created at'), auto_now_add=True, editable=False)
    updated = models.DateTimeField(_('Updated at'), auto_now=True)
    user_wishlist = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="user_wishlist", blank=True)

    class Meta:
        ordering = ('-created',)
        verbose_name = 'Product'
        verbose_name_plural = 'Products'

    def get_absolute_url(self):
        return reverse('shop:product_detail', args=[self.slug])

    def __str__(self):
        return self.title


class ProductSpecificationValue(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    specification = models.ForeignKey(ProductSpecification, on_delete=models.RESTRICT)
    value = models.CharField(
        verbose_name='value',
        help_text='Product specification value (maximum of 255 words',
        max_length=255)

    class Meta:
        verbose_name = 'Product Specification Value'
        verbose_name_plural = 'Product Specification Values'

    def __str__(self):
        return self.value


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='product_image')
    image = models.ImageField(
        verbose_name='image',
        help_text='Upload a product image',
        upload_to='images/',
        default='')
    alt_text = models.CharField(
        verbose_name='Alternative text',
        help_text='Please add alternative text',
        max_length=255,
        null=True,
        blank=True)
    is_feature = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Product Image'
        verbose_name_plural = 'Product Images'