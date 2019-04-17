import markdown
from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils import timezone

from slugify import slugify


class ArticleColumn(models.Model):
    user = models.ForeignKey(User, related_name='article_column', on_delete=models.CASCADE)
    column = models.CharField(max_length=200)
    created = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.column


class ArticleTag(models.Model):
    author = models.ForeignKey(User, related_name="tag", on_delete=models.CASCADE)
    tag = models.CharField(max_length=500)

    def __str__(self):
        return self.tag


class ArticlePost(models.Model):
    author = models.ForeignKey(User, related_name="article", on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=500)
    image_url = models.CharField(max_length=200, default="image_2.jpg")
    column = models.ForeignKey(ArticleColumn, related_name="article_column",
                               on_delete=models.CASCADE)
    body = models.TextField()
    created = models.DateTimeField(default=timezone.now)
    updated = models.DateTimeField(auto_now=True)
    users_like = models.ManyToManyField(User, related_name="articles_like", blank=True)
    article_tag = models.ManyToManyField(ArticleTag, related_name='article_tag', blank=True)

    # abstract = models.CharField(max_length=300, default=markdown.markdown(body[:70]))

    class Meta:
        # ordering = ("title",)
        ordering = ("-updated",)
        index_together = (('id', 'slug'),)

    def __str__(self):
        return self.title

    def save(self, *args, **kargs):
        self.slug = slugify(self.title)
        super(ArticlePost, self).save(*args, **kargs)

    def get_absolute_url(self):
        return reverse("article:article_detail", args=[self.id, self.slug])

    def get_url_path(self):
        # return "/article/read-article/{0}/{1}".format(self.id, self.slug)
        return reverse("article:list_article_detail", args=[self.id, self.slug])


class Comment(models.Model):
    article = models.ForeignKey(ArticlePost, related_name="comments", on_delete=models.CASCADE)
    commentator = models.CharField(max_length=90)
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return "Comment by {0} on {1}".format(self.commentator.username, self.article)