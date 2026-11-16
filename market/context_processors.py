from .models import Category, Product


def market_global_context(request):
    """
    Context processor to inject categories, active ticker items,
    and user specific stats across all templates.
    """
    categories = Category.objects.filter(is_active=True).prefetch_related('subcategories')
    # Only ticker products that have a price (exclude unpriced/call)
    featured_ticker_products = Product.objects.filter(
        is_featured=True
    ).exclude(
        pricing_mode=Product.PricingMode.CALL
    ).exclude(
        price=0
    )[:8]
    
    user_orders_count = 0
    if request.user.is_authenticated:
        user_orders_count = request.user.orders.count()

    return {
        'nav_categories': categories,
        'ticker_products': featured_ticker_products,
        'user_orders_count': user_orders_count,
        'brand_name': 'فلزی‌ها',
        'brand_en': 'Feleziha',
        'brand_tagline': 'مرجع تخصصی استعلام قیمت و معاملات مس و فلزات',
        'support_phone': '۰۲۱-۸۸۹۹۰۰۱۱',
        'support_mobile': '۰۹۱۲-۹۸۷۶۵۴۳',
    }
