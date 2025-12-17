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
        with sqlite3.connect(self.db_path) as conn:
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
            
            # Run database migrations to add new columns if needed
            self._migrate_database()
            
            print(f"Database initialized at {self.db_path}")
    
    def _migrate_database(self) -> None:
        """
        Migrate database schema to add new columns
        Safely adds columns if they don't exist (backward compatible)
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get existing columns
            cursor.execute("PRAGMA table_info(mountain_huts)")
            existing_columns = {row[1] for row in cursor.fetchall()}
            
            # New service fields to add
            new_columns = {
                'has_water_access': 'INTEGER',  # 0/1 or NULL
                'has_hot_water': 'INTEGER',     # 0/1 or NULL
                'has_electricity': 'INTEGER',   # 0/1 or NULL
                'accessible_by_car': 'INTEGER', # 0/1 or NULL
                'management_type': 'TEXT'       # V-box sociale, Managed, Unmanaged, etc.
            }
            
            # Add missing columns
            for column_name, column_type in new_columns.items():
                if column_name not in existing_columns:
                    try:
                        cursor.execute(f"ALTER TABLE mountain_huts ADD COLUMN {column_name} {column_type}")
                        print(f"Added column: {column_name}")
                    except sqlite3.OperationalError as e:
                        # Column might already exist (race condition), ignore
                        if "duplicate column" not in str(e).lower():
                            print(f"Warning: Could not add column {column_name}: {e}")
            
            conn.commit()
    
    def register_source(self, name: str, url: str, description: str = "") -> None:
        """Register a scraper source"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR IGNORE INTO scraper_sources (name, url, description)
                VALUES (?, ?, ?)
            """, (name, url, description))
            
            conn.commit()
    
    def update_source_stats(self, source_name: str) -> None:
        """Update statistics for a source after scraping"""
        with sqlite3.connect(self.db_path) as conn:
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
    
    def save_hut(self, hut: Dict, source: str) -> bool:
        """
        Save or update a single hut with input validation
        Returns True if successful
        """
        # Input validation and sanitization
        if not isinstance(hut, dict):
            logger = logging.getLogger(__name__)
            logger.warning("Invalid hut data: not a dictionary")
            return False
        
        if not source or not isinstance(source, str) or len(source) > 100:
            logger = logging.getLogger(__name__)
            logger.warning(f"Invalid source: {source}")
            return False
        
        # Validate and sanitize source_id
        source_id = hut.get('source_id')
        if source_id and (not isinstance(source_id, str) or len(str(source_id)) > 255):
            logger = logging.getLogger(__name__)
            logger.warning(f"Invalid source_id length: {len(str(source_id))}")
            return False
        
        # Validate name
        name = hut.get('name', 'Unknown')
        if not isinstance(name, str) or len(name) > 500:
            logger = logging.getLogger(__name__)
            logger.warning(f"Invalid name length: {len(name) if isinstance(name, str) else 'not a string'}")
            return False
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Check if hut already exists and get country in one query
                cursor.execute(
                    "SELECT id, country FROM mountain_huts WHERE source = ? AND source_id = ?",
                    (source, hut.get('source_id'))
                )
                existing = cursor.fetchone()
                
                if existing:
                    # Update existing hut - preserve country if scraper doesn't provide it
                    existing_country = existing[1]  # Get country from the SELECT above
                    
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
                            has_water_access = ?, has_hot_water = ?, has_electricity = ?,
                            accessible_by_car = ?, management_type = ?,
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
                        hut.get('has_water_access'),
                        hut.get('has_hot_water'),
                        hut.get('has_electricity'),
                        hut.get('accessible_by_car'),
                        hut.get('management_type'),
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
                         best_time_to_visit, access, posted_by, posted_date,
                         has_water_access, has_hot_water, has_electricity,
                         accessible_by_car, management_type,
                         scraped_at, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                        hut.get('has_water_access'),
                        hut.get('has_hot_water'),
                        hut.get('has_electricity'),
                        hut.get('accessible_by_car'),
                        hut.get('management_type'),
                        datetime.now(),
                        datetime.now()
                    ))
                
                conn.commit()
                return True
                
        except sqlite3.IntegrityError as e:
            # Database constraint violation - don't expose internal details
            logger = logging.getLogger(__name__)
            logger.warning(f"Database constraint violation for hut: {hut.get('name', 'Unknown')}")
            return False
        except Exception as e:
            # Log full error internally but don't expose to user
            logger = logging.getLogger(__name__)
            logger.error(f"Error saving hut {hut.get('name', 'Unknown')}: {e}", exc_info=True)
            # Return False without exposing error details
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
        with sqlite3.connect(self.db_path) as conn:
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
            
            return stats
