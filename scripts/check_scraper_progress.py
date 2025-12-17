"""
Quick progress checker for refuges.info scraping
Shows current database statistics
"""
import sys
import os

# Add src directory to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(project_root, 'src'))

from database import MountainHutsDatabase

def main():
    print("=" * 70)
    print("REFUGES.INFO SCRAPER - PROGRESS CHECK")
    print("=" * 70)
    print()
    
    try:
        db = MountainHutsDatabase()
        stats = db.get_statistics()
        
        print(f"Total huts in database: {stats['total_huts']}")
        print(f"Huts with coordinates: {stats['with_coordinates']}")
        print()
        
        if stats.get('by_source'):
            print("By Source:")
            for source in stats['by_source']:
                print(f"  {source['source']}: {source['count']} huts")
            print()
        
        if stats.get('by_country'):
            print("Top Countries:")
            for country in stats['by_country'][:10]:
                print(f"  {country['country']}: {country['count']} huts")
            print()
        
        if stats.get('sources'):
            print("Source Details:")
            for source in stats['sources']:
                if source['name'] == 'refuges.info':
                    print(f"  Refuges.info:")
                    print(f"    Last scraped: {source['last_scraped'] or 'Never'}")
                    print(f"    Total huts: {source['total_huts']}")
                    print()
        
        print("=" * 70)
        
    except Exception as e:
        print(f"Error getting statistics: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

