from django import forms
from django.utils import timezone
from datetime import timedelta
from .models import Booking, Payment
import re
from datetime import datetime


class BookingForm(forms.ModelForm):
    travel_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'min': '', 'id': 'id_travel_date'})
    )

    class Meta:
        model = Booking
        fields = ('first_name', 'last_name', 'email', 'phone',
                  'num_travellers', 'travel_date', 'special_requests')
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Last Name'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email Address'}),
            'phone': forms.TextInput(attrs={'placeholder': '+91 XXXXX XXXXX'}),
            'num_travellers': forms.NumberInput(attrs={'min': 1, 'max': 50}),
            'special_requests': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Any dietary requirements, accessibility needs, or special requests...'
            }),
        }

    def clean_num_travellers(self):
        n = self.cleaned_data['num_travellers']
        if n < 1:
            raise forms.ValidationError('At least 1 traveller is required.')
        if n > 50:
            raise forms.ValidationError('Maximum 50 travellers per booking.')
        return n

    def clean_travel_date(self):
        date = self.cleaned_data['travel_date']
        min_date = timezone.now().date() + timedelta(days=1)
        max_date = timezone.now().date() + timedelta(days=730)  # 2 years max
        
        if date < min_date:
            raise forms.ValidationError('Travel date must be at least tomorrow.')
        if date > max_date:
            raise forms.ValidationError('Travel date cannot be more than 2 years in advance.')
        return date


class PaymentForm(forms.Form):
    METHOD_CHOICES = [
        ('card', '💳 Credit / Debit Card'),
        ('razorpay', '🚀 Razorpay (UPI, Wallets, etc.)'),
    ]
    method = forms.ChoiceField(
        choices=METHOD_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'payment-radio'}),
        initial='razorpay'
    )
    
    razorpay_payment_id = forms.CharField(required=False, widget=forms.HiddenInput())

    # Card fields
    card_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Name on Card', 'id': 'id_card_name'})
    )
    card_number = forms.CharField(
        required=False,
        max_length=19,
        widget=forms.TextInput(attrs={'placeholder': '1234 5678 9012 3456', 'id': 'id_card_number', 'maxlength': '19'})
    )
    card_expiry = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'MM/YY', 'id': 'id_card_expiry', 'maxlength': '5'})
    )
    card_cvv = forms.CharField(
        required=False,
        max_length=4,
        widget=forms.PasswordInput(attrs={'placeholder': 'CVV', 'id': 'id_card_cvv', 'maxlength': '4'})
    )

    def clean_card_number(self):
        number = self.cleaned_data.get('card_number', '').replace(' ', '')
        method = self.data.get('method')
        if method == 'card' and number:
            if not number.isdigit() or not (13 <= len(number) <= 19):
                raise forms.ValidationError('Card number must be 13-19 digits.')
            
            # Luhn Algorithm
            total = 0
            reverse_digits = number[::-1]
            for i, digit in enumerate(reverse_digits):
                n = int(digit)
                if i % 2 == 1:
                    n *= 2
                    if n > 9:
                        n -= 9
                total += n
            if total % 10 != 0:
                raise forms.ValidationError('Invalid card number (Luhn check failed).')
        return number

    def clean_card_expiry(self):
        expiry = self.cleaned_data.get('card_expiry')
        method = self.data.get('method')
        if method == 'card' and expiry:
            if not re.match(r'^(0[1-9]|1[0-2])\/([0-9]{2})$', expiry):
                raise forms.ValidationError('Expiry must be in MM/YY format.')
            
            # Check if date is in the future
            month, year = map(int, expiry.split('/'))
            year += 2000  # Assume 21st century
            now = datetime.now()
            if year < now.year or (year == now.year and month < now.month):
                raise forms.ValidationError('Card has expired.')
        return expiry

    def clean_card_cvv(self):
        cvv = self.cleaned_data.get('card_cvv')
        method = self.data.get('method')
        if method == 'card' and cvv:
            if not cvv.isdigit() or len(cvv) not in [3, 4]:
                raise forms.ValidationError('CVV must be 3 or 4 digits.')
        return cvv

    def clean(self):
        cleaned_data = super().clean()
        method = cleaned_data.get('method')
        
        if method == 'card':
            if not cleaned_data.get('card_name'):
                self.add_error('card_name', 'Card holder name is required.')
            if not cleaned_data.get('card_number'):
                self.add_error('card_number', 'Card number is required.')
            if not cleaned_data.get('card_expiry'):
                self.add_error('card_expiry', 'Expiry date is required.')
            if not cleaned_data.get('card_cvv'):
                self.add_error('card_cvv', 'CVV is required.')
        elif method == 'razorpay':
            pass
            
        return cleaned_data
