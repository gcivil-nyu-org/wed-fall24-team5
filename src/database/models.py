from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid


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
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
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
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    rating = models.IntegerField()
    comment = models.TextField(blank=True, null=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Review by {self.user.get_full_name() if self.user else 'Anonymous'} for {self.organization.organization_name}"


# As it currently stands it is users sending eachother messages, which needs to change to users exchanging messages with organizations.
class Message(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
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
                self.sender_organization.organization_name if self.sender_organization else "Unknown"
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

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
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
        return (
            f"Order {self.id} - {self.user.get_full_name() if self.user else 'No User'}"
        )
