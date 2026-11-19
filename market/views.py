import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from django.contrib.auth import get_user_model
from .models import Category, SubCategory, Product, PriceHistory, OrderInquiry, SiteContentBlock, MediaAsset
from .forms import OrderInquiryForm, SalesQuotationUpdateForm, SiteContentBlockForm, MediaAssetForm, ProductQuickEditForm
from .pricing_service import sync_all_api_products, calculate_formula_price
from news.models import Article

User = get_user_model()


def home_view(request):
    """
    Main portal homepage:
    - Live Ticker of metals
    - Category & Subcategory tabs
    - Daily price tables (handling Manual, API, and Call-for-price)
    - Interactive calculator
    - Real industry news & market insights
    """
    categories = Category.objects.filter(is_active=True).prefetch_related('subcategories__products')
    
    # Categorized products (Focused on Copper & its specialized segments)
    copper_cat = Category.objects.filter(slug='copper').first()
    copper_products = Product.objects.filter(subcategory__category=copper_cat).order_by('subcategory__order', '-updated_at') if copper_cat else Product.objects.all()[:15]
    
    # Specific copper subgroups for specialized tabs
    export_rod_products = copper_products.filter(subcategory__slug__in=['copper-export-rod', 'copper-wire-rod'])
    busbar_products = copper_products.filter(subcategory__slug='copper-busbar')
    wire_conductor_products = copper_products.filter(subcategory__slug='copper-wire-conductor')
    cathode_products = copper_products.filter(subcategory__slug='copper-cathode')
    tube_sheet_products = copper_products.filter(subcategory__slug__in=['copper-tubes', 'copper-sheet-strip'])

    # Preserved for future expansion (currently hidden/inactive)
    aluminum_cat = Category.objects.filter(slug='aluminum').first()
    aluminum_products = Product.objects.filter(subcategory__category=aluminum_cat)[:12] if aluminum_cat else []

    steel_cat = Category.objects.filter(slug='steel').first()
    steel_products = Product.objects.filter(subcategory__category=steel_cat)[:12] if steel_cat else []

    other_cat = Category.objects.filter(slug='other-metals').first()
    other_products = Product.objects.filter(subcategory__category=other_cat)[:12] if other_cat else []

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

    # Featured copper products with real industrial photos for top visual showcase
    featured_products = [p for p in copper_products if p.image][:6]
    if not featured_products:
        featured_products = copper_products[:6]

    context = {
        'categories': categories,
        'copper_products': copper_products,
        'featured_products': featured_products,
        'export_rod_products': export_rod_products,
        'busbar_products': busbar_products,
        'wire_conductor_products': wire_conductor_products,
        'cathode_products': cathode_products,
        'tube_sheet_products': tube_sheet_products,
        # Preserved in context for future use
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
    Defaults to active categories (copper).
    """
    products = Product.objects.select_related('subcategory__category').filter(subcategory__category__is_active=True)
    active_category = None
    active_subcategory = None

    if category_slug:
        active_category = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.select_related('subcategory__category').filter(subcategory__category=active_category)
    
    if subcategory_slug:
        active_subcategory = get_object_or_404(SubCategory, slug=subcategory_slug)
        products = Product.objects.select_related('subcategory__category').filter(subcategory=active_subcategory)
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
    Product details: specs, live price (or call-for-price), history chart, and direct inquiry form.
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
            if order.product and order.product.price and not order.product.is_call_for_price:
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
    return render(request, 'market/proforma_invoice.html', {'order': order})


# ========================================================
# Sales & Admin Management Portal (SIMPLIFIED & FAST)
# ========================================================

@login_required
def management_dashboard_view(request):
    """
    User-Friendly & Unified Management Control Center:
    - Tab 1: Pricing Board (Manual, Auto-API, Call-for-price)
    - Tab 2: Orders & Inquiries pipeline
    - Tab 3: CMS Content Blocks (Every block on the website)
    - Tab 4: Media Gallery (Photos, Videos, PDF Catalogs)
    - Tab 5: Team Staff & Granular RBAC Permissions
    """
    has_any_perm = (
        request.user.is_admin_role or
        request.user.is_sales_role or
        request.user.is_content_role or
        request.user.has_price_perm() or
        request.user.has_content_perm() or
        request.user.has_media_perm() or
        request.user.has_inquiry_perm()
    )
    if not has_any_perm:
        messages.error(request, "شما دسترسی مجاز به پنل مدیریت را ندارید.")
        return redirect('market:home')

    active_tab = request.GET.get('tab', 'pricing')
    status_filter = request.GET.get('status', '')

    inquiries_qs = OrderInquiry.objects.all().order_by('-created_at')
    if status_filter:
        inquiries_qs = inquiries_qs.filter(status=status_filter)

    products = Product.objects.select_related('subcategory__category').all().order_by('subcategory__category', 'title')

    # Content Blocks (CMS)
    content_blocks = SiteContentBlock.objects.all().order_by('section', 'order')

    # Media Assets (Gallery)
    media_assets = MediaAsset.objects.all().order_by('order', '-created_at')

    # Staff Members (Permissions)
    staff_users = User.objects.filter(is_staff=True).order_by('-date_joined')

    # Concise stats
    stats = {
        'inquiries_pending': OrderInquiry.objects.filter(status=OrderInquiry.Status.PENDING).count(),
        'inquiries_quoted': OrderInquiry.objects.filter(status=OrderInquiry.Status.QUOTED).count(),
        'products_total': products.count(),
        'products_api': products.filter(pricing_mode=Product.PricingMode.AUTO_API).count(),
        'products_call': products.filter(pricing_mode=Product.PricingMode.CALL).count(),
        'products_manual': products.filter(pricing_mode=Product.PricingMode.MANUAL).count(),
        'blocks_total': content_blocks.count(),
        'media_total': media_assets.count(),
        'staff_total': staff_users.count(),
    }

    context = {
        'inquiries': inquiries_qs[:35],
        'products': products,
        'content_blocks': content_blocks,
        'media_assets': media_assets,
        'staff_users': staff_users,
        'block_form': SiteContentBlockForm(),
        'media_form': MediaAssetForm(),
        'product_form': ProductQuickEditForm(),
        'stats': stats,
        'active_tab': active_tab,
        'status_filter': status_filter,
        'status_choices': OrderInquiry.Status.choices,
        'pricing_mode_choices': Product.PricingMode.choices,
        'section_choices': SiteContentBlock.Section.choices,
        'media_type_choices': MediaAsset.MediaType.choices,
    }
    return render(request, 'market/management_dashboard.html', context)


def _clean_price_input(value_str):
    """
    Sanitize price input: converts Persian/Arabic numerals to English,
    strips commas, spaces, and separators, returning a positive integer or 0.
    """
    if not value_str:
        return 0
    persian_digits = '۰۱۲۳۴۵۶۷۸۹'
    arabic_digits = '٠١٢٣٤٥٦٧٨٩'
    s = str(value_str).strip()
    for i in range(10):
        s = s.replace(persian_digits[i], str(i)).replace(arabic_digits[i], str(i))
    s = s.replace(',', '').replace('،', '').replace(' ', '').replace('_', '')
    try:
        val = int(float(s))
        return max(0, val)
    except (ValueError, TypeError):
        return 0


@login_required
def fast_price_update_api(request):
    """
    Agile AJAX endpoint for Sales & Admin to:
    1. Set Manual price
    2. Switch to Auto-API pricing
    3. Set to 'Call for price' (بدون نرخ / تماس بگیرید)
    """
    if not request.user.has_price_perm():
        return JsonResponse({'status': 'error', 'message': 'عدم دسترسی مجاز برای تغییر قیمت'}, status=403)

    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        pricing_mode = request.POST.get('pricing_mode', Product.PricingMode.MANUAL)
        new_price_raw = request.POST.get('new_price', '').strip()
        note = request.POST.get('note', 'بروزرسانی از پنل مدیریت')

        try:
            product = Product.objects.get(id=product_id)
            product.pricing_mode = pricing_mode

            if pricing_mode == Product.PricingMode.CALL:
                # Unpriced / Call for price
                product.price_previous = product.price
                product.price = 0
                product.save()

                PriceHistory.objects.create(
                    product=product,
                    price=0,
                    note=f"تغییر به وضعیت تماس بگیرید (توسط {request.user.username})"
                )

                return JsonResponse({
                    'status': 'success',
                    'mode': 'call',
                    'product_id': product.id,
                    'display_text': 'تماس بگیرید',
                    'new_price': 0,
                    'message': f'کالای «{product.title}» روی وضعیت «تماس بگیرید» تنظیم شد.',
                })

            elif pricing_mode == Product.PricingMode.AUTO_API:
                # Auto API calculation
                computed_price = calculate_formula_price(product)
                product.price_previous = product.price or computed_price
                product.price = computed_price
                product.save()

                PriceHistory.objects.create(
                    product=product,
                    price=computed_price,
                    note=f"محاسبه وب‌سرویس LME/نیما: {computed_price:,} تومان"
                )

                return JsonResponse({
                    'status': 'success',
                    'mode': 'api',
                    'product_id': product.id,
                    'display_text': f"{computed_price:,} تومان (API)",
                    'new_price': f"{computed_price:,}",
                    'raw_price': computed_price,
                    'diff_percent': product.price_diff_percent,
                    'message': f'نرخ «{product.title}» به صورت خودکار از API روی {computed_price:,} تومان همگام شد.',
                })

            else:
                # Manual pricing
                new_price = _clean_price_input(new_price_raw)
                if new_price > 0:
                    product.price_previous = product.price or new_price
                    product.price = new_price
                    product.save()

                    PriceHistory.objects.create(
                        product=product,
                        price=new_price,
                        note=f"{note} (توسط {request.user.username})"
                    )

                    return JsonResponse({
                        'status': 'success',
                        'mode': 'manual',
                        'product_id': product.id,
                        'display_text': f"{new_price:,} تومان",
                        'new_price': f"{new_price:,}",
                        'raw_price': new_price,
                        'diff_percent': product.price_diff_percent,
                        'message': f'نرخ دستی «{product.title}» با موفقیت روی {new_price:,} تومان ثبت شد.',
                    })
                else:
                    product.save()
                    display_p = f"{product.price:,} تومان" if product.price > 0 else "تعیین نشده"
                    return JsonResponse({
                        'status': 'success',
                        'mode': 'manual',
                        'product_id': product.id,
                        'display_text': display_p,
                        'new_price': f"{product.price:,}" if product.price > 0 else "",
                        'raw_price': product.price,
                        'message': f'حالت قیمت‌گذاری «{product.title}» به نرخ دستی تغییر یافت.',
                    })

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    return JsonResponse({'status': 'error', 'message': 'متد نامعتبر'}, status=405)


@login_required
def sync_all_api_view(request):
    """
    One-click trigger to sync all API-connected products with live market rates.
    """
    if not (request.user.is_admin_role or request.user.is_sales_role):
        messages.error(request, "عدم دسترسی مجاز")
        return redirect('market:management_dashboard')

    updated = sync_all_api_products()
    messages.success(request, f"همگام‌سازی وب‌سرویس با موفقیت انجام شد: {updated} محصول متصل به API بروزرسانی شدند.")
    return redirect('market:management_dashboard')


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


# ========================================================
# CMS CONTENT BLOCKS MANAGEMENT (ویرایش تمام بخش‌های محتوایی سایت)
# ========================================================

@login_required
def block_save_view(request, block_id=None):
    """
    Create or edit a dynamic CMS content block.
    """
    if not request.user.has_content_perm():
        messages.error(request, "شما مجوز ویرایش بلاک‌های متنی و محتوای سایت را ندارید.")
        return redirect('market:management_dashboard')

    instance = get_object_or_404(SiteContentBlock, id=block_id) if block_id else None

    if request.method == 'POST':
        form = SiteContentBlockForm(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            block = form.save()
            messages.success(request, f"بلاک محتوایی «{block.title}» با موفقیت ذخیره شد.")
            return redirect('/management/?tab=content_blocks')
        else:
            messages.error(request, f"خطا در فرم بلاک محتوایی: {form.errors.as_text()}")
    
    return redirect('/management/?tab=content_blocks')


@login_required
def block_delete_view(request, block_id):
    """
    Delete a CMS content block.
    """
    if not request.user.has_content_perm():
        messages.error(request, "عدم دسترسی مجاز برای حذف محتوا.")
        return redirect('market:management_dashboard')

    block = get_object_or_404(SiteContentBlock, id=block_id)
    title = block.title
    block.delete()
    messages.success(request, f"بلاک محتوایی «{title}» حذف شد.")
    return redirect('/management/?tab=content_blocks')


# ========================================================
# PRODUCT SPECIFICATIONS & PHOTO MANAGEMENT
# ========================================================

@login_required
def product_edit_view(request, product_id):
    """
    Quick edit product specs, brand, warehouse, and photo from management dashboard.
    """
    if not (request.user.is_admin_role or request.user.has_price_perm()):
        messages.error(request, "شما مجوز ویرایش کالا و تصاویر را ندارید.")
        return redirect('market:management_dashboard')

    prod = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        form = ProductQuickEditForm(request.POST, request.FILES, instance=prod)
        if form.is_valid():
            form.save()
            messages.success(request, f"مشخصات و تصویر محصول «{prod.title}» با موفقیت ذخیره شد.")
            return redirect('/management/?tab=products')
        else:
            messages.error(request, f"خطا در فرم ویرایش محصول: {form.errors.as_text()}")

    return redirect('/management/?tab=products')


# ========================================================
# MEDIA GALLERY ASSETS MANAGEMENT (گالری تصاویر و ویدیوها)
# ========================================================

@login_required
def media_save_view(request, media_id=None):
    """
    Upload and save photos, video clips, or PDF documents.
    """
    if not request.user.has_media_perm():
        messages.error(request, "شما مجوز بارگذاری و مدیریت رسانه‌ها را ندارید.")
        return redirect('market:management_dashboard')

    instance = get_object_or_404(MediaAsset, id=media_id) if media_id else None

    if request.method == 'POST':
        form = MediaAssetForm(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            media = form.save(commit=False)
            if not media.uploaded_by:
                media.uploaded_by = request.user
            media.save()
            messages.success(request, f"فایل «{media.title}» با موفقیت در گالری ثبت شد.")
            return redirect('/management/?tab=media_gallery')
        else:
            messages.error(request, f"خطا در بارگذاری رسانه: {form.errors.as_text()}")

    return redirect('/management/?tab=media_gallery')


@login_required
def media_delete_view(request, media_id):
    """
    Delete a media asset from the gallery.
    """
    if not request.user.has_media_perm():
        messages.error(request, "عدم دسترسی مجاز برای حذف رسانه.")
        return redirect('market:management_dashboard')

    media = get_object_or_404(MediaAsset, id=media_id)
    title = media.title
    media.delete()
    messages.success(request, f"رسانه «{title}» با موفقیت حذف گردید.")
    return redirect('/management/?tab=media_gallery')


# ========================================================
# STAFF PERMISSIONS (تنظیم دقیق سطوح دسترسی کاربران و همکاران)
# ========================================================

@login_required
def staff_permission_save_view(request, user_id):
    """
    Admin updates roles and granular RBAC permission checkboxes for team staff.
    """
    if not request.user.has_user_perm():
        messages.error(request, "تنها مدیران ارشد مجاز به تغییر سطوح دسترسی پرسنل هستند.")
        return redirect('market:management_dashboard')

    target_user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        new_role = request.POST.get('role', target_user.role)
        target_user.role = new_role
        target_user.can_manage_prices = (request.POST.get('can_manage_prices') == 'on')
        target_user.can_manage_content = (request.POST.get('can_manage_content') == 'on')
        target_user.can_manage_media = (request.POST.get('can_manage_media') == 'on')
        target_user.can_view_inquiries = (request.POST.get('can_view_inquiries') == 'on')
        target_user.can_manage_users = (request.POST.get('can_manage_users') == 'on')
        target_user.is_active = (request.POST.get('is_active') == 'on')

        # If admin, ensure staff status and full perms
        if new_role == User.Role.ADMIN:
            target_user.is_staff = True
            target_user.can_manage_prices = True
            target_user.can_manage_content = True
            target_user.can_manage_media = True
            target_user.can_view_inquiries = True
            target_user.can_manage_users = True
        elif new_role in [User.Role.SALES, User.Role.CONTENT]:
            target_user.is_staff = True

        target_user.save()
        messages.success(request, f"حقوق دسترسی کاربر «{target_user.username}» با موفقیت ذخیره شد.")
        return redirect('/management/?tab=staff_perms')

    return redirect('/management/?tab=staff_perms')


# ========================================================
# PUBLIC MEDIA GALLERY PAGE (گالری چندرسانه‌ای کارخانجات مس)
# ========================================================

def gallery_public_view(request):
    """
    Public media showcase of factory lines, copper busbars, wire rods,
    and metallurgical test certificates (Ahan Online & Taban Mes style).
    """
    media_type = request.GET.get('type', 'all')
    tag = request.GET.get('tag', '')

    assets_qs = MediaAsset.objects.filter(is_active=True).order_by('order', '-created_at')

    if media_type != 'all':
        assets_qs = assets_qs.filter(media_type=media_type)
    if tag:
        assets_qs = assets_qs.filter(category_tag=tag)

    # Unique category tags for filtering
    tags = MediaAsset.objects.filter(is_active=True).values_list('category_tag', flat=True).distinct()

    context = {
        'assets': assets_qs,
        'current_type': media_type,
        'current_tag': tag,
        'tags': tags,
        'media_type_choices': MediaAsset.MediaType.choices,
    }
    return render(request, 'market/gallery.html', context)
