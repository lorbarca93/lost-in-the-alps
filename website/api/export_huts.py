"""
Export all huts to a JSON file for the search interface
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

import sqlite3
import json
from pathlib import Path

def export_huts_json():
    """Export all huts to JSON"""
    db_path = Path(__file__).parent.parent.parent / "data" / "mountain_huts.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all huts with essential fields
    cursor.execute("""
        SELECT 
            id, name, hut_type, country, region, 
            latitude, longitude, altitude,
            phone, email, website, source,
            capacity, opening_hours, description
        FROM mountain_huts
        ORDER BY name
    """)
    
    huts = []
    for row in cursor.fetchall():
        hut = {
            'id': row[0],
            'name': row[1],
            'hut_type': row[2],
            'country': row[3],
            'region': row[4],
            'latitude': row[5],
            'longitude': row[6],
            'altitude': row[7],
            'phone': row[8],
            'email': row[9],
            'website': row[10],
            'source': row[11],
            'capacity': row[12],
            'opening_hours': row[13],
            'description': row[14]
        }
        huts.append(hut)
    
    conn.close()
    
    # Create api directory if it doesn't exist
    api_dir = Path(__file__).parent
    api_dir.mkdir(exist_ok=True)
    
    # Write to JSON file
    output_path = api_dir / "huts.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(huts, f, indent=2, ensure_ascii=False)
    
    print(f"Exported {len(huts)} huts to {output_path}")
    return output_path

if __name__ == "__main__":
    export_huts_json()

