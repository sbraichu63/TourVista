import os
import django
import sys
from django.utils.text import slugify

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tourvista.settings')
django.setup()

from core.models import TourPackage, Destination

def list_packages():
    """Lists all current tour packages in the database."""
    print("\n--- Current Tour Packages ---")
    pkgs = TourPackage.objects.all().order_by('best_season')
    print(f"Total Count: {pkgs.count()}")
    for p in pkgs:
        print(f"[{p.best_season.upper():<8}] {p.title} ({p.get_state_display()})")
    print("----------------------------\n")

def cleanup_duplicates():
    """Removes specific duplicate or redundant packages based on their slugs."""
    slugs_to_remove = [
        'roopkund-trek-the-mystery-lake',
        'munnar-tea-garden-retreat',
        'spiti-valley-high-altitude-safari',
        'malshej-ghat-waterfall-trail',
        'valley-of-flowers-monsoon-special',
        'coorg-coffee-estate-monsoon-stay',
        'varanasi-dev-deepavali-experience',
        'mysore-dasara-heritage-tour',
        'darjeeling-autumn-charm',
        'hampi-ruins-exploration',
        'auli-skiing-adventure',
        'rann-of-kutch-desert-festival',
        'rajasthan-royal-forts-circuit',
        'goa-winter-sun-beaches',
        'kaziranga-wildlife-safari'
    ]
    deleted, _ = TourPackage.objects.filter(slug__in=slugs_to_remove).delete()
    print(f"\nCleanup: Removed {deleted} redundant packages.")

