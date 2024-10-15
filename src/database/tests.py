from django.test import TestCase
from .models import Organization

# Create your tests here.


class DummyTestCase(TestCase):
    def test_dummy(self):
        """A dummy test to satisfy flake8."""
        organization = Organization.objects.create(
            organization_name="Test Organization",
            type="restaurant",
            address="123 Test Street",
            zipcode=10001,
        )
        self.assertTrue(organization.organization_name == "Test Organization")
