# core/forms.py
from django import forms
from django.contrib.auth.models import User
from django.core.validators import RegexValidator


phone_validator = RegexValidator(
    regex=r'^(?:\+7|8)\d{10}$',
    message="Введите номер в формате +7XXXXXXXXXX или 8XXXXXXXXXX."
)


class RegisterForm(forms.Form):
    full_name = forms.CharField(
        label="Полное имя",
        max_length=255
    )
    email = forms.EmailField(
        label="Электронная почта"
    )
    phone = forms.CharField(
        label="Номер телефона",
        validators=[phone_validator]
    )
    password1 = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput
    )
    password2 = forms.CharField(
        label="Подтвердите пароль",
        widget=forms.PasswordInput
    )

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Пользователь с таким email уже существует.")
        return email

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get("password1")
        p2 = cleaned.get("password2")
        if p1 and p2 and p1 != p2:
            self.add_error("password2", "Пароли не совпадают.")
        return cleaned


class EmailLoginForm(forms.Form):
    email = forms.EmailField(label="Электронная почта")
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput
    )
