# Generated by Django 2.0.7 on 2019-03-08 07:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('timetable', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='courseshtml',
            name='notified',
            field=models.BooleanField(default=False),
        ),
    ]
