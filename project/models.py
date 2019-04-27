from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
import numpy as np
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

    def get_star_list(self):
        return list(range(int(self.star)))

    def get_none_star_list(self):
        return list(range(5-int(self.star)))


class FaceVector(models.Model):
    vector = models.BinaryField()
    face_name = models.CharField(max_length=50, default='NoOne')
    user_id = models.CharField(max_length=50, default='')
    image_url = models.CharField(max_length=200, default='')

    def get_embedding(self):
        return np.frombuffer(self.vector, dtype=np.float)

    def to_string(self):
        info = {}
        info['face_name'] = self.face_name
        info['image_url'] = self.image_url
        image_from = self.image_url.split('/')[-1].split('_')[0] + '.jpg'
        info['from_image'] = 'face/' + image_from
        return info
