"""
API endpoint to serve real database statistics to the website
This can be run as a simple Flask server or used to generate static JSON
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

import sqlite3
import json
from pathlib import Path

def get_database_stats():
    """Get real statistics from the database"""
    db_path = Path(__file__).parent.parent.parent / "data" / "mountain_huts.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    stats = {}
    
    # Total huts
    cursor.execute("SELECT COUNT(*) FROM mountain_huts")
    stats['total_huts'] = cursor.fetchone()[0]
    
    # Count by country
    cursor.execute("""
        SELECT country, COUNT(*) as count
        FROM mountain_huts
        WHERE country IS NOT NULL AND country != ''
        GROUP BY country
        ORDER BY count DESC
    """)
    stats['by_country'] = [
        {'country': row[0], 'count': row[1]}
        for row in cursor.fetchall()
    ]
    stats['countries_count'] = len(stats['by_country'])
    
    # Count by source
    cursor.execute("""
        SELECT source, COUNT(*) as count
        FROM mountain_huts
        GROUP BY source
        ORDER BY count DESC
    """)
    stats['by_source'] = [
        {'source': row[0], 'count': row[1]}
        for row in cursor.fetchall()
    ]
    stats['sources_count'] = len(stats['by_source'])
    
    # Huts with complete data
    cursor.execute("""
        SELECT COUNT(*) FROM mountain_huts
        WHERE phone IS NOT NULL AND phone != ''
           OR email IS NOT NULL AND email != ''
           OR website IS NOT NULL AND website != ''
    """)
    stats['with_contact_info'] = cursor.fetchone()[0]
    
    # Percentage with trail access/capacity
    stats['with_details_percent'] = int((stats['with_contact_info'] / stats['total_huts']) * 100)
    
    # Count by hut type
    cursor.execute("""
        SELECT hut_type, COUNT(*) as count
        FROM mountain_huts
        WHERE hut_type IS NOT NULL AND hut_type != ''
        GROUP BY hut_type
        ORDER BY count DESC
        LIMIT 5
    """)
    stats['by_type'] = [
        {'type': row[0], 'count': row[1]}
        for row in cursor.fetchall()
    ]
    
    # Get altitude stats
    cursor.execute("""
        SELECT AVG(altitude), MIN(altitude), MAX(altitude)
        FROM mountain_huts
        WHERE altitude IS NOT NULL AND altitude > 0
    """)
    row = cursor.fetchone()
    stats['altitude'] = {
        'average': int(row[0]) if row[0] else 0,
        'min': int(row[1]) if row[1] else 0,
        'max': int(row[2]) if row[2] else 0
    }
    
    conn.close()
    return stats

def export_stats_json():
    """Export stats to a JSON file for static hosting"""
    stats = get_database_stats()
    
    # Export to web/data directory
    data_dir = Path(__file__).parent.parent.parent / "web" / "data"
    data_dir.mkdir(exist_ok=True)
    
    # Write stats to JSON file
    output_path = data_dir / "stats.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    
    print(f"Statistics exported to {output_path}")
    return output_path

if __name__ == "__main__":
    export_stats_json()

