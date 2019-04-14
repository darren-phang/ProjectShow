from django.db import models
# Create your models here.


class Inception(models.Model):
    img = models.ImageField(upload_to='image')
    name = models.CharField(max_length=255)
    predict = models.TextField(default='')

