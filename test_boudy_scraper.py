"""
Test the enhanced boudy.info scraper on a single hut
"""
import sys
sys.path.append('scrapers')

from scraper_boudy_info import BoudyInfoScraper

# Create scraper instance
scraper = BoudyInfoScraper()

# Test with the hut from the screenshot: Sobes (ID would need to be found)
# Let's get a few huts from the AJAX endpoint first
print("Testing enhanced boudy.info scraper...")
print("=" * 80)

# Get a small region to test
huts = scraper.scrape_ajax_data(48.8, 15.8, 49.0, 16.0)

if huts:
    print(f"\nFound {len(huts)} huts in test region")
    print("Testing detail scraping on first hut...\n")
    
    test_hut = huts[0]
    print(f"Hut: {test_hut.get('name')}")
    print(f"ID: {test_hut.get('source_id')}")
    print(f"Coordinates: {test_hut.get('latitude')}, {test_hut.get('longitude')}")
    print(f"URL: {test_hut.get('url')}")
    
    # Scrape details
    hut_id = test_hut.get('source_id')
    if hut_id:
        print(f"\nScraping details from {test_hut.get('url')}...")
        details = scraper.scrape_hut_details(hut_id)
        
        print("\n" + "=" * 80)
        print("EXTRACTED DETAILS:")
        print("=" * 80)
        for key, value in details.items():
            print(f"{key:25} : {value}")
        
        if not details:
            print("No additional details found (page might have different structure)")
else:
    print("No huts found in test region")
