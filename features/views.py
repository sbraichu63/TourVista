import json
import requests
import logging
import datetime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
from django.shortcuts import render
from django.db.models import Q, Avg
from core.models import TourPackage, Destination

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────
# WEATHER API
# ──────────────────────────────────────────────────────────────────
def weather_api(request):
    city = request.GET.get('city', 'New Delhi')
    api_key = settings.OPENWEATHERMAP_API_KEY

    if not api_key or api_key == 'YOUR_OWM_KEY_HERE':
        # Return mock data for development
        mock = {
            "city": city,
            "temp": 28,
            "feels_like": 31,
            "description": "Partly cloudy",
            "icon": "02d",
            "humidity": 65,
            "wind_speed": 12,
            "forecast": [
                {"day": "Mon", "icon": "01d", "high": 32, "low": 24},
                {"day": "Tue", "icon": "02d", "high": 30, "low": 23},
                {"day": "Wed", "icon": "10d", "high": 27, "low": 21},
                {"day": "Thu", "icon": "03d", "high": 29, "low": 22},
                {"day": "Fri", "icon": "01d", "high": 33, "low": 25},
            ],
            "mock": True
        }
        return JsonResponse(mock)

    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city},IN&appid={api_key}&units=metric"
        resp = requests.get(url, timeout=5)
        data = resp.json()

        if resp.status_code != 200:
            return JsonResponse({"error": "City not found"}, status=404)

        # Forecast
        forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?q={city},IN&appid={api_key}&units=metric&cnt=5"
        forecast_resp = requests.get(forecast_url, timeout=5)
        forecast_data = forecast_resp.json()

        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        forecast = []
        if forecast_resp.status_code == 200:
            for item in forecast_data.get('list', [])[:5]:
                dt = datetime.datetime.fromtimestamp(item['dt'])
                forecast.append({
                    "day": days[dt.weekday()],
                    "icon": item['weather'][0]['icon'],
                    "high": round(item['main']['temp_max']),
                    "low": round(item['main']['temp_min']),
                })

        return JsonResponse({
            "city": data['name'],
            "temp": round(data['main']['temp']),
            "feels_like": round(data['main']['feels_like']),
            "description": data['weather'][0]['description'].title(),
            "icon": data['weather'][0]['icon'],
            "humidity": data['main']['humidity'],
            "wind_speed": round(data['wind']['speed'] * 3.6),  # m/s to km/h
            "forecast": forecast,
            "mock": False
        })
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    except requests.RequestException as e:
        logger.error(f'Weather API request failed: {str(e)}')
        return JsonResponse({"error": "Unable to fetch weather data"}, status=500)


