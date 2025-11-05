"""Generate all website data files after database updates"""

import json
import sqlite3
from datetime import datetime

def generate_stats():
    """Generate stats.json"""
    conn = sqlite3.connect('data/mountain_huts.db')
    cursor = conn.cursor()
    
    # Get statistics
    cursor.execute('SELECT COUNT(*) FROM mountain_huts')
    total_huts = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(DISTINCT country) FROM mountain_huts WHERE country IS NOT NULL AND country != ''")
    total_countries = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(DISTINCT source) FROM mountain_huts')
    total_sources = cursor.fetchone()[0]
    
    cursor.execute('SELECT AVG(altitude) FROM mountain_huts WHERE altitude IS NOT NULL')
    avg_altitude = int(cursor.fetchone()[0])
    
    # Get huts by source
    cursor.execute('SELECT source, COUNT(*) FROM mountain_huts GROUP BY source')
    by_source = {row[0]: row[1] for row in cursor.fetchall()}
    
    # Get huts by country  
    cursor.execute("SELECT country, COUNT(*) FROM mountain_huts WHERE country IS NOT NULL AND country != '' GROUP BY country ORDER BY COUNT(*) DESC")
    by_country = {row[0]: row[1] for row in cursor.fetchall()}
    
    stats = {
        'total_huts': total_huts,
        'total_countries': total_countries,
        'total_sources': total_sources,
        'average_altitude': avg_altitude,
        'by_source': by_source,
        'by_country': by_country,
        'last_updated': datetime.now().strftime('%Y-%m-%d')
    }
    
    with open('website/api/stats.json', 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    
    print(f'Generated stats.json:')
    print(f'  Total huts: {total_huts}')
    print(f'  Countries: {total_countries}')
    print(f'  Sources: {total_sources}')
    
    conn.close()
    return stats

def generate_huts_json():
    """Generate simplified huts.json"""
    conn = sqlite3.connect('data/mountain_huts.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT name, latitude, longitude, altitude, country, hut_type, source
        FROM mountain_huts
        WHERE latitude IS NOT NULL AND longitude IS NOT NULL
    ''')
    
    huts_simple = []
    for row in cursor.fetchall():
        huts_simple.append({
            'name': row[0],
            'lat': row[1],
            'lon': row[2],
            'alt': row[3],
            'country': row[4],
            'type': row[5],
            'source': row[6]
        })
    
    with open('website/api/huts.json', 'w', encoding='utf-8') as f:
        json.dump(huts_simple, f, separators=(',', ':'), ensure_ascii=False)
    
    print(f'Generated huts.json with {len(huts_simple)} huts')
    
    conn.close()

if __name__ == '__main__':
    print('=' * 60)
    print('GENERATING WEBSITE DATA FILES')
    print('=' * 60)
    
    stats = generate_stats()
    generate_huts_json()
    
    print('\n[SUCCESS] All data files generated!')

