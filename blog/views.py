from django.shortcuts import render, get_object_or_404

# Create your views here.
from blog.models import BlogArticles
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from article.models import ArticleColumn, ArticlePost, ArticleTag


def index(request):
    # articles = ArticlePost.objects.filter(author=request.user)
    # return render(request, "article/column/article_list.html", {"articles":articles})
    articles_list = ArticlePost.objects.filter()
    paginator = Paginator(articles_list, 6)
    page = request.GET.get('page')
    try:
        current_page = paginator.page(page)
        articles = current_page.object_list
    except PageNotAnInteger:
        current_page = paginator.page(1)
        articles = current_page.object_list
    except EmptyPage:
        current_page = paginator.page(paginator.num_pages)
        articles = current_page.object_list
    return render(request, "blog/blog.html",
                  {"articles": articles, "page": current_page,
                   "total_pages": list(range(1, int(ArticlePost.objects.count()/6+2)))})


def blog_titile(request):
    blogs = BlogArticles.objects.all()
    return render(request, "blog/titles.html", {"blogs": blogs})


def blog_article(request, article_id):
    # article = BlogArticles.objects.get(id=article_id)
    article = get_object_or_404(BlogArticles, id=article_id)
    pub = article.publish
    return render(request, "blog/content.html", {"article": article, "publish": pub})
