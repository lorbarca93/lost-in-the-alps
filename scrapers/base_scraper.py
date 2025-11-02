"""
Base scraper class that all website scrapers should inherit from
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional
import requests
from database import MountainHutsDatabase


class BaseScraper(ABC):
    """Abstract base class for all mountain hut scrapers"""
    
    def __init__(self, db_path: str = "data/mountain_huts.db"):
        self.db = MountainHutsDatabase(db_path)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    @property
    @abstractmethod
    def source_name(self) -> str:
        """Name of the source website"""
        pass
    
    @property
    @abstractmethod
    def source_url(self) -> str:
        """Base URL of the source website"""
        pass
    
    @property
    @abstractmethod
    def source_description(self) -> str:
        """Description of the source"""
        pass
    
    @abstractmethod
    def scrape(self) -> List[Dict]:
        """
        Main scraping method - must be implemented by each scraper
        Should return a list of hut dictionaries
        """
        pass
    
    def run(self):
        """Main execution workflow"""
        print(f"Starting {self.source_name} scraper...")
        print("=" * 60)
        
        # Initialize database and register source
        self.db.init_database()
        self.db.register_source(self.source_name, self.source_url, self.source_description)
        
        # Run the scraper
        huts = self.scrape()
        
        if not huts:
            print(f"No huts found from {self.source_name}")
            return
        
        print(f"\nTotal huts scraped: {len(huts)}")
        
        # Save to database
        print("Saving to database...")
        saved_count = self.db.save_huts_batch(huts, self.source_name)
        
        print("\n" + "=" * 60)
        print(f"Scraping completed!")
        print(f"Saved {saved_count} huts to database")
        print(f"Source: {self.source_name}")
    
    def normalize_hut_data(self, hut: Dict) -> Dict:
        """
        Normalize hut data to common format
        Override this in subclasses if needed
        """
        return {
            'source_id': hut.get('id') or hut.get('source_id'),
            'name': hut.get('name', 'Unknown'),
            'type': hut.get('type'),
            'type_description': hut.get('type_description'),
            'status': hut.get('status'),
            'status_description': hut.get('status_description'),
            'latitude': hut.get('latitude'),
            'longitude': hut.get('longitude'),
            'altitude': hut.get('altitude'),
            'description': hut.get('description', ''),
            'url': hut.get('url', ''),
            'country': hut.get('country', ''),
            'region': hut.get('region', ''),
            'amenities': hut.get('amenities', ''),
            'capacity': hut.get('capacity'),
            'phone': hut.get('phone', ''),
            'email': hut.get('email', ''),
            'website': hut.get('website', ''),
            'opening_hours': hut.get('opening_hours', ''),
            'image_url': hut.get('image_url', ''),
        }
