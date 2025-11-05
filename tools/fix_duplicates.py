"""
Fix duplicate entries from mountainhuts.info in the database
"""

import sqlite3
from typing import List, Tuple

def find_duplicates(db_path: str = "data/mountain_huts.db") -> List[Tuple]:
    """Find all duplicate entries from mountainhuts.info"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Find duplicates based on name and coordinates
    query = '''
    SELECT name, latitude, longitude, COUNT(*) as count, GROUP_CONCAT(id) as ids
    FROM mountain_huts 
    WHERE source = 'mountainhuts.info'
    GROUP BY name, latitude, longitude
    HAVING COUNT(*) > 1
    ORDER BY name
    '''
    
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    
    return results

def remove_duplicates(db_path: str = "data/mountain_huts.db", dry_run: bool = True):
    """Remove duplicate entries, keeping only the first one"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    duplicates = find_duplicates(db_path)
    
    print(f"Found {len(duplicates)} groups of duplicates")
    print(f"Total entries before cleanup: ", end="")
    cursor.execute('SELECT COUNT(*) FROM mountain_huts WHERE source = ?', ('mountainhuts.info',))
    print(cursor.fetchone()[0])
    
    removed_count = 0
    
    for name, lat, lon, count, ids_str in duplicates:
        ids = [int(i) for i in ids_str.split(',')]
        # Keep the first ID, remove the rest
        keep_id = ids[0]
        remove_ids = ids[1:]
        
        print(f"\n{name} ({lat}, {lon})")
        print(f"  Total duplicates: {count}")
        print(f"  Keeping ID: {keep_id}")
        print(f"  Removing IDs: {remove_ids}")
        
        if not dry_run:
            for remove_id in remove_ids:
                cursor.execute('DELETE FROM mountain_huts WHERE id = ?', (remove_id,))
                removed_count += 1
    
    if not dry_run:
        conn.commit()
        print(f"\n[SUCCESS] Removed {removed_count} duplicate entries")
        
        cursor.execute('SELECT COUNT(*) FROM mountain_huts WHERE source = ?', ('mountainhuts.info',))
        print(f"Total entries after cleanup: {cursor.fetchone()[0]}")
    else:
        print(f"\n[DRY RUN] Would remove {sum(int(count) - 1 for _, _, _, count, _ in duplicates)} duplicate entries")
        print("Run with dry_run=False to actually remove duplicates")
    
    conn.close()

def check_scraper_deduplication():
    """Check the scraper's deduplication logic"""
    print("\n=== CHECKING SCRAPER DEDUPLICATION LOGIC ===")
    
    try:
        with open('scrapers/scraper_mountainhuts_info.py', 'r', encoding='utf-8') as f:
            content = f.read()
            
        if 'source_id' in content:
            print("[OK] Scraper uses source_id field")
        else:
            print("[WARN] Scraper doesn't use source_id field")
            
        if 'latitude' in content and 'longitude' in content:
            print("[OK] Scraper extracts coordinates")
        else:
            print("[WARN] Scraper doesn't extract coordinates properly")
            
    except FileNotFoundError:
        print("[ERROR] Scraper file not found")

if __name__ == "__main__":
    print("=" * 60)
    print("MOUNTAINHUTS.INFO DUPLICATE DETECTION AND REMOVAL")
    print("=" * 60)
    
    # First, check scraper logic
    check_scraper_deduplication()
    
    print("\n" + "=" * 60)
    print("STEP 1: DRY RUN - Analyzing duplicates")
    print("=" * 60)
    
    # Dry run first
    remove_duplicates(dry_run=True)
    
    print("\n" + "=" * 60)
    print("STEP 2: Do you want to remove duplicates? (yes/no)")
    print("=" * 60)
    
    response = input("Enter 'yes' to proceed: ").strip().lower()
    
    if response == 'yes':
        print("\n[REMOVING] Removing duplicates...")
        remove_duplicates(dry_run=False)
        print("\n[SUCCESS] Cleanup complete!")
    else:
        print("\n[CANCELLED] No changes made.")

