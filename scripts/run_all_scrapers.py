"""
Master script to run all scrapers
Usage: python run_all_scrapers.py [scraper_names...]
"""

import sys
import importlib
from pathlib import Path

# Add src and src/scrapers directories to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / 'src'))
sys.path.insert(0, str(project_root / 'src' / 'scrapers'))


def get_available_scrapers():
    """Find all scraper modules in the scrapers directory"""
    scrapers = []
    scrapers_dir = project_root / 'src' / 'scrapers'
    
    for file in scrapers_dir.glob('scraper_*.py'):
        if file.name == 'scraper_template.py':
            continue
        
        module_name = file.stem
        scrapers.append(module_name)
    
    return scrapers


def run_scraper(scraper_name: str):
    """Import and run a scraper module"""
    try:
        print(f"\n{'='*60}")
        print(f"Running {scraper_name}...")
        print(f"{'='*60}\n")
        
        # Import the scraper module
        # Try direct import first (if scrapers is a package)
        try:
            module = importlib.import_module(f'scrapers.{scraper_name}')
        except ImportError:
            # Fallback: import directly if scrapers dir is in path
            module = importlib.import_module(scraper_name)
        
        # Find the scraper class (should end with 'Scraper')
        scraper_class = None
        for name in dir(module):
            obj = getattr(module, name)
            if (isinstance(obj, type) and 
                name.endswith('Scraper') and 
                name != 'BaseScraper'):
                scraper_class = obj
                break
        
        if not scraper_class:
            print(f"Error: No scraper class found in {scraper_name}")
            return False
        
        # Create and run the scraper
        scraper = scraper_class()
        scraper.run()
        
        return True
        
    except Exception as e:
        print(f"Error running {scraper_name}: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main execution"""
    available_scrapers = get_available_scrapers()
    
    if not available_scrapers:
        print("No scrapers found!")
        print("Scrapers should be named 'scraper_*.py'")
        return
    
    print("Mountain Huts Multi-Scraper")
    print("="*60)
    print(f"Found {len(available_scrapers)} scraper(s):")
    for scraper in available_scrapers:
        print(f"  - {scraper}")
    print()
    
    # Determine which scrapers to run
    if len(sys.argv) > 1:
        # Run specified scrapers
        scrapers_to_run = []
        for arg in sys.argv[1:]:
            if not arg.startswith('scraper_'):
                arg = f'scraper_{arg}'
            if arg.endswith('.py'):
                arg = arg[:-3]
            
            if arg in available_scrapers:
                scrapers_to_run.append(arg)
            else:
                print(f"Warning: Scraper '{arg}' not found")
        
        if not scrapers_to_run:
            print("No valid scrapers specified")
            return
    else:
        # Run all scrapers
        scrapers_to_run = available_scrapers
    
    print(f"Running {len(scrapers_to_run)} scraper(s)...\n")
    
    # Run each scraper
    results = {}
    for scraper_name in scrapers_to_run:
        success = run_scraper(scraper_name)
        results[scraper_name] = success
    
    # Summary
    print("\n" + "="*60)
    print("SCRAPING SUMMARY")
    print("="*60)
    
    successful = sum(1 for v in results.values() if v)
    failed = len(results) - successful
    
    print(f"\nTotal scrapers run: {len(results)}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    
    if failed > 0:
        print("\nFailed scrapers:")
        for name, success in results.items():
            if not success:
                print(f"  - {name}")
    
    # Show database statistics
    print("\n" + "="*60)
    print("DATABASE STATISTICS")
    print("="*60)
    
    try:
        from src.database import MountainHutsDatabase
        db = MountainHutsDatabase()
        stats = db.get_statistics()
        
        print(f"\nTotal huts in database: {stats['total_huts']}")
        print(f"Huts with coordinates: {stats['with_coordinates']}")
        
        if stats.get('by_source'):
            print("\nBy Source:")
            for source in stats['by_source']:
                print(f"  {source['source']}: {source['count']} huts")
        
        if stats.get('by_country'):
            print("\nBy Country:")
            for country in stats['by_country'][:10]:  # Top 10
                print(f"  {country['country']}: {country['count']} huts")
        
        if stats.get('sources'):
            print("\nSource Information:")
            for source in stats['sources']:
                print(f"  {source['name']}")
                print(f"    URL: {source['url']}")
                print(f"    Last scraped: {source['last_scraped'] or 'Never'}")
                print(f"    Total huts: {source['total_huts']}")
    
    except Exception as e:
        print(f"Error getting statistics: {e}")


if __name__ == "__main__":
    main()
