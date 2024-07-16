from django import forms
from django.contrib.auth.forms import (AuthenticationForm, UserCreationForm, PasswordResetForm,
                                       SetPasswordForm)

from .models import Customer, Address


class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'Email address',
        'class': 'form-control auth__form-input',
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Password',
        'class': 'form-control auth__form-input',
    }))

class RegistrationForm(UserCreationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Username',
                                      'class': 'form-control'
                                      }),
                               min_length=6, max_length=20, help_text='Required')
    email = forms.EmailField(widget=forms.TextInput(attrs={'placeholder': 'Email',
                                                           'class': 'form-control'}),
                             help_text='Required')
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Password',
        'class': 'form-control auth__form-input',
    }), help_text='Required')
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Repeat Password',
        'class': 'form-control auth__form-input',
    }), help_text='Required')

    class Meta:
        model = Customer
        fields = ('email', 'username')

    def clean_username(self):
        username = self.cleaned_data['username'].lower()
        v = Customer.objects.filter(username=username)
        if v.count():
            raise forms.ValidationError('This username already exists')
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if Customer.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already taken')
        return email

    def clean_password(self):
        cd = self.cleaned_data
        if cd['password1'] != cd['password2']:
            raise forms.ValidationError("Ups, passwords don't match")
        return cd['password2']

    def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.fields['username'].widget.attrs.update(
                {'placeholder': 'Username'})
            self.fields['email'].widget.attrs.update(
                {'placeholder': 'E-mail'})
            self.fields['password1'].widget.attrs.update(
                {'placeholder': 'Password'})
            self.fields['password2'].widget.attrs.update(
                {'placeholder': 'Repeat Password'})


class UserAddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['full_name', 'phone', 'address_line_1', 'address_line_2', 'city', 'postcode']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['full_name'].widget.attrs.update(
            {'placeholder': 'Full Name'})
        self.fields['phone'].widget.attrs.update({'placeholder': 'Phone'})
        self.fields['address_line_1'].widget.attrs.update({'placeholder': 'Address'})
        self.fields['address_line_2'].widget.attrs.update({'placeholder': 'Address'})
        self.fields['city'].widget.attrs.update({'placeholder': 'City'})
        self.fields['postcode'].widget.attrs.update({'placeholder': 'Postcode'})


class PwdResetForm(PasswordResetForm):
    email = forms.EmailField(max_length=254, widget=forms.TextInput(
        attrs={'placeholder': 'Email'}))

    def clean_email(self):
        email = self.cleaned_data['email']
        c = Customer.objects.filter(email=email)
        if not c:
            raise forms.ValidationError(
                "We can't find that email address")
        return email


class PasswordResetConfirmForm(SetPasswordForm):
    new_password1 = forms.CharField(
        label='New password', widget=forms.PasswordInput(
            attrs={'placeholder': 'New Password'}))
    new_password2 = forms.CharField(
        label='Repeat password', widget=forms.PasswordInput(
            attrs={'placeholder': 'New Password'}))

class UserEditForm(forms.ModelForm):
    email = forms.EmailField(
        label="Email can't be changed",
        max_length=50,
        widget=forms.TextInput(
            attrs={'placeholder': 'email', 'readonly': 'readonly'}))
    username = forms.CharField(
        label='Username',
        min_length=6,
        max_length=20,
        widget=forms.TextInput(
            attrs={'placeholder': 'Username'}))

    class Meta:
        model = Customer
        fields = ('email', 'username')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].required = True
        self.fields['email'].required = True