from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from database.models import Organization, OrganizationAdmin
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
