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


class ModelsTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        """Set up non-modified data for all class tests."""
        # Create test users
        cls.user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="password123",
            first_name="Test",
            last_name="User",
        )
        cls.user2 = User.objects.create_user(
            username="testuser2",
            email="testuser2@example.com",
            password="password123",
            first_name="Test",
            last_name="User2",
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

        cls.organization2 = Organization.objects.create(
            organization_name="Test Organization 2",
            type="food_pantry",
            address="456 Test Ave",
            zipcode=12346,
        )

        # Handle UserProfile creation
        cls.profile, _ = UserProfile.objects.get_or_create(
            user=cls.user, defaults={"phone_number": "555-5678", "active": True}
        )

    def test_organization_creation(self):
        """Test organization creation and all its fields"""
        org = self.organization
        self.assertEqual(org.organization_name, "Test Organization")
        self.assertEqual(org.type, "restaurant")
        self.assertEqual(org.address, "123 Test St")
        self.assertEqual(org.zipcode, 12345)
        self.assertEqual(org.contact_number, "555-1234")
        self.assertEqual(org.email, "contact@example.com")
        self.assertEqual(org.website, "https://example.com")
        self.assertTrue(org.active)
        self.assertIsNotNone(org.created_at)
        self.assertIsNotNone(org.modified_at)
        self.assertEqual(str(org), "Test Organization")

    def test_user_profile_signal(self):
        """Test that UserProfile is automatically created when User is created"""
        new_user = User.objects.create_user(
            username="signaltest", email="signal@test.com", password="password123"
        )
        self.assertTrue(hasattr(new_user, "userprofile"))
        self.assertIsNotNone(new_user.userprofile)

    def test_user_profile_update(self):
        """Test UserProfile update functionality"""
        self.profile.phone_number = "999-9999"
        self.profile.save()
        refreshed_profile = UserProfile.objects.get(user=self.user)
        self.assertEqual(refreshed_profile.phone_number, "999-9999")
        self.assertEqual(str(refreshed_profile), "testuser")

    def test_organization_admin_creation(self):
        """Test OrganizationAdmin creation and string representation"""
        admin = OrganizationAdmin.objects.create(
            organization=self.organization,
            user=self.user,
            access_level="Owner",
        )
        self.assertEqual(admin.access_level, "Owner")
        self.assertTrue(admin.active)
        self.assertEqual(str(admin), "Test User - Test Organization")

    def test_donation_creation(self):
        """Test Donation creation and string representation"""
        donation = Donation.objects.create(
            organization=self.organization,
            food_item="Canned Beans",
            quantity=100,
            pickup_by=date.today(),
        )
        self.assertEqual(donation.food_item, "Canned Beans")
        self.assertEqual(donation.quantity, 100)
        self.assertTrue(donation.active)
        self.assertEqual(str(donation), "Canned Beans - Test Organization")

    def test_user_review_creation(self):
        """Test UserReview creation and string representation"""
        review = UserReview.objects.create(
            organization=self.organization,
            user=self.user,
            rating=5,
            comment="Great organization!",
        )
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.comment, "Great organization!")
        self.assertTrue(review.active)
        self.assertEqual(str(review), "Review by Test User for Test Organization")

    def test_message_creation(self):
        """Test Message creation with all combinations and string representation"""
        message = Message.objects.create(
            sender_user=self.user,
            receiver_user=self.user2,
            message_body="Hello, this is a test message!",
        )
        self.assertEqual(message.message_body, "Hello, this is a test message!")
        self.assertEqual(str(message), "Message from Test User to Test User2")

    def test_order_creation(self):
        """Test Order creation and string representation"""
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
        self.assertEqual(order.order_status, "pending")
        self.assertTrue(order.active)
        self.assertIn("order_id", str(order))
        self.assertIn("Test User", str(order))
