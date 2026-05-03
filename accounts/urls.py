from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-verify/<int:user_id>/', views.admin_verify_user, name='admin_verify_user'),
    path('admin-booking-status/<int:booking_id>/<str:status>/', views.admin_update_booking_status, name='admin_update_booking_status'),
    path('profile/update/', views.profile_update, name='profile_update'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('resend-otp/', views.resend_otp, name='resend_otp'),
]
