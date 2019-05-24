from django.contrib import admin

# Register your models here.
from . import models

admin.site.register(models.ProjectPost)
admin.site.register(models.FaceVector)
admin.site.register(models.Inception)