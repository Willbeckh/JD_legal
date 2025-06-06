# Generated by Django 5.2.1 on 2025-06-04 21:38

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("scriptapp", "0002_assignment"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="project",
            name="proofreader",
            field=models.ForeignKey(
                blank=True,
                limit_choices_to={"role": "proofreader"},
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="proofread_projects",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="project",
            name="transcriber",
            field=models.ForeignKey(
                blank=True,
                limit_choices_to={"role": "transcriber"},
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="transcribed_projects",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
