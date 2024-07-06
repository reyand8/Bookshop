from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.mail import send_mail
import uuid


class CustomAccountManager(BaseUserManager):
    def create_superuser(self, email, username, password, **other_field):
        other_field.setdefault('is_staff', True)
        other_field.setdefault('is_superuser', True)
        other_field.setdefault('is_active', True)
        if other_field.get('is_staff') is not True:
            raise ValueError('Superuser must be assigned to staff=True')
        if other_field.get('is_superuser') is not True:
            raise ValueError('Ups! Superuser must be assigned to is_superuser=True.')
        return self.create_user(email, username, password, **other_field)

    def create_user(self, email, username, password, **other_fields):
        if not email:
            raise ValueError('You must provide an email address')
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **other_fields)
        user.set_password(password)
        user.save()
        return user


class Customer(AbstractBaseUser, PermissionsMixin):
    # Main information
    email = models.EmailField(max_length=50, unique=True, db_index=True)
    username = models.CharField(max_length=20, unique=True, db_index=True)
    phone = models.CharField(max_length=20, blank=True)
    # Status
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    objects = CustomAccountManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = "Customer"
        verbose_name_plural = "Customers"

    def email_user(self, subject, message):
        send_mail(subject, message, 'example@example.com', [self.email], fail_silently=False)

    def __str__(self):
        return self.username


class Address(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(Customer, verbose_name='Customer', on_delete=models.CASCADE)
    full_name = models.CharField(label='Full Name', max_length=50)
    phone = models.CharField(max_length=20)
    postcode = models.CharField(label='Postcode', max_length=20)
    address_line_1 = models.CharField(max_length=90, blank=True)
    address_line_2 = models.CharField(max_length=90, blank=True)
    city = models.CharField(max_length=150, blank=True)
    delivery_instructions = models.CharField(label='Delivery Instructions', max_length=200)
    created_at = models.DateTimeField(label='Created at', auto_now_add=True)
    updated_at = models.DateTimeField(label='Updated at', auto_now=True)
    default = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Address"
        verbose_name_plural = "Addresses"

    def __str__(self):
        return "Address"