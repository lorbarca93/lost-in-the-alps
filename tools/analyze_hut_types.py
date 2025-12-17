#!/usr/bin/env python3
"""
Analyze hut types across all sources to understand categorization
"""
import sqlite3
from pathlib import Path
from collections import defaultdict

def analyze_hut_types():
    db_path = Path(__file__).parent.parent / "data" / "mountain_huts.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("=" * 70)
    print("HUT TYPE ANALYSIS")
    print("=" * 70)
    
    # 1. Current hut types in database
    print("\n1. CURRENT HUT TYPES IN DATABASE")
    print("-" * 50)
    cursor.execute("""
        SELECT hut_type, COUNT(*) as cnt 
        FROM mountain_huts 
        GROUP BY hut_type 
        ORDER BY cnt DESC
    """)
    for row in cursor.fetchall():
        hut_type = row[0] or "NULL/Empty"
        print(f"  {hut_type}: {row[1]}")
    
    # 2. Hut types by source
    print("\n2. HUT TYPES BY SOURCE")
    print("-" * 50)
    cursor.execute("""
        SELECT source, hut_type, COUNT(*) as cnt 
        FROM mountain_huts 
        GROUP BY source, hut_type 
        ORDER BY source, cnt DESC
    """)
    
    current_source = None
    for row in cursor.fetchall():
        source, hut_type, count = row
        hut_type = hut_type or "NULL/Empty"
        if source != current_source:
            print(f"\n  {source}:")
            current_source = source
        print(f"    - {hut_type}: {count}")
    
    # 3. Sample huts for each type
    print("\n3. SAMPLE HUTS FOR EACH TYPE")
    print("-" * 50)
    cursor.execute("SELECT DISTINCT hut_type FROM mountain_huts WHERE hut_type IS NOT NULL")
    hut_types = [row[0] for row in cursor.fetchall()]
    
    for hut_type in hut_types:
        print(f"\n  [{hut_type}]")
        cursor.execute("""
            SELECT name, source, altitude, country
            FROM mountain_huts 
            WHERE hut_type = ?
            LIMIT 5
        """, (hut_type,))
        for row in cursor.fetchall():
            name, source, alt, country = row
            alt_str = f"{alt}m" if alt else "N/A"
            print(f"    - {name} ({source}, {alt_str}, {country})")
    
    # 4. Analyze descriptions for clues
    print("\n4. DESCRIPTION KEYWORD ANALYSIS")
    print("-" * 50)
    keywords = {
        'staffed': ['staffed', 'manned', 'warden', 'guardian', 'gardien', 'gardé', 'bewirtschaftet'],
        'unstaffed': ['unstaffed', 'unmanned', 'self-service', 'non gardé', 'unbewirtschaftet'],
        'bivouac': ['bivouac', 'bivacco', 'biwak', 'bivak', 'emergency'],
        'shelter': ['shelter', 'abri', 'refuge', 'schutzhütte', 'notunterkunft'],
        'cabin': ['cabin', 'cabane', 'cabana', 'hütte', 'hutte', 'chata', 'koča'],
        'guesthouse': ['guesthouse', 'gîte', 'gite', 'pension', 'gasthaus', 'albergo', 'hotel'],
        'alpine_club': ['cai', 'sac', 'caf', 'dav', 'öav', 'pza', 'alpine club'],
    }
    
    for category, kws in keywords.items():
        cursor.execute("""
            SELECT COUNT(*) FROM mountain_huts 
            WHERE LOWER(description) LIKE ? OR LOWER(name) LIKE ?
        """, ('%' + kws[0].lower() + '%', '%' + kws[0].lower() + '%'))
        count = cursor.fetchone()[0]
        if count > 0:
            print(f"  {category}: ~{count} mentions")
    
    # 5. Altitude distribution by type
    print("\n5. ALTITUDE DISTRIBUTION BY TYPE")
    print("-" * 50)
    cursor.execute("""
        SELECT hut_type, 
               COUNT(*) as cnt,
               ROUND(AVG(altitude), 0) as avg_alt,
               MIN(altitude) as min_alt,
               MAX(altitude) as max_alt
        FROM mountain_huts 
        WHERE altitude IS NOT NULL AND hut_type IS NOT NULL
        GROUP BY hut_type
        ORDER BY avg_alt DESC
    """)
    print(f"  {'Type':<20} {'Count':<8} {'Avg Alt':<10} {'Min':<8} {'Max':<8}")
    print(f"  {'-'*20} {'-'*8} {'-'*10} {'-'*8} {'-'*8}")
    for row in cursor.fetchall():
        hut_type, cnt, avg_alt, min_alt, max_alt = row
        print(f"  {hut_type:<20} {cnt:<8} {avg_alt or 'N/A':<10} {min_alt or 'N/A':<8} {max_alt or 'N/A':<8}")
    
    # 6. Proposed categorization based on analysis
    print("\n" + "=" * 70)
    print("PROPOSED HUT CATEGORIZATION")
    print("=" * 70)
    
    proposed = """
Based on the analysis, here's a proposed categorization:

1. STAFFED MOUNTAIN HUT (Refuge gardé)
   - Has staff during season
   - Provides meals and services
   - Usually has beds/dorms
   - Examples: DAV huts, CAI rifugi, SAC huts
   
2. UNSTAFFED MOUNTAIN HUT (Refuge non gardé)
   - No permanent staff
   - Basic amenities (beds, kitchen)
   - Self-service, often with payment box
   - Examples: Many French cabanes, some Swiss huts
   
3. BIVOUAC (Bivouac / Emergency Shelter)
   - Very basic shelter
   - Usually no beds, just floor space
   - Emergency use primarily
   - High altitude, remote locations
   - Examples: Italian bivacchi, alpine emergency shelters
   
4. ALPINE SHELTER (Schutzhütte)
   - Intermediate between hut and bivouac
   - May have basic beds
   - No cooking facilities usually
   - Often unmanned
   
5. GUESTHOUSE (Gîte d'étape)
   - Valley or lower altitude
   - More comfortable
   - Usually with restaurant
   - Aimed at hikers/trekkers
   
6. ALPINE CLUB HUT (Club Hut)
   - Owned by alpine club (CAI, SAC, DAV, etc.)
   - Usually staffed in season
   - Member discounts
   - Mountaineering focus
"""
    print(proposed)
    
    conn.close()

if __name__ == "__main__":
    analyze_hut_types()

