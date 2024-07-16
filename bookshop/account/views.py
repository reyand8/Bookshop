from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.contrib.auth import login, logout
from django.contrib import messages

from .models import Customer, Address
from .forms import RegistrationForm, UserEditForm, UserAddressForm
from .tokens import account_activation_token
from orders.models import Order
from orders.views import all_orders
from shop.models import Product



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
                'account/account_actions/account_activation.html',
                {'user': user,
                 'domain': current_site.domain,
                 'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                 'token': account_activation_token.make_token(user),
                 })
            user.email_user(subject=subject, message=message)
            return HttpResponse('You were registered successfully')
        else:
            return render(request,
                          'account/user/user_registration.html',
                          {'form': reg_form})
    else:
        reg_form = RegistrationForm()
    return render(request,
                  'account/user/user_registration.html',
                  {'form': reg_form})


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
        return render(request, 'account/account_actions/account_activation_invalid.html')


@login_required
def user_edit(request):
    if request.method == 'POST':
        user_form = UserEditForm(instance=request.user, data=request.POST)
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
    orders = all_orders(request)
    return render(request, 'account/user_orders/dashboard.html',
                  {'section': 'profile', 'orders': orders})


@login_required
def get_wishlist(request):
    products = Product.objects.filter(user_wishlist=request.user)
    return render(request, 'account/user_orders/user_wishlist.html', {'wishlist': products})


@login_required
def get_user_orders(request):
    user_id = request.user.id
    orders = Order.objects.filter(user_id=user_id).filter(billing_status=True)
    return render(request, 'account/user_orders/user_orders.html', {'orders': orders})


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


# Addresses

@login_required
def view_address(request):
    addresses = Address.objects.filter(customer=request.user)
    return render(request, 'account/user/user_addresses.html', {'addresses': addresses})


@login_required
def add_address(request):
    if request.method == 'POST':
        address_form = UserAddressForm(data=request.POST)
        if address_form.is_valid():
            address_form = address_form.save(commit=False)
            address_form.customer = request.user
            address_form.save()
            return HttpResponseRedirect(reverse('account:addresses'))
    else:
        address_form = UserAddressForm()
    return render(request, 'account/user/user_edit_addresses.html',
                  {'form': address_form})


@login_required
def edit_address(request, id):
    if request.method == 'POST':
        address = Address.objects.get(pk=id, customer=request.user)
        address_form = UserAddressForm(instance=address, data=request.POST)
        if address_form.is_valid():
            address_form.save()
            return HttpResponseRedirect(reverse('account:addresses'))
    else:
        address = Address.objects.get(pk=id, customer=request.user)
        address_form = UserAddressForm(instance=address)
    return render(request, 'account/user/user_edit_addresses.html',
                  {'form': address_form})


@login_required
def delete_address(request, id):
    address = Address.objects.filter(pk=id, customer=request.user).delete()
    return redirect('account:addresses')


@login_required
def set_default_address(request, id):
    Address.objects.filter(customer=request.user, default=True).update(default=False)
    Address.objects.filter(pk=id, customer=request.user).update(default=True)
    previous_url = request.META.get('HTTP_REFERER')
    if 'delivery_address' in previous_url:
        return redirect('checkout:delivery_address')
    return redirect('account:addresses')


@login_required
def get_user_orders(request):
    user_id = request.user.id
    orders = Order.objects.filter(user_id=user_id).filter(billing_status=True)
    return render(request, 'account/user_orders/user_orders.html', {'orders': orders})