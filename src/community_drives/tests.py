from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from database.models import CommunityDrive, Organization, OrganizationAdmin
from django.utils import timezone
from datetime import timedelta
from django.contrib import messages


class CommunityDrivesViewsTests(TestCase):
    def setUp(self):
        # Set up test data
        User = get_user_model()
        self.user = User.objects.create_user(username="testuser", password="testpass")

        # Logging in the user
        self.client.login(username="testuser", password="testpass")

        self.organization1 = Organization.objects.create(
            organization_name="Test Org",
            type="self",
            address="123 Test Street",
            zipcode="12345",
            email="org@test.com",
            website="https://test.org",
            contact_number="1234567890",
            active=True,
        )

        self.organization2 = Organization.objects.create(
            organization_name="Test Org 2",
            type="restaurant",
            address="123 Test Street",
            zipcode="12345",
            email="org@test.com",
            website="https://test.org",
            contact_number="1234567890",
            active=True,
        )

        self.org_admin = OrganizationAdmin.objects.create(
            user=self.user, organization=self.organization1, access_level="owner"
        )

        self.drive1 = CommunityDrive.objects.create(
            name="Test Drive",
            description="Test drive description",
            lead_organization=self.organization1,
            meal_target=500,
            volunteer_target=10,
            start_date=timezone.now().date(),
            end_date=timezone.now() + timedelta(days=7),
            active=True,
        )

        self.drive2 = CommunityDrive.objects.create(
            name="Test Drive 2",
            description="Test drive description",
            lead_organization=self.organization2,
            meal_target=500,
            volunteer_target=10,
            start_date=timezone.now().date(),
            end_date=timezone.now() + timedelta(days=7),
            active=True,
        )

    def test_community_drives_view_all(self):
        response = self.client.get(reverse("community_drives:drive_list"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "community_drives/list.html")
        self.assertIn("drives", response.context)
        self.assertIn("my_drives", response.context)
        self.assertEqual(
            len(response.context["drives"]), 2
        )  # Should include 2 active community drives
        self.assertEqual(
            len(response.context["my_drives"]), 1
        )  # Should include 1 active community drive


class AddCommunityDriveTests(TestCase):
    def setUp(self):
        # Set up test data
        User = get_user_model()
        self.user = User.objects.create_user(username="testuser", password="testpass")

        # Logging in the user
        self.client.login(username="testuser", password="testpass")

        today = timezone.now().date()

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

        self.drive = CommunityDrive.objects.create(
            name="Test Drive",
            description="Test drive description",
            lead_organization=self.organization,
            meal_target=500,
            volunteer_target=10,
            start_date=today,
            end_date=today + timedelta(days=7),
            active=True,
        )

    def test_add_valid_drive(self):
        form_data = {
            "name": "New Drive",
            "description": "New drive description",
            "lead_organization": str(self.organization.organization_id),
            "meal_target": 100,
            "volunteer_target": 15,
            "start_date": timezone.now().date() + timedelta(days=1),
            "end_date": timezone.now().date() + timedelta(days=10),
        }
        response = self.client.post(reverse("community_drives:drive_list"), form_data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            CommunityDrive.objects.filter(name="New Drive").exists()
        )
        messages_list = list(messages.get_messages(response.wsgi_request))
        self.assertIn(
            "Community drive successfully created.",
            [msg.message for msg in messages_list],
        )

    def test_add_drive_missing_fields(self):
        form_data = {
            "name": "Test Drive",
            "description": "New drive description",
            "lead_organization": str(self.organization.organization_id),
            "meal_target": -5,
            "volunteer_target": 15,
            "start_date": timezone.now().date() + timedelta(days=1),
            "end_date": timezone.now().date() + timedelta(days=10),
        }
        response = self.client.post(reverse("community_drives:drive_list"), form_data)
        self.assertEqual(response.status_code, 302)
        messages_list = list(messages.get_messages(response.wsgi_request))
        self.assertTrue(any(str(message) == "Target numbers must be positive integers." for message in messages_list))
