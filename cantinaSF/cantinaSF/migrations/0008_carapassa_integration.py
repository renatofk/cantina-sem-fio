import uuid

import django.db.models.deletion
from django.db import migrations, models


def populate_student_integration_ids(apps, schema_editor):
    Student = apps.get_model("cantinaSF", "Student")
    for student in Student.objects.filter(integration_id__isnull=True).iterator():
        student.integration_id = uuid.uuid4()
        student.save(update_fields=("integration_id",))


class Migration(migrations.Migration):
    dependencies = [("cantinaSF", "0007_alter_course_options_alter_history_options_and_more")]

    operations = [
        migrations.AddField(
            model_name="student", name="integration_id",
            field=models.UUIDField(editable=False, null=True, verbose_name="ID de integração"),
        ),
        migrations.RunPython(populate_student_integration_ids, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="student", name="integration_id",
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name="ID de integração"),
        ),
        migrations.AddField(
            model_name="history", name="consumption_key",
            field=models.CharField(blank=True, editable=False, max_length=150, null=True, unique=True),
        ),
        migrations.CreateModel(
            name="CaraPassaDevice",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("tenant_id", models.UUIDField()), ("school_id", models.UUIDField()),
                ("device_id", models.UUIDField(unique=True)), ("name", models.CharField(max_length=150)),
                ("active", models.BooleanField(default=True)), ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"verbose_name": "Dispositivo CaraPassa", "verbose_name_plural": "Dispositivos CaraPassa"},
        ),
        migrations.CreateModel(
            name="CaraPassaEvent",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("event_id", models.UUIDField(unique=True)), ("event_type", models.CharField(max_length=80)),
                ("tenant_id", models.UUIDField()), ("school_id", models.UUIDField()),
                ("subject_id", models.UUIDField()), ("device_id", models.UUIDField()),
                ("occurred_at", models.DateTimeField()),
                ("confidence", models.DecimalField(decimal_places=6, max_digits=8)),
                ("distance", models.DecimalField(decimal_places=6, max_digits=8)),
                ("model_version", models.CharField(max_length=100)), ("payload", models.JSONField()),
                ("received_at", models.DateTimeField(auto_now_add=True)),
                ("processed_at", models.DateTimeField(blank=True, null=True)),
                ("processing_status", models.CharField(choices=[("received", "Recebido"), ("processed", "Processado"), ("rejected", "Recusado"), ("error", "Erro")], default="received", max_length=20)),
                ("processing_error", models.TextField(blank=True)),
                ("device_mapping", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="cantinaSF.carapassadevice")),
                ("history", models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="cantinaSF.history")),
                ("student", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="cantinaSF.student")),
                ("transaction", models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="cantinaSF.transaction")),
            ],
            options={"verbose_name": "Evento CaraPassa", "verbose_name_plural": "Eventos CaraPassa", "ordering": ("-received_at",)},
        ),
        migrations.AddConstraint(
            model_name="carapassadevice",
            constraint=models.UniqueConstraint(fields=("tenant_id", "school_id", "device_id"), name="unique_carapassa_device_mapping"),
        ),
    ]
