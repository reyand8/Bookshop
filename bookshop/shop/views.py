from django.shortcuts import render, get_object_or_404
from .models import Category, Product


def all_products(request):
    products = Product.objects.prefetch_related('product_image').filter(is_active=True)
    return render(request, 'products/products.html',
                  {'products': products})


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    return render(request, 'products/product_details.html',
                  {'product': product})


def category_list(request, category_slug=None):
    category = get_object_or_404(Category, slug=category_slug)
    products = Product.objects.filter(
        category__in=Category.objects.get(name=category_slug).get_descendants(include_self=True)
    )
    return render(request, 'products/category.html',
                  {'category': category, 'products': products})


def contact(request):
    return render(request, 'other/contact.html')


def about(request):
    return render(request, 'other/about.html')