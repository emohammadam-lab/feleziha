from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import User


class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'نام کاربری یا شماره موبایل',
            'autocomplete': 'username',
            'dir': 'ltr'
        }),
        label='نام کاربری'
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'رمز عبور',
            'autocomplete': 'current-password',
            'dir': 'ltr'
        }),
        label='رمز عبور'
    )


class RegisterForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'حداقل ۶ کاراکتر',
            'autocomplete': 'new-password',
            'dir': 'ltr'
        }),
        label='رمز عبور'
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'تکرار رمز عبور',
            'autocomplete': 'new-password',
            'dir': 'ltr'
        }),
        label='تکرار رمز عبور'
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'phone_number', 'company_name', 'national_id', 'address']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'نام کاربری انگلیسی', 'dir': 'ltr'}),
            'first_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'نام'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'نام خانوادگی'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '۰۹۱۲۳۴۵۶۷۸۹', 'dir': 'ltr'}),
            'company_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'نام شرکت، کارگاه یا بازرگانی (اختیاری)'}),
            'national_id': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'کد ملی یا شناسه ملی ۱۰ یا ۱۱ رقمی (اختیاری)', 'dir': 'ltr'}),
            'address': forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'نشانی پستی کارخانه یا انبار خریدار جهت ارسال بار'}),
        }

    def clean_password(self):
        password = self.cleaned_data.get('password')
        validate_password(password)
        return password

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password')
        p2 = cleaned_data.get('password_confirm')
        if p1 and p2 and p1 != p2:
            self.add_error('password_confirm', 'رمزهای عبور وارد شده همخوانی ندارند.')
        return cleaned_data


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone_number', 'email', 'company_name', 'national_id', 'economic_code', 'address', 'postal_code']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-input'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-input', 'dir': 'ltr'}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'dir': 'ltr'}),
            'company_name': forms.TextInput(attrs={'class': 'form-input'}),
            'national_id': forms.TextInput(attrs={'class': 'form-input', 'dir': 'ltr'}),
            'economic_code': forms.TextInput(attrs={'class': 'form-input', 'dir': 'ltr'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-input', 'dir': 'ltr'}),
            'address': forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),
        }


class UserRoleEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['role', 'is_active', 'is_verified', 'is_staff']
        widgets = {
            'role': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'is_verified': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'is_staff': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }
