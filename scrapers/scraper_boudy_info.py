"""
Scraper for boudy.info
Mountain huts database covering Czech Republic, Slovakia, Alps region
"""

from base_scraper import BaseScraper
from typing import List, Dict
import time
import json
import re
from bs4 import BeautifulSoup


class BoudyInfoScraper(BaseScraper):
    """Scraper for boudy.info website"""
    
    @property
    def source_name(self) -> str:
        return "boudy.info"
    
    @property
    def source_url(self) -> str:
        return "https://www.boudy.info"
    
    @property
    def source_description(self) -> str:
        return "Open database of mountain huts, bivouacs and bivouacs in Central Europe and Alps"
    
    def get_hut_types(self) -> Dict[int, str]:
        """Map of hut type codes to descriptions"""
        return {
            0: "Unidentified object",
            1: "Bivouac/camping spot",
            2: "Shelter/hut",
            3: "Mountain hut/hotel"
        }
    
    def get_status_types(self) -> Dict[int, str]:
        """Map of status codes to descriptions"""
        return {
            0: "New object",
            1: "Approved object",
            2: "Deleted object",
            3: "Secret object"
        }
    
    def scrape_hut_details(self, hut_id: str) -> Dict:
        """
        Scrape detailed information from a hut's detail page
        Returns dict with: altitude, capacity, water_source, best_time_to_visit, posted_by, comments
        """
        details = {}
        
        try:
            url = f"{self.source_url}/bouda.php?id={hut_id}"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract altitude from header subtitle (div.podnadpis)
            # Format: "Česká republika, Podyjí, Šobes, pravý břeh Dyje | 250 m.n.m."
            podnadpis = soup.find('div', class_='podnadpis')
            if podnadpis:
                subtitle_text = podnadpis.get_text()
                # Look for pattern like "250 m.n.m." (meters above sea level in Czech)
                altitude_match = re.search(r'(\d+)\s*m\.n\.m\.', subtitle_text)
                if altitude_match:
                    details['altitude'] = int(altitude_match.group(1))
            
            # Extract capacity (number of people)
            # Look for div.info_pocet (regular capacity) and div.info_pocet_max (max capacity)
            info_pocet = soup.find('div', class_='info_pocet')
            if info_pocet:
                capacity_text = info_pocet.get_text(strip=True)
                try:
                    details['capacity'] = int(capacity_text)
                except:
                    pass
            
            info_pocet_max = soup.find('div', class_='info_pocet_max')
            if info_pocet_max:
                max_capacity_text = info_pocet_max.get_text(strip=True)
                try:
                    details['capacity_max'] = int(max_capacity_text)
                except:
                    pass
            
            # Extract posted by information (Vložil)
            info_txt = soup.find('div', class_='info_txt')
            if info_txt:
                vlozil = info_txt.find('b', string=re.compile(r'Vložil', re.I))
                if vlozil:
                    # Get next text after the bold tag
                    posted_text = vlozil.next_sibling
                    if posted_text:
                        posted_text = str(posted_text).strip()
                        # Format: "Beránek a Mazda (08.06.2006)"
                        match = re.search(r'(.+?)\s*\((\d{2}\.\d{2}\.\d{4})\)', posted_text)
                        if match:
                            details['posted_by'] = match.group(1).strip()
                            details['posted_date'] = match.group(2)
            
            # Extract comments (Poznámky)
            poz_section = soup.find('div', class_='sloupek_poz')
            if poz_section:
                comments = []
                poz_txts = poz_section.find_all('div', class_='poz_txt')
                for poz in poz_txts[:3]:  # Get first 3 comments
                    # Get date
                    datum = poz.find('div', class_='poz_datum_cas')
                    # Get comment text (everything after the date)
                    comment_text = poz.get_text(strip=True)
                    if datum:
                        # Remove the date from comment text
                        date_text = datum.get_text(strip=True)
                        comment_text = comment_text.replace(date_text, '', 1).strip()
                    # Also remove the author name if present
                    vlozil = poz.find('div', class_='poz_vlozil')
                    if vlozil:
                        author = vlozil.get_text(strip=True)
                        comment_text = comment_text.replace(author, '').strip()
                    
                    if comment_text and len(comment_text) > 10:
                        comments.append(comment_text[:300])  # Limit to 300 chars each
                
                if comments:
                    details['comments'] = ' | '.join(comments)
            
            # Extract description sections (Popis)
            # These are in sections with div.popis_nadpis as headers
            popis_sections = soup.find_all('div', class_='popis_nadpis')
            for section in popis_sections:
                section_title = section.get_text(strip=True)
                # Get the text content after this header (before the next section)
                content_parts = []
                for sibling in section.next_siblings:
                    if sibling.name == 'div' and 'popis_nadpis' in sibling.get('class', []):
                        break  # Stop at next section header
                    if sibling.name == 'div' and 'popis_upravit' in sibling.get('class', []):
                        continue  # Skip edit links
                    if hasattr(sibling, 'get_text'):
                        text = sibling.get_text(strip=True)
                        if text and len(text) > 3:
                            content_parts.append(text)
                
                content = ' '.join(content_parts)
                
                # Map Czech section names to English keys
                if 'Zdroj vody' in section_title or 'Water' in section_title:
                    if content:
                        details['water_source'] = content[:200]
                elif 'Nejvhodnější doba' in section_title or 'Best time' in section_title:
                    if content:
                        details['best_time_to_visit'] = content[:200]
                elif 'Přístup' in section_title or 'Access' in section_title:
                    if content:
                        details['access'] = content[:300]
                elif 'Popis' == section_title or 'Description' == section_title:
                    if content:
                        # This is the main description
                        if 'description' not in details:
                            details['description'] = content[:500]
            
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
                }
            )
            response.raise_for_status()
            
            data = response.json()
            
            # The response should be GeoJSON format with features array
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
                        'description': props.get('popupContent', ''),
                        'icon': props.get('icon', '')
                    }
                    
                    # Extract coordinates
                    # NOTE: boudy.info uses [latitude, longitude] format (NOT standard GeoJSON!)
                    if len(coords) >= 2:
                        hut_data['latitude'] = float(coords[0])   # First value is latitude
                        hut_data['longitude'] = float(coords[1])  # Second value is longitude
                    
                    # Parse icon to get type and status
                    # Icon format: "2_4_1" means type_subtype_status
                    if hut_data['icon']:
                        icon_parts = hut_data['icon'].split('_')
                        if len(icon_parts) >= 3:
                            hut_data['type'] = int(icon_parts[0])
                            hut_data['subtype'] = int(icon_parts[1])
                            hut_data['status'] = int(icon_parts[2])
                    
                    # Add type and status descriptions
                    type_map = self.get_hut_types()
                    status_map = self.get_status_types()
                    hut_data['type_description'] = type_map.get(hut_data.get('type', 0))
                    hut_data['status_description'] = status_map.get(hut_data.get('status', 0))
                    
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
        print("Scraping all regions (Alps, Slovenia, Czech Republic, Slovakia)...")
        
        all_huts = []
        seen_ids = set()
        
        # Expanded grid covering entire Alps region and Central Europe
        lat_min, lat_max = 43.5, 52.0  # From French Alps to Northern Czech Republic
        lon_min, lon_max = 5.0, 20.0   # From France to Eastern Czech Republic/Slovakia
        
        # Grid size (degrees) - larger boxes to minimize requests
        grid_size = 2.0
        
        lat = lat_min
        while lat < lat_max:
            lon = lon_min
            while lon < lon_max:
                lat1, lon1 = lat, lon
                lat2, lon2 = min(lat + grid_size, lat_max), min(lon + grid_size, lon_max)
                
                print(f"Fetching region: ({lat1:.2f}, {lon1:.2f}) to ({lat2:.2f}, {lon2:.2f})")
                
                huts = self.scrape_ajax_data(lat1, lon1, lat2, lon2)
                print(f"  Found {len(huts)} huts")
                
                # Deduplicate by ID
                for hut in huts:
                    hut_id = hut.get('source_id')
                    if hut_id and hut_id not in seen_ids:
                        seen_ids.add(hut_id)
                        
                        # Scrape detailed information from the hut page
                        print(f"  Scraping details for: {hut.get('name', 'Unknown')[:40]}")
                        details = self.scrape_hut_details(hut_id)
                        
                        # Merge details into hut data
                        hut.update(details)
                        
                        # Normalize the data
                        normalized = self.normalize_hut_data(hut)
                        all_huts.append(normalized)
                        
                        # Be polite - short delay between detail page requests
                        time.sleep(0.3)
                
                time.sleep(0.5)  # Be polite to the server
                
                lon += grid_size
            lat += grid_size
        
        print(f"\nTotal unique huts found: {len(all_huts)}")
        return all_huts


if __name__ == "__main__":
    scraper = BoudyInfoScraper()
    scraper.run()
