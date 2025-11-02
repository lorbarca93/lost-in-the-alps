"""
Create a super simple HTML map with NO special characters in embedded data
"""
import sqlite3
from pathlib import Path
import json

def clean_string(s):
    """Remove any problematic characters"""
    if not s:
        return "N/A"
    # Replace quotes and backslashes
    s = str(s).replace('\\', '').replace('"', '').replace("'", '')
    # Remove any other problematic characters
    s = s.replace('\n', ' ').replace('\r', ' ')
    return s.strip() or "N/A"

def create_simple_map():
    # Connect to database
    db_path = Path(__file__).parent.parent / "data" / "mountain_huts.db"
    conn = sqlite3.connect(db_path)
    
    # Get all huts with coordinates
    cursor = conn.execute("""
        SELECT name, latitude, longitude, altitude, country, type_description, website, source,
               owner, manager, phone, email, opening_hours, description
        FROM mountain_huts
        WHERE latitude IS NOT NULL AND longitude IS NOT NULL
        ORDER BY name
    """)
    
    huts = cursor.fetchall()
    conn.close()
    
    # Build clean JSON data
    huts_data = []
    for hut in huts:
        name = clean_string(hut[0])
        lat = float(hut[1])
        lon = float(hut[2])
        source = hut[7]
        
        # Fix boudy.info coordinate swap
        if source == 'boudy.info':
            lat, lon = lon, lat
        
        altitude = clean_string(hut[3]) if hut[3] else "N/A"
        country = clean_string(hut[4]) if hut[4] else "N/A"
        hut_type = clean_string(hut[5]) if hut[5] else "N/A"
        website = clean_string(hut[6]) if hut[6] else ""
        owner = clean_string(hut[8]) if hut[8] else ""
        manager = clean_string(hut[9]) if hut[9] else ""
        phone = clean_string(hut[10]) if hut[10] else ""
        email = clean_string(hut[11]) if hut[11] else ""
        opening_hours = clean_string(hut[12]) if hut[12] else ""
        description = clean_string(hut[13]) if hut[13] else ""
        
        # Color by source
        if source == 'boudy.info':
            color = 'blue'
        elif source == 'mountain-huts.net':
            color = 'red'
        elif source == 'mountainhuts.info':
            color = 'green'
        else:
            color = 'gray'
        
        huts_data.append({
            'name': name,
            'lat': lat,
            'lon': lon,
            'altitude': altitude,
            'country': country,
            'type': hut_type,
            'website': website,
            'source': source,
            'color': color,
            'owner': owner,
            'manager': manager,
            'phone': phone,
            'email': email,
            'opening': opening_hours,
            'description': description
        })
    
    # Convert to JSON
    huts_json = json.dumps(huts_data, indent=2)
    
    # Create HTML
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Mountain Huts Map</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <style>
        body {{ margin: 0; padding: 0; font-family: Arial, sans-serif; }}
        #map {{ height: 100vh; width: 100%; }}
        .filter-panel {{
            position: absolute;
            top: 10px;
            right: 10px;
            background: white;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.2);
            z-index: 1000;
            max-width: 250px;
            max-height: 80vh;
            overflow-y: auto;
        }}
        .filter-panel h3 {{ margin: 0 0 10px 0; font-size: 16px; }}
        .filter-panel label {{ display: block; padding: 3px 0; cursor: pointer; font-size: 13px; }}
        .filter-panel input[type="checkbox"] {{ margin-right: 5px; }}
        .stats {{ margin-top: 10px; padding-top: 10px; border-top: 1px solid #ddd; font-size: 12px; }}
        .legend {{ margin-top: 10px; padding-top: 10px; border-top: 1px solid #ddd; font-size: 12px; }}
        .legend-item {{ margin: 3px 0; }}
        .legend-color {{ display: inline-block; width: 12px; height: 12px; border-radius: 50%; margin-right: 5px; }}
    </style>
</head>
<body>
    <div id="map"></div>
    <div class="filter-panel">
        <h3>Filter by Country</h3>
        <label><input type="checkbox" id="filter-all" checked> All Countries</label>
        <div id="country-filters"></div>
        <div class="stats">
            <div id="stats-display"></div>
        </div>
        <div class="legend">
            <div class="legend-item"><span class="legend-color" style="background: blue;"></span> boudy.info</div>
            <div class="legend-item"><span class="legend-color" style="background: red;"></span> mountain-huts.net</div>
            <div class="legend-item"><span class="legend-color" style="background: green;"></span> mountainhuts.info</div>
        </div>
    </div>
    <script>
        // Initialize map
        var map = L.map('map').setView([47.0, 13.0], 6);
        
        // Add tiles
        L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
            maxZoom: 18,
            attribution: '&copy; OpenStreetMap'
        }}).addTo(map);
        
        // Huts data
        var huts = {huts_json};
        
        console.log('Loading ' + huts.length + ' huts...');
        
        // Get unique countries
        var countries = {{}};
        huts.forEach(function(hut) {{
            if (hut.country && hut.country !== 'N/A') {{
                countries[hut.country] = (countries[hut.country] || 0) + 1;
            }}
        }});
        
        // Create country filters
        var sortedCountries = Object.keys(countries).sort();
        var filterDiv = document.getElementById('country-filters');
        sortedCountries.forEach(function(country) {{
            var label = document.createElement('label');
            var checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.checked = true;
            checkbox.className = 'country-filter';
            checkbox.dataset.country = country;
            label.appendChild(checkbox);
            label.appendChild(document.createTextNode(' ' + country + ' (' + countries[country] + ')'));
            filterDiv.appendChild(label);
        }});
        
        // Store markers
        var markers = [];
        
        // Add markers
        huts.forEach(function(hut) {{
            var popup = '<b>' + hut.name + '</b><br>' +
                'Altitude: ' + hut.altitude + ' m<br>' +
                'Country: ' + hut.country + '<br>' +
                'Type: ' + hut.type + '<br>';
            
            if (hut.owner && hut.owner !== 'N/A' && hut.owner !== '') {{
                popup += 'Owner: ' + hut.owner + '<br>';
            }}
            
            if (hut.manager && hut.manager !== 'N/A' && hut.manager !== '') {{
                popup += 'Manager: ' + hut.manager + '<br>';
            }}
            
            if (hut.phone && hut.phone !== 'N/A' && hut.phone !== '') {{
                popup += 'Phone: ' + hut.phone + '<br>';
            }}
            
            if (hut.email && hut.email !== 'N/A' && hut.email !== '') {{
                popup += 'Email: ' + hut.email + '<br>';
            }}
            
            if (hut.website && hut.website !== 'N/A' && hut.website !== '') {{
                popup += 'Website: <a href="http://' + hut.website + '" target="_blank">' + hut.website + '</a><br>';
            }}
            
            if (hut.opening && hut.opening !== 'N/A' && hut.opening !== '') {{
                popup += 'Open: ' + hut.opening + '<br>';
            }}
            
            if (hut.description && hut.description !== 'N/A' && hut.description !== '') {{
                popup += '<small>' + hut.description + '</small><br>';
            }}
            
            popup += '<small>Source: ' + hut.source + '</small>';
            
            var marker = L.circleMarker([hut.lat, hut.lon], {{
                radius: 5,
                fillColor: hut.color,
                color: '#fff',
                weight: 1,
                opacity: 1,
                fillOpacity: 0.8
            }});
            
            marker.bindPopup(popup);
            marker.hutData = hut;
            marker.addTo(map);
            markers.push(marker);
        }});
        
        // Update stats
        function updateStats() {{
            var visible = markers.filter(function(m) {{ return map.hasLayer(m); }}).length;
            document.getElementById('stats-display').innerHTML = 
                '<b>Showing: ' + visible + ' of ' + huts.length + ' huts</b>';
        }}
        
        // Apply filter
        function applyFilter() {{
            var checkedCountries = [];
            var checkboxes = document.querySelectorAll('.country-filter');
            checkboxes.forEach(function(cb) {{
                if (cb.checked) {{
                    checkedCountries.push(cb.dataset.country);
                }}
            }});
            
            markers.forEach(function(marker) {{
                var country = marker.hutData.country;
                if (country === 'N/A' || checkedCountries.length === 0 || checkedCountries.indexOf(country) !== -1) {{
                    if (!map.hasLayer(marker)) marker.addTo(map);
                }} else {{
                    if (map.hasLayer(marker)) map.removeLayer(marker);
                }}
            }});
            
            updateStats();
        }}
        
        // All Countries checkbox
        document.getElementById('filter-all').addEventListener('change', function() {{
            var checkboxes = document.querySelectorAll('.country-filter');
            checkboxes.forEach(function(cb) {{
                cb.checked = this.checked;
            }}, this);
            applyFilter();
        }});
        
        // Individual checkboxes
        document.querySelectorAll('.country-filter').forEach(function(cb) {{
            cb.addEventListener('change', function() {{
                var allChecked = Array.from(document.querySelectorAll('.country-filter')).every(function(c) {{
                    return c.checked;
                }});
                document.getElementById('filter-all').checked = allChecked;
                applyFilter();
            }});
        }});
        
        updateStats();
        console.log('Map ready with ' + markers.length + ' markers!');
    </script>
</body>
</html>"""
    
    # Write file
    output_path = Path(__file__).parent.parent / "mountain_huts_map.html"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"Created ultra-simple map with {len(huts)} huts at {output_path}")
    print(f"Map file size: {output_path.stat().st_size / 1024:.1f} KB")

if __name__ == "__main__":
    create_simple_map()