# ──────────────────────────────────────────────────────────────────
# AI CHATBOT
# ──────────────────────────────────────────────────────────────────
CHATBOT_KNOWLEDGE = {
    "rajasthan": "Rajasthan is the land of kings! Best visited Oct–Mar. Top spots: Jaipur (Pink City), Jodhpur (Blue City), Udaipur (City of Lakes), Jaisalmer (Golden City). Average cost: ₹15,000–₹40,000 per person for 5–7 days.",
    "goa": "Goa is India's beach paradise! Best Nov–Feb. North Goa (Baga, Calangute) is lively; South Goa (Palolem, Agonda) is peaceful. Don't miss: Dudhsagar Falls, spice plantations, Portuguese forts.",
    "kerala": "Kerala — God's Own Country! Best Sep–Mar. Must-do: houseboat ride in Alleppey backwaters, tea gardens of Munnar, Kovalam beach. Wildlife at Periyar. Average cost: ₹12,000–₹35,000 for 5 days.",
    "manali": "Manali in Himachal Pradesh is stunning! Best for snow: Dec–Feb, adventure: Jun–Sep. Must visit: Rohtang Pass, Solang Valley, Old Manali, Hadimba Temple.",
    "kashmir": "Kashmir — Heaven on Earth! Best Apr–Oct. Srinagar's Dal Lake shikara rides, Gulmarg for skiing, Pahalgam for trekking. Avoid Dec–Feb (heavy snow).",
    "rishikesh": "Rishikesh is India's adventure capital! Best Oct–May. Activities: white water rafting, bungee jumping, yoga retreats. Also visit Haridwar (30 km). Budget trip: ₹5,000–₹15,000 for 3 days.",
    "agra": "Agra — home of the Taj Mahal! Best Oct–Mar. Must see: Taj Mahal (sunrise!), Agra Fort, Fatehpur Sikri. Day trip from Delhi or combine with Rajasthan Golden Triangle tour.",
    "andaman": "Andaman & Nicobar — India's best beaches! Best Nov–Apr. Top: Radhanagar Beach, Havelock Island, Neil Island, scuba diving. Permit required for Andaman (easily obtained).",
    "ooty": "Ooty (Udhagamandalam) in Tamil Nadu — Queen of Hills! Best Mar–Jun, Sep–Nov. Must see: Nilgiri Mountain Railway, Ooty Lake, Botanical Gardens, tea estates.",
    "budget": "India tour budget tips: Budget ₹2,000–₹3,000/day for backpacker style (hostel + local food + buses). ₹5,000–₹8,000/day for mid-range (3-star hotel + some activities). ₹15,000+/day for luxury. Book flights 3–6 months early for best deals!",
    "visa": "Indian citizens don't need a visa for domestic travel! For foreign tourists, India offers e-Visa for 60+ countries at indianvisaonline.gov.in. Tourist visa: up to 180 days.",
    "season": "India travel seasons: Oct–Mar is peak (pleasant weather everywhere). Apr–Jun is summer (good for hills: Manali, Shimla, Ooty). Jul–Sep is monsoon (Kerala, Northeast India are beautiful; avoid Rajasthan/Goa). Dec–Jan: cold in north, perfect in south.",
    "packing": "India packing essentials: Lightweight cotton clothes, sunscreen SPF50+, mosquito repellent, ORS packets, hand sanitizer, travel adapter (Type D/M plugs), comfortable walking shoes, scarf (for temples), rain cover for bags.",
    "food": "Indian food is amazing! Must try: Rajasthan's Dal Baati Churma, Kerala's Fish Curry with Appam, Goa's Fish Curry Rice, Punjab's Butter Chicken, Gujarat's Dhokla. Always drink bottled water. Street food is great if it's hot and freshly made!",
    "booking": "To book a package on TourVista: 1) Browse packages and pick your destination 2) Click 'Book Now' 3) Fill your details and travel date 4) Complete payment via UPI/Card/Net Banking 5) Get instant confirmation email. You can view booking history in your dashboard.",
    "cancel": "To cancel a booking: Go to your Dashboard → My Bookings → Select booking → Click Cancel. Cancellations made 7+ days before travel date get 80% refund. 3–7 days: 50% refund. Less than 3 days: no refund.",
    "default": "Hello! I'm TourVista's travel assistant. I can help you with:\n🏝️ Destination info (Goa, Rajasthan, Kerala, Kashmir…)\n💰 Budget planning\n📅 Best time to visit\n🎒 Packing tips\n🍛 Food recommendations\n📋 Booking & cancellation queries\n\nJust ask me anything about India travel!"
}

