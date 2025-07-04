# Generated by Django 5.2.1 on 2025-06-09 09:06

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models



class Migration(migrations.Migration):
    dependencies = [
        ("leads", "0015_departmentassignmentpointer"),
        ("profiles", "0004_departmentcategory_department_category"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name="lead",
            name="department",
            field=models.ForeignKey(
                help_text="Assign this lead to a Sales department",
                on_delete=django.db.models.deletion.PROTECT,
                related_name="leads",
                to="profiles.department",
                null=True,    # allow NULL in the DB
                blank=True, 
            ),
        ),
        migrations.CreateModel(
            name="LeadAssignmentLog",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("timestamp", models.DateTimeField(auto_now_add=True)),
                (
                    "assigned_to",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "department",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="profiles.department",
                    ),
                ),
                (
                    "lead",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="assignment_logs",
                        to="leads.lead",
                    ),
                ),
            ],
            options={
                "verbose_name": "Lead Assignment Log",
                "verbose_name_plural": "Lead Assignment Logs",
                "ordering": ["-timestamp"],
            },
        ),
    ]
