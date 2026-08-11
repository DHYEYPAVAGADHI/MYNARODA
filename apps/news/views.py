from django.shortcuts import render, get_object_or_404
from django.views import View
from django.utils import timezone
from django.core.paginator import Paginator

from apps.news.models import NewsArticle, NewsCategory, Document

class NewsListView(View):
    template_name = "news/list.html"

    def get(self, request):
        category_slug = request.GET.get("category")
        articles = NewsArticle.objects.filter(is_published=True, published_at__lte=timezone.now())
        
        if category_slug:
            articles = articles.filter(category__slug=category_slug)
            
        paginator = Paginator(articles, 6) # 6 articles per page
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        categories = NewsCategory.objects.all()
        documents = Document.objects.filter(is_public=True).order_by("-created_at")

        context = {
            "page_obj": page_obj,
            "categories": categories,
            "documents": documents,
            "selected_category": category_slug,
        }
        return render(request, self.template_name, context)


class NewsDetailView(View):
    template_name = "news/detail.html"

    def get(self, request, slug):
        article = get_object_or_404(
            NewsArticle, 
            slug=slug, 
            is_published=True, 
            published_at__lte=timezone.now()
        )
        # Show recent articles in sidebar
        recent_articles = NewsArticle.objects.filter(
            is_published=True, 
            published_at__lte=timezone.now()
        ).exclude(id=article.id).order_by("-published_at")[:4]

        context = {
            "article": article,
            "recent_articles": recent_articles,
        }
        return render(request, self.template_name, context)
