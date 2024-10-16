# Generated by Django 5.1.1 on 2024-10-17 21:10

from django.db import migrations


def create_user_profiles(apps, schema_editor):
    User = apps.get_model("auth", "User")
    UserProfile = apps.get_model("database", "UserProfile")
    for user in User.objects.all():
        UserProfile.objects.get_or_create(user=user)


def reverse_func(apps, schema_editor):
    pass  # We don't want to delete UserProfiles if we unapply this migration


class Migration(migrations.Migration):

    dependencies = [
        ("database", "0003_userprofile_remove_message_sender_id_and_more"),
    ]

    operations = [
        migrations.RunPython(create_user_profiles, reverse_func),
    ]  # noqa: W292
