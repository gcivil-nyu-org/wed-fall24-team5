# Generated by Django 5.1.1 on 2024-11-04 00:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("database", "0009_room_message_room"),
    ]

    operations = [
        migrations.AddField(
            model_name="room",
            name="conversor_1_name",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="room",
            name="conversor_2_name",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]