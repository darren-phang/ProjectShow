from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

# Create your models here.


class Inception(models.Model):
    img = models.ImageField(upload_to='image')
    name = models.CharField(max_length=255)
    predict = models.TextField(default='')


class ProjectPost(models.Model):
    company = models.CharField(max_length=200)
    title = models.CharField(max_length=200)
    describe = models.CharField(max_length=500)
    image_url = models.CharField(max_length=200, default="image_2.jpg")
    star = models.IntegerField(default=5)
    about_more_url = models.CharField(max_length=200, default="http://www.baidu.com")

    type = models.CharField(max_length=40)
    port = models.IntegerField(default=9000)
    address = models.CharField(max_length=100)
    input_tensor_name = models.CharField(max_length=100, default='images')
    model_name = models.CharField(max_length=100, default='inception')
    signature_name = models.CharField(max_length=100, default='None')

    def get_project_url(self):
        return reverse("project_show", args=[self.id, self.type])
