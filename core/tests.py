from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User
from market.models import Category, SubCategory, Product, OrderInquiry
from news.models import NewsCategory, Article


class MetalMarketPlatformTests(TestCase):
    def setUp(self):
        self.client = Client()

        # Create test users with various roles
        self.admin_user = User.objects.create_user(
            username='admin_test',
            password='password123',
            role=User.Role.ADMIN,
            is_staff=True,
            is_superuser=True
        )
        self.sales_user = User.objects.create_user(
            username='sales_test',
            password='password123',
            role=User.Role.SALES,
            is_staff=True
        )
        self.customer_user = User.objects.create_user(
            username='customer_test',
            password='password123',
            role=User.Role.CUSTOMER
        )

        # Create Category, SubCategory, Product
        self.cat_copper = Category.objects.create(name="مس", slug="copper", order=1)
        self.sub_cathode = SubCategory.objects.create(category=self.cat_copper, name="کاتد مس", slug="copper-cathode")
        self.product = Product.objects.create(
            subcategory=self.sub_cathode,
            title="کاتد مس سرچشمه",
            slug="copper-cathode-sarcheshmeh",
            alloy_grade="Cu-ETP 99.99%",
            manufacturer="ملی مس",
            dimensions="۱*۱ متر",
            unit="کیلوگرم",
            pricing_mode=Product.PricingMode.MANUAL,
            price=642000,
            price_previous=631000,
            stock_status="موجود",
            warehouse_location="شورآباد",
            density=8.96,
            is_featured=True
        )

        # Create unpriced product (call for price)
        self.call_product = Product.objects.create(
            subcategory=self.sub_cathode,
            title="مفتول مس ویژه",
            slug="copper-wire-special",
            alloy_grade="Cu-OFE",
            manufacturer="باهنر",
            dimensions="سفارشی",
            unit="کیلوگرم",
            pricing_mode=Product.PricingMode.CALL,
            price=0,
            stock_status="سفارش تولید",
            warehouse_location="کارخانه",
            density=8.96
        )

        # Create News
        self.news_cat = NewsCategory.objects.create(name="بورس کالا", slug="ime")
        self.article = Article.objects.create(
            category=self.news_cat,
            title="تحلیل مس بورس کالا",
            slug="copper-ime-analysis",
            summary="خلاصه گزارش",
            content="متن کامل خبر و تحلیل...",
            source="بورس کالا",
            published_at="2026-11-15T12:00:00Z"
        )

    def test_homepage_renders(self):
        response = self.client.get(reverse('market:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "کاتد مس سرچشمه")
        self.assertContains(response, "محاسبه‌گر آنلاین وزن و بهای فلزات")
        self.assertContains(response, "تماس بگیرید")

    def test_product_detail_view(self):
        response = self.client.get(reverse('market:product_detail', args=[self.product.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Cu-ETP 99.99%")
        self.assertContains(response, "ملی مس")

    def test_call_for_price_rendering(self):
        response = self.client.get(reverse('market:product_detail', args=[self.call_product.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "تماس بگیرید")

    def test_rbac_management_access(self):
        # 1. Unauthenticated user
        response = self.client.get(reverse('market:management_dashboard'))
        self.assertEqual(response.status_code, 302)

        # 2. Customer user (should be denied management)
        self.client.login(username='customer_test', password='password123')
        response = self.client.get(reverse('market:management_dashboard'), follow=True)
        self.assertContains(response, "شما دسترسی مجاز به پنل مدیریت را ندارید")

        # 3. Customer cannot access user management
        response = self.client.get(reverse('accounts:user_management'))
        self.assertEqual(response.status_code, 302)

        # 4. Sales user can access management
        self.client.login(username='sales_test', password='password123')
        response = self.client.get(reverse('market:management_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "میز مدیریت نرخ‌گذاری و سفارشات")

        # 5. Admin user can access user management
        self.client.login(username='admin_test', password='password123')
        response = self.client.get(reverse('accounts:user_management'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "مدیریت کاربران و سطوح دسترسی سازمانی")

    def test_pricing_mode_switching_api(self):
        self.client.login(username='sales_test', password='password123')

        # Switch to CALL
        res_call = self.client.post(reverse('market:fast_price_update'), {
            'product_id': self.product.id,
            'pricing_mode': 'call',
        })
        self.assertEqual(res_call.status_code, 200)
        self.assertEqual(res_call.json()['mode'], 'call')

        # Switch to AUTO_API
        res_api = self.client.post(reverse('market:fast_price_update'), {
            'product_id': self.product.id,
            'pricing_mode': 'api',
        })
        self.assertEqual(res_api.status_code, 200)
        self.assertEqual(res_api.json()['mode'], 'api')
        self.assertTrue(self.product.price > 0)

        # Switch to MANUAL with English numerals
        res_manual = self.client.post(reverse('market:fast_price_update'), {
            'product_id': self.product.id,
            'pricing_mode': 'manual',
            'new_price': '680000'
        })
        self.assertEqual(res_manual.status_code, 200)
        self.assertEqual(res_manual.json()['mode'], 'manual')

        # Test Persian numerals with commas input sanitization
        res_persian = self.client.post(reverse('market:fast_price_update'), {
            'product_id': self.product.id,
            'pricing_mode': 'manual',
            'new_price': '۶۹۵,۰۰۰'
        })
        self.assertEqual(res_persian.status_code, 200)
        self.product.refresh_from_db()
        self.assertEqual(self.product.price, 695000)

    def test_inquiry_and_proforma_flow(self):
        post_data = {
            'product': self.product.id,
            'quantity': 2.5,
            'unit': 'تن',
            'customer_name': 'شرکت کابل نوین',
            'customer_phone': '09121234567',
            'destination_city': 'قزوین',
            'delivery_address': 'شهرک صنعتی کاسپین',
            'description': 'تحویل فوری'
        }
        response = self.client.post(reverse('market:inquiry_create'), post_data, follow=True)
        self.assertEqual(response.status_code, 200)

        inquiry = OrderInquiry.objects.filter(customer_phone='09121234567').first()
        self.assertIsNotNone(inquiry)
        self.assertTrue(inquiry.tracking_code.startswith('FLZ-'))

        invoice_response = self.client.get(reverse('market:proforma_invoice', args=[inquiry.tracking_code]))
        self.assertEqual(invoice_response.status_code, 200)
        self.assertContains(invoice_response, inquiry.tracking_code)
