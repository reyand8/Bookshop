from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.contrib.auth import login, logout, authenticate

from .forms import RegistrationForm, LoginForm
from .tokens import account_activation_token


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
                      'account/user_auth/registration.html',
                      {'reg_form': reg_form})


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
    return render(request, 'account/user_auth/login.html', {'log_form': log_form})
