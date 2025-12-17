"""
Improved scraper for boudy.info
Extracts comprehensive information from mountain huts database
"""

from base_scraper import BaseScraper
from typing import List, Dict
import time
import json
import re
from bs4 import BeautifulSoup
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from translator import get_translator
from data_cleaner import clean_phone, clean_email, clean_url, clean_text


class BoudyInfoScraperImproved(BaseScraper):
    """Improved scraper for boudy.info website"""
    
    def __init__(self, db_path: str = "data/mountain_huts.db"):
        super().__init__(db_path)
        # Initialize translator for Czech -> English translation
        self.translator = get_translator()
        self.fields_to_translate = [
            'description', 'water_source', 'access', 'opening_hours',
            'owner', 'manager', 'comments'
        ]
    
    @property
    def source_name(self) -> str:
        return "boudy.info"
    
    @property
    def source_url(self) -> str:
        return "https://www.boudy.info"
    
    @property
    def source_description(self) -> str:
        return "Open database of mountain huts, bivouacs and shelters in Central Europe and Alps"
    
    def get_hut_types(self) -> Dict[int, str]:
        """Map of hut type codes to descriptions"""
        return {
            0: "Unknown",
            1: "Bivouac",
            2: "Shelter",
            3: "Mountain hut"
        }
    
    def get_status_types(self) -> Dict[int, str]:
        """Map of status codes to descriptions"""
        return {
            0: "New",
            1: "Approved",
            2: "Deleted",
            3: "Secret"
        }
    
    def scrape_hut_details(self, hut_id: str) -> Dict:
        """
        Scrape detailed information from a hut's detail page
        """
        details = {}
        
        try:
            url = f"{self.source_url}/bouda.php?id={hut_id}"
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Get full page text for pattern matching
            page_text = soup.get_text()
            
            # Extract altitude from subtitle
            podnadpis = soup.find('div', class_='podnadpis')
            if podnadpis:
                subtitle = podnadpis.get_text()
                # Pattern: "... | 2 050 m.n.m." or "... | 2050 m.n.m."
                altitude_match = re.search(r'(\d[\d\s]+)\s*m\.n\.m\.', subtitle)
                if altitude_match:
                    alt_str = altitude_match.group(1).replace(' ', '').replace(',', '')
                    try:
                        details['altitude'] = int(alt_str)
                    except:
                        pass
            
            # Extract capacity
            info_pocet = soup.find('div', class_='info_pocet')
            if info_pocet:
                try:
                    capacity = int(re.sub(r'\D', '', info_pocet.get_text()))
                    if capacity > 0:
                        details['capacity'] = capacity
                except:
                    pass
            
            info_pocet_max = soup.find('div', class_='info_pocet_max')
            if info_pocet_max:
                try:
                    max_cap = int(re.sub(r'\D', '', info_pocet_max.get_text()))
                    if max_cap > 0:
                        details['capacity_max'] = max_cap
                except:
                    pass
            
            # Extract phone numbers - look in all text
            phone_patterns = [
                r'\+\d{1,3}[\s\-]?\d{3}[\s\-]?\d{3}[\s\-]?\d{3,4}',  # +420 xxx xxx xxx
                r'\b\d{3}[\s\-]\d{3}[\s\-]\d{3}\b',  # xxx xxx xxx
                r'tel[:\.\s]+(\+?\d[\d\s\-]{8,})',  # tel: xxx
            ]
            
            for pattern in phone_patterns:
                matches = re.findall(pattern, page_text, re.I)
                for match in matches:
                    phone = match if isinstance(match, str) else match[0] if match else None
                    if phone and len(phone.replace(' ', '').replace('-', '')) >= 9:
                        # Clean up
                        phone = re.sub(r'\s+', ' ', phone).strip()
                        if 'boudy.info' not in phone.lower() and 'upravit' not in phone.lower():
                            details['phone'] = phone
                            break
                if 'phone' in details:
                    break
            
            # Extract email
            email_matches = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', page_text)
            for email in email_matches:
                # Filter out obvious non-emails
                if ('boudy.info' not in email.lower() and 
                    'example' not in email.lower() and
                    len(email) > 5):
                    details['email'] = email
                    break
            
            # Extract website - look for external links
            for link in soup.find_all('a', href=True):
                href = link.get('href', '')
                if (href.startswith('http') and 
                    'boudy.info' not in href and
                    'mailto:' not in href and
                    'javascript:' not in href and
                    'facebook' not in href):
                    details['website'] = href
                    break
            
            # Extract descriptions from content sections
            # Look for div elements with actual content (not just "Upravit")
            content_divs = soup.find_all('div', class_='popis_text')
            description_parts = []
            
            for div in content_divs:
                text = div.get_text(strip=True)
                # Skip edit links and very short text
                if (text and 
                    len(text) > 20 and 
                    'Upravit' not in text and
                    'upravit' not in text.lower()):
                    description_parts.append(text)
            
            if description_parts:
                description_text = ' '.join(description_parts[:3])[:500]
                # Translate Czech description to English
                details['description'] = self.translator.translate(description_text) if self.translator.enabled else description_text
            
            # Look for description in any div/p with substantial text
            if 'description' not in details or len(details.get('description', '')) < 50:
                for elem in soup.find_all(['div', 'p']):
                    text = elem.get_text(strip=True)
                    if (len(text) > 50 and 
                        len(text) < 800 and
                        'Upravit' not in text and
                        'Vložil' not in text and
                        '@' not in text):  # Skip user info
                        # Check if it's actual descriptive content
                        if any(word in text.lower() for word in ['hut', 'bouda', 'refuge', 'bivak', 'chata', 'situated', 'located']):
                            description_text = text[:500]
                            # Translate Czech description to English
                            details['description'] = self.translator.translate(description_text) if self.translator.enabled else description_text
                            break
            
            # Extract water source info
            water_keywords = ['voda', 'water', 'zdroj', 'source', 'studna', 'well', 'potok', 'stream']
            for elem in soup.find_all(['div', 'p', 'li']):
                text = elem.get_text(strip=True)
                if (len(text) > 10 and 
                    len(text) < 300 and
                    any(kw in text.lower() for kw in water_keywords) and
                    'Upravit' not in text):
                    water_text = text[:200]
                    # Translate Czech water source info to English
                    details['water_source'] = self.translator.translate(water_text) if self.translator.enabled else water_text
                    break
            
            # Extract access information
            access_keywords = ['přístup', 'access', 'cesta', 'trail', 'path', 'route', 'approach']
            for elem in soup.find_all(['div', 'p', 'li']):
                text = elem.get_text(strip=True)
                if (len(text) > 10 and 
                    len(text) < 400 and
                    any(kw in text.lower() for kw in access_keywords) and
                    'Upravit' not in text):
                    access_text = text[:300]
                    # Translate Czech access info to English
                    details['access'] = self.translator.translate(access_text) if self.translator.enabled else access_text
                    break
            
            # Extract opening/season information  
            season_keywords = ['otevřeno', 'opening', 'open', 'sezóna', 'season', 'celoročně', 'year-round']
            for elem in soup.find_all(['div', 'p', 'li']):
                text = elem.get_text(strip=True)
                if (len(text) > 5 and 
                    len(text) < 200 and
                    any(kw in text.lower() for kw in season_keywords) and
                    'Upravit' not in text):
                    opening_text = text[:150]
                    # Translate Czech opening hours to English
                    details['opening_hours'] = self.translator.translate(opening_text) if self.translator.enabled else opening_text
                    break
            
            # Extract owner/manager from any text mentioning them
            owner_patterns = [
                r'[Mm]ajitel[:\s]+([^|]+)',
                r'[Oo]wner[:\s]+([^|]+)',
                r'[Vv]lastník[:\s]+([^|]+)'
            ]
            for pattern in owner_patterns:
                match = re.search(pattern, page_text)
                if match:
                    owner = match.group(1).strip()
                    if len(owner) > 2 and len(owner) < 100:
                        # Translate owner name if it contains Czech text (usually names don't need translation, but descriptions might)
                        details['owner'] = self.translator.translate(owner, force=False) if self.translator.enabled else owner
                        break
            
            manager_patterns = [
                r'[Ss]právce[:\s]+([^|]+)',
                r'[Mm]anager[:\s]+([^|]+)',
                r'[Kk]ontakt[:\s]+([^|]+)'
            ]
            for pattern in manager_patterns:
                match = re.search(pattern, page_text)
                if match:
                    manager = match.group(1).strip()
                    if len(manager) > 2 and len(manager) < 100 and manager != details.get('owner'):
                        # Translate manager name if it contains Czech text
                        details['manager'] = self.translator.translate(manager, force=False) if self.translator.enabled else manager
                        break
            
            # Extract comments from comment section
            poz_section = soup.find('div', class_='sloupek_poz')
            if poz_section:
                comments = []
                # Look for comment text divs
                poz_txts = poz_section.find_all('div', class_='poz_txt')
                for poz in poz_txts[:3]:  # Get first 3 comments
                    comment = poz.get_text(strip=True)
                    # Remove date and author
                    comment = re.sub(r'\d{2}\.\d{2}\.\d{4}.*?\d{2}:\d{2}', '', comment)
                    comment = re.sub(r'Vložil.*?:', '', comment)
                    comment = comment.strip()
                    
                    if len(comment) > 15 and len(comment) < 500:
                        comments.append(comment)
                
                if comments:
                    comments_text = ' | '.join(comments)[:600]
                    # Translate Czech comments to English
                    details['comments'] = self.translator.translate(comments_text) if self.translator.enabled else comments_text
            
            # Extract posted by information
            vlozil_match = re.search(r'Vložil[:\s]+([^\(]+)\s*\((\d{2}\.\d{2}\.\d{4})\)', page_text)
            if vlozil_match:
                details['posted_by'] = vlozil_match.group(1).strip()
                details['posted_date'] = vlozil_match.group(2)
            
        except Exception as e:
            print(f"  Error scraping details for hut {hut_id}: {e}")
        
        return details
    
    def scrape_ajax_data(self, lat1: float, lon1: float, lat2: float, lon2: float) -> List[Dict]:
        """Scrape data from the AJAX endpoint for a given bounding box"""
        try:
            response = self.session.get(
                f"{self.source_url}/_ajax_boudy.php",
                params={
                    'lat1': lat1,
                    'lon1': lon1,
                    'lat2': lat2,
                    'lon2': lon2
                },
                timeout=15
            )
            response.raise_for_status()
            
            data = response.json()
            features = data.get('features', [])
            
            huts = []
            for feature in features:
                try:
                    props = feature.get('properties', {})
                    geometry = feature.get('geometry', {})
                    coords = geometry.get('coordinates', [])
                    
                    hut_data = {
                        'source_id': str(feature.get('id')),
                        'name': props.get('name', 'Unknown'),
                        'icon': props.get('icon', '')
                    }
                    
                    # Extract coordinates (boudy.info uses [latitude, longitude])
                    if len(coords) >= 2:
                        hut_data['latitude'] = float(coords[0])
                        hut_data['longitude'] = float(coords[1])
                    
                    # Parse icon to get type and status
                    if hut_data['icon']:
                        icon_parts = hut_data['icon'].split('_')
                        if len(icon_parts) >= 3:
                            type_code = int(icon_parts[0])
                            hut_data['status'] = int(icon_parts[2])
                            
                            type_map = self.get_hut_types()
                            hut_data['hut_type'] = type_map.get(type_code, 'Unknown')
                            
                            status_map = self.get_status_types()
                            hut_data['status_description'] = status_map.get(hut_data['status'], '')
                    
                    # Build URL
                    if hut_data.get('source_id'):
                        hut_data['url'] = f"{self.source_url}/bouda.php?id={hut_data['source_id']}"
                    
                    huts.append(hut_data)
                    
                except Exception as e:
                    print(f"Error parsing feature: {e}")
            
            return huts
            
        except Exception as e:
            print(f"Error fetching AJAX data: {e}")
            return []
    
    def scrape(self) -> List[Dict]:
        """Scrape all regions covering the entire Alps and Central Europe"""
        print("Scraping boudy.info - Alps and Central Europe regions...")
        print("This will take approximately 5-7 minutes to scrape ~889 huts with details.\n")
        
        all_huts = []
        seen_ids = set()
        
        # Grid covering Alps and Central Europe
        lat_min, lat_max = 43.5, 52.0
        lon_min, lon_max = 5.0, 20.0
        grid_size = 2.0
        
        lat = lat_min
        region_count = 0
        total_regions = int(((lat_max - lat_min) / grid_size) * ((lon_max - lon_min) / grid_size))
        
        while lat < lat_max:
            lon = lon_min
            while lon < lon_max:
                region_count += 1
                lat1, lon1 = lat, lon
                lat2, lon2 = min(lat + grid_size, lat_max), min(lon + grid_size, lon_max)
                
                print(f"[{region_count}/{total_regions}] Region ({lat1:.1f}, {lon1:.1f}) to ({lat2:.1f}, {lon2:.1f})", end=' ')
                
                huts = self.scrape_ajax_data(lat1, lon1, lat2, lon2)
                print(f"- Found {len(huts)} huts")
                
                # Process each hut
                for hut in huts:
                    hut_id = hut.get('source_id')
                    if hut_id and hut_id not in seen_ids:
                        seen_ids.add(hut_id)
                        
                        # Scrape detailed information
                        try:
                            name = hut.get('name', 'Unknown')[:40]
                            print(f"  Scraping: {name}")
                        except:
                            print(f"  Scraping hut ID: {hut_id}")
                        
                        details = self.scrape_hut_details(hut_id)
                        hut.update(details)
                        
                        # Translate any remaining Czech text fields
                        if self.translator.enabled:
                            hut = self.translator.translate_dict_fields(hut, self.fields_to_translate)
                        
                        # Normalize and add
                        normalized = self.normalize_hut_data(hut)
                        all_huts.append(normalized)
                        
                        time.sleep(0.2)  # Be polite
                
                time.sleep(0.3)
                lon += grid_size
            lat += grid_size
        
        print(f"\n[OK] Scraping complete! Found {len(all_huts)} unique huts")
        return all_huts


if __name__ == "__main__":
    scraper = BoudyInfoScraperImproved()
    scraper.run()

