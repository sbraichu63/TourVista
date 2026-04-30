from django.contrib import admin
from .models import UserProfile, EmailVerificationToken

admin.site.register(UserProfile)
admin.site.register(EmailVerificationToken)
