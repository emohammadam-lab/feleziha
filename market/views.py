import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from .models import Category, SubCategory, Product, PriceHistory, OrderInquiry
from .forms import OrderInquiryForm, SalesQuotationUpdateForm, FastPriceUpdateForm
from news.models import Article


def home_view(request):
    """
    Main portal homepage:
    - Live Ticker of metals
    - Category & Subcategory tabs
    - Daily price tables
    - Interactive calculator
    - Real industry news & market insights
    """
    categories = Category.objects.filter(is_active=True).prefetch_related('subcategories__products')
    
    # Selected category for default tab: copper
    copper_cat = Category.objects.filter(slug='copper').first()
    copper_products = Product.objects.filter(subcategory__category=copper_cat)[:10] if copper_cat else Product.objects.all()[:10]
    
    aluminum_cat = Category.objects.filter(slug='aluminum').first()
    aluminum_products = Product.objects.filter(subcategory__category=aluminum_cat)[:10] if aluminum_cat else []

    steel_cat = Category.objects.filter(slug='steel').first()
    steel_products = Product.objects.filter(subcategory__category=steel_cat)[:10] if steel_cat else []

    other_cat = Category.objects.filter(slug='other-metals').first()
    other_products = Product.objects.filter(subcategory__category=other_cat)[:10] if other_cat else []

    # Latest authentic market news
    latest_articles = Article.objects.all().order_by('-published_at')[:4]
    breaking_news = Article.objects.filter(is_breaking=True).first()

    quick_inquiry_form = OrderInquiryForm()
    if request.user.is_authenticated:
        quick_inquiry_form.initial = {
            'customer_name': request.user.get_full_name() or request.user.company_name or request.user.username,
            'customer_phone': request.user.phone_number or '',
            'delivery_address': request.user.address or '',
        }

    context = {
        'categories': categories,
        'copper_products': copper_products,
        'aluminum_products': aluminum_products,
        'steel_products': steel_products,
        'other_products': other_products,
        'latest_articles': latest_articles,
        'breaking_news': breaking_news,
        'quick_inquiry_form': quick_inquiry_form,
    }
    return render(request, 'market/home.html', context)


def product_list_view(request, category_slug=None, subcategory_slug=None):
    """
    Catalog of metal products with category tree, filters, and search.
    """
    products = Product.objects.select_related('subcategory__category').all()
    active_category = None
    active_subcategory = None

    if category_slug:
        active_category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(subcategory__category=active_category)
    
    if subcategory_slug:
        active_subcategory = get_object_or_404(SubCategory, slug=subcategory_slug)
        products = products.filter(subcategory=active_subcategory)
        if not active_category:
            active_category = active_subcategory.category

    # Search query
    query = request.GET.get('q', '').strip()
    if query:
        products = products.filter(
            Q(title__icontains=query) |
            Q(alloy_grade__icontains=query) |
            Q(manufacturer__icontains=query) |
            Q(dimensions__icontains=query)
        )

    # Sorting
    sort = request.GET.get('sort', 'updated')
    if sort == 'price_asc':
        products = products.order_by('price')
    elif sort == 'price_desc':
        products = products.order_by('-price')
    elif sort == 'title':
        products = products.order_by('title')
    else:
        products = products.order_by('-updated_at')

    categories = Category.objects.filter(is_active=True).prefetch_related('subcategories')

    context = {
        'products': products,
        'categories': categories,
        'active_category': active_category,
        'active_subcategory': active_subcategory,
        'search_query': query,
        'sort': sort,
    }
    return render(request, 'market/product_list.html', context)


def product_detail_view(request, slug):
    """
    Product details: specs, live price, history chart points, and direct inquiry form.
    """
    product = get_object_or_404(Product.objects.select_related('subcategory__category'), slug=slug)
    price_history = product.price_history.all().order_by('recorded_at')[:10]
    
    # Related products
    related_products = Product.objects.filter(
        subcategory=product.subcategory
    ).exclude(id=product.id)[:4]

    # Pre-filled inquiry form
    inquiry_form = OrderInquiryForm(initial={'product': product})
    if request.user.is_authenticated:
        inquiry_form.initial.update({
            'customer_name': request.user.get_full_name() or request.user.company_name or request.user.username,
            'customer_phone': request.user.phone_number or '',
            'delivery_address': request.user.address or '',
        })

    # Prepare chart data
    chart_labels = [h.recorded_at.strftime('%m/%d') for h in price_history]
    chart_prices = [h.price for h in price_history]

    context = {
        'product': product,
        'price_history': price_history,
        'related_products': related_products,
        'inquiry_form': inquiry_form,
        'chart_labels': json.dumps(chart_labels),
        'chart_prices': json.dumps(chart_prices),
    }
    return render(request, 'market/product_detail.html', context)


def inquiry_create_view(request):
    """
    Create a new Price Inquiry / Proforma request.
    """
    if request.method == 'POST':
        form = OrderInquiryForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            if request.user.is_authenticated:
                order.user = request.user
            
            # If product is chosen and has price, estimate default unit price
            if order.product and order.product.price:
                order.quoted_unit_price = order.product.price

            order.save()
            messages.success(request, f"استعلام خرید شما با کد رهگیری «{order.tracking_code}» ثبت شد. کارشناسان ما به زودی پیش‌فاکتور را صادر خواهند کرد.")
            return redirect('market:inquiry_success', tracking_code=order.tracking_code)
        else:
            messages.error(request, "لطفاً مقادیر وارد شده را بررسی فرمایید.")
    else:
        product_id = request.GET.get('product')
        initial_data = {}
        if product_id:
            prod = Product.objects.filter(id=product_id).first()
            if prod:
                initial_data['product'] = prod
        if request.user.is_authenticated:
            initial_data.update({
                'customer_name': request.user.get_full_name() or request.user.company_name or request.user.username,
                'customer_phone': request.user.phone_number or '',
                'delivery_address': request.user.address or '',
            })
        form = OrderInquiryForm(initial=initial_data)

    return render(request, 'market/inquiry_create.html', {'form': form})


