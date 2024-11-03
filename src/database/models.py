from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class Organization(models.Model):
    ORGANIZATION_TYPES = [
        ("restaurant", "Restaurant"),
        ("grocery_store", "Grocery Store"),
        ("food_pantry", "Food Pantry"),
        ("self", "Self"),
        ("other", "Other"),
    ]

    organization_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    organization_name = models.CharField(max_length=255)
    type = models.CharField(max_length=20, choices=ORGANIZATION_TYPES)
    address = models.CharField(max_length=255)
    zipcode = models.IntegerField()
    contact_number = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.organization_name


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    else:
        instance.userprofile.save()


class OrganizationAdmin(models.Model):
    admin_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    access_level = models.CharField(max_length=50)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name() if self.user else 'No User'} - {self.organization.organization_name}"


class Donation(models.Model):
    donation_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    food_item = models.CharField(max_length=255)
    quantity = models.IntegerField()
    pickup_by = models.DateField()
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.food_item} - {self.organization.organization_name}"


class UserReview(models.Model):
    review_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    donation = models.ForeignKey(
        Donation, on_delete=models.CASCADE, null=True, blank=True
    )
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    rating = models.IntegerField()
    comment = models.TextField(blank=True, null=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Review by {self.user.get_full_name() if self.user else 'Anonymous'} for {self.donation.food_item}:\
        {self.donation.organization.organization_name}"


class Room(models.Model):
    room_id = models.CharField(primary_key=True, default=uuid.uuid4, max_length=255)
    room_name = models.CharField(max_length=255, default="Chat Room")

    # Generic foreign key fields for conversors
    conversor_1_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, default=User, related_name='conversor_1')
    conversor_1_id = models.CharField(default=uuid.uuid4)
    conversor_1 = GenericForeignKey('conversor_1_type', 'conversor_1_id')

    conversor_2_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, default=Organization, related_name='conversor_2')
    conversor_2_id = models.CharField(default=uuid.uuid4)
    conversor_2 = GenericForeignKey('conversor_2_type', 'conversor_2_id')

    def __str__(self):
        return self.room_name


# As it currently stands it is users sending eachother messages, which needs to change to users exchanging messages with organizations.
class Message(models.Model):
    message_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, null=True, blank=True)
    sender_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sent_messages",
        null=True,
        blank=True,
    )
    sender_organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="org_sent_messages",
        null=True,
        blank=True,
    )
    receiver_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="received_messages",
        null=True,
        blank=True,
    )
    receiver_organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="org_received_messages",
        null=True,
        blank=True,
    )
    message_body = models.TextField()
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        sender = (
            self.sender_user.get_full_name()
            if self.sender_user
            else (
                self.sender_organization.organization_name
                if self.sender_organization
                else "Unknown"
            )
        )
        receiver = (
            self.receiver_user.get_full_name()
            if self.receiver_user
            else (
                self.receiver_organization.organization_name
                if self.receiver_organization
                else "Unknown"
            )
        )
        return f"Message from {sender} to {receiver}"


class Order(models.Model):
    ORDER_STATUS_CHOICES = [
        ("picked_up", "Picked Up"),
        ("canceled", "Canceled"),
        ("pending", "Pending"),
    ]
    order_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    donation = models.ForeignKey(Donation, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    order_quantity = models.IntegerField()
    order_status = models.CharField(
        max_length=20, choices=ORDER_STATUS_CHOICES, default="pending"
    )
    active = models.BooleanField(default=True)
    order_created_at = models.DateTimeField(auto_now_add=True)
    order_modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.order_id} - {self.user.get_full_name() if self.user else 'No User'}"


class DietaryRestriction(models.Model):
    restriction_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    restriction = models.CharField(max_length=40)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}: {self.restriction}"