@require_http_methods(["POST"])
def chatbot_api(request):
    try:
        body = json.loads(request.body)
        user_message = body.get('message', '').lower().strip()
    except json.JSONDecodeError as e:
        logger.warning(f'Invalid JSON in chatbot request: {str(e)}')
        return JsonResponse({"error": "Invalid request"}, status=400)

    if not user_message:
        return JsonResponse({"reply": CHATBOT_KNOWLEDGE["default"]})

    # Try Gemini API first
    gemini_key = settings.GEMINI_API_KEY
    if gemini_key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel('gemini-pro')
            system_prompt = (
                "You are Vistara, TourVista India's premium AI travel concierge. "
                "You are an expert in Indian tourism. "
                "Guidelines:\n"
                "1. Answer ONLY questions about Indian travel, destinations, packages, and bookings.\n"
                "2. Be extremely friendly, professional, and helpful. Use emojis! 🌏🏔️🏝️\n"
                "3. Keep responses concise (under 150 words).\n"
                "4. Use Markdown for formatting: **bold** for emphasis, *italics* for highlights.\n"
                "5. Always mention prices in Indian Rupees (₹).\n"
                "6. If asked about a specific destination, try to sound enthusiastic about its unique features.\n"
                "7. If a user asks something out of scope, politely redirect them back to travel."
            )
            response = model.generate_content(f"{system_prompt}\n\nUser: {user_message}")
            return JsonResponse({"reply": response.text, "source": "gemini"})
        except Exception as e:
            logger.debug(f'Gemini API failed, using fallback: {str(e)}')

    # Check for destination/package mentions
    matching_packages = TourPackage.objects.filter(
        Q(title__icontains=user_message) | 
        Q(state__icontains=user_message) | 
        Q(city_name__icontains=user_message) |
        Q(description__icontains=user_message)
    ).filter(is_active=True)[:3]

    if matching_packages.exists():
        tours_data = []
        for pkg in matching_packages:
            tours_data.append({
                "title": pkg.title,
                "price": f"{int(pkg.discounted_price):,}",
                "image": pkg.main_image.url if pkg.main_image else "/static/img/placeholder.jpg",
                "url": pkg.get_absolute_url()
            })
            
        reply = "I found some incredible packages matching your interest! 🌏\n\nTake a look at these hand-picked options:"
        return JsonResponse({
            "reply": reply, 
            "source": "database",
            "tours": tours_data,
            "quick_replies": ["Plan a budget", "Best destinations", "Travel tips"]
        })

    keywords = {
        "rajasthan": ["rajasthan", "jaipur", "jodhpur", "udaipur", "jaisalmer", "pink city"],
        "goa": ["goa", "baga", "calangute", "palolem", "beach", "coastal"],
        "kerala": ["kerala", "munnar", "alleppey", "kochi", "backwater", "god's own"],
        "manali": ["manali", "himachal", "rohtang", "solang", "spiti", "lahaul"],
        "kashmir": ["kashmir", "srinagar", "gulmarg", "pahalgam", "dal lake"],
        "rishikesh": ["rishikesh", "haridwar", "uttarakhand", "rafting", "yoga", "bungee"],
        "agra": ["agra", "taj mahal", "fatehpur", "uttar pradesh"],
        "andaman": ["andaman", "nicobar", "havelock", "neil island", "scuba"],
        "ooty": ["ooty", "tamil", "nilgiri", "coorg", "kodaikanal"],
        "budget": ["budget", "cost", "price", "cheap", "expensive", "afford", "money"],
        "season": ["season", "when to visit", "best time", "monsoon", "winter", "summer"],
        "packing": ["pack", "carry", "luggage", "clothes", "what to bring"],
        "food": ["food", "eat", "restaurant", "cuisine", "dish", "thali"],
        "booking": ["book", "reserve", "how to", "purchase", "buy package"],
        "cancel": ["cancel", "refund", "cancellation", "money back"],
    }

    for topic, kws in keywords.items():
        if any(kw in user_message for kw in kws):
            return JsonResponse({
                "reply": CHATBOT_KNOWLEDGE[topic], 
                "source": "rule-based",
                "quick_replies": ["Plan a budget", "Best destinations", "Travel tips"]
            })

    return JsonResponse({
        "reply": CHATBOT_KNOWLEDGE["default"], 
        "source": "rule-based",
        "quick_replies": ["Goa", "Rajasthan", "Manali", "Kashmir"]
    })



