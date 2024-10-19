from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from database.models import Order, Donation, Organization
from django.utils import timezone
from datetime import timedelta


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
            active=True
        )

        # Create test donations
        self.donation1 = Donation.objects.create(
            organization=self.organization,
            food_item="Pizza",
            quantity=10,
            pickup_by=timezone.now() + timedelta(days=2),
            active=True
        )
        self.donation2 = Donation.objects.create(
            organization=self.organization,
            food_item="Burger",
            quantity=5,
            pickup_by=timezone.now() + timedelta(days=2),
            active=True
        )
        
        # Create orders with different statuses
        Order.objects.create(
            donation=self.donation1,
            user=self.user,
            order_quantity=2,
            order_status="pending",
            active=True
        )
        Order.objects.create(
            donation=self.donation1,
            user=self.user,
            order_quantity=1,
            order_status="picked_up",
            active=True
        )
        Order.objects.create(
            donation=self.donation2,
            user=self.user,
            order_quantity=3,
            order_status="canceled",
            active=True
        )

    def test_recipient_orders_status_code(self):
        """Test that the recipient orders view returns a 200 OK status."""
        response = self.client.get(reverse('recipient_orders'))
        self.assertEqual(response.status_code, 200)

    def test_recipient_orders_template_used(self):
        """Test that the correct template is used."""
        response = self.client.get(reverse('recipient_orders'))
        self.assertTemplateUsed(response, "recipient_orders/orders.html")

    def test_recipient_orders_grouped_by_status(self):
        """Test that orders are correctly grouped by status."""
        response = self.client.get(reverse('recipient_orders'))

        # Test that the pending orders are returned correctly
        pending_orders = response.context['pending_orders']
        self.assertEqual(pending_orders.count(), 1)
        self.assertEqual(pending_orders.first().donation.food_item, "Pizza")

        # Test that the picked up orders are returned correctly
        picked_up_orders = response.context['picked_up_orders']
        self.assertEqual(picked_up_orders.count(), 1)
        self.assertEqual(picked_up_orders.first().donation.food_item, "Pizza")

        # Test that the canceled orders are returned correctly
        canceled_orders = response.context['canceled_orders']
        self.assertEqual(canceled_orders.count(), 1)
        self.assertEqual(canceled_orders.first().donation.food_item, "Burger")
        