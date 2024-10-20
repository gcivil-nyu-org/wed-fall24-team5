from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from database.models import Donation, Organization


class RecipientDashboardViewTests(TestCase):
    def setUp(self):
        # Creating a dummy user for testing
        User = get_user_model()
        self.user = User.objects.create_user(username="testuser", password="testpass")

        # Logging in the user
        self.client.login(username="testuser", password="testpass")

        # Create an organization for donations
        self.organization = Organization.objects.create(
            organization_name="Team 5 Test Organization",
            type="restaurant",
            address="123 Test St",
            zipcode=12345,
            contact_number="1234567890",
            email="test@example.com",
            website="http://test.org",
            active=True,
        )

        # Create active donations for testing
        self.donation1 = Donation.objects.create(
            organization_id=self.organization.organization_id,
            food_item="Biryani",
            quantity=10,
            pickup_by="2024-10-15",
            active=True,
        )
        self.donation2 = Donation.objects.create(
            organization_id=self.organization.organization_id,
            food_item="Shawarma",
            quantity=5,
            pickup_by="2024-10-15",
            active=True,
        )

    def test_recipient_dashboard_status_code(self):
        """
        Test that the recipient dashboard view returns a 200 OK status.
        """
        response = self.client.get(reverse("recipient_dashboard"))
        self.assertEqual(response.status_code, 200)

    def test_recipient_dashboard_template_used(self):
        """
        Test that the correct template is used for the recipient dashboard.
        """
        response = self.client.get(reverse("recipient_dashboard"))
        self.assertTemplateUsed(response, "recipient_dashboard/dashboard.html")

    def test_recipient_dashboard_active_donations(self):
        """
        Test that the context contains only active donations.
        """
        response = self.client.get(reverse("recipient_dashboard"))
        self.assertIn("donations", response.context)
        self.assertEqual(
            len(response.context["donations"]), 2
        )  # Should include 2 active donations

    def test_recipient_dashboard_donations_content(self):
        """
        Test that the donations returned are as expected.
        """
        response = self.client.get(reverse("recipient_dashboard"))
        donation_items = [
            donation.food_item for donation in response.context["donations"]
        ]
        self.assertIn("Biryani", donation_items)
        self.assertIn("Shawarma", donation_items)
        self.assertNotIn(
            "Pasta", donation_items
        )  # Checking if a non-listed item is checked or not
