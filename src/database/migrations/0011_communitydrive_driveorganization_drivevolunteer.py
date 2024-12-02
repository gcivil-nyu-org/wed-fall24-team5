# Generated by Django 5.1.1 on 2024-11-24 22:41

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("database", "0010_room_conversor_1_name_room_conversor_2_name"),
    ]

    operations = [
        migrations.CreateModel(
            name="CommunityDrive",
            fields=[
                (
                    "drive_id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                ("description", models.TextField()),
                ("meal_target", models.IntegerField()),
                ("volunteer_target", models.IntegerField()),
                ("start_date", models.DateField()),
                ("end_date", models.DateField()),
                ("active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                (
                    "lead_organization",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="database.organization",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="DriveOrganization",
            fields=[
                (
                    "participation_id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("meal_pledge", models.IntegerField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                (
                    "drive",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="database.communitydrive",
                    ),
                ),
                (
                    "organization",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="database.organization",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="DriveVolunteer",
            fields=[
                (
                    "participation_id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                ("email", models.EmailField(max_length=254)),
                ("phone", models.CharField(max_length=20)),
                ("active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                (
                    "drive",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="database.communitydrive",
                    ),
                ),
            ],
        ),
    ]