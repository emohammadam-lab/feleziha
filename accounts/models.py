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

    class Meta:
        verbose_name = 'کاربر'
        verbose_name_plural = 'کاربران'

    def __str__(self):
        full = self.get_full_name()
        display = full if full else self.username
        if self.phone_number:
            return f"{display} ({self.phone_number}) - {self.get_role_display()}"
        return f"{display} - {self.get_role_display()}"

    @property
    def is_admin_role(self):
        return self.is_superuser or self.role == self.Role.ADMIN

    @property
    def is_sales_role(self):
        return self.is_admin_role or self.role == self.Role.SALES

    @property
    def is_content_role(self):
        return self.is_admin_role or self.role == self.Role.CONTENT

    @property
    def is_customer_role(self):
        return self.role == self.Role.CUSTOMER

    def can_manage_prices(self):
        return self.is_admin_role or self.role == self.Role.SALES

    def can_manage_orders(self):
        return self.is_admin_role or self.role == self.Role.SALES

    def can_manage_news(self):
        return self.is_admin_role or self.role == self.Role.CONTENT

    def can_manage_users(self):
        return self.is_admin_role
