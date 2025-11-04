"""
Timed Refuges.info Scraper
Runs the refuges.info scraper for a specified duration
"""
import sys
import os
import time
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scrapers.scraper_refuges_info_pages import RefugesInfoPageScraper
from database import MountainHutsDatabase

class TimedRefugesScraper:
    def __init__(self, duration_minutes=90):
        """
        Initialize timed scraper
        
        Args:
            duration_minutes: How long to run the scraper (default: 90 minutes = 1.5 hours)
        """
        self.duration_minutes = duration_minutes
        self.start_time = None
        self.end_time = None
        self.scraper = RefugesInfoPageScraper()
        
    def should_continue(self):
        """Check if we should continue scraping based on time"""
        if not self.start_time or not self.end_time:
            return True
        
        elapsed = datetime.now() - self.start_time
        remaining = self.end_time - datetime.now()
        
        if remaining.total_seconds() <= 0:
            return False
        
        return True
    
    def get_time_info(self):
        """Get formatted time information"""
        if not self.start_time:
            return "Not started"
        
        elapsed = datetime.now() - self.start_time
        remaining = self.end_time - datetime.now()
        
        elapsed_str = str(elapsed).split('.')[0]  # Remove microseconds
        remaining_str = str(remaining).split('.')[0] if remaining.total_seconds() > 0 else "0:00:00"
        
        return f"Elapsed: {elapsed_str} | Remaining: {remaining_str}"
    
    def run(self, include_gite=False):
        """
        Run the scraper for the specified duration
        
        Args:
            include_gite: Whether to include guesthouses (gîtes d'étape)
        """
        print("=" * 70)
        print("TIMED REFUGES.INFO SCRAPER")
        print("=" * 70)
        print(f"Duration: {self.duration_minutes} minutes ({self.duration_minutes/60:.1f} hours)")
        print()
        
        # Set time limits
        self.start_time = datetime.now()
        self.end_time = self.start_time + timedelta(minutes=self.duration_minutes)
        
        print(f"[*] Start time: {self.start_time.strftime('%H:%M:%S')}")
        print(f"[*] End time: {self.end_time.strftime('%H:%M:%S')}")
        print()
        
        # Initialize database
        db = self.scraper.db
        db.init_database()
        db.register_source('refuges.info', self.scraper.base_url, 
                          'French Alpine refuges and mountain huts database')
        
        # Determine which types to include
        include_types = ['cabane', 'refuge', 'bivouac']
        if include_gite:
            include_types.append('gite')
        
        # Get ALL refuge IDs
        print("[*] Fetching refuge IDs from API...")
        refuge_ids = self.scraper.get_all_refuge_ids(include_types)
        
        if not refuge_ids:
            print("[ERROR] No refuges to scrape")
            return
        
        print(f"\n[*] Found {len(refuge_ids)} total refuges available")
        print(f"[*] Will scrape as many as possible in {self.duration_minutes} minutes")
        print(f"[*] Estimated: ~{int(self.duration_minutes * 60 / 1.2)} refuges\n")
        
        successful = 0
        failed = 0
        skipped = 0
        
        for i, refuge_id in enumerate(refuge_ids, 1):
            # Check time limit before each scrape
            if not self.should_continue():
                print(f"\n[!] Time limit reached after {i-1} refuges")
                print(f"[!] Stopping gracefully...")
                break
            
            try:
                # Progress indicator every 10 huts
                if i % 10 == 0 or i == 1:
                    time_info = self.get_time_info()
                    print(f"\n[Progress: {i}/{len(refuge_ids)}] ({successful} saved, {failed} failed, {skipped} skipped)")
                    print(f"[Time: {time_info}]")
                
                hut_data = self.scraper.scrape_refuge_page(refuge_id)
                
                if hut_data:
                    # Double-check it's not a cave or water point
                    hut_type = hut_data.get('type', '').lower() if hut_data.get('type') else ''
                    if 'grotte' in hut_type or 'cave' in hut_type:
                        skipped += 1
                        continue
                    if 'point d' in hut_type or 'water' in hut_type or 'eau' in hut_type:
                        skipped += 1
                        continue
                    
                    db.save_hut(hut_data, 'refuges.info')
                    successful += 1
                    
                    if i % 10 == 0:  # Show name every 10 huts
                        try:
                            print(f"  [OK] {hut_data.get('name', 'Unknown')[:40]}")
                        except:
                            print(f"  [OK] Refuge {refuge_id}")
                else:
                    failed += 1
                
                # Be polite - add delay between requests
                time.sleep(1)
                
                # Commit to database every 50 huts
                if i % 50 == 0:
                    db.update_source_stats('refuges.info')
                    print(f"  [COMMIT] Saved batch to database")
                
            except KeyboardInterrupt:
                print(f"\n[!] Interrupted by user after {i} refuges")
                print(f"[!] Saving progress...")
                break
            except Exception as e:
                failed += 1
                if i % 10 == 0:
                    print(f"  [ERROR] Refuge {refuge_id}: {str(e)[:50]}")
                continue
        
        # Final commit
        db.update_source_stats('refuges.info')
        
        # Calculate actual runtime
        actual_duration = datetime.now() - self.start_time
        
        print("\n" + "=" * 70)
        print("SCRAPING SUMMARY")
        print("=" * 70)
        print(f"[TIME] Started: {self.start_time.strftime('%H:%M:%S')}")
        print(f"[TIME] Finished: {datetime.now().strftime('%H:%M:%S')}")
        print(f"[TIME] Duration: {str(actual_duration).split('.')[0]}")
        print()
        print(f"[OK] Successfully scraped: {successful}")
        print(f"[ERROR] Failed: {failed}")
        print(f"[SKIP] Skipped (caves/water): {skipped}")
        print(f"[*] Total processed: {successful + failed + skipped}")
        print()
        
        # Show database stats
        try:
            stats = db.get_statistics()
            print(f"[DATABASE] Total huts in database: {stats['total_huts']}")
            
            if stats.get('by_source'):
                for source in stats['by_source']:
                    if source['source'] == 'refuges.info':
                        print(f"[DATABASE] Refuges.info entries: {source['count']}")
                        break
        except Exception as e:
            print(f"[!] Could not get database stats: {e}")
        
        print("\n[OK] Timed scraping complete!")
        print(f"[*] You can resume later - the scraper will continue from where it left off")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Run refuges.info scraper for a specified duration')
    parser.add_argument('--minutes', type=int, default=90, 
                       help='Duration to run in minutes (default: 90 = 1.5 hours)')
    parser.add_argument('--hours', type=float, 
                       help='Duration to run in hours (overrides --minutes)')
    parser.add_argument('--include-gite', action='store_true',
                       help='Include guesthouses (gîtes d\'étape)')
    
    args = parser.parse_args()
    
    # Convert hours to minutes if specified
    duration = int(args.hours * 60) if args.hours else args.minutes
    
    print(f"\n[*] Will run scraper for {duration} minutes ({duration/60:.1f} hours)")
    
    scraper = TimedRefugesScraper(duration_minutes=duration)
    scraper.run(include_gite=args.include_gite)

