from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes


from account.forms import RegistrationForm
from account.tokens import account_activation_token
from shop.models import Product, Category


def common_user_registration(request):
    if request.user.is_authenticated:
        return redirect('account:dashboard')
    if request.method == 'POST':
        reg_form = RegistrationForm(request.POST)
        if reg_form.is_valid():
            user = reg_form.save(commit=False)
            user.email = reg_form.cleaned_data['email']
            user.set_password(reg_form.cleaned_data['password1'])
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            subject = 'Please, activate your account'
            message = render_to_string(
                'account/account_actions/account_activation.html',
                {'user': user,
                 'domain': current_site.domain,
                 'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                 'token': account_activation_token.make_token(user),
                 })
            user.email_user(subject=subject, message=message)
            return HttpResponse('You were registered successfully')
        else:
            return reg_form
    else:
        return RegistrationForm()


def common_categories_by_id(category_id=None):
    categories = Category.objects.all()
    if category_id:
        category = get_object_or_404(Category, id=category_id)
        books = Product.objects.prefetch_related('product_image').filter(category=category, is_active=True)[:5]
    else:
        books = Product.objects.prefetch_related('product_image').filter(is_active=True)[:5]
    return {'categories': categories, 'books': books}


def index_view(request):
    reg_form = common_user_registration(request)
    category_id = request.GET.get('category_id')
    common = common_categories_by_id(category_id)
    context = {
        'form': reg_form,
        'categories': common['categories'],
        'selected_category': category_id,
        'products': common['books']
    }
    return render(request, 'home.html', context)