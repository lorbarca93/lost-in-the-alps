"""
Fast Country Assignment Using Offline Data
Uses reverse_geocoder library for instant lookups (no API calls!)
Can process 8,000+ coordinates in seconds instead of hours
"""
import sqlite3
from pathlib import Path
import sys
import io

# Set UTF-8 encoding for console output on Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Check if reverse_geocoder is installed
try:
    import reverse_geocoder as rg
    RG_AVAILABLE = True
except ImportError:
    RG_AVAILABLE = False
    print("[!] reverse_geocoder not installed!")
    print("\nTo install:")
    print("  pip install reverse_geocoder")
    print("\nThis library provides OFFLINE reverse geocoding - much faster than API calls!")
    print("It can process 8,000+ coordinates in seconds instead of 40+ minutes.\n")
    sys.exit(1)


def get_country_from_coords_fast(lat, lon):
    """
    Use offline reverse geocoding to get country instantly
    Returns country name or None if not found
    """
    try:
        # reverse_geocoder returns a list, we take the first result
        result = rg.search((lat, lon), mode=1)[0]  # mode=1 for single result
        
        # Get country code and convert to full name
        country_code = result.get('cc', '')  # ISO 3166-1 alpha-2 code
        country_name = result.get('name', '')  # Admin1 name
        
        # Map country codes to full names (comprehensive)
        country_map = {
            'AT': 'Austria',
            'IT': 'Italy', 
            'SI': 'Slovenia',
            'HR': 'Croatia',
            'BG': 'Bulgaria',
            'PL': 'Poland',
            'RO': 'Romania',
            'SK': 'Slovakia',
            'GR': 'Greece',
            'BA': 'Bosnia and Herzegovina',
            'RS': 'Serbia',
            'CZ': 'Czech Republic',
            'HU': 'Hungary',
            'FR': 'France',
            'ME': 'Montenegro',
            'DE': 'Germany',
            'CH': 'Switzerland',
            'LI': 'Liechtenstein',
            'MK': 'North Macedonia',
            'AL': 'Albania',
            'XK': 'Kosovo',
            'ES': 'Spain',
            'AD': 'Andorra',
            'SM': 'San Marino',
            'VA': 'Vatican City',
            'MC': 'Monaco',
            'BE': 'Belgium',
            'RE': 'Réunion',
            'IS': 'Iceland',
            'NC': 'New Caledonia',
            'TF': 'French Southern Territories',
            'MA': 'Morocco',
            'NO': 'Norway',
            'GP': 'Guadeloupe',
            'MQ': 'Martinique',
            'AR': 'Argentina',
            'CO': 'Colombia',
            'JP': 'Japan',
            'CR': 'Costa Rica',
            'EE': 'Estonia',
            'GB': 'United Kingdom',
            'GE': 'Georgia',
            'LV': 'Latvia',
            'US': 'United States',
            'UA': 'Ukraine',
            'TR': 'Turkey'
        }
        
        return country_map.get(country_code, country_code)
        
    except Exception as e:
        print(f"    Error: {e}")
        return None


