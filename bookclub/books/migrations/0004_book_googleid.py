# Generated by Django 4.2.4 on 2024-01-24 14:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0003_book_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='googleID',
            field=models.CharField(default='', max_length=100),
            preserve_default=False,
        ),
    ]