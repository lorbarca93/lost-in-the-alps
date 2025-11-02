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
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            margin: 0; 
            padding: 0; 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f5f5f5;
        }}
        #map {{ 
            height: 100vh; 
            width: 100%;
            position: relative;
        }}
        
        /* Filter Panel with Glass Morphism */
        .filter-panel {{
            position: absolute;
            top: 15px;
            right: 15px;
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            padding: 20px;
            border-radius: 16px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.8);
            z-index: 1000;
            max-width: 280px;
            max-height: 85vh;
            overflow-y: auto;
            transition: all 0.3s ease;
        }}
        
        .filter-panel:hover {{
            box-shadow: 0 12px 48px rgba(0, 0, 0, 0.15);
        }}
        
        .filter-panel h3 {{ 
            margin: 0 0 15px 0; 
            font-size: 18px;
            font-weight: 600;
            color: #1e3a8a;
            border-bottom: 2px solid #3b82f6;
            padding-bottom: 8px;
        }}
        
        .filter-panel label {{ 
            display: flex;
            align-items: center;
            padding: 8px 4px;
            cursor: pointer;
            font-size: 14px;
            border-radius: 6px;
            transition: background 0.2s ease;
            color: #374151;
        }}
        
        .filter-panel label:hover {{
            background: rgba(59, 130, 246, 0.1);
        }}
        
        .filter-panel input[type="checkbox"] {{ 
            margin-right: 10px;
            width: 18px;
            height: 18px;
            cursor: pointer;
            accent-color: #3b82f6;
        }}
        
        .stats {{ 
            margin-top: 15px;
            padding-top: 15px;
            border-top: 2px solid #e5e7eb;
            font-size: 13px;
            background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
            padding: 12px;
            border-radius: 8px;
            font-weight: 500;
            color: #1e3a8a;
        }}
        
        .legend {{ 
            margin-top: 15px;
            padding-top: 15px;
            border-top: 2px solid #e5e7eb;
            font-size: 13px;
        }}
        
        .legend h4 {{
            margin: 0 0 10px 0;
            font-size: 14px;
            font-weight: 600;
            color: #374151;
        }}
        
        .legend-item {{ 
            margin: 8px 0;
            display: flex;
            align-items: center;
            font-weight: 500;
            color: #4b5563;
        }}
        
        .legend-color {{ 
            display: inline-block;
            width: 16px;
            height: 16px;
            border-radius: 50%;
            margin-right: 10px;
            border: 2px solid white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }}
        
        /* Custom Leaflet Popup Styling */
        .leaflet-popup-content-wrapper {{
            border-radius: 12px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.15);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            padding: 0;
        }}
        
        .leaflet-popup-content {{
            margin: 16px 20px;
            font-size: 14px;
            line-height: 1.8;
            min-width: 200px;
        }}
        
        .leaflet-popup-content div {{
            margin: 4px 0;
        }}
        
        .leaflet-popup-content b {{
            color: #1e3a8a;
            font-size: 16px;
            display: block;
            margin-bottom: 10px;
            border-bottom: 2px solid #3b82f6;
            padding-bottom: 6px;
        }}
        
        .leaflet-popup-content a {{
            color: #3b82f6;
            text-decoration: none;
            font-weight: 500;
            transition: color 0.2s ease;
        }}
        
        .leaflet-popup-content a:hover {{
            color: #2563eb;
            text-decoration: underline;
        }}
        
        .leaflet-popup-tip {{
            background: white;
        }}
        
        /* Scrollbar Styling */
        .filter-panel::-webkit-scrollbar {{
            width: 8px;
        }}
        
        .filter-panel::-webkit-scrollbar-track {{
            background: rgba(0,0,0,0.05);
            border-radius: 4px;
        }}
        
        .filter-panel::-webkit-scrollbar-thumb {{
            background: #3b82f6;
            border-radius: 4px;
        }}
        
        .filter-panel::-webkit-scrollbar-thumb:hover {{
            background: #2563eb;
        }}
        
        /* Toggle Button for Mobile */
        .toggle-panel {{
            display: none;
            position: absolute;
            top: 15px;
            right: 15px;
            z-index: 1001;
            background: white;
            border: none;
            padding: 12px 16px;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            cursor: pointer;
            font-size: 18px;
            transition: transform 0.2s ease;
        }}
        
        .toggle-panel:hover {{
            transform: scale(1.05);
        }}
        
        @media (max-width: 768px) {{
            .filter-panel {{
                max-width: 90%;
                right: 5%;
            }}
        }}
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
            <h4>📍 Data Sources</h4>
            <div class="legend-item"><span class="legend-color" style="background: blue;"></span> Boudy.info</div>
            <div class="legend-item"><span class="legend-color" style="background: red;"></span> Mountain-huts.net</div>
            <div class="legend-item"><span class="legend-color" style="background: green;"></span> Mountainhuts.info</div>
        </div>
    </div>
    <script>
        // Initialize map centered on Alps
        var map = L.map('map', {{
            center: [47.0, 13.0],
            zoom: 6,
            zoomControl: true,
            attributionControl: true
        }});
        
        // Add beautiful terrain tiles
        var terrainLayer = L.tileLayer('https://{{s}}.tile.opentopomap.org/{{z}}/{{x}}/{{y}}.png', {{
            maxZoom: 17,
            attribution: 'Map data: &copy; OpenStreetMap contributors, SRTM | Map style: &copy; OpenTopoMap'
        }});
        
        var standardLayer = L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
            maxZoom: 19,
            attribution: '&copy; OpenStreetMap contributors'
        }});
        
        var satelliteLayer = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{{z}}/{{y}}/{{x}}', {{
            maxZoom: 19,
            attribution: 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'
        }});
        
        // Add terrain layer by default
        terrainLayer.addTo(map);
        
        // Add layer control
        var baseMaps = {{
            "🏔️ Terrain": terrainLayer,
            "🗺️ Standard": standardLayer,
            "🛰️ Satellite": satelliteLayer
        }};
        
        L.control.layers(baseMaps).addTo(map);
        
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
            // Build popup content safely
            var popupParts = [];
            popupParts.push('<div style="max-width: 250px;">');
            popupParts.push('<b>' + hut.name + '</b>');
            
            if (hut.altitude && hut.altitude !== 'N/A') {{
                popupParts.push('<div>🏔️ Altitude: ' + hut.altitude + ' m</div>');
            }}
            
            if (hut.country && hut.country !== 'N/A') {{
                popupParts.push('<div>🌍 Country: ' + hut.country + '</div>');
            }}
            
            if (hut.type && hut.type !== 'N/A') {{
                popupParts.push('<div>🏠 Type: ' + hut.type + '</div>');
            }}
            
            if (hut.owner && hut.owner !== 'N/A' && hut.owner !== '') {{
                popupParts.push('<div>👤 Owner: ' + hut.owner + '</div>');
            }}
            
            if (hut.manager && hut.manager !== 'N/A' && hut.manager !== '') {{
                popupParts.push('<div>👔 Manager: ' + hut.manager + '</div>');
            }}
            
            if (hut.phone && hut.phone !== 'N/A' && hut.phone !== '') {{
                popupParts.push('<div>📞 Phone: ' + hut.phone + '</div>');
            }}
            
            if (hut.email && hut.email !== 'N/A' && hut.email !== '') {{
                popupParts.push('<div>📧 Email: ' + hut.email + '</div>');
            }}
            
            if (hut.website && hut.website !== 'N/A' && hut.website !== '') {{
                popupParts.push('<div>🌐 <a href="http://' + hut.website + '" target="_blank" rel="noopener">Website</a></div>');
            }}
            
            if (hut.opening && hut.opening !== 'N/A' && hut.opening !== '') {{
                popupParts.push('<div>🕐 Opening: ' + hut.opening + '</div>');
            }}
            
            if (hut.description && hut.description !== 'N/A' && hut.description !== '' && hut.description.length < 200) {{
                popupParts.push('<div style="margin-top: 8px; font-size: 0.9em; color: #666;">' + hut.description + '</div>');
            }}
            
            popupParts.push('<div style="margin-top: 8px; font-size: 0.85em; color: #999;">Source: ' + hut.source + '</div>');
            popupParts.push('</div>');
            
            var popup = popupParts.join('');
            
            var marker = L.circleMarker([hut.lat, hut.lon], {{
                radius: 6,
                fillColor: hut.color,
                color: '#fff',
                weight: 2,
                opacity: 1,
                fillOpacity: 0.85
            }});
            
            // Add hover effects
            marker.on('mouseover', function(e) {{
                this.setStyle({{
                    radius: 9,
                    weight: 3,
                    fillOpacity: 1
                }});
            }});
            
            marker.on('mouseout', function(e) {{
                this.setStyle({{
                    radius: 6,
                    weight: 2,
                    fillOpacity: 0.85
                }});
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
