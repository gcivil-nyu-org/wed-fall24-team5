from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

class MyAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'input',
            'type': 'email',
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'input',
            'type': 'password',
            'required': True,
        })
    )
    class Meta:
        model = User

class MyUserCreationForm(UserCreationForm):  # pylint: disable=too-many-ancestors
    username = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'input',
            'type': 'email'
        })
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'input',
            'type': 'email',
            'placeholder': 'Email',
        })
    )
    first_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'input',
            'type': 'text',
            'placeholder': 'First Name',
        })
    )
    last_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'input',
            'type': 'text',
            'placeholder': 'Last Name',
        })
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'input',
            'type': 'password',
            'placeholder': 'Enter Password',
        })
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'input',
            'type': 'password',
            'placeholder': 'Re-enter Password',
        })
    )
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']

    
