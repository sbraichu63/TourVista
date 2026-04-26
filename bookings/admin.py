from django.contrib import admin
from .models import Booking, Payment


class PaymentInline(admin.StackedInline):
    model = Payment
    extra = 0
    readonly_fields = ('receipt_number', 'transaction_id', 'paid_at')


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('booking_ref', 'user', 'package', 'travel_date', 'num_travellers', 'total_amount', 'status', 'created_at')
    list_filter = ('status', 'travel_date', 'created_at')
    search_fields = ('booking_ref', 'user__username', 'email', 'package__title')
    list_editable = ('status',)
    readonly_fields = ('booking_ref', 'created_at', 'updated_at')
    inlines = [PaymentInline]
    actions = ['mark_confirmed', 'mark_completed', 'mark_cancelled']

    def mark_confirmed(self, request, queryset):
        queryset.update(status='confirmed')
    mark_confirmed.short_description = '✅ Mark selected as Confirmed'

    def mark_completed(self, request, queryset):
        queryset.update(status='completed')
    mark_completed.short_description = '🏁 Mark selected as Completed'

    def mark_cancelled(self, request, queryset):
        queryset.update(status='cancelled')
    mark_cancelled.short_description = '❌ Mark selected as Cancelled'


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('receipt_number', 'booking', 'amount', 'method', 'status', 'paid_at')
    list_filter = ('method', 'status')
    search_fields = ('receipt_number', 'transaction_id', 'booking__booking_ref')
    readonly_fields = ('receipt_number', 'transaction_id', 'paid_at')
