from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.exceptions import ImmediateHttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):

    def is_open_for_signup(self, request, sociallogin):
        # Get the email associated with the social account
        email = sociallogin.user.email

        # Check if a user with this email already exists
        if User.objects.filter(email=email).exists():
            # If the email already exists, raise an exception or block signup
            #return redirect(reverse('login'))
            messages.error(request, "Email already associated. Use password to login")
            raise ImmediateHttpResponse(redirect(reverse('accounts:login')))

        # Allow signup if the email doesn't exist
        return True