def assign_countries_fast(force=False, fix_incorrect=True):
    """
    Fast country assignment using offline data
    
    Args:
        force: If True, re-check all huts
        fix_incorrect: If True, also fix huts with potentially incorrect countries
    """
    db_path = Path(__file__).parent.parent / "data" / "mountain_huts.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get huts that need country assignment
    if force:
        # Re-check everything
        print("[*] FORCE MODE: Re-checking all huts\n")
        cursor.execute("""
            SELECT id, name, latitude, longitude, source, country
            FROM mountain_huts
            WHERE latitude IS NOT NULL AND longitude IS NOT NULL
        """)
    elif fix_incorrect:
        # Check huts with no country OR suspicious countries
        # (Huts in France should not show as "N/A" given refuges.info coverage)
        print("[*] Checking huts with missing or potentially incorrect countries\n")
        cursor.execute("""
            SELECT id, name, latitude, longitude, source, country
            FROM mountain_huts
            WHERE latitude IS NOT NULL AND longitude IS NOT NULL
            AND (country IS NULL OR country = '' OR country = 'N/A')
        """)
    else:
        # Only missing countries
        print("[*] Checking huts with missing countries only\n")
        cursor.execute("""
            SELECT id, name, latitude, longitude, source, country
            FROM mountain_huts
            WHERE latitude IS NOT NULL AND longitude IS NOT NULL
            AND (country IS NULL OR country = '')
        """)
    
    huts = cursor.fetchall()
    
    if not huts:
        print("[OK] All huts already have countries assigned!")
        conn.close()
        return
    
    print(f"[*] Processing {len(huts)} huts...")
    print(f"[*] Using OFFLINE reverse geocoding (very fast!)\n")
    
    # Batch process coordinates for maximum speed
    coords = [(h[2], h[3]) for h in huts]  # (lat, lon) tuples
    
    print("[*] Looking up countries (this will be fast)...")
    
    # Single batch call - much faster than individual lookups!
    results = rg.search(coords)
    
    print("[OK] Lookups complete! Updating database...\n")
    
    updated = 0
    already_had = 0
    not_found = 0
    
    # Map country codes
    country_map = {
        'AT': 'Austria',
        'IT': 'Italy',
        'SI': 'Slovenia',
        'HR': 'Croatia',
        'BG': 'Bulgaria',
        'PL': 'Poland',
        'RO': 'Romania',
        'SK': 'Slovakia',
        'GR': 'Greece',
        'BA': 'Bosnia and Herzegovina',
        'RS': 'Serbia',
        'CZ': 'Czech Republic',
        'HU': 'Hungary',
        'FR': 'France',
        'ME': 'Montenegro',
        'DE': 'Germany',
        'CH': 'Switzerland',
        'LI': 'Liechtenstein',
        'MK': 'North Macedonia',
        'AL': 'Albania',
        'XK': 'Kosovo',
        'ES': 'Spain',
        'AD': 'Andorra',
        'SM': 'San Marino',
        'VA': 'Vatican City',
        'MC': 'Monaco'
    }
    
    for i, (hut_data, result) in enumerate(zip(huts, results), 1):
        hut_id, name, lat, lon, source, current_country = hut_data
        
        # Get country from result
        country_code = result.get('cc', '')
        country = country_map.get(country_code, country_code)
        
        if country and country != current_country:
            cursor.execute("""
                UPDATE mountain_huts
                SET country = ?
                WHERE id = ?
            """, (country, hut_id))
            updated += 1
            
            if i % 100 == 0 or i <= 10:
                old = current_country or "(none)"
                print(f"  [{i:4}/{len(huts)}] {name[:40]:40} {old:20} -> {country}")
        elif current_country and current_country not in ['N/A', '', None]:
            already_had += 1
        else:
            not_found += 1
        
        # Commit every 100 updates
        if i % 100 == 0:
            conn.commit()
    
    conn.commit()
    conn.close()
    
    print(f"\n{'='*60}")
    print(f"SUMMARY")
    print(f"{'='*60}")
    print(f"Total huts processed: {len(huts)}")
    print(f"Updated with country: {updated}")
    print(f"Already had country: {already_had}")
    print(f"No country found: {not_found}")
    print(f"{'='*60}\n")


def show_statistics():
    """Show country distribution after update"""
    db_path = Path(__file__).parent.parent / "data" / "mountain_huts.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT country, COUNT(*) as count
        FROM mountain_huts
        WHERE country IS NOT NULL AND country != '' AND country != 'N/A'
        GROUP BY country
        ORDER BY count DESC
    """)
    
    print(f"{'='*60}")
    print(f"COUNTRY DISTRIBUTION")
    print(f"{'='*60}")
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
    
    total = cursor.execute("SELECT COUNT(*) FROM mountain_huts").fetchone()[0]
    assigned = total - missing
    percentage = (assigned / total * 100) if total > 0 else 0
    
    print(f"\n[OK] Country coverage: {assigned}/{total} ({percentage:.1f}%)")
    
    conn.close()


if __name__ == "__main__":
    print("=" * 60)
    print("FAST COUNTRY ASSIGNMENT - OFFLINE REVERSE GEOCODING")
    print("=" * 60)
    print()
    
    # Check for flags
    force = '--force' in sys.argv
    
    if force:
        print("[!] FORCE MODE: Will re-assign countries for ALL huts")
        response = input("\nAre you sure? (yes/no): ")
        if response.lower() != 'yes':
            print("Cancelled.")
            sys.exit(0)
    
    assign_countries_fast(force=force, fix_incorrect=True)
    show_statistics()
    
    print("\n[OK] Country assignment complete!")
    print("\n[TIP] Regenerate the map to see updated countries:")
    print("   python tools/create_ultra_simple_map.py")
    print("   Copy-Item mountain_huts_map.html website/ -Force")

