# Generated by Django 5.1.4 on 2024-12-20 19:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0004_alter_book_isbn'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='available',
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AddField(
            model_name='book',
            name='number',
            field=models.PositiveIntegerField(default=1),
        ),
    ]
