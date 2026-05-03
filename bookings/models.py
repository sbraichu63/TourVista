from django.db import models
from django.contrib.auth.models import User
from core.models import TourPackage
import uuid


BOOKING_STATUS = [
    ('pending', 'Pending'),
    ('confirmed', 'Confirmed'),
    ('cancelled', 'Cancelled'),
    ('completed', 'Completed'),
]

PAYMENT_STATUS = [
    ('pending', 'Pending'),
    ('paid', 'Paid'),
    ('refunded', 'Refunded'),
    ('failed', 'Failed'),
]

PAYMENT_METHOD = [
    ('upi', 'UPI'),
    ('card', 'Credit/Debit Card'),
    ('netbanking', 'Net Banking'),
    ('wallet', 'Digital Wallet'),
]


class Booking(models.Model):
    booking_ref = models.CharField(max_length=12, unique=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    package = models.ForeignKey(TourPackage, on_delete=models.CASCADE, related_name='bookings')

    # Traveller info
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    num_travellers = models.PositiveIntegerField(default=1)
    travel_date = models.DateField()
    special_requests = models.TextField(blank=True)

    # Pricing
    price_per_person = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)

    # Status
    status = models.CharField(max_length=20, choices=BOOKING_STATUS, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
            models.Index(fields=['travel_date']),
        ]

    def __str__(self):
        return f"#{self.booking_ref} — {self.user.username} → {self.package.title}"

    def save(self, *args, **kwargs):
        if not self.booking_ref:
            self.booking_ref = "TV" + uuid.uuid4().hex[:8].upper()
        if not self.total_amount:
            self.total_amount = self.price_per_person * self.num_travellers
        super().save(*args, **kwargs)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class Payment(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='payment')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    method = models.CharField(max_length=20, choices=PAYMENT_METHOD, default='upi')
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    transaction_id = models.CharField(max_length=100, unique=True, blank=True)
    card_last4 = models.CharField(max_length=4, blank=True)
    upi_id = models.CharField(max_length=100, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    receipt_number = models.CharField(max_length=20, unique=True, blank=True)

    def __str__(self):
        return f"Payment #{self.receipt_number} — {self.booking.booking_ref}"

    def save(self, *args, **kwargs):
        if not self.receipt_number:
            self.receipt_number = "RCP-" + uuid.uuid4().hex[:8].upper()
        if not self.transaction_id:
            self.transaction_id = "TXN-" + uuid.uuid4().hex[:12].upper()
        super().save(*args, **kwargs)
