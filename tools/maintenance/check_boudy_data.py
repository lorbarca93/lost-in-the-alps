import sqlite3

conn = sqlite3.connect('data/mountain_huts.db')
cursor = conn.cursor()

# Check if boudy.info huts have the detailed information
cursor.execute('''
    SELECT name, altitude, capacity, capacity_max, comments, water_source, posted_by, posted_date
    FROM mountain_huts 
    WHERE source="boudy.info" AND altitude IS NOT NULL 
    LIMIT 5
''')

print("Sample boudy.info huts with altitude data:")
print("=" * 80)
for row in cursor.fetchall():
    print(f"\nName: {row[0]}")
    print(f"Altitude: {row[1]}")
    print(f"Capacity: {row[2]}")
    print(f"Capacity Max: {row[3]}")
    print(f"Comments: {row[4][:100] if row[4] else 'None'}...")
    print(f"Water Source: {row[5]}")
    print(f"Posted By: {row[6]}")
    print(f"Posted Date: {row[7]}")

# Check how many have this data
cursor.execute('SELECT COUNT(*) FROM mountain_huts WHERE source="boudy.info" AND altitude IS NOT NULL')
with_altitude = cursor.fetchone()[0]

cursor.execute('SELECT COUNT(*) FROM mountain_huts WHERE source="boudy.info" AND capacity IS NOT NULL')
with_capacity = cursor.fetchone()[0]

cursor.execute('SELECT COUNT(*) FROM mountain_huts WHERE source="boudy.info"')
total = cursor.fetchone()[0]

print("\n" + "=" * 80)
print("Statistics:")
print(f"Total boudy.info huts: {total}")
print(f"With altitude: {with_altitude}")
print(f"With capacity: {with_capacity}")

conn.close()
