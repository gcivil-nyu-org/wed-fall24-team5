# Generated by Django 5.1.1 on 2024-11-03 09:57

import database.models
import django.contrib.auth.models
import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("contenttypes", "0002_remove_content_type_name"),
        ("database", "0008_dietaryrestriction"),
    ]

    operations = [
        migrations.CreateModel(
            name="Room",
            fields=[
                (
                    "room_id",
                    models.CharField(
                        default=uuid.uuid4,
                        max_length=255,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("room_name", models.CharField(default="Chat Room", max_length=255)),
                ("conversor_1_id", models.CharField(default=uuid.uuid4)),
                ("conversor_2_id", models.CharField(default=uuid.uuid4)),
                (
                    "conversor_1_type",
                    models.ForeignKey(
                        default=django.contrib.auth.models.User,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="conversor_1",
                        to="contenttypes.contenttype",
                    ),
                ),
                (
                    "conversor_2_type",
                    models.ForeignKey(
                        default=database.models.Organization,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="conversor_2",
                        to="contenttypes.contenttype",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="message",
            name="room",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="database.room",
            ),
        ),
    ]
