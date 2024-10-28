from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from database.models import Order, Donation, Organization, UserReview
from django.utils import timezone
from datetime import timedelta
from django.contrib.messages import get_messages


class RecipientOrdersViewTests(TestCase):

    def setUp(self):
        # Create a test user
        User = get_user_model()
        self.user = User.objects.create_user(username="testuser", password="testpass")

        # Log in the user
        self.client.login(username="testuser", password="testpass")

        # Create a test organization
        self.organization = Organization.objects.create(
            organization_name="Test Organization",
            type="restaurant",
            address="123 Test St",
            zipcode=12345,
            contact_number="1234567890",
            email="test@example.com",
            active=True,
        )

        # Create test donations
        self.donation1 = Donation.objects.create(
            organization=self.organization,
            food_item="Pizza",
            quantity=10,
            pickup_by=timezone.now() + timedelta(days=2),
            active=True,
        )
        self.donation2 = Donation.objects.create(
            organization=self.organization,
            food_item="Burger",
            quantity=5,
            pickup_by=timezone.now() + timedelta(days=2),
            active=True,
        )

        # Create orders with different statuses
        Order.objects.create(
            donation=self.donation1,
            user=self.user,
            order_quantity=2,
            order_status="pending",
            active=True,
        )
        Order.objects.create(
            donation=self.donation1,
            user=self.user,
            order_quantity=1,
            order_status="picked_up",
            active=True,
        )
        Order.objects.create(
            donation=self.donation2,
            user=self.user,
            order_quantity=3,
            order_status="canceled",
            active=True,
        )

    def test_recipient_orders_status_code(self):
        """Test that the recipient orders view returns a 200 OK status."""
        response = self.client.get(reverse("recipient_orders"))
        self.assertEqual(response.status_code, 200)

    def test_recipient_orders_template_used(self):
        """Test that the correct template is used."""
        response = self.client.get(reverse("recipient_orders"))
        self.assertTemplateUsed(response, "recipient_orders/orders.html")

    def test_recipient_orders_grouped_by_status(self):
        """Test that orders are correctly grouped by status."""
        response = self.client.get(reverse("recipient_orders"))

        # Test that the pending orders are returned correctly
        pending_orders = response.context["pending_orders"]
        self.assertEqual(pending_orders.count(), 1)
        self.assertEqual(pending_orders.first().donation.food_item, "Pizza")

        # Test that the picked up orders are returned correctly
        picked_up_orders = response.context["picked_up_orders"]
        self.assertEqual(picked_up_orders.count(), 1)
        self.assertEqual(picked_up_orders.first().donation.food_item, "Pizza")

        # Test that the canceled orders are returned correctly
        canceled_orders = response.context["canceled_orders"]
        self.assertEqual(canceled_orders.count(), 1)
        self.assertEqual(canceled_orders.first().donation.food_item, "Burger")


class CancelOrderTests(TestCase):
    def setUp(self):
        # Create test user
        User = get_user_model()
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.client.login(username="testuser", password="testpass")

        # Create test organization
        self.organization = Organization.objects.create(
            organization_name="Test Organization",
            type="restaurant",
            address="123 Test St",
            zipcode=12345,
            contact_number="1234567890",
            email="test@example.com",
            active=True,
        )

        # Create test donation
        self.donation = Donation.objects.create(
            organization=self.organization,
            food_item="Test Food",
            quantity=5,
            pickup_by=timezone.now().date(),
            active=True,
        )

        # Create test order
        self.order = Order.objects.create(
            donation=self.donation,
            user=self.user,
            order_quantity=2,
            order_status="pending",
            active=True,
        )

    def test_cancel_order_success(self):
        """Test successful cancellation of a pending order"""
        initial_donation_quantity = self.donation.quantity
        response = self.client.post(reverse("cancel_order", args=[self.order.order_id]))

        # Check redirect
        self.assertRedirects(response, reverse("recipient_orders"))

        # Refresh order from database
        self.order.refresh_from_db()
        self.donation.refresh_from_db()

        # Check order status
        self.assertEqual(self.order.order_status, "canceled")

        # Check donation quantity was restored
        self.assertEqual(
            self.donation.quantity,
            initial_donation_quantity + self.order.order_quantity,
        )

        # Check success message
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(
            str(messages[0]), "Your reservation has been cancelled successfully."
        )

    def test_cancel_non_pending_order(self):
        """Test attempting to cancel a non-pending order"""
        self.order.order_status = "picked_up"
        self.order.save()

        response = self.client.post(reverse("cancel_order", args=[self.order.order_id]))

        # Check redirect
        self.assertRedirects(response, reverse("recipient_orders"))

        # Refresh order from database
        self.order.refresh_from_db()

        # Check order status hasn't changed
        self.assertEqual(self.order.order_status, "picked_up")

        # Check error message
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), "Only pending orders can be cancelled.")

    def test_cancel_order_get_request(self):
        """Test that GET requests are not allowed for canceling orders"""
        response = self.client.get(reverse("cancel_order", args=[self.order.order_id]))

        # Check redirect
        self.assertRedirects(response, reverse("recipient_orders"))

        # Check error message
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), "Invalid request method.")

    def test_cancel_nonexistent_order(self):
        """Test attempting to cancel a non-existent order"""
        response = self.client.post(
            reverse("cancel_order", args=["12345678-1234-5678-1234-567812345678"])
        )
        self.assertEqual(response.status_code, 404)


class RecipientOrdersTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.client.login(username="testuser", password="testpass")

        # Create test organization
        self.organization = Organization.objects.create(
            organization_name="Test Organization",
            type="restaurant",
            address="123 Test St",
            zipcode=12345,
            contact_number="1234567890",
            email="test@example.com",
            active=True,
        )

        # Create test donation
        self.donation = Donation.objects.create(
            organization=self.organization,
            food_item="Test Food",
            quantity=5,
            pickup_by=timezone.now().date(),
            active=True,
        )

        self.order = Order.objects.create(
            user=self.user,
            donation=self.donation,
            order_quantity=2,
            order_status="picked_up",
            active=True,
        )

    def test_attach_review_to_order(self):
        """Test if review is correctly attached to each order in recipient_orders"""
        UserReview.objects.create(
            donation=self.donation,
            user=self.user,
            rating=5,
            comment="Great food!",
            active=True,
        )

        response = self.client.get(reverse("recipient_orders"))
        orders = response.context["picked_up_orders"]

        # Check that the review is correctly attached to the order
        self.assertEqual(orders[0].review.rating, 5)
        self.assertEqual(orders[0].review.comment, "Great food!")
        self.assertEqual(orders[0].review.donation, self.donation)


class SubmitReviewTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.client.login(username="testuser", password="testpass")

        # Create test organization
        self.organization = Organization.objects.create(
            organization_name="Test Organization",
            type="restaurant",
            address="123 Test St",
            zipcode=12345,
            contact_number="1234567890",
            email="test@example.com",
            active=True,
        )

        # Create test donation
        self.donation = Donation.objects.create(
            organization=self.organization,
            food_item="Test Food",
            quantity=5,
            pickup_by=timezone.now().date(),
            active=True,
        )
        self.order = Order.objects.create(
            user=self.user,
            donation=self.donation,
            order_quantity=2,
            order_status="picked_up",
            active=True,
        )

    def test_create_review(self):
        """Test creating a new review if one doesn't exist"""
        data = {
            "order_id": str(self.order.pk),
            "rating": 4,
            "comment": "Very good food",
        }

        response = self.client.post(reverse("submit_review"), data)

        self.assertEqual(UserReview.objects.count(), 1)
        review = UserReview.objects.first()
        self.assertEqual(review.donation, self.donation)
        self.assertEqual(review.user, self.user)
        self.assertEqual(review.rating, 4)
        self.assertEqual(review.comment, "Very good food")
        self.assertRedirects(response, reverse("recipient_orders"))

    def test_update_existing_review(self):
        """Test updating an existing review if it already exists"""
        # Create an initial review
        UserReview.objects.create(
            donation=self.donation,
            user=self.user,
            rating=3,
            comment="Good food",
            active=True,
        )

        data = {
            "order_id": str(self.order.pk),
            "rating": 5,
            "comment": "Excellent food!",
        }

        response = self.client.post(reverse("submit_review"), data)

        # Check that the review has been updated
        review = UserReview.objects.first()
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.comment, "Excellent food!")
        self.assertRedirects(response, reverse("recipient_orders"))
