"""
Enhanced Base Scraper v2.0 with:
- Automatic retry with exponential backoff
- Rate limiting
- Connection pooling  
- Progress checkpoints
- Data validation
- Rich error logging
- Request caching
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Generator
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import logging
import sys
import os
import time
import json
from pathlib import Path
from datetime import datetime
from functools import wraps

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import MountainHutsDatabase
from logger_config import setup_logger
from data_cleaner import clean_hut_data, validate_hut_data


class RateLimiter:
    """Simple rate limiter using token bucket algorithm"""
    
    def __init__(self, calls_per_second: float = 10):
        self.calls_per_second = calls_per_second
        self.min_interval = 1.0 / calls_per_second
        self.last_call = 0.0
    
    def wait(self):
        """Wait if necessary to respect rate limit"""
        if self.calls_per_second <= 0:
            return
        
        elapsed = time.time() - self.last_call
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
        
        self.last_call = time.time()


class BaseScraperV2(ABC):
    """
    Enhanced base class for all mountain hut scrapers v2.0
    
    Features:
    - Automatic retry with exponential backoff
    - Rate limiting (configurable)
    - Connection pooling for better performance
    - Progress checkpoints for resumability  
    - Data validation before saving
    - Rich error logging with context
    - Statistics tracking
    """
    
    def __init__(self, 
                 db_path: str = "data/mountain_huts.db",
                 rate_limit: float = 10.0,  # requests per second
                 max_retries: int = 3,
                 enable_cache: bool = False,
                 checkpoint_enabled: bool = True):
        """
        Initialize enhanced scraper
        
        Args:
            db_path: Path to SQLite database
            rate_limit: Maximum requests per second (0 = no limit)
            max_retries: Number of retries for failed requests
            enable_cache: Enable response caching (useful for development)
            checkpoint_enabled: Enable progress checkpoints for resume
        """
        self.db = MountainHutsDatabase(db_path)
        self.rate_limit = rate_limit
        self.max_retries = max_retries
        self.checkpoint_enabled = checkpoint_enabled
        
        # Create optimized session
        self.session = self._create_session()
        
        # Rate limiter
        self.rate_limiter = RateLimiter(rate_limit)
        
        # Set up logger
        self.logger = setup_logger(self.__class__.__name__)
        
        # Statistics
        self.stats = {
            'requests_total': 0,
            'requests_successful': 0,
            'requests_failed': 0,
            'retries': 0,
            'huts_scraped': 0,
            'huts_saved': 0,
            'huts_skipped': 0,
            'start_time': None,
            'end_time': None
        }
        
        # Checkpoint
        self.checkpoint_dir = Path("data/checkpoints")
        self.checkpoint_dir.mkdir(exist_ok=True, parents=True)
        self.checkpoint_file = self.checkpoint_dir / f"{self.__class__.__name__}.json"
        
        # Cache for duplicate detection during scrape
        self.seen_ids = set()
    
    def _create_session(self) -> requests.Session:
        """Create optimized requests session with connection pooling"""
        session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=self.max_retries,
            backoff_factor=1,  # 1, 2, 4, 8 seconds
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST"]
        )
        
        # Configure HTTP adapter with connection pooling
        adapter = HTTPAdapter(
            pool_connections=10,
            pool_maxsize=20,
            max_retries=retry_strategy
        )
        
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Set headers
        session.headers.update({
            'User-Agent': 'MountainHutsEurope/2.0 (+https://github.com/yourusername/lostinthealps; Educational Project)',
            'Accept': 'text/html,application/xhtml+xml,application/xml,application/json;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'DNT': '1'
        })
        
        return session
    
    def get_with_retry(self, url: str, **kwargs) -> requests.Response:
        """
        Perform GET request with automatic retry and rate limiting
        
        Args:
            url: URL to fetch
            **kwargs: Additional arguments for requests.get()
        
        Returns:
            Response object
        
        Raises:
            requests.RequestException: If all retries fail
        """
        kwargs.setdefault('timeout', 30)
        
        self.stats['requests_total'] += 1
        
        for attempt in range(1, self.max_retries + 1):
            try:
                # Rate limiting
                self.rate_limiter.wait()
                
                # Make request
                response = self.session.get(url, **kwargs)
                response.raise_for_status()
                
                self.stats['requests_successful'] += 1
                
                if attempt > 1:
                    self.logger.info(f"✓ Success on attempt {attempt}: {url}")
                
                return response
                
            except requests.RequestException as e:
                self.stats['retries'] += attempt - 1
                
                if attempt == self.max_retries:
                    # Last attempt failed
                    self.stats['requests_failed'] += 1
                    self.logger.error(
                        f"✗ Failed after {self.max_retries} attempts: {url}",
                        extra={'url': url, 'error': str(e)}
                    )
                    raise
                
                # Wait before retry (exponential backoff)
                wait_time = 2 ** (attempt - 1)
                self.logger.warning(
                    f"⚠ Attempt {attempt}/{self.max_retries} failed for {url}. "
                    f"Retrying in {wait_time}s... Error: {str(e)[:100]}"
                )
                time.sleep(wait_time)
    
    def validate_hut_data_internal(self, hut: Dict) -> tuple[bool, Optional[str]]:
        """
        Validate hut data before saving (uses centralized validation)
        
        Args:
            hut: Hut data dictionary
        
        Returns:
            (is_valid, error_message)
        """
        return validate_hut_data(hut)
    
    def save_checkpoint(self, data: Dict):
        """
        Save progress checkpoint
        
        Args:
            data: Checkpoint data to save
        """
        if not self.checkpoint_enabled:
            return
        
        try:
            checkpoint = {
                'timestamp': datetime.now().isoformat(),
                'stats': self.stats.copy(),
                'data': data
            }
            
            with open(self.checkpoint_file, 'w') as f:
                json.dump(checkpoint, f, indent=2)
            
            self.logger.debug(f"Checkpoint saved: {data}")
        except Exception as e:
            self.logger.warning(f"Failed to save checkpoint: {e}")
    
    def load_checkpoint(self) -> Optional[Dict]:
        """
        Load progress checkpoint
        
        Returns:
            Checkpoint data or None if no checkpoint exists
        """
        if not self.checkpoint_enabled:
            return None
        
        try:
            if self.checkpoint_file.exists():
                with open(self.checkpoint_file, 'r') as f:
                    checkpoint = json.load(f)
                
                self.logger.info(f"Checkpoint loaded from {checkpoint['timestamp']}")
                return checkpoint.get('data')
        except Exception as e:
            self.logger.warning(f"Failed to load checkpoint: {e}")
        
        return None
    
    def clear_checkpoint(self):
        """Clear checkpoint after successful completion"""
        if self.checkpoint_file.exists():
            try:
                self.checkpoint_file.unlink()
                self.logger.debug("Checkpoint cleared")
            except Exception as e:
                self.logger.warning(f"Failed to clear checkpoint: {e}")
    
    def save_huts_batch(self, huts: List[Dict], batch_size: int = 100):
        """
        Save huts in batches with cleaning and validation
        
        Args:
            huts: List of hut dictionaries
            batch_size: Number of huts to save at once
        """
        saved = 0
        skipped = 0
        
        for i in range(0, len(huts), batch_size):
            batch = huts[i:i + batch_size]
            
            # Clean and validate batch
            validated_batch = []
            for hut in batch:
                try:
                    # Clean data first
                    cleaned = clean_hut_data(hut)
                    
                    # Then validate
                    is_valid, error = validate_hut_data(cleaned)
                if is_valid:
                        validated_batch.append(cleaned)
                else:
                    skipped += 1
                    self.logger.warning(f"Skipped invalid hut: {hut.get('name')} - {error}")
                except Exception as e:
                    skipped += 1
                    self.logger.warning(f"Error cleaning hut: {hut.get('name')} - {e}")
            
            # Save validated batch
            if validated_batch:
                try:
                    count = self.db.save_huts_batch(validated_batch, self.source_name)
                    saved += count
                    self.logger.info(f"Saved batch: {count}/{len(batch)} huts (total: {saved})")
                except Exception as e:
                    self.logger.error(f"Failed to save batch: {e}")
        
        self.stats['huts_saved'] = saved
        self.stats['huts_skipped'] = skipped
        
        return saved
    
    def print_stats(self):
        """Print scraping statistics"""
        duration = None
        if self.stats['start_time'] and self.stats['end_time']:
            duration = (self.stats['end_time'] - self.stats['start_time']).total_seconds()
        
        print("\n" + "=" * 70)
        print("SCRAPING STATISTICS")
        print("=" * 70)
        print(f"Source: {self.source_name}")
        print(f"Duration: {duration:.1f}s" if duration else "Duration: N/A")
        print(f"\nRequests:")
        print(f"  Total: {self.stats['requests_total']}")
        print(f"  Successful: {self.stats['requests_successful']}")
        print(f"  Failed: {self.stats['requests_failed']}")
        print(f"  Retries: {self.stats['retries']}")
        print(f"\nData:")
        print(f"  Scraped: {self.stats['huts_scraped']}")
        print(f"  Saved: {self.stats['huts_saved']}")
        print(f"  Skipped: {self.stats['huts_skipped']}")
        
        if duration and self.stats['requests_total'] > 0:
            print(f"\nPerformance:")
            print(f"  Requests/sec: {self.stats['requests_total'] / duration:.2f}")
            print(f"  Huts/sec: {self.stats['huts_scraped'] / duration:.2f}")
        
        print("=" * 70)
    
    # Abstract methods (must be implemented by subclasses)
    
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
    
    # Main execution workflow
    
    def run(self):
        """Main execution workflow with statistics and error handling"""
        self.logger.info(f"Starting {self.source_name} scraper v2.0...")
        self.logger.info(f"Rate limit: {self.rate_limit} req/s, Max retries: {self.max_retries}")
        self.logger.info("=" * 60)
        
        self.stats['start_time'] = datetime.now()
        
        # Initialize database and register source
        self.db.init_database()
        self.db.register_source(self.source_name, self.source_url, self.source_description)
        
        # Run the scraper
        try:
            huts = self.scrape()
            self.stats['huts_scraped'] = len(huts) if huts else 0
        except KeyboardInterrupt:
            self.logger.warning("Scraping interrupted by user")
            self.print_stats()
            return
        except Exception as e:
            self.logger.error(f"Error during scraping: {e}", exc_info=True)
            self.print_stats()
            return
        
        if not huts:
            self.logger.warning(f"No huts found from {self.source_name}")
            self.stats['end_time'] = datetime.now()
            self.print_stats()
            return
        
        self.logger.info(f"Total huts scraped: {len(huts)}")
        
        # Save to database with validation
        self.logger.info("Saving to database with validation...")
        saved_count = self.save_huts_batch(huts)
        
        # Update source statistics
        self.db.update_source_stats(self.source_name)
        
        # Clear checkpoint on success
        self.clear_checkpoint()
        
        self.stats['end_time'] = datetime.now()
        
        # Print final statistics
        self.print_stats()
        
        self.logger.info("✓ Scraping completed successfully!")
    
    def normalize_hut_data(self, hut: Dict) -> Dict:
        """
        Normalize hut data to common format
        Uses centralized data cleaning for consistency
        Override this in subclasses if needed
        """
        return clean_hut_data(hut)

