from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.text import slugify
from decimal import Decimal
import uuid


INDIAN_STATES = [
    ('rajasthan', 'Rajasthan'),
    ('goa', 'Goa'),
    ('kerala', 'Kerala'),
    ('himachal_pradesh', 'Himachal Pradesh'),
    ('kashmir', 'Jammu & Kashmir'),
    ('uttarakhand', 'Uttarakhand'),
    ('maharashtra', 'Maharashtra'),
    ('tamil_nadu', 'Tamil Nadu'),
    ('karnataka', 'Karnataka'),
    ('odisha', 'Odisha'),
    ('west_bengal', 'West Bengal'),
    ('gujarat', 'Gujarat'),
    ('andaman', 'Andaman & Nicobar'),
    ('uttar_pradesh', 'Uttar Pradesh'),
    ('northeast', 'Northeast India'),
    ('punjab', 'Punjab'),
    ('madhya_pradesh', 'Madhya Pradesh'),
    ('tripura','Tripura'),
] 

DIFFICULTY_LEVELS = [
    ('easy', 'Easy'),
    ('moderate', 'Moderate'),
    ('challenging', 'Challenging'),
    ('extreme', 'Extreme'),
]

SEASONS = [
    ('all', 'All Year'),
    ('summer', 'Summer (Mar–Jun)'),
    ('monsoon', 'Monsoon (Jul–Sep)'),
    ('autumn', 'Autumn (Oct–Nov)'),
    ('winter', 'Winter (Dec–Feb)'),
]

TRANSPORT_CHOICES = [
    ('flight', 'Flight'),
    ('train', 'Train'),
    ('bus', 'Bus'),
    ('private_cab', 'Private Cab'),
    ('houseboat', 'Houseboat'),
    ('jeep', '4WD Jeep'),
]

ACCOMMODATION_CHOICES = [
    ('luxury_hotel', 'Luxury Hotel (5★)'),
    ('hotel', 'Hotel (3–4★)'),
    ('resort', 'Resort'),
    ('homestay', 'Homestay'),
    ('hostel', 'Hostel'),
    ('camp', 'Camping'),
    ('houseboat', 'Houseboat'),
]


class Destination(models.Model):
    name = models.CharField(max_length=100)
    state = models.CharField(max_length=50, choices=INDIAN_STATES)
    description = models.TextField()
    category = models.CharField(max_length=50, default='Heritage', choices=[
        ('Heritage', 'Heritage'),
        ('Beach', 'Beach'),
        ('Hills', 'Hills'),
        ('Adventure', 'Adventure'),
        ('Spiritual', 'Spiritual'),
        ('Nature', 'Nature'),
    ])
    image = models.ImageField(upload_to='destinations/', null=True, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    is_featured = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name}, {self.get_state_display()}"


class TourPackage(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    destination = models.ForeignKey(Destination, on_delete=models.SET_NULL, null=True, blank=True)
    state = models.CharField(max_length=50, choices=INDIAN_STATES, default='rajasthan')
    description = models.TextField()
    highlights = models.TextField(blank=True, help_text="One highlight per line")
    itinerary = models.TextField(blank=True, help_text="Day-wise itinerary")
    inclusions = models.TextField(blank=True)
    exclusions = models.TextField(blank=True)

    duration_days = models.PositiveIntegerField(default=3)
    max_group_size = models.PositiveIntegerField(default=20)
    price_per_person = models.DecimalField(max_digits=10, decimal_places=2)
    discount_percent = models.PositiveIntegerField(default=0)

    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_LEVELS, default='easy')
    best_season = models.CharField(max_length=20, choices=SEASONS, default='all')
    transportation = models.CharField(max_length=30, choices=TRANSPORT_CHOICES, default='flight')
    accommodation = models.CharField(max_length=30, choices=ACCOMMODATION_CHOICES, default='hotel')

    # Hotel & Transport specifics
    hotel_name = models.CharField(max_length=255, blank=True, help_text="Specific hotel name, e.g. Taj Lake Palace")
    hotel_star_rating = models.PositiveIntegerField(
        null=True, blank=True,
        choices=[(i, f'{i} Star') for i in range(1, 6)],
        help_text="Hotel star rating 1–5"
    )
    transport_details = models.CharField(max_length=255, blank=True, help_text="e.g. Indigo Flight + Private Innova Crysta")

    # Images
    main_image = models.ImageField(upload_to='packages/', null=True, blank=True)
    image_2 = models.ImageField(upload_to='packages/', null=True, blank=True)
    image_3 = models.ImageField(upload_to='packages/', null=True, blank=True)
    image_4 = models.ImageField(upload_to='packages/', null=True, blank=True)

    # Meta
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Location for weather widget
    city_name = models.CharField(max_length=100, blank=True, help_text="City name for weather API (e.g. Jaipur)")

    class Meta:
        ordering = ['-is_featured', '-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while TourPackage.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('core:package_detail', kwargs={'slug': self.slug})

    @property
    def discounted_price(self):
        if self.discount_percent > 0:
            multiplier = Decimal('1') - (Decimal(str(self.discount_percent)) / Decimal('100'))
            return (self.price_per_person * multiplier).quantize(Decimal('1.00'))
        return self.price_per_person

    @property
    def discount_savings(self):
        if self.discount_percent > 0:
            return self.price_per_person - self.discounted_price
        return Decimal('0')

    @property
    def avg_rating(self):
        reviews = self.reviews.all()
        if reviews.exists():
            return round(sum(r.rating for r in reviews) / reviews.count(), 1)
        return 0

    @property
    def review_count(self):
        return self.reviews.count()

    @property
    def highlights_list(self):
        return [l.strip() for l in self.highlights.splitlines() if l.strip()]

    @property
    def itinerary_list(self):
        return [l.strip() for l in self.itinerary.splitlines() if l.strip()]

    @property
    def inclusions_list(self):
        return [l.strip() for l in self.inclusions.splitlines() if l.strip()]

    @property
    def exclusions_list(self):
        return [l.strip() for l in self.exclusions.splitlines() if l.strip()]

    @property
    def nights(self):
        return self.duration_days - 1


class Review(models.Model):
    package = models.ForeignKey(TourPackage, related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(default=5, choices=[(i, i) for i in range(1, 6)])
    title = models.CharField(max_length=100, blank=True)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('package', 'user')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} → {self.package.title} ({self.rating}★)"


class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist')
    package = models.ForeignKey(TourPackage, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'package')

    def __str__(self):
        return f"{self.user.username} ♥ {self.package.title}"


class Place(models.Model):
    """Stores notable places with their specialties for the itinerary hover tooltip feature."""
    name = models.CharField(max_length=150, unique=True)
    specialty = models.TextField(help_text="Short description of what makes this place special")
    emoji = models.CharField(max_length=10, blank=True, default='📍')
    image = models.ImageField(upload_to='places/', blank=True, null=True, help_text="Upload a cover photo for the tooltip")

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
