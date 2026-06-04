from django.db import migrations


def approve_existing_published(apps, schema_editor):
    Exam = apps.get_model("exams", "Exam")
    Exam.objects.filter(is_published=True).update(approval_status="approved")


class Migration(migrations.Migration):
    dependencies = [
        ("exams", "0002_alter_question_options_exam_admin_notes_and_more"),
    ]

    operations = [
        migrations.RunPython(approve_existing_published, migrations.RunPython.noop),
    ]
