import uuid
from django.db import models
from django.conf import settings


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="نام دسته‌بندی")
    slug = models.SlugField(max_length=100, unique=True, allow_unicode=True, verbose_name="شناسه یکتا (Slug)")
    icon = models.CharField(max_length=50, default="layers", verbose_name="آیکون یا نماد")
    description = models.TextField(blank=True, verbose_name="توضیحات دسته‌بندی")
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب نمایش")
    is_active = models.BooleanField(default=True, verbose_name="فعال")

    class Meta:
        verbose_name = "دسته‌بندی اصلی فلزات"
        verbose_name_plural = "دسته‌بندی‌های اصلی فلزات"
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class SubCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories', verbose_name="دسته‌بندی والد")
    name = models.CharField(max_length=100, verbose_name="نام زیردسته")
    slug = models.SlugField(max_length=100, unique=True, allow_unicode=True, verbose_name="شناسه یکتا (Slug)")
    description = models.TextField(blank=True, verbose_name="توضیحات")
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب نمایش")

    class Meta:
        verbose_name = "زیردسته محصول"
        verbose_name_plural = "زیردسته‌های محصولات"
        ordering = ['order', 'name']

    def __str__(self):
        return f"{self.category.name} > {self.name}"


class Product(models.Model):
    subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE, related_name='products', verbose_name="زیردسته")
    title = models.CharField(max_length=200, verbose_name="عنوان محصول")
    slug = models.SlugField(max_length=200, unique=True, allow_unicode=True, verbose_name="شناسه یکتا (Slug)")
    alloy_grade = models.CharField(max_length=100, verbose_name="گرید / آلیاژ / استاندارد", help_text="مثال: Cu-ETP (99.99%) یا 6063 یا ST37")
    manufacturer = models.CharField(max_length=120, verbose_name="تولیدکننده / برند", help_text="مثال: مس سرچشمه، ایرالکو، ذوب آهن اصفهان")
    dimensions = models.CharField(max_length=150, verbose_name="ابعاد / سایز / ضخامت", help_text="مثال: قطر ۸ میلیمتر، شاخه ۶ متری، ضخامت ۲ میل")
    unit = models.CharField(max_length=30, default="کیلوگرم", verbose_name="واحد قیمت‌گذاری")
    
    price = models.BigIntegerField(verbose_name="قیمت روز (تومان)")
    price_previous = models.BigIntegerField(default=0, verbose_name="قیمت روز قبل (تومان)")
    min_order = models.CharField(max_length=80, default="۱ تن", verbose_name="حداقل میزان سفارش")
    
    stock_status = models.CharField(
        max_length=50,
        default="موجود در انبار تهران",
        verbose_name="وضعیت موجودی و بارگیری"
    )
    warehouse_location = models.CharField(
        max_length=100,
        default="شورآباد، تهران",
        verbose_name="محل انبار / مبدأ بارگیری"
    )
    description = models.TextField(blank=True, verbose_name="توضیحات و مشخصات فنی")
    standards = models.CharField(max_length=200, blank=True, verbose_name="استانداردهای بین‌المللی", help_text="مثال: ASTM B115, DIN 1787")
    density = models.FloatField(default=8.96, verbose_name="چگالی (g/cm³)", help_text="مس: 8.96، آلومینیوم: 2.70، آهن: 7.85")
    
    is_featured = models.BooleanField(default=False, verbose_name="نمایش در تابلو ویژه صفحه نخست")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ثبت")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="آخرین بروزرسانی قیمت")

    class Meta:
        verbose_name = "محصول فلزی"
        verbose_name_plural = "محصولات فلزی"
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.title} - {self.manufacturer}"

    @property
    def price_diff(self):
        if self.price_previous and self.price_previous > 0:
            return self.price - self.price_previous
        return 0

    @property
    def price_diff_percent(self):
        if self.price_previous and self.price_previous > 0:
            diff = self.price - self.price_previous
            return round((diff / self.price_previous) * 100, 2)
        return 0.0

    @property
    def is_price_up(self):
        return self.price_diff > 0

    @property
    def is_price_down(self):
        return self.price_diff < 0


