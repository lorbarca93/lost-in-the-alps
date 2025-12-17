#!/usr/bin/env python3
import sqlite3
import sys
from pathlib import Path

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

db_path = Path(__file__).parent.parent / "data" / "mountain_huts.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check for fake boudy.info URLs
cursor.execute("""
    SELECT COUNT(*) FROM mountain_huts 
    WHERE source = 'boudy.info' 
    AND (website LIKE '%qefzsx%' OR website LIKE '%hxwbgj%' OR website LIKE '%fhytem%' OR website LIKE '%gkialb%')
""")
fake_count = cursor.fetchone()[0]

# Check for missing protocols
cursor.execute("""
    SELECT COUNT(*) FROM mountain_huts 
    WHERE website LIKE 'www.%' AND website NOT LIKE 'http%'
""")
missing_protocol = cursor.fetchone()[0]

# Sample of each
print(f"FAKE BOUDY.INFO URLs: {fake_count}")
cursor.execute("""
    SELECT name, website FROM mountain_huts 
    WHERE source = 'boudy.info' AND website LIKE '%qefzsx%'
    LIMIT 5
""")
for row in cursor.fetchall():
    print(f"  - {row[0]}: {row[1]}")

print(f"\nMISSING PROTOCOL: {missing_protocol}")
cursor.execute("""
    SELECT name, website FROM mountain_huts 
    WHERE website LIKE 'www.%' AND website NOT LIKE 'http%'
    LIMIT 5
""")
for row in cursor.fetchall():
    print(f"  - {row[0]}: {row[1]}")

conn.close()

