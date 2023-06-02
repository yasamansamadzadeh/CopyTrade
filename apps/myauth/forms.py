# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User
from django.core.exceptions import ValidationError

from apps.trade.services import validate_kucoin_credentials
from ..trade.models import Trader


class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Username",
                "class": "form-control"
            }
        ))
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Password",
                "class": "form-control"
            }
        ))


class SignUpForm(UserCreationForm):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Username",
                "class": "form-control"
            }
        ))
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "placeholder": "Email",
                "class": "form-control"
            }
        ))
    password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Password",
                "class": "form-control"
            }
        ))
    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Password check",
                "class": "form-control"
            }
        ))
    master = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(
            attrs={
                "class": "form-check-input"
            }
        )
    )
    key = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "KuCoin API Key",
                "class": "form-control"
            }
        )
    )
    secret = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "KuCoin API Secret",
                "class": "form-control"
            }
        )
    )
    passphrase = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "KuCoin API Passphrase",
                "class": "form-control"
            }
        )
    )

    def clean(self):
        cleaned_data = super().clean()
        try:
            validate_kucoin_credentials(
                cleaned_data.get('key'),
                cleaned_data.get('secret'),
                cleaned_data.get('passphrase'),
                not cleaned_data.get('master'),
            )
        except ValueError as e:
            raise ValidationError(str(e)) from e

    def clean_key(self):
        key = self.cleaned_data.get('key')
        if key and Trader.objects.filter(kc_key=key).exists():
            raise ValidationError("Key already exists")
        return key

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'master', 'key', 'secret', 'passphrase')