# ──────────────────────────────────────────────────────────────────
# BUDGET CALCULATOR
# ──────────────────────────────────────────────────────────────────
BUDGET_DATA = {
    "rajasthan":       {"hotel": 2800, "food": 700, "transport": 1000, "activities": 500,  "flight": 4500},
    "goa":             {"hotel": 3800, "food": 950, "transport": 700,  "activities": 900,  "flight": 5500},
    "kerala":          {"hotel": 3400, "food": 750, "transport": 1100, "activities": 800,  "flight": 6500},
    "himachal_pradesh":{"hotel": 2600, "food": 650, "transport": 1600, "activities": 1200, "flight": 5000},
    "kashmir":         {"hotel": 4200, "food": 850, "transport": 2000, "activities": 1000, "flight": 7000},
    "uttarakhand":     {"hotel": 2200, "food": 550, "transport": 1200, "activities": 1100, "flight": 4500},
    "maharashtra":     {"hotel": 3600, "food": 900, "transport": 900,  "activities": 600,  "flight": 4000},
    "tamil_nadu":      {"hotel": 2900, "food": 600, "transport": 1000, "activities": 500,  "flight": 6000},
    "karnataka":       {"hotel": 3200, "food": 800, "transport": 1100, "activities": 700,  "flight": 5500},
    "west_bengal":     {"hotel": 2700, "food": 700, "transport": 900,  "activities": 800,  "flight": 5800},
    "odisha":          {"hotel": 2400, "food": 650, "transport": 1000, "activities": 600,  "flight": 5500},
    "gujarat":         {"hotel": 2500, "food": 750, "transport": 1200, "activities": 400,  "flight": 4800},
    "andaman":         {"hotel": 5000, "food": 1200, "transport": 2200, "activities": 1800, "flight": 11000},
    "uttar_pradesh":   {"hotel": 2400, "food": 600, "transport": 1100, "activities": 900,  "flight": 4000},
    "northeast":       {"hotel": 2600, "food": 600, "transport": 1800, "activities": 1200, "flight": 8500},
    "punjab":          {"hotel": 2200, "food": 800, "transport": 1000, "activities": 400,  "flight": 4500},
    "madhya_pradesh":  {"hotel": 2100, "food": 500, "transport": 1100, "activities": 700,  "flight": 5000},
    "tripura":         {"hotel": 1900, "food": 450, "transport": 1400, "activities": 500,  "flight": 8000},
    "default":         {"hotel": 2800, "food": 700, "transport": 1000, "activities": 700,  "flight": 5000},
}

# Multipliers for different categories based on stay type
STAY_MULTIPLIERS = {
    "budget":   {"hotel": 0.5, "food": 0.6, "transport": 0.8, "activities": 0.7, "flight": 1.0},
    "standard": {"hotel": 1.0, "food": 1.0, "transport": 1.0, "activities": 1.0, "flight": 1.0},
    "luxury":   {"hotel": 3.5, "food": 2.5, "transport": 2.2, "activities": 2.0, "flight": 2.5},
}

def budget_calculator(request):
    destination = request.GET.get('destination', 'default').lower().replace(' ', '_')
    days = int(request.GET.get('days', 5))
    travellers = int(request.GET.get('travellers', 2))
    accommodation = request.GET.get('accommodation', 'standard')

    base = BUDGET_DATA.get(destination, BUDGET_DATA['default'])
    mults = STAY_MULTIPLIERS.get(accommodation, STAY_MULTIPLIERS['standard'])

    # Calculate per category
    hotel_per_day = base['hotel'] * mults['hotel']
    food_per_day = base['food'] * mults['food']
    activities_per_day = base['activities'] * mults['activities']
    
    # Transport scaling (slightly less per person for groups)
    transport_base = base['transport'] * mults['transport']
    transport_total = transport_base * days * (1 + (travellers - 1) * 0.4)
    
    # Flights (one-time per person)
    flight_per_person = base['flight'] * mults['flight']
    flight_total = flight_per_person * travellers

    hotel_total = hotel_per_day * days * travellers
    food_total = food_per_day * days * travellers
    activities_total = activities_per_day * days * travellers

    grand_total = hotel_total + food_total + transport_total + activities_total + flight_total
    per_person = grand_total / max(travellers, 1)

    return JsonResponse({
        "breakdown": {
            "hotel": round(hotel_total),
            "food": round(food_total),
            "transport": round(transport_total),
            "activities": round(activities_total),
            "flights": round(flight_total),
        },
        "per_person": round(per_person),
        "grand_total": round(grand_total),
        "days": days,
        "travellers": travellers,
        "destination": destination.replace('_', ' ').title(),
        "tier": accommodation.title()
    })


