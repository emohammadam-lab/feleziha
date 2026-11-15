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
            price=642000,
            price_previous=631000,
            stock_status="موجود",
            warehouse_location="شورآباد",
            density=8.96,
            is_featured=True
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
        self.assertContains(response, "بورس کالای ایران")

    def test_product_detail_view(self):
        response = self.client.get(reverse('market:product_detail', args=[self.product.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Cu-ETP 99.99%")
        self.assertContains(response, "ملی مس")

    def test_news_detail_view(self):
        response = self.client.get(reverse('news:news_detail', args=[self.article.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "تحلیل مس بورس کالا")

    def test_rbac_management_access(self):
        # 1. Unauthenticated user
        response = self.client.get(reverse('market:management_dashboard'))
        self.assertEqual(response.status_code, 302) # Redirects to login

        # 2. Customer user (should be denied management)
        self.client.login(username='customer_test', password='password123')
        response = self.client.get(reverse('market:management_dashboard'), follow=True)
        self.assertContains(response, "شما دسترسی مجاز به پنل مدیریت داخلی را ندارید")

        # 3. Customer cannot access user management
        response = self.client.get(reverse('accounts:user_management'))
        self.assertEqual(response.status_code, 302)

        # 4. Sales user can access management
        self.client.login(username='sales_test', password='password123')
        response = self.client.get(reverse('market:management_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "داشبورد مدیریت و کنترل عملیات")

        # 5. Admin user can access user management
        self.client.login(username='admin_test', password='password123')
        response = self.client.get(reverse('accounts:user_management'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "مدیریت کاربران و سطوح دسترسی سازمانی")

    def test_inquiry_and_proforma_flow(self):
        # Submit an inquiry
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

        # Check proforma invoice view
        invoice_response = self.client.get(reverse('market:proforma_invoice', args=[inquiry.tracking_code]))
        self.assertEqual(invoice_response.status_code, 200)
        self.assertContains(invoice_response, inquiry.tracking_code)
        self.assertContains(invoice_response, "شرکت کابل نوین")
