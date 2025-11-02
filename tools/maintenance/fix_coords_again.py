"""
Legacy emergency script that swapped boudy.info coordinates in-place.
Retained for historical tracing only.
"""

import sqlite3

conn = sqlite3.connect('data/mountain_huts.db')
cursor = conn.cursor()

# Count affected huts
cursor.execute('SELECT COUNT(*) FROM mountain_huts WHERE source="boudy.info" AND (latitude < 20 OR longitude > 40)')
count = cursor.fetchone()[0]
print(f"Found {count} boudy.info huts with swapped coordinates")

# Swap latitude and longitude for boudy.info huts
cursor.execute('''
    UPDATE mountain_huts 
    SET latitude = longitude,
        longitude = latitude
    WHERE source = "boudy.info"
''')

conn.commit()

# Verify the fix
cursor.execute('SELECT MIN(latitude), MAX(latitude), MIN(longitude), MAX(longitude) FROM mountain_huts WHERE source="boudy.info"')
min_lat, max_lat, min_lon, max_lon = cursor.fetchone()
print(f"\nAfter fix:")
print(f"Latitude range:  {min_lat:.4f} to {max_lat:.4f}")
print(f"Longitude range: {min_lon:.4f} to {max_lon:.4f}")
print(f"\nFixed {cursor.rowcount} records")

conn.close()
