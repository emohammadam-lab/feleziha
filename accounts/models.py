from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'admin', 'مدیر ارشد سیستم'
        SALES = 'sales', 'کارشناس فروش و قیمت‌گذاری'
        CONTENT = 'content', 'کارشناس محتوا و اخبار'
        CUSTOMER = 'customer', 'مشتری / خریدار'

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.CUSTOMER,
        verbose_name='نقش کاربری'
    )
    phone_number = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        unique=True,
        verbose_name='شماره تماس همراه'
    )
    company_name = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        verbose_name='نام شرکت / بنگاه'
    )
    national_id = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='کد ملی / شناسه ملی'
    )
    economic_code = models.CharField(
        max_length=25,
        blank=True,
        null=True,
        verbose_name='کد اقتصادی (برای فاکتور رسمی)'
    )
    address = models.TextField(
        blank=True,
        null=True,
        verbose_name='نشانی و آدرس تحویل بار'
    )
    postal_code = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        verbose_name='کد پستی'
    )
    is_verified = models.BooleanField(
        default=False,
        verbose_name='تأیید مدارک رسمی'
    )

    # Granular Permissions & Role-Based Access Control (RBAC)
    can_manage_prices = models.BooleanField(
        default=False,
        verbose_name='تغییر نرخ و قیمت‌گذاری مس'
    )
    can_manage_content = models.BooleanField(
        default=False,
        verbose_name='ویرایش بلاک‌های متنی و محتوای سایت'
    )
    can_manage_media = models.BooleanField(
        default=False,
        verbose_name='بارگذاری و مدیریت گالری تصاویر و ویدیوها'
    )
    can_view_inquiries = models.BooleanField(
        default=False,
        verbose_name='مشاهده سفارشات و صدور پیش‌فاکتورها'
    )
    can_manage_users = models.BooleanField(
        default=False,
        verbose_name='مدیریت پرسنل و دسترسی‌ها'
    )

    class Meta:
        verbose_name = 'کاربر'
        verbose_name_plural = 'کاربران'

    def __str__(self):
        full = self.get_full_name()
        display = full if full else self.username
        if self.phone_number:
            return f"{display} ({self.phone_number}) - {self.get_role_display()}"
        return f"{display} - {self.get_role_display()}"

    def save(self, *args, **kwargs):
        # Superadmin / Admin automatically receives full permissions
        if self.is_superuser or self.role == self.Role.ADMIN:
            self.is_staff = True
            self.can_manage_prices = True
            self.can_manage_content = True
            self.can_manage_media = True
            self.can_view_inquiries = True
            self.can_manage_users = True
        elif self.role == self.Role.SALES:
            self.is_staff = True
            if not self.pk:
                self.can_manage_prices = True
                self.can_view_inquiries = True
        elif self.role == self.Role.CONTENT:
            self.is_staff = True
            if not self.pk:
                self.can_manage_content = True
                self.can_manage_media = True
        super().save(*args, **kwargs)

    @property
    def is_admin_role(self):
        return self.is_superuser or self.role == self.Role.ADMIN

    @property
    def is_sales_role(self):
        return self.is_admin_role or self.role == self.Role.SALES or bool(self.can_manage_prices)

    @property
    def is_content_role(self):
        return self.is_admin_role or self.role == self.Role.CONTENT or bool(self.can_manage_content)

    @property
    def is_customer_role(self):
        return self.role == self.Role.CUSTOMER

    def has_price_perm(self):
        return self.is_superuser or self.is_admin_role or bool(self.can_manage_prices) or self.role == self.Role.SALES

    def has_content_perm(self):
        return self.is_superuser or self.is_admin_role or bool(self.can_manage_content) or self.role == self.Role.CONTENT

    def has_media_perm(self):
        return self.is_superuser or self.is_admin_role or bool(self.can_manage_media) or self.role == self.Role.CONTENT

    def has_inquiry_perm(self):
        return self.is_superuser or self.is_admin_role or bool(self.can_view_inquiries) or self.role == self.Role.SALES

    def has_user_perm(self):
        return self.is_superuser or self.is_admin_role or bool(self.can_manage_users)

    def can_manage_orders(self):
        return self.has_inquiry_perm()

    def can_manage_news(self):
        return self.has_content_perm()
