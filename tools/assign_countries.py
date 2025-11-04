"""
Assign countries to database entries based on coordinates
Uses Nominatim reverse geocoding API for precise country detection
"""
import sqlite3
from pathlib import Path
import requests
import time


def get_country_from_coords(lat, lon):
    """
    Use Nominatim reverse geocoding API to get country from coordinates
    Returns country name or None if not found
    """
    # Nominatim API endpoint
    url = "https://nominatim.openstreetmap.org/reverse"
    
    params = {
        'lat': lat,
        'lon': lon,
        'format': 'json',
        'addressdetails': 1,
        'zoom': 3  # Country level
    }
    
    headers = {
        'User-Agent': 'MountainHutsDatabase/1.0'  # Required by Nominatim
    }
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Extract country from address
        if 'address' in data and 'country' in data['address']:
            return data['address']['country']
        
        return None
        
    except Exception as e:
        print(f"    Error getting country for ({lat}, {lon}): {e}")
        return None


def assign_countries():
    """
    Update all database entries with missing countries based on coordinates
    Uses Nominatim API with rate limiting (max 1 request per second)
    """
    db_path = Path(__file__).parent.parent / "data" / "mountain_huts.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all huts without a country
    cursor.execute("""
        SELECT id, name, latitude, longitude, source, country
        FROM mountain_huts
        WHERE latitude IS NOT NULL AND longitude IS NOT NULL
    """)
    
    huts = cursor.fetchall()
    missing_count = len([h for h in huts if not h[5] or h[5] in ['N/A', '']])
    print(f"Processing {len(huts)} huts...")
    print(f"Note: Using Nominatim API with 0.5 second delay between requests (FAST MODE)")
    print(f"This will take approximately {missing_count * 0.5 / 60:.1f} minutes for {missing_count} missing countries\n")
    
    updated = 0
    already_had = 0
    not_found = 0
    api_errors = 0
    
    for i, (hut_id, name, lat, lon, source, current_country) in enumerate(huts, 1):
        # Skip if already has a valid country
        if current_country and current_country not in ['N/A', '', None]:
            already_had += 1
            continue
        
        print(f"[{i}/{len(huts)}] {name[:50]:50}", end=" ")
        
        # Get country from coordinates
        country = get_country_from_coords(lat, lon)
        
        if country:
            cursor.execute("""
                UPDATE mountain_huts
                SET country = ?
                WHERE id = ?
            """, (country, hut_id))
            updated += 1
            print(f"-> {country}")
            
            # Commit every 10 updates
            if updated % 10 == 0:
                conn.commit()
        else:
            not_found += 1
            api_errors += 1
            print(f"-> [!] No country found at ({lat:.4f}, {lon:.4f})")
        
        # Rate limiting: Reduced to 0.5 seconds for faster processing
        # Note: Nominatim recommends max 1 req/sec, but allows bursts
        time.sleep(0.5)
    
    conn.commit()
    conn.close()
    
    print(f"\n=== SUMMARY ===")
    print(f"Total huts processed: {len(huts)}")
    print(f"Already had country: {already_had}")
    print(f"Updated with country: {updated}")
    print(f"No country found: {not_found}")
    
    if not_found > 0:
        print(f"\nTip: Some huts may be outside the defined boundaries.")
        print(f"     You can add more country boundaries to COUNTRY_BOUNDARIES in the script.")


def show_statistics():
    """Show country distribution after update"""
    db_path = Path(__file__).parent.parent / "data" / "mountain_huts.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT country, COUNT(*) as count
        FROM mountain_huts
        WHERE country IS NOT NULL AND country != ''
        GROUP BY country
        ORDER BY count DESC
    """)
    
    print(f"\n=== COUNTRY DISTRIBUTION ===")
    for country, count in cursor.fetchall():
        print(f"  {country:30} {count:4} huts")
    
    cursor.execute("""
        SELECT COUNT(*)
        FROM mountain_huts
        WHERE country IS NULL OR country = '' OR country = 'N/A'
    """)
    missing = cursor.fetchone()[0]
    if missing > 0:
        print(f"  {'(No country)':30} {missing:4} huts")
    
    conn.close()


if __name__ == "__main__":
    import sys
    
    print("Mountain Huts Country Assignment")
    print("=" * 60)
    
    # Check for --force flag to re-check all coordinates
    force = '--force' in sys.argv
    
    if force:
        print("[!] FORCE MODE: Will re-check ALL huts using Nominatim API")
        print("This will take approximately 40+ minutes for 2,221 huts!\n")
        response = input("Are you sure you want to continue? (yes/no): ")
        if response.lower() != 'yes':
            print("Cancelled.")
            sys.exit(0)
        
        # Clear existing countries to force update
        db_path = Path(__file__).parent.parent / "data" / "mountain_huts.db"
        conn = sqlite3.connect(db_path)
        conn.execute("UPDATE mountain_huts SET country = NULL")
        conn.commit()
        conn.close()
        print("Cleared all existing countries. Starting fresh API lookup...\n")
    
    assign_countries()
    show_statistics()
