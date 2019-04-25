from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm, SetPasswordForm
from django import forms
from django.forms import CharField


class RegistroForm(UserCreationForm):
    first_name = forms.CharField(label='first_name', max_length=140, required=True, widget=forms.TextInput(
        attrs={'class': 'form-control', 'id': 'first_name', 'style': 'color:black', 'autocomplete': 'on', }))
    last_name = forms.CharField(label='last_name', max_length=140, required=True, widget=forms.TextInput(
        attrs={'class': 'form-control', 'id': 'last_name', 'style': 'color:black', 'autocomplete': 'on'}))
    email = forms.EmailField(label='email', required=True, widget=forms.TextInput(
        attrs={'class': 'form-control', 'id': 'email', 'style': 'color:black', 'autocomplete': 'on', 'placeholder': 'ejemplo@mantosgroup.com'}))
    username = forms.CharField(required=True, widget=forms.TextInput(
        attrs={'class': 'form-control', 'id': 'username', 'style': 'color:black', 'autocomplete': 'on', 'autofocus': '', }))
    password1 = forms.CharField(label='password1', widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'id': 'password1', 'style': 'color:black', 'autocomplete': 'new-password'}))
    password2 = forms.CharField(label='password2', widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'id': 'password2', 'style': 'color:black', 'autocomplete': 'new-password'}))

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'password1',
            'password2',
        )
        # widgets = {'username': forms.TextInput(
        # attrs={'class':
        # 'form-control','id':'username','style':'color:black','autocomplete':'on','autofocus':''}),
        # }


class UserPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(label='email', required=True, widget=forms.TextInput(
        attrs={'class': 'form-control', 'id': 'email', 'style': 'color:black', 'autocomplete': 'on', 'placeholder': 'ejemplo@mantosgroup.com'}))

    


class UserPasswordConfirmForm(SetPasswordForm):
    new_password1 = forms.CharField(label='new_password1', widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'id': 'new_password1', 'style': 'color:black', 'autocomplete': 'new-password'}))
    new_password2 = forms.CharField(label='new_password2', widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'id': 'new_password2', 'style': 'color:black', 'autocomplete': 'new-password'}))
