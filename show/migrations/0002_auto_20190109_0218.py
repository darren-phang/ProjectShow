# Generated by Django 2.0.7 on 2019-01-09 02:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('show', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inception',
            name='predict',
            field=models.TextField(default=''),
        ),
    ]
