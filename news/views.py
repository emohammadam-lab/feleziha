from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.text import slugify
from django.utils import timezone
from .models import Article, NewsCategory
from market.models import Product


def news_list_view(request, category_slug=None):
    articles = Article.objects.select_related('category', 'author').all()
    categories = NewsCategory.objects.all()
    active_category = None

    if category_slug:
        active_category = get_object_or_404(NewsCategory, slug=category_slug)
        articles = articles.filter(category=active_category)

    breaking_news = Article.objects.filter(is_breaking=True).first()
    recent_products = Product.objects.filter(is_featured=True)[:5]

    context = {
        'articles': articles,
        'categories': categories,
        'active_category': active_category,
        'breaking_news': breaking_news,
        'recent_products': recent_products,
    }
    return render(request, 'news/news_list.html', context)


def news_detail_view(request, slug):
    article = get_object_or_404(Article.objects.select_related('category', 'author'), slug=slug)
    
    # Increment view count safely
    Article.objects.filter(id=article.id).update(views_count=article.views_count + 1)
    article.views_count += 1

    related_articles = Article.objects.filter(category=article.category).exclude(id=article.id)[:3]
    featured_copper_products = Product.objects.filter(subcategory__category__slug='copper')[:4]

    context = {
        'article': article,
        'related_articles': related_articles,
        'featured_copper_products': featured_copper_products,
    }
    return render(request, 'news/news_detail.html', context)


@login_required
def article_create_view(request):
    """
    Editor / Admin view to publish market news.
    """
    if not (request.user.is_admin_role or request.user.is_content_role):
        messages.error(request, "شما دسترسی مجاز به انتشار اخبار را ندارید.")
        return redirect('news:news_list')

    categories = NewsCategory.objects.all()

    if request.method == 'POST':
        title = request.POST.get('title')
        category_id = request.POST.get('category')
        summary = request.POST.get('summary')
        content = request.POST.get('content')
        source = request.POST.get('source', 'تحریریه فلز آنلاین')
        image_badge = request.POST.get('image_badge', 'تحلیل بازار')
        is_breaking = request.POST.get('is_breaking') == 'on'

        if title and category_id and summary and content:
            category = get_object_or_404(NewsCategory, id=category_id)
            slug = slugify(title, allow_unicode=True)[:200]
            # Ensure unique slug
            base_slug = slug
            counter = 1
            while Article.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            article = Article.objects.create(
                category=category,
                title=title,
                slug=slug,
                summary=summary,
                content=content,
                source=source,
                author=request.user,
                image_badge=image_badge,
                is_breaking=is_breaking,
                published_at=timezone.now()
            )
            messages.success(request, f"خبر «{article.title}» با موفقیت منتشر شد.")
            return redirect('news:news_detail', slug=article.slug)
        else:
            messages.error(request, "لطفاً تمامی فیلدهای الزامی را تکمیل نمایید.")

    return render(request, 'news/article_form.html', {'categories': categories})
