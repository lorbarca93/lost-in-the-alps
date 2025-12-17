"""
Query tool for mountain huts database
Provides various ways to search and analyze the scraped data
"""

import sqlite3
from typing import List, Dict, Optional
import json
from pathlib import Path


class MountainHutsDB:
    def __init__(self, db_path: str = None):
        if db_path is None:
            # Default to data/mountain_huts.db relative to parent directory
            db_path = str(Path(__file__).parent.parent / 'data' / 'mountain_huts.db')
        self.db_path = db_path
    
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def get_all_huts(self) -> List[Dict]:
        """Get all mountain huts"""
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM mountain_huts ORDER BY name")
        rows = cursor.fetchall()
        
        conn.close()
        return [dict(row) for row in rows]
    
    def search_by_name(self, name: str) -> List[Dict]:
        """Search huts by name"""
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM mountain_huts WHERE name LIKE ? ORDER BY name",
            (f"%{name}%",)
        )
        rows = cursor.fetchall()
        
        conn.close()
        return [dict(row) for row in rows]
    
    def get_by_type(self, hut_type: int) -> List[Dict]:
        """Get huts by type (0=unidentified, 1=bivouac, 2=shelter, 3=hut/hotel)"""
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM mountain_huts WHERE type = ? ORDER BY name",
            (hut_type,)
        )
        rows = cursor.fetchall()
        
        conn.close()
        return [dict(row) for row in rows]
    
    def get_by_location(self, lat: float, lon: float, radius_km: float = 10.0) -> List[Dict]:
        """
        Get huts near a location
        radius_km: search radius in kilometers
        Simple approximation: 1 degree ≈ 111 km
        """
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        lat_range = radius_km / 111.0
        lon_range = radius_km / (111.0 * abs(0.5))  # Rough approximation
        
        cursor.execute("""
            SELECT *, 
                   (ABS(latitude - ?) + ABS(longitude - ?)) as distance
            FROM mountain_huts 
            WHERE latitude BETWEEN ? AND ?
              AND longitude BETWEEN ? AND ?
              AND latitude IS NOT NULL
              AND longitude IS NOT NULL
            ORDER BY distance
        """, (
            lat, lon,
            lat - lat_range, lat + lat_range,
            lon - lon_range, lon + lon_range
        ))
        rows = cursor.fetchall()
        
        conn.close()
        return [dict(row) for row in rows]
    
    def get_statistics(self) -> Dict:
        """Get database statistics"""
        conn = self.get_connection()
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
        
        # Count by type
        cursor.execute("""
            SELECT type, type_description, COUNT(*) as count 
            FROM mountain_huts 
            WHERE type IS NOT NULL
            GROUP BY type, type_description
        """)
        stats['by_type'] = [
            {'type': row[0], 'description': row[1], 'count': row[2]}
            for row in cursor.fetchall()
        ]
        
        # Count by status
        cursor.execute("""
            SELECT status, status_description, COUNT(*) as count 
            FROM mountain_huts 
            WHERE status IS NOT NULL
            GROUP BY status, status_description
        """)
        stats['by_status'] = [
            {'status': row[0], 'description': row[1], 'count': row[2]}
            for row in cursor.fetchall()
        ]
        
        # Huts with coordinates
        cursor.execute("""
            SELECT COUNT(*) FROM mountain_huts 
            WHERE latitude IS NOT NULL AND longitude IS NOT NULL
        """)
        stats['with_coordinates'] = cursor.fetchone()[0]
        
        # Altitude statistics
        cursor.execute("""
            SELECT 
                MIN(altitude) as min_altitude,
                MAX(altitude) as max_altitude,
                AVG(altitude) as avg_altitude
            FROM mountain_huts 
            WHERE altitude IS NOT NULL
        """)
        row = cursor.fetchone()
        stats['altitude'] = {
            'min': row[0],
            'max': row[1],
            'average': round(row[2], 2) if row[2] else None
        }
        
        conn.close()
        return stats
    
    def export_to_json(self, filename: str = "mountain_huts.json"):
        """Export all data to JSON file"""
        huts = self.get_all_huts()
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(huts, f, indent=2, ensure_ascii=False)
        
        print(f"Exported {len(huts)} huts to {filename}")
    
    def export_to_csv(self, filename: str = "mountain_huts.csv"):
        """Export all data to CSV file"""
        import csv
        
        huts = self.get_all_huts()
        
        if not huts:
            print("No data to export")
            return
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=huts[0].keys())
            writer.writeheader()
            writer.writerows(huts)
        
        print(f"Exported {len(huts)} huts to {filename}")
    
    def print_hut(self, hut: Dict):
        """Pretty print a hut's information"""
        print("\n" + "=" * 60)
        print(f"Name: {hut.get('name', 'Unknown')}")
        print(f"Type: {hut.get('type_description', 'Unknown')}")
        print(f"Status: {hut.get('status_description', 'Unknown')}")
        
        if hut.get('latitude') and hut.get('longitude'):
            print(f"Location: {hut['latitude']:.6f}, {hut['longitude']:.6f}")
        
        if hut.get('altitude'):
            print(f"Altitude: {hut['altitude']} m")
        
        if hut.get('url'):
            print(f"URL: {hut['url']}")
        
        if hut.get('description'):
            print(f"\nDescription: {hut['description'][:200]}...")
        
        print("=" * 60)


