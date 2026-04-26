from django.contrib import admin
from .models import UserProfile, EmailVerificationToken


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'city', 'email_verified', 'created_at')
    list_filter = ('email_verified',)
    search_fields = ('user__username', 'user__email', 'phone', 'city')
    list_editable = ('email_verified',)
    readonly_fields = ('created_at',)


@admin.register(EmailVerificationToken)
class EmailVerificationTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'token', 'is_used', 'created_at')
    list_filter = ('is_used',)
    readonly_fields = ('token', 'created_at')