def seed_unique_packages():
    """Seeds the 15+ unique tour packages across all seasons."""
    def get_dest(name, state):
        dest, _ = Destination.objects.get_or_create(name=name, defaults={'state': state, 'is_featured': True})
        return dest

    packages = [
        # SUMMER
        {
            'title': 'Tirthan Valley & Great Himalayan National Park',
            'destination': get_dest('Tirthan Valley', 'himachal_pradesh'),
            'state': 'himachal_pradesh',
            'city_name': 'Gushaini',
            'duration_days': 5,
            'price_per_person': 14500,
            'best_season': 'summer',
            'difficulty': 'moderate',
            'description': 'Discover the hidden gem of Himachal. Trout fishing, riverside camping, and trekking through the UNESCO World Heritage GHNP.',
        },
        {
            'title': 'Tawang Monastery & Sela Pass Adventure',
            'destination': get_dest('Tawang', 'northeast'),
            'state': 'northeast',
            'city_name': 'Tawang',
            'duration_days': 7,
            'price_per_person': 22500,
            'best_season': 'summer',
            'difficulty': 'moderate',
            'description': 'Journey to the land of the Monpas. Visit the largest monastery in India and cross the high-altitude Sela Pass.',
        },
        {
            'title': 'Dharamshala & Mcleodganj Yoga Retreat',
            'destination': get_dest('Mcleodganj', 'himachal_pradesh'),
            'state': 'himachal_pradesh',
            'city_name': 'Dharamshala',
            'duration_days': 4,
            'price_per_person': 12500,
            'best_season': 'summer',
            'difficulty': 'easy',
            'description': 'Find inner peace in the home of the Dalai Lama. Yoga sessions with Himalayan views and monastery tours.',
        },
        # MONSOON
        {
            'title': 'Amboli Ghat Mist & Waterfalls Trek',
            'destination': get_dest('Amboli', 'maharashtra'),
            'state': 'maharashtra',
            'city_name': 'Sawantwadi',
            'duration_days': 2,
            'price_per_person': 5500,
            'best_season': 'monsoon',
            'difficulty': 'easy',
            'description': 'Visit the "Cherrapunji of Maharashtra". Experience incredible biodiversity and dozens of active waterfalls.',
        },
        {
            'title': 'Mandu — The Monsoon Romance Heritage',
            'destination': get_dest('Mandu', 'madhya_pradesh'),
            'state': 'madhya_pradesh',
            'city_name': 'Dhar',
            'duration_days': 3,
            'price_per_person': 8500,
            'best_season': 'monsoon',
            'difficulty': 'easy',
            'description': 'Explore the ancient "City of Joy" which comes alive during the rains. Afghan architecture and legendary love stories.',
        },
        {
            'title': 'Dudhsagar Falls & Jungle Safari',
            'destination': get_dest('Dudhsagar', 'goa'),
            'state': 'goa',
            'city_name': 'Mollem',
            'duration_days': 2,
            'price_per_person': 6500,
            'best_season': 'monsoon',
            'difficulty': 'moderate',
            'description': 'Trek to the "Sea of Milk" — one of India\'s tallest waterfalls through a wildlife sanctuary.',
        },
        # AUTUMN
        {
            'title': 'Ajanta & Ellora Caves Exploration',
            'destination': get_dest('Aurangabad', 'maharashtra'),
            'state': 'maharashtra',
            'city_name': 'Aurangabad',
            'duration_days': 4,
            'price_per_person': 15000,
            'best_season': 'autumn',
            'difficulty': 'moderate',
            'description': 'Marvel at the UNESCO World Heritage rock-cut temples. Post-monsoon greenery adds magic to these ancient monuments.',
        },
        {
            'title': 'Nagaland Hornbill Festival Experience',
            'destination': get_dest('Kohima', 'northeast'),
            'state': 'northeast',
            'city_name': 'Kisama',
            'duration_days': 6,
            'price_per_person': 28500,
            'best_season': 'autumn',
            'difficulty': 'moderate',
            'description': 'Witness the "Festival of Festivals". Experience rich tribal heritage, traditional dances, and Naga cuisine.',
        },
        {
            'title': 'Mahabalipuram & Tanjore Temple Trail',
            'destination': get_dest('Mahabalipuram', 'tamil_nadu'),
            'state': 'tamil_nadu',
            'city_name': 'Tanjore',
            'duration_days': 5,
            'price_per_person': 17500,
            'best_season': 'autumn',
            'difficulty': 'easy',
            'description': 'A journey through architectural wonders of the Pallavas and Cholas. Shore temples and massive monolithic sculptures.',
        },
        {
            'title': 'Bikaner & Mandawa Haveli Heritage',
            'destination': get_dest('Bikaner', 'rajasthan'),
            'state': 'rajasthan',
            'city_name': 'Shekhawati',
            'duration_days': 4,
            'price_per_person': 14000,
            'best_season': 'autumn',
            'difficulty': 'easy',
            'description': 'Explore the "Open Air Art Gallery" of India. Painted havelis and historic Rajasthan forts.',
        },
        # WINTER
        {
            'title': 'Pahalgam & Sonmarg Snow Valley Safari',
            'destination': get_dest('Pahalgam', 'kashmir'),
            'state': 'kashmir',
            'city_name': 'Anantnag',
            'duration_days': 5,
            'price_per_person': 21000,
            'best_season': 'winter',
            'difficulty': 'easy',
            'description': 'Experience the "Switzerland of the East" covered in a blanket of white. Sledge rides and snow fights.',
        },
        {
            'title': 'Varkala & Alleppey Backwater Escape',
            'destination': get_dest('Varkala', 'kerala'),
            'state': 'kerala',
            'city_name': 'Alleppey',
            'duration_days': 6,
            'price_per_person': 19500,
            'best_season': 'winter',
            'difficulty': 'easy',
            'description': 'Combine dramatic red cliffs with a luxury houseboat cruise through serene backwaters.',
        },
        {
            'title': 'Dhanushkodi & Rameshwaram Island Tour',
            'destination': get_dest('Rameshwaram', 'tamil_nadu'),
            'state': 'tamil_nadu',
            'city_name': 'Dhanushkodi',
            'duration_days': 3,
            'price_per_person': 9500,
            'best_season': 'winter',
            'difficulty': 'easy',
            'description': 'Visit the ghost town of Dhanushkodi where the Bay of Bengal meets the Indian Ocean.',
        },
        {
            'title': 'Kanha National Park Wildlife Safari',
            'destination': get_dest('Kanha', 'madhya_pradesh'),
            'state': 'madhya_pradesh',
            'city_name': 'Mandla',
            'duration_days': 4,
            'price_per_person': 24000,
            'best_season': 'winter',
            'difficulty': 'easy',
            'description': 'The inspiration for Kipling\'s "The Jungle Book". Track tigers and rare deer in their natural habitat.',
        },
        {
            'title': 'Aurangabad & Daulatabad Fort History',
            'destination': get_dest('Daulatabad', 'maharashtra'),
            'state': 'maharashtra',
            'city_name': 'Aurangabad',
            'duration_days': 3,
            'price_per_person': 11500,
            'best_season': 'winter',
            'difficulty': 'moderate',
            'description': 'Climb the invincible Daulatabad Fort and visit the Bibi Ka Maqbara.',
        },
        # MAHARASHTRA SPECIALS
        {
            'title': 'Lonavala & Khandala Monsoon Escape',
            'destination': get_dest('Lonavala', 'maharashtra'),
            'state': 'maharashtra',
            'city_name': 'Lonavala',
            'duration_days': 3,
            'price_per_person': 8500,
            'best_season': 'monsoon',
            'difficulty': 'easy',
            'description': 'Experience the mist-covered peaks, lush green valleys, and cascading waterfalls of the Western Ghats.',
        },
        {
            'title': 'Mahabaleshwar & Panchgani Hill Retreat',
            'destination': get_dest('Mahabaleshwar', 'maharashtra'),
            'state': 'maharashtra',
            'city_name': 'Mahabaleshwar',
            'duration_days': 4,
            'price_per_person': 12500,
            'best_season': 'winter',
            'difficulty': 'easy',
            'description': 'Enjoy the cool mountain air, strawberry farms, and breathtaking sunrise points.',
        },
        {
            'title': 'Tarkarli Scuba & Konkan Beach Tour',
            'destination': get_dest('Tarkarli', 'maharashtra'),
            'state': 'maharashtra',
            'city_name': 'Malvan',
            'duration_days': 4,
            'price_per_person': 14500,
            'best_season': 'winter',
            'difficulty': 'moderate',
            'description': 'Dive into the crystal clear waters of the Arabian Sea. Experience scuba diving and Sindhudurg Fort.',
        }
    ]

    added = 0
    for p_data in packages:
        p_data['slug'] = slugify(p_data['title'])
        if not TourPackage.objects.filter(slug=p_data['slug']).exists():
            TourPackage.objects.create(**p_data, is_active=True)
            added += 1
    print(f"\nSeed: Added {added} unique packages successfully.")

def main():
    print("TourVista Database Manager")
    print("1. List All Packages")
    print("2. Cleanup Duplicates/Redundant")
    print("3. Seed Unique Packages")
    print("4. Run All (Cleanup + Seed + List)")
    print("5. Exit")
    
    choice = input("\nEnter your choice (1-5): ")
    
    if choice == '1':
        list_packages()
    elif choice == '2':
        cleanup_duplicates()
    elif choice == '3':
        seed_unique_packages()
    elif choice == '4':
        cleanup_duplicates()
        seed_unique_packages()
        list_packages()
    elif choice == '5':
        sys.exit()
    else:
        print("Invalid choice.")

if __name__ == "__main__":
    main()
