from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from database.models import (
    CommunityDrive,
    Organization,
    OrganizationAdmin,
    DriveOrganization,
)
from django.utils import timezone
from datetime import timedelta
from django.contrib import messages
from django.utils.html import strip_tags
import base64
from io import BytesIO
from uuid import uuid4


# Create your tests here.
class CommunityDriveViewTests(TestCase):
    def setUp(self):
        # Set up a test user
        User = get_user_model()
        self.user = User.objects.create_user(
            username="testuser@example.com",
            email="testuser@example.com",
            password="password",
        )
        self.client.login(email="testuser@example.com", password="password")

        # Set up a test organization
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
        self.assertTrue(CommunityDrive.objects.filter(name="New Drive").exists())
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
        self.assertIn(
            "Target numbers must be positive integers.",
            [strip_tags(msg.message) for msg in messages_list],
        )


class DriveImageTests(TestCase):
    def setUp(self):
        # Set up test data
        User = get_user_model()
        self.user = User.objects.create_user(username="testuser", password="testpass")

        # Logging in the user
        self.client.login(username="testuser", password="testpass")

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

        # Set up a test community drive
        self.drive = CommunityDrive.objects.create(
            name="Test Drive",
            description="A test community drive.",
            lead_organization=self.organization,
            meal_target=100,
            volunteer_target=50,
            start_date="2024-01-01",
            end_date="2024-12-31",
            active=True,
        )
        self.upload_image_url = "/community_drives/upload-drive-image/"
        self.delete_image_url = "/community_drives/delete-drive-image/"

    def create_image_file(self, content=b"image content", name="test.png"):
        """Helper method to create an in-memory image file."""
        image_file = BytesIO(content)
        image_file.name = name
        return image_file

    def test_upload_drive_image_success(self):
        image_file = self.create_image_file()

        response = self.client.post(
            self.upload_image_url,
            {"drive_id": self.drive.drive_id, "image": image_file},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["success"], True)

        # Verify the image was saved as base64
        self.drive.refresh_from_db()
        self.assertEqual(
            base64.b64decode(self.drive.image_data).decode("utf-8"), "image content"
        )

    def test_upload_drive_image_invalid_data(self):
        response = self.client.post(
            self.upload_image_url, {"drive_id": "", "image": ""}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["success"], False)
        self.assertEqual(response.json()["error"], "Invalid data.")

    def test_upload_drive_image_nonexistent_drive(self):
        image_file = self.create_image_file()
        invalid_drive_id = uuid4()

        response = self.client.post(
            self.upload_image_url,
            {"drive_id": invalid_drive_id, "image": image_file},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["success"], False)
        self.assertEqual(response.json()["error"], "Community Drive not found.")

    def test_upload_drive_image_invalid_request_method(self):
        response = self.client.get(self.upload_image_url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["success"], False)
        self.assertEqual(response.json()["error"], "Invalid request method.")

    def test_delete_drive_image_success(self):
        self.drive.image_data = "test_data"
        self.drive.save()

        response = self.client.post(
            self.delete_image_url, {"drive_id": self.drive.drive_id}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["success"], True)

        # Verify the image data was deleted
        self.drive.refresh_from_db()
        self.assertIsNone(self.drive.image_data)

    def test_delete_drive_image_invalid_data(self):
        response = self.client.post(self.delete_image_url, {"drive_id": ""})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["success"], False)
        self.assertEqual(response.json()["error"], "Invalid data.")

    def test_delete_drive_image_nonexistent_drive(self):
        invalid_drive_id = uuid4()
        response = self.client.post(
            self.delete_image_url, {"drive_id": invalid_drive_id}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["success"], False)
        self.assertEqual(response.json()["error"], "Community Drive not found.")

    def test_delete_drive_image_invalid_request_method(self):
        response = self.client.get(self.delete_image_url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["success"], False)
        self.assertEqual(response.json()["error"], "Invalid request method.")

    def test_get_participation_details_success(self):
        # Create a DriveOrganization record
        DriveOrganization.objects.create(
            organization=self.organization,
            drive=self.drive,
            meal_pledge=10,
            volunteer_pledge=5,
        )

        url = reverse(
            "community_drives:participation-details",
            kwargs={
                "organization_id": self.organization.organization_id,
                "drive_id": self.drive.drive_id,
            },
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"meals": 10, "volunteers": 5})

    def test_get_participation_details_nonexistent(self):
        url = reverse(
            "community_drives:participation-details",
            kwargs={
                "organization_id": self.organization.organization_id,
                "drive_id": uuid4(),
            },
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

    def test_delete_participation_success(self):
        # Create a DriveOrganization record
        drive_org = DriveOrganization.objects.create(
            organization=self.organization,
            drive=self.drive,
            meal_pledge=10,
            volunteer_pledge=5,
        )

        url = reverse(
            "community_drives:delete-participation",
            kwargs={
                "organization_id": self.organization.organization_id,
                "drive_id": self.drive.drive_id,
            },
        )
        response = self.client.delete(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["success"], True)

        # Verify the record was deleted
        with self.assertRaises(DriveOrganization.DoesNotExist):
            DriveOrganization.objects.get(pk=drive_org.pk)

    def test_delete_participation_nonexistent(self):
        url = reverse(
            "community_drives:delete-participation",
            kwargs={
                "organization_id": self.organization.organization_id,
                "drive_id": uuid4(),
            },
        )
        response = self.client.delete(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["success"], False)
        self.assertEqual(response.json()["error"], "Participation not found")

    def test_delete_participation_invalid_method(self):
        url = reverse(
            "community_drives:delete-participation",
            kwargs={
                "organization_id": self.organization.organization_id,
                "drive_id": self.drive.drive_id,
            },
        )
        response = self.client.post(url)  # Invalid method

        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.json()["success"], False)
        self.assertEqual(response.json()["error"], "Invalid request method")

    def test_delete_drive_success(self):
        url = reverse(
            "community_drives:delete_drive", kwargs={"drive_id": self.drive.drive_id}
        )

        response = self.client.post(url)

        self.assertEqual(response.status_code, 302)  # Expect redirect after success
        self.drive.refresh_from_db()
        self.assertFalse(self.drive.active)  # Ensure the drive is deactivated
        drive_orgs = DriveOrganization.objects.filter(drive=self.drive)
        for drive_org in drive_orgs:
            self.assertEqual(drive_org.meal_pledge, 0)
            self.assertEqual(drive_org.volunteer_pledge, 0)

    def test_delete_drive_nonexistent(self):
        invalid_drive_id = uuid4()
        url = reverse(
            "community_drives:delete_drive", kwargs={"drive_id": invalid_drive_id}
        )

        response = self.client.post(url)

        self.assertEqual(
            response.status_code, 302
        )  # Expect redirect even if deletion fails
        messages = list(response.wsgi_request._messages)
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            "Failed to delete community drive. Couldn't find the drive.",
        )