# ──────────────────────────────────────────────────────────────────
# NEARBY DESTINATIONS (for map)
# ──────────────────────────────────────────────────────────────────
INDIA_DESTINATIONS = [
    {"name": "Jaipur", "lat": 26.9124, "lng": 75.7873, "state": "Rajasthan", "type": "Heritage"},
    {"name": "Udaipur", "lat": 24.5854, "lng": 73.7125, "state": "Rajasthan", "type": "Lakes"},
    {"name": "Goa", "lat": 15.2993, "lng": 74.1240, "state": "Goa", "type": "Beach"},
    {"name": "Munnar", "lat": 10.0889, "lng": 77.0595, "state": "Kerala", "type": "Hills"},
    {"name": "Alleppey", "lat": 9.4981, "lng": 76.3388, "state": "Kerala", "type": "Backwater"},
    {"name": "Manali", "lat": 32.2396, "lng": 77.1887, "state": "Himachal Pradesh", "type": "Adventure"},
    {"name": "Shimla", "lat": 31.1048, "lng": 77.1734, "state": "Himachal Pradesh", "type": "Hills"},
    {"name": "Srinagar", "lat": 34.0837, "lng": 74.7973, "state": "Kashmir", "type": "Lakes"},
    {"name": "Rishikesh", "lat": 30.0869, "lng": 78.2676, "state": "Uttarakhand", "type": "Adventure"},
    {"name": "Agra", "lat": 27.1767, "lng": 78.0081, "state": "Uttar Pradesh", "type": "Heritage"},
    {"name": "Varanasi", "lat": 25.3176, "lng": 82.9739, "state": "Uttar Pradesh", "type": "Spiritual"},
    {"name": "Darjeeling", "lat": 27.0410, "lng": 88.2663, "state": "West Bengal", "type": "Hills"},
    {"name": "Andaman Islands", "lat": 11.7401, "lng": 92.6586, "state": "Andaman", "type": "Beach"},
    {"name": "Mysore", "lat": 12.2958, "lng": 76.6394, "state": "Karnataka", "type": "Heritage"},
    {"name": "Coorg", "lat": 12.3375, "lng": 75.8069, "state": "Karnataka", "type": "Nature"},
    {"name": "Ooty", "lat": 11.4102, "lng": 76.6950, "state": "Tamil Nadu", "type": "Hills"},
    {"name": "Jaisalmer", "lat": 26.9157, "lng": 70.9083, "state": "Rajasthan", "type": "Desert"},
    {"name": "Jodhpur", "lat": 26.2389, "lng": 73.0243, "state": "Rajasthan", "type": "Heritage"},
]

def destinations_map(request):
    dest_list = Destination.objects.all()
    
    if not dest_list.exists():
        # Fallback to hardcoded if DB is empty (for dev)
        return JsonResponse({"destinations": INDIA_DESTINATIONS})

    data = []
    for d in dest_list:
        if d.latitude and d.longitude:
            # Count active packages for this destination
            pkg_count = TourPackage.objects.filter(destination=d, is_active=True).count()
            
            # Fix for missing image
            image_url = d.image.url if d.image else "https://images.unsplash.com/photo-1524492412937-b28074a5d7da?auto=format&fit=crop&w=600&q=80"
            
            # Fix for description
            desc = d.description[:100] + "..." if d.description else "Discover the beauty and culture of " + d.name + "."
            
            # Fix for state display (if code is used)
            state_display = d.get_state_display()
            if len(state_display) <= 3: # Likely a code like 'MH'
                state_map = {'MH': 'Maharashtra', 'RJ': 'Rajasthan', 'GA': 'Goa', 'KL': 'Kerala', 'HP': 'Himachal Pradesh'}
                state_display = state_map.get(state_display, state_display)

            data.append({
                "id": d.id,
                "name": d.name,
                "lat": float(d.latitude),
                "lng": float(d.longitude),
                "state": state_display,
                "type": d.category,
                "image": image_url,
                "pkg_count": pkg_count,
                "description": desc
            })
            
    return JsonResponse({"destinations": data})


