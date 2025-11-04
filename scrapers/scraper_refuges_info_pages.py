"""
Refuges.info Individual Page Scraper
Scrapes detailed information from individual refuge pages
"""
import requests
from bs4 import BeautifulSoup
import time
import random
import re
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import MountainHutsDatabase

class RefugesInfoPageScraper:
    def __init__(self):
        self.base_url = "https://www.refuges.info"
        self.api_url = "https://www.refuges.info/api/bbox"
        self.db = MountainHutsDatabase()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'MountainHutsEurope/1.0 (Educational Project)'
        })
        
        # Translation dictionary (same as before)
        self.translations = {
            'cabane non gardée': 'Unmanaged hut',
            'refuge gardé': 'Managed hut',
            "gîte d'étape": 'Guesthouse',
            'grotte': 'Cave shelter',
            'bivouac': 'Bivouac shelter',
            # Add more as needed
            'matelas': 'mattresses',
            'poêle': 'stove',
            'cheminée': 'fireplace',
            'couvertures': 'blankets',
            'eau': 'water',
            'bois': 'wood',
            'latrines': 'latrines',
            'Oui': 'Yes',
            'Non': 'No',
            'Capacité d\'accueil': 'Capacity',
            'Eau gratuite en libre accès': 'Free water access',
            'Site officiel': 'Official website',
            'Accès': 'Access',
            'Remarques': 'Remarks',
            'Propriétaires': 'Owners',
            'Localisation administrative': 'Administrative location',
            'Coordonnées': 'Coordinates'
        }
    
    def translate_text(self, text):
        """Translate French text to English"""
        if not text:
            return text
        
        translated = text
        for fr, en in self.translations.items():
            translated = re.sub(r'\b' + re.escape(fr) + r'\b', en, translated, flags=re.IGNORECASE)
        
        return translated
    
    def get_all_refuge_ids(self, include_types=['cabane', 'refuge', 'bivouac']):
        """
        Get ALL refuge IDs from the API
        
        Types available:
        - cabane (ID: 7): Unmanned huts/cabins - 3,672 points
        - refuge (ID: 10): Staffed refuges - 412 points  
        - bivouac: Bivouac shelters - ~4,000+ points
        - gite (ID: 9): Guesthouses - 787 points (optional)
        
        EXCLUDED:
        - grotte (ID: 29): Cave shelters - 25 points (not mountain huts)
        - point d'eau (ID: 23): Water points - 78 points (not shelters)
        """
        print(f"\n[*] Fetching ALL refuge IDs from refuges.info API...")
        print(f"[*] Including types: {', '.join(include_types)}")
        
        all_refuges = []
        type_counts = {}
        
        # Fetch in batches by type to handle large datasets
        for point_type in include_types:
            print(f"\n[*] Fetching {point_type} type...")
            
            params = {
                'bbox': 'world',
                'type_points': point_type,
                'nb_points': '10000',  # Maximum allowed
                'format': 'geojson',
                'detail': 'simple'
            }
            
            try:
                response = self.session.get(self.api_url, params=params, timeout=60)
                response.raise_for_status()
                data = response.json()
                
                features = data.get('features', [])
                
                for feature in features:
                    props = feature['properties']
                    refuge_id = props.get('id')
                    type_info = props.get('type', {})
                    type_val = type_info.get('valeur', 'Unknown')
                    
                    # Filter out unwanted types
                    if 'grotte' in type_val.lower():  # Exclude caves
                        continue
                    if 'point d' in type_val.lower() or 'eau' in type_val.lower():  # Exclude water points
                        continue
                    
                    if refuge_id:
                        all_refuges.append({
                            'id': refuge_id,
                            'name': props.get('nom', 'Unknown'),
                            'type': type_val
                        })
                        
                        # Count by type
                        type_counts[type_val] = type_counts.get(type_val, 0) + 1
                
                print(f"  [OK] Found {len(features)} {point_type} points")
                
            except Exception as e:
                print(f"  [ERROR] Error fetching {point_type}: {e}")
                continue
            
            # Be polite between requests
            time.sleep(0.5)
        
        # Remove duplicates by ID
        seen_ids = set()
        unique_refuges = []
        for refuge in all_refuges:
            if refuge['id'] not in seen_ids:
                seen_ids.add(refuge['id'])
                unique_refuges.append(refuge)
        
        print(f"\n" + "=" * 70)
        print(f"[OK] Total unique refuges found: {len(unique_refuges)}")
        print(f"\nBreakdown by type:")
        for type_name, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  {type_name}: {count}")
        print("=" * 70)
        
        return [r['id'] for r in unique_refuges]
    
    def scrape_refuge_page(self, refuge_id):
        """Scrape a single refuge page"""
        # Get the refuge data from API using the point endpoint
        api_url = f"https://www.refuges.info/api/point"
        
        try:
            # First get the link from API using the point ID
            params = {'id': refuge_id, 'format': 'geojson', 'detail': 'complet'}
            response = self.session.get(api_url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if not data or 'features' not in data or not data['features']:
                return None
            
            feature = data['features'][0]
            props = feature['properties']
            geom = feature['geometry']
            
            # Get the page URL
            page_url = props.get('lien')
            if not page_url:
                print(f"[!] No page URL for refuge {refuge_id}")
                return None
            
            print(f"[*] Scraping: {props.get('nom', 'Unknown')} ({page_url})")
            
            # Scrape the page
            response = self.session.get(page_url, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract data - pass both properties and geometry
            hut_data = self.parse_refuge_page(soup, {'properties': props, 'geometry': geom})
            
            return hut_data
            
        except Exception as e:
            print(f"[ERROR] Error scraping refuge {refuge_id}: {e}")
            return None
    
    def parse_refuge_page(self, soup, api_data):
        """Parse a refuge page and extract all data"""
        hut = {}
        
        props = api_data.get('properties', {})
        
        # Basic info from API
        hut['source_id'] = str(props.get('id'))
        hut['name'] = props.get('nom', '').strip()
        hut['url'] = props.get('lien', '')
        
        # Coordinates from geometry (GeoJSON format: [longitude, latitude])
        if 'geometry' in api_data and api_data['geometry']:
            coords = api_data['geometry'].get('coordinates', [0, 0])
            hut['longitude'] = float(coords[0]) if len(coords) > 0 else 0
            hut['latitude'] = float(coords[1]) if len(coords) > 1 else 0
        
        # Altitude from properties
        coord_data = api_data.get('properties', {}).get('coord', {})
        hut['altitude'] = coord_data.get('alt')
        
        # Type from API
        type_info = props.get('type', {})
        type_val = type_info.get('valeur', '').strip()
        type_map = {
            'cabane non gardée': 'Unmanned cabin',
            'refuge gardé': 'Staffed refuge',
            "gîte d'étape": 'Guesthouse',
            'grotte': 'Cave shelter',
            'bivouac': 'Bivouac shelter'
        }
        hut['type'] = type_map.get(type_val, None)
        
        # Parse the definition list for detailed information
        dl = soup.find('dl', class_='liste-wri')
        if dl:
            dts = dl.find_all('dt')
            dds = dl.find_all('dd')
            
            current_section = None
            for i, dt in enumerate(dts):
                section_name = dt.get_text(strip=True).lower()
                
                # Get corresponding dd elements (there might be multiple)
                dd_elements = []
                next_dt_index = i + 1
                dd_index = dts[:i+1].__len__() + len(dd_elements)
                
                # Collect all dd elements until next dt
                while dd_index < len(dds):
                    dd_elements.append(dds[dd_index])
                    dd_index += 1
                    if next_dt_index < len(dts):
                        break
                
                # Extract based on section
                if 'propriétaires' in section_name or 'owners' in section_name or 'gestionnaires' in section_name:
                    owner_text = ' '.join([dd.get_text(strip=True) for dd in dd_elements])
                    owner_text = owner_text.replace('Refuge.info n\'a aucun lien avec les gestionnaires. Vous devez les appeler directement.', '').strip()
                    
                    # Try to extract manager vs owner
                    if 'gestionnaire' in section_name:
                        hut['manager'] = self.translate_text(owner_text) if owner_text else None
                    else:
                        hut['owner'] = self.translate_text(owner_text) if owner_text else None
                    
                    # Extract phone and email from owner/manager text
                    if owner_text:
                        phone_match = re.search(r'\+\d{1,3}[\s\-]?\d{2,4}[\s\-]?\d{3,4}[\s\-]?\d{3,4}', owner_text)
                        if phone_match:
                            hut['phone'] = phone_match.group(0)
                        
                        email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', owner_text)
                        if email_match:
                            hut['email'] = email_match.group(0)
                
                elif 'accès' in section_name or 'access' in section_name:
                    access_text = ' '.join([dd.get_text(strip=True) for dd in dd_elements])
                    hut['access'] = self.translate_text(access_text) if access_text else None
                
                elif 'remarques' in section_name or 'remarks' in section_name:
                    remarks_text = ' '.join([dd.get_text(strip=True) for dd in dd_elements])
                    hut['comments'] = self.translate_text(remarks_text) if remarks_text else None
                
                elif 'ouverture' in section_name or 'opening' in section_name or 'horaires' in section_name:
                    opening_text = ' '.join([dd.get_text(strip=True) for dd in dd_elements])
                    hut['opening_hours'] = self.translate_text(opening_text) if opening_text else None
                
                elif 'informations complémentaires' in section_name:
                    # Parse additional information
                    for dd in dd_elements:
                        text = dd.get_text(strip=True)
                        
                        # Capacity
                        if 'Capacité' in text or 'Capacity' in text:
                            capacity_match = re.search(r':\s*(\d+)', text)
                            if capacity_match:
                                hut['capacity'] = int(capacity_match.group(1))
                        
                        # Water
                        if 'eau' in text.lower() or 'water' in text.lower():
                            hut['water_source'] = self.translate_text(text)
                        
                        # Latrines
                        if 'latrine' in text.lower():
                            has_latrines = 'Oui' in text or 'Yes' in text
                            if 'amenities' not in hut:
                                hut['amenities'] = []
                            if has_latrines:
                                hut['amenities'].append('Latrines')
                        
                        # Website
                        if 'Site officiel' in text or 'Official website' in text or 'site web' in text.lower():
                            link = dd.find('a')
                            if link and link.get('href'):
                                hut['website'] = link.get('href')
                        
                        # Phone number in additional info
                        if not hut.get('phone'):
                            phone_match = re.search(r'\+\d{1,3}[\s\-]?\d{2,4}[\s\-]?\d{3,4}[\s\-]?\d{3,4}', text)
                            if phone_match:
                                hut['phone'] = phone_match.group(0)
                        
                        # Email in additional info
                        if not hut.get('email'):
                            email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
                            if email_match:
                                hut['email'] = email_match.group(0)
        
        # Get location from page
        location_p = soup.find('p')
        if location_p:
            location_text = location_p.get_text()
            
            # Country will be assigned by geolocation script based on coordinates
            # (Removed direct extraction to ensure consistency across all sources)
        
        # Convert amenities list to string
        if 'amenities' in hut and hut['amenities']:
            hut['amenities'] = ', '.join(hut['amenities'])
        
        # Add source
        hut['source'] = 'refuges.info'
        
        return hut
    
    def run(self, scrape_all=True, limit=None, include_gite=False):
        """
        Main scraping process
        
        Args:
            scrape_all: If True, scrapes ALL refuges (8,000+). If False, uses limit.
            limit: Max number of refuges to scrape (only used if scrape_all=False)
            include_gite: Whether to include guesthouses (gîtes d'étape)
        """
        print("=" * 70)
        print("REFUGES.INFO COMPREHENSIVE SCRAPER")
        print("=" * 70)
        print()
        
        # Initialize database
        self.db.init_database()
        self.db.register_source('refuges.info', self.base_url, 
                                'French Alpine refuges and mountain huts database')
        
        # Determine which types to include
        include_types = ['cabane', 'refuge', 'bivouac']
        if include_gite:
            include_types.append('gite')
        
        # Get refuge IDs
        if scrape_all:
            print("[*] MODE: Scraping ALL refuges from refuges.info")
            print("[!] This will take several hours (8,000+ pages)")
            print("[!] Estimated time: 2.5-3 hours with 1 second delay per page\n")
            refuge_ids = self.get_all_refuge_ids(include_types)
        else:
            print(f"[*] MODE: Limited scraping ({limit} refuges)")
            all_ids = self.get_all_refuge_ids(include_types)
            refuge_ids = random.sample(all_ids, min(limit or 100, len(all_ids)))
        
        if not refuge_ids:
            print("[ERROR] No refuges to scrape")
            return
        
        print(f"\n[*] Will scrape {len(refuge_ids)} refuges...")
        print(f"[*] Estimated time: {len(refuge_ids) * 1.2 / 60:.1f} minutes\n")
        
        successful = 0
        failed = 0
        skipped = 0
        
        for i, refuge_id in enumerate(refuge_ids, 1):
            try:
                # Progress indicator every 10 huts
                if i % 10 == 0 or i == 1:
                    print(f"\n[Progress: {i}/{len(refuge_ids)}] ({successful} saved, {failed} failed, {skipped} skipped)")
                
                hut_data = self.scrape_refuge_page(refuge_id)
                
                if hut_data:
                    # Double-check it's not a cave or water point
                    hut_type = hut_data.get('type', '').lower() if hut_data.get('type') else ''
                    if 'grotte' in hut_type or 'cave' in hut_type:
                        skipped += 1
                        continue
                    if 'point d' in hut_type or 'water' in hut_type or 'eau' in hut_type:
                        skipped += 1
                        continue
                    
                    self.db.save_hut(hut_data, 'refuges.info')
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
                    self.db.update_source_stats('refuges.info')
                    print(f"  [COMMIT] Saved batch to database")
                
            except Exception as e:
                failed += 1
                if i % 10 == 0:
                    print(f"  [ERROR] Refuge {refuge_id}: {str(e)[:50]}")
                continue
        
        # Final commit
        self.db.update_source_stats('refuges.info')
        
        print("\n" + "=" * 70)
        print("SCRAPING SUMMARY")
        print("=" * 70)
        print(f"[OK] Successfully scraped: {successful}")
        print(f"[ERROR] Failed: {failed}")
        print(f"[SKIP] Skipped (caves/water): {skipped}")
        print(f"[*] Total processed: {len(refuge_ids)}")
        print(f"[*] Final database count: {successful}")
        print("\n[OK] Scraping complete!")


if __name__ == "__main__":
    import sys
    
    scraper = RefugesInfoPageScraper()
    
    # Check command line arguments
    if '--all' in sys.argv:
        print("\n" + "!" * 70)
        print("WARNING: You are about to scrape ALL refuges from refuges.info")
        print("This will scrape 8,000+ pages and take 2.5-3 hours!")
        print("!" * 70)
        response = input("\nAre you sure you want to continue? (yes/no): ")
        if response.lower() == 'yes':
            scraper.run(scrape_all=True, include_gite=False)
        else:
            print("Cancelled. Use without --all flag for limited scraping.")
    elif '--sample' in sys.argv:
        # Sample mode: scrape 200 refuges for testing
        print("[*] Sample mode: Scraping 200 random refuges")
        scraper.run(scrape_all=False, limit=200, include_gite=False)
    else:
        # Default: scrape 100 refuges
        print("[*] Default mode: Scraping 100 random refuges")
        print("[*] Use --all flag to scrape ALL refuges (8,000+)")
        print("[*] Use --sample flag to scrape 200 random refuges")
        scraper.run(scrape_all=False, limit=100, include_gite=False)
