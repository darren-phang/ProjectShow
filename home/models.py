from django.db import models


class LinkGameRanking(models.Model):
    date = models.CharField(max_length=25)
    username = models.CharField(max_length=25)
    type = models.IntegerField()
    record = models.IntegerField()

    class Meta:
        ordering = ("record",)

    def __str__(self):
        return self.record
