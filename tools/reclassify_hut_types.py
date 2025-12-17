#!/usr/bin/env python3
"""
Reclassify hut types in the database using improved categorization

New Categories:
1. Staffed hut - Has warden, meals, services (refuge gardé)
2. Unstaffed cabin - Self-service, basic amenities (cabane non gardée)
3. Bivouac - Emergency shelter, very basic
4. Shelter - Basic weather shelter
5. Guesthouse - Valley accommodation (gîte d'étape)
6. Unknown - Fallback
"""
import sqlite3
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))
from data_cleaner import standardize_hut_type

def reclassify_huts():
    db_path = Path(__file__).parent.parent / "data" / "mountain_huts.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("=" * 70)
    print("HUT TYPE RECLASSIFICATION")
    print("=" * 70)
    
    # Show current distribution
    print("\n1. CURRENT TYPE DISTRIBUTION (BEFORE)")
    print("-" * 50)
    cursor.execute("""
        SELECT hut_type, COUNT(*) as cnt 
        FROM mountain_huts 
        GROUP BY hut_type 
        ORDER BY cnt DESC
    """)
    before = {row[0]: row[1] for row in cursor.fetchall()}
    for hut_type, count in before.items():
        print(f"  {hut_type or 'NULL'}: {count}")
    
    # Get all huts with their current types and names
    print("\n2. RECLASSIFYING HUTS...")
    print("-" * 50)
    
    cursor.execute("""
        SELECT id, name, hut_type, source
        FROM mountain_huts
    """)
    huts = cursor.fetchall()
    
    updates = []
    changes = {}
    
    for hut_id, name, current_type, source in huts:
        # Determine new type based on current type and name
        # First try current type
        new_type = standardize_hut_type(current_type)
        
        # If still unknown, try to infer from name
        if new_type == 'Unknown' and name:
            # Check name for clues
            name_lower = name.lower()
            
            if any(kw in name_lower for kw in ['bivouac', 'bivacco', 'bivak', 'biwak']):
                new_type = 'Bivouac'
            elif any(kw in name_lower for kw in ['gîte', 'gite', 'auberge', 'hotel']):
                new_type = 'Guesthouse'
            elif any(kw in name_lower for kw in ['zavetišče', 'shelter']):
                new_type = 'Shelter'
            elif any(kw in name_lower for kw in ['cabane', 'abri', 'chalet']):
                new_type = 'Unstaffed cabin'
            elif any(kw in name_lower for kw in ['refuge', 'rifugio', 'hütte', 'koča', 'dom', 'chata']):
                # Check if likely staffed or unstaffed
                if source == 'tyrol.com' or source == 'mountainhuts.info':
                    new_type = 'Staffed hut'  # These sources mainly have staffed huts
                else:
                    new_type = 'Staffed hut'  # Default refuge to staffed
        
        if new_type != current_type:
            updates.append((new_type, hut_id))
            key = f"{current_type or 'NULL'} -> {new_type}"
            changes[key] = changes.get(key, 0) + 1
    
    # Show planned changes
    print(f"\n  Total huts: {len(huts)}")
    print(f"  To be updated: {len(updates)}")
    print("\n  Change summary:")
    for change, count in sorted(changes.items(), key=lambda x: -x[1]):
        print(f"    {change}: {count}")
    
    # Apply updates
    print("\n3. APPLYING UPDATES...")
    print("-" * 50)
    
    cursor.executemany("""
        UPDATE mountain_huts SET hut_type = ? WHERE id = ?
    """, updates)
    
    conn.commit()
    print(f"  Updated {len(updates)} records")
    
    # Show new distribution
    print("\n4. NEW TYPE DISTRIBUTION (AFTER)")
    print("-" * 50)
    cursor.execute("""
        SELECT hut_type, COUNT(*) as cnt 
        FROM mountain_huts 
        GROUP BY hut_type 
        ORDER BY cnt DESC
    """)
    after = {row[0]: row[1] for row in cursor.fetchall()}
    for hut_type, count in after.items():
        change = count - before.get(hut_type, 0)
        change_str = f" ({'+' if change > 0 else ''}{change})" if change != 0 else ""
        print(f"  {hut_type or 'NULL'}: {count}{change_str}")
    
    # Show samples for each new type
    print("\n5. SAMPLE HUTS FOR EACH NEW TYPE")
    print("-" * 50)
    
    for hut_type in after.keys():
        if hut_type:
            print(f"\n  [{hut_type}]")
            cursor.execute("""
                SELECT name, source, altitude, country
                FROM mountain_huts 
                WHERE hut_type = ?
                ORDER BY RANDOM()
                LIMIT 3
            """, (hut_type,))
            for row in cursor.fetchall():
                name, source, alt, country = row
                alt_str = f"{alt}m" if alt else "N/A"
                print(f"    - {name} ({source}, {alt_str}, {country})")
    
    conn.close()
    
    print("\n" + "=" * 70)
    print("RECLASSIFICATION COMPLETE!")
    print("=" * 70)
    print("\nNext steps:")
    print("  1. Run: python tools/generate_huts_json.py")
    print("  2. Refresh the web app to see updated types")

if __name__ == "__main__":
    reclassify_huts()

