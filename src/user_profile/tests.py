from django.test import TestCase, TransactionTestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.contrib import messages
from database.models import UserProfile
from django.utils import timezone
from django.db import transaction


class ProfileViewTests(TestCase):
    def setUp(self):
        # Set up a user and profile for testing
        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="password123",
            first_name="Test",
            last_name="User",
        )

        self.user_profile, _ = UserProfile.objects.get_or_create(
            user=self.user, defaults={"phone_number": "555-5678", "active": True}
        )
        self.client.login(username="testuser", password="password123")

    def test_profile_view_get_request(self):
        """Test GET request to profile view retrieves profile details."""
        response = self.client.get(reverse("user_profile:profile"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "user_profile/profile.html")
        self.assertContains(response, self.user_profile.phone_number)

    def test_profile_view_post_request_successful_update(self):
        """Test successful profile update via POST request."""
        with transaction.atomic():  # Ensure transaction block for this test
            response = self.client.post(
                reverse("user_profile:profile"),
                {
                    "first_name": "John",
                    "last_name": "Doe",
                    "phone_number": "0987654321",
                }
            )

        self.user.refresh_from_db()
        self.user_profile.refresh_from_db()

        # Verify changes were saved
        self.assertEqual(self.user.first_name, "John")
        self.assertEqual(self.user.last_name, "Doe")
        self.assertEqual(self.user_profile.phone_number, "0987654321")

        # Check for success message
        messages_list = list(messages.get_messages(response.wsgi_request))
        self.assertIn("Profile updated successfully!", [msg.message for msg in messages_list])
        
        # Check redirection
        self.assertRedirects(response, reverse("user_profile:profile"))

    def test_profile_update_error_handling(self):
        """Test profile update with simulated failure to trigger error message"""
        # Introduce an error by setting an invalid phone number that exceeds allowed length
        response = self.client.post(
            reverse("user_profile:profile"),
            {
                "first_name": "ValidFirstName",
                "last_name": "ValidLastName",
                "phone_number": "1" * 50  # This will fail due to max_length=20 in phone_number
            }
        )

        # Check for warning message
        messages_list = list(messages.get_messages(response.wsgi_request))
        
        # self.assertIn("Some error occured while updating your profile!", [msg.message for msg in messages_list])

        # Ensure data was not updated due to error
        self.user.refresh_from_db()
        self.user_profile.refresh_from_db()
        self.assertNotEqual(self.user.first_name, "ValidFirstName")
        self.assertNotEqual(self.user_profile.phone_number, "1" * 50)
