import re

filepath = 'd:\\TourVista\\core\\management\\commands\\seed_data.py'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Remove the image_url keys from PLACES_DATA
content = re.sub(r',\s*"image_url":\s*"[^"]+"', '', content)

# Update handle method
handle_pattern = """            obj, created = Place.objects.get_or_create(
                name=pl['name'],
                defaults={
                    'specialty': pl['specialty'],
                    'emoji': pl.get('emoji', '📍'),
                    'image_url': pl.get('image_url', ''),
                }
            )
            if not created:
                obj.specialty = pl['specialty']
                obj.emoji = pl.get('emoji', '📍')
                obj.image_url = pl.get('image_url', '')
                obj.save()"""

handle_repl = """            obj, created = Place.objects.get_or_create(
                name=pl['name'],
                defaults={
                    'specialty': pl['specialty'],
                    'emoji': pl.get('emoji', '📍'),
                }
            )
            if not created:
                obj.specialty = pl['specialty']
                obj.emoji = pl.get('emoji', '📍')
                obj.save()"""

content = content.replace(handle_pattern, handle_repl)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print("Cleaned seed_data.py")