def main():
    """Interactive query interface"""
    db = MountainHutsDB()
    
    print("Mountain Huts Database Query Tool")
    print("=" * 60)
    print("\nCommands:")
    print("  1. stats       - Show database statistics")
    print("  2. all         - List all huts")
    print("  3. search      - Search by name")
    print("  4. type        - Filter by type")
    print("  5. location    - Search by location")
    print("  6. export-json - Export to JSON")
    print("  7. export-csv  - Export to CSV")
    print("  8. quit        - Exit")
    print("=" * 60)
    
    while True:
        try:
            command = input("\nEnter command: ").strip().lower()
            
            if command in ['quit', 'exit', 'q']:
                break
            
            elif command in ['stats', '1']:
                stats = db.get_statistics()
                print("\n=== Database Statistics ===")
                print(f"Total huts: {stats['total_huts']}")
                print(f"With coordinates: {stats['with_coordinates']}")
                
                print("\nBy Type:")
                for item in stats['by_type']:
                    print(f"  {item['description']}: {item['count']}")
                
                print("\nBy Status:")
                for item in stats['by_status']:
                    print(f"  {item['description']}: {item['count']}")
                
                if stats['altitude']['min']:
                    print(f"\nAltitude range: {stats['altitude']['min']} - {stats['altitude']['max']} m")
                    print(f"Average altitude: {stats['altitude']['average']} m")
            
            elif command in ['all', '2']:
                huts = db.get_all_huts()
                print(f"\nFound {len(huts)} huts:")
                for i, hut in enumerate(huts[:20], 1):  # Show first 20
                    print(f"{i}. {hut['name']} ({hut.get('type_description', 'Unknown')})")
                if len(huts) > 20:
                    print(f"... and {len(huts) - 20} more")
            
            elif command in ['search', '3']:
                name = input("Enter search term: ").strip()
                huts = db.search_by_name(name)
                print(f"\nFound {len(huts)} huts:")
                for hut in huts:
                    db.print_hut(hut)
            
            elif command in ['type', '4']:
                print("\nTypes: 0=unidentified, 1=bivouac, 2=shelter, 3=hut/hotel")
                hut_type = int(input("Enter type: ").strip())
                huts = db.get_by_type(hut_type)
                print(f"\nFound {len(huts)} huts:")
                for hut in huts[:10]:  # Show first 10
                    print(f"- {hut['name']}")
                if len(huts) > 10:
                    print(f"... and {len(huts) - 10} more")
            
            elif command in ['location', '5']:
                lat = float(input("Enter latitude: ").strip())
                lon = float(input("Enter longitude: ").strip())
                radius = float(input("Enter radius in km (default 10): ").strip() or "10")
                huts = db.get_by_location(lat, lon, radius)
                print(f"\nFound {len(huts)} huts within {radius} km:")
                for hut in huts:
                    db.print_hut(hut)
            
            elif command in ['export-json', '6']:
                db.export_to_json()
            
            elif command in ['export-csv', '7']:
                db.export_to_csv()
            
            else:
                print("Unknown command")
        
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()
