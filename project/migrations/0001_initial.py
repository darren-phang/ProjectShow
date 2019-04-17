# Generated by Django 2.0.7 on 2019-04-15 11:35

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Inception',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('img', models.ImageField(upload_to='image')),
                ('name', models.CharField(max_length=255)),
                ('predict', models.TextField(default='')),
            ],
        ),
    ]