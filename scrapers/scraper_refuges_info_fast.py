"""
Refuges.info FAST Parallel Scraper
Uses asyncio + aiohttp for concurrent requests
Speed: 10-20x faster than sequential scraper
"""
import asyncio
import aiohttp
from bs4 import BeautifulSoup
import time
import random
import re
import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import MountainHutsDatabase

class RefugesInfoFastScraper:
    def __init__(self, max_concurrent=20):
        """
        Fast parallel scraper for refuges.info
        
        Args:
            max_concurrent: Number of concurrent requests (default: 20)
        """
        self.base_url = "https://www.refuges.info"
        self.api_url = "https://www.refuges.info/api/bbox"
        self.db = MountainHutsDatabase()
        self.max_concurrent = max_concurrent
        self.semaphore = None  # Will be created in async context
        
        # Stats
        self.successful = 0
        self.failed = 0
        self.skipped = 0
        
        # Translation dictionary
        self.translations = {
            'cabane non gardée': 'Unmanned hut',
            'refuge gardé': 'Managed hut',
            "gîte d'étape": 'Guesthouse',
            'grotte': 'Cave shelter',
            'bivouac': 'Bivouac shelter',
            'matelas': 'mattresses',
            'poêle': 'stove',
            'cheminée': 'fireplace',
            'couvertures': 'blankets',
            'eau': 'water',
            'bois': 'wood',
            'latrines': 'latrines',
            'Oui': 'Yes',
            'Non': 'No',
        }
    
    def translate_text(self, text):
        """Translate French text to English"""
        if not text:
            return text
        
        translated = text
        for fr, en in self.translations.items():
            translated = re.sub(r'\b' + re.escape(fr) + r'\b', en, translated, flags=re.IGNORECASE)
        
        return translated
    
    def get_all_refuge_ids(self):
        """Get ALL refuge IDs from the API (synchronous)"""
        import requests
        
        print(f"\n[*] Fetching ALL refuge IDs from refuges.info API...")
        
        all_refuges = []
        include_types = ['cabane', 'refuge', 'bivouac']
        
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'MountainHutsEurope/1.0 (Educational Project)'
        })
        
        for point_type in include_types:
            print(f"  [*] Fetching {point_type}...")
            
            params = {
                'bbox': 'world',
                'type_points': point_type,
                'nb_points': '10000',
                'format': 'geojson',
                'detail': 'simple'
            }
            
            try:
                response = session.get(self.api_url, params=params, timeout=60)
                response.raise_for_status()
                data = response.json()
                
                features = data.get('features', [])
                
                for feature in features:
                    props = feature['properties']
                    refuge_id = props.get('id')
                    type_info = props.get('type', {})
                    type_val = type_info.get('valeur', 'Unknown')
                    
                    # Filter out unwanted types
                    if 'grotte' in type_val.lower() or 'point d' in type_val.lower() or 'eau' in type_val.lower():
                        continue
                    
                    if refuge_id:
                        all_refuges.append(refuge_id)
                
                print(f"    [OK] Found {len(features)} {point_type} points")
                
            except Exception as e:
                print(f"    [ERROR] Error fetching {point_type}: {e}")
                continue
        
        # Remove duplicates
        unique_ids = list(set(all_refuges))
        
        print(f"\n[OK] Total unique refuges: {len(unique_ids)}")
        
        return unique_ids
    
    async def scrape_refuge_async(self, session, refuge_id):
        """Scrape a single refuge (async)"""
        async with self.semaphore:  # Limit concurrent requests
            api_url = f"https://www.refuges.info/api/point"
            
            try:
                # Get API data
                params = {'id': refuge_id, 'format': 'geojson', 'detail': 'complet'}
                
                async with session.get(api_url, params=params, timeout=30) as response:
                    if response.status != 200:
                        return None
                    
                    data = await response.json()
                    
                    if not data or 'features' not in data or not data['features']:
                        return None
                    
                    feature = data['features'][0]
                    props = feature['properties']
                    geom = feature['geometry']
                    
                    # Get page URL
                    page_url = props.get('lien')
                    if not page_url:
                        return None
                    
                    # Get coordinates
                    coords = geom.get('coordinates', [0, 0])
                    longitude = coords[0]
                    latitude = coords[1]
                    
                    # Extract data from API
                    name = props.get('nom', 'Unknown')
                    hut_type_info = props.get('type', {})
                    hut_type = hut_type_info.get('valeur', 'Unknown')
                    
                    # Map French types to standard types
                    if 'cabane' in hut_type.lower() or 'abri' in hut_type.lower():
                        hut_type_std = 'Unmanned cabin'
                    elif 'refuge' in hut_type.lower() and 'gardé' in hut_type.lower():
                        hut_type_std = 'Mountain Hut'
                    elif 'bivouac' in hut_type.lower():
                        hut_type_std = 'Bivouac'
                    elif 'gîte' in hut_type.lower():
                        hut_type_std = 'Guesthouse'
                    else:
                        hut_type_std = 'Unmanned cabin'
                    
                    # Get altitude
                    altitude = props.get('coord', {}).get('alt', 0)
                    
                    # Now scrape the page for additional details
                    async with session.get(page_url, timeout=30) as page_response:
                        if page_response.status != 200:
                            # Save what we have from API
                            return self.create_hut_data(
                                name, latitude, longitude, altitude, hut_type_std,
                                page_url, '', '', '', '', '', '', '', '', '', '', '', '', '', refuge_id
                            )
                        
                        html = await page_response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # Extract additional data from page
                        phone = ''
                        email = ''
                        website = ''
                        capacity = ''
                        capacity_max = ''
                        opening_hours = ''
                        description = ''
                        manager = ''
                        owner = ''
                        access = ''
                        comments = ''
                        water_source = ''
                        best_time = ''
                        posted_by = ''
                        
                        # Extract capacity
                        capacity_section = soup.find(string=re.compile(r'Places\s*prévues\s*pour\s*dormir', re.I))
                        if capacity_section:
                            capacity_val = capacity_section.find_next('td')
                            if capacity_val:
                                capacity_text = capacity_val.get_text(strip=True)
                                capacity = re.search(r'\d+', capacity_text)
                                if capacity:
                                    capacity = capacity.group()
                        
                        # Extract phone
                        phone_link = soup.find('a', href=re.compile(r'^tel:'))
                        if phone_link:
                            phone = phone_link.get_text(strip=True)
                        
                        # Extract email
                        email_link = soup.find('a', href=re.compile(r'^mailto:'))
                        if email_link:
                            email = email_link['href'].replace('mailto:', '')
                        
                        # Extract website
                        site_label = soup.find(string=re.compile(r'Site\s+officiel', re.I))
                        if site_label:
                            site_link = site_label.find_next('a')
                            if site_link and site_link.get('href'):
                                website = site_link['href']
                        
                        # Extract description/remarks
                        remarks_section = soup.find(string=re.compile(r'Remarques', re.I))
                        if remarks_section:
                            remarks_content = remarks_section.find_next('div', class_='info')
                            if remarks_content:
                                comments = self.translate_text(remarks_content.get_text(strip=True))
                        
                        # Extract owner
                        owner_section = soup.find(string=re.compile(r'Propriétaires?', re.I))
                        if owner_section:
                            owner_content = owner_section.find_next('td')
                            if owner_content:
                                owner = owner_content.get_text(strip=True)
                        
                        return self.create_hut_data(
                            name, latitude, longitude, altitude, hut_type_std,
                            page_url, phone, email, website, capacity, capacity_max,
                            opening_hours, description, manager, owner, access,
                            comments, water_source, best_time, posted_by, refuge_id
                        )
                        
            except asyncio.TimeoutError:
                self.failed += 1
                return None
            except Exception as e:
                self.failed += 1
                return None
    
    def create_hut_data(self, name, lat, lon, alt, hut_type, url,
                       phone, email, website, capacity, capacity_max,
                       opening, desc, manager, owner, access, comments,
                       water, best_time, posted_by, refuge_id):
        """Create standardized hut data dictionary matching database format"""
        return {
            'source_id': str(refuge_id),
            'name': name,
            'latitude': lat,
            'longitude': lon,
            'altitude': alt,
            'hut_type': hut_type,
            'country': None,  # Will be geocoded later
            'region': None,
            'phone': phone,
            'email': email,
            'website': website,
            'capacity': capacity,
            'capacity_max': capacity_max,
            'opening_hours': opening,
            'description': desc,
            'manager': manager,
            'owner': owner,
            'access': access,
            'comments': comments,
            'water_source': water,
            'best_time_to_visit': best_time,
            'posted_by': posted_by,
            'url': url,
            'status': '',
            'status_description': '',
            'amenities': '',
            'image_url': '',
            'posted_date': ''
        }
    
    async def process_batch(self, session, refuge_ids, batch_num, total_batches):
        """Process a batch of refuge IDs"""
        print(f"\n[Batch {batch_num}/{total_batches}] Processing {len(refuge_ids)} refuges...")
        
        tasks = [self.scrape_refuge_async(session, rid) for rid in refuge_ids]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out None and exceptions
        valid_huts = []
        for result in results:
            if result and not isinstance(result, Exception):
                valid_huts.append(result)
                self.successful += 1
            elif isinstance(result, Exception):
                self.failed += 1
        
        # Save to database
        if valid_huts:
            for hut in valid_huts:
                self.db.save_hut(hut, 'refuges.info')
        
        return len(valid_huts)
    
    async def run_async(self, refuge_ids):
        """Main async scraping loop"""
        self.semaphore = asyncio.Semaphore(self.max_concurrent)
        
        # Create aiohttp session with timeout
        timeout = aiohttp.ClientTimeout(total=60, connect=30)
        connector = aiohttp.TCPConnector(limit=self.max_concurrent, limit_per_host=self.max_concurrent)
        
        async with aiohttp.ClientSession(
            timeout=timeout,
            connector=connector,
            headers={'User-Agent': 'MountainHutsEurope/1.0 (Educational Project)'}
        ) as session:
            
            # Process in batches to manage memory
            batch_size = 100
            total_batches = (len(refuge_ids) + batch_size - 1) // batch_size
            
            start_time = time.time()
            
            for i in range(0, len(refuge_ids), batch_size):
                batch = refuge_ids[i:i + batch_size]
                batch_num = (i // batch_size) + 1
                
                batch_start = time.time()
                saved = await self.process_batch(session, batch, batch_num, total_batches)
                batch_time = time.time() - batch_start
                
                # Progress
                elapsed = time.time() - start_time
                rate = (i + len(batch)) / elapsed
                remaining = len(refuge_ids) - (i + len(batch))
                eta = remaining / rate if rate > 0 else 0
                
                print(f"  [OK] Saved {saved} huts in {batch_time:.1f}s")
                print(f"  [Progress] {self.successful}/{len(refuge_ids)} | "
                      f"Rate: {rate:.1f} huts/s | ETA: {eta/60:.1f} min")
                
                # Small delay between batches
                await asyncio.sleep(0.5)
    
    def run(self, scrape_all=True, limit=None):
        """Main entry point"""
        print("=" * 70)
        print("REFUGES.INFO FAST PARALLEL SCRAPER")
        print(f"[SPEED] {self.max_concurrent}x concurrent requests")
        print("=" * 70)
        print()
        
        # Initialize database
        self.db.init_database()
        self.db.register_source('refuges.info', self.base_url, 
                                'French Alpine refuges and mountain huts database')
        
        # Get refuge IDs
        refuge_ids = self.get_all_refuge_ids()
        
        if not scrape_all and limit:
            refuge_ids = random.sample(refuge_ids, min(limit, len(refuge_ids)))
        
        if not refuge_ids:
            print("[ERROR] No refuges to scrape")
            return
        
        print(f"\n[*] Will scrape {len(refuge_ids)} refuges...")
        print(f"[*] Estimated time: {len(refuge_ids) / (self.max_concurrent * 2) / 60:.1f} minutes")
        print(f"[*] (vs. {len(refuge_ids) * 1.2 / 60:.1f} minutes with old scraper)\n")
        
        # Run async scraper
        start_time = time.time()
        asyncio.run(self.run_async(refuge_ids))
        total_time = time.time() - start_time
        
        # Final stats
        self.db.update_source_stats('refuges.info')
        
        print("\n" + "=" * 70)
        print("SCRAPING SUMMARY")
        print("=" * 70)
        print(f"[OK] Successfully scraped: {self.successful}")
        print(f"[ERROR] Failed: {self.failed}")
        print(f"[*] Total processed: {len(refuge_ids)}")
        print(f"[*] Time elapsed: {total_time/60:.1f} minutes")
        print(f"[*] Average rate: {self.successful/total_time:.1f} huts/second")
        print(f"[*] Speedup: {len(refuge_ids)*1.2/total_time:.1f}x faster than sequential!")
        print("\n[OK] Scraping complete!")


if __name__ == "__main__":
    import sys
    
    # Default: 20 concurrent requests (adjustable)
    concurrent = 20
    if '--concurrent' in sys.argv:
        idx = sys.argv.index('--concurrent')
        if idx + 1 < len(sys.argv):
            concurrent = int(sys.argv[idx + 1])
    
    scraper = RefugesInfoFastScraper(max_concurrent=concurrent)
    
    if '--all' in sys.argv:
        print(f"\n[*] Scraping ALL refuges with {concurrent} concurrent requests")
        scraper.run(scrape_all=True)
    elif '--limit' in sys.argv:
        idx = sys.argv.index('--limit')
        if idx + 1 < len(sys.argv):
            limit = int(sys.argv[idx + 1])
            print(f"\n[*] Scraping {limit} refuges with {concurrent} concurrent requests")
            scraper.run(scrape_all=False, limit=limit)
    else:
        print("\n[*] Usage:")
        print("  python scraper_refuges_info_fast.py --all [--concurrent 20]")
        print("  python scraper_refuges_info_fast.py --limit 500 [--concurrent 20]")
        print("\n[*] Default: --limit 100 --concurrent 20")
        scraper.run(scrape_all=False, limit=100)

