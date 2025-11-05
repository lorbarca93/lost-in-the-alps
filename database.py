"""
Database layer for mountain huts
This module handles all database operations and can be used by multiple scrapers
"""

import sqlite3
from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime


class MountainHutsDatabase:
    """Centralized database handler for mountain huts from multiple sources"""
    
    def __init__(self, db_path: str = "data/mountain_huts.db") -> None:
        self.db_path = db_path
    
    def init_database(self) -> None:
        """Initialize the SQLite database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create main huts table with clean schema
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mountain_huts (
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
        
        # Create sources table to track different websites
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scraper_sources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                url TEXT NOT NULL,
                description TEXT,
                last_scraped TIMESTAMP,
                total_huts INTEGER DEFAULT 0
            )
        """)
        
        # Create indexes for faster lookups
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_name ON mountain_huts(name)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_location ON mountain_huts(latitude, longitude)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_source ON mountain_huts(source)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_country ON mountain_huts(country)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_hut_type ON mountain_huts(hut_type)
        """)
        
        conn.commit()
        conn.close()
        print(f"Database initialized at {self.db_path}")
    
    def register_source(self, name: str, url: str, description: str = "") -> None:
        """Register a scraper source"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR IGNORE INTO scraper_sources (name, url, description)
            VALUES (?, ?, ?)
        """, (name, url, description))
        
        conn.commit()
        conn.close()
    
    def update_source_stats(self, source_name: str) -> None:
        """Update statistics for a source after scraping"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Count huts from this source
        cursor.execute("SELECT COUNT(*) FROM mountain_huts WHERE source = ?", (source_name,))
        count = cursor.fetchone()[0]
        
        # Update source record
        cursor.execute("""
            UPDATE scraper_sources 
            SET last_scraped = ?, total_huts = ?
            WHERE name = ?
        """, (datetime.now(), count, source_name))
        
        conn.commit()
        conn.close()
    
    def save_hut(self, hut: Dict, source: str) -> bool:
        """
        Save or update a single hut
        Returns True if successful
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Check if hut already exists
            cursor.execute(
                "SELECT id FROM mountain_huts WHERE source = ? AND source_id = ?",
                (source, hut.get('source_id'))
            )
            existing = cursor.fetchone()
            
            if existing:
                # Update existing hut - preserve country if scraper doesn't provide it
                # Get existing country value
                cursor.execute("SELECT country FROM mountain_huts WHERE source = ? AND source_id = ?",
                             (source, hut.get('source_id')))
                existing_country = cursor.fetchone()[0]
                
                # Use scraped country only if it's provided and not None/empty
                country_to_save = hut.get('country')
                if not country_to_save or country_to_save in ['', 'None']:
                    country_to_save = existing_country  # Preserve existing
                
                cursor.execute("""
                    UPDATE mountain_huts 
                    SET name = ?, hut_type = ?, 
                        status = ?, status_description = ?,
                        latitude = ?, longitude = ?, altitude = ?,
                        description = ?, url = ?, country = ?, region = ?,
                        amenities = ?, capacity = ?, phone = ?, email = ?,
                        website = ?, opening_hours = ?, image_url = ?,
                        owner = ?, manager = ?,
                        capacity_max = ?, comments = ?, water_source = ?,
                        best_time_to_visit = ?, access = ?, posted_by = ?, posted_date = ?,
                        updated_at = ?
                    WHERE source = ? AND source_id = ?
                """, (
                    hut.get('name', 'Unknown'),
                    hut.get('hut_type') or hut.get('type'),
                    hut.get('status'),
                    hut.get('status_description'),
                    hut.get('latitude'),
                    hut.get('longitude'),
                    hut.get('altitude'),
                    hut.get('description', ''),
                    hut.get('url', ''),
                    country_to_save,  # Use preserved or new country
                    hut.get('region', ''),
                    hut.get('amenities', ''),
                    hut.get('capacity'),
                    hut.get('phone', ''),
                    hut.get('email', ''),
                    hut.get('website', ''),
                    hut.get('opening_hours', ''),
                    hut.get('image_url', ''),
                    hut.get('owner', ''),
                    hut.get('manager', ''),
                    hut.get('capacity_max'),
                    hut.get('comments', ''),
                    hut.get('water_source', ''),
                    hut.get('best_time_to_visit', ''),
                    hut.get('access', ''),
                    hut.get('posted_by', ''),
                    hut.get('posted_date', ''),
                    datetime.now(),
                    source,
                    hut.get('source_id')
                ))
            else:
                # Insert new hut
                cursor.execute("""
                    INSERT INTO mountain_huts 
                    (source, source_id, name, hut_type, status, status_description,
                     latitude, longitude, altitude, description, url, country, region,
                     amenities, capacity, phone, email, website, opening_hours, image_url,
                     owner, manager, capacity_max, comments, water_source, 
                     best_time_to_visit, access, posted_by, posted_date, scraped_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    source,
                    hut.get('source_id'),
                    hut.get('name', 'Unknown'),
                    hut.get('hut_type') or hut.get('type'),
                    hut.get('status'),
                    hut.get('status_description'),
                    hut.get('latitude'),
                    hut.get('longitude'),
                    hut.get('altitude'),
                    hut.get('description', ''),
                    hut.get('url', ''),
                    hut.get('country', ''),
                    hut.get('region', ''),
                    hut.get('amenities', ''),
                    hut.get('capacity'),
                    hut.get('phone', ''),
                    hut.get('email', ''),
                    hut.get('website', ''),
                    hut.get('opening_hours', ''),
                    hut.get('image_url', ''),
                    hut.get('owner', ''),
                    hut.get('manager', ''),
                    hut.get('capacity_max'),
                    hut.get('comments', ''),
                    hut.get('water_source', ''),
                    hut.get('best_time_to_visit', ''),
                    hut.get('access', ''),
                    hut.get('posted_by', ''),
                    hut.get('posted_date', ''),
                    datetime.now(),
                    datetime.now()
                ))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error saving hut {hut.get('name', 'Unknown')}: {e}")
            conn.close()
            return False
    
    def save_huts_batch(self, huts: List[Dict], source: str) -> int:
        """
        Save multiple huts in a batch
        Returns number of huts saved
        """
        saved_count: int = 0
        for hut in huts:
            if self.save_hut(hut, source):
                saved_count += 1
        
        # Update source statistics
        self.update_source_stats(source)
        
        return saved_count
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics including sources"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {}
        
        # Total count
        cursor.execute("SELECT COUNT(*) FROM mountain_huts")
        stats['total_huts'] = cursor.fetchone()[0]
        
        # Count by source
        cursor.execute("""
            SELECT source, COUNT(*) as count 
            FROM mountain_huts 
            GROUP BY source
        """)
        stats['by_source'] = [
            {'source': row[0], 'count': row[1]}
            for row in cursor.fetchall()
        ]
        
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
        
        # Count by hut type
        cursor.execute("""
            SELECT hut_type, COUNT(*) as count 
            FROM mountain_huts 
            GROUP BY hut_type
            ORDER BY count DESC
        """)
        stats['by_type'] = [
            {'type': row[0] or 'Unknown', 'count': row[1]}
            for row in cursor.fetchall()
        ]
        
        # Huts with coordinates
        cursor.execute("""
            SELECT COUNT(*) FROM mountain_huts 
            WHERE latitude IS NOT NULL AND longitude IS NOT NULL
        """)
        stats['with_coordinates'] = cursor.fetchone()[0]
        
        # Source information
        cursor.execute("SELECT name, url, last_scraped, total_huts FROM scraper_sources")
        stats['sources'] = [
            {
                'name': row[0],
                'url': row[1],
                'last_scraped': row[2],
                'total_huts': row[3]
            }
            for row in cursor.fetchall()
        ]
        
        conn.close()
        return stats
