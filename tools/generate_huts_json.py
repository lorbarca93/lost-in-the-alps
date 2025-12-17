#!/usr/bin/env python3
"""
Simple script to generate huts_data.json from database
This is the ONLY script needed to export data for the web interface
"""
import sqlite3
import json
import sys
from pathlib import Path

# Fix Windows encoding issues
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def clean_string(s):
    """Clean string for JSON output"""
    if not s:
        return "N/A"
    s = str(s).replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
    s = ''.join(char for char in s if ord(char) >= 32 or char == ' ')
    return s.strip() or "N/A"

def generate_json():
    # Connect to database
    db_path = Path(__file__).parent.parent / "data" / "mountain_huts.db"
    conn = sqlite3.connect(db_path)
    
    # Get all huts with coordinates
    cursor = conn.execute("""
        SELECT name, latitude, longitude, altitude, country, hut_type, website, source,
               owner, manager, phone, email, opening_hours, description,
               capacity, capacity_max, comments, water_source, best_time_to_visit, 
               access, posted_by, url
        FROM mountain_huts
        WHERE latitude IS NOT NULL AND longitude IS NOT NULL
        ORDER BY name
    """)
    
    huts_data = []
    
    for hut in cursor.fetchall():
        # Determine color based on source
        source = hut[7]
        color_map = {
            'refuges.info': '#ea580c',
            'boudy.info': '#2563eb',
            'mountainhuts.info': '#16a34a',
            'mountain-huts.net': '#dc2626'
        }
        color = color_map.get(source, '#6b7280')
        
        huts_data.append({
            'name': clean_string(hut[0]),
            'lat': float(hut[1]),
            'lon': float(hut[2]),
            'altitude': clean_string(hut[3]) if hut[3] else "N/A",
            'country': clean_string(hut[4]) if hut[4] else "N/A",
            'type': clean_string(hut[5]) if hut[5] else "N/A",
            'website': clean_string(hut[6]) if hut[6] else "",
            'source': source,
            'color': color,
            'owner': clean_string(hut[8]) if hut[8] else "",
            'manager': clean_string(hut[9]) if hut[9] else "",
            'phone': clean_string(hut[10]) if hut[10] else "",
            'email': clean_string(hut[11]) if hut[11] else "",
            'opening': clean_string(hut[12]) if hut[12] else "",
            'description': clean_string(hut[13]) if hut[13] else "",
            'capacity': clean_string(hut[14]) if hut[14] else "",
            'capacity_max': clean_string(hut[15]) if hut[15] else "",
            'comments': clean_string(hut[16]) if hut[16] else "",
            'water_source': clean_string(hut[17]) if hut[17] else "",
            'best_time': clean_string(hut[18]) if hut[18] else "",
            'access': clean_string(hut[19]) if hut[19] else "",
            'posted_by': clean_string(hut[20]) if hut[20] else "",
            'url': clean_string(hut[21]) if len(hut) > 21 and hut[21] else ""
        })
    
    conn.close()
    
    # Write JSON
    json_path = Path(__file__).parent.parent / "web" / "data" / "huts_data.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(huts_data, f, indent=2, ensure_ascii=True)
    
    print(f"Created {json_path}")
    print(f"Exported {len(huts_data)} huts")
    return len(huts_data)

if __name__ == "__main__":
    count = generate_json()
    print(f"\nSuccess! {count} huts exported to web/data/huts_data.json")

