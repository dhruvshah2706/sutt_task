# Generated by Django 5.1.4 on 2024-12-20 12:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0002_book_publisher_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='isbn',
            field=models.PositiveBigIntegerField(max_length=13, unique=True),
        ),
    ]
