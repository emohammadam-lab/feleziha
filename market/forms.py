from django import forms
from .models import OrderInquiry, Product


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
