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


# Create your tests here.
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

    def setUp(self):
        # For clean up track what needs to be deleted
        # later during tear down (I am reseraching if this is actually needed,
        # since Django already tears down things automatically)
        self.created_users = []
        self.created_organizations = []
        self.created_profiles = []
        self.created_admins = []
        self.created_donations = []
        self.created_reviews = []
        self.created_messages = []
        self.created_orders = []

        # Create Users
        user = User.objects.create_user(
            username="testuser", email="testuser@example.com", password="password123"
        )
        user2 = User.objects.create_user(
            username="testuser2", email="testuser2@example.com", password="password123"
        )
        self.created_users.extend([user, user2])

        # Create an Organization
        organization = Organization.objects.create(
            organization_name="Test Organization",
            type="restaurant",
            address="123 Test St",
            zipcode=12345,
            contact_number="555-1234",
            email="contact@example.com",
            website="https://example.com",
        )
        self.created_organizations.append(organization)

        # Create a UserProfile
        profile = UserProfile.objects.create(
            user=user, phone_number="555-5678", active=True
        )
        self.created_profiles.append(profile)

    def tearDown(self):
        """Cleanup only the objects created during tests."""
        for obj in self.created_orders:
            obj.delete()
        for obj in self.created_messages:
            obj.delete()
        for obj in self.created_reviews:
            obj.delete()
        for obj in self.created_donations:
            obj.delete()
        for obj in self.created_admins:
            obj.delete()
        for obj in self.created_profiles:
            obj.delete()
        for obj in self.created_organizations:
            obj.delete()
        for obj in self.created_users:
            obj.delete()

    def test_organization_creation(self):
        self.assertEqual(self.created_organizations[0].type, "restaurant")

    def test_user_profile_creation(self):
        self.assertEqual(self.created_profiles[0].phone_number, "555-5678")

    def test_organization_admin_creation(self):
        admin = OrganizationAdmin.objects.create(
            organization=self.created_organizations[0],
            user=self.created_users[0],
            access_level="Owner",
        )
        self.created_admins.append(admin)
        self.assertEqual(admin.access_level, "Owner")

    def test_donation_creation(self):
        donation = Donation.objects.create(
            organization=self.created_organizations[0],
            food_item="Canned Beans",
            quantity=100,
            pickup_by=date.today(),
        )
        self.created_donations.append(donation)
        self.assertEqual(donation.food_item, "Canned Beans")

    def test_user_review_creation(self):
        review = UserReview.objects.create(
            organization=self.created_organizations[0],
            user=self.created_users[0],
            rating=5,
            comment="Great organization!",
        )
        self.created_reviews.append(review)
        self.assertEqual(review.rating, 5)

    def test_message_creation(self):
        message = Message.objects.create(
            sender_user=self.created_users[0],
            receiver_user=self.created_users[1],
            message_body="Hello, this is a test message!",
        )
        self.created_messages.append(message)
        self.assertEqual(message.message_body, "Hello, this is a test message!")

    def test_order_creation(self):
        donation = Donation.objects.create(
            organization=self.created_organizations[0],
            food_item="Canned Beans",
            quantity=100,
            pickup_by=date.today(),
        )
        self.created_donations.append(donation)

        order = Order.objects.create(
            donation=donation,
            user=self.created_users[0],
            order_quantity=10,
            order_status="pending",
        )
        self.created_orders.append(order)
        self.assertEqual(order.order_quantity, 10)
