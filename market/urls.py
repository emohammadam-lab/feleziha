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
    path('management/products/<int:product_id>/edit/', views.product_edit_view, name='product_edit'),
    
    # CMS Content Blocks Endpoints
    path('management/blocks/save/', views.block_save_view, name='block_create'),
    path('management/blocks/<int:block_id>/save/', views.block_save_view, name='block_edit'),
    path('management/blocks/<int:block_id>/delete/', views.block_delete_view, name='block_delete'),
    
    # Media Assets Endpoints
    path('management/media/save/', views.media_save_view, name='media_create'),
    path('management/media/<int:media_id>/save/', views.media_save_view, name='media_edit'),
    path('management/media/<int:media_id>/delete/', views.media_delete_view, name='media_delete'),
    
    # Staff Permissions Endpoint
    path('management/staff/<int:user_id>/perms/', views.staff_permission_save_view, name='staff_permission_save'),
    
    # Public Media Gallery Showcase
    path('gallery/', views.gallery_public_view, name='gallery'),
]
