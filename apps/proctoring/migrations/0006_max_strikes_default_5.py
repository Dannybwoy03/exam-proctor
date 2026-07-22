from django.db import migrations, models


def bump_active_sessions(apps, schema_editor):
    """Raise the limit for sessions whose exams are still running so students
    mid-exam get the new 5-strike tolerance. Finished/terminated sessions keep
    their historical limit."""
    ProctoringSession = apps.get_model("proctoring", "ProctoringSession")
    ProctoringSession.objects.filter(
        max_strikes=3,
        attempt__status__in=["in_progress", "pending_id", "paused"],
    ).update(max_strikes=5)


class Migration(migrations.Migration):

    dependencies = [
        ("proctoring", "0005_proctoringsession_look_away_started_at_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="proctoringsession",
            name="max_strikes",
            field=models.PositiveIntegerField(default=5),
        ),
        migrations.RunPython(bump_active_sessions, migrations.RunPython.noop),
    ]
