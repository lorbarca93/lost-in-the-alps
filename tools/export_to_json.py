"""
Export database to JSON for map visualization
"""
import sys
from pathlib import Path
import json

# Add src directory to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / 'src'))

from database import MountainHutsDatabase

def export_to_json(output_file: str = 'web/data/huts.json'):
    """Export all huts to JSON file"""
    import sqlite3
    db = MountainHutsDatabase()
    conn = sqlite3.connect(db.db_path)
    cursor = conn.cursor()
    
    # Get all huts with coordinates
    cursor.execute("""
        SELECT 
            name, latitude, longitude, altitude, hut_type, country, 
            website, url, description, source
        FROM mountain_huts
        WHERE latitude IS NOT NULL AND longitude IS NOT NULL
    """)
    
    huts = []
    for row in cursor.fetchall():
        huts.append({
            'name': row[0],
            'lat': row[1],
            'lon': row[2],
            'altitude': row[3],
            'type': row[4],
            'country': row[5],
            'website': row[6],
            'url': row[7],
            'description': row[8],
            'source': row[9]
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
