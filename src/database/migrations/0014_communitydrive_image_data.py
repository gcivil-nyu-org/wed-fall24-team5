# Generated by Django 5.1.1 on 2024-11-28 02:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("database", "0013_driveorganization_volunteer_pledge_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="communitydrive",
            name="image_data",
            field=models.TextField(blank=True, null=True),
        ),
    ]
