"""
Check mountainhuts.info statistics in database
"""

import sqlite3

conn = sqlite3.connect('data/mountain_huts.db')
cursor = conn.cursor()

# Get overall statistics
cursor.execute("""
    SELECT 
        COUNT(*) as total,
        COUNT(DISTINCT source_id) as unique_ids,
        COUNT(CASE WHEN owner IS NOT NULL AND owner != '' THEN 1 END) as with_owner,
        COUNT(CASE WHEN manager IS NOT NULL AND manager != '' THEN 1 END) as with_manager,
        COUNT(CASE WHEN phone IS NOT NULL AND phone != '' THEN 1 END) as with_phone,
        COUNT(CASE WHEN email IS NOT NULL AND email != '' THEN 1 END) as with_email,
        COUNT(CASE WHEN website IS NOT NULL AND website != '' THEN 1 END) as with_website,
        COUNT(CASE WHEN opening_hours IS NOT NULL AND opening_hours != '' THEN 1 END) as with_opening
    FROM mountain_huts 
    WHERE source='mountainhuts.info'
""")

row = cursor.fetchone()
print("mountainhuts.info statistics:")
print(f"  Total records: {row[0]}")
print(f"  Unique source_ids: {row[1]}")
print(f"  With owner: {row[2]}")
print(f"  With manager: {row[3]}")
print(f"  With phone: {row[4]}")
print(f"  With email: {row[5]}")
print(f"  With website: {row[6]}")
print(f"  With opening hours: {row[7]}")

# Check if there are duplicates
if row[0] != row[1]:
    print(f"\nWARNING: Found duplicates! ({row[0]} records, {row[1]} unique)")
    cursor.execute("""
        SELECT source_id, COUNT(*) as count 
        FROM mountain_huts 
        WHERE source='mountainhuts.info'
        GROUP BY source_id 
        HAVING count > 1
        LIMIT 5
    """)
    print("\nSample duplicates:")
    for dup in cursor.fetchall():
        print(f"  {dup[0]}: {dup[1]} records")

# Sample records with rich data
print("\nSample huts with complete data:")
cursor.execute("""
    SELECT name, country, altitude, owner, manager, phone, email, website, opening_hours
    FROM mountain_huts
    WHERE source='mountainhuts.info' 
      AND owner IS NOT NULL AND owner != ''
      AND manager IS NOT NULL AND manager != ''
    LIMIT 3
""")

for hut in cursor.fetchall():
    print(f"\n  {hut[0]} ({hut[1]}, {hut[2]}m)")
    print(f"    Owner: {hut[3]}")
    print(f"    Manager: {hut[4]}")
    print(f"    Phone: {hut[5]}")
    print(f"    Email: {hut[6]}")
    print(f"    Website: {hut[7]}")
    print(f"    Opening: {hut[8]}")

conn.close()
