#!/usr/bin/env python3
"""
Comprehensive analysis of hut types from refuges.info
"""
import requests

def analyze_french_types():
    url = 'https://www.refuges.info/api/bbox'
    
    # All possible type_points on refuges.info
    type_points_list = ['cabane', 'refuge', 'bivouac', 'gite']
    
    all_types = {}
    
    print("=" * 70)
    print("REFUGES.INFO HUT TYPE ANALYSIS")
    print("=" * 70)
    
    for type_points in type_points_list:
        params = {
            'bbox': 'world',
            'type_points': type_points,
            'nb_points': '10000',  # Get all
            'format': 'geojson',
            'detail': 'simple'
        }
        
        print(f"\nFetching type_points='{type_points}'...")
        
        try:
            resp = requests.get(url, params=params, timeout=60)
            data = resp.json()
            
            # Count types
            type_counts = {}
            for feature in data.get('features', []):
                props = feature['properties']
                type_info = props.get('type', {})
                type_val = type_info.get('valeur', 'Unknown')
                type_counts[type_val] = type_counts.get(type_val, 0) + 1
                all_types[type_val] = all_types.get(type_val, 0) + 1
            
            print(f"  Found {len(data.get('features', []))} features")
            for type_val, count in sorted(type_counts.items(), key=lambda x: -x[1]):
                print(f"    '{type_val}': {count}")
                
        except Exception as e:
            print(f"  Error: {e}")
    
    print("\n" + "=" * 70)
    print("ALL UNIQUE HUT TYPES FROM REFUGES.INFO")
    print("=" * 70)
    
    for type_val, count in sorted(all_types.items(), key=lambda x: -x[1]):
        print(f"  '{type_val}': {count}")
    
    # Proposed mapping
    print("\n" + "=" * 70)
    print("PROPOSED TYPE MAPPING")
    print("=" * 70)
    
    mapping = {
        # Staffed huts - "gardé" means staffed/managed
        'refuge gardé': 'Staffed Mountain Hut',
        
        # Unstaffed/basic cabins
        'cabane non gardée': 'Unstaffed Cabin',
        
        # Guesthouses  
        "gîte d'étape": 'Guesthouse',
        
        # Bivouacs (emergency shelters)
        'bivouac': 'Bivouac',
        
        # Others (if any)
    }
    
    print("\nFrench Type -> English Standard")
    print("-" * 50)
    for french, english in mapping.items():
        print(f"  '{french}' -> '{english}'")
    
    print("\n" + "=" * 70)
    print("COMPREHENSIVE CATEGORIZATION PROPOSAL")
    print("=" * 70)
    
    proposal = """
PROPOSED HUT CATEGORIES (6 types):

1. STAFFED MOUNTAIN HUT
   - Has warden/guardian during season
   - Provides meals, beds, services
   - French: "refuge gardé"
   - German: "bewirtschaftete Hütte"
   - Italian: "rifugio con gestore"
   
2. UNSTAFFED CABIN  
   - No permanent staff
   - Basic amenities (beds, kitchen area)
   - Self-service, often donation/payment box
   - French: "cabane non gardée", "refuge non gardé"
   - German: "Selbstversorgerhütte"
   
3. BIVOUAC
   - Very basic emergency shelter
   - Usually just floor space, no beds
   - High altitude, remote locations
   - French: "bivouac", "abri d'urgence"
   - German: "Biwakschachtel"
   - Italian: "bivacco"
   
4. ALPINE SHELTER
   - Basic shelter (zavetišče in Slovenian)
   - May have bunks
   - No cooking facilities
   - Often for emergency/bad weather
   
5. GUESTHOUSE
   - Valley or lower altitude
   - More comfortable, hotel-like
   - Restaurant/meals available
   - French: "gîte d'étape", "auberge"
   - German: "Gasthaus", "Pension"
   
6. ALPINE CLUB HUT
   - Owned by alpine club (CAI, SAC, DAV, ÖAV)
   - Usually staffed in season
   - Member discounts
   - High standard of service
"""
    print(proposal)

if __name__ == "__main__":
    analyze_french_types()

