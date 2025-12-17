"""
Database migration to harmonize hut type column
- Rename type_description to hut_type
- Consolidate all type information into hut_type
- Standardize type values across all sources
"""
import sqlite3
from datetime import datetime

def migrate_database():
    conn = sqlite3.connect('data/mountain_huts.db')
    cursor = conn.cursor()
    
    print("=" * 70)
    print("DATABASE MIGRATION: Harmonizing Hut Types")
    print("=" * 70)
    
    # Step 1: Add new hut_type column
    print("\n1. Adding new 'hut_type' column...")
    try:
        cursor.execute('ALTER TABLE mountain_huts ADD COLUMN hut_type TEXT')
        print("   ✅ Column added")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("   ⚠️  Column already exists, continuing...")
        else:
            raise
    
    # Step 2: Create type mapping dictionary
    print("\n2. Creating type mapping...")
    type_mapping = {
        # Boudy.info numeric types
        ('0', 'Unidentified object'): 'Unknown',
        ('1', 'Bivouac/camping spot'): 'Bivouac',
        ('2', 'Shelter/hut'): 'Mountain hut',
        ('3', 'Mountain hut/hotel'): 'Mountain hut',
        
        # Mountain-huts.net text types
        ('mountain_hut', None): 'Mountain hut',
        ('bivouac', None): 'Bivouac',
        ('shelter', None): 'Shelter',
        
        # Mountainhuts.info type_description
        (None, 'Mountain hut'): 'Mountain hut',
        (None, 'Mountain Hut'): 'Mountain hut',
        
        # Refuges.info types
        ('Unmanned cabin', None): 'Unmanned cabin',
        ('Staffed refuge', None): 'Staffed refuge',
        ('Guesthouse', None): 'Guesthouse',
        ('Cave shelter', None): 'Cave shelter',
        ('Bivouac shelter', None): 'Bivouac',
        
        # Default for None/None
        (None, None): None
    }
    
    # Step 3: Update hut_type based on existing data
    print("\n3. Migrating type data to hut_type...")
    
    # Get all distinct type combinations
    cursor.execute('SELECT DISTINCT type, type_description, source FROM mountain_huts')
    combinations = cursor.fetchall()
    
    updated = 0
    for type_val, type_desc, source in combinations:
        # Convert type to string for comparison
        type_str = str(type_val) if type_val is not None else None
        
        # Find matching mapping
        new_type = None
        for (t, td), mapped in type_mapping.items():
            if t == type_str and td == type_desc:
                new_type = mapped
                break
        
        # If no exact match, try partial matches
        if new_type is None:
            if type_desc and type_desc not in [None, 'None']:
                new_type = type_desc
            elif type_str and type_str not in [None, 'None']:
                # Try to use the type column if it's text
                if not type_str.isdigit():
                    new_type = type_str
        
        # Update records
        if type_val is None and type_desc is None:
            cursor.execute(
                'UPDATE mountain_huts SET hut_type = ? WHERE (type IS NULL OR type = "") AND (type_description IS NULL OR type_description = "") AND source = ?',
                (new_type, source)
            )
        elif type_val is None:
            cursor.execute(
                'UPDATE mountain_huts SET hut_type = ? WHERE (type IS NULL OR type = "") AND type_description = ? AND source = ?',
                (new_type, type_desc, source)
            )
        elif type_desc is None:
            cursor.execute(
                'UPDATE mountain_huts SET hut_type = ? WHERE type = ? AND (type_description IS NULL OR type_description = "") AND source = ?',
                (new_type, type_val, source)
            )
        else:
            cursor.execute(
                'UPDATE mountain_huts SET hut_type = ? WHERE type = ? AND type_description = ? AND source = ?',
                (new_type, type_val, type_desc, source)
            )
        
        count = cursor.rowcount
        updated += count
        if count > 0:
            print(f"   Updated {count:4d} records: type={type_val}, type_desc={type_desc}, source={source:20s} -> {new_type}")
    
    print(f"\n   ✅ Total records updated: {updated}")
    
    # Step 4: Show statistics
    print("\n4. New hut_type distribution:")
    cursor.execute('SELECT hut_type, COUNT(*) as cnt FROM mountain_huts GROUP BY hut_type ORDER BY cnt DESC')
    for hut_type, count in cursor.fetchall():
        print(f"   {str(hut_type):30s}: {count:4d} huts")
    
    # Step 5: Drop old columns (optional - commented out for safety)
    print("\n5. Cleaning up old columns...")
    print("   ⚠️  Keeping 'type' and 'type_description' for now (can be removed later)")
    # Uncomment these lines if you want to remove the old columns:
    # cursor.execute('ALTER TABLE mountain_huts DROP COLUMN type')
    # cursor.execute('ALTER TABLE mountain_huts DROP COLUMN type_description')
    
    # Commit changes
    conn.commit()
    
    print("\n" + "=" * 70)
    print("✅ Migration completed successfully!")
    print("=" * 70)
    
    conn.close()

if __name__ == "__main__":
    migrate_database()