# ──────────────────────────────────────────────────────────────────
# TRAVEL STYLE QUIZ API
# ──────────────────────────────────────────────────────────────────
@require_http_methods(["POST"])
def quiz_api(request):
    try:
        data = json.loads(request.body)
        terrain = data.get('terrain') # hills, beach, heritage, nature, spiritual
        duration = data.get('duration') # short, medium, long
        pace = data.get('pace')       # easy, moderate, challenging
        comfort = data.get('comfort') # budget, standard, luxury
        budget = data.get('budget')   # low, mid, high
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid data"}, status=400)

    # --- Step 1: Initial Filtering ---
    packages = TourPackage.objects.filter(is_active=True)

    # 1. Terrain (Essential)
    if terrain:
        packages = packages.filter(destination__category__iexact=terrain)

    # 2. Duration
    if duration == 'short':
        packages = packages.filter(duration_days__lte=3)
    elif duration == 'medium':
        packages = packages.filter(duration_days__gt=3, duration_days__lte=6)
    elif duration == 'long':
        packages = packages.filter(duration_days__gt=6)

    # 3. Pace
    if pace:
        packages = packages.filter(difficulty__iexact=pace)

    # 4. Comfort
    if comfort == 'luxury':
        packages = packages.filter(accommodation__in=['luxury_hotel', 'resort'])
    elif comfort == 'budget':
        packages = packages.filter(accommodation__in=['hostel', 'camp', 'homestay'])

    # 5. Budget
    if budget == 'low':
        packages = packages.filter(price_per_person__lt=15000)
    elif budget == 'mid':
        packages = packages.filter(price_per_person__gte=15000, price_per_person__lte=40000)
    elif budget == 'high':
        packages = packages.filter(price_per_person__gt=40000)

    # --- Step 2: Intelligent Recommendation Engine ---
    is_perfect = True
    recommendations = packages.annotate(rating=Avg('reviews__rating')).order_by('-is_featured', '-rating')

    # If no results for the FULL filter, try relaxing non-essential ones (Duration, Pace)
    if not recommendations.exists():
        is_perfect = False
        packages_f1 = TourPackage.objects.filter(is_active=True, destination__category__iexact=terrain)
        
        # Try keeping Budget or Comfort if possible
        f1_results = packages_f1.filter(Q(price_per_person__lt=20000) if budget == 'low' else Q())
        if f1_results.exists():
            recommendations = f1_results.annotate(rating=Avg('reviews__rating')).order_by('-is_featured', '-rating')
        else:
            recommendations = packages_f1.annotate(rating=Avg('reviews__rating')).order_by('-is_featured', '-rating')

    # If still no results (Landscape itself has no packages), show Featured ones
    if not recommendations.exists():
        is_perfect = False
        recommendations = TourPackage.objects.filter(is_active=True).annotate(rating=Avg('reviews__rating')).order_by('-is_featured', '-rating')

    recommendations = recommendations[:3]
    
    # --- Step 3: Global Suggestions (Diverse popular options) ---
    match_ids = [pkg.id for pkg in recommendations]
    suggestions_qs = TourPackage.objects.filter(is_active=True).exclude(id__in=match_ids).annotate(rating=Avg('reviews__rating')).order_by('-is_featured', '-rating')[:3]

    results = []
    for pkg in recommendations:
        results.append({
            "id": pkg.id,
            "title": pkg.title,
            "price": f"{int(pkg.discounted_price):,}",
            "image": pkg.main_image.url if pkg.main_image else "/static/img/placeholder.jpg",
            "url": pkg.get_absolute_url(),
            "duration": f"{pkg.duration_days} Days",
            "state": pkg.get_state_display()
        })

    suggestions = []
    for pkg in suggestions_qs:
        suggestions.append({
            "id": pkg.id,
            "title": pkg.title,
            "price": f"{int(pkg.discounted_price):,}",
            "image": pkg.main_image.url if pkg.main_image else "/static/img/placeholder.jpg",
            "url": pkg.get_absolute_url(),
            "duration": f"{pkg.duration_days} Days",
            "state": pkg.get_state_display()
        })

    return JsonResponse({
        "packages": results,
        "suggestions": suggestions,
        "is_perfect": is_perfect,
        "count": len(results)
    })


def quiz_page(request):
    """Renders the quiz interface."""
    return render(request, 'features/quiz.html')
