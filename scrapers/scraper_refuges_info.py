"""
Scraper for refuges.info - Mountain huts across Europe

This scraper uses the refuges.info API to retrieve comprehensive data about
mountain huts, cabins, and shelters. The site has 8,266+ points with rich data.

Data source: https://www.refuges.info/
API documentation: https://www.refuges.info/api/doc/
License: CC By-Sa 2.0

Author: Mountain Huts Europe
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import json
import time
import re
from database import MountainHutsDatabase

# French to English translations for common terms
TRANSLATIONS = {
    # Types
    'cabane': 'Unmanned cabin',
    'refuge': 'Staffed refuge',
    'gîte': 'Guesthouse',
    'bivouac': 'Bivouac',
    
    # Equipment/Facilities
    'matelas': 'mattresses',
    'couvertures': 'blankets',
    'poêle': 'stove',
    'cheminée': 'fireplace',
    'bois sur place': 'wood on site',
    'eau à proximité': 'water nearby',
    
    # Common phrases
    'Équipements': 'Equipment',
    'Accès': 'Access',
    'Description': 'Description',
    'places': 'beds',
    'gardé': 'staffed',
    'non gardé': 'unstaffed',
    
    # Access terms
    'à pied': 'on foot',
    'en voiture': 'by car',
    'téléphérique': 'cable car',
    'sentier': 'trail',
    'chemin': 'path',
    'route': 'road',
    'parking': 'parking',
    'heures': 'hours',
    'minutes': 'minutes',
    'dénivelé': 'elevation gain',
    'difficulté': 'difficulty',
    'facile': 'easy',
    'moyen': 'moderate',
    'difficile': 'difficult'
}

def translate_text(text):
    """Translate French text to English using simple dictionary replacement"""
    if not text:
        return text
    
    translated = text
    for fr, en in TRANSLATIONS.items():
        # Use word boundaries to avoid partial matches
        translated = re.sub(r'\b' + re.escape(fr) + r'\b', en, translated, flags=re.IGNORECASE)
    
    return translated

class RefugesInfoScraper:
    def __init__(self):
        self.base_url = "https://www.refuges.info/api"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'MountainHutsEurope/1.0 (Educational project)'
        })
        self.db = MountainHutsDatabase()
        
    def get_all_points(self):
        """
        Fetch all points from refuges.info API using bbox=world
        Focus on cabane, refuge, and gite types
        """
        print("🔄 Fetching all mountain huts from refuges.info API...")
        
        url = f"{self.base_url}/bbox"
        params = {
            'bbox': 'world',  # Get all points worldwide
            'type_points': 'cabane,refuge,gite',  # Only huts, refuges, and gites
            'nb_points': 'all',  # Get all points
            'format': 'geojson',
            'detail': 'complet'  # Get complete information
        }
        
        try:
            print(f"📡 Requesting: {url}")
            print(f"   Parameters: {params}")
            
            response = self.session.get(url, params=params, timeout=60)
            response.raise_for_status()
            
            data = response.json()
            
            if 'features' in data:
                print(f"✅ Retrieved {len(data['features'])} points from API")
                return data['features']
            else:
                print(f"❌ Unexpected response format")
                return []
                
        except Exception as e:
            print(f"❌ Error fetching data: {e}")
            return []
    
    def parse_point(self, feature):
        """
        Parse a GeoJSON feature from refuges.info API
        Extract all available information and translate to English
        """
        try:
            properties = feature.get('properties', {})
            geometry = feature.get('geometry', {})
            coordinates = geometry.get('coordinates', [])
            
            if len(coordinates) < 2:
                return None
            
            # Basic information
            name = properties.get('nom', '').strip()
            if not name:
                return None
            
            # Coordinates (refuges.info uses [lon, lat] format)
            longitude = coordinates[0]
            latitude = coordinates[1]
            altitude = coordinates[2] if len(coordinates) > 2 else None
            
            # Type mapping with English translations
            type_map = {
                'cabane': 'Unmanned cabin',
                'refuge': 'Staffed refuge',
                'gite': 'Guesthouse',
                'bivouac': 'Bivouac shelter'
            }
            hut_type = type_map.get(properties.get('type', {}).get('valeur', ''), None)
            
            # Owner/Manager information
            owner = None
            if properties.get('createur'):
                creator_nom = properties['createur'].get('nom')
                if creator_nom:
                    creator = str(creator_nom).strip()
                    if creator and creator != 'NULL':
                        owner = creator
            
            # Capacity information
            capacity = None
            if properties.get('places'):
                try:
                    places = properties['places'].get('valeur')
                    if places and places != 'NULL':
                        capacity = int(places)
                except:
                    pass
            
            # Contact and booking information
            phone = None
            if properties.get('telephone'):
                phone = properties['telephone'].get('valeur', '').strip()
            
            website = None
            if properties.get('site_web'):
                website = properties['site_web'].get('valeur', '').strip()
            
            # Additional details
            matelas = properties.get('matelas', {}).get('valeur') == '1' if properties.get('matelas') else None
            couvertures = properties.get('couvertures', {}).get('valeur') == '1' if properties.get('couvertures') else None
            poele = properties.get('poele', {}).get('valeur') == '1' if properties.get('poele') else None
            cheminee = properties.get('cheminee', {}).get('valeur') == '1' if properties.get('cheminee') else None
            bois = properties.get('bois_sur_place', {}).get('valeur') == '1' if properties.get('bois_sur_place') else None
            eau = properties.get('eau_a_proximite', {}).get('valeur') == '1' if properties.get('eau_a_proximite') else None
            
            # Build facilities description (translated to English)
            facilities = []
            if matelas:
                facilities.append("mattresses available")
            if couvertures:
                facilities.append("blankets provided")
            if poele:
                facilities.append("stove available")
            if cheminee:
                facilities.append("fireplace")
            if bois:
                facilities.append("wood on site")
            if eau:
                facilities.append("water nearby")
            
            facilities_str = ", ".join(facilities) if facilities else None
            
            # Description/comments (translate to English)
            description = None
            if properties.get('description'):
                desc_text = properties['description'].get('valeur', '').strip()
                if desc_text and desc_text != 'NULL':
                    description = translate_text(desc_text)
            
            # Access information (translate to English)
            access_info = None
            if properties.get('acces'):
                access_text = properties['acces'].get('valeur', '').strip()
                if access_text and access_text != 'NULL':
                    access_info = translate_text(access_text)
            
            # Remarques (additional remarks/comments)
            remarks = None
            if properties.get('remarques'):
                remarks_text = properties['remarques'].get('valeur', '').strip()
                if remarks_text and remarks_text != 'NULL':
                    remarks = translate_text(remarks_text)
            
            # Combine all information into comments field
            comments = []
            if description:
                comments.append(f"Description: {description}")
            if access_info:
                comments.append(f"Access: {access_info}")
            if facilities_str:
                comments.append(f"Equipment: {facilities_str}")
            if remarks:
                comments.append(f"Remarks: {remarks}")
            
            comments_str = " | ".join(comments) if comments else None
            
            # URL to the point on refuges.info
            point_id = properties.get('id')
            url = f"https://www.refuges.info/point/{point_id}/" if point_id else None
            
            # Create comprehensive hut data
            hut_data = {
                'source_id': str(point_id) if point_id else None,
                'name': name,
                'latitude': latitude,
                'longitude': longitude,
                'altitude': altitude,
                'capacity': capacity,
                'type_description': hut_type,
                'phone': phone if phone and phone != 'NULL' else None,
                'website': website if website and website != 'NULL' else None,
                'owner': owner if owner and owner != 'NULL' else None,
                'comments': comments_str,
                'description': description[:500] if description else None,  # Limit description length
                'access': access_info[:500] if access_info else None,  # Store translated access separately
                'amenities': facilities_str,
                'url': url
            }
            
            return hut_data
            
        except Exception as e:
            print(f"⚠️  Error parsing point: {e}")
            return None
    
    def scrape(self):
        """
        Main scraping function
        """
        print("=" * 70)
        print("🏔️  REFUGES.INFO SCRAPER")
        print("=" * 70)
        print()
        
        # Get all points
        features = self.get_all_points()
        
        if not features:
            print("❌ No data retrieved. Exiting.")
            return
        
        print(f"\n📊 Processing {len(features)} points...")
        print()
        
        # Parse and insert into database
        inserted = 0
        skipped = 0
        errors = 0
        
        for i, feature in enumerate(features, 1):
            try:
                # Parse the point
                hut_data = self.parse_point(feature)
                
                if not hut_data:
                    skipped += 1
                    continue
                
                # Save to database
                success = self.db.save_hut(hut_data, 'refuges.info')
                
                if success:
                    inserted += 1
                    if inserted % 100 == 0:
                        print(f"✅ Processed {inserted} huts...")
                else:
                    skipped += 1
                
                # Rate limiting - be respectful
                if i % 100 == 0:
                    time.sleep(0.5)
                    
            except Exception as e:
                errors += 1
                print(f"❌ Error processing point {i}: {e}")
                continue
        
        print()
        print("=" * 70)
        print("📊 SCRAPING SUMMARY")
        print("=" * 70)
        print(f"✅ Successfully inserted: {inserted} huts")
        print(f"⏭️  Skipped (duplicates/invalid): {skipped}")
        print(f"❌ Errors: {errors}")
        print(f"📝 Total processed: {len(features)}")
        print()
        
        # Show database statistics
        print("=" * 70)
        print("📊 DATABASE STATISTICS")
        print("=" * 70)
        self.db.get_statistics()
        print()
        
        print("✅ Scraping complete!")
        print()

def main():
    scraper = RefugesInfoScraper()
    scraper.scrape()

if __name__ == '__main__':
    main()
