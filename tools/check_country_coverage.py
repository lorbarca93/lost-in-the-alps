"""Check country assignment coverage"""
import sqlite3
from pathlib import Path

db_path = Path(__file__).parent.parent / "data" / "mountain_huts.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Total huts
cursor.execute("SELECT COUNT(*) FROM mountain_huts")
total = cursor.fetchone()[0]

# Huts with country
cursor.execute("SELECT COUNT(*) FROM mountain_huts WHERE country IS NOT NULL AND country != ''")
with_country = cursor.fetchone()[0]

# Unique countries
cursor.execute("SELECT COUNT(DISTINCT country) FROM mountain_huts WHERE country IS NOT NULL AND country != ''")
unique_countries = cursor.fetchone()[0]

# Huts without country
without_country = total - with_country

print(f"Total huts: {total}")
print(f"Huts with country: {with_country} ({with_country/total*100:.1f}%)")
print(f"Huts without country: {without_country}")
print(f"Unique countries: {unique_countries}")

if without_country > 0:
    print("\nHuts without country assignment:")
    cursor.execute("""
        SELECT source, COUNT(*) as count
        FROM mountain_huts
        WHERE country IS NULL OR country = ''
        GROUP BY source
    """)
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]} huts")

conn.close()

