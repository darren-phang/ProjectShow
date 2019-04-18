from django.db import models

# Create your models here.


class ConcatMessage(models.Model):
    name = models.CharField(max_length=200, default='None')
    email = models.CharField(max_length=200, default='None')
    subject = models.CharField(max_length=500, default='None')
    message = models.TextField()


