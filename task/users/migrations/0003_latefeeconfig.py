# Generated by Django 5.1.4 on 2024-12-22 19:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_remove_profile_email'),
    ]

    operations = [
        migrations.CreateModel(
            name='LateFeeConfig',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('days_before_late_fee', models.PositiveIntegerField(default=7)),
            ],
        ),
    ]
