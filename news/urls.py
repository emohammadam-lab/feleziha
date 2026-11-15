from django.urls import path
from . import views

app_name = 'news'

urlpatterns = [
    path('', views.news_list_view, name='news_list'),
    path('category/<slug:category_slug>/', views.news_list_view, name='category_news'),
    path('article/<slug:slug>/', views.news_detail_view, name='news_detail'),
    path('publish/', views.article_create_view, name='article_create'),
]
