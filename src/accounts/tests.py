from django.test import TestCase
from django.contrib.sites.models import Site
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.contrib.messages import get_messages


class TestData(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.current_site = Site.objects.get_current()
        cls.SocialApp1 = cls.current_site.socialapp_set.create(
            provider="google",
            name="google",
            client_id="1234567890",
            secret="0987654321",
        )


class CollectionPageTest(TestData):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username="testuser", email="testuser@example.com", password="testpass"
        )

    def test_accounts_register_status_code(self):
        """Test that the accounts register view returns a 200 OK status."""
        response = self.client.get(reverse("accounts:register"))
        self.assertEqual(response.status_code, 200)

    def test_register_view_get_redirects_post_authenticated_user(self):
        """Test that the register page redirects when authenticated users hits register page again."""
        self.client.login(username="testuser", password="testpass")
        response = self.client.get(reverse("accounts:register"))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/recipient_dashboard")

    def test_register_view_post_success(self):
        """Test successful registration view behavior."""
        response = self.client.post(
            reverse("accounts:register"),
            {
                "email": "newuser@example.com",
                "password1": "C*pml3XP4ssw0RD!",
                "password2": "C*pml3XP4ssw0RD!",
                "first_name": "New",
                "last_name": "User",
            },
        )

        # Only check form errors if the response did not redirect (status code 200)
        if response.status_code == 200:
            form = response.context.get("form")
            if form and form.errors:
                print("Form errors:", form.errors)

        self.assertEqual(
            response.status_code, 302
        )  # Redirects after successful registration
        self.assertEqual(response.url, "/accounts/profile/")
        self.assertTrue(User.objects.filter(email="newuser@example.com").exists())

    def test_register_view_post_email_already_exists(self):
        """Test registration view when email is already in use."""
        response = self.client.post(
            reverse("accounts:register"),
            {
                "email": "testuser@example.com",
                "password1": "C*pml3XP4ssw0RD!",
                "password2": "C*pml3XP4ssw0RD!",
            },
        )
        self.assertEqual(response.status_code, 200)  # Stays on the registration page
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(
            any("This email is already registered." in str(m) for m in messages)
        )

    def test_register_view_invalid_email(self):
        """Test registration view with invalid email."""
        response = self.client.post(
            reverse("accounts:register"),
            {
                "email": "invalidemail@email",
                "password1": "C*pml3XP4ssw0RD!",
                "password2": "C*pml3XP4ssw0RD!",
            },
        )
        self.assertEqual(response.status_code, 200)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(
            any("Email is not valid. Please try again with a valid email." in str(m) for m in messages)
        )

    def test_register_view_post_password_mismatch(self):
        """Test registration view with password mismatch."""
        response = self.client.post(
            reverse("accounts:register"),
            {
                "email": "anotheruser@example.com",
                "password1": "C*pml3XP4ssw0RD!",
                "password2": "differentpassword",
            },
        )
        self.assertEqual(response.status_code, 200)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(
            any("Password mismatch." in str(m) for m in messages)
        )

    def test_login_view_get(self):
        """Test that the login view returns a 200 OK status on GET request."""
        response = self.client.get(reverse("accounts:login"))
        self.assertEqual(response.status_code, 200)

    def test_login_view_get_redirects_authenticated_user(self):
        """Test that the login page redirects when authenticated users hits login page again."""
        self.client.login(username="testuser", password="testpass")
        response = self.client.get(reverse("accounts:login"))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/recipient_dashboard")

    def test_login_view_post_success(self):
        """Test login view with correct credentials."""
        response = self.client.post(
            reverse("accounts:login"),
            {
                "username": "testuser@example.com",
                "password": "testpass",
            },
        )
        self.assertEqual(
            response.status_code, 302
        )  # Redirects after successful registration
        self.assertEqual(response.url, "/accounts/profile/")

    def test_login_view_post_invalid_credentials(self):
        """Test login view with incorrect credentials."""
        response = self.client.post(
            reverse("accounts:login"),
            {
                "username": "testuser@example.com",
                "password": "wrongpass",
            },
        )
        self.assertEqual(response.status_code, 200)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("Incorrect email or password" in str(m) for m in messages))

    def test_profile_view_redirects_unauthenticated_user(self):
        """Test that the profile view redirects unauthenticated users to the login page."""
        response = self.client.get(reverse("accounts:profile"))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response, f"{reverse('accounts:login')}?next=/accounts/profile/"
        )

    def test_profile_view_authenticated_user(self):
        """Test that the profile view redirects authenticated users to /recipient_dashboard."""
        self.client.login(username="testuser", password="testpass")
        response = self.client.get(reverse("accounts:profile"))

        self.assertEqual(
            response.status_code, 302
        )  # Redirects after successful registration
        self.assertEqual(response.url, "/recipient_dashboard")

    def test_logout_view_clears_messages(self):
        """Test that the logout view clears messages and redirects."""
        self.client.login(username="testuser", password="testpass")
        response = self.client.get(reverse("accounts:logout"))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/")
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 0)
