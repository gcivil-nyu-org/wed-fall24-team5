# Generated by Django 5.1.1 on 2024-10-14 20:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="order",
            name="donation_id",
        ),
        migrations.RemoveField(
            model_name="message",
            name="receiver_id",
        ),
        migrations.RemoveField(
            model_name="message",
            name="sender_id",
        ),
        migrations.RemoveField(
            model_name="order",
            name="user_email",
        ),
        migrations.RemoveField(
            model_name="userreview",
            name="organization_id",
        ),
        migrations.RemoveField(
            model_name="organizationadmin",
            name="organization_id",
        ),
        migrations.RemoveField(
            model_name="organizationadmin",
            name="user_email",
        ),
        migrations.RemoveField(
            model_name="userreview",
            name="user_email",
        ),
        migrations.DeleteModel(
            name="Donation",
        ),
        migrations.DeleteModel(
            name="Message",
        ),
        migrations.DeleteModel(
            name="Order",
        ),
        migrations.DeleteModel(
            name="Organization",
        ),
        migrations.DeleteModel(
            name="OrganizationAdmin",
        ),
        migrations.DeleteModel(
            name="User",
        ),
        migrations.DeleteModel(
            name="UserReview",
        ),
    ]
