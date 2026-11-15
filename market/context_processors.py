from .models import Category, Product


def market_global_context(request):
    """
    Context processor to inject categories, featured ticker items,
    and user specific stats across all templates.
    """
    categories = Category.objects.filter(is_active=True).prefetch_related('subcategories')
    featured_ticker_products = Product.objects.filter(is_featured=True)[:8]
    
    user_orders_count = 0
    if request.user.is_authenticated:
        if request.user.is_admin_role or request.user.is_sales_role:
            user_orders_count = request.user.orders.count()
        else:
            user_orders_count = request.user.orders.count()

    return {
        'nav_categories': categories,
        'ticker_products': featured_ticker_products,
        'user_orders_count': user_orders_count,
        'brand_name': 'فلز آنلاین',
        'brand_tagline': 'مرجع تخصصی استعلام قیمت و تأمین مس و فلزات',
        'support_phone': '۰۲۱-۸۸۹۹۰۰۱۱',
        'support_mobile': '۰۹۱۲-۹۸۷۶۵۴۳',
    }
