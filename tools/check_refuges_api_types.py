#!/usr/bin/env python3
"""
Check what hut types the refuges.info API actually returns
"""
import requests

def check_api_types():
    url = 'https://www.refuges.info/api/bbox'
    
    type_points_list = ['cabane', 'refuge', 'bivouac']
    
    for type_points in type_points_list:
        params = {
            'bbox': 'world',
            'type_points': type_points,
            'nb_points': '20',
            'format': 'geojson',
            'detail': 'simple'
        }
        
        print(f"\nAPI type_points='{type_points}':")
        print("-" * 50)
        
        try:
            resp = requests.get(url, params=params, timeout=30)
            data = resp.json()
            
            # Collect unique types
            types_seen = {}
            for feature in data.get('features', []):
                props = feature['properties']
                type_info = props.get('type', {})
                type_val = type_info.get('valeur', 'N/A')
                if type_val not in types_seen:
                    types_seen[type_val] = props.get('nom', 'Unknown')
            
            for type_val, example_name in types_seen.items():
                print(f"  Type: '{type_val}'")
                print(f"    Example: {example_name}")
        except Exception as e:
            print(f"  Error: {e}")
    
    # Now check a specific point with full detail
    print("\n" + "=" * 60)
    print("FULL DETAIL CHECK FOR A STAFFED VS UNSTAFFED HUT")
    print("=" * 60)
    
    # Get one cabane and one refuge gardé for comparison
    params = {
        'bbox': 'world',
        'type_points': 'refuge',
        'nb_points': '100',
        'format': 'geojson',
        'detail': 'simple'
    }
    
    try:
        resp = requests.get(url, params=params, timeout=30)
        data = resp.json()
        
        cabane_gardee = None
        cabane_non_gardee = None
        
        for feature in data.get('features', []):
            props = feature['properties']
            type_info = props.get('type', {})
            type_val = type_info.get('valeur', '')
            
            if 'gardé' in type_val.lower() and not cabane_gardee:
                cabane_gardee = props
            elif 'non gardé' in type_val.lower() and not cabane_non_gardee:
                cabane_non_gardee = props
            
            if cabane_gardee and cabane_non_gardee:
                break
        
        if cabane_gardee:
            print(f"\nSTAFFED (gardé):")
            print(f"  Name: {cabane_gardee.get('nom')}")
            print(f"  Type: {cabane_gardee.get('type', {}).get('valeur')}")
            print(f"  ID: {cabane_gardee.get('id')}")
        
        if cabane_non_gardee:
            print(f"\nUNSTAFFED (non gardé):")
            print(f"  Name: {cabane_non_gardee.get('nom')}")
            print(f"  Type: {cabane_non_gardee.get('type', {}).get('valeur')}")
            print(f"  ID: {cabane_non_gardee.get('id')}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_api_types()

