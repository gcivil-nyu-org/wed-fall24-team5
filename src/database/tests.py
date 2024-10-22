from django.test import TestCase
from django.contrib.auth.models import User
from .models import (
    Organization,
    UserProfile,
    OrganizationAdmin,
    Donation,
    UserReview,
    Message,
    Order,
)
from datetime import date


class DummyTestCase(TestCase):
    def test_dummy(self):
        """A dummy test to satisfy flake8."""
        organization = Organization.objects.create(
            organization_name="Test Organization",
            type="restaurant",
            address="123 Test Street",
            zipcode=10001,
        )
        self.assertTrue(organization.organization_name == "Test Organization")


class ModelsTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        """
        Set up non-modified data for all class tests.
        This is run once at the beginning of the test run.
        """
        # Create test users
        cls.user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="password123"
        )
        cls.user2 = User.objects.create_user(
            username="testuser2",
            email="testuser2@example.com",
            password="password123"
        )

        # Create test organization
        cls.organization = Organization.objects.create(
            organization_name="Test Organization",
            type="restaurant",
            address="123 Test St",
            zipcode=12345,
            contact_number="555-1234",
            email="contact@example.com",
            website="https://example.com",
        )

        # Create test user profile
        cls.profile = UserProfile.objects.create(
            user=cls.user,
            phone_number="555-5678",
            active=True
        )

    def test_organization_creation(self):
        self.assertEqual(self.organization.type, "restaurant")

    def test_user_profile_creation(self):
        self.assertEqual(self.profile.phone_number, "555-5678")

    def test_organization_admin_creation(self):
        admin = OrganizationAdmin.objects.create(
            organization=self.organization,
            user=self.user,
            access_level="Owner",
        )
        self.assertEqual(admin.access_level, "Owner")

    def test_donation_creation(self):
        donation = Donation.objects.create(
            organization=self.organization,
            food_item="Canned Beans",
            quantity=100,
            pickup_by=date.today(),
        )
        self.assertEqual(donation.food_item, "Canned Beans")

    def test_user_review_creation(self):
        review = UserReview.objects.create(
            organization=self.organization,
            user=self.user,
            rating=5,
            comment="Great organization!",
        )
        self.assertEqual(review.rating, 5)

    def test_message_creation(self):
        message = Message.objects.create(
            sender_user=self.user,
            receiver_user=self.user2,
            message_body="Hello, this is a test message!",
        )
        self.assertEqual(message.message_body, "Hello, this is a test message!")

    def test_order_creation(self):
        donation = Donation.objects.create(
            organization=self.organization,
            food_item="Canned Beans",
            quantity=100,
            pickup_by=date.today(),
        )
        order = Order.objects.create(
            donation=donation,
            user=self.user,
            order_quantity=10,
            order_status="pending",
        )
        self.assertEqual(order.order_quantity, 10)