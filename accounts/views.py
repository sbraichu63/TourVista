from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
import logging
import random
import string

logger = logging.getLogger(__name__)

from .forms import RegisterForm, LoginForm, ProfileUpdateForm
from .models import UserProfile, EmailOTP
from bookings.models import Booking


# ──────────────────────────────────────────────────────────────────
# REGISTER
# ──────────────────────────────────────────────────────────────────
def register_view(request):
    if request.user.is_authenticated:
        return redirect('core:home')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.email = form.cleaned_data['email']
            user.is_active = True  # Active but email unverified
            user.save()

            # Create profile
            phone = form.cleaned_data.get('phone', '')
            UserProfile.objects.create(user=user, phone=phone, email_verified=False)

            # Create email verification OTP
            otp_code = ''.join(random.choices(string.digits, k=6))
            EmailOTP.objects.create(user=user, otp=otp_code)

            # Send verification email
            try:
                send_mail(
                    subject='🌏 Verify Your TourVista India Account',
                    message=f'''Hi {user.first_name or user.username}!

Welcome to TourVista India! 🇮🇳

Your verification code is: {otp_code}

Please enter this code on the verification page to activate your account. This code expires in 10 minutes.

Happy Travels!
— Team TourVista India
''',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=False,
                )
            except Exception as e:
                logger.warning(f'Email verification failed for user {user.username}: {str(e)}')

            messages.success(request, f'🎉 Account created! We sent a 6-digit code to {user.email}.')
            login(request, user)
            return redirect('accounts:verify_otp')
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        form = RegisterForm()

    return render(request, 'accounts/register.html', {'form': form})


# ──────────────────────────────────────────────────────────────────
# OTP VERIFICATION
# ──────────────────────────────────────────────────────────────────
@login_required
def verify_otp(request):
    if request.user.profile.email_verified:
        return redirect('accounts:dashboard')

    if request.method == 'POST':
        otp_entered = request.POST.get('otp', '').strip()
        
        # Get latest valid OTP
        otp_obj = EmailOTP.objects.filter(user=request.user, is_verified=False).order_by('-created_at').first()
        
        if otp_obj and otp_obj.is_valid() and otp_obj.otp == otp_entered:
            otp_obj.is_verified = True
            otp_obj.save()
            
            profile = request.user.profile
            profile.email_verified = True
            profile.save()
            
            messages.success(request, '✅ Email verified successfully! You can now book tours.')
            return redirect('accounts:dashboard')
        else:
            messages.error(request, '❌ Invalid or expired OTP. Please try again.')

    return render(request, 'accounts/verify_otp.html')


@login_required
def resend_otp(request):
    if request.user.profile.email_verified:
        return redirect('accounts:dashboard')

    # Generate new OTP
    otp_code = ''.join(random.choices(string.digits, k=6))
    EmailOTP.objects.create(user=request.user, otp=otp_code)

    try:
        send_mail(
            subject='🌏 Your New TourVista Verification Code',
            message=f'Your new verification code is: {otp_code}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[request.user.email],
        )
        messages.success(request, '📧 New code sent! Check your inbox.')
    except Exception as e:
        logger.warning(f'OTP resend failed for user {request.user.username}: {str(e)}')
        messages.error(request, 'Could not send email. Please try again later.')

    return redirect('accounts:verify_otp')


# ──────────────────────────────────────────────────────────────────
# LOGIN / LOGOUT
# ──────────────────────────────────────────────────────────────────
def login_view(request):
    if request.user.is_authenticated:
        return redirect('core:home')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            remember = form.cleaned_data.get('remember_me')

            login(request, user)
            
            # Set session expiry based on "Remember Me" checkbox
            if not remember:
                request.session.set_expiry(0)  # Expire at browser close
            
            messages.success(request, f'👋 Welcome back, {user.first_name or user.username}!')
            
            # Redirect staff to Admin Dashboard
            if user.is_staff:
                return redirect('accounts:admin_dashboard')
                
            next_url = request.GET.get('next', 'accounts:dashboard')
            return redirect(next_url)
        else:
            messages.error(request, '❌ Invalid username or password.')
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    if request.method == 'POST':
        logout(request)
        messages.info(request, 'You have been logged out. Safe travels! ✈️')
    return redirect('core:home')


