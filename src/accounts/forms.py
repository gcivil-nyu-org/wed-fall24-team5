from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

class MyAuthenticationForm(AuthenticationForm):
    email = forms.EmailField(
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

class MyUserCreationForm(UserCreationForm):  # pylint: disable=too-many-ancestors
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'input',
            'type': 'email',
        })
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'input',
            'type': 'password',
        })
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'input',
            'type': 'password',
        })
    )
