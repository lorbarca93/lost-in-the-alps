"""
Database cleanup script to fix schema inconsistencies and improve data quality
"""
import sqlite3
import shutil
from datetime import datetime

def backup_database(db_path='data/mountain_huts.db'):
    """Create a backup before making changes"""
    backup_path = f'data/mountain_huts_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'
    shutil.copy(db_path, backup_path)
    print(f"[OK] Created backup at {backup_path}")
    return backup_path

def clean_schema(db_path='data/mountain_huts.db'):
    """Clean up the database schema"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("\n" + "="*80)
    print("CLEANING DATABASE SCHEMA")
    print("="*80)
    
    # Step 1: Create new clean table with proper structure
    print("\n1. Creating new clean table structure...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS mountain_huts_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT NOT NULL,
            source_id TEXT,
            name TEXT NOT NULL,
            hut_type TEXT,
            status INTEGER,
            status_description TEXT,
            latitude REAL,
            longitude REAL,
            altitude INTEGER,
            country TEXT,
            region TEXT,
            description TEXT,
            amenities TEXT,
            capacity INTEGER,
            capacity_max INTEGER,
            phone TEXT,
            email TEXT,
            website TEXT,
            url TEXT,
            opening_hours TEXT,
            owner TEXT,
            manager TEXT,
            water_source TEXT,
            access TEXT,
            best_time_to_visit TEXT,
            comments TEXT,
            image_url TEXT,
            posted_by TEXT,
            posted_date TEXT,
            scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(source, source_id)
        )
    """)
    print("   [OK] New table created")
    
    # Step 2: Migrate data from old table to new table
    print("\n2. Migrating data to new table...")
    cursor.execute("""
        INSERT INTO mountain_huts_new 
        (id, source, source_id, name, hut_type, status, status_description,
         latitude, longitude, altitude, country, region, description,
         amenities, capacity, capacity_max, phone, email, website, url,
         opening_hours, owner, manager, water_source, access, 
         best_time_to_visit, comments, image_url, posted_by, posted_date,
         scraped_at, updated_at)
        SELECT 
         id, source, source_id, name,
         COALESCE(hut_type, 
            CASE type 
                WHEN 1 THEN 'Mountain hut'
                WHEN 2 THEN 'Bivouac'
                WHEN 3 THEN 'Unmanned cabin'
                WHEN 4 THEN 'Shelter'
                ELSE 'Unknown'
            END),
         status, status_description,
         latitude, longitude, altitude, country, region, description,
         amenities, capacity, capacity_max, phone, email, website, url,
         opening_hours, owner, manager, water_source, access,
         best_time_to_visit, comments, image_url, posted_by, posted_date,
         scraped_at, updated_at
        FROM mountain_huts
    """)
    migrated = cursor.rowcount
    print(f"   [OK] Migrated {migrated} huts")
    
    # Step 3: Drop old table and rename new one
    print("\n3. Replacing old table with new one...")
    cursor.execute("DROP TABLE mountain_huts")
    cursor.execute("ALTER TABLE mountain_huts_new RENAME TO mountain_huts")
    print("   [OK] Table replaced")
    
    # Step 4: Recreate indexes
    print("\n4. Creating indexes...")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_name ON mountain_huts(name)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_location ON mountain_huts(latitude, longitude)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_source ON mountain_huts(source)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_country ON mountain_huts(country)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_hut_type ON mountain_huts(hut_type)")
    print("   [OK] Indexes created")
    
    # Step 5: Remove unused tables
    print("\n5. Checking for unused tables...")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name IN ('users', 'user_favorites')")
    unused_tables = [row[0] for row in cursor.fetchall()]
    
    if unused_tables:
        print(f"   Found unused tables: {', '.join(unused_tables)}")
        for table in unused_tables:
            cursor.execute(f"DROP TABLE {table}")
            print(f"   [OK] Dropped table: {table}")
    else:
        print("   No unused tables found")
    
    conn.commit()
    
    # Step 6: Verify the cleanup
    print("\n6. Verifying cleanup...")
    cursor.execute("SELECT COUNT(*) FROM mountain_huts")
    count = cursor.fetchone()[0]
    print(f"   [OK] Total huts in database: {count}")
    
    cursor.execute("PRAGMA table_info(mountain_huts)")
    columns = [row[1] for row in cursor.fetchall()]
    print(f"   [OK] Columns in clean schema: {len(columns)}")
    
    conn.close()
    print("\n" + "="*80)
    print("DATABASE CLEANUP COMPLETE")
    print("="*80)

def main():
    """Main cleanup function"""
    print("\nStarting database cleanup process...")
    
    # Create backup first
    backup_path = backup_database()
    
    # Clean the schema
    clean_schema()
    
    print(f"\nAll done! Original database backed up to {backup_path}")

if __name__ == "__main__":
    main()

