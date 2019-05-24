from django.contrib import admin

# Register your models here.
from . import models


class ArticleColumnAdmin(admin.ModelAdmin):
    list_filter = ("column",)
    list_display = ("column", "created", "user",)


admin.site.register(models.ArticleColumn)
admin.site.register(models.ArticlePost)
admin.site.register(models.ArticleTag)
admin.site.register(models.Comment)

