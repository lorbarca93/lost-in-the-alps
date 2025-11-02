"""Check sample records"""
import sqlite3
from pathlib import Path

# Connect to database in data folder
db_path = Path(__file__).parent.parent / 'data' / 'mountain_huts.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=== mountain-huts.net samples ===")
cursor.execute('SELECT name, country, altitude, description FROM mountain_huts WHERE source="mountain-huts.net" LIMIT 5')
for row in cursor.fetchall():
    print(f"  {row[0][:50]:50} | {row[1] or '(no country)':20} | {row[2] or 0}m")

print("\n=== boudy.info samples ===")
cursor.execute('SELECT name, country, altitude, description FROM mountain_huts WHERE source="boudy.info" LIMIT 5')
for row in cursor.fetchall():
    print(f"  {row[0][:50]:50} | {row[1] or '(no country)':20} | {row[2] or 0}m")

print("\n=== Country distribution for mountain-huts.net ===")
cursor.execute('SELECT country, COUNT(*) as count FROM mountain_huts WHERE source="mountain-huts.net" GROUP BY country ORDER BY count DESC')
for row in cursor.fetchall():
    print(f"  {row[0] or '(none)':25}: {row[1]} huts")

conn.close()
