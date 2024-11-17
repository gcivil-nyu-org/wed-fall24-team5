from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from database.models import Room, Organization, Message, OrganizationAdmin
from django.contrib.contenttypes.models import ContentType
import json

class MessagingViewTests(TestCase):
    def setUp(self):
        # Create a test client
        self.client = Client()

        # Create two users
        self.user1 = User.objects.create_user(
            username="user1",
            email="user1@test.com",
            password="password1",
            first_name="User",
            last_name="One",
        )
        self.user2 = User.objects.create_user(
            username="user2",
            email="user2@test.com",
            password="password2",
            first_name="User",
            last_name="Two",
        )

        # Create an organization
        self.org1 = Organization.objects.create(
            organization_name="Test Org",
            type="self",
            address="123 Test St",
            zipcode=12345,
        )

        self.org_admin = OrganizationAdmin.objects.create(
            user=self.user1, organization=self.org1, access_level="owner"
        )

        # Create room
        self.room_id_1 = f"{self.user1.id}_{self.org1.organization_id}"
        self.room1 = Room.objects.create(
            room_id=self.room_id_1,
            room_name="Room 1",
            conversor_1_type=ContentType.objects.get_for_model(self.user1),
            conversor_1_id=self.user1.id,
            conversor_1_name="User One",
            conversor_2_type=ContentType.objects.get_for_model(self.org1),
            conversor_2_id=self.org1.organization_id,
            conversor_2_name="Test Org",
        )

        # Create a message in room1
        self.message1 = Message.objects.create(
            room=self.room1,
            sender_user=self.user1,
            message_body="Hello!",
            receiver_user=self.user2,
        )

    def test_messaging_view_authenticated(self):
        self.client.login(username="user1", password="password1")
        response = self.client.get(reverse("messaging:messaging"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "messaging_dashboard.html")
        self.assertIn("rooms", response.context)
        self.assertEqual(len(response.context["rooms"]), 1)

    def test_messaging_view_unauthenticated(self):
        response = self.client.get(reverse("messaging:messaging"))
        self.assertEqual(response.status_code, 302)  # Redirect to login page

    def test_get_messages_view(self):
        self.client.login(username="user1", password="password1")
        response = self.client.get(
            reverse("messaging:get_messages", args=[self.room1.room_id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "messaging_dashboard.html")
        self.assertIn("messages", response.context)
        self.assertEqual(len(response.context["messages"]), 1)
        self.assertEqual(response.context["messages"][0]["message_body"], "Hello!")

    def test_get_messages_invalid_user_view(self):
        self.client.login(username="user2", password="password2")
        response = self.client.get(
            reverse("messaging:get_messages", args=[self.room1.room_id])
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/messaging/")

    def test_start_conversation_new(self):
        self.client.login(username="user1", password="password1")
        data = {
            "sender_id": self.user2.id,
            "receiver_id": self.org1.organization_id,
            "sender_type": "user",
            "receiver_type": "organization",
        }
        response = self.client.post(reverse("messaging:start_conversation"), data)
        self.assertEqual(response.status_code, 302)  # Redirect after creation
        room = Room.objects.filter(
            room_id=f"{self.user2.id}_{self.org1.organization_id}"
        ).first()
        self.assertIsNotNone(room)
        self.assertEqual(room.room_name, "Chat with User and Test Org")

    def test_start_conversation_existing(self):
        self.client.login(username="user1", password="password1")
        data = {
            "sender_id": self.user1.id,
            "receiver_id": self.org1.organization_id,
            "sender_type": "user",
            "receiver_type": "organization",
        }
        response = self.client.post(reverse("messaging:start_conversation"), data)
        self.assertEqual(response.status_code, 302)  # Redirect after checking existence
        messages = list(response.wsgi_request._messages)
        self.assertEqual(
            str(messages[0]), f"Chat already exists with {self.org1.organization_name}"
        )

    def test_org_messaging_view(self):
        self.client.login(username="user1", password="password1")
        response = self.client.get(
            reverse("messaging:org_messaging_view", args=[self.org1.organization_id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "messaging_dashboard.html")
        self.assertIn("rooms", response.context)
        self.assertEqual(len(response.context["rooms"]), 1)

    def test_org_messaging_invalid_user_view(self):
        self.client.login(username="user2", password="password2")
        response = self.client.get(
            reverse("messaging:org_messaging_view", args=[self.org1.organization_id])
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/donor_dashboard/")

    def test_org_get_messages_view(self):
        self.client.login(username="user1", password="password1")
        response = self.client.get(
            reverse(
                "messaging:org_get_messages",
                args=[self.org1.organization_id, self.room_id_1],
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "messaging_dashboard.html")
        self.assertIn("messages", response.context)
        self.assertEqual(len(response.context["messages"]), 1)
        self.assertEqual(response.context["messages"][0]["message_body"], "Hello!")

    def test_org_get_messages_invalid_user_view(self):
        self.client.login(username="user2", password="password2")
        response = self.client.get(
            reverse(
                "messaging:org_get_messages",
                args=[self.org1.organization_id, self.room_id_1],
            )
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/donor_dashboard/")

    def test_get_new_messages(self):
        self.client.login(username="user1", password="password1")
        response = self.client.get(reverse("messaging:get_new_messages", args=[self.room_id_1]))
        self.assertEqual(response.status_code, 200)
        messages = json.loads(response.content)
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0]['message_body'], 'Hello!')

    def test_org_get_new_messages(self):
        self.client.login(username="user1", password="password1")
        response = self.client.get(reverse("messaging:org_get_new_messages", args=[self.org1.organization_id, self.room_id_1]))
        self.assertEqual(response.status_code, 200)
        messages = json.loads(response.content)
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0]['message_body'], 'Hello!')

    def test_send_message(self):
        self.client.login(username="user1", password="password1")
        data = {'message_body': 'New Message from User'}
        response = self.client.post(
            reverse("messaging:send_message", args=[self.room_id_1]),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        self.assertEqual(Message.objects.filter(room_id=self.room_id_1).count(), 2)

    def test_send_message_invalid_request(self):
        self.client.login(username="user1", password="password1")
        response = self.client.get(reverse("messaging:send_message", args=[self.room_id_1]))
        self.assertEqual(response.status_code, 405)
        response_data = json.loads(response.content)
        self.assertFalse(response_data['success'])

    def test_org_send_message(self):
        self.client.login(username="user1", password="password1")
        data = {'message_body': 'New Message from Organization'}
        response = self.client.post(
            reverse("messaging:org_send_message", args=[self.org1.organization_id, self.room_id_1]),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        self.assertEqual(Message.objects.filter(room_id=self.room_id_1).count(), 2)

    def test_org_send_message_invalid_request(self):
        self.client.login(username="user1", password="password1")
        response = self.client.get(reverse("messaging:org_send_message", args=[self.org1.organization_id, self.room_id_1]))
        self.assertEqual(response.status_code, 405)
        response_data = json.loads(response.content)
        self.assertFalse(response_data['success'])