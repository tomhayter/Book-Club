# Generated by Django 4.2.4 on 2024-02-18 13:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0006_alter_book_description_alter_book_pages_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='bookrating',
            name='stars',
            field=models.CharField(default='0.0_stars.html', max_length=50),
            preserve_default=False,
        ),
    ]
