# Generated by Django 5.1.4 on 2024-12-22 19:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0007_alter_book_available_copies_alter_book_total_copies_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='borrow',
            name='due_date',
        ),
    ]
