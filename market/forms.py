from django import forms
from .models import OrderInquiry, Product, SiteContentBlock, MediaAsset


class OrderInquiryForm(forms.ModelForm):
    class Meta:
        model = OrderInquiry
        fields = [
            'product',
            'custom_product_title',
            'quantity',
            'unit',
            'customer_name',
            'customer_phone',
            'destination_city',
            'delivery_address',
            'description'
        ]
        widgets = {
            'product': forms.Select(attrs={'class': 'form-select'}),
            'custom_product_title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'در صورت نبود کالا در لیست، نام دقیق و ابعاد را بنویسید'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'مثال: ۲.۵', 'step': '0.1', 'min': '0.1'}),
            'unit': forms.Select(choices=[('کیلوگرم', 'کیلوگرم'), ('تن', 'تن'), ('شاخه', 'شاخه'), ('کلاف', 'کلاف'), ('شیت / برگ', 'شیت / برگ')], attrs={'class': 'form-select'}),
            'customer_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'نام و نام‌خانوادگی / نام شرکت'}),
            'customer_phone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '۰۹۱۲۳۴۵۶۷۸۹', 'dir': 'ltr'}),
            'destination_city': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'مثال: تهران / شهرک صنعتی شمس‌آباد'}),
            'delivery_address': forms.Textarea(attrs={'class': 'form-input', 'rows': 2, 'placeholder': 'آدرس دقیق کارخانه یا انبار جهت محاسبه کرایه بار'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'مشخصات ویژه، استاندارد مورد نیاز، نحوه بارگیری و بسته‌بندی'}),
        }


class SalesQuotationUpdateForm(forms.ModelForm):
    class Meta:
        model = OrderInquiry
        fields = ['quoted_unit_price', 'status', 'sales_rep_notes']
        widgets = {
            'quoted_unit_price': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'قیمت هر واحد به تومان'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'sales_rep_notes': forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'شرایط پرداخت، اعتبار زمانی قیمت، مبدأ بارگیری و توضیحات'}),
        }


class FastPriceUpdateForm(forms.Form):
    product_id = forms.IntegerField(widget=forms.HiddenInput())
    new_price = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-input py-1 text-sm', 'placeholder': 'قیمت جدید'}))
    change_note = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-input py-1 text-sm', 'placeholder': 'دلیل نوسان (اختیاری)'}))


class SiteContentBlockForm(forms.ModelForm):
    class Meta:
        model = SiteContentBlock
        fields = ['title', 'key', 'subtitle', 'content', 'image', 'link_url', 'link_text', 'section', 'order', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'عنوان بلاک محتوایی'}),
            'key': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'مثال: hero_title یا about_text (حروف لاتین و خط تیره)'}),
            'subtitle': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'زیرعنوان یا برچسب کوتاه (اختیاری)'}),
            'content': forms.Textarea(attrs={'class': 'form-input', 'rows': 4, 'placeholder': 'متن، توضیحات یا کدهای HTML بلاک'}),
            'link_url': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'مثال: /products/ یا #inquiry'}),
            'link_text': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'مثال: استعلام فوری'}),
            'section': forms.Select(attrs={'class': 'form-select'}),
            'order': forms.NumberInput(attrs={'class': 'form-input', 'style': 'max-width:100px;'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }


class MediaAssetForm(forms.ModelForm):
    class Meta:
        model = MediaAsset
        fields = ['title', 'media_type', 'file', 'thumbnail', 'external_url', 'caption', 'category_tag', 'is_featured', 'is_active', 'order']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'عنوان رسانه یا فایل'}),
            'media_type': forms.Select(attrs={'class': 'form-select'}),
            'file': forms.FileInput(attrs={'class': 'form-input'}),
            'thumbnail': forms.FileInput(attrs={'class': 'form-input'}),
            'external_url': forms.URLInput(attrs={'class': 'form-input', 'placeholder': 'لینک ویدیو یا آپارات (اختیاری)'}),
            'caption': forms.Textarea(attrs={'class': 'form-input', 'rows': 2, 'placeholder': 'توضیحات کوتاه یا زیرنویس فنی فایل'}),
            'category_tag': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'مثال: باسبار باهنر، دنیای مس، آزمایشگاه'}),
            'order': forms.NumberInput(attrs={'class': 'form-input', 'style': 'max-width:100px;'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }


class ProductQuickEditForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['title', 'manufacturer', 'alloy_grade', 'dimensions', 'stock_status', 'warehouse_location', 'image', 'is_featured']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'نام کالا'}),
            'manufacturer': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'تولیدکننده / برند'}),
            'alloy_grade': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'گرید یا آلیاژ'}),
            'dimensions': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'سایز / ضخامت'}),
            'stock_status': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'وضعیت موجودی'}),
            'warehouse_location': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'انبار بارگیری'}),
            'image': forms.FileInput(attrs={'class': 'form-input'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }
