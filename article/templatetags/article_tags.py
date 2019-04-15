import re

import markdown
from django import template
from django.db.models import Count
from django.utils.safestring import mark_safe

register = template.Library()

from article.models import ArticlePost


@register.simple_tag
def total_articles():
    return ArticlePost.objects.count()


@register.filter(name='count_word')
def total_words(text):
    return len(re.split(r" |;|,", text))


@register.simple_tag
def author_total_articles(user):
    return user.article.count()


@register.inclusion_tag('article/list/latest_articles.html')
def latest_articles(n=5):
    latest_articles = ArticlePost.objects.order_by("-created")[:n]
    return {"latest_articles": latest_articles}


@register.simple_tag
def most_commented_articles(n=3):
    return ArticlePost.objects.annotate(total_comments=Count('comments')).order_by(
        "-total_comments")[:n]


@register.filter(name='markdown')
def markdown_filter(text):
    return mark_safe(markdown.markdown(text, ['extra', 'codehilite', 'toc']))


@register.filter(name='markdownabstract')
def markdown_filter_abstract(text):
    content_text1 = text.replace('<p>', '').replace('</p>', '').replace('\'', '')
    content_text2 = re.sub('!\[(.*?)\]\((.*?)\)', '', content_text1)
    content_text2 = re.sub('\[(.*?)\]\((.*?)\)', '', content_text2)
    pattern = '[\\\`\*\_\[\]\#\+\-\!\>]'
    content_text3 = re.sub(pattern, '', content_text2)
    return content_text3[:150] + "......"
