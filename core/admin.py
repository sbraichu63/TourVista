from django.contrib import admin
from .models import TourPackage, Destination, Review, Wishlist, Place


@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    list_display = ('name', 'emoji', 'specialty')
    search_fields = ('name', 'specialty')


@admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):
    list_display = ('name', 'state', 'is_featured')
    list_filter = ('state', 'is_featured')
    search_fields = ('name', 'state')
    list_editable = ('is_featured',)


@admin.register(TourPackage)
class TourPackageAdmin(admin.ModelAdmin):
    list_display = ('title', 'state', 'duration_days', 'price_per_person', 'discount_percent', 'is_featured', 'is_active')
    list_filter = ('state', 'difficulty', 'best_season', 'is_featured', 'is_active')
    search_fields = ('title', 'city_name', 'description')
    list_editable = ('is_featured', 'is_active', 'discount_percent')
    prepopulated_fields = {'slug': ('title',)}
    fieldsets = (
        ('Basic Info', {
            'fields': ('title', 'slug', 'destination', 'state', 'city_name', 'description', 'highlights')
        }),
        ('Details', {
            'fields': ('itinerary', 'inclusions', 'exclusions', 'difficulty', 'best_season')
        }),
        ('Pricing & Group', {
            'fields': ('price_per_person', 'discount_percent', 'duration_days', 'max_group_size')
        }),
        ('Travel Info', {
            'fields': ('transportation', 'accommodation')
        }),
        ('Images', {
            'fields': ('main_image', 'image_2', 'image_3', 'image_4')
        }),
        ('Visibility', {
            'fields': ('is_featured', 'is_active')
        }),
    )


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'package', 'rating', 'created_at')
    list_filter = ('rating',)
    search_fields = ('user__username', 'package__title', 'comment')
    readonly_fields = ('created_at',)


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'package', 'added_at')
    search_fields = ('user__username', 'package__title')

