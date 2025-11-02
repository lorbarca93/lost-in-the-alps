"""
Scraper for boudy.info
Mountain huts database covering Czech Republic, Slovakia, Alps region
"""

from base_scraper import BaseScraper
from typing import List, Dict
import time
import json


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
                    
                    # Extract coordinates (GeoJSON is [lon, lat])
                    # IMPORTANT: GeoJSON coordinates are [longitude, latitude]
                    if len(coords) >= 2:
                        hut_data['latitude'] = float(coords[1])   # Second value is latitude
                        hut_data['longitude'] = float(coords[0])  # First value is longitude
                    
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
                        # Normalize the data
                        normalized = self.normalize_hut_data(hut)
                        all_huts.append(normalized)
                
                time.sleep(0.5)  # Be polite to the server
                
                lon += grid_size
            lat += grid_size
        
        print(f"\nTotal unique huts found: {len(all_huts)}")
        return all_huts


if __name__ == "__main__":
    scraper = BoudyInfoScraper()
    scraper.run()
