# Generated by Django 2.0.7 on 2019-04-14 10:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('show', '0002_auto_20190109_0218'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inception',
            name='name',
            field=models.CharField(max_length=255),
        ),
    ]
