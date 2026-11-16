from django.urls import path
from . import views

app_name = 'market'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('products/', views.product_list_view, name='product_list'),
    path('category/<slug:category_slug>/', views.product_list_view, name='category_products'),
    path('subcategory/<slug:subcategory_slug>/', views.product_list_view, name='subcategory_products'),
    path('product/<slug:slug>/', views.product_detail_view, name='product_detail'),
    
    path('inquiry/new/', views.inquiry_create_view, name='inquiry_create'),
    path('inquiry/success/<str:tracking_code>/', views.inquiry_success_view, name='inquiry_success'),
    
    path('dashboard/', views.customer_dashboard_view, name='dashboard'),
    path('invoice/<str:tracking_code>/', views.proforma_invoice_view, name='proforma_invoice'),
    path('proforma/<str:tracking_code>/', views.proforma_invoice_view, name='proforma_invoice_alt'),
    
    # Management & Sales Portal
    path('management/', views.management_dashboard_view, name='management_dashboard'),
    path('management/fast-price-update/', views.fast_price_update_api, name='fast_price_update'),
    path('management/sync-api-prices/', views.sync_all_api_view, name='sync_api_prices'),
    path('management/quote/<str:tracking_code>/', views.sales_quotation_edit_view, name='sales_quotation_edit'),
]
