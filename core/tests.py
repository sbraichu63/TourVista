"""
TourVista India - Core Application Tests
Tests for models, views, and basic functionality
"""

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from core.models import TourPackage, Destination, Review, Wishlist
from accounts.models import UserProfile
from bookings.models import Booking, Payment
import uuid


class DestinationModelTest(TestCase):
    def setUp(self):
        self.dest = Destination.objects.create(
            name="Test Destination",
            state='rajasthan',
            description="A test destination"
        )

    def test_destination_creation(self):
        self.assertEqual(self.dest.name, "Test Destination")
        self.assertEqual(self.dest.state, 'rajasthan')

    def test_destination_str(self):
        self.assertIn("Test Destination", str(self.dest))


class TourPackageModelTest(TestCase):
    def setUp(self):
        self.dest = Destination.objects.create(
            name="Rajasthan",
            state='rajasthan',
            description="Land of kings"
        )
        self.package = TourPackage.objects.create(
            title="Rajasthan Golden Triangle",
            destination=self.dest,
            state='rajasthan',
            description="5-day tour of Jaipur, Agra, Delhi",
            duration_days=5,
            price_per_person=25000.00,
            discount_percent=10
        )

    def test_package_creation(self):
        self.assertEqual(self.package.title, "Rajasthan Golden Triangle")
        self.assertEqual(self.package.duration_days, 5)

    def test_package_slug_generation(self):
        self.assertIsNotNone(self.package.slug)
        self.assertEqual(self.package.slug, 'rajasthan-golden-triangle')

    def test_discounted_price(self):
        from decimal import Decimal
        # Price is 25000.00 with 10% discount = 22500.00
        expected = Decimal('22500.00')
        self.assertEqual(self.package.discounted_price, expected)

    def test_nights_property(self):
        self.assertEqual(self.package.nights, 4)  # 5 days = 4 nights


class HomePageViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_homepage_view(self):
        response = self.client.get(reverse('core:home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/index.html')
