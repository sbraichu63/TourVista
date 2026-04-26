from django.urls import path
from . import views
from .views import calculate_price

app_name = 'bookings'

urlpatterns = [
    path('book/<slug:slug>/', views.book_package, name='book'),

    path('calculate-price/', calculate_price, name='calculate_price'),

    path('payment/<str:booking_ref>/', views.payment_view, name='payment'),
    path('receipt/<str:booking_ref>/', views.receipt_view, name='receipt'),
    path('cancel/<str:booking_ref>/', views.cancel_booking, name='cancel'),
    
    path('download/<str:booking_ref>/', views.download_receipt, name='download_receipt'),
]
