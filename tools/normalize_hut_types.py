"""Normalize hut_type values to fix inconsistencies"""
import sqlite3
from pathlib import Path

db_path = Path(__file__).parent.parent / "data" / "mountain_huts.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("Normalizing hut_type values...")

# Fix "Mountain Hut" -> "Mountain hut"
cursor.execute("UPDATE mountain_huts SET hut_type = 'Mountain hut' WHERE hut_type = 'Mountain Hut'")
print(f"[OK] Fixed {cursor.rowcount} 'Mountain Hut' -> 'Mountain hut'")

# Consolidate Unknown values
cursor.execute("""
    UPDATE mountain_huts 
    SET hut_type = 'Unknown' 
    WHERE hut_type IS NULL OR hut_type = '' OR hut_type = 'Unknown'
""")
print(f"[OK] Cleaned up Unknown values")

conn.commit()

# Show results
cursor.execute("""
    SELECT hut_type, COUNT(*) as count
    FROM mountain_huts
    GROUP BY hut_type
    ORDER BY count DESC
""")

print("\nCurrent hut_type distribution:")
for row in cursor.fetchall():
    print(f"  {row[0] or 'NULL'}: {row[1]} huts")

conn.close()
print("\n[OK] Normalization complete!")