# ──────────────────────────────────────────────────────────────────
# USER DASHBOARD
# ──────────────────────────────────────────────────────────────────
@login_required
def dashboard(request):
    user = request.user
    
    # Redirect staff to Admin Dashboard
    if user.is_staff:
        return redirect('accounts:admin_dashboard')

    bookings = Booking.objects.filter(user=user).select_related('package').order_by('-created_at')

    # Stats
    total_bookings = bookings.count()
    confirmed = bookings.filter(status='confirmed').count()
    pending = bookings.filter(status='pending').count()
    completed = bookings.filter(status='completed').count()

    # Wishlist
    from core.models import Wishlist
    wishlist = Wishlist.objects.filter(user=user).select_related('package').order_by('-added_at')

    # Recent reviews
    from core.models import Review
    reviews = Review.objects.filter(user=user).select_related('package').order_by('-created_at')[:5]

    profile, _ = UserProfile.objects.get_or_create(user=user)

    context = {
        'bookings': bookings,
        'total_bookings': total_bookings,
        'confirmed': confirmed,
        'pending': pending,
        'completed': completed,
        'wishlist': wishlist,
        'reviews': reviews,
        'profile': profile,
    }
    return render(request, 'accounts/dashboard.html', context)


# ──────────────────────────────────────────────────────────────────
# ADMIN DASHBOARD
# ──────────────────────────────────────────────────────────────────
@login_required
def admin_dashboard(request):
    if not request.user.is_staff:
        messages.error(request, 'Access denied. Admins only.')
        return redirect('accounts:dashboard')

    # Global Stats
    all_users = User.objects.all().select_related('profile')
    all_bookings = Booking.objects.all().select_related('user', 'package').order_by('-created_at')
    
    from core.models import TourPackage
    all_packages = TourPackage.objects.all()

    from django.db.models import Sum
    total_revenue = Booking.objects.filter(
        status='confirmed'
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    pending_bookings = all_bookings.filter(status='pending').count()

    context = {
        'all_users': all_users,
        'all_bookings': all_bookings,
        'all_packages': all_packages,
        'total_users': all_users.count(),
        'total_bookings': all_bookings.count(),
        'total_packages': all_packages.count(),
        'total_revenue': total_revenue,
        'pending_count': pending_bookings,
    }
    return render(request, 'accounts/admin_dashboard.html', context)


@login_required
def admin_verify_user(request, user_id):
    if not request.user.is_staff:
        return redirect('accounts:dashboard')
        
    target_user = get_object_or_404(User, id=user_id)
    profile, _ = UserProfile.objects.get_or_create(user=target_user)
    profile.email_verified = True
    profile.save()
    
    messages.success(request, f'✅ User {target_user.username} has been manually verified!')
    return redirect('accounts:admin_dashboard')


@login_required
def admin_update_booking_status(request, booking_id, status):
    if not request.user.is_staff:
        messages.error(request, 'Access denied. Admins only.')
        return redirect('accounts:dashboard')
        
    booking = get_object_or_404(Booking, id=booking_id)
    valid_statuses = ['pending', 'confirmed', 'completed', 'cancelled']
    
    if status in valid_statuses:
        booking.status = status
        booking.save()
        messages.success(request, f'Booking #{booking.booking_ref} marked as {status.upper()}.')
    else:
        messages.error(request, 'Invalid status.')
        
    return redirect('accounts:admin_dashboard')



# ──────────────────────────────────────────────────────────────────
# PROFILE UPDATE
# ──────────────────────────────────────────────────────────────────
@login_required
def profile_update(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            # Update user fields
            request.user.first_name = form.cleaned_data.get('first_name', request.user.first_name)
            request.user.last_name = form.cleaned_data.get('last_name', request.user.last_name)
            request.user.email = form.cleaned_data.get('email', request.user.email)
            request.user.save()
            form.save()
            messages.success(request, '✅ Profile updated successfully!')
            return redirect('accounts:dashboard')
    else:
        initial = {
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
        }
        form = ProfileUpdateForm(instance=profile, initial=initial)

    return render(request, 'accounts/profile_update.html', {'form': form, 'profile': profile})
