# Generated by Django 5.2.1 on 2025-06-23 14:23

import django.core.validators
import profiles.models
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("profiles", "0005_approvallimit"),
    ]

    operations = [
        migrations.AddField(
            model_name="department",
            name="draft_quotation",
            field=models.FileField(
                blank=True,
                help_text="Upload a PDF up to 100 MB.",
                null=True,
                upload_to="departments/draft_quotations/",
                validators=[
                    django.core.validators.FileExtensionValidator(
                        allowed_extensions=["pdf"]
                    ),
                    profiles.models.validate_file_size,
                ],
            ),
        ),
    ]
