"""
Base scraper class that all website scrapers should inherit from
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Tuple
import requests
import logging
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import MountainHutsDatabase
from logger_config import setup_logger
from data_cleaner import clean_hut_data, validate_hut_data


class BaseScraper(ABC):
    """Abstract base class for all mountain hut scrapers"""
    
    def __init__(self, db_path: str = "data/mountain_huts.db"):
        self.db = MountainHutsDatabase(db_path)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'MountainHutsExplorer/2.0 (Educational Project; +https://github.com/lostinthealps)',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
        })
        # Set up logger for this scraper
        self.logger = setup_logger(self.__class__.__name__)
        
        # Statistics
        self.stats = {
            'scraped': 0,
            'saved': 0,
            'skipped': 0,
            'errors': 0
        }
    
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
            self.stats['scraped'] = len(huts) if huts else 0
        except Exception as e:
            self.logger.error(f"Error during scraping: {e}", exc_info=True)
            return
        
        if not huts:
            self.logger.warning(f"No huts found from {self.source_name}")
            return
        
        self.logger.info(f"Total huts scraped: {len(huts)}")
        
        # Clean and validate data
        self.logger.info("Cleaning and validating data...")
        cleaned_huts = []
        for hut in huts:
            try:
                cleaned = clean_hut_data(hut)
                is_valid, error = validate_hut_data(cleaned)
                if is_valid:
                    cleaned_huts.append(cleaned)
                else:
                    self.stats['skipped'] += 1
                    self.logger.debug(f"Skipped invalid hut: {hut.get('name', 'Unknown')} - {error}")
            except Exception as e:
                self.stats['errors'] += 1
                self.logger.warning(f"Error cleaning hut data: {e}")
        
        self.logger.info(f"Valid huts after cleaning: {len(cleaned_huts)}/{len(huts)}")
        
        # Save to database
        self.logger.info("Saving to database...")
        saved_count = self.db.save_huts_batch(cleaned_huts, self.source_name)
        self.stats['saved'] = saved_count
        
        self.logger.info("=" * 60)
        self.logger.info(f"Scraping completed!")
        self.logger.info(f"  Scraped: {self.stats['scraped']}")
        self.logger.info(f"  Saved: {self.stats['saved']}")
        self.logger.info(f"  Skipped: {self.stats['skipped']}")
        self.logger.info(f"  Errors: {self.stats['errors']}")
        self.logger.info(f"Source: {self.source_name}")
    
    def normalize_hut_data(self, hut: Dict) -> Dict:
        """
        Normalize hut data to common format
        Uses centralized data cleaning for consistency
        Override this in subclasses if needed
        """
        # Use centralized data cleaner
        return clean_hut_data(hut)
