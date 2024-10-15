from django.db import models
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


class User(models.Model):
    user_email = models.EmailField(primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class OrganizationAdmin(models.Model):
    admin_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization_id = models.ForeignKey(
        Organization, on_delete=models.CASCADE, to_field="organization_id"
    )
    user_email = models.ForeignKey(
        User, on_delete=models.CASCADE, to_field="user_email"
    )
    access_level = models.CharField(max_length=50)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - {self.organization.organization_name}"


class Donation(models.Model):
    donation_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization_id = models.ForeignKey(
        Organization, on_delete=models.CASCADE, to_field="organization_id"
    )
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
    organization_id = models.ForeignKey(
        Organization, on_delete=models.CASCADE, to_field="organization_id"
    )
    user_email = models.ForeignKey(
        User, on_delete=models.CASCADE, to_field="user_email"
    )
    rating = models.IntegerField()
    comment = models.TextField(blank=True, null=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Review by {self.user.first_name} for {self.organization.organization_name}"


# As it currently stands it is users sending eachother messages, which needs to change to users exchanging messages with organizations.
class Message(models.Model):
    message_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender_id = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sent_messages",
        to_field="user_email",
    )
    receiver_id = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="received_messages",
        to_field="user_email",
    )
    message_body = models.TextField()
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.sender.first_name} to {self.receiver.first_name}"


class Order(models.Model):
    ORDER_STATUS_CHOICES = [
        ("picked_up", "Picked Up"),
        ("canceled", "Canceled"),
        ("pending", "Pending"),
    ]

    order_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    donation_id = models.ForeignKey(Donation, on_delete=models.CASCADE)
    user_email = models.ForeignKey(
        User, on_delete=models.CASCADE, to_field="user_email"
    )
    order_quantity = models.IntegerField()
    order_status = models.CharField(
        max_length=20, choices=ORDER_STATUS_CHOICES, default="pending"
    )
    active = models.BooleanField(default=True)
    order_created_at = models.DateTimeField(auto_now_add=True)
    order_modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.order_id} - {self.user.first_name} {self.user.last_name}"
