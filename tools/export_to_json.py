"""
Export database to JSON for map visualization
"""
import sys
from pathlib import Path
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database import MountainHutsDatabase

def export_to_json(output_file: str = 'huts_data.json'):
    """Export all huts to JSON file"""
    import sqlite3
    db = MountainHutsDatabase()
    conn = sqlite3.connect(db.db_path)
    cursor = conn.cursor()
    
    # Get all huts with coordinates
    cursor.execute("""
        SELECT 
            name, latitude, longitude, altitude, type, country, 
            website, description, source
        FROM mountain_huts
        WHERE latitude IS NOT NULL AND longitude IS NOT NULL
    """)
    
    huts = []
    for row in cursor.fetchall():
        huts.append({
            'name': row[0],
            'latitude': row[1],
            'longitude': row[2],
            'altitude': row[3],
            'type': row[4],
            'country': row[5],
            'website': row[6],
            'description': row[7],
            'source': row[8]
        })
    
    conn.close()
    
    # Write to JSON file
    output_path = Path(__file__).parent.parent / output_file
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(huts, f, ensure_ascii=False, indent=2)
    
    print(f"Exported {len(huts)} huts to {output_path}")
    return len(huts)

if __name__ == '__main__':
    export_to_json()
