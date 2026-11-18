from django.contrib import admin
from .models import Category, SubCategory, Product, PriceHistory, OrderInquiry, SiteContentBlock, MediaAsset


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'order', 'is_active')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('order', 'is_active')
    search_fields = ('name',)


@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'slug', 'order')
    list_filter = ('category',)
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('order',)
    search_fields = ('name', 'category__name')


class PriceHistoryInline(admin.TabularInline):
    model = PriceHistory
    extra = 1
    readonly_fields = ('recorded_at',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'subcategory', 'manufacturer', 'pricing_mode', 'price', 'price_diff_percent', 'stock_status', 'is_featured', 'updated_at')
    list_filter = ('pricing_mode', 'subcategory__category', 'subcategory', 'manufacturer', 'is_featured')
    search_fields = ('title', 'alloy_grade', 'manufacturer', 'dimensions')
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('pricing_mode', 'price', 'is_featured')
    inlines = [PriceHistoryInline]

    def save_model(self, request, obj, form, change):
        if change and 'price' in form.changed_data:
            old_price = form.initial.get('price')
            if old_price:
                obj.price_previous = old_price
                PriceHistory.objects.create(
                    product=obj,
                    price=obj.price,
                    note=f"تغییر توسط کاربر {request.user.username}"
                )
        super().save_model(request, obj, form, change)


@admin.register(PriceHistory)
class PriceHistoryAdmin(admin.ModelAdmin):
    list_display = ('product', 'price', 'note', 'recorded_at')
    list_filter = ('product__subcategory__category', 'recorded_at')
    search_fields = ('product__title', 'note')
    readonly_fields = ('recorded_at',)


@admin.register(OrderInquiry)
class OrderInquiryAdmin(admin.ModelAdmin):
    list_display = ('tracking_code', 'customer_name', 'customer_phone', 'product', 'quantity', 'status', 'final_amount', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('tracking_code', 'customer_name', 'customer_phone', 'destination_city')
    readonly_fields = ('tracking_code', 'created_at', 'updated_at', 'quoted_subtotal', 'tax_amount', 'final_amount')
    list_editable = ('status',)
    fieldsets = (
        ('اطلاعات سفارش‌دهنده', {
            'fields': ('tracking_code', 'user', 'customer_name', 'customer_phone', 'destination_city', 'delivery_address')
        }),
        ('مشخصات کالای درخواستی', {
            'fields': ('product', 'custom_product_title', 'quantity', 'unit', 'description')
        }),
        ('محاسبات مالی و صدور پیش‌فاکتور', {
            'fields': ('quoted_unit_price', 'quoted_subtotal', 'tax_amount', 'final_amount', 'status', 'sales_rep_notes')
        }),
        ('تاریخچه زمانی', {
            'fields': ('created_at', 'updated_at')
        })
    )


@admin.register(SiteContentBlock)
class SiteContentBlockAdmin(admin.ModelAdmin):
    list_display = ('title', 'key', 'section', 'order', 'is_active', 'updated_at')
    list_filter = ('section', 'is_active')
    search_fields = ('title', 'key', 'content')
    list_editable = ('order', 'is_active')
    fieldsets = (
        ('مشخصات بلاک محتوایی', {
            'fields': ('key', 'title', 'subtitle', 'section', 'order', 'is_active')
        }),
        ('متن و مدیا', {
            'fields': ('content', 'image', 'link_url', 'link_text')
        }),
    )


@admin.register(MediaAsset)
class MediaAssetAdmin(admin.ModelAdmin):
    list_display = ('title', 'media_type', 'category_tag', 'is_featured', 'is_active', 'order', 'created_at')
    list_filter = ('media_type', 'is_featured', 'is_active', 'category_tag')
    search_fields = ('title', 'caption', 'category_tag')
    list_editable = ('is_featured', 'is_active', 'order')

