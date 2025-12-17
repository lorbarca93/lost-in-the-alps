"""
Scraper for SAT.tn.it (Società degli Alpinisti Tridentini)
Covers mountain huts (Rifugi SAT) and bivouacs (Bivacchi) in Trentino, Italy
Data source: Interactive map with GeoJSON data
"""

from base_scraper import BaseScraper
import json
from typing import List, Dict
import time


class SatTnItScraper(BaseScraper):
    """Scraper for SAT.tn.it covering Rifugi SAT and Bivacchi in Trentino"""
    
    # GeoJSON endpoints
    RIFUGI_GEOJSON_URL = "https://k.webmapp.it/trentino/geojson/rifugi_webapp.geojson"
    BIVACCHI_GEOJSON_URL = "https://k.webmapp.it/trentino/geojson/bivacchi_webapp.geojson"
    PUNTI_APPOGGIO_GEOJSON_URL = "https://k.webmapp.it/trentino/geojson/punti_appoggio.geojson"
    
    @property
    def source_name(self) -> str:
        return "sat.tn.it"
    
    @property
    def source_url(self) -> str:
        return "https://www.sat.tn.it/rifugi/mappa-rifugi-e-bivacchi/"
    
    @property
    def source_description(self) -> str:
        return "SAT (Società degli Alpinisti Tridentini) mountain huts and bivouacs in Trentino, Italy"
    
    def scrape(self) -> List[Dict]:
        """
        Scrape Rifugi SAT and Bivacchi from GeoJSON endpoints
        """
        self.logger.info(f"Starting to scrape {self.source_name}...")
        all_huts = []
        
        # Scrape Rifugi SAT
        try:
            self.logger.info(f"Fetching Rifugi SAT from {self.RIFUGI_GEOJSON_URL}")
            rifugi = self._scrape_geojson(self.RIFUGI_GEOJSON_URL, hut_type="Staffed Hut")
            all_huts.extend(rifugi)
            self.logger.info(f"Found {len(rifugi)} Rifugi SAT")
        except Exception as e:
            self.logger.error(f"Error scraping Rifugi SAT: {e}", exc_info=True)
        
        # Small delay between requests
        time.sleep(0.5)
        
        # Small delay between requests
        time.sleep(0.5)
        
        # Scrape Bivacchi
        try:
            self.logger.info(f"Fetching Bivacchi from {self.BIVACCHI_GEOJSON_URL}")
            bivacchi = self._scrape_geojson(self.BIVACCHI_GEOJSON_URL, hut_type="Bivouac")
            all_huts.extend(bivacchi)
            self.logger.info(f"Found {len(bivacchi)} Bivacchi")
        except Exception as e:
            self.logger.error(f"Error scraping Bivacchi: {e}", exc_info=True)
        
        # Small delay between requests
        time.sleep(0.5)
        
        # Scrape additional Rifugi/Bivacchi from punti_appoggio (excluding pure hotels)
        try:
            self.logger.info(f"Fetching additional Rifugi/Bivacchi from {self.PUNTI_APPOGGIO_GEOJSON_URL}")
            # Get names already scraped to avoid duplicates
            existing_names = {hut.get('name', '').lower().strip() for hut in all_huts}
            additional = self._scrape_punti_appoggio(existing_names)
            all_huts.extend(additional)
            self.logger.info(f"Found {len(additional)} additional Rifugi/Bivacchi from punti_appoggio")
        except Exception as e:
            self.logger.error(f"Error scraping punti_appoggio: {e}", exc_info=True)
        
        self.logger.info(f"Total huts scraped: {len(all_huts)}")
        return all_huts
    
    def _scrape_geojson(self, url: str, hut_type: str) -> List[Dict]:
        """
        Fetch and parse a GeoJSON file
        
        Args:
            url: URL to the GeoJSON file
            hut_type: Type to assign to huts from this file
            
        Returns:
            List of hut dictionaries
        """
        huts = []
        
        # Fetch the GeoJSON file
        response = self.session.get(url, timeout=30)
        response.raise_for_status()
        
        # Parse JSON
        geojson_data = response.json()
        
        # Validate GeoJSON structure
        if not isinstance(geojson_data, dict) or geojson_data.get('type') != 'FeatureCollection':
            self.logger.warning(f"Unexpected GeoJSON structure from {url}")
            return huts
        
        features = geojson_data.get('features', [])
        self.logger.info(f"Found {len(features)} features in GeoJSON")
        
        # Process each feature
        for feature in features:
            try:
                hut = self._parse_feature(feature, hut_type)
                if hut:
                    huts.append(hut)
            except Exception as e:
                self.logger.warning(f"Error parsing feature: {e}")
                continue
        
        return huts
    
    def _parse_feature(self, feature: Dict, hut_type: str) -> Dict:
        """
        Parse a GeoJSON feature into a hut dictionary
        
        Args:
            feature: GeoJSON feature object
            hut_type: Type to assign to this hut
            
        Returns:
            Hut dictionary or None if invalid
        """
        if not isinstance(feature, dict) or feature.get('type') != 'Feature':
            return None
        
        geometry = feature.get('geometry', {})
        properties = feature.get('properties', {})
        
        # Extract coordinates (GeoJSON format: [longitude, latitude])
        coords = geometry.get('coordinates', [])
        if not coords or len(coords) < 2:
            self.logger.debug("Feature missing coordinates, skipping")
            return None
        
        longitude = float(coords[0])
        latitude = float(coords[1])
        
        # Validate coordinates (Trentino region roughly: 45.5-47°N, 10.5-12.5°E)
        if not (45.5 <= latitude <= 47.0) or not (10.5 <= longitude <= 12.5):
            self.logger.debug(f"Coordinates out of expected range: {latitude}, {longitude}")
            # Still include it, but log the warning
        
        # Extract name (try multiple possible property names)
        name = (
            properties.get('name') or 
            properties.get('nome') or 
            properties.get('title') or 
            properties.get('titolo') or
            properties.get('Name') or
            ''
        ).strip()
        
        if not name:
            # Try to use feature ID as fallback
            feature_id = feature.get('id') or properties.get('id')
            if feature_id:
                name = f"{hut_type} {feature_id}"
            else:
                self.logger.debug("Feature missing name, skipping")
                return None
        
        # Build hut dictionary
        hut = {
            'source_id': str(properties.get('id') or feature.get('id') or name),
            'name': name,
            'latitude': latitude,
            'longitude': longitude,
            'type': hut_type,
            'country': 'Italy',
            'region': 'Trentino',
        }
        
        # Extract altitude (try multiple property names, including 'ele' which is common in GeoJSON)
        altitude = (
            properties.get('ele') or  # Common GeoJSON property for elevation
            properties.get('altitude') or 
            properties.get('altitudine') or 
            properties.get('elevation') or
            properties.get('quota') or
            properties.get('alt')
        )
        if altitude:
            try:
                hut['altitude'] = int(float(altitude))
            except (ValueError, TypeError):
                pass
        
        # Extract description
        description = (
            properties.get('description') or 
            properties.get('descrizione') or
            properties.get('desc') or
            properties.get('note') or
            properties.get('note_webapp')
        )
        if description:
            hut['description'] = str(description).strip()
        
        # Extract URL if available (check related_url first, then website, then url)
        url = None
        related_urls = properties.get('related_url')
        if related_urls and isinstance(related_urls, list) and len(related_urls) > 0:
            url = related_urls[0]
        elif not url:
            url = (
                properties.get('website') or 
                properties.get('url') or 
                properties.get('link') or
                properties.get('web')
            )
        
        if url:
            # Ensure URL is complete
            url_str = str(url).strip()
            if url_str.startswith('http://') or url_str.startswith('https://'):
                hut['url'] = url_str
            elif url_str.startswith('www.'):
                hut['url'] = f"https://{url_str}"
            elif url_str.startswith('/'):
                hut['url'] = f"https://www.sat.tn.it{url_str}"
            else:
                hut['url'] = f"https://www.sat.tn.it/{url_str}"
        
        # Extract capacity if available
        capacity = properties.get('capacity') or properties.get('capacita') or properties.get('posti')
        if capacity:
            try:
                hut['capacity'] = int(float(capacity))
            except (ValueError, TypeError):
                pass
        
        # Extract phone if available
        phone = properties.get('phone') or properties.get('telefono') or properties.get('tel')
        if phone:
            hut['phone'] = str(phone).strip()
        
        # Extract email if available
        email = properties.get('email') or properties.get('mail')
        if email:
            hut['email'] = str(email).strip()
        
        # Extract opening hours if available
        opening = (
            properties.get('opening_hours') or 
            properties.get('orari') or 
            properties.get('apertura') or
            properties.get('season') or
            properties.get('stagione')
        )
        if opening:
            hut['opening_hours'] = str(opening).strip()
        
        # Normalize the data using base class method
        return self.normalize_hut_data(hut)
    
    def _scrape_punti_appoggio(self, existing_names: set) -> List[Dict]:
        """
        Scrape punti_appoggio.geojson for additional Rifugi and Bivacchi
        Filters out pure hotels (Albergo without Rifugio) and duplicates
        
        Args:
            existing_names: Set of lowercase names already scraped (to avoid duplicates)
            
        Returns:
            List of additional hut dictionaries
        """
        huts = []
        
        # Fetch the GeoJSON file
        response = self.session.get(self.PUNTI_APPOGGIO_GEOJSON_URL, timeout=30)
        response.raise_for_status()
        
        # Parse JSON
        geojson_data = response.json()
        
        # Validate GeoJSON structure
        if not isinstance(geojson_data, dict) or geojson_data.get('type') != 'FeatureCollection':
            self.logger.warning(f"Unexpected GeoJSON structure from {self.PUNTI_APPOGGIO_GEOJSON_URL}")
            return huts
        
        features = geojson_data.get('features', [])
        self.logger.info(f"Found {len(features)} features in punti_appoggio")
        
        # Process each feature
        for feature in features:
            try:
                props = feature.get('properties', {})
                name = (props.get('name') or '').strip()
                name_lower = name.lower()
                desc = (props.get('description') or '').lower() if props.get('description') else ''
                
                # Skip if already in our list
                if name_lower in existing_names:
                    continue
                
                # Skip pure hotels (Albergo without Rifugio/Bivacco)
                if 'albergo' in name_lower and 'rifugio' not in name_lower and 'bivacco' not in name_lower:
                    continue
                
                # Check if it's a Rifugio or Bivacco
                is_rifugio = 'rifugio' in name_lower or 'rifugio' in desc
                is_bivacco = 'bivacco' in name_lower or 'bivacco' in desc
                
                # Also check for "baita" which might be a mountain hut
                is_baita = 'baita' in name_lower and ('rifugio' in desc or 'bivacco' in desc)
                
                if is_rifugio or is_bivacco or is_baita:
                    # Determine hut type
                    if is_bivacco:
                        hut_type = "Bivouac"
                    elif is_rifugio or is_baita:
                        # For Albergo/Rifugio combos, still classify as Staffed Hut
                        hut_type = "Staffed Hut"
                    else:
                        continue
                    
                    # Parse the feature
                    hut = self._parse_feature(feature, hut_type)
                    if hut:
                        huts.append(hut)
                        # Add to existing names to avoid duplicates within this file
                        existing_names.add(name_lower)
                        
            except Exception as e:
                self.logger.warning(f"Error parsing punti_appoggio feature: {e}")
                continue
        
        return huts


# Example usage:
if __name__ == "__main__":
    scraper = SatTnItScraper()
    scraper.run()

