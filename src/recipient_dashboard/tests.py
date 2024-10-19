from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from database.models import Donation, Organization, Order
from django.utils import timezone  # for pickup date being tomorrow in tests
from datetime import timedelta  # for pickup date being tomorrow in tests
from django.contrib.messages import get_messages  # to capture messages
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp

# class RecipientDashboardViewTests(TestCase):
#     def setUp(self):
#         # Creating a dummy user for testing
#         User = get_user_model()
#         self.user = User.objects.create_user(username="testuser", password="testpass")

#         # Logging in the user
#         self.client.login(username="testuser", password="testpass")

#         # Create an organization for donations
#         self.organization = Organization.objects.create(
#             organization_name="Team 5 Test Organization",
#             type="restaurant",
#             address="123 Test St",
#             zipcode=12345,
#             contact_number="1234567890",
#             email="test@example.com",
#             website="http://test.org",
#             active=True,
#         )

#         # Create active donations for testing
#         self.donation1 = Donation.objects.create(
#             organization_id=self.organization,
#             food_item="Biryani",
#             quantity=10,
#             pickup_by="2024-10-15",
#             active=True,
#         )
#         self.donation2 = Donation.objects.create(
#             organization_id=self.organization,
#             food_item="Shawarma",
#             quantity=5,
#             pickup_by="2024-10-15",
#             active=True,
#         )

#     def test_recipient_dashboard_status_code(self):
#         """
#         Test that the recipient dashboard view returns a 200 OK status.
#         """
#         response = self.client.get(reverse("recipient_dashboard"))
#         self.assertEqual(response.status_code, 200)

#     def test_recipient_dashboard_template_used(self):
#         """
#         Test that the correct template is used for the recipient dashboard.
#         """
#         response = self.client.get(reverse("recipient_dashboard"))
#         self.assertTemplateUsed(response, "recipient_dashboard/dashboard.html")

#     def test_recipient_dashboard_active_donations(self):
#         """
#         Test that the context contains only active donations.
#         """
#         response = self.client.get(reverse("recipient_dashboard"))
#         self.assertIn("donations", response.context)
#         self.assertEqual(
#             len(response.context["donations"]), 2
#         )  # Should include 2 active donations

#     def test_recipient_dashboard_donations_content(self):
#         """
#         Test that the donations returned are as expected.
#         """
#         response = self.client.get(reverse("recipient_dashboard"))
#         donation_items = [
#             donation.food_item for donation in response.context["donations"]
#         ]
#         self.assertIn("Biryani", donation_items)
#         self.assertIn("Shawarma", donation_items)
#         self.assertNotIn(
#             "Pasta", donation_items
#         )  # Checking if a non-listed item is checked or not


class ReserveDonationTest(TestCase):

    def setUp(self):
        # Creating a dummy user for testing
        User = get_user_model()
        self.user = User.objects.create_user(username="testuser", password="testpass")

        # Logging in the user
        self.client.login(username="testuser", password="testpass")

        # Create an organization
        self.organization = Organization.objects.create(
            organization_name="Test Organization",
            type="restaurant",
            address="123 Test St",
            zipcode=12345,
            contact_number="1234567890",
            email="test@example.com",
            active=True,
        )

        # Create a donation
        self.donation = Donation.objects.create(
            organization=self.organization,
            food_item="Test Food",
            quantity=5,
            pickup_by=timezone.now() + timedelta(days=1),
            active=True,
        )

        # Set up SocialApp for allauth (required for login redirection)
        site = Site.objects.get_current()
        self.social_app = SocialApp.objects.create(
            provider="google",  # or 'facebook', depending on your setup
            name="Test Google App",
            client_id="test-client-id",
            secret="test-secret",
        )
        self.social_app.sites.add(site)

    def test_reserve_donation_success(self):
        """Test a successful donation reservation."""
        response = self.client.get(
            reverse("reserve_donation", args=[self.donation.donation_id])
        )

        # Check if the reservation was successful
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.assertRedirects(response, reverse("recipient_dashboard"))

        # Check if the order was created
        order = Order.objects.filter(
            user=self.user, donation=self.donation, order_status="pending"
        ).first()
        self.assertIsNotNone(order)
        self.assertEqual(order.order_quantity, 1)

        # Check if the donation quantity was reduced
        self.donation.refresh_from_db()
        self.assertEqual(self.donation.quantity, 4)

        # Check if the success message was returned
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Donation reserved successfully.")

    def test_reserve_donation_no_quantity(self):
        """Test reservation when the donation is no longer available."""
        self.donation.quantity = 0
        self.donation.save()

        response = self.client.get(
            reverse("reserve_donation", args=[self.donation.donation_id])
        )

        # Check if it redirects back
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("recipient_dashboard"))

        # Ensure no order was created
        order = Order.objects.filter(user=self.user, donation=self.donation).first()
        self.assertIsNone(order)

        # Check if the error message was returned
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "This donation is no longer available.")

    def test_reserve_donation_not_logged_in(self):
        """Test that a user must be logged in to reserve a donation."""
        self.client.logout()
        response = self.client.get(
            reverse("reserve_donation", args=[self.donation.donation_id])
        )

        # Ensure user is redirected to the login page
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            f"/accounts/login/?next=/recipient_dashboard/reserve/{self.donation.donation_id}/",
        )
