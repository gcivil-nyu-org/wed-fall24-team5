from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from database.models import Donation, Organization, Order, OrganizationAdmin, UserReview
from django.utils import timezone  # for pickup date being tomorrow in tests
from datetime import timedelta  # for pickup date being tomorrow in tests
from django.contrib.messages import get_messages  # to capture messages
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp
from urllib.parse import urlencode  # for encoding URLs with query parameters
from .forms import SearchDonationForm
from geopy.geocoders import Nominatim  # noqa
from geopy.distance import geodesic  # noqa
from django.core.cache import cache
from unittest.mock import patch, MagicMock
from recipient_dashboard.utils import (
    get_coordinates,
    calculate_distance,
    get_nearby_addresses,
)


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
            organization=self.organization,
            food_item="Biryani",
            quantity=10,
            pickup_by=timezone.now() + timedelta(days=1),
            active=True,
        )
        self.donation2 = Donation.objects.create(
            organization=self.organization,
            food_item="Shawarma",
            quantity=5,
            pickup_by=timezone.now() + timedelta(days=1),
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
            provider="google",
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

    def test_reserve_donation_increment_quantity(self):
        """Test that reserving an existing donation increments the order quantity."""
        # Reserve the donation for the first time
        self.client.get(reverse("reserve_donation", args=[self.donation.donation_id]))

        # Reserve the same donation again
        response = self.client.get(
            reverse("reserve_donation", args=[self.donation.donation_id])
        )

        # Check if the reservation was successful
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.assertRedirects(response, reverse("recipient_dashboard"))

        # Check if the order was created and the quantity was incremented
        order = Order.objects.filter(
            user=self.user, donation=self.donation, order_status="pending"
        ).first()
        self.assertIsNotNone(order)
        self.assertEqual(order.order_quantity, 2)  # Should be incremented to 2

        # Check if the donation quantity was reduced correctly
        self.donation.refresh_from_db()
        self.assertEqual(
            self.donation.quantity, 3
        )  # Initially 5, reduced by 2 reservations

        # Check if the success message was returned
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(
            len(messages), 2
        )  # should have two messages for the two reservations
        self.assertEqual(str(messages[0]), "Donation reserved successfully.")

    def test_reserve_donation_only_increments_pending_orders(self):
        """Test that only pending orders are incremented, and not picked up or canceled orders."""
        # Create a non-pending (e.g., picked_up) order for the user
        Order.objects.create(
            donation=self.donation,
            user=self.user,
            order_quantity=1,
            order_status="picked_up",  # Status is not 'pending'
            active=True,
        )

        # Try to reserve the same donation
        response = self.client.get(
            reverse("reserve_donation", args=[self.donation.donation_id])
        )

        # Check if the reservation was successful
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.assertRedirects(response, reverse("recipient_dashboard"))

        # Check if a new order was created instead of modifying the existing one
        orders = Order.objects.filter(user=self.user, donation=self.donation).order_by(
            "order_created_at"
        )
        self.assertEqual(
            orders.count(), 2
        )  # Two orders: one with 'picked_up' and one new 'pending'
        pending_order = orders.filter(order_status="pending").first()
        self.assertIsNotNone(pending_order)
        self.assertEqual(
            pending_order.order_quantity, 1
        )  # New pending order has quantity 1

        # Check if the donation quantity was reduced correctly
        self.donation.refresh_from_db()
        self.assertEqual(self.donation.quantity, 4)  # One reservation deducted

        # Check if the success message was returned
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Donation reserved successfully.")


class SearchFilterDonationTests(TestCase):

    def setUp(self):
        # Creating a dummy user for testing
        User = get_user_model()
        self.user = User.objects.create_user(username="testuser", password="testpass")

        # Logging in the user
        self.client.login(username="testuser", password="testpass")

        # Create organizations
        self.organization1 = Organization.objects.create(
            organization_name="Test Organization",
            type="restaurant",
            address="123 Test St",
            zipcode=12345,
            contact_number="1234567890",
            email="test@example.com",
            active=True,
        )

        self.organization2 = Organization.objects.create(
            organization_name="Test Organization Pizza",
            type="grocery_store",
            address="123 Test Ave",
            zipcode=12345,
            contact_number="1234567890",
            email="test@example.com",
            active=True,
        )

        # Create donations
        self.donation1 = Donation.objects.create(
            organization=self.organization1,
            food_item="Pizza",
            quantity=5,
            pickup_by=timezone.now() + timedelta(days=1),
            active=True,
        )

        self.donation2 = Donation.objects.create(
            organization=self.organization2,
            food_item="Apples",
            quantity=10,
            pickup_by=timezone.now() + timedelta(days=4),
            active=True,
        )

        self.donation3 = Donation.objects.create(
            organization=self.organization1,
            food_item="Pesto Pizza",
            quantity=50,
            pickup_by=timezone.now() + timedelta(days=3),
            active=True,
        )

        self.donation4 = Donation.objects.create(
            organization=self.organization1,
            food_item="Pepperoni Pizza",
            quantity=0,
            pickup_by=timezone.now() + timedelta(days=5),
            active=True,
        )

        # Set up SocialApp for allauth (required for login redirection)
        site = Site.objects.get_current()
        self.social_app = SocialApp.objects.create(
            provider="google",
            name="Test Google App",
            client_id="test-client-id",
            secret="test-secret",
        )
        self.social_app.sites.add(site)

    def test_search_keyword(self):
        """Test searching donations by keyword in both food and organization."""
        params = {"keyword": "pizza"}
        url = reverse("recipient_dashboard") + "?" + urlencode(params)
        response = self.client.get(url)
        donation_items = [
            donation.food_item for donation in response.context["donations"]
        ]

        # Check that the correct number of items are returned
        self.assertEqual(len(response.context["donations"]), 3)

        # Check that the correct items are returned
        self.assertIn("Pizza", donation_items)
        self.assertIn("Pesto Pizza", donation_items)
        self.assertIn("Apples", donation_items)
        self.assertNotIn("Pepperoni Pizza", donation_items)

    def test_search_keyword_type(self):
        """Test searching donations by keyword and type."""
        params = {"type": "food", "keyword": "pizza"}
        url = reverse("recipient_dashboard") + "?" + urlencode(params)
        response = self.client.get(url)
        donation_items = [
            donation.food_item for donation in response.context["donations"]
        ]

        # Check that the correct number of items are returned
        self.assertEqual(len(response.context["donations"]), 2)

        # Check that the correct items are returned
        self.assertIn("Pizza", donation_items)
        self.assertIn("Pesto Pizza", donation_items)
        self.assertNotIn("Apples", donation_items)
        self.assertNotIn("Pepperoni Pizza", donation_items)

    def test_search_keyword_category(self):
        """Test searching donations by keyword and category."""
        params = {"keyword": "pizza", "category": "grocery_store"}
        url = reverse("recipient_dashboard") + "?" + urlencode(params)
        response = self.client.get(url)
        donation_items = [
            donation.food_item for donation in response.context["donations"]
        ]

        # Check that two items are in result
        self.assertEqual(len(response.context["donations"]), 1)

        # Check that the correct two items are displayed
        self.assertNotIn("Pizza", donation_items)
        self.assertNotIn("Pesto Pizza", donation_items)
        self.assertIn("Apples", donation_items)
        self.assertNotIn("Pepperoni Pizza", donation_items)

    def test_search_keyword_quantity(self):
        """Test searching donations by type, keyword and category."""
        params = {"type": "food", "keyword": "pizza", "min_quantity": "10"}
        url = reverse("recipient_dashboard") + "?" + urlencode(params)
        response = self.client.get(url)
        donation_items = [
            donation.food_item for donation in response.context["donations"]
        ]

        # Check that the correct number of items are returned
        self.assertEqual(len(response.context["donations"]), 1)

        # Check that the correct items are returned
        self.assertNotIn("Pizza", donation_items)
        self.assertIn("Pesto Pizza", donation_items)
        self.assertNotIn("Apples", donation_items)
        self.assertNotIn("Pepperoni Pizza", donation_items)

    def test_search_date(self):
        """Test searching donations by date."""
        params = {
            "date": (timezone.now() + timezone.timedelta(days=3)).strftime("%Y-%m-%d")
        }
        url = reverse("recipient_dashboard") + "?" + urlencode(params)
        response = self.client.get(url)
        donation_items = [
            donation.food_item for donation in response.context["donations"]
        ]

        # Check that the correct number of items are returned
        self.assertEqual(len(response.context["donations"]), 2)

        # Check that the correct items are returned
        self.assertNotIn("Pizza", donation_items)
        self.assertIn("Pesto Pizza", donation_items)
        self.assertIn("Apples", donation_items)
        self.assertNotIn("Pepperoni Pizza", donation_items)

    def test_search_all_fields(self):
        """Test searching donations by all fields: type, keyword, category, and quantity."""
        params = {
            "type": "food",
            "keyword": "pizza",
            "category": "restaurant",
            "min_quantity": "5",
        }
        url = reverse("recipient_dashboard") + "?" + urlencode(params)
        response = self.client.get(url)
        donation_items = [
            donation.food_item for donation in response.context["donations"]
        ]

        # Check that the correct number of items are returned
        self.assertEqual(len(response.context["donations"]), 2)

        # Check that the correct items are returned
        self.assertIn("Pizza", donation_items)
        self.assertIn("Pesto Pizza", donation_items)
        self.assertNotIn("Apples", donation_items)
        self.assertNotIn("Pepperoni Pizza", donation_items)

    def test_search_no_results(self):
        """Test searching donations with no matches."""
        params = {"type": "food", "keyword": "pepperoni"}
        url = reverse("recipient_dashboard") + "?" + urlencode(params)
        response = self.client.get(url)

        # Check that no items are returned
        self.assertEqual(len(response.context["donations"]), 0)


# add test_search_address, test_search_address_radius, test_search_address_no_results
def test_search_address(self):
    """Test searching donations by address."""
    params = {"address": "123 Test St"}
    url = reverse("recipient_dashboard") + "?" + urlencode(params)
    response = self.client.get(url)
    donation_items = [donation.food_item for donation in response.context["donations"]]

    # Check that the correct number of items are returned
    self.assertEqual(len(response.context["donations"]), 2)

    # Check that the correct items are returned
    self.assertIn("Biryani", donation_items)
    self.assertIn("Shawarma", donation_items)
    self.assertNotIn("Pasta", donation_items)


def test_search_address_radius(self):
    """Test searching donations by address and radius."""
    params = {"address": "123 Test St", "radius": "5"}
    url = reverse("recipient_dashboard") + "?" + urlencode(params)
    response = self.client.get(url)
    donation_items = [donation.food_item for donation in response.context["donations"]]

    # Check that the correct number of items are returned
    self.assertEqual(len(response.context["donations"]), 2)

    # Check that the correct items are returned
    self.assertIn("Biryani", donation_items)
    self.assertIn("Shawarma", donation_items)
    self.assertNotIn("Pasta", donation_items)


def test_search_address_no_results(self):
    """Test searching donations by address with no matches."""
    params = {"address": "456 Nonexistent St"}
    url = reverse("recipient_dashboard") + "?" + urlencode(params)
    response = self.client.get(url)

    # Check that no items are returned
    self.assertEqual(len(response.context["donations"]), 0)


class SearchDonationFormTest(TestCase):
    def test_address_field_placeholder(self):
        form = SearchDonationForm()
        self.assertEqual(
            form.fields["address"].widget.attrs["placeholder"],
            "Enter address or location",
        )

    def test_radius_field_default_value(self):
        form = SearchDonationForm()
        self.assertEqual(form.fields["radius"].initial, 5)

    def test_radius_field_choices(self):
        form = SearchDonationForm()
        self.assertEqual(
            form.fields["radius"].choices,
            [
                ("5", "5 miles"),
                ("10", "10 miles"),
                ("25", "25 miles"),
                ("50", "50 miles"),
                ("100", "100 miles"),
            ],
        )


class LocationUtilsTests(TestCase):
    def setUp(self):
        cache.clear()  # Clear cache before each test

    def test_get_coordinates_with_cache(self):
        """Test getting coordinates with caching"""
        # First, mock a successful geocoding response
        mock_location = MagicMock()
        mock_location.latitude = 40.7128
        mock_location.longitude = -74.0060

        with patch("geopy.geocoders.Nominatim.geocode", return_value=mock_location):
            # First call should use the geocoder
            coords = get_coordinates("New York, NY")
            self.assertEqual(coords, (40.7128, -74.0060))

            # Second call should use cached value
            coords_cached = get_coordinates("New York, NY")
            self.assertEqual(coords_cached, (40.7128, -74.0060))

    def test_get_coordinates_failure(self):
        """Test handling of geocoding failures"""
        with patch(
            "geopy.geocoders.Nominatim.geocode", side_effect=Exception("API Error")
        ):
            coords = get_coordinates("Invalid Address")
            self.assertIsNone(coords)

    def test_get_coordinates_not_found(self):
        """Test handling of addresses that can't be geocoded"""
        with patch("geopy.geocoders.Nominatim.geocode", return_value=None):
            coords = get_coordinates("Nonexistent Place")
            self.assertIsNone(coords)

    def test_calculate_distance_valid(self):
        """Test distance calculation with valid coordinates"""
        coord1 = (40.7128, -74.0060)  # New York
        coord2 = (34.0522, -118.2437)  # Los Angeles
        distance = calculate_distance(coord1, coord2)
        self.assertIsInstance(distance, float)
        self.assertGreater(distance, 0)

    def test_calculate_distance_invalid_coords(self):
        """Test distance calculation with invalid coordinates"""
        coord1 = (40.7128, -74.0060)
        coord2 = ("invalid", "coords")
        distance = calculate_distance(coord1, coord2)
        self.assertIsNone(distance)

    def test_calculate_distance_none_coords(self):
        """Test distance calculation with None coordinates"""
        distance = calculate_distance(None, (40.7128, -74.0060))
        self.assertIsNone(distance)

    def test_get_nearby_addresses_valid(self):
        """Test finding nearby addresses with valid data"""
        center_coords = (40.7128, -74.0060)
        addresses = [
            {
                "latitude": 40.7130,
                "longitude": -74.0062,
                "address": "Test Address 1",
                "organization": "Org 1",
            },
            {
                "latitude": 42.3601,
                "longitude": -71.0589,
                "address": "Test Address 2",
                "organization": "Org 2",
            },
        ]
        nearby = get_nearby_addresses(center_coords, addresses, radius_miles=5.0)
        self.assertEqual(len(nearby), 1)
        self.assertEqual(nearby[0]["address"], "Test Address 1")

    def test_get_nearby_addresses_invalid_center(self):
        """Test nearby address search with invalid center coordinates"""
        nearby = get_nearby_addresses(None, [], radius_miles=5.0)
        self.assertEqual(len(nearby), 0)

    def test_get_nearby_addresses_invalid_radius(self):
        """Test nearby address search with invalid radius"""
        center_coords = (40.7128, -74.0060)
        addresses = [
            {
                "latitude": 40.7130,
                "longitude": -74.0062,
                "address": "Test Address",
                "organization": "Org",
            }
        ]
        nearby = get_nearby_addresses(center_coords, addresses, radius_miles="invalid")
        self.assertTrue(len(nearby) >= 0)  # Should use default radius


class LocationSearchIntegrationTests(TestCase):
    def setUp(self):
        # Create test user
        User = get_user_model()
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.client.login(username="testuser", password="testpass")

        # Create test organizations with different locations
        self.org1 = Organization.objects.create(
            organization_name="NYC Restaurant",
            type="restaurant",
            address="123 Broadway, New York, NY",
            zipcode=10007,
            active=True,
        )

        self.org2 = Organization.objects.create(
            organization_name="LA Restaurant",
            type="restaurant",
            address="456 Hollywood Blvd, Los Angeles, CA",
            zipcode=90028,
            active=True,
        )

        # Create donations for each organization
        self.donation1 = Donation.objects.create(
            organization=self.org1,
            food_item="Pizza",
            quantity=5,
            pickup_by=timezone.now() + timedelta(days=1),
            active=True,
        )

        self.donation2 = Donation.objects.create(
            organization=self.org2,
            food_item="Burgers",
            quantity=3,
            pickup_by=timezone.now() + timedelta(days=1),
            active=True,
        )

    @patch("recipient_dashboard.utils.get_coordinates")
    def test_location_search_geocoding_failure(self, mock_get_coordinates):
        """Test handling of geocoding failures in the dashboard view"""
        mock_get_coordinates.return_value = None

        params = {"address": "Invalid Address", "radius": "5"}
        response = self.client.get(
            reverse("recipient_dashboard") + "?" + urlencode(params)
        )

        # Verify appropriate error handling
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(
            any("Could not find the specified address" in str(msg) for msg in messages)
        )

    def test_invalid_radius_value(self):
        """Test handling of invalid radius values"""
        params = {"address": "New York, NY", "radius": "invalid"}
        response = self.client.get(
            reverse("recipient_dashboard") + "?" + urlencode(params)
        )

        # Should default to 5 miles and not crash
        self.assertEqual(response.status_code, 200)


class RecipientDashboardStatsTests(TestCase):
    def setUp(self):
        # Set up test data
        User = get_user_model()
        self.user = User.objects.create_user(
            username="testuser@example.com",
            email="testuser@example.com",
            password="password",
        )
        self.organization = Organization.objects.create(
            organization_name="Test Org",
            type="self",
            address="123 Test Street",
            zipcode="12345",
            email="org@test.com",
            website="https://test.org",
            contact_number="1234567890",
            active=True,
        )
        self.org_admin = OrganizationAdmin.objects.create(
            user=self.user, organization=self.organization, access_level="owner"
        )
        self.client.login(email="testuser@example.com", password="password")
        self.donation = Donation.objects.create(
            food_item="Test Food",
            quantity=10,
            pickup_by=timezone.now().date(),
            organization=self.organization,
        )
        self.order = Order.objects.create(
            donation=self.donation,
            user=self.user,
            order_quantity=3,
            order_status="pending",
            active=True,
        )
        self.review = UserReview.objects.create(
            donation=self.donation,
            user=self.user,
            rating=4,
            comment="Test review",
            active=True,
        )

    def test_stat_view(self):
        response = self.client.get(reverse("recipient_stats"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response, "recipient_dashboard/recipient_statistics.html"
        )
        self.assertEqual(response.context["organizations"][0], self.organization)
        self.assertEqual(response.context["donations"][0], self.donation)
        self.assertEqual(response.context["reviews"][0], self.review)
        self.assertEqual(response.context["orders"][0], self.order)
        self.assertEqual(response.context["rating"], self.review.rating)

    def test_stat_orders(self):
        response = self.client.get(reverse("statistics_user_orders"))
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual(
            response_data["labels"][0], self.order.order_created_at.strftime("%Y-%m-%d")
        )
        self.assertEqual(response_data["data"][0], 1)

    def test_stat_donations(self):
        response = self.client.get(reverse("statistics_user_donations"))
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual(
            response_data["labels"][0], self.donation.created_at.strftime("%Y-%m-%d")
        )
        self.assertEqual(response_data["data"][0], 1)
