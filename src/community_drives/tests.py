from django.test import TestCase  # noqa
from django.contrib.auth import get_user_model
from database.models import Organization, CommunityDrive, DriveOrganization
import base64
from io import BytesIO
from uuid import uuid4
from django.urls import reverse


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
