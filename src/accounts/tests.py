from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.conf import settings
from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site
import os
from unittest.mock import patch

class ViewTests(TestCase):
    def setUp(self):
        # Set up reusable client and user
        User = get_user_model()
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser@example.com",
            email="testuser@example.com",
            password="password",
        )

        # Create a Site instance (needed by allauth's SocialApp)
        self.site = Site.objects.get(id=1)

        # Create a SocialApp instance
        self.social_app, _ = SocialApp.objects.get_or_create(
            provider="google",
            name="google"
        )
        self.social_app.client_id=os.getenv("google_auth_client_id", "none")
        self.social_app.secret=os.getenv("google_auth_secret_key", "none")
        self.social_app.sites.add(self.site)
        self.social_app.save()
        
    def test_landing_view_anonymous(self):
        """Test landing view for anonymous users"""
        response = self.client.get(reverse("accounts:landing"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/landing.html")

    def test_profile_view_authenticated(self):
        """Test profile view for authenticated users"""
        self.client.login(email="testuser@example.com", password="password")
        response = self.client.get(reverse("accounts:profile"), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, "/recipient_dashboard/", status_code=302, target_status_code=200)

    @patch('allauth.socialaccount.templatetags.socialaccount.provider_login_url', return_value="/mock-login-url/")
    def test_register_view_get(self, mock_provider_login_url): #f
        """Test GET request for register view"""
        response = self.client.get(reverse("accounts:register"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/register.html")

    @patch('allauth.socialaccount.templatetags.socialaccount.provider_login_url', return_value="/mock-login-url/")
    def test_register_view_post_success(self, mock_provider_login_url): #f
        """Test successful registration"""
        response = self.client.post(
            reverse("accounts:register"),
            {
                "email": "newuser@example.com",
                "password1": "strongpassword123",
                "password2": "strongpassword123",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse("accounts:profile"))
        self.assertTrue(get_user_model().objects.filter(username="newuser@example.com").exists())

    @patch('allauth.socialaccount.templatetags.socialaccount.provider_login_url', return_value="/mock-login-url/")
    def test_register_view_post_email_exists(self, mock_provider_login_url): #
        """Test registration with an existing email"""
        get_user_model().objects.create_user(username="existing@example.com", email="existing@example.com", password="password")
        response = self.client.post(
            reverse("accounts:register"),
            {
                "email": "existing@example.com",
                "password1": "newpassword123",
                "password2": "newpassword123",
            },
        )
        self.assertEqual(response.status_code, 200)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("already registered" in str(message) for message in messages))

    @patch('allauth.socialaccount.templatetags.socialaccount.provider_login_url', return_value="/mock-login-url/")
    def test_login_view_get(self, mock_provider_login_url):
        """Test GET request for login view"""
        response = self.client.get(reverse("accounts:login"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/login.html")

    @patch('allauth.socialaccount.templatetags.socialaccount.provider_login_url', return_value="/mock-login-url/")
    def test_login_view_post_success(self, mock_provider_login_url):
        """Test successful login"""
        response = self.client.post(
            reverse("accounts:login"),
            {"username": "testuser", "password": "testpassword"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse("accounts:profile"))

    @patch('allauth.socialaccount.templatetags.socialaccount.provider_login_url', return_value="/mock-login-url/")
    def test_login_view_post_incorrect_credentials(self, mock_provider_login_url): #f
        """Test login with incorrect credentials"""
        response = self.client.post(
            reverse("accounts:login"),
            {"username": "testuser", "password": "wrongpassword"},
        )
        self.assertEqual(response.status_code, 200)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("Incorrect email or password" in str(message) for message in messages))

    def test_logout_view(self):
        """Test logout view"""
        self.client.login(email="testuser@example.com", password="password")
        response = self.client.get(reverse("accounts:logout"), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, "/accounts/landing/", status_code=302, target_status_code=200)
