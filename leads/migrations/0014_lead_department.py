# Generated by Django 5.2.1 on 2025-06-09 08:51

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("leads", "0013_alter_lead_grid_type_alter_lead_stage"),
        ("profiles", "0004_departmentcategory_department_category"),
    ]

    operations = [
        migrations.AddField(
            model_name="lead",
            name="department",
            field=models.ForeignKey(
                blank=True,
                help_text="Which Sales department should own this lead",
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="leads",
                to="profiles.department",
            ),
        ),
    ]
