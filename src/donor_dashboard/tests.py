from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.contrib import messages
from database.models import (
    Organization,
    OrganizationAdmin,
    Donation,
    Order,
    UserReview,
    DietaryRestriction,
)
from donor_dashboard.forms import AddOrganizationForm
from donor_dashboard.views import (
    update_donations,
    cancel_expired_orders,
    get_donations_with_reviews,
)
import json
import base64
from io import BytesIO
from uuid import uuid4
from django.utils.timezone import now
from datetime import timedelta


class DonorDashboardViewsTests(TestCase):
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

        today = now().date()
        # Create test donations
        self.donation1 = Donation.objects.create(
            food_item="Rice",
            quantity=10,
            organization=self.organization,
            pickup_by=today,
            active=True,
        )
        self.donation2 = Donation.objects.create(
            food_item="Pasta",
            quantity=5,
            organization=self.organization,
            pickup_by=today,
            active=True,
        )
        self.donation3 = Donation.objects.create(
            food_item="Bread",
            quantity=15,
            organization=self.organization,
            pickup_by=today - timedelta(days=1),
            active=True,
        )

        # Create test orders
        self.order1 = Order.objects.create(
            donation=self.donation1,
            user=self.user,
            order_quantity=1,
            order_status="pending",
            active=True,
        )
        self.order2 = Order.objects.create(
            donation=self.donation2,
            user=self.user,
            order_quantity=3,
            order_status="pending",
            active=True,
        )
        self.order3 = Order.objects.create(
            donation=self.donation3,
            user=self.user,
            order_quantity=2,
            order_status="pending",
            active=True,
        )

        # Add reviews to one donation
        UserReview.objects.create(
            donation=self.donation1,
            user=self.user,
            rating=4,
            comment="Test review",
            active=True,
        )

        self.client.login(email="testuser@example.com", password="password")

    def test_get_org_list_view(self):
        response = self.client.get(reverse("donor_dashboard:org_list"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "donor_dashboard/list.html")
        self.assertIn("active_org_list", response.context)
        self.assertIn("inactive_org_list", response.context)

    def test_manage_organization_view(self):
        response = self.client.get(
            reverse(
                "donor_dashboard:manage_organization",
                args=[self.organization.organization_id],
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "donor_dashboard/manage_organization.html")
        self.assertEqual(response.context["organization"], self.organization)

    def test_organization_details_view_get(self):
        response = self.client.get(
            reverse(
                "donor_dashboard:organization_details",
                args=[self.organization.organization_id],
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "donor_dashboard/organization_details.html")
        self.assertIsInstance(response.context["form"], AddOrganizationForm)

    def test_update_donations(self):
        update_donations()
        today = now().date()

        # Verify donations with pickup_by >= today are active
        active_donations = Donation.objects.filter(pickup_by__gte=today, active=True)
        self.assertEqual(active_donations.count(), 2)

        # Verify donations with pickup_by < today are inactive
        inactive_donations = Donation.objects.filter(pickup_by__lt=today, active=False)
        self.assertEqual(inactive_donations.count(), 1)

    def test_cancel_expired_orders(self):
        cancel_expired_orders()
        today = now().date()

        # Verify expired orders are canceled and inactive
        expired_orders = Order.objects.filter(
            donation__pickup_by__lt=today, order_status="canceled", active=False
        )
        self.assertEqual(expired_orders.count(), 1)

        # Verify non-expired orders remain pending
        pending_orders = Order.objects.filter(
            donation__pickup_by__gte=today, order_status="pending", active=True
        )
        self.assertEqual(pending_orders.count(), 2)

    def test_get_donations_with_reviews(self):
        donations = get_donations_with_reviews(self.organization.organization_id)

        # Verify only donations with reviews are returned
        self.assertEqual(len(donations), 1)
        self.assertEqual(donations[0].food_item, "Rice")

    def test_organization_details_view_post_valid(self):
        form_data = {
            "organization_name": "Updated Org",
            "type": "self",
            "address": "456 Updated Avenue",
            "zipcode": "54321",
            "email": "updated@test.com",
            "website": "https://updated.org",
            "contact_number": "0987654321",
        }
        response = self.client.post(
            reverse(
                "donor_dashboard:organization_details",
                args=[self.organization.organization_id],
            ),
            form_data,
        )
        self.assertEqual(response.status_code, 302)
        self.organization.refresh_from_db()
        self.assertEqual(self.organization.organization_name, "Updated Org")

    def test_delete_organization_view_post(self):
        response = self.client.post(
            reverse(
                "donor_dashboard:delete_organization",
                args=[self.organization.organization_id],
            )
        )
        self.assertEqual(response.status_code, 302)
        self.organization.refresh_from_db()
        self.assertFalse(self.organization.active)

    def test_view_organization_orders(self):
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
        response = self.client.get(
            reverse(
                "donor_dashboard:manage_organization",
                args=[self.organization.organization_id],
            )
        )
        self.assertEqual(len(response.context["orders"]), 3)
        self.assertIn(self.order, response.context["orders"])

    def test_download_orders(self):
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
        response = self.client.get(
            reverse(
                "donor_dashboard:download_orders",
                args=[self.organization.organization_id],
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/csv")
        current_date = timezone.datetime.now().strftime("%Y%m%d")
        expected_filename = (
            f"{self.organization.organization_id}_orders_{current_date}.csv"
        )

        # Check that the filename is correct
        self.assertIn(
            f'filename="{expected_filename}"', response["Content-Disposition"]
        )

        # Check file contents
        csv_content = response.content.decode("utf-8")
        self.assertIn(
            "Item,Reserved By (Email),Reserved By (Name),Quantity,Pickup Date,Address,Order Status,Order Created On,Order Modified On",
            csv_content,
        )
        self.assertIn(self.donation.food_item, csv_content)
        self.assertIn(self.order.user.username, csv_content)

    def test_view_organization_no_orders(self):
        self.donation1.order_set.filter(order_status="pending").update(
            order_status="picked_up"
        )
        self.donation2.order_set.filter(order_status="pending").update(
            order_status="picked_up"
        )

        response = self.client.get(
            reverse(
                "donor_dashboard:manage_organization",
                args=[self.organization.organization_id],
            )
        )
        num_orders = (
            len(response.context["orders"])
            if response and response.context["orders"]
            else 0
        )
        self.assertEqual(num_orders, 0)


class DonationTests(TestCase):
    def setUp(self):
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

        self.org_admin = OrganizationAdmin.objects.create(
            user=self.user, organization=self.organization, access_level="owner"
        )

        # Create a donation
        self.donation = Donation.objects.create(
            food_item="Test Food",
            quantity=10,
            pickup_by=timezone.now().date(),
            organization=self.organization,
        )

    def test_add_donation_successful_post_request(self):
        """Test successful addition of a new donation via a valid POST request."""
        response = self.client.post(
            reverse("donor_dashboard:add_donation"),
            {
                "food_item": "Hyderabadi Biryani",
                "quantity": 5,
                "pickup_by": timezone.now().date(),
                "organization": str(self.organization.organization_id),
            },
        )

        self.assertEqual(response.status_code, 302)
        messages_list = list(messages.get_messages(response.wsgi_request))
        self.assertIn(
            "Donation: Hyderabadi Biryani added successfully!",
            [msg.message for msg in messages_list],
        )
        self.assertTrue(
            Donation.objects.filter(food_item="Hyderabadi Biryani").exists()
        )
        self.assertRedirects(
            response,
            reverse(
                "donor_dashboard:manage_organization",
                args=[self.organization.organization_id],
            ),
        )

    def test_add_donation_unsuccessful_get_request(self):
        """Test that a GET request doesn't add a donation and returns an error message."""
        response = self.client.get(
            reverse("donor_dashboard:add_donation"),
            {
                "food_item": "Pizza",
                "quantity": 5,
                "pickup_by": timezone.now().date(),
                "organization": str(self.organization.organization_id),
            },
        )

        # Check if an error message is displayed
        messages_list = list(messages.get_messages(response.wsgi_request))
        self.assertIn(
            "Invalid Add Donation Request!", [msg.message for msg in messages_list]
        )

    def test_add_donation_missing_fields(self):
        """Test unsuccessful addition of a donation when required fields are missing in the POST request."""
        response = self.client.post(
            reverse("donor_dashboard:add_donation"),
            {
                "food_item": "",  # empty value
                "quantity": 5,
                "pickup_by": timezone.now().date(),
                "organization": str(self.organization.organization_id),
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertFalse(Donation.objects.filter(food_item="").exists())
        self.assertRedirects(
            response,
            reverse(
                "donor_dashboard:manage_organization",
                args=[self.organization.organization_id],
            ),
        )

    def test_add_donation_invalid_quantity(self):
        """Test unsuccessful addition of a donation with an invalid (negative) quantity."""
        response = self.client.post(
            reverse("donor_dashboard:add_donation"),
            {
                "food_item": "Italian Pasta",
                "quantity": -5,  # negative value
                "pickup_by": timezone.now().date(),
                "organization": str(self.organization.organization_id),
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertFalse(Donation.objects.filter(food_item="").exists())
        self.assertRedirects(
            response,
            reverse(
                "donor_dashboard:manage_organization",
                args=[self.organization.organization_id],
            ),
        )

    def test_add_donation_invalid_date(self):
        """Test unsuccessful addition of a donation with a pickup date beyond the allowed range."""
        response = self.client.post(
            reverse("donor_dashboard:add_donation"),
            {
                "food_item": "Italian Pasta",
                "quantity": 5,
                "pickup_by": (timezone.now() + timezone.timedelta(days=8)).strftime(
                    "%Y-%m-%d"
                ),  # date after 7 day period
                "organization": str(self.organization.organization_id),
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertFalse(Donation.objects.filter(food_item="").exists())
        self.assertRedirects(
            response,
            reverse(
                "donor_dashboard:manage_organization",
                args=[self.organization.organization_id],
            ),
        )

    def test_modify_donation_successful_post(self):
        """Test successful modification of a donation via a valid POST request."""
        response = self.client.post(
            reverse(
                "donor_dashboard:modify_donation", args=[str(self.donation.donation_id)]
            ),
            {
                "food_item": "Updated Test Food",
                "quantity": 15,
                "pickup_by": timezone.now().date(),
                "organization": str(self.organization.organization_id),
            },
        )

        self.assertEqual(response.status_code, 302)
        updated_donation = Donation.objects.get(donation_id=self.donation.donation_id)
        self.assertEqual(updated_donation.food_item, "Updated Test Food")
        self.assertEqual(updated_donation.quantity, 15)
        self.assertRedirects(
            response,
            reverse(
                "donor_dashboard:manage_organization",
                args=[self.organization.organization_id],
            ),
        )

    def test_modify_donation_missing_fields(self):
        """Test unsuccessful donation modification when required fields are missing."""
        response = self.client.post(
            reverse(
                "donor_dashboard:modify_donation", args=[str(self.donation.donation_id)]
            ),
            {
                "food_item": "",
                "quantity": 15,
                "pickup_by": timezone.now().date(),
                "organization": str(self.organization.organization_id),
            },
        )

        self.assertEqual(response.status_code, 302)
        updated_donation = Donation.objects.get(donation_id=self.donation.donation_id)
        self.assertEqual(updated_donation.food_item, "Test Food")
        self.assertEqual(updated_donation.quantity, 10)
        self.assertRedirects(
            response,
            reverse(
                "donor_dashboard:manage_organization",
                args=[self.organization.organization_id],
            ),
        )

    def test_modify_donation_invalid_quantity(self):
        """Test unsuccessful modification of a donation with an invalid (negative) quantity."""
        response = self.client.post(
            reverse(
                "donor_dashboard:modify_donation", args=[str(self.donation.donation_id)]
            ),
            {
                "food_item": "Updated Test Food",
                "quantity": -15,
                "pickup_by": timezone.now().date(),
                "organization": str(self.organization.organization_id),
            },
        )

        self.assertEqual(response.status_code, 302)
        updated_donation = Donation.objects.get(donation_id=self.donation.donation_id)
        self.assertEqual(updated_donation.food_item, "Test Food")
        self.assertEqual(updated_donation.quantity, 10)
        self.assertRedirects(
            response,
            reverse(
                "donor_dashboard:manage_organization",
                args=[self.organization.organization_id],
            ),
        )

    def test_modify_donation_invalid_date(self):
        """Test unsuccessful modification of a donation with a pickup date beyond the allowed range."""
        response = self.client.post(
            reverse(
                "donor_dashboard:modify_donation", args=[str(self.donation.donation_id)]
            ),
            {
                "food_item": "Random Test Food",
                "quantity": 15,
                "pickup_by": (timezone.now() + timezone.timedelta(days=8)).strftime(
                    "%Y-%m-%d"
                ),  # date after 7 day period
                "organization": str(self.organization.organization_id),
            },
        )

        self.assertEqual(response.status_code, 302)
        updated_donation = Donation.objects.get(donation_id=self.donation.donation_id)
        self.assertEqual(updated_donation.food_item, "Test Food")
        self.assertEqual(updated_donation.quantity, 10)
        self.assertRedirects(
            response,
            reverse(
                "donor_dashboard:manage_organization",
                args=[self.organization.organization_id],
            ),
        )

    def test_delete_donation_successful_post(self):
        """Test that the donation is soft deleted with a POST request"""
        response = self.client.post(
            reverse(
                "donor_dashboard:delete_donation", args=[str(self.donation.donation_id)]
            )
        )
        self.donation.refresh_from_db()
        self.assertFalse(self.donation.active)

        # Check if a success message is displayed
        messages_list = list(messages.get_messages(response.wsgi_request))
        self.assertIn(
            "Donation 'Test Food' has been deleted successfully!",
            [msg.message for msg in messages_list],
        )

        # Check redirection after deletion
        self.assertRedirects(
            response,
            reverse(
                "donor_dashboard:manage_organization",
                args=[str(self.organization.organization_id)],
            ),
        )

    def test_delete_donation_unsuccessful_get_request(self):
        """Test that a GET request doesn't delete the donation and shows an error"""
        response = self.client.get(
            reverse(
                "donor_dashboard:delete_donation", args=[str(self.donation.donation_id)]
            )
        )
        self.donation.refresh_from_db()

        # Ensure that the donation is still active (was not deleted)
        self.assertTrue(self.donation.active)

        # Check if an error message is displayed
        messages_list = list(messages.get_messages(response.wsgi_request))
        self.assertIn(
            "Invalid Delete Donation Request!", [msg.message for msg in messages_list]
        )

        # Check redirection after failed deletion attempt
        self.assertRedirects(
            response,
            reverse(
                "donor_dashboard:manage_organization",
                args=[str(self.organization.organization_id)],
            ),
        )

    def test_delete_donation_nonexistent_donation(self):
        """Test that trying to delete a nonexistent donation results in a 404 error"""
        # URL with a non-existent donation ID
        fake_donation_id = "12345678-1234-5678-1234-567812345678"
        response = self.client.post(
            reverse("donor_dashboard:delete_donation", args=[str(fake_donation_id)])
        )

        # Check if the response status code is 404 (Not Found)
        self.assertEqual(response.status_code, 404)


class OrganizationAdminViewsTestCase(TestCase):
    def setUp(self):
        # Set up users, organization, and admin roles
        User = get_user_model()
        self.owner = User.objects.create_user(
            username="owner@example.com", email="owner@example.com", password="password"
        )
        self.admin = User.objects.create_user(
            username="admin@example.com", email="admin@example.com", password="password"
        )
        self.new_admin = User.objects.create_user(
            username="new_admin@example.com",
            email="new_admin@example.com",
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

        # Owner setup
        OrganizationAdmin.objects.create(
            user=self.owner, organization=self.organization, access_level="owner"
        )
        # Admin setup
        OrganizationAdmin.objects.create(
            user=self.admin, organization=self.organization, access_level="admin"
        )
        # Log in as owner for tests
        self.client.login(email="owner@example.com", password="password")

    def test_add_org_admin_as_owner(self):
        # Simulate adding a new admin
        response = self.client.post(
            reverse("donor_dashboard:add_org_admin"),
            {
                "organization_id": self.organization.organization_id,
                "email": self.new_admin.email,
            },
        )
        self.assertRedirects(
            response,
            reverse(
                "donor_dashboard:organization_details",
                args=[self.organization.organization_id],
            ),
        )

        # Check if new admin was added
        self.assertTrue(
            OrganizationAdmin.objects.filter(
                user=self.new_admin, organization=self.organization
            ).exists()
        )

        # Check success message
        messages_list = list(messages.get_messages(response.wsgi_request))
        self.assertEqual(str(messages_list[0]), "Admin successfully added.")

    def test_add_org_admin_already_exists(self):
        # Try to add an admin who is already an admin
        response = self.client.post(
            reverse("donor_dashboard:add_org_admin"),
            {
                "organization_id": self.organization.organization_id,
                "email": self.admin.email,
            },
        )
        self.assertRedirects(
            response,
            reverse(
                "donor_dashboard:organization_details",
                args=[self.organization.organization_id],
            ),
        )

        # Check message for existing admin
        messages_list = list(messages.get_messages(response.wsgi_request))
        self.assertEqual(str(messages_list[0]), "Admin already associated")

    def test_add_org_admin_no_permission(self):
        # Login as a non-owner
        self.client.login(email="admin@example.com", password="password")

        response = self.client.post(
            reverse("donor_dashboard:add_org_admin"),
            {
                "organization_id": self.organization.organization_id,
                "email": self.new_admin.email,
            },
        )
        self.assertRedirects(
            response,
            reverse(
                "donor_dashboard:manage_organization",
                args=[self.organization.organization_id],
            ),
        )

        # Check permission warning
        messages_list = list(messages.get_messages(response.wsgi_request))
        self.assertEqual(
            str(messages_list[0]), "You Don't have permission to do this action"
        )

    def test_assign_organization_access_level(self):
        # Owner changes an admin's access level
        response = self.client.post(
            reverse(
                "donor_dashboard:assign_organization_access_level",
                args=[self.organization.organization_id, self.admin.email, "admin"],
            )
        )
        self.assertRedirects(
            response,
            reverse(
                "donor_dashboard:organization_details",
                args=[self.organization.organization_id],
            ),
        )

        # Verify the access level was updated
        org_admin = OrganizationAdmin.objects.get(
            user=self.admin, organization=self.organization
        )
        self.assertEqual(org_admin.access_level, "owner")

    def test_remove_admin_owner(self):
        # Remove admin
        response = self.client.post(
            reverse(
                "donor_dashboard:remove_admin_owner",
                args=[self.organization.organization_id, self.admin.email],
            )
        )
        self.assertRedirects(
            response,
            reverse(
                "donor_dashboard:organization_details",
                args=[self.organization.organization_id],
            ),
        )

        # Ensure the admin was removed
        self.assertFalse(
            OrganizationAdmin.objects.filter(
                user=self.admin, organization=self.organization
            ).exists()
        )

        # Check success message
        messages_list = list(messages.get_messages(response.wsgi_request))
        self.assertEqual(
            str(messages_list[0]),
            "Succesfully remove this org access to email: admin@example.com",
        )

    def test_check_user(self):
        data = json.dumps({"email": self.new_admin.email})
        response = self.client.post(
            reverse("donor_dashboard:check_user"), data, content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)

        # Check that admin email exists in user
        response_data = response.json()
        self.assertEqual(response_data["exists"], True)

    def test_check_user_does_not_exist(self):
        data = json.dumps({"email": "noadmin@example.com"})
        response = self.client.post(
            reverse("donor_dashboard:check_user"), data, content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)

        # Check that admin email exists in user
        response_data = response.json()
        self.assertEqual(response_data["exists"], False)


class DonorDashboardStatsTests(TestCase):
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
        response = self.client.get(
            reverse(
                "donor_dashboard:organization_statistics",
                args=[self.organization.organization_id],
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "donor_dashboard/statistics.html")
        self.assertEqual(response.context["organization"], self.organization)
        self.assertEqual(len(response.context["reviews"]), 1)
        self.assertEqual(response.context["num_users"], 1)
        self.assertEqual(len(response.context["activity_feed"]), 2)

    def test_stat_orders(self):
        response = self.client.get(
            reverse(
                "donor_dashboard:statistics_orders",
                args=[self.organization.organization_id],
            )
        )
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual(
            response_data["labels"][0], self.order.order_created_at.strftime("%b %d")
        )
        self.assertEqual(response_data["data"][0], 1)

    def test_stat_orders_status(self):
        response = self.client.get(
            reverse(
                "donor_dashboard:statistics_orders_status",
                args=[self.organization.organization_id],
            )
        )
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        labels = ["Picked Up", "Pending", "Canceled"]
        self.assertEqual(response_data["labels"], labels)
        self.assertEqual(response_data["data"][1], 1)

    def test_stat_donations(self):
        response = self.client.get(
            reverse(
                "donor_dashboard:statistics_donations",
                args=[self.organization.organization_id],
            )
        )
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual(
            response_data["labels"][0], self.donation.created_at.strftime("%b %d")
        )
        self.assertEqual(response_data["data"][0], 1)

    def test_stat_ratings(self):
        response = self.client.get(
            reverse(
                "donor_dashboard:statistics_ratings",
                args=[self.organization.organization_id],
            )
        )
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        labels = [1, 2, 3, 4, 5]
        self.assertEqual(response_data["labels"], labels)
        self.assertEqual(response_data["data"][3], 1)


class DietaryRestrictionTests(TestCase):
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
            order_quantity=2,
            order_status="pending",
            active=True,
        )
        DietaryRestriction.objects.create(user=self.user, restriction="gluten_free")
        DietaryRestriction.objects.create(user=self.user, restriction="nut_free")

        # Login for access to views
        self.client.login(email="testuser@example.com", password="password")

    def test_access_dietary_restrictions(self):
        response = self.client.get(
            reverse(
                "donor_dashboard:manage_organization",
                args=[self.organization.organization_id],
            )
        )

        # Check if the view is accessible
        self.assertEqual(response.status_code, 200)

        # Check dietary restrictions in the context
        orders = response.context["orders"]
        self.assertEqual(len(orders), 1)
        dietary_restrictions = orders[0].user.dietary_restrictions

        # Verify dietary restrictions are correctly formatted
        formatted_restrictions = [
            restriction.restriction for restriction in dietary_restrictions
        ]
        self.assertIn("Gluten Free", formatted_restrictions)
        self.assertIn("Nut Free", formatted_restrictions)


class AddOrganizationFormErrorsTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username="testuser@example.com",
            email="testuser@example.com",
            password="password",
        )
        self.client.login(email="testuser@example.com", password="password")

    def test_add_organization_view_post_valid(self):
        form_data = {
            "organization_name": "New Org",
            "type": "self",
            "address": "456 Test Avenue",
            "zipcode": "54321",
            "email": "neworg@test.com",
            "website": "https://new.org",
            "contact_number": "1234567890",
        }
        response = self.client.post(reverse("donor_dashboard:org_list"), form_data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Organization.objects.filter(organization_name="New Org").exists()
        )

    def test_add_organization_missing_required_field(self):
        """Test missing required field generates the correct error message."""
        form_data = {
            "organization_name": "",
            "type": "self",
            "address": "123 Test Street",
            "zipcode": "12345",
            "contact_number": "1234567890",
            "email": "org@test.com",
            "website": "https://test.org",
        }
        response = self.client.post(reverse("donor_dashboard:org_list"), form_data)
        self.assertEqual(response.status_code, 302)

        # Check error message
        messages_list = list(messages.get_messages(response.wsgi_request))
        self.assertIn(
            "Organization Name is invalid. Please try again.",
            [msg.message for msg in messages_list],
        )

    def test_add_organization_invalid_zipcode(self):
        """Test invalid zipcode generates the correct error message."""
        form_data = {
            "organization_name": "Test Org",
            "type": "self",
            "address": "123 Test Street",
            "zipcode": "1234",  # Invalid: Less than 5 digits
            "contact_number": "1234567890",
            "email": "org@test.com",
            "website": "https://test.org",
        }
        response = self.client.post(reverse("donor_dashboard:org_list"), form_data)
        self.assertEqual(response.status_code, 302)

        # Check error message
        messages_list = list(messages.get_messages(response.wsgi_request))
        self.assertIn(
            "Zipcode is not valid. Please try again.",
            [msg.message for msg in messages_list],
        )

    def test_add_organization_duplicate(self):
        """Test duplicate organization generates the correct error message."""
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
        form_data = {
            "organization_name": "Test Org",
            "type": "self",
            "address": "123 Test Street",
            "zipcode": "12345",
            "contact_number": "1234567890",
            "email": "org@test.com",
            "website": "https://test.org",
        }
        response = self.client.post(reverse("donor_dashboard:org_list"), form_data)
        self.assertEqual(response.status_code, 302)

        # Check error message
        messages_list = list(messages.get_messages(response.wsgi_request))
        self.assertIn(
            "An organization with the same details already exists. Please modify at least one field and try again.",
            [msg.message for msg in messages_list],
        )


class UploadDonationImageTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username="testuser@example.com",
            email="testuser@example.com",
            password="password",
        )
        self.client.login(email="testuser@example.com", password="password")
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
        self.donation = Donation.objects.create(
            food_item="Test Food",
            quantity=10,
            pickup_by=timezone.now().date(),
            organization=self.organization,
        )
        self.url = "/donor_dashboard/upload-donation-image/"  # Update with the actual URL for this view

    def create_image_file(self, content=b"image content", name="test.png"):
        """Helper method to create an in-memory image file."""
        image_file = BytesIO(content)
        image_file.name = name
        return image_file

    def test_successful_image_upload(self):
        image_file = self.create_image_file()
        response = self.client.post(
            self.url,
            {
                "donation_id": self.donation.donation_id,
                "image": image_file,
            },
        )
        self.donation.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {"success": True, "image_data": self.donation.image_data},
        )
        self.assertIsNotNone(self.donation.image_data)
        self.assertEqual(
            base64.b64decode(self.donation.image_data).decode("utf-8"), "image content"
        )

    def test_missing_donation_id(self):
        image_file = self.create_image_file()
        response = self.client.post(self.url, {"image": image_file})

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {"success": False, "error": "Invalid data."},
        )

    def test_missing_image(self):
        response = self.client.post(
            self.url, {"donation_id": self.donation.donation_id}
        )

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {"success": False, "error": "Invalid data."},
        )

    def test_invalid_donation_id(self):
        image_file = self.create_image_file()
        invalid_donation_id = uuid4()
        response = self.client.post(
            self.url,
            {
                "donation_id": invalid_donation_id,
                "image": image_file,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {"success": False, "error": "Donation not found."},
        )

    def test_invalid_request_method(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {"success": False, "error": "Invalid request method."},
        )

    def test_unauthenticated_user(self):
        self.client.logout()
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, 302)  # Redirects to login page


class DeleteDonationImageTests(TestCase):
    def setUp(self):
        # Create a user and log in
        User = get_user_model()
        self.user = User.objects.create_user(
            username="testuser@example.com",
            email="testuser@example.com",
            password="password",
        )
        self.client.login(email="testuser@example.com", password="password")
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
        self.donation = Donation.objects.create(
            food_item="Test Food",
            quantity=10,
            pickup_by=timezone.now().date(),
            organization=self.organization,
        )

        self.url = "/donor_dashboard/delete-donation-image/"

    def test_successful_image_deletion(self):
        response = self.client.post(
            self.url, {"donation_id": self.donation.donation_id}
        )
        self.donation.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"success": True})
        self.assertIsNone(self.donation.image_data)

    def test_missing_donation_id(self):
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content, {"success": False, "error": "Invalid data."}
        )

    def test_nonexistent_donation(self):
        invalid_donation_id = uuid4()
        response = self.client.post(self.url, {"donation_id": invalid_donation_id})
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content, {"success": False, "error": "Donation not found."}
        )

    def test_invalid_request_method(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content, {"success": False, "error": "Invalid request method."}
        )

    def test_unauthenticated_access(self):
        self.client.logout()  # Log out the authenticated user
        response = self.client.post(
            self.url, {"donation_id": self.donation.donation_id}
        )
        self.assertEqual(response.status_code, 302)  # Redirect to login page
        self.assertTrue(
            response.url.startswith("/accounts/login/")
        )  # Adjust the login URL if different
