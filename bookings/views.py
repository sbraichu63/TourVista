from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.http import FileResponse, HttpResponse
import io

from core.models import TourPackage
from .models import Booking, Payment
from .forms import BookingForm, PaymentForm


@login_required
def book_package(request, slug):
    package = get_object_or_404(TourPackage, slug=slug, is_active=True)

    # Check email verification
    try:
        profile = request.user.profile
        if not profile.email_verified:
            messages.warning(request, '⚠️ Please verify your email before booking. Check your inbox or resend verification.')
            return redirect('accounts:dashboard')
    except Exception:
        pass

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.package = package
            booking.price_per_person = package.discounted_price
            booking.total_amount = package.discounted_price * form.cleaned_data['num_travellers']
            booking.status = 'pending'
            booking.save()
            return redirect('bookings:payment', booking_ref=booking.booking_ref)
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        form = BookingForm(initial={
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
        })
        try:
            form.fields['phone'].initial = request.user.profile.phone
        except Exception:
            pass

    context = {
        'form': form,
        'package': package,
    }
    return render(request, 'bookings/book.html', context)


@login_required
def payment_view(request, booking_ref):
    booking = get_object_or_404(Booking, booking_ref=booking_ref, user=request.user)

    if booking.status == 'confirmed':
        return redirect('bookings:receipt', booking_ref=booking_ref)

    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            method = form.cleaned_data['method']
            card_last4 = ''
            upi_id = ''

            if method == 'card':
                raw = form.cleaned_data.get('card_number', '').replace(' ', '')
                card_last4 = raw[-4:] if len(raw) >= 4 else '0000'
            elif method == 'upi':
                upi_id = form.cleaned_data.get('upi_id', '')

            payment = Payment.objects.create(
                booking=booking,
                amount=booking.total_amount,
                method=method,
                status='paid',
                card_last4=card_last4,
                upi_id=upi_id,
                paid_at=timezone.now(),
            )

            booking.status = 'confirmed'
            booking.save()

            # Send confirmation email
            try:
                dashboard_url = request.build_absolute_uri('/accounts/dashboard/')
                send_mail(
                    subject=f'✅ Booking Confirmed — {booking.package.title} | TourVista India',
                    message=f'''Hi {booking.first_name}!

Your booking is CONFIRMED! 🎉

📋 Booking Reference: #{booking.booking_ref}
🌏 Package: {booking.package.title}
📅 Travel Date: {booking.travel_date.strftime("%d %B %Y")}
👥 Travellers: {booking.num_travellers}
💰 Amount Paid: ₹{booking.total_amount:,.0f}
🎫 Receipt: {payment.receipt_number}

View your booking: {dashboard_url}

Happy Travels! 🇮🇳
— Team TourVista India
''',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[booking.email],
                    fail_silently=True,
                )
            except Exception:
                pass

            messages.success(request, f'🎉 Payment successful! Booking confirmed.')
            return redirect('bookings:receipt', booking_ref=booking_ref)
        else:
            messages.error(request, 'Please check your payment details.')
    else:
        form = PaymentForm()

    context = {
        'booking': booking,
        'package': booking.package,
        'form': form,
    }
    return render(request, 'bookings/payment.html', context)


@login_required
def receipt_view(request, booking_ref):
    booking = get_object_or_404(Booking, booking_ref=booking_ref, user=request.user)
    try:
        payment = booking.payment
    except Payment.DoesNotExist:
        payment = None

    context = {
        'booking': booking,
        'payment': payment,
        'package': booking.package,
    }
    return render(request, 'bookings/receipt.html', context)


@login_required
def cancel_booking(request, booking_ref):
    booking = get_object_or_404(Booking, booking_ref=booking_ref, user=request.user)

    if booking.status in ['cancelled', 'completed']:
        messages.warning(request, 'This booking cannot be cancelled.')
        return redirect('accounts:dashboard')

    if request.method == 'POST':
        booking.status = 'cancelled'
        booking.save()
        messages.success(request, f'Booking #{booking.booking_ref} has been cancelled.')
        return redirect('accounts:dashboard')

    return render(request, 'bookings/cancel_confirm.html', {'booking': booking})


@login_required
def download_receipt(request, booking_ref):
    """Generate PDF receipt using reportlab"""
    booking = get_object_or_404(Booking, booking_ref=booking_ref, user=request.user)

    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import cm
        from reportlab.lib import colors

        buf = io.BytesIO()
        c = canvas.Canvas(buf, pagesize=A4)
        w, h = A4

        # Header
        c.setFillColor(colors.HexColor('#FF6B35'))
        c.rect(0, h - 80, w, 80, fill=True, stroke=False)
        c.setFillColor(colors.white)
        c.setFont('Helvetica-Bold', 22)
        c.drawString(40, h - 50, 'TourVista India')
        c.setFont('Helvetica', 12)
        c.drawString(40, h - 68, 'Your Gateway to Incredible India')

        # Receipt number
        c.setFillColor(colors.HexColor('#0D1B2A'))
        c.setFont('Helvetica-Bold', 16)
        c.drawString(40, h - 120, f'BOOKING RECEIPT')
        c.setFont('Helvetica', 11)
        c.drawString(40, h - 140, f'Receipt No: {booking.payment.receipt_number if hasattr(booking, "payment") else "N/A"}')
        c.drawString(40, h - 158, f'Booking Ref: #{booking.booking_ref}')

        y = h - 200
        details = [
            ('Package', booking.package.title),
            ('Passenger Name', booking.full_name),
            ('Email', booking.email),
            ('Phone', booking.phone),
            ('Travel Date', booking.travel_date.strftime('%d %B %Y')),
            ('Number of Travellers', str(booking.num_travellers)),
            ('Price Per Person', f'Rs. {booking.price_per_person:,.2f}'),
            ('Total Amount', f'Rs. {booking.total_amount:,.2f}'),
            ('Payment Status', 'PAID'),
            ('Booking Status', booking.status.upper()),
        ]

        for label, value in details:
            c.setFont('Helvetica-Bold', 10)
            c.drawString(40, y, f'{label}:')
            c.setFont('Helvetica', 10)
            c.drawString(200, y, value)
            y -= 22

        # Footer
        c.setFillColor(colors.HexColor('#FF6B35'))
        c.rect(0, 0, w, 40, fill=True, stroke=False)
        c.setFillColor(colors.white)
        c.setFont('Helvetica', 9)
        c.drawCentredString(w / 2, 15, 'TourVista India | noreply@tourvista.in | www.tourvista.in')

        c.save()
        buf.seek(0)
        return FileResponse(buf, as_attachment=True, filename=f'TourVista_Receipt_{booking.booking_ref}.pdf')

    except ImportError:
        return HttpResponse('PDF generation requires reportlab. Install it with: pip install reportlab', status=500)
