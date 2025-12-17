"""
Scraper for mountainhuts.info - Enhanced version
Extracts comprehensive data including owner, manager, contact details, opening hours
"""

import requests
import re
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scrapers.base_scraper import BaseScraper
from data_cleaner import clean_text, clean_phone, clean_email, clean_url, standardize_country


class MountainhutsInfoScraper(BaseScraper):
    """Scraper for mountainhuts.info website with comprehensive data extraction"""
    
    # Map 3-letter country codes to full names
    COUNTRY_MAP = {
        'AUT': 'Austria', 'BIH': 'Bosnia and Herzegovina', 'BGR': 'Bulgaria',
        'HRV': 'Croatia', 'CZE': 'Czech Republic', 'FRA': 'France',
        'DEU': 'Germany', 'GRC': 'Greece', 'ITA': 'Italy',
        'MKD': 'North Macedonia', 'MNE': 'Montenegro', 'POL': 'Poland',
        'ROU': 'Romania', 'SRB': 'Serbia', 'SVK': 'Slovakia',
        'SVN': 'Slovenia', 'ESP': 'Spain', 'CHE': 'Switzerland',
        'UKR': 'Ukraine', 'GER': 'Germany', 'SUI': 'Switzerland',
        'SLO': 'Slovenia', 'ROM': 'Romania', 'BUL': 'Bulgaria',
        'BLG': 'Bulgaria', 'CRO': 'Croatia', 'MCD': 'North Macedonia',
        'ALB': 'Albania', 'GRE': 'Greece', 'LIE': 'Liechtenstein',
        'HUN': 'Hungary'
    }
    
    # Month names for opening hours
    MONTHS = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 
              'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
    
    @property
    def source_name(self) -> str:
        return "mountainhuts.info"
    
    @property
    def source_url(self) -> str:
        return "http://www.mountainhuts.info/map"
    
    @property
    def source_description(self) -> str:
        return "European mountain hut database with comprehensive management and contact details"
    
    def scrape(self) -> list:
        """
        Scrape huts from mountainhuts.info with comprehensive data extraction
        
        Array structure (50+ fields):
        [0] region, [1] lat, [2] lon, [3] altitude, [4] marker, [5] country,
        [6] year, [7] month, [8] day, [9] name_var, [10] name, [11] image,
        [12-16] capacity, [17-18] winter/review, [19] contact, [20] website,
        [21] phone, [22] email, [23-34] opening months, [35] languages,
        [36-39] services, [40] ad, [41] owner, [42] manager, [43+] amenities
        """
        print(f"Scraping {self.source_name}...")
        
        # Fetch the JavaScript file containing hut locations
        js_url = "http://www.mountainhuts.info/js/locations.js"
        response = requests.get(js_url, timeout=30)
        response.raise_for_status()
        
        js_content = response.text
        print(f"Downloaded {len(js_content)} characters of JavaScript data")
        
        # Parse the JavaScript array
        huts = self.parse_locations_array(js_content)
        
        print(f"Successfully scraped {len(huts)} huts from {self.source_name}")
        return huts
    
    def parse_locations_array(self, js_content: str) -> list:
        """Parse the complete locations array extracting all available fields"""
        huts = []
        
        # Find all array entries (lines starting with [)
        pattern = r'\[([^\]]+)\],'
        matches = re.finditer(pattern, js_content, re.MULTILINE | re.DOTALL)
        
        for match_num, match in enumerate(matches, 1):
            try:
                array_content = match.group(1)
                fields = self.smart_split(array_content)
                
                if len(fields) < 43:
                    print(f"Warning: Entry {match_num} has only {len(fields)} fields, skipping")
                    continue
                
                # Extract basic info
                latitude = self.clean_value(fields[1])
                longitude = self.clean_value(fields[2])
                altitude_str = self.clean_value(fields[3])
                country_code = self.clean_value(fields[5])
                name = self.clean_value(fields[10])
                
                # Extract update date
                year = self.clean_value(fields[6])
                month = self.clean_value(fields[7])
                day = self.clean_value(fields[8])
                last_update = f"{year}-{month.zfill(2)}-{day.zfill(2)}" if year and month and day else None
                
                # Extract contact information (use centralized cleaners)
                website = clean_url(self.clean_value(fields[20]))
                phone = clean_phone(self.clean_value(fields[21]))
                email = clean_email(self.clean_value(fields[22]))
                
                # Extract opening months (fields 23-34)
                opening_months = []
                for i, month_name in enumerate(self.MONTHS):
                    if i + 23 < len(fields):
                        month_field = fields[i + 23].strip().strip("'\"")
                        if month_field == 'y':
                            opening_months.append(month_name)
                
                opening_hours = ', '.join(opening_months) if opening_months else ''
                
                # Extract capacity information (fields 12-16)
                capacity_parts = []
                for i in [12, 13, 14, 15]:
                    if i < len(fields):
                        cap = self.clean_value(fields[i])
                        if cap and cap not in ['none', 'bedrooms', 'bunkrooms', '']:
                            # Remove variable names like 'person', 'bednumber', etc.
                            cap_clean = re.sub(r'\s*\+\s*\w+$', '', cap)
                            if cap_clean:
                                capacity_parts.append(cap_clean)
                
                capacity_str = ' | '.join(capacity_parts) if capacity_parts else ''
                
                # Extract owner and manager (fields 43 and 44)
                owner = self.clean_value(fields[43]) if len(fields) > 43 else ''
                manager = self.clean_value(fields[44]) if len(fields) > 44 else ''
                
                # Extract amenities/services
                amenities = []
                if len(fields) > 35:
                    languages = self.clean_value(fields[35])
                    if languages and languages not in ['pol', 'ger', 'cze']:
                        # Remove variable concatenations
                        lang_clean = re.sub(r'\s*\+\s*\'[^\']*\'\s*\+\s*', ' | ', languages)
                        if lang_clean:
                            amenities.append(f"Languages: {lang_clean}")
                
                # Additional service fields
                for i in range(43, min(len(fields), 55)):
                    service = self.clean_value(fields[i])
                    if service and service not in ['n', 'y', 'none', ''] and len(service) > 2:
                        # Skip variable names
                        if not service.islower() or ' ' in service:
                            amenities.append(service)
                
                amenities_str = ' | '.join(amenities) if amenities else ''
                
                # Convert country code
                country = self.COUNTRY_MAP.get(country_code, country_code)
                
                # Parse numeric values
                try:
                    altitude = int(altitude_str) if altitude_str else None
                except ValueError:
                    altitude = None
                
                try:
                    lat = float(latitude)
                    lon = float(longitude)
                except (ValueError, TypeError):
                    print(f"Warning: Invalid coordinates for {name}")
                    continue
                
                # Create source_id and individual page URL
                source_id = f"{lat}_{lon}"
                
                # Build individual hut page URL
                # Mountainhuts.info uses a detail page format with coordinates
                individual_url = f"http://www.mountainhuts.info/map?lat={lat}&lon={lon}&zoom=15"
                
                # Build hut dictionary
                hut = {
                    'source_id': source_id,
                    'name': name,
                    'latitude': lat,
                    'longitude': lon,
                    'altitude': altitude,
                    'country': None,  # Will be assigned by geolocation script based on coordinates
                    'hut_type': 'Mountain hut',
                    'website': website if website and website not in ['-', ''] else '',
                    'phone': phone if phone and phone not in ['-', ''] else '',
                    'email': email if email and email not in ['-', ''] else '',
                    'owner': owner if owner and owner not in ['manager', 'priv', ''] else '',
                    'manager': manager if manager and manager not in ['manager', 'n', ''] else '',
                    'opening_hours': opening_hours,
                    'capacity': None,
                    'description': capacity_str,
                    'amenities': amenities_str,
                    'url': individual_url,
                }
                
                # Add last update to description
                if last_update:
                    if hut['description']:
                        hut['description'] += f" | Last updated: {last_update}"
                    else:
                        hut['description'] = f"Last updated: {last_update}"
                
                huts.append(hut)
                
            except Exception as e:
                print(f"Error parsing entry {match_num}: {e}")
                continue
        
        return huts
    
    def smart_split(self, array_content: str) -> list:
        """Split array content by commas, handling quoted strings and expressions"""
        fields = []
        current_field = ""
        in_quotes = False
        quote_char = None
        paren_depth = 0
        
        i = 0
        while i < len(array_content):
            char = array_content[i]
            
            # Handle quotes
            if char in ["'", '"'] and (not in_quotes or char == quote_char):
                in_quotes = not in_quotes
                if in_quotes:
                    quote_char = char
                else:
                    quote_char = None
                current_field += char
            # Handle parentheses (for expressions)
            elif char == '(' and not in_quotes:
                paren_depth += 1
                current_field += char
            elif char == ')' and not in_quotes:
                paren_depth -= 1
                current_field += char
            # Handle commas
            elif char == ',' and not in_quotes and paren_depth == 0:
                fields.append(current_field.strip())
                current_field = ""
            else:
                current_field += char
            
            i += 1
        
        # Add the last field
        if current_field:
            fields.append(current_field.strip())
        
        return fields
    
    def clean_phone(self, value: str) -> str:
        """Clean phone number field (preserve + signs)"""
        if not value:
            return ''
        
        value = value.strip()
        
        # Remove quotes
        if (value.startswith("'") and value.endswith("'")) or \
           (value.startswith('"') and value.endswith('"')):
            value = value[1:-1]
        
        # If it doesn't start with +, it's probably not a phone number
        if value and not value.startswith('+') and value != '-':
            return ''
        
        return value.strip()
    
    def clean_value(self, value: str) -> str:
        """Clean and extract value from field"""
        if not value:
            return ''
        
        value = value.strip()
        
        # Remove quotes
        if (value.startswith("'") and value.endswith("'")) or \
           (value.startswith('"') and value.endswith('"')):
            value = value[1:-1]
        
        # Check if this is a simple variable name (no spaces, no special chars except underscore)
        # These should be ignored as they're JavaScript variables, not data
        if value and not any(c in value for c in [' ', '+', '|', '@', '.', '/', '-', '(', ')', ',', ':', ';']):
            # Check if it's all lowercase (typical JS variable naming)
            if value.islower() or value in ['priv', 'manager', 'none', 'contact', 'noreview', 
                                             'winterraum', 'bedrooms', 'bunkrooms', 'n', 'y']:
                return ''
        
        # Clean up concatenated strings (variable + string)
        value = re.sub(r'\'\s*\+\s*\'', '', value)
        value = re.sub(r'\s*\+\s*[a-z_]+\s*$', '', value)
        value = re.sub(r'^[a-z_]+\s*\+\s*', '', value)
        
        return value.strip()


def main():
    """Test the scraper"""
    scraper = MountainhutsInfoScraper()
    huts = scraper.scrape()
    
    if huts:
        print("\n=== Sample huts ===")
        for hut in huts[:5]:
            try:
                print(f"{hut['name']} ({hut['country']}) - {hut['altitude']}m at {hut['latitude']}, {hut['longitude']}")
            except:
                print(f"Hut at {hut['latitude']}, {hut['longitude']}")
        
        # Count by country
        countries = {}
        for hut in huts:
            country = hut.get('country', 'Unknown')
            countries[country] = countries.get(country, 0) + 1
        
        print("\n=== Country distribution ===")
        for country, count in sorted(countries.items(), key=lambda x: x[1], reverse=True):
            print(f"{country}: {count} huts")


if __name__ == "__main__":
    main()
