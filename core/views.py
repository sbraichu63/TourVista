from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Avg
from .models import TourPackage, Destination, Review, Wishlist, Place, INDIAN_STATES, SEASONS, DIFFICULTY_LEVELS
from django import forms
import json


# ──────────────────────────────────────────────────────────────────
# HOMEPAGE
# ──────────────────────────────────────────────────────────────────
def homepage(request):
    featured_packages = TourPackage.objects.filter(is_featured=True, is_active=True)[:6]
    latest_packages = TourPackage.objects.filter(is_active=True).order_by('-created_at')[:8]
    featured_destinations = Destination.objects.filter(is_featured=True)[:8]
    total_packages = TourPackage.objects.filter(is_active=True).count()
    total_destinations = Destination.objects.count()
    
    # Stats for homepage
    context = {
        'featured_packages': featured_packages,
        'latest_packages': latest_packages,
        'featured_destinations': featured_destinations,
        'total_packages': total_packages,
        'total_destinations': total_destinations,
        'states': INDIAN_STATES,
    }
    return render(request, 'core/index.html', context)


# ──────────────────────────────────────────────────────────────────
# PACKAGES LIST (with filters)
# ──────────────────────────────────────────────────────────────────
def package_list(request):
    packages = TourPackage.objects.filter(is_active=True)

    # Filters
    state = request.GET.get('state', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    duration = request.GET.get('duration', '')
    season = request.GET.get('season', '')
    difficulty = request.GET.get('difficulty', '')
    search = request.GET.get('q', '')
    sort = request.GET.get('sort', 'featured')

    if search:
        packages = packages.filter(
            Q(title__icontains=search) |
            Q(description__icontains=search) |
            Q(city_name__icontains=search)
        )
    if state:
        packages = packages.filter(state=state)
    if min_price:
        packages = packages.filter(price_per_person__gte=min_price)
    if max_price:
        packages = packages.filter(price_per_person__lte=max_price)
    if duration:
        if duration == '1-3':
            packages = packages.filter(duration_days__lte=3)
        elif duration == '4-7':
            packages = packages.filter(duration_days__gte=4, duration_days__lte=7)
        elif duration == '8+':
            packages = packages.filter(duration_days__gte=8)
    if season:
        packages = packages.filter(best_season=season)
    if difficulty:
        packages = packages.filter(difficulty=difficulty)
    # Sorting
    if sort == 'price_low':
        packages = packages.order_by('price_per_person')
    elif sort == 'price_high':
        packages = packages.order_by('-price_per_person')
    elif sort == 'deals':
        packages = packages.order_by('-discount_percent')
    elif sort == 'duration':
        packages = packages.order_by('duration_days')
    elif sort == 'newest':
        packages = packages.order_by('-created_at')
    else:
        packages = packages.order_by('-is_featured', '-created_at')

    # Wishlist check
    wishlist_ids = []
    if request.user.is_authenticated:
        wishlist_ids = list(
            Wishlist.objects.filter(user=request.user).values_list('package_id', flat=True)
        )

    context = {
        'packages': packages,
        'wishlist_ids': wishlist_ids,
        'states': INDIAN_STATES,
        'seasons': SEASONS,
        'difficulties': DIFFICULTY_LEVELS,
        'selected_state': state,
        'selected_season': season,
        'selected_difficulty': difficulty,
        'selected_duration': duration,
        'min_price': min_price,
        'max_price': max_price,
        'search': search,
        'sort': sort,
        'total_count': packages.count(),
    }
    return render(request, 'core/packages.html', context)


# ──────────────────────────────────────────────────────────────────
# PACKAGE DETAIL
# ──────────────────────────────────────────────────────────────────
def package_detail(request, slug):
    package = get_object_or_404(TourPackage, slug=slug, is_active=True)
    reviews = package.reviews.select_related('user').all()
    related = TourPackage.objects.filter(state=package.state, is_active=True).exclude(pk=package.pk)[:3]

    in_wishlist = False
    user_review = None
    if request.user.is_authenticated:
        in_wishlist = Wishlist.objects.filter(user=request.user, package=package).exists()
        user_review = reviews.filter(user=request.user).first()

    # Handle review submission
    if request.method == 'POST' and request.user.is_authenticated:
        if not user_review:
            rating = int(request.POST.get('rating', 5))
            title = request.POST.get('title', '')
            comment = request.POST.get('comment', '')
            if comment:
                Review.objects.create(
                    package=package,
                    user=request.user,
                    rating=rating,
                    title=title,
                    comment=comment
                )
                messages.success(request, '✅ Your review has been submitted!')
                return redirect('core:package_detail', slug=slug)
        else:
            messages.warning(request, 'You have already reviewed this package.')

    # Rating distribution (list of dicts for easier template looping)
    rating_counts = {i: 0 for i in range(1, 6)}
    for r in reviews:
        rating_counts[r.rating] += 1
    
    rating_dist = []
    total_reviews = reviews.count()
    for i in range(5, 0, -1):
        count = rating_counts[i]
        percent = (count / total_reviews * 100) if total_reviews > 0 else 0
        rating_dist.append({
            'rating': i,
            'count': count,
            'percent': percent,
        })

    places_json = json.dumps([
        {'name': p.name, 'specialty': p.specialty, 'emoji': p.emoji, 'image_url': p.image.url if p.image else ''}
        for p in Place.objects.all()
    ])

    context = {
        'package': package,
        'reviews': reviews,
        'related': related,
        'in_wishlist': in_wishlist,
        'user_review': user_review,
        'rating_dist': rating_dist,
        'avg_rating': package.avg_rating,
        'review_count': package.review_count,
        'places_json': places_json,
    }
    return render(request, 'core/package_detail.html', context)


# ──────────────────────────────────────────────────────────────────
# WISHLIST
# ──────────────────────────────────────────────────────────────────
@login_required
def toggle_wishlist(request, pk):
    package = get_object_or_404(TourPackage, pk=pk)
    obj, created = Wishlist.objects.get_or_create(user=request.user, package=package)
    if not created:
        obj.delete()
        return JsonResponse({'status': 'removed'})
    return JsonResponse({'status': 'added'})


# ──────────────────────────────────────────────────────────────────
# SEASONS PAGE
# ──────────────────────────────────────────────────────────────────
def seasons_view(request):
    packages = TourPackage.objects.filter(is_active=True)
    months = [
        "January", "February", "March", "April", "May", "June", 
        "July", "August", "September", "October", "November", "December"
    ]
    return render(request, 'core/seasons.html', {
        'packages': packages,
        'months': months
    })


# ──────────────────────────────────────────────────────────────────
# ABOUT US
# ──────────────────────────────────────────────────────────────────
def about_view(request):
    return render(request, 'core/about.html')


# ──────────────────────────────────────────────────────────────────
# EXPLORE MAP PAGE
# ──────────────────────────────────────────────────────────────────
def explore_map(request):
    packages = TourPackage.objects.filter(is_active=True)
    return render(request, 'core/map.html', {'packages': packages})
