from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.contrib import messages
from database.models import Organization, OrganizationAdmin, Donation
from donor_dashboard.forms import AddOrganizationForm


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
            user=self.user, organization=self.organization
        )
        self.client.login(email="testuser@example.com", password="password")

    def test_add_organization_view_get(self):
        response = self.client.get(reverse("donor_dashboard:add_organization"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "add_organization.html")
        self.assertIsInstance(response.context["form"], AddOrganizationForm)

    def test_add_organization_view_post_valid(self):
        form_data = {
            "organization_name": "New Org",
            "type": "self",
            "address": "456 Test Avenue",
            "zipcode": "54321",
            "email": "neworg@test.com",
            "website": "https://new.org",
            "contact_number": "0987654321",
        }
        response = self.client.post(
            reverse("donor_dashboard:add_organization"), form_data
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Organization.objects.filter(organization_name="New Org").exists()
        )

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


class DonationTests(TestCase):
    def setUp(self):
        User = get_user_model()
        # Create test user and log them in
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.client.login(username="testuser", password="testpassword")

        # Create test organization
        self.organization = Organization.objects.create(
            organization_name="Test Organization",
            type="restaurant",
            address="123 Test St",
            zipcode=12345,
        )

        # Create a donation
        self.donation = Donation.objects.create(
            food_item="Test Food",
            quantity=10,
            pickup_by=timezone.now().date(),
            organization=self.organization,
        )

    def test_add_donation_success(self):
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
