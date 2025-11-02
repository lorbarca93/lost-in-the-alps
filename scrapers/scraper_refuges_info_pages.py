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
    
    def get_refuge_ids(self, limit=50):
        """Get a list of refuge IDs from the API"""
        print(f"🔄 Fetching refuge IDs from API...")
        
        params = {
            'bbox': 'world',
            'type_points': 'cabane,refuge,gite,grotte',
            'nb_points': '1000',  # Get a larger sample to choose from
            'format': 'geojson',
            'detail': 'simple'  # We only need IDs
        }
        
        try:
            response = self.session.get(self.api_url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            all_ids = [feature['properties']['id'] for feature in data['features']]
            
            # Randomly select the requested number
            selected_ids = random.sample(all_ids, min(limit, len(all_ids)))
            
            print(f"✅ Selected {len(selected_ids)} random refuges from {len(all_ids)} total")
            return selected_ids
            
        except Exception as e:
            print(f"❌ Error fetching refuge IDs: {e}")
            return []
    
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
                print(f"⚠️  No page URL for refuge {refuge_id}")
                return None
            
            print(f"📄 Scraping: {props.get('nom', 'Unknown')} ({page_url})")
            
            # Scrape the page
            response = self.session.get(page_url, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract data - pass both properties and geometry
            hut_data = self.parse_refuge_page(soup, {'properties': props, 'geometry': geom})
            
            return hut_data
            
        except Exception as e:
            print(f"❌ Error scraping refuge {refuge_id}: {e}")
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
                if 'propriétaires' in section_name or 'owners' in section_name:
                    owner_text = ' '.join([dd.get_text(strip=True) for dd in dd_elements])
                    owner_text = owner_text.replace('Refuge.info n\'a aucun lien avec les gestionnaires. Vous devez les appeler directement.', '').strip()
                    hut['owner'] = self.translate_text(owner_text) if owner_text else None
                
                elif 'accès' in section_name or 'access' in section_name:
                    access_text = ' '.join([dd.get_text(strip=True) for dd in dd_elements])
                    hut['access'] = self.translate_text(access_text) if access_text else None
                
                elif 'remarques' in section_name or 'remarks' in section_name:
                    remarks_text = ' '.join([dd.get_text(strip=True) for dd in dd_elements])
                    hut['comments'] = self.translate_text(remarks_text) if remarks_text else None
                
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
                        if 'Site officiel' in text or 'Official website' in text:
                            link = dd.find('a')
                            if link and link.get('href'):
                                hut['website'] = link.get('href')
        
        # Get location from page
        location_p = soup.find('p')
        if location_p:
            location_text = location_p.get_text()
            
            # Extract country
            country_match = re.search(r'Localisation administrative:.*?([A-Z][a-zà-ÿ]+)', location_text)
            if country_match:
                country_name = country_match.group(1).strip()
                # Translate some common countries
                country_translations = {
                    'Italia': 'Italy',
                    'France': 'France',
                    'Schweiz': 'Switzerland',
                    'Österreich': 'Austria',
                    'Deutschland': 'Germany',
                    'España': 'Spain'
                }
                hut['country'] = country_translations.get(country_name, country_name)
        
        # Convert amenities list to string
        if 'amenities' in hut and hut['amenities']:
            hut['amenities'] = ', '.join(hut['amenities'])
        
        # Add source
        hut['source'] = 'refuges.info'
        
        return hut
    
    def run(self, limit=50):
        """Main scraping process"""
        print("=" * 70)
        print("🏔️  REFUGES.INFO PAGE SCRAPER")
        print("=" * 70)
        print()
        
        # Get refuge IDs
        refuge_ids = self.get_refuge_ids(limit)
        
        if not refuge_ids:
            print("❌ No refuges to scrape")
            return
        
        print(f"\n📊 Will scrape {len(refuge_ids)} refuges...\n")
        
        successful = 0
        failed = 0
        
        for i, refuge_id in enumerate(refuge_ids, 1):
            print(f"\n[{i}/{len(refuge_ids)}] Processing refuge ID: {refuge_id}")
            
            try:
                hut_data = self.scrape_refuge_page(refuge_id)
                
                if hut_data:
                    self.db.save_hut(hut_data, 'refuges.info')
                    successful += 1
                    print(f"✅ Saved: {hut_data.get('name', 'Unknown')}")
                else:
                    failed += 1
                    print(f"⚠️  Failed to parse refuge {refuge_id}")
                
                # Be polite - add delay between requests
                time.sleep(1)
                
            except Exception as e:
                failed += 1
                print(f"❌ Error processing refuge {refuge_id}: {e}")
                continue
        
        print("\n" + "=" * 70)
        print("📊 SCRAPING SUMMARY")
        print("=" * 70)
        print(f"✅ Successfully scraped: {successful}")
        print(f"❌ Failed: {failed}")
        print(f"📝 Total processed: {len(refuge_ids)}")
        print("\n✅ Scraping complete!")


if __name__ == "__main__":
    scraper = RefugesInfoPageScraper()
    scraper.run(limit=50)
