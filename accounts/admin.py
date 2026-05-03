from django.contrib import admin
from .models import UserProfile, EmailOTP

admin.site.register(UserProfile)
admin.site.register(EmailOTP)
