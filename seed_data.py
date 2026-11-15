import os
import django
from datetime import datetime, timedelta
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from accounts.models import User
from market.models import Category, SubCategory, Product, PriceHistory, OrderInquiry
from news.models import NewsCategory, Article

def seed_database():
    print("Clearing existing data...")
    Product.objects.all().delete()
    SubCategory.objects.all().delete()
    Category.objects.all().delete()
    Article.objects.all().delete()
    NewsCategory.objects.all().delete()
    OrderInquiry.objects.all().delete()

    print("Creating user accounts with various roles...")
    # 1. Admin
    admin_user, _ = User.objects.get_or_create(
        username='admin',
        defaults={
            'first_name': 'مهندس علیرضا',
            'last_name': 'رستگار',
            'email': 'admin@felezonline.com',
            'role': User.Role.ADMIN,
            'phone_number': '09121111111',
            'company_name': 'سامانه معاملات فلز آنلاین',
            'is_staff': True,
            'is_superuser': True,
            'is_verified': True
        }
    )
    admin_user.set_password('admin12345')
    admin_user.save()

    # 2. Sales Manager
    sales_user, _ = User.objects.get_or_create(
        username='sales_manager',
        defaults={
            'first_name': 'رضا',
            'last_name': 'کاظمی',
            'email': 'sales@felezonline.com',
            'role': User.Role.SALES,
            'phone_number': '09122222222',
            'company_name': 'دپارتمان فروش و استعلام قیمت',
            'is_staff': True,
            'is_verified': True
        }
    )
    sales_user.set_password('sales12345')
    sales_user.save()

    # 3. Content Editor
    content_user, _ = User.objects.get_or_create(
        username='news_editor',
        defaults={
            'first_name': 'سارا',
            'last_name': 'محمدی',
            'email': 'editor@felezonline.com',
            'role': User.Role.CONTENT,
            'phone_number': '09123333333',
            'company_name': 'واحد تحلیل بازار و اخبار',
            'is_staff': True,
            'is_verified': True
        }
    )
    content_user.set_password('editor12345')
    content_user.save()

    # 4. Customer Buyer
    buyer_user, _ = User.objects.get_or_create(
        username='buyer1',
        defaults={
            'first_name': 'حمید',
            'last_name': 'فرهادی',
            'email': 'buyer@example.com',
            'role': User.Role.CUSTOMER,
            'phone_number': '09124444444',
            'company_name': 'صنایع الکتریک پویان البرز',
            'national_id': '0019876543',
            'economic_code': '411589321456',
            'address': 'شهرک صنعتی کاسپین، بلوار صنعت، پلاک ۲۴',
            'is_verified': True
        }
    )
    buyer_user.set_password('buyer12345')
    buyer_user.save()

    print("Creating Categories & Subcategories...")
    # Categories
    cat_copper = Category.objects.create(
        name="مس و آلیاژها",
        slug="copper",
        icon="copper-wire",
        description="قیمت لحظه‌ای انواع کاتد، مفتول، لوله، ورق و شمش مس سرچشمه و باهنر",
        order=1
    )
    cat_aluminum = Category.objects.create(
        name="آلومینیوم صنعتی",
        slug="aluminum",
        icon="aluminum-ingot",
        description="انواع شمش خالص، بیلت آلیاژی، ورق و پروفیل آلومینیوم ایرالکو و سالکو",
        order=2
    )
    cat_steel = Category.objects.create(
        name="آهن و فولاد",
        slug="steel",
        icon="steel-beam",
        description="قیمت روز میلگرد، تیرآهن، ورق سیاه و لوله قوطی کارخانجات معتبر فولادی",
        order=3
    )
    cat_other = Category.objects.create(
        name="سایر فلزات پایه (روی، سرب، برنج)",
        slug="other-metals",
        icon="other-metals",
        description="شمش روی خالص کالسیمین، شمش سرب خالص و شمش برنجی با تضمین آنالیز",
        order=4
    )

    # Subcategories for Copper
    sub_cathode = SubCategory.objects.create(
        category=cat_copper,
        name="کاتد مس (Copper Cathode)",
        slug="copper-cathode",
        description="کاتد مس درجه ۱ با درجه خلوص ۹۹.۹۹ درصد عرضه شده در بورس کالا",
        order=1
    )
    sub_wire = SubCategory.objects.create(
        category=cat_copper,
        name="مفتول و راد مس (Wire Rod)",
        slug="copper-wire-rod",
        description="مفتول مس ۸ میلیمتر مناسب خطوط کشش و کابل‌سازی و الکتروموتور",
        order=2
    )
    sub_tube = SubCategory.objects.create(
        category=cat_copper,
        name="لوله مسی (Tubes & Coils)",
        slug="copper-tubes",
        description="انواع لوله مسی کلاف، شاخه، مویی تیپ L و K جهت صنایع برودتی و حرارتی",
        order=3
    )
    sub_sheet = SubCategory.objects.create(
        category=cat_copper,
        name="ورق و تسمه مسی",
        slug="copper-sheet-strip",
        description="ورق مس و تسمه با بالاترین رسانایی الکتریکی و حرارتی صنایع تابلوسازی",
        order=4
    )

    # Subcategories for Aluminum
    sub_al_ingot = SubCategory.objects.create(
        category=cat_aluminum,
        name="شمش آلومینیوم (Ingots & Billets)",
        slug="aluminum-ingot",
        description="شمش آلومینیوم خلوص ۹۹.۷٪ و بیلت‌های اکستروژن ۶۰۶۳ ایرالکو و سالکو",
        order=1
    )
    sub_al_sheet = SubCategory.objects.create(
        category=cat_aluminum,
        name="ورق آلومینیوم",
        slug="aluminum-sheet",
        description="ورق‌های ساده، آجدار و فرم‌دار در آلیاژهای ۱۰۵۰، ۳۱۰۵، ۵۰۸۳ و ۶۰۶۱",
        order=2
    )
    sub_al_profile = SubCategory.objects.create(
        category=cat_aluminum,
        name="پروفیل و لوله آلومینیوم",
        slug="aluminum-profile",
        description="پروفیل‌های اختصاصی صنعتی، شیاردار مهندسی و مقاطع ساختمانی",
        order=3
    )

    # Subcategories for Steel
    sub_rebar = SubCategory.objects.create(
        category=cat_steel,
        name="میلگرد آجدار و ساده",
        slug="steel-rebar",
        description="میلگرد استاندارد A3 و A2 کارخانجات ذوب آهن، نیشابور، میانه و بناب",
        order=1
    )
    sub_beam = SubCategory.objects.create(
        category=cat_steel,
        name="تیرآهن و هاش (IPE / IPB)",
        slug="steel-beam",
        description="تیرآهن بال نیم پهن و هاش سنگین و سبک ذوب آهن اصفهان",
        order=2
    )
    sub_black_sheet = SubCategory.objects.create(
        category=cat_steel,
        name="ورق سیاه و روغنی",
        slug="steel-sheets",
        description="ورق سیاه ST37 فولاد مبارکه و اکسین اهواز، ورق روغنی و گالوانیزه",
        order=3
    )

    # Subcategories for Other Metals
    sub_zinc = SubCategory.objects.create(
        category=cat_other,
        name="شمش روی (Zinc)",
        slug="zinc-ingot",
        description="شمش روی درجه ۱ با عیار ۹۹.۹۹ درصد کالسیمین و روی زنجان",
        order=1
    )
    sub_brass = SubCategory.objects.create(
        category=cat_other,
        name="شمش و مقاطع برنجی",
        slug="brass-alloys",
        description="شمش و میلگرد برنجی خوش‌تراش آلیاژ MS58 مناسب تراشکاری و شیرآلات",
        order=2
    )

    print("Creating realistic Products & Prices...")
    # Copper products
    p1 = Product.objects.create(
        subcategory=sub_cathode,
        title="کاتد مس سرچشمه (خلوص ۹۹.۹۹٪)",
        slug="copper-cathode-sarcheshmeh",
        alloy_grade="Cu-ETP (ASTM B115 Grade 1)",
        manufacturer="شرکت ملی صنایع مس ایران (سرچشمه)",
        dimensions="ابعاد ورق ۱*۱ متر، وزن تقریبی هر برگ ۱۰۰ کیلو",
        unit="کیلوگرم",
        price=642000,
        price_previous=631000,
        min_order="۱ تن",
        stock_status="موجود در انبار تهران و سرچشمه",
        warehouse_location="انبار مرکزی شورآباد / کارخانه رفسنجان",
        standards="ASTM B115 Grade 1, BS EN 1978",
        density=8.96,
        is_featured=True,
        description="کاتد مس پالایش شده با خلوص ۹۹.۹۹٪، مبنای اصلی قیمت‌گذاری کلیه صنایع مس در کشور و بورس کالای ایران. دارای آنالیز رسمی آزمایشگاهی مس سرچشمه."
    )

    p2 = Product.objects.create(
        subcategory=sub_cathode,
        title="کاتد مس مجتمع مس بابک",
        slug="copper-cathode-babak",
        alloy_grade="Cu-ETP خلوص 99.99%",
        manufacturer="مس بابک ایرانیان",
        dimensions="برگ کاتد استاندارد ابعاد ۹۵*۹۵ سانتیمتر",
        unit="کیلوگرم",
        price=638500,
        price_previous=639000,
        min_order="۲ تن",
        stock_status="تحویل درب کارخانه شهربابک",
        warehouse_location="مجتمع مس بابک (شهربابک کرمان)",
        standards="ASTM B115",
        density=8.96,
        is_featured=True,
        description="کاتد مس تولید شده به روش بایولیچینگ سازگار با محیط زیست، با بالاترین استاندارد کیفی جهت مصارف سیم و کابل‌سازی و صنایع الکترونیک."
    )

    p3 = Product.objects.create(
        subcategory=sub_wire,
        title="مفتول مس قطر ۸ میلیمتر (پیوسته)",
        slug="copper-wire-rod-8mm",
        alloy_grade="Cu-OFE / Cu-ETP اکسیژن آزاد",
        manufacturer="دنیای مس کاشان / گیل‌راد",
        dimensions="قطر ۸.۰ میلیمتر (کلاف ۵ تن)",
        unit="کیلوگرم",
        price=664000,
        price_previous=652000,
        min_order="۱ کلاف (حدود ۲.۵ الی ۵ تن)",
        stock_status="موجود در انبار تهران",
        warehouse_location="شورآباد تهران",
        standards="ASTM B49, EN 1977",
        density=8.96,
        is_featured=True,
        description="مفتول مس کستینگ پیوسته گرید هادی الکتریسیته (IACS بالاتر از ۱۰۱٪) با انعطاف‌پذیری استثنایی جهت خطوط کشش ریز و متوسط."
    )

    p4 = Product.objects.create(
        subcategory=sub_tube,
        title="لوله مسی کلاف سایز ۳/۸ اینچ (ضخامت ۰.۷۵)",
        slug="copper-tube-coil-3-8",
        alloy_grade="Cu-DHP آلیاژ C12200 فسفردار",
        manufacturer="صنایع مس شهید باهنر / مهر اصل",
        dimensions="سایز 3/8 اینچ (قطر 9.52mm)، ضخامت 0.75mm کلاف ۱۵ متری",
        unit="شاخه/کلاف",
        price=715000,
        price_previous=702000,
        min_order="۵ کلاف",
        stock_status="موجود انبار تهران",
        warehouse_location="بازار آهن شادآباد، تهران",
        standards="ASTM B280, EN 12735-1",
        density=8.94,
        is_featured=True,
        description="لوله مسی نرم آنیل شده بدون درز (Seamless) دارای بالاترین مقاومت در برابر فشار و گاز مبرد جهت سیستم‌های کولر گازی و چیلر."
    )

    p5 = Product.objects.create(
        subcategory=sub_sheet,
        title="ورق مسی شهید باهنر ضخامت ۲ میلیمتر",
        slug="copper-sheet-bahonar-2mm",
        alloy_grade="Cu-ETP نیمه‌سخت (Half Hard)",
        manufacturer="صنایع مس شهید باهنر کرمان",
        dimensions="ابعاد ۲۰۰۰*۱۰۰۰ میلیمتر (۲*۱ متر)، ضخامت ۲ میل",
        unit="کیلوگرم",
        price=689000,
        price_previous=689000,
        min_order="۱ شیت (حدود ۳۶ کیلوگرم)",
        stock_status="موجود انبار تهران",
        warehouse_location="شورآباد تهران",
        standards="DIN 1787, ASTM B152",
        density=8.96,
        is_featured=False,
        description="ورق مس با سطحی کاملا صاف و پولیش خورده، بسیار مناسب برای ساخت شینه‌های تابلو برق فشار قوی و مخازن صنعتی انتقال حرارت."
    )

    # Aluminum products
    p6 = Product.objects.create(
        subcategory=sub_al_ingot,
        title="شمش آلومینیوم ۹۹.۷ خالص ایرالکو",
        slug="aluminum-ingot-997-iralco",
        alloy_grade="خلوص ۹۹.۷٪ گرید A7",
        manufacturer="آلومینیوم ایران (ایرالکو اراک)",
        dimensions="شمش ۵۰ پوندی (حدود ۲۲.۵ کیلوگرم)",
        unit="کیلوگرم",
        price=238000,
        price_previous=232000,
        min_order="۱ تن",
        stock_status="تحویل بورس کالا / انبار اراک و تهران",
        warehouse_location="انبار تهران / کارخانه اراک",
        standards="ASTM B179, BS 1490",
        density=2.70,
        is_featured=True,
        description="شمش استاندارد آلومینیوم خالص ایرالکو تولیدی با فرآیند الکترولیز پیشرفته، دارای کمترین ناخالصی آهن و سیلیسیوم، مبنای آلیاژسازی صنایع."
    )

    p7 = Product.objects.create(
        subcategory=sub_al_ingot,
        title="شمش آلومینیوم سالکو (جنوب)",
        slug="aluminum-ingot-salco",
        alloy_grade="خلوص ۹۹.۸٪ فوق ممتاز",
        manufacturer="آلومینیوم جنوب (SALCO)",
        dimensions="شمش T-Bar و استاندارد ۵۰ پوندی",
        unit="کیلوگرم",
        price=239500,
        price_previous=235000,
        min_order="۵ تن",
        stock_status="آماده تحویل در بندر پارسیان و انبار مرکزی",
        warehouse_location="مجتمع سالکو لامرد / بندر پارسیان",
        standards="ISO 9001, ASTM B179",
        density=2.70,
        is_featured=False,
        description="تولید شده در مدرن‌ترین خط احیای آلومینیوم کشور در منطقه ویژه اقتصادی لامرد با استفاده از برق پایدار و تکنولوژی ۴۳۰ کیلوآمپر."
    )

    p8 = Product.objects.create(
        subcategory=sub_al_sheet,
        title="ورق آلومینیوم ۲ میل ساده آلیاژ ۱۰۵۰ نورد اراک",
        slug="aluminum-sheet-1050-2mm",
        alloy_grade="Al 1050 H14 (نرم نیمه‌سخت)",
        manufacturer="شرکت آلومینیوم نورد اراک",
        dimensions="ابعاد ۲۰۰۰*۱۰۰۰ میلیمتر، ضخامت ۲ میلیمتر",
        unit="کیلوگرم",
        price=282000,
        price_previous=278000,
        min_order="۱۰۰ کیلوگرم",
        stock_status="موجود انبار شادآباد",
        warehouse_location="شادآباد تهران",
        standards="EN AW-1050A",
        density=2.71,
        is_featured=True,
        description="ورق آلومینیوم خالص فرم‌پذیری عالی، مقاومت بسیار بالا در برابر خوردگی، مناسب برای نماسازی ساختمان، لوازم خانگی و تابلوهای صنعتی."
    )

    # Steel products
    p9 = Product.objects.create(
        subcategory=sub_rebar,
        title="میلگرد ۱۴ آجدار A3 ذوب آهن اصفهان",
        slug="rebar-14-a3-zobahan",
        alloy_grade="فولاد آجدار جناقی A3 (آج 400)",
        manufacturer="ذوب آهن اصفهان (علامت اختصاری ESCO)",
        dimensions="سایز ۱۴ میلیمتر، طول شاخه ۱۲ متر",
        unit="کیلوگرم",
        price=32400,
        price_previous=31800,
        min_order="۲ تن (یک بندیل)",
        stock_status="موجود انبار تهران و بارگیری درب کارخانه اصفهان",
        warehouse_location="شورآباد / کارخانه ذوب آهن",
        standards="استاندارد ملی ایران 3132",
        density=7.85,
        is_featured=True,
        description="معتبرترین میلگرد ساختمانی کشور با مشخصات تنش تسلیم ۴۰۰۰ کیلوگرم بر سانتیمتر مربع و استحکام کششی ۶۰۰۰. دارای حک آرم ESCO روی بدنه شاخه."
    )

    p10 = Product.objects.create(
        subcategory=sub_beam,
        title="تیرآهن ۱۸ ذوب آهن اصفهان (IPE)",
        slug="steel-beam-18-zobahan",
        alloy_grade="ST37-2 فولاد ساختمانی عمومی",
        manufacturer="ذوب آهن اصفهان",
        dimensions="سایز ۱۸، طول شاخه ۱۲ متر (وزن هر شاخه حدود ۲۲۵ کیلو)",
        unit="کیلوگرم",
        price=34600,
        price_previous=34900,
        min_order="۱ شاخه",
        stock_status="موجود انبار آهن‌مکان تهران",
        warehouse_location="انبار آهن مکان، تهران",
        standards="DIN 1025-5, EN 10034",
        density=7.85,
        is_featured=False,
        description="تیرآهن معمولی نیم‌پهن با بالاترین دقت وزنی منطبق بر جدول اشتال آلمان جهت اجرای ستون‌ها، خرپاها و تیرهای اصلی سازه‌های فلزی."
    )

    p11 = Product.objects.create(
        subcategory=sub_black_sheet,
        title="ورق سیاه ۲ میل فولاد مبارکه اصفهان (رول)",
        slug="steel-sheet-black-2mm-mobarakeh",
        alloy_grade="ST37-2 نورد گرم (Hot Rolled)",
        manufacturer="فولاد مبارکه اصفهان",
        dimensions="عرض ۱۲۵۰ میلیمتر، ضخامت ۲ میلیمتر، به صورت رول یا شیت برش خورده",
        unit="کیلوگرم",
        price=37500,
        price_previous=36900,
        min_order="۱ تن",
        stock_status="موجود انبار تهران",
        warehouse_location="انبار شادآباد تهران",
        standards="DIN 17100, EN 10025",
        density=7.85,
        is_featured=True,
        description="ورق سیاه فولاد مبارکه اصفهان با یکنواختی ضخامت در کل طول رول، قابلیت جوشکاری و فرم‌دهی عالی جهت مصارف ماشین‌سازی و تانکرسازی."
    )

    # Zinc & Brass products
    p12 = Product.objects.create(
        subcategory=sub_zinc,
        title="شمش روی ۹۹.۹۹٪ کالسیمین زنجان",
        slug="zinc-ingot-9999-calcimin",
        alloy_grade="SHG (Special High Grade 99.99%)",
        manufacturer="شرکت کالسیمین (زنجان)",
        dimensions="قالب شمش ۲۵ کیلوگرمی استاندارد",
        unit="کیلوگرم",
        price=268000,
        price_previous=264000,
        min_order="۵۰۰ کیلوگرم",
        stock_status="موجود انبار زنجان و تهران",
        warehouse_location="انبار مرکزی زنجان",
        standards="ASTM B6",
        density=7.14,
        is_featured=False,
        description="شمش روی با خلوص فوق‌العاده بالا به روش الکترووینینگ در مجتمع دندی زنجان، ماده اولیه اصلی خطوط گالوانیزاسیون لوله و ورق و ساخت آلیاژ زاماک."
    )

    print("Adding historical price points for charts...")
    now = timezone.now()
    history_entries = [
        (p1, [615000, 622000, 628000, 631000, 642000]),
        (p3, [635000, 641000, 648000, 652000, 664000]),
        (p6, [226000, 229000, 230000, 232000, 238000]),
        (p9, [30500, 31000, 31400, 31800, 32400]),
    ]
    for prod, prices in history_entries:
        for idx, prc in enumerate(prices):
            PriceHistory.objects.create(
                product=prod,
                price=prc,
                note=f"ثبت نرخ روز {idx + 1}",
                recorded_at=now - timedelta(days=5 - idx)
            )

    print("Creating real, authentic industry news...")
    news_cat_ime = NewsCategory.objects.create(
        name="بورس کالای ایران (IME)",
        slug="ime-market",
        description="تحلیل و اخبار رینگ فلزات و تالار حراج صنعتی بورس کالا"
    )
    news_cat_lme = NewsCategory.objects.create(
        name="بازار جهانی و بورس لندن (LME)",
        slug="global-lme",
        description="نرخ‌های جهانی مس، آلومینیوم و اثرات ژئوپلیتیک و انرژی"
    )
    news_cat_copper = NewsCategory.objects.create(
        name="تحلیل تخصصی بازار مس",
        slug="copper-insights",
        description="گزارش‌های جامع شرکت ملی صنایع مس، معادن و صنایع مفتول‌سازی"
    )

    art1 = Article.objects.create(
        category=news_cat_ime,
        title="ثبت رقابت سنگین بر سر کاتد مس در تالار صنعتی بورس کالا؛ فملی ۴ هزار تن کاتد عرضه کرد",
        slug="copper-cathode-ime-competition-report",
        summary="در معاملات روز گذشته تالار صنعتی و معدنی بورس کالای ایران، شرکت ملی صنایع مس ایران (فملی) بالغ بر ۴ هزار تن کاتد مس عرضه کرد که با استقبال گسترده مفتول‌سازان و رقابت قیمتی تا نرخ پایانی مواجه شد.",
        content="""در جریان آخرین جلسه معاملاتی تالار صنعتی بورس کالای ایران، تالار فلزات سرخ شاهد رقابت پرحرارت متقاضیان بود. طبق آمار رسمی مدیریت معاملات بورس کالا، شرکت ملی صنایع مس ایران (فملی) تعداد ۴۰۰۰ تن کاتد مس با قیمت پایه تعیین شده بر اساس فرمول میانگین هفتگی انس مس در بورس فلزات لندن (LME) ضرب‌در نرخ ارز حواله دلار نیما به روی تابلو برد.

با توجه به پیش‌بینی‌ها مبنی بر افزایش سفارشات کابل‌سازی و توسعه خطوط زیرساختی برق کشور، تقاضای ثبت‌شده در تابلوی معاملات به بیش از ۸۲۰۰ تن رسید که ضریب رقابتی معادل ۲.۰۵ برابری را نشان می‌دهد. کارشناسان بازار سرمایه معتقدند با تثبیت تقاضای پایدار داخلی و رونق صادرات مقاطع مسی نیمه‌ساخته، سطح تقاضا برای ماه‌های آینده نیز صعودی باقی خواهد ماند.

همچنین در این روز، عرضه ۱۲۰۰ تن مفتول مس نیز با قیمت پایه متناسب انجام پذیرفت که تمام محموله‌ها در لحظات اولیه زمان معاملات با رقابت معقول به فروش رسید و قراردادهای سلف یک‌ماهه منعقد گردید.""",
        source="پایگاه خبری بورس کالای ایران (IME)",
        author=content_user,
        image_badge="گزارش بورس کالا",
        views_count=482,
        is_breaking=True,
        published_at=now - timedelta(hours=4)
    )

    art2 = Article.objects.create(
        category=news_cat_lme,
        title="جهش بهای جهانی مس به مرز ۹,۸۰۰ دلار در پی رونق خودروهای الکتریکی و هوش مصنوعی",
        slug="lme-copper-price-rally-ev-ai-datacenters",
        summary="تحلیلگران بورس فلزات لندن (LME) اعلام کردند کاهش سطح ذخایر انبارها و عطش ساخت دیتاسنترهای عظیم هوش مصنوعی و زیرساخت خودروهای برقی، بازار مس جهانی را با کسری عرضه در سال آینده مواجه خواهد کرد.",
        content="""بهای هر تن مس در تالار معاملات آتی بورس فلزات لندن (London Metal Exchange) با رشد ۱.۸ درصدی به کانال ۹,۷۸۰ دلار صعود کرد. این رشد همزمان با انتشار گزارش فصلی موسسه بین‌المللی مطالعات مس (ICSG) رخ داد که پیش‌بینی کرده کسری تراز بازار مس جهان تا پایان سال به بیش از ۱۸۰ هزار تن بالغ خواهد شد.

کارشناسان متال‌بولتن (Fastmarkets) تاکید کرده‌اند که بر خلاف بحران‌های دهه‌های گذشته، پیشران تقاضای کنونی مس صرفاً بخش ساخت‌وساز نیست؛ بلکه گسترش شبکه برق دیتاسنترهای هوش مصنوعی (که هر گیگاوات آن بیش از ۳۰ هزار تن مس در ترانسفورماتورها و کابل‌ها مصرف می‌کند) به همراه رشد تصاعدی تولید خودروهای الکتریکی در آسیا و اروپا، کشش بی‌پایانی برای مس خالص کاتد ایجاد کرده است.

همچنین اختلالات بهره‌برداری در برخی معادن بزرگ شیلی و پاناما سبب شده شرکت‌های ذوب بزرگ در چین، کارمزد فرآوری کنسانتره (TC/RC) را به سطوح تاریخی کاهش دهند که هشداری جدی برای کاهش تولید مس تصفیه شده در ماه‌های آینده است.""",
        source="بورس فلزات لندن (LME / Reuters)",
        author=content_user,
        image_badge="بازار بین‌المللی",
        views_count=356,
        is_breaking=False,
        published_at=now - timedelta(days=1, hours=2)
    )

    art3 = Article.objects.create(
        category=news_cat_copper,
        title="بررسی بازدهی صنایع مس شهید باهنر و جهش تقاضای لوله‌های مسی شیاردار در صنعت برودت",
        slug="bahonar-copper-tubes-cooling-market-review",
        summary="گزارش واحد بازرگانی فلز آنلاین نشان می‌دهد با مدرن‌سازی سیستم‌های تبرید صنعتی و تهویه مطبوع، تقاضای لوله‌های مسی تیپ اینرگرو (Inner Groove) با ضریب تبادل حرارتی بالا بیش از ۳۵ درصد رشد یافته است.",
        content="""صنایع مس شهید باهنر به عنوان بزرگترین مجتمع غیردولتی تولید نیمه‌ساخته‌های مسی و برنجی در خاورمیانه، در گزارش عملکرد سالانه خود از رشد متوازن تولید مقاطع برنجی و لوله‌های برودتی خبر داده است. لوله‌های مسی با شیار داخلی (Inner Groove) به دلیل انتقال حرارت تا ۲ برابر سریع‌تر از لوله‌های ساده، اکنون به استاندارد اجباری شرکت‌های سازنده چیلر و داکت اسپلیت تبدیل شده‌اند.

در گفت‌وگوی اختصاصی با مهندسان متالورژی کارخانه، این نکته تبیین شد که کاربرد آلیاژ فسفردار Cu-DHP علاوه بر انعطاف بالا در فرآیند جوشکاری نقره، مقاومت به خوردگی در برابر روغن‌های سنتتیک مبردهای نسل جدید مثل R410a و R32 را به شدت ارتقا می‌دهد. خریداران عمده می‌توانند از طریق کارشناسان فلز آنلاین نسبت به رزرو ظرفیت کارخانه با نرخ رسمی بورس کالا اقدام فرمایند.""",
        source="واحد تحقیقات متالورژی فلز آنلاین",
        author=content_user,
        image_badge="تحلیل تکنیکال",
        views_count=289,
        is_breaking=False,
        published_at=now - timedelta(days=2)
    )

    art4 = Article.objects.create(
        category=news_cat_ime,
        title="عرضه گسترده شمش آلومینیوم ۹۹.۷ ایرالکو و سالکو در تالار اختصاصی بورس کالا",
        slug="aluminum-ingot-iralco-salco-supply-ime",
        summary="تالار فلزات بورس کالای ایران میزبان عرضه ۳۵۰۰ تن شمش آلومینیوم خالص شرکت‌های آلومینیوم ایران (ایرالکو) و مجتمع آلومینیوم جنوب (سالکو) بود.",
        content="""در رینگ معاملاتی امروز فلزات غیرآهنی، معامله‌گران شاهد عرضه پرحجم شمش خالص آلومینیوم تی‌بار و ۵۰ پوندی با عیار ۹۹.۷ و ۹۹.۸۵ درصد بودند. شرکت سالکو با عرضه ۲ هزار تن و ایرالکو با عرضه ۱۵۰۰ تن، پاسخگوی تقاضای شرکت‌های پروفیل‌ساز و اکستروژن‌کاران سراسر کشور بودند.

قیمت پایانی معاملات پس از احتساب رقابت با میانگین نرخ روز به تایید ناظر بازار رسید. فعالان این حوزه عنوان کردند با تثبیت تامین برق صنایع در فصل پاییز، خطوط احیا با حداکثر ظرفیت مشغول فعالیت هستند و کمبود محسوسی در زنجیره تامین شمش پایه مشاهده نمی‌شود.""",
        source="پایگاه اطلاعاتی فلزات ایران (ایمیدرو)",
        author=content_user,
        image_badge="اخبار آلومینیوم",
        views_count=215,
        is_breaking=False,
        published_at=now - timedelta(days=3)
    )

    print("Creating sample customer inquiries / orders...")
    order1 = OrderInquiry.objects.create(
        tracking_code="FLZ-98421",
        user=buyer_user,
        product=p1,
        quantity=3.5,
        unit="تن",
        customer_name="حمید فرهادی (صنایع الکتریک پویان)",
        customer_phone="09124444444",
        destination_city="قزوین / شهرک صنعتی کاسپین",
        delivery_address="بلوار صنعت، انتهای خیابان هشتم، سوله پویان الکتریک",
        description="کاتد حتماً مس سرچشمه با برگ آنالیز خلوص ۹۹.۹۹٪ باشد. بارگیری تریلی کفی با پالت‌بندی تسمه فلزی استاندارد.",
        quoted_unit_price=642000,
        status=OrderInquiry.Status.QUOTED,
        sales_rep_notes="پیش‌فاکتور با مهلت پرداخت ۴۸ ساعته صادر گردید. هزینه باربری از انبار شورآباد به مقصد بر عهده خریدار طبق بارنامه دولتی محاسبه خواهد شد."
    )

    order2 = OrderInquiry.objects.create(
        tracking_code="FLZ-98422",
        user=buyer_user,
        product=p3,
        quantity=1.2,
        unit="تن",
        customer_name="حمید فرهادی (صنایع الکتریک پویان)",
        customer_phone="09124444444",
        destination_city="تهران / شهرک صنعتی شمس‌آباد",
        delivery_address="خیابان پروفسور حسابی، پلاک ۱۱",
        description="مفتول ۸ میلیمتر دنیای مس کاشان ویژه خط کشش نازک‌سیم.",
        quoted_unit_price=664000,
        status=OrderInquiry.Status.APPROVED,
        sales_rep_notes="تأییدیه مالی و واریز پیش‌پرداخت انجام شده است. هماهنگی بارگیری برای فردا صبح ساعت ۹ انجام شد."
    )

    order3 = OrderInquiry.objects.create(
        tracking_code="FLZ-98423",
        user=None,
        product=p6,
        quantity=5.0,
        unit="تن",
        customer_name="شرکت مهندسی نوین قالب اصفهان",
        customer_phone="09135555555",
        destination_city="اصفهان / منطقه صنعتی دولت‌آباد",
        delivery_address="فاز ۳ خیابان صنعتگران",
        description="استعلام خرید شمش خالص ۹۹.۷ ایرالکو به همراه برگه سرتیفیکیت آزمایشگاه.",
        quoted_unit_price=0,
        status=OrderInquiry.Status.PENDING,
        sales_rep_notes="در حال هماهنگی با انبار و بررسی موجودی شمش ۵۰ پوندی."
    )

    print("Database seeding completed successfully!")

if __name__ == '__main__':
    seed_database()
