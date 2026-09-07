from django.db import migrations, models


def remove_duplicate_email_accounts(apps, schema_editor):
    """Keep the oldest account per email; drop incomplete duplicate registrations."""
    User = apps.get_model("accounts", "User")
    StudentProfile = apps.get_model("accounts", "StudentProfile")
    TeacherProfile = apps.get_model("accounts", "TeacherProfile")
    AdminProfile = apps.get_model("accounts", "AdminProfile")

    def has_profile(user_id):
        return (
            StudentProfile.objects.filter(user_id=user_id).exists()
            or TeacherProfile.objects.filter(user_id=user_id).exists()
            or AdminProfile.objects.filter(user_id=user_id).exists()
        )

    seen = {}
    for user in User.objects.order_by("id"):
        email = (user.email or "").strip().lower()
        if not email:
            continue
        if email not in seen:
            seen[email] = user.id
            continue

        keep_id = seen[email]
        if has_profile(user.id) and not has_profile(keep_id):
            User.objects.filter(pk=keep_id).delete()
            seen[email] = user.id
        else:
            user.delete()


def normalize_user_emails(apps, schema_editor):
    User = apps.get_model("accounts", "User")
    for user in User.objects.exclude(email=""):
        normalized = user.email.strip().lower()
        if user.email != normalized:
            user.email = normalized
            user.save(update_fields=["email"])


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0003_teacherprofile_id_card_verified_and_more"),
    ]

    operations = [
        migrations.RunPython(remove_duplicate_email_accounts, migrations.RunPython.noop),
        migrations.RunPython(normalize_user_emails, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="user",
            name="email",
            field=models.EmailField(max_length=254, unique=True, verbose_name="email address"),
        ),
    ]
