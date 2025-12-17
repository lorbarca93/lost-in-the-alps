import sqlite3

conn = sqlite3.connect('data/mountain_huts.db')
cursor = conn.cursor()

# Get sample huts from boudy.info
cursor.execute('''
    SELECT name, latitude, longitude, source 
    FROM mountain_huts 
    WHERE source = "boudy.info" 
    LIMIT 20
''')

print("Sample huts from boudy.info:")
print("-" * 80)
for row in cursor.fetchall():
    name, lat, lon, source = row
    print(f"{name:40s} | lat={lat:8.4f}, lon={lon:8.4f}")

# Check if coordinates look swapped (lat/lon reversed)
print("\n" + "=" * 80)
print("Checking coordinate ranges:")
print("=" * 80)

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
print(f"Total huts: {row[0]}")
print(f"Latitude range:  {row[1]:.4f} to {row[2]:.4f}")
print(f"Longitude range: {row[3]:.4f} to {row[4]:.4f}")

# Alps region should be roughly:
# Latitude: 43°N to 48°N (43.0 to 48.0)
# Longitude: 5°E to 17°E (5.0 to 17.0)

print("\nExpected ranges for Alps:")
print("Latitude:  43.0 to 48.0")
print("Longitude: 5.0 to 17.0")

# Check for swapped coordinates
cursor.execute('''
    SELECT COUNT(*) 
    FROM mountain_huts 
    WHERE source = "boudy.info" 
    AND (latitude < 5.0 OR latitude > 25.0 OR longitude < 43.0 OR longitude > 52.0)
''')

suspicious = cursor.fetchone()[0]
print(f"\nSuspicious coordinates (possibly swapped): {suspicious}")

conn.close()
