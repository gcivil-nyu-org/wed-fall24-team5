from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from database.models import Order, Donation, Organization, UserReview
from django.utils import timezone
from datetime import timedelta
from uuid import uuid4
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

    def test_pickup_order_success(self):
        """Test that a pending order is successfully marked as picked up."""
        response = self.client.get(reverse("pickup_order", args=[self.order.order_id]))

        # Check that the order status is updated to "picked_up"
        self.order.refresh_from_db()
        self.assertEqual(self.order.order_status, "picked_up")

        # Check that the user is redirected to recipient_orders
        self.assertRedirects(response, reverse("recipient_orders"))

        # Verify success message
        messages = list(response.wsgi_request._messages)
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Donation marked as picked up successfully.")

    def test_pickup_order_failure(self):
        """Test that marking an invalid order as picked up fails gracefully."""
        invalid_order_id = uuid4()  # UUID that doesn't exist
        response = self.client.get(reverse("pickup_order", args=[invalid_order_id]))

        # Check that the user is redirected to recipient_orders
        self.assertRedirects(response, reverse("recipient_orders"))

        # Verify failure message
        messages = list(response.wsgi_request._messages)
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            "Unable to mark order as picked up. Please try again later.",
        )

    def test_mark_order_as_pending_success(self):
        """Test that a picked up order is successfully marked as pending."""
        # Change the order status to picked_up
        self.order.order_status = "picked_up"
        self.order.save()

        response = self.client.get(
            reverse("mark_order_as_pending", args=[self.order.order_id])
        )

        # Check that the order status is updated to "pending"
        self.order.refresh_from_db()
        self.assertEqual(self.order.order_status, "pending")

        # Check that the user is redirected to recipient_orders
        self.assertRedirects(response, reverse("recipient_orders"))

        # Verify success message
        messages = list(response.wsgi_request._messages)
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Donation marked as pending successfully.")

    def test_mark_order_as_pending_failure(self):
        """Test that marking an invalid order as pending fails gracefully."""
        invalid_order_id = uuid4()  # UUID that doesn't exist
        response = self.client.get(
            reverse("mark_order_as_pending", args=[invalid_order_id])
        )

        # Check that the user is redirected to recipient_orders
        self.assertRedirects(response, reverse("recipient_orders"))

        # Verify failure message
        messages = list(response.wsgi_request._messages)
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]), "Unable to mark order as pending. Please try again later."
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


class ModifyOrderTests(TestCase):
    def setUp(self):
        # Create test user with a unique email
        User = get_user_model()
        self.user = User.objects.create_user(
            username="testuser", email="testuser@example.com", password="testpass123"
        )
        self.client = Client()
        self.client.login(username="testuser", password="testpass123")

        # Create test organization
        self.organization = Organization.objects.create(
            organization_name="Test Organization",
            type="restaurant",
            address="123 Test St",
            zipcode=12345,
            contact_number="1234567890",
            email="organization@example.com",
            active=True,
        )

        # Create test donation
        self.donation = Donation.objects.create(
            organization=self.organization,
            food_item="Test Food",
            quantity=5,
            pickup_by=timezone.now() + timedelta(days=1),
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

    def test_modify_order_success(self):
        """Test successful order modification within limits"""
        response = self.client.post(
            reverse("modify_order"),
            {"order_id": self.order.order_id, "new_quantity": 3, "current_quantity": 2},
        )
        self.assertRedirects(response, reverse("recipient_orders"))

        # Check if order was updated
        updated_order = Order.objects.get(order_id=self.order.order_id)
        self.assertEqual(updated_order.order_quantity, 3)

        # Check if donation quantity was updated
        updated_donation = Donation.objects.get(donation_id=self.donation.donation_id)
        self.assertEqual(updated_donation.quantity, 4)  # Original 5 - (3-2)

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), "Order quantity updated successfully")

    def test_modify_order_exceeds_maximum(self):
        """Test order modification exceeding maximum allowed quantity"""
        response = self.client.post(
            reverse("modify_order"),
            {"order_id": self.order.order_id, "new_quantity": 4, "current_quantity": 2},
        )
        self.assertRedirects(response, reverse("recipient_orders"))

        updated_order = Order.objects.get(order_id=self.order.order_id)
        self.assertEqual(updated_order.order_quantity, 2)

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), "Maximum allowed quantity is 3")

    def test_modify_order_zero_quantity(self):
        """Test order modification with zero quantity"""
        response = self.client.post(
            reverse("modify_order"),
            {"order_id": self.order.order_id, "new_quantity": 0, "current_quantity": 2},
        )
        self.assertRedirects(response, reverse("recipient_orders"))

        updated_order = Order.objects.get(order_id=self.order.order_id)
        self.assertEqual(updated_order.order_quantity, 2)

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), "Quantity must be at least 1")

    def test_modify_nonexistent_order(self):
        """Test modifying an order that doesn't exist"""
        import uuid

        fake_order_id = uuid.uuid4()

        response = self.client.post(
            reverse("modify_order"),
            {"order_id": fake_order_id, "new_quantity": 2, "current_quantity": 2},
        )
        self.assertRedirects(response, reverse("recipient_orders"))

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), "Order not found")

    def test_modify_order_unauthorized_user(self):
        """Test modifying an order as an unauthorized user"""
        User = get_user_model()
        other_user = User.objects.create_user(  # noqa
            username="otheruser", email="otheruser@example.com", password="testpass123"
        )
        self.client.login(username="otheruser", password="testpass123")

        response = self.client.post(
            reverse("modify_order"),
            {"order_id": self.order.order_id, "new_quantity": 3, "current_quantity": 2},
        )
        self.assertRedirects(response, reverse("recipient_orders"))

        updated_order = Order.objects.get(order_id=self.order.order_id)
        self.assertEqual(updated_order.order_quantity, 2)

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), "Order not found")

    def test_modify_order_get_request(self):
        """Test that GET requests are rejected"""
        response = self.client.get(reverse("modify_order"))
        self.assertRedirects(response, reverse("recipient_orders"))

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), "Invalid request method")

    def test_modify_completed_order(self):
        """Test modifying a completed order"""
        self.order.order_status = "picked_up"
        self.order.save()

        response = self.client.post(
            reverse("modify_order"),
            {"order_id": self.order.order_id, "new_quantity": 3, "current_quantity": 2},
        )
        self.assertRedirects(response, reverse("recipient_orders"))

        updated_order = Order.objects.get(order_id=self.order.order_id)
        self.assertEqual(updated_order.order_quantity, 2)

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), "Order not found")

    def test_modify_order_inactive(self):
        """Test modifying an inactive order"""
        self.order.active = False
        self.order.save()

        response = self.client.post(
            reverse("modify_order"),
            {"order_id": self.order.order_id, "new_quantity": 3, "current_quantity": 2},
        )
        self.assertRedirects(response, reverse("recipient_orders"))

        updated_order = Order.objects.get(order_id=self.order.order_id)
        self.assertEqual(updated_order.order_quantity, 2)

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), "Order not found")

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
