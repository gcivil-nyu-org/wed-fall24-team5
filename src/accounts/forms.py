from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

INPUT_CLASS = 'mt-1 block w-full py-1.5 border border-gray-300 rounded-md shadow-sm' \
    'focus:outline-none focus:ring-sky-500 focus:border-sky-500 sm:text-sm'

class MyAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': INPUT_CLASS,
            'type': 'email',
        }),
        error_messages={'required': 'Email is required.'}
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': INPUT_CLASS,
            'type': 'password',
        }),
        error_messages={'required': 'Password is required.'}
    )
    class Meta:
        model = User

class MyUserCreationForm(UserCreationForm):  # pylint: disable=too-many-ancestors
    username = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={
            'class': INPUT_CLASS,
            'type': 'email'
        })
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': INPUT_CLASS,
            'type': 'email',
        }),
        error_messages={'required': 'Email is required.'}
    )
    first_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            'class': INPUT_CLASS,
            'type': 'text',
        }),
        error_messages={'required': 'Name is required.'}
    )
    last_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            'class': INPUT_CLASS,
            'type': 'text',
        }),
        error_messages={'required': 'Name is required.'}
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': INPUT_CLASS,
            'type': 'password',
        }),
        error_messages={'required': 'Password is required.'}
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': INPUT_CLASS,
            'type': 'password',
        }),
    )
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']
