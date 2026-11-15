from django.db import models
from django.conf import settings


class NewsCategory(models.Model):
    name = models.CharField(max_length=100, verbose_name="نام حوزه خبری")
    slug = models.SlugField(max_length=100, unique=True, allow_unicode=True, verbose_name="شناسه یکتا (Slug)")
    description = models.TextField(blank=True, verbose_name="توضیح")

    class Meta:
        verbose_name = "دسته‌بندی خبر"
        verbose_name_plural = "دسته‌بندی‌های اخبار"

    def __str__(self):
        return self.name


class Article(models.Model):
    category = models.ForeignKey(NewsCategory, on_delete=models.CASCADE, related_name='articles', verbose_name="حوزه خبری")
    title = models.CharField(max_length=250, verbose_name="تیتر خبر")
    slug = models.SlugField(max_length=250, unique=True, allow_unicode=True, verbose_name="شناسه یکتا (Slug)")
    summary = models.TextField(verbose_name="خلاصه / روتیتر خبر")
    content = models.TextField(verbose_name="متن کامل خبر و تحلیل")
    source = models.CharField(max_length=150, default="بورس کالای ایران / LME", verbose_name="منبع موثق خبر")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='articles',
        verbose_name="نویسنده / تحلیل‌گر"
    )
    image_badge = models.CharField(
        max_length=50,
        default="تحلیل بازار",
        verbose_name="برچسب موضوعی روی تصویر"
    )
    views_count = models.PositiveIntegerField(default=142, verbose_name="تعداد بازدید")
    is_breaking = models.BooleanField(default=False, verbose_name="خبر ویژه / فوری")
    published_at = models.DateTimeField(verbose_name="تاریخ و ساعت انتشار")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "خبر و تحلیل بازار"
        verbose_name_plural = "اخبار و تحلیل‌های بازار"
        ordering = ['-published_at']

    def __str__(self):
        return self.title
