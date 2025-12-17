import requests

# Fetch a sample region
url = "https://www.boudy.info/api/get_objects.php"
params = {
    'lat1': 45.0,
    'lat2': 46.0,
    'lng1': 7.0,
    'lng2': 8.0
}

response = requests.post(url, data=params)
data = response.json()

if data and 'features' in data and len(data['features']) > 0:
    feature = data['features'][0]
    coords = feature['geometry']['coordinates']
    props = feature['properties']
    
    print("Sample GeoJSON feature:")
    print("="*80)
    print(f"Name: {props.get('nazov', 'N/A')}")
    print(f"Raw coordinates: {coords}")
    print(f"coords[0]: {coords[0]}")
    print(f"coords[1]: {coords[1]}")
    print()
    print("GeoJSON format is: [longitude, latitude]")
    print(f"So coords[0] = {coords[0]} should be LONGITUDE")
    print(f"And coords[1] = {coords[1]} should be LATITUDE")
    print()
    print("For Alps region:")
    print("  Latitude should be 43-48°N")
    print("  Longitude should be 6-9°E")
    print()
    if coords[0] > 40:
        print("❌ coords[0] looks like a LATITUDE (>40), not longitude!")
        print("❌ The GeoJSON from boudy.info is [lat, lon] NOT [lon, lat]!")
    else:
        print("✓ coords[0] looks correct as longitude")
