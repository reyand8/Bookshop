from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages

from .models import Customer
from .forms import RegistrationForm, LoginForm, UserEditForm
from .tokens import account_activation_token



# User

def user_registration(request):
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
                'account/account_activation/account_activation.html',
                {'user': user,
                 'domain': current_site.domain,
                 'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                 'token': account_activation_token.make_token(user),
                 })
            user.email_user(subject=subject, message=message)
            return HttpResponse('You were registered successfully')
        else:
            registration_form = RegistrationForm()
        return render(request,
                      'account/user/user_registration.html',
                      {'reg_form': reg_form})


def user_activation(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = Customer.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, user.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return redirect('account:dashboard')
    else:
        return render(request, 'account/account_activation/account_activation_invalid.html')


def user_login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is None:
            return HttpResponse("Username or password is incorrect")
        login(request, user)
        return redirect('/')
    else:
        log_form = LoginForm()
    return render(request, 'account/user/user_login.html',
                  {'log_form': log_form})


@login_required
def user_edit(request):
    if request.method == 'POST':
        user_form = UserEditForm(instace=request.user, data=request.POST)
        if user_form.is_valid():
            user_form.save()
    else:
        user_form = UserEditForm(instance=request.user)
    return render(request, 'account/user/user_edit.html', {'user_form': user_form})


@login_required
def user_delete(request):
    user = Customer.objects.get(username=request.user)
    user.is_active = False
    user.save()
    logout(request)
    return redirect('account:delete_confirmation')


# Orders, wishlist and dashboard

def dashboard(request):
    orders = user_orders(request)
    return render(request, 'account/user_orders/dashboard.html',
                  {'section': 'profile', 'orders': orders})


@login_required
def get_wishlist(request):
    products = Product.objects.filter(user_wishlist=request.user)
    return render(request, 'account/user_orders/wishlist.html', {'wishlist': products})


@login_required
def get_user_orders(request):
    user_id = request.user.id
    orders = Order.objects.filter(user_id=user_id).filter(billing_status=True)
    return render(request, 'account/account_orders/account_user_orders.html', {'orders': orders})


@login_required
def add_to_wishlist(request, id):
    product = get_object_or_404(Product, id=id)
    if product.user_wishlist.filter(id=request.user.id).exists():
        product.user_wishlist.remove(request.user)
        messages.success(request, product.title + ' has been removed from your wishlist')
    else:
        product.user_wishlist.add(request.user)
        messages.success(request, product.title + ' was added to your wishlist')
    return HttpResponseRedirect(request.META['HTTP_REFERER'])

