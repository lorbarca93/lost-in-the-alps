import sqlite3

conn = sqlite3.connect('data/mountain_huts.db')
cursor = conn.cursor()

# Check boudy.info coordinates
cursor.execute('SELECT name, latitude, longitude, source FROM mountain_huts WHERE source="boudy.info" LIMIT 10')
print("Sample boudy.info coordinates:")
print("-" * 80)
for row in cursor.fetchall():
    print(f"{row[0][:40]:40} | Lat: {row[1]:8.4f} | Lon: {row[2]:8.4f}")

print("\n" + "="*80)
print("Coordinate ranges for boudy.info:")
cursor.execute('SELECT MIN(latitude), MAX(latitude), MIN(longitude), MAX(longitude) FROM mountain_huts WHERE source="boudy.info"')
min_lat, max_lat, min_lon, max_lon = cursor.fetchone()
print(f"Latitude range:  {min_lat:.4f} to {max_lat:.4f}")
print(f"Longitude range: {min_lon:.4f} to {max_lon:.4f}")

print("\n" + "="*80)
print("Expected for Alps/Czech region:")
print("Latitude range:  43-51°N (Alps and Czech Republic)")
print("Longitude range: 5-20°E")

conn.close()
