from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import User
from .forms import LoginForm, RegisterForm, ProfileUpdateForm, UserRoleEditForm


def login_view(request):
    if request.user.is_authenticated:
        return redirect('market:dashboard')

    if request.method == 'POST':
        # Check if it is a demo quick-login button
        demo_user = request.POST.get('demo_user')
        if demo_user in ['admin', 'sales_manager', 'news_editor', 'buyer1']:
            user = User.objects.filter(username=demo_user).first()
            if user:
                login(request, user)
                messages.success(request, f"خوش آمدید! شما با نقش «{user.get_role_display()}» وارد شدید.")
                next_url = request.GET.get('next')
                if next_url:
                    return redirect(next_url)
                if user.is_admin_role or user.is_sales_role:
                    return redirect('market:management_dashboard')
                return redirect('market:dashboard')

        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            
            # Allow login by phone number as well
            user = authenticate(request, username=username, password=password)
            if not user:
                # check by phone
                u_by_phone = User.objects.filter(phone_number=username).first()
                if u_by_phone and u_by_phone.check_password(password):
                    user = u_by_phone

            if user is not None:
                if user.is_active:
                    login(request, user)
                    messages.success(request, f"ورود با موفقیت انجام شد. خوش آمدید، {user.get_full_name() or user.username}!")
                    next_url = request.GET.get('next')
                    if next_url:
                        return redirect(next_url)
                    if user.is_admin_role or user.is_sales_role:
                        return redirect('market:management_dashboard')
                    return redirect('market:dashboard')
                else:
                    messages.error(request, "حساب کاربری شما مسدود یا غیرفعال شده است. لطفاً با پشتیبانی تماس بگیرید.")
            else:
                messages.error(request, "نام کاربری یا کلمه عبور وارد شده اشتباه است.")
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form})


def register_view(request):
    if request.user.is_authenticated:
        return redirect('market:dashboard')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = User.Role.CUSTOMER  # Default newly registered users to Customer
            user.set_password(form.cleaned_data['password'])
            user.save()
            login(request, user)
            messages.success(request, "ثبت‌نام شما با موفقیت تکمیل شد! به سامانه تخصصی فلزی‌ها (Feleziha) خوش آمدید.")
            return redirect('market:dashboard')
        else:
            messages.error(request, "لطفاً خطاهای فرم ثبت‌نام را بررسی و اصلاح فرمایید.")
    else:
        form = RegisterForm()

    return render(request, 'accounts/register.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, "شما با موفقیت از سامانه خارج شدید.")
    return redirect('market:home')


@login_required
def profile_view(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "اطلاعات حساب کاربری شما با موفقیت بروزرسانی شد.")
            return redirect('accounts:profile')
    else:
        form = ProfileUpdateForm(instance=request.user)

    return render(request, 'accounts/profile.html', {'form': form})


# ========================================================
# RBAC: User & Permission Management (Superadmin / Admin)
# ========================================================

def is_admin_check(user):
    return user.is_authenticated and (user.is_superuser or user.role == User.Role.ADMIN)


@login_required
@user_passes_test(is_admin_check, login_url='accounts:login')
def user_management_view(request):
    """
    Superadmin view to view all users, inspect permissions,
    and update roles (Admin, Sales, Editor, Customer).
    """
    role_filter = request.GET.get('role', '')
    search_query = request.GET.get('q', '')

    users_qs = User.objects.all().order_by('-date_joined')
    if role_filter:
        users_qs = users_qs.filter(role=role_filter)
    if search_query:
        users_qs = users_qs.filter(
            username__icontains=search_query
        ) | users_qs.filter(
            first_name__icontains=search_query
        ) | users_qs.filter(
            last_name__icontains=search_query
        ) | users_qs.filter(
            phone_number__icontains=search_query
        ) | users_qs.filter(
            company_name__icontains=search_query
        )

    stats = {
        'total': User.objects.count(),
        'admins': User.objects.filter(role=User.Role.ADMIN).count(),
        'sales': User.objects.filter(role=User.Role.SALES).count(),
        'content': User.objects.filter(role=User.Role.CONTENT).count(),
        'customers': User.objects.filter(role=User.Role.CUSTOMER).count(),
    }

    context = {
        'user_list': users_qs,
        'role_filter': role_filter,
        'search_query': search_query,
        'stats': stats,
        'role_choices': User.Role.choices,
    }
    return render(request, 'accounts/user_management.html', context)


@login_required
@user_passes_test(is_admin_check, login_url='accounts:login')
def user_edit_role_view(request, user_id):
    target_user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        new_role = request.POST.get('role')
        is_active = request.POST.get('is_active') == 'on'
        is_verified = request.POST.get('is_verified') == 'on'
        
        if new_role in [c[0] for c in User.Role.choices]:
            target_user.role = new_role
            target_user.is_active = is_active
            target_user.is_verified = is_verified
            # If admin or sales or content, grant staff status so they can access administrative sections
            if new_role in [User.Role.ADMIN, User.Role.SALES, User.Role.CONTENT]:
                target_user.is_staff = True
            else:
                target_user.is_staff = False
            
            target_user.save()
            messages.success(request, f"نقش و حقوق دسترسی کاربر «{target_user.username}» به «{target_user.get_role_display()}» تغییر یافت.")
            return redirect('accounts:user_management')
    
    return render(request, 'accounts/user_edit_role.html', {'target_user': target_user, 'role_choices': User.Role.choices})
