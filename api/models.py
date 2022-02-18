from django.db import models
from django.contrib.auth.models import User
# Create your models here.


# class AuthUser(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     email = models.TextField(max_length=500, blank=True)


class Credit(models.Model):
    user_id = models.OneToOneField('auth.User', on_delete=models.CASCADE, primary_key=True)
    balance = models.DecimalField(max_digits=7, decimal_places=2)
    max_credit = models.DecimalField(max_digits=7, decimal_places=2)
    amount_owed = models.DecimalField(max_digits=7, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Savings(models.Model):
    user_id = models.OneToOneField('auth.User', on_delete=models.CASCADE, primary_key=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Transactions(models.Model):
    SOURCE_CHOICES = (
        ('SAVINGS', 'Savings'),
        ('CREDIT', 'Credit')
    )
    TYPE_CHOICES = (
        ('BUY', 'buy'),
        ('SELL', 'sell')
    )

    user_id = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='user_transaction')
    source = models.CharField(max_length=10, choices=SOURCE_CHOICES)
    amount = models.DecimalField(max_digits=7, decimal_places=2)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