class PriceHistory(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='price_history', verbose_name="محصول")
    price = models.BigIntegerField(verbose_name="قیمت ثبت شده (تومان)")
    note = models.CharField(max_length=255, blank=True, verbose_name="علت تغییر یا نوسان قیمت")
    recorded_at = models.DateTimeField(auto_now_add=True, verbose_name="زمان ثبت")

    class Meta:
        verbose_name = "تاریخچه نوسان قیمت"
        verbose_name_plural = "تاریخچه نوسانات قیمت"
        ordering = ['-recorded_at']

    def __str__(self):
        return f"{self.product.title} - {self.price:,} تومان در {self.recorded_at.strftime('%Y/%m/%d')}"


class OrderInquiry(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'در حال بررسی کارشناس فروش'
        QUOTED = 'quoted', 'پیش‌فاکتور صادر شد'
        APPROVED = 'approved', 'تأیید مالی و آماده بارگیری'
        DISPATCHED = 'dispatched', 'بارگیری و ارسال شد'
        COMPLETED = 'completed', 'تحویل نهایی گردید'
        CANCELLED = 'cancelled', 'انصراف / لغو شده'

    tracking_code = models.CharField(max_length=20, unique=True, editable=False, verbose_name="کد رهگیری استعلام")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders',
        verbose_name="کاربر ثبت‌کننده"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders',
        verbose_name="محصول انتخابی"
    )
    custom_product_title = models.CharField(max_length=200, blank=True, verbose_name="نام کالای درخواستی (در صورت نبود در لیست)")
    
    quantity = models.FloatField(verbose_name="مقدار درخواستی")
    unit = models.CharField(max_length=30, default="کیلوگرم", verbose_name="واحد سنجش")
    
    customer_name = models.CharField(max_length=120, verbose_name="نام خریدار / شرکت")
    customer_phone = models.CharField(max_length=20, verbose_name="شماره تماس")
    destination_city = models.CharField(max_length=100, verbose_name="شهر و مقصد تحویل بار")
    delivery_address = models.TextField(blank=True, verbose_name="آدرس دقیق تخلیه بار")
    description = models.TextField(blank=True, verbose_name="توضیحات و نیازمندی‌های باربری / بسته‌بندی")

    # Financial / Quotation details
    quoted_unit_price = models.BigIntegerField(default=0, verbose_name="نرخ واحد پیش‌فاکتور (تومان)")
    quoted_subtotal = models.BigIntegerField(default=0, verbose_name="مبلغ پایه (تومان)")
    tax_amount = models.BigIntegerField(default=0, verbose_name="مالیات بر ارزش افزوده (۱۰٪)")
    final_amount = models.BigIntegerField(default=0, verbose_name="مبلغ نهایی پیش‌فاکتور (تومان)")
    
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name="وضعیت سفارش"
    )
    sales_rep_notes = models.TextField(blank=True, verbose_name="یادداشت و شرایط کارشناس فروش")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="زمان ثبت استعلام")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="آخرین وضعیت")

    class Meta:
        verbose_name = "استعلام و سفارش خرید"
        verbose_name_plural = "استعلام‌ها و سفارشات خرید"
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.tracking_code:
            self.tracking_code = f"FLZ-{uuid.uuid4().hex[:6].upper()}"
        if self.quoted_unit_price > 0 and self.quantity > 0:
            self.quoted_subtotal = int(self.quoted_unit_price * self.quantity)
            self.tax_amount = int(self.quoted_subtotal * 0.10)
            self.final_amount = self.quoted_subtotal + self.tax_amount
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.tracking_code} - {self.customer_name} ({self.get_status_display()})"
