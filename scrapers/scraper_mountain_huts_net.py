"""
Scraper for mountain-huts.net
Covers Balkan and Southeast Europe mountain huts
Data source: Alpine Association of Slovenia
"""

from base_scraper import BaseScraper
import requests
from bs4 import BeautifulSoup
import re
from typing import List, Dict
from datetime import datetime


class MountainHutsNetScraper(BaseScraper):
    """Scraper for mountain-huts.net covering Balkan countries"""
    
    @property
    def source_name(self) -> str:
        return "mountain-huts.net"
    
    @property
    def source_url(self) -> str:
        return "https://www.mountain-huts.net/"
    
    @property
    def source_description(self) -> str:
        return "Mountain huts in Balkan and Southeast Europe (Slovenia, Croatia, Bosnia, Serbia, Montenegro, Bulgaria, Macedonia, Greece)"
    
    def scrape(self) -> List[Dict]:
        """
        Scrape all mountain huts from mountain-huts.net
        Data is embedded in JavaScript with L.marker() calls
        """
        print(f"\n=== Scraping {self.source_name} ===")
        print(f"URL: {self.source_url}")
        
        try:
            # Fetch the page
            response = self.session.get(self.source_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find all inline scripts
            scripts = soup.find_all('script', src=False)
            marker_script = None
            
            # Find the large script with L.marker calls
            for script in scripts:
                if script.string and len(script.string) > 100000:
                    marker_script = script.string
                    break
            
            if not marker_script:
                print("ERROR: Could not find marker data script")
                return []
            
            print(f"Found marker script ({len(marker_script)} chars)")
            
            # Parse all L.marker() calls
            huts_data = self._parse_markers(marker_script)
            
            print(f"Successfully parsed {len(huts_data)} huts")
            return huts_data
            
        except Exception as e:
            print(f"ERROR scraping {self.source_name}: {e}")
            return []
    
    def _parse_markers(self, script: str) -> List[Dict]:
        """
        Parse L.marker() calls from JavaScript
        Format: L.marker([lat, lon], {title: 'Name, elevation'}).bindPopup('HTML').addTo(drzava_XX)
        """
        huts = []
        
        # Pattern to match L.marker calls with their popup data and country code
        # Captures: lat, lon, title, popup_html, country_code
        marker_pattern = r'L\.marker\(\[([-\d.]+),\s*([-\d.]+)\]\s*,\s*\{\s*title:\s*[\'"]([^\'"]+)[\'"]\s*[^}]*\}\s*\)\.bindPopup\([\'"]([^\'"]+?)(?<!\\)[\'"].*?\.addTo\(drzava_(\w+)\)'
        
        matches = re.findall(marker_pattern, script, re.DOTALL)
        
        print(f"Found {len(matches)} marker matches with country codes")
        
        for match in matches:
            lat, lon, title, popup_html, country_code = match
            
            # Parse the popup HTML for additional data
            hut_data = self._parse_popup(popup_html, title, float(lat), float(lon), country_code)
            
            if hut_data:
                huts.append(hut_data)
        
        return huts
    
    def _parse_popup(self, popup_html: str, title: str, lat: float, lon: float, country_code: str) -> Dict:
        """
        Parse the bindPopup HTML to extract hut details
        Example popup contains:
        - Organization/country flag
        - Name and elevation
        - Address
        - Website link
        - Coordinates
        """
        try:
            # Decode HTML entities
            from html import unescape
            popup_html = unescape(popup_html)
            
            soup = BeautifulSoup(popup_html, 'html.parser')
            
            # Extract name and elevation from title
            # Format: "Name, elevation m"
            name = title
            elevation = None
            
            name_match = re.match(r'(.+?),\s*(\d+)\s*m', title)
            if name_match:
                name = name_match.group(1).strip()
                elevation = int(name_match.group(2))
            
            # Extract organization (usually in first link)
            organization = None
            org_link = soup.find('a', href=re.compile(r'pzs\.si|hrs\.hr|pss\.ba|pss\.rs|fpcg\.me|bfp\.bg|fsm\.mk|eos\.gr', re.I))
            if org_link:
                org_b = org_link.find('b')
                if org_b:
                    organization = org_b.get_text(strip=True)
            
            # Map country codes from drzava_XX
            country_map = {
                'SI': 'Slovenia',
                'HR': 'Croatia',
                'BA': 'Bosnia and Herzegovina',
                'RS': 'Serbia',
                'ME': 'Montenegro',
                'BG': 'Bulgaria',
                'MK': 'North Macedonia',
                'GR': 'Greece'
            }
            country = country_map.get(country_code.upper(), country_code)
            
            # Extract name from h2 (more reliable than title)
            h2 = soup.find('h2')
            if h2:
                h2_text = h2.get_text(strip=True)
                # Parse "Name, elevation m"
                h2_match = re.match(r'(.+?),\s*(\d+)\s*m', h2_text)
                if h2_match:
                    name = h2_match.group(1).strip()
                    elevation = int(h2_match.group(2))
            
            # Extract address (text between h2 and first <p>)
            address = None
            # Look for text nodes after h2
            if h2:
                next_text = h2.next_sibling
                while next_text:
                    if isinstance(next_text, str):
                        addr = next_text.strip()
                        if addr and addr != ',':
                            address = addr
                            break
                    elif next_text.name == 'p':
                        break
                    next_text = next_text.next_sibling
            
            # Extract website URL
            website = None
            website_link = soup.find('a', string=re.compile(r'Mountain hut|website', re.I))
            if website_link:
                website = website_link.get('href')
            
            # Determine hut type
            hut_type = None
            if 'bivak' in name.lower() or 'bivouac' in name.lower():
                hut_type = 'bivouac'
            elif 'dom' in name.lower() or 'koča' in name.lower() or 'hut' in name.lower():
                hut_type = 'mountain_hut'
            elif 'zavetišče' in name.lower() or 'shelter' in name.lower():
                hut_type = 'shelter'
            
            # Build hut data
            hut_data = {
                'name': name,
                'latitude': lat,
                'longitude': lon,
                'altitude': elevation,  # Database expects 'altitude' not 'elevation'
                'type': hut_type,
                'country': country,
                'website': website,
                'source_id': f"{lat}_{lon}",  # Use coordinates as unique ID
                'description': organization,
            }
            
            return hut_data
            
        except Exception as e:
            print(f"ERROR parsing popup for {title}: {e}")
            return None


if __name__ == "__main__":
    scraper = MountainHutsNetScraper()
    scraper.run()
