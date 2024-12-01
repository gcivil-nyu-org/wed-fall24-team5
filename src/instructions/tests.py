from django.test import TestCase
from django.contrib.sites.models import Site
from django.urls import reverse
from django.contrib.auth import get_user_model


# Create your tests here.
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


class InstructionsPageTest(TestData):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username="testuser", email="testuser@example.com", password="testpass"
        )

    def test_instructions_view_not_authenticate(self):
        """Test that the instructions view returns to login page if not logged in"""
        response = self.client.get(reverse("instructions"))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response, f"{reverse('accounts:login')}?next=/instructions/"
        )

    def test_instructions_view_authenticated(self):
        """Test that the instructions view returns successfully if logged in"""
        self.client.login(username="testuser", password="testpass")
        response = self.client.get(reverse("instructions"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "instructions/instructions.html")
