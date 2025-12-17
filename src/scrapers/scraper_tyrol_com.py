"""
Scraper for Tyrol Tourism Alpine Club Huts
Website: https://www.tyrol.com/activities/sport/hiking/refuge-huts/all-huts

This scraper fetches Alpine Club huts in Tyrol, Austria from the official Tyrol tourism website.
It provides data about huts in various mountain groups including coordinates, altitude, and amenities.
"""

from typing import List, Dict
from bs4 import BeautifulSoup
import re
import json
from base_scraper_v2 import BaseScraperV2


class TyrolComScraper(BaseScraperV2):
    """Scraper for Tyrol Tourism Alpine Club Huts"""
    
    @property
    def source_name(self) -> str:
        return "tyrol.com"
    
    @property
    def source_url(self) -> str:
        return "https://www.tyrol.com"
    
    @property
    def source_description(self) -> str:
        return "Official Tyrol Tourism website listing Alpine Club huts in Tyrol, Austria"
    
    def scrape(self) -> List[Dict]:
        """
        Main scraping logic
        
        The website has a map view that contains ALL huts in a single data-markers JSON attribute.
        This is much easier and faster than pagination!
        """
        
        self.logger.info("Starting to scrape tyrol.com Alpine Club huts...")
        all_huts = []
        
        # Base URL
        base_url = "https://www.tyrol.com/activities/sport/hiking/refuge-huts/all-huts"
        
        try:
            # Fetch the main page
            self.logger.info("Fetching main page with map data...")
            response = self.get_with_retry(base_url)
            
            # Parse the HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # First, build a mapping of hut names to their actual URLs
            self.logger.info("Building name-to-URL mapping from page links...")
            name_to_url = self._build_url_mapping(soup)
            self.logger.info(f"Found {len(name_to_url)} hut URLs")
            
            # Find the element with data-markers attribute (contains all huts in JSON)
            map_element = soup.find(attrs={'data-markers': True})
            
            if not map_element:
                self.logger.error("Could not find map element with data-markers attribute")
                return []
            
            # Extract and parse the JSON data
            markers_json = map_element.get('data-markers', '[]')
            
            try:
                markers_data = json.loads(markers_json)
                self.logger.info(f"Found {len(markers_data)} huts in map data")
            except json.JSONDecodeError as e:
                self.logger.error(f"Failed to parse markers JSON: {e}")
                return []
            
            # Process each marker
            for marker in markers_data:
                try:
                    hut = self.parse_marker_data(marker, name_to_url)
                    if hut:
                        # Fetch additional details if critical fields are missing
                        needs_details = (
                            not hut.get('altitude') or 
                            not hut.get('description')
                        )
                        
                        if needs_details and hut.get('url'):
                            try:
                                self.logger.debug(f"Fetching details for {hut['name']}")
                                details = self.fetch_hut_details(hut['url'])
                                if details:
                                    hut.update(details)
                            except Exception as e:
                                self.logger.warning(f"Could not fetch details for {hut['name']}: {e}")
                        
                        all_huts.append(hut)
                except Exception as e:
                    self.logger.warning(f"Error parsing marker: {e}")
                    continue
            
            self.logger.info(f"Successfully scraped {len(all_huts)} huts from tyrol.com")
            
        except Exception as e:
            self.logger.error(f"Error scraping tyrol.com: {e}")
        
        return all_huts
    
    def _build_url_mapping(self, soup: BeautifulSoup) -> Dict[str, str]:
        """
        Build a mapping of hut names to their actual URLs from the page
        Uses pagination to load ALL huts and extract their URLs
        
        Args:
            soup: BeautifulSoup object of the main page
        
        Returns:
            Dictionary mapping normalized hut names to their URLs
        """
        name_to_url = {}
        
        # Start with the first page (already loaded)
        self._extract_urls_from_page(soup, name_to_url)
        
        # Now load remaining pages via pagination API
        # listpos is simply a page number: 1, 2, 3, 4...
        base_url = "https://www.tyrol.com/activities/sport/hiking/refuge-huts/all-huts"
        max_pages = 15  # Safety limit (162 huts / 18 per page = 9 pages, but give extra room)
        
        for page_num in range(2, max_pages + 1):
            try:
                url = f"{base_url}?listpos={page_num}&type=1000&extension=content"
                response = self.get_with_retry(url)
                
                # Parse JSON/HTML response
                try:
                    json_data = response.json()
                    # The JSON has structure: {'content': {'content': '<html>', ...}, ...}
                    content_obj = json_data.get('content', {})
                    if isinstance(content_obj, dict):
                        html_content = content_obj.get('content', '') or content_obj.get('html', '') or response.text
                    else:
                        html_content = response.text
                except (ValueError, json.JSONDecodeError):
                    html_content = response.text
                
                page_soup = BeautifulSoup(html_content, 'html.parser')
                
                # Extract URLs from this page
                urls_found = self._extract_urls_from_page(page_soup, name_to_url)
                self.logger.info(f"  Page {page_num} (listpos={page_num}): found {urls_found} new URLs (total: {len(name_to_url)})")
                
                if urls_found == 0:
                    # No more huts
                    self.logger.info("  No more huts found, stopping pagination")
                    break
                
            except Exception as e:
                self.logger.warning(f"Error loading page {page_num} for URL mapping: {e}")
                break
        
        return name_to_url
    
    def _extract_urls_from_page(self, soup: BeautifulSoup, name_to_url: Dict[str, str]) -> int:
        """
        Extract hut URLs from a page and add to the mapping
        
        Args:
            soup: BeautifulSoup object of the page
            name_to_url: Dictionary to update with found URLs
        
        Returns:
            Number of URLs found on this page
        """
        count = 0
        
        # Find all article elements with hut links
        articles = soup.find_all('article')
        
        for article in articles:
            # Find the link
            link = article.find('a', href=re.compile(r'/refuge-huts/all-huts/[^/]+$'))
            if not link:
                continue
            
            href = link.get('href', '')
            if not href or '/all-huts/' not in href:
                continue
            
            # Find the hut name in the heading
            heading = article.find(['h1', 'h2', 'h3', 'h4'])
            if not heading:
                continue
            
            name = heading.get_text(strip=True)
            
            # Build full URL
            if href.startswith('/'):
                url = f"{self.source_url}{href}"
            else:
                url = href
            
            # Store with normalized name as key (for matching)
            normalized_name = name.strip()
            if normalized_name not in name_to_url:
                name_to_url[normalized_name] = url
                count += 1
        
        return count
    
    def parse_marker_data(self, marker: Dict, name_to_url: Dict[str, str]) -> Dict:
        """
        Parse a single marker from the map data
        
        Args:
            marker: Dictionary containing marker data
            name_to_url: Mapping of hut names to their actual URLs
        
        Returns:
            Dictionary with hut data
        """
        hut = {}
        
        # Extract name
        hut['name'] = marker.get('title', 'Unknown')
        
        # Extract coordinates
        latlng = marker.get('latlng', [])
        if len(latlng) == 2:
            hut['latitude'] = float(latlng[0])
            hut['longitude'] = float(latlng[1])
        
        # Extract identifier
        ident = marker.get('ident', '')
        if ident:
            hut['source_id'] = f"tyrol_{ident}"
        else:
            # Fallback: use slugified name
            slug = hut['name'].lower().replace(' ', '-').replace('ü', 'ue').replace('ö', 'oe').replace('ä', 'ae')
            hut['source_id'] = f"tyrol_{slug}"
        
        # NEW: Try to extract altitude from marker if available
        if 'altitude' in marker:
            hut['altitude'] = marker.get('altitude')
        elif 'elevation' in marker:
            hut['altitude'] = marker.get('elevation')
        elif 'height' in marker:
            hut['altitude'] = marker.get('height')
        elif 'alt' in marker:
            hut['altitude'] = marker.get('alt')
        
        # NEW: Try to extract description from marker if available
        if 'description' in marker:
            hut['description'] = marker.get('description')
        elif 'text' in marker:
            hut['description'] = marker.get('text')
        elif 'info' in marker:
            hut['description'] = marker.get('info')
        
        # Get the actual URL from our mapping (much more reliable!)
        actual_url = name_to_url.get(hut['name'])
        if actual_url:
            hut['url'] = actual_url
        else:
            # Fallback: try to generate it (though this might not be correct)
            self.logger.warning(f"Could not find URL for hut: {hut['name']}, using generated URL")
            slug = hut['name'].lower().replace(' ', '-').replace('ü', 'ue').replace('ö', 'oe').replace('ä', 'ae')
            hut['url'] = f"{self.source_url}/activities/sport/hiking/refuge-huts/all-huts/{slug}"
        
        # Set country (all Tyrol huts are in Austria)
        hut['country'] = 'Austria'
        
        # Set hut type
        hut['hut_type'] = 'Mountain Hut'
        
        # Normalize the data
        return self.normalize_hut_data(hut)
    
    def parse_hut_item(self, item) -> Dict:
        """
        Parse a single hut item from the page
        
        Args:
            item: BeautifulSoup element containing hut data
        
        Returns:
            Dictionary with hut data
        """
        hut = {}
        
        # Extract link (contains slug/ID)
        link = item.find('a', href=True)
        if link:
            href = link.get('href', '')
            if href.startswith('/'):
                hut['url'] = f"{self.source_url}{href}"
            else:
                hut['url'] = href
            
            # Extract ID from URL
            # Format: /activities/sport/hiking/refuge-huts/ackerlhuette
            match = re.search(r'/refuge-huts/([^/?]+)', href)
            if match:
                hut['source_id'] = f"tyrol_{match.group(1)}"
            else:
                # Fallback: use the entire href as ID
                hut['source_id'] = f"tyrol_{href.replace('/', '_').strip('_')}"
        else:
            # If no link, skip this item
            return None
        
        # Extract name
        name_elem = item.find(['h1', 'h2', 'h3', 'h4', 'strong', 'span'], class_=re.compile(r'title|name|heading', re.I))
        if not name_elem:
            name_elem = item.find(['h1', 'h2', 'h3', 'h4'])
        
        if name_elem:
            hut['name'] = name_elem.get_text(strip=True)
        else:
            # Try to get from link text
            if link:
                hut['name'] = link.get_text(strip=True)
        
        if not hut.get('name'):
            return None
        
        # Extract altitude (height)
        altitude_elem = item.find(text=re.compile(r'\d+\s*m', re.I))
        if altitude_elem:
            altitude_match = re.search(r'(\d+)\s*m', altitude_elem)
            if altitude_match:
                hut['altitude'] = int(altitude_match.group(1))
        
        # Extract mountain group / region
        region_elem = item.find(['span', 'div', 'p'], class_=re.compile(r'region|location|place', re.I))
        if region_elem:
            hut['region'] = region_elem.get_text(strip=True)
        
        # Extract suitable activities (convert to amenities)
        activities = []
        activity_elements = item.find_all(['span', 'div'], class_=re.compile(r'suitable|activity', re.I))
        for act in activity_elements:
            activities.append(act.get_text(strip=True))
        
        if activities:
            hut['amenities'] = ', '.join(activities)
        
        # Set country to Austria (all Tyrol huts are in Austria)
        hut['country'] = 'Austria'
        
        # Set hut type (most are mountain huts)
        hut['hut_type'] = 'Mountain Hut'
        
        # Extract image URL
        img = item.find('img', src=True)
        if img:
            img_src = img.get('src', '')
            if img_src:
                if img_src.startswith('//'):
                    hut['image_url'] = f"https:{img_src}"
                elif img_src.startswith('/'):
                    hut['image_url'] = f"{self.source_url}{img_src}"
                else:
                    hut['image_url'] = img_src
        
        # Normalize the data
        return self.normalize_hut_data(hut)
    
    def fetch_hut_details(self, hut_url: str) -> Dict:
        """
        Fetch detailed information for a single hut
        
        Args:
            hut_url: URL to the hut's detail page
        
        Returns:
            Dictionary with additional hut details
        """
        try:
            response = self.get_with_retry(hut_url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            details = {}
            
            # Extract contact information
            email_elem = soup.find('a', href=re.compile(r'mailto:', re.I))
            if email_elem:
                email = email_elem.get('href', '').replace('mailto:', '').strip()
                details['email'] = email
            
            phone_elem = soup.find('a', href=re.compile(r'tel:', re.I))
            if phone_elem:
                phone = phone_elem.get('href', '').replace('tel:', '').strip()
                details['phone'] = phone
            
            # Extract website
            website_elem = soup.find('a', href=re.compile(r'^https?://', re.I), string=re.compile(r'website|homepage', re.I))
            if website_elem:
                details['website'] = website_elem.get('href', '')
            
            # Extract GPS coordinates (only if not already present)
            # Skip this - coordinates should already be in marker data
            # Trying to parse from text can cause errors
            
            # Extract description - try multiple approaches
            desc_elem = soup.find(['div', 'p'], class_=re.compile(r'description|content|text', re.I))
            if desc_elem:
                details['description'] = desc_elem.get_text(strip=True)[:1000]
            else:
                # Try to find any paragraph with substantial text
                paragraphs = soup.find_all('p')
                for p in paragraphs:
                    text = p.get_text(strip=True)
                    if len(text) > 50:  # Substantial text
                        details['description'] = text[:1000]
                        break
            
            # Extract altitude - look for altitude/elevation in text
            altitude_pattern = re.compile(r'(\d+)\s*m\s*(?:ü\.?M\.?|über\s*Meer|above\s*sea|altitude|elevation)', re.I)
            page_text = soup.get_text()
            alt_match = altitude_pattern.search(page_text)
            if alt_match:
                details['altitude'] = int(alt_match.group(1))
            else:
                # Try simpler pattern
                simple_alt = re.search(r'(\d{3,4})\s*m\b', page_text, re.I)
                if simple_alt:
                    alt_val = int(simple_alt.group(1))
                    if 500 < alt_val < 4000:  # Reasonable altitude range
                        details['altitude'] = alt_val
            
            # Extract capacity if available
            capacity_pattern = re.compile(r'(\d+)\s*(?:places|beds|bunks|capacity|Betten|Plätze)', re.I)
            cap_match = capacity_pattern.search(page_text)
            if cap_match:
                details['capacity'] = int(cap_match.group(1))
            
            return details
            
        except Exception as e:
            self.logger.warning(f"Could not fetch details for {hut_url}: {e}")
            return {}


if __name__ == '__main__':
    # Run the scraper
    scraper = TyrolComScraper(
        rate_limit=5.0,  # Be respectful: 5 requests per second max
        max_retries=3
    )
    scraper.run()