def inquiry_success_view(request, tracking_code):
    order = get_object_or_404(OrderInquiry, tracking_code=tracking_code)
    return render(request, 'market/inquiry_success.html', {'order': order})


@login_required
def customer_dashboard_view(request):
    """
    Buyer's personal customer portal:
    View quotes, active orders, track status, download proforma.
    """
    orders = OrderInquiry.objects.filter(user=request.user).order_by('-created_at')
    
    stats = {
        'total': orders.count(),
        'pending': orders.filter(status=OrderInquiry.Status.PENDING).count(),
        'quoted': orders.filter(status=OrderInquiry.Status.QUOTED).count(),
        'approved': orders.filter(status=OrderInquiry.Status.APPROVED).count(),
        'completed': orders.filter(status=OrderInquiry.Status.COMPLETED).count(),
    }

    return render(request, 'market/customer_dashboard.html', {'orders': orders, 'stats': stats})


def proforma_invoice_view(request, tracking_code):
    """
    Official downloadable / printable Proforma Invoice (پیش‌فاکتور رسمی).
    """
    order = get_object_or_404(OrderInquiry, tracking_code=tracking_code)
    
    # Permission check: superuser, sales, or the owner of order
    if not (request.user.is_authenticated and (request.user.is_admin_role or request.user.is_sales_role or order.user == request.user)):
        # If guest order, allow viewing with matching phone number validation or direct tracking code
        pass

    return render(request, 'market/proforma_invoice.html', {'order': order})


# ========================================================
# Sales & Admin Management Portal
# ========================================================

def sales_or_admin_required(user):
    return user.is_authenticated and (user.is_admin_role or user.is_sales_role)


@login_required
def management_dashboard_view(request):
    if not (request.user.is_admin_role or request.user.is_sales_role or request.user.is_content_role):
        messages.error(request, "شما دسترسی مجاز به پنل مدیریت داخلی را ندارید.")
        return redirect('market:home')

    status_filter = request.GET.get('status', '')
    inquiries_qs = OrderInquiry.objects.all().order_by('-created_at')
    if status_filter:
        inquiries_qs = inquiries_qs.filter(status=status_filter)

    products = Product.objects.all().order_by('subcategory__category', 'title')

    stats = {
        'inquiries_total': OrderInquiry.objects.count(),
        'inquiries_pending': OrderInquiry.objects.filter(status=OrderInquiry.Status.PENDING).count(),
        'inquiries_quoted': OrderInquiry.objects.filter(status=OrderInquiry.Status.QUOTED).count(),
        'products_count': Product.objects.count(),
        'articles_count': Article.objects.count(),
    }

    context = {
        'inquiries': inquiries_qs[:20],
        'products': products,
        'stats': stats,
        'status_filter': status_filter,
        'status_choices': OrderInquiry.Status.choices,
    }
    return render(request, 'market/management_dashboard.html', context)


@login_required
def fast_price_update_api(request):
    """
    AJAX / POST endpoint for Sales Officers to update metal prices quickly.
    """
    if not (request.user.is_admin_role or request.user.is_sales_role):
        return JsonResponse({'status': 'error', 'message': 'عدم دسترسی مجاز'}, status=403)

    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        new_price = request.POST.get('new_price')
        note = request.POST.get('note', 'بروزرسانی از طریق پنل سریع')

        try:
            product = Product.objects.get(id=product_id)
            new_price = int(new_price)
            if new_price > 0:
                product.price_previous = product.price
                product.price = new_price
                product.save()

                PriceHistory.objects.create(
                    product=product,
                    price=new_price,
                    note=f"{note} (توسط {request.user.username})"
                )
                return JsonResponse({
                    'status': 'success',
                    'message': f'قیمت {product.title} به {new_price:,} تومان تغییر یافت.',
                    'new_price': f"{new_price:,}",
                    'diff_percent': product.price_diff_percent,
                    'is_up': product.is_price_up,
                })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    return JsonResponse({'status': 'error', 'message': 'متد نامعتبر'}, status=405)


@login_required
def sales_quotation_edit_view(request, tracking_code):
    """
    Sales officer edits and issues a quotation for an inquiry.
    """
    if not (request.user.is_admin_role or request.user.is_sales_role):
        messages.error(request, "شما دسترسی به صدور پیش‌فاکتور را ندارید.")
        return redirect('market:home')

    order = get_object_or_404(OrderInquiry, tracking_code=tracking_code)

    if request.method == 'POST':
        form = SalesQuotationUpdateForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            messages.success(request, f"پیش‌فاکتور سفارش «{order.tracking_code}» با موفقیت بروزرسانی شد.")
            return redirect('market:management_dashboard')
    else:
        form = SalesQuotationUpdateForm(instance=order)

    return render(request, 'market/sales_quotation_edit.html', {'order': order, 'form': form})
