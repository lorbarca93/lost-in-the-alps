"""
Base scraper class that all website scrapers should inherit from
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional
import requests
import logging
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import MountainHutsDatabase
from logger_config import setup_logger


class BaseScraper(ABC):
    """Abstract base class for all mountain hut scrapers"""
    
    def __init__(self, db_path: str = "data/mountain_huts.db"):
        self.db = MountainHutsDatabase(db_path)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        # Set up logger for this scraper
        self.logger = setup_logger(self.__class__.__name__)
    
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
        self.logger.info(f"Starting {self.source_name} scraper...")
        self.logger.info("=" * 60)
        
        # Initialize database and register source
        self.db.init_database()
        self.db.register_source(self.source_name, self.source_url, self.source_description)
        
        # Run the scraper
        try:
            huts = self.scrape()
        except Exception as e:
            self.logger.error(f"Error during scraping: {e}", exc_info=True)
            return
        
        if not huts:
            self.logger.warning(f"No huts found from {self.source_name}")
            return
        
        self.logger.info(f"Total huts scraped: {len(huts)}")
        
        # Save to database
        self.logger.info("Saving to database...")
        saved_count = self.db.save_huts_batch(huts, self.source_name)
        
        self.logger.info("=" * 60)
        self.logger.info(f"Scraping completed!")
        self.logger.info(f"Saved {saved_count} huts to database")
        self.logger.info(f"Source: {self.source_name}")
    
    def normalize_hut_data(self, hut: Dict) -> Dict:
        """
        Normalize hut data to common format
        Override this in subclasses if needed
        """
        return {
            'source_id': hut.get('id') or hut.get('source_id'),
            'name': hut.get('name', 'Unknown'),
            'hut_type': hut.get('hut_type') or hut.get('type'),
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
            'capacity_max': hut.get('capacity_max'),
            'phone': hut.get('phone', ''),
            'email': hut.get('email', ''),
            'website': hut.get('website', ''),
            'opening_hours': hut.get('opening_hours', ''),
            'image_url': hut.get('image_url', ''),
            'owner': hut.get('owner', ''),
            'manager': hut.get('manager', ''),
            'water_source': hut.get('water_source', ''),
            'access': hut.get('access', ''),
            'best_time_to_visit': hut.get('best_time_to_visit', ''),
            'comments': hut.get('comments', ''),
            'posted_by': hut.get('posted_by', ''),
            'posted_date': hut.get('posted_date', ''),
        }
