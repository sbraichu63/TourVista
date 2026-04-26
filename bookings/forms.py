from django import forms
from .models import Booking, Payment


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
        from django.utils import timezone
        import datetime
        date = self.cleaned_data['travel_date']
        if date < (timezone.now().date() + datetime.timedelta(days=1)):
            raise forms.ValidationError('Travel date must be at least tomorrow.')
        return date


class PaymentForm(forms.Form):
    METHOD_CHOICES = [
        ('upi', '💳 UPI'),
        ('card', '💳 Credit / Debit Card'),
        ('netbanking', '🏦 Net Banking'),
        ('wallet', '📱 Digital Wallet'),
    ]
    method = forms.ChoiceField(
        choices=METHOD_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'payment-radio'}),
        initial='upi'
    )

    # UPI fields
    upi_id = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'yourname@upi', 'id': 'id_upi_id'})
    )

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

    def clean(self):
        cleaned_data = super().clean()
        method = cleaned_data.get('method')
        if method == 'upi' and not cleaned_data.get('upi_id'):
            self.add_error('upi_id', 'Please enter your UPI ID.')
        if method == 'card':
            if not cleaned_data.get('card_name'):
                self.add_error('card_name', 'Card holder name is required.')
            if not cleaned_data.get('card_number'):
                self.add_error('card_number', 'Card number is required.')
        return cleaned_data
