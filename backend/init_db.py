import csv
import sqlite3
import json
import time
import os
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut

def init_db():
    conn = sqlite3.connect('startups.db')
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS startups (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        location TEXT,
        founders TEXT,
        website TEXT,
        article_url TEXT,
        lat REAL,
        lng REAL
    )
    ''')
    # Clear existing if any
    cursor.execute('DELETE FROM startups')
    conn.commit()
    return conn, cursor

def geocode_city(city_name, geolocator, cache):
    if not city_name or city_name.lower() in ('n/a', 'null', 'not specified in the article', 'not specified', 'italy'):
        # If it's just 'Italy' or null, we might not want to plot it, or plot it centrally
        # But 'Italy' is a country. Let's just return None for invalid ones
        if city_name.lower() == 'italy':
            return (41.8719, 12.5674) # Center of Italy roughly
        return None
        
    # Clean up the city name if it has comma (like 'Milan, Italy' -> 'Milan')
    clean_name = city_name.split(',')[0].strip()
    
    if clean_name in cache:
        return cache[clean_name]
        
    try:
        # To be safe and narrow it down, if it's an Italian city often, we might append Italy but we can't assume all are in Italy (e.g. London).
        location = geolocator.geocode(clean_name, timeout=10)
        # Be polite to Nominatim
        time.sleep(1.1)
        
        if location:
            cache[clean_name] = (location.latitude, location.longitude)
            print(f"Geocoded {clean_name} -> {location.latitude}, {location.longitude}")
            return (location.latitude, location.longitude)
        else:
            print(f"Could not geocode {clean_name}")
            cache[clean_name] = None
            return None
    except Exception as e:
        print(f"Error geocoding {clean_name}: {e}")
        time.sleep(2)
        return None

def main():
    conn, cursor = init_db()
    geolocator = Nominatim(user_agent="eu_startups_mapper_script")
    geo_cache = {}
    
    startups = []
    
    with open('italy_startups_llm.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            loc_str = row.get('Location', '')
            coords = geocode_city(loc_str, geolocator, geo_cache)
            
            lat, lng = coords if coords else (None, None)
            
            startup = {
                'name': row.get('Startup Name', 'N/A'),
                'location': loc_str,
                'founders': row.get('Founders', 'N/A'),
                'website': row.get('Website', 'N/A'),
                'article_url': row.get('Article URL', 'N/A'),
                'lat': lat,
                'lng': lng
            }
            startups.append(startup)
            
            cursor.execute('''
            INSERT INTO startups (name, location, founders, website, article_url, lat, lng)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (startup['name'], startup['location'], startup['founders'], startup['website'], startup['article_url'], startup['lat'], startup['lng']))
            
    conn.commit()
    print(f"Inserted {len(startups)} startups into database.")
    
    # Ensure frontend/public exists
    os.makedirs('../frontend/public', exist_ok=True)
    
    # Export to JSON for frontend
    # Filter out ones without coordinates for the map
    valid_startups = [s for s in startups if s['lat'] is not None and s['lng'] is not None]
    with open('../frontend/public/startups.json', 'w', encoding='utf-8') as f:
        json.dump(valid_startups, f, indent=2)
        
    print(f"Exported {len(valid_startups)} startups with valid coordinates to ../frontend/public/startups.json")
    conn.close()

if __name__ == "__main__":
    main()
