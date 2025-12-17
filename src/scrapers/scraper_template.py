"""
Example template for creating a new scraper
Copy this file and modify for your target website
"""

from base_scraper import BaseScraper
from typing import List, Dict
import time


class ExampleScraper(BaseScraper):
    """Template scraper for [WEBSITE NAME]"""
    
    @property
    def source_name(self) -> str:
        return "example.com"  # Change this to your website
    
    @property
    def source_url(self) -> str:
        return "https://example.com"  # Change this to the base URL
    
    @property
    def source_description(self) -> str:
        return "Example mountain huts database"  # Describe the website
    
    def scrape(self) -> List[Dict]:
        """
        Main scraping logic - implement your scraping here
        
        This method should:
        1. Fetch data from the website (HTML, API, etc.)
        2. Parse the data
        3. Convert to the standard format
        4. Return a list of hut dictionaries
        """
        
        print("Starting to scrape example.com...")
        all_huts = []
        
        # EXAMPLE: Scrape a list page
        try:
            response = self.session.get(f"{self.source_url}/huts")
            response.raise_for_status()
            
            # TODO: Parse the response
            # from bs4 import BeautifulSoup
            # soup = BeautifulSoup(response.text, 'html.parser')
            
            # EXAMPLE: Extract hut data
            # huts_data = soup.find_all('div', class_='hut-item')
            # for hut_element in huts_data:
            #     hut = self.parse_hut(hut_element)
            #     if hut:
            #         all_huts.append(hut)
            
            # For now, return empty list
            pass
            
        except Exception as e:
            print(f"Error scraping: {e}")
        
        return all_huts
    
    def parse_hut(self, element) -> Dict:
        """
        Parse a single hut element/data
        
        Return a dictionary with these fields (all optional except source_id and name):
        - source_id: Unique ID from the source website (required)
        - name: Name of the hut (required)
        - latitude: GPS latitude
        - longitude: GPS longitude
        - altitude: Elevation in meters
        - description: Text description
        - url: Direct link to hut page
        - country: Country code or name
        - region: Region/area name
        - type: Numeric type code
        - type_description: Human-readable type
        - amenities: Comma-separated list of amenities
        - capacity: Number of beds/people
        - phone: Contact phone
        - email: Contact email
        - website: Official website
        - opening_hours: Opening hours/season
        - image_url: URL to main image
        """
        
        hut = {
            'source_id': 'example_id',  # TODO: Extract from element
            'name': 'Example Hut',      # TODO: Extract from element
            'latitude': 46.5,            # TODO: Extract from element
            'longitude': 11.5,           # TODO: Extract from element
            'altitude': 2000,            # TODO: Extract from element
            'country': 'Austria',        # TODO: Extract from element
            'url': 'https://example.com/hut/123',  # TODO: Build URL
        }
        
        # Normalize the data using the base class method
        return self.normalize_hut_data(hut)


# Example usage:
if __name__ == "__main__":
    scraper = ExampleScraper()
    scraper.run()
