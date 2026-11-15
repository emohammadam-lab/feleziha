from django.contrib import admin
from .models import NewsCategory, Article


@admin.register(NewsCategory)
class NewsCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'source', 'author', 'views_count', 'is_breaking', 'published_at')
    list_filter = ('category', 'is_breaking', 'published_at')
    search_fields = ('title', 'summary', 'content', 'source')
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('is_breaking',)

    def save_model(self, request, obj, form, change):
        if not obj.author:
            obj.author = request.user
        super().save_model(request, obj, form, change)
