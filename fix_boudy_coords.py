"""
Fix swapped coordinates for boudy.info huts in the database
The scraper was incorrectly assigning lat/lon (they were swapped)
"""

import sqlite3

def fix_boudy_coordinates():
    conn = sqlite3.connect('data/mountain_huts.db')
    cursor = conn.cursor()
    
    # Get all boudy.info huts
    cursor.execute('''
        SELECT id, name, latitude, longitude 
        FROM mountain_huts 
        WHERE source = "boudy.info"
    ''')
    
    huts = cursor.fetchall()
    print(f"Found {len(huts)} huts from boudy.info")
    
    # Swap latitude and longitude for each hut
    fixed_count = 0
    for hut_id, name, old_lat, old_lon in huts:
        new_lat = old_lon  # Old longitude becomes new latitude
        new_lon = old_lat  # Old latitude becomes new longitude
        
        cursor.execute('''
            UPDATE mountain_huts 
            SET latitude = ?, longitude = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (new_lat, new_lon, hut_id))
        
        fixed_count += 1
        if fixed_count <= 5:  # Show first 5 as examples
            print(f"  Fixed '{name}': ({old_lat:.4f}, {old_lon:.4f}) -> ({new_lat:.4f}, {new_lon:.4f})")
    
    conn.commit()
    
    # Verify the fix
    print("\nVerifying fix...")
    cursor.execute('''
        SELECT 
            COUNT(*) as total,
            MIN(latitude) as min_lat,
            MAX(latitude) as max_lat,
            MIN(longitude) as min_lon,
            MAX(longitude) as max_lon
        FROM mountain_huts 
        WHERE source = "boudy.info"
    ''')
    
    row = cursor.fetchone()
    print(f"\nAfter fix:")
    print(f"  Total huts: {row[0]}")
    print(f"  Latitude range:  {row[1]:.4f} to {row[2]:.4f} (should be ~43-52)")
    print(f"  Longitude range: {row[3]:.4f} to {row[4]:.4f} (should be ~5-20)")
    
    # Check if ranges look correct now
    if 43 <= row[1] <= 52 and 43 <= row[2] <= 52 and 5 <= row[3] <= 20 and 5 <= row[4] <= 20:
        print("\n✅ Coordinates look correct!")
    else:
        print("\n⚠️ Coordinates might still have issues")
    
    conn.close()
    print(f"\n✅ Fixed {fixed_count} huts from boudy.info")

if __name__ == "__main__":
    fix_boudy_coordinates()
