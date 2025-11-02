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
        SELECT name, latitude, longitude, altitude, country, hut_type, website, source,
               owner, manager, phone, email, opening_hours, description,
               capacity, capacity_max, comments, water_source, best_time_to_visit, access, posted_by
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
        capacity = clean_string(hut[14]) if hut[14] else ""
        capacity_max = clean_string(hut[15]) if hut[15] else ""
        comments = clean_string(hut[16]) if hut[16] else ""
        water_source = clean_string(hut[17]) if hut[17] else ""
        best_time = clean_string(hut[18]) if hut[18] else ""
        access = clean_string(hut[19]) if hut[19] else ""
        posted_by = clean_string(hut[20]) if hut[20] else ""
        
        # Color by source – use a vivid blue that shows up well on the dark background
        if source == 'boudy.info':
            color = '#3b82f6'  # vivid blue that stays readable on dark background
        elif source == 'mountain-huts.net':
            color = 'red'
        elif source == 'mountainhuts.info':
            color = 'green'
        elif source == 'refuges.info':
            color = 'orange'
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
            'description': description,
            'capacity': capacity,
            'capacity_max': capacity_max,
            'comments': comments,
            'water_source': water_source,
            'best_time': best_time,
            'access': access,
            'posted_by': posted_by
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
    <link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.css" />
    <link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.Default.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script src="https://unpkg.com/leaflet.markercluster@1.5.3/dist/leaflet.markercluster.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            margin: 0; 
            padding: 0; 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f5f5f5;
            display: flex;
            overflow: hidden;
        }}
        
        /* Left Sidebar */
        .sidebar {{
            width: 350px;
            height: 100vh;
            background: linear-gradient(180deg, #0f172a 0%, #1e293b 50%, #334155 100%);
            color: white;
            overflow-y: auto;
            box-shadow: 4px 0 20px rgba(0,0,0,0.15);
            z-index: 1001;
            display: flex;
            flex-direction: column;
        }}
        
        .sidebar-header {{
            padding: 30px 25px 20px;
            background: linear-gradient(135deg, #0ea5e9 0%, #06b6d4 100%);
        }}
        
        .sidebar-header h1 {{
            font-size: 24px;
            margin: 0 0 8px 0;
            font-weight: 700;
        }}
        
        .sidebar-header p {{
            margin: 0;
            font-size: 14px;
            opacity: 0.9;
            line-height: 1.6;
        }}
        
        .sidebar-content {{
            padding: 25px;
            flex: 1;
        }}
        
        .filter-section {{
            margin-bottom: 30px;
        }}
        
        .filter-section h3 {{
            font-size: 16px;
            margin: 0 0 15px 0;
            font-weight: 600;
            border-bottom: 2px solid rgba(255,255,255,0.3);
            padding-bottom: 8px;
        }}
        
        .filter-group {{
            margin-bottom: 20px;
        }}
        
        .filter-group label {{
            display: block;
            margin-bottom: 8px;
            font-size: 13px;
            opacity: 0.9;
            font-weight: 500;
        }}
        
        .filter-group input[type="text"],
        .filter-group input[type="number"],
        .filter-group select {{
            width: 100%;
            padding: 10px;
            border: none;
            border-radius: 8px;
            font-size: 14px;
            background: rgba(255,255,255,0.15);
            color: white;
            backdrop-filter: blur(10px);
        }}
        
        .filter-group input[type="text"]::placeholder {{
            color: rgba(255,255,255,0.6);
        }}
        
        .filter-group input[type="text"]:focus,
        .filter-group input[type="number"]:focus,
        .filter-group select:focus {{
            outline: none;
            background: rgba(255,255,255,0.25);
        }}
        
        .checkbox-list {{
            max-height: 250px;
            overflow-y: auto;
            background: rgba(0,0,0,0.2);
            padding: 10px;
            border-radius: 8px;
        }}
        
        .checkbox-list label {{
            display: flex;
            align-items: center;
            padding: 6px 8px;
            cursor: pointer;
            border-radius: 6px;
            transition: background 0.2s ease;
            font-size: 13px;
        }}
        
        .checkbox-list label:hover {{
            background: rgba(255,255,255,0.1);
        }}
        
        .checkbox-list input[type="checkbox"] {{
            margin-right: 10px;
            width: 16px;
            height: 16px;
            cursor: pointer;
        }}
        
        .action-buttons {{
            margin-top: 25px;
            display: flex;
            flex-direction: column;
            gap: 12px;
        }}
        
        .btn {{
            padding: 12px 20px;
            border: none;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
        }}
        
        .btn-primary {{
            background: linear-gradient(135deg, #06b6d4 0%, #0ea5e9 100%);
            color: white;
            border: none;
        }}
        
        .btn-primary:hover {{
            background: linear-gradient(135deg, #0891b2 0%, #0284c7 100%);
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        }}
        
        .btn-secondary {{
            background: rgba(255,255,255,0.15);
            color: white;
            border: 1px solid rgba(255,255,255,0.3);
        }}
        
        .btn-secondary:hover {{
            background: rgba(255,255,255,0.25);
            transform: translateY(-2px);
        }}
        
        /* Altitude Slider */
        .slider-container {{
            margin-top: 10px;
        }}
        
        .slider-values {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 8px;
            font-size: 13px;
            opacity: 0.9;
        }}
        
        input[type="range"] {{
            -webkit-appearance: none;
            appearance: none;
            width: 100%;
            height: 6px;
            border-radius: 3px;
            background: rgba(255,255,255,0.2);
            outline: none;
            margin: 10px 0;
        }}
        
        input[type="range"]::-webkit-slider-thumb {{
            -webkit-appearance: none;
            appearance: none;
            width: 18px;
            height: 18px;
            border-radius: 50%;
            background: #06b6d4;
            cursor: pointer;
            box-shadow: 0 2px 6px rgba(0,0,0,0.3);
            transition: all 0.2s ease;
        }}
        
        input[type="range"]::-webkit-slider-thumb:hover {{
            background: #0ea5e9;
            transform: scale(1.2);
        }}
        
        input[type="range"]::-moz-range-thumb {{
            width: 18px;
            height: 18px;
            border-radius: 50%;
            background: #06b6d4;
            cursor: pointer;
            border: none;
            box-shadow: 0 2px 6px rgba(0,0,0,0.3);
            transition: all 0.2s ease;
        }}
        
        input[type="range"]::-moz-range-thumb:hover {{
            background: #0ea5e9;
            transform: scale(1.2);
        }}
        
        #map {{ 
            flex: 1;
            height: 100vh;
            position: relative;
        }}
        
        .stats-display {{
            background: rgba(0,0,0,0.3);
            padding: 15px;
            border-radius: 8px;
            margin-top: 20px;
            text-align: center;
            font-size: 14px;
            font-weight: 600;
        }}
        
        .stats-display .number {{
            font-size: 32px;
            display: block;
            margin-bottom: 5px;
        }}
        
        .legend {{
            margin-top: 20px;
        }}
        
        .legend h4 {{
            font-size: 14px;
            margin: 0 0 12px 0;
            font-weight: 600;
            opacity: 0.9;
        }}
        
        .legend-item {{
            display: flex;
            align-items: center;
            margin: 8px 0;
            font-size: 13px;
        }}
        
        .legend-color {{
            width: 14px;
            height: 14px;
            border-radius: 50%;
            margin-right: 10px;
            border: 2px solid rgba(255,255,255,0.5);
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
        .sidebar::-webkit-scrollbar,
        .checkbox-list::-webkit-scrollbar {{
            width: 8px;
        }}
        
        .sidebar::-webkit-scrollbar-track,
        .checkbox-list::-webkit-scrollbar-track {{
            background: rgba(0,0,0,0.2);
            border-radius: 4px;
        }}
        
        .sidebar::-webkit-scrollbar-thumb,
        .checkbox-list::-webkit-scrollbar-thumb {{
            background: rgba(255,255,255,0.3);
            border-radius: 4px;
        }}
        
        .sidebar::-webkit-scrollbar-thumb:hover,
        .checkbox-list::-webkit-scrollbar-thumb:hover {{
            background: rgba(255,255,255,0.5);
        }}
        
        /* Marker Cluster Styling */
        .marker-cluster-small {{
            background-color: rgba(6, 182, 212, 0.6);
        }}
        .marker-cluster-small div {{
            background-color: rgba(6, 182, 212, 0.8);
            color: white;
            font-weight: bold;
        }}
        .marker-cluster-medium {{
            background-color: rgba(251, 146, 60, 0.6);
        }}
        .marker-cluster-medium div {{
            background-color: rgba(251, 146, 60, 0.8);
            color: white;
            font-weight: bold;
        }}
        .marker-cluster-large {{
            background-color: rgba(239, 68, 68, 0.6);
        }}
        .marker-cluster-large div {{
            background-color: rgba(239, 68, 68, 0.8);
            color: white;
            font-weight: bold;
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
        
        @media (max-width: 1024px) {{
            .sidebar {{
                width: 300px;
            }}
        }}
        
        @media (max-width: 768px) {{
            body {{
                flex-direction: column;
            }}
            .sidebar {{
                width: 100%;
                height: auto;
                max-height: 40vh;
            }}
            #map {{
                height: 60vh;
            }}
        }}
    </style>
</head>
<body>
    <div class="sidebar">
        <div class="sidebar-header">
            <h1>🏔️ Mountain Huts Explorer</h1>
            <p>Discover and explore mountain huts across the Alps and beyond. Filter by location, capacity, and more.</p>
        </div>
        <div class="sidebar-content">
            <!-- Search Filter -->
            <div class="filter-section">
                <h3>🔍 Search</h3>
                <div class="filter-group">
                    <label for="search-input">Hut Name</label>
                    <input type="text" id="search-input" placeholder="Search by name...">
                </div>
            </div>
            
            <!-- Country Filter -->
            <div class="filter-section">
                <h3>🌍 Countries</h3>
                <div class="filter-group">
                    <label><input type="checkbox" id="filter-all" checked> All Countries</label>
                </div>
                <div class="checkbox-list" id="country-filters"></div>
            </div>
            
            <!-- Altitude Filter -->
            <div class="filter-section">
                <h3>⛰️ Altitude</h3>
                <div class="filter-group">
                    <label>Minimum Altitude (m)</label>
                    <div class="slider-container">
                        <div class="slider-values">
                            <span>0 m</span>
                            <span id="min-altitude-value">0 m</span>
                        </div>
                        <input type="range" id="min-altitude" min="0" max="4000" value="0" step="100">
                    </div>
                </div>
                <div class="filter-group">
                    <label>Maximum Altitude (m)</label>
                    <div class="slider-container">
                        <div class="slider-values">
                            <span id="max-altitude-value">4000 m</span>
                            <span>4000 m</span>
                        </div>
                        <input type="range" id="max-altitude" min="0" max="4000" value="4000" step="100">
                    </div>
                </div>
            </div>
            
            <!-- Capacity Filter -->
            <div class="filter-section">
                <h3>🛏️ Capacity</h3>
                <div class="filter-group">
                    <label for="min-capacity">Minimum Beds</label>
                    <input type="number" id="min-capacity" placeholder="1">
                </div>
            </div>
            
            <!-- Data Source Filter -->
            <div class="filter-section">
                <h3>📍 Data Sources</h3>
                <div class="filter-group">
                    <label><input type="checkbox" class="source-filter" value="boudy.info" checked> <span class="legend-color" style="background: #3b82f6;"></span> Boudy.info</label>
                    <label><input type="checkbox" class="source-filter" value="mountain-huts.net" checked> <span class="legend-color" style="background: red;"></span> Mountain-huts.net</label>
                    <label><input type="checkbox" class="source-filter" value="mountainhuts.info" checked> <span class="legend-color" style="background: green;"></span> Mountainhuts.info</label>
                    <label><input type="checkbox" class="source-filter" value="refuges.info" checked> <span class="legend-color" style="background: orange;"></span> Refuges.info</label>
                </div>
            </div>
            
            <!-- Action Buttons -->
            <div class="action-buttons">
                <button class="btn btn-secondary" id="reset-filters">🔄 Reset All</button>
                <button class="btn btn-primary" id="export-kmz">📥 Export to KMZ</button>
            </div>
            
            <!-- Stats -->
            <div class="stats-display">
                <span class="number" id="visible-count">0</span>
                <div>huts visible</div>
            </div>
        </div>
    </div>
    <div id="map"></div>
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
        
        // Function to generate KML content
        function generateKML(visibleHuts) {{
            var kml = '<?xml version="1.0" encoding="UTF-8"?>\\n';
            kml += '<kml xmlns="http://www.opengis.net/kml/2.2">\\n';
            kml += '<Document>\\n';
            kml += '<name>Mountain Huts</name>\\n';
            kml += '<description>Exported mountain huts from Lost in the Alps</description>\\n';
            
            // Add styles for different sources
            kml += '<Style id="boudy"><IconStyle><Icon><href>http://maps.google.com/mapfiles/kml/paddle/blu-circle.png</href></Icon></IconStyle></Style>\\n';
            kml += '<Style id="mountain-huts"><IconStyle><Icon><href>http://maps.google.com/mapfiles/kml/paddle/red-circle.png</href></Icon></IconStyle></Style>\\n';
            kml += '<Style id="mountainhuts"><IconStyle><Icon><href>http://maps.google.com/mapfiles/kml/paddle/grn-circle.png</href></Icon></IconStyle></Style>\\n';
            
            // Helper function to escape XML entities
            function escapeXml(text) {{
                return String(text).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&apos;');
            }}
            
            visibleHuts.forEach(function(hut) {{
                var styleId = hut.source.replace('.', '-').replace(' ', '-');
                kml += '<Placemark>\\n';
                kml += '<name>' + escapeXml(hut.name) + '</name>\\n';
                kml += '<styleUrl>#' + styleId + '</styleUrl>\\n';
                kml += '<description><![CDATA[';
                if (hut.altitude && hut.altitude !== 'N/A') kml += '<b>Altitude:</b> ' + escapeXml(String(hut.altitude)) + ' m<br/>';
                if (hut.country && hut.country !== 'N/A') kml += '<b>Country:</b> ' + escapeXml(hut.country) + '<br/>';
                if (hut.capacity && hut.capacity !== 'N/A' && hut.capacity !== '') kml += '<b>Capacity:</b> ' + escapeXml(String(hut.capacity)) + '<br/>';
                if (hut.website && hut.website !== 'N/A' && hut.website !== '') {{
                    var kmlWebUrl = hut.website.startsWith('http') ? hut.website : 'http://' + hut.website;
                    kml += '<b>Website:</b> <a href="' + escapeXml(kmlWebUrl) + '">' + escapeXml(hut.website) + '</a><br/>';
                }}
                kml += '<b>Source:</b> ' + escapeXml(hut.source);
                kml += ']]></description>\\n';
                kml += '<Point><coordinates>' + hut.lon + ',' + hut.lat + ',0</coordinates></Point>\\n';
                kml += '</Placemark>\\n';
            }});
            
            kml += '</Document>\\n';
            kml += '</kml>';
            return kml;
        }}
        
        // Export to KMZ function
        function exportToKMZ() {{
            var visibleHuts = [];
            markers.forEach(function(marker) {{
                if (markerCluster.hasLayer(marker)) {{
                    visibleHuts.push(marker.hutData);
                }}
            }});
            
            if (visibleHuts.length === 0) {{
                alert('No huts to export! Please adjust your filters.');
                return;
            }}
            
            var kml = generateKML(visibleHuts);
            var blob = new Blob([kml], {{ type: 'application/vnd.google-earth.kml+xml' }});
            var url = URL.createObjectURL(blob);
            var a = document.createElement('a');
            a.href = url;
            a.download = 'mountain_huts_' + visibleHuts.length + '.kml';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
            
            alert('Exported ' + visibleHuts.length + ' huts to KML file!\\n\\nNote: KML format is used (KMZ is KML + ZIP). You can convert to KMZ using Google Earth.');
        }}
        
        // Store markers and create marker cluster group
        var markers = [];
        var markerCluster = L.markerClusterGroup({{
            maxClusterRadius: 50,
            spiderfyOnMaxZoom: true,
            showCoverageOnHover: false,
            zoomToBoundsOnClick: true,
            disableClusteringAtZoom: 13,
            chunkedLoading: true,
            chunkInterval: 50,
            chunkDelay: 50
        }});
        
        map.addLayer(markerCluster);
        
        // HTML escape function to prevent XSS
        function escapeHtml(text) {{
            var div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }}
        
        // Add markers
        huts.forEach(function(hut) {{
            // Build popup content safely
            var popupParts = [];
            popupParts.push('<div style="max-width: 250px;">');
            popupParts.push('<b>' + escapeHtml(hut.name) + '</b>');
            
            if (hut.altitude && hut.altitude !== 'N/A') {{
                popupParts.push('<div>🏔️ Altitude: ' + escapeHtml(String(hut.altitude)) + ' m</div>');
            }}
            
            if (hut.country && hut.country !== 'N/A') {{
                popupParts.push('<div>🌍 Country: ' + escapeHtml(hut.country) + '</div>');
            }}
            
            if (hut.type && hut.type !== 'N/A') {{
                popupParts.push('<div>🏠 Type: ' + escapeHtml(hut.type) + '</div>');
            }}
            
            // Capacity information
            if (hut.capacity && hut.capacity !== 'N/A' && hut.capacity !== '') {{
                var capacityText = '🛏️ Capacity: ' + escapeHtml(String(hut.capacity));
                if (hut.capacity_max && hut.capacity_max !== 'N/A' && hut.capacity_max !== '') {{
                    capacityText += ' (max: ' + escapeHtml(String(hut.capacity_max)) + ')';
                }}
                popupParts.push('<div>' + capacityText + '</div>');
            }}
            
            // Water source
            if (hut.water_source && hut.water_source !== 'N/A' && hut.water_source !== '') {{
                popupParts.push('<div>💧 Water: ' + escapeHtml(hut.water_source) + '</div>');
            }}
            
            // Best time to visit
            if (hut.best_time && hut.best_time !== 'N/A' && hut.best_time !== '') {{
                popupParts.push('<div>📅 Best time: ' + escapeHtml(hut.best_time) + '</div>');
            }}
            
            // Access
            if (hut.access && hut.access !== 'N/A' && hut.access !== '') {{
                popupParts.push('<div>🥾 Access: ' + escapeHtml(hut.access) + '</div>');
            }}
            
            if (hut.owner && hut.owner !== 'N/A' && hut.owner !== '') {{
                popupParts.push('<div>👤 Owner: ' + escapeHtml(hut.owner) + '</div>');
            }}
            
            if (hut.manager && hut.manager !== 'N/A' && hut.manager !== '') {{
                popupParts.push('<div>👔 Manager: ' + escapeHtml(hut.manager) + '</div>');
            }}
            
            if (hut.phone && hut.phone !== 'N/A' && hut.phone !== '') {{
                popupParts.push('<div>📞 Phone: ' + escapeHtml(hut.phone) + '</div>');
            }}
            
            if (hut.email && hut.email !== 'N/A' && hut.email !== '') {{
                popupParts.push('<div>📧 Email: ' + escapeHtml(hut.email) + '</div>');
            }}
            
            if (hut.website && hut.website !== 'N/A' && hut.website !== '') {{
                var websiteUrl = hut.website.startsWith('http') ? hut.website : 'http://' + hut.website;
                popupParts.push('<div>🌐 <a href="' + websiteUrl + '" target="_blank" rel="noopener">Website</a></div>');
            }}
            
            if (hut.opening && hut.opening !== 'N/A' && hut.opening !== '') {{
                popupParts.push('<div>🕐 Opening: ' + escapeHtml(hut.opening) + '</div>');
            }}
            
            // Comments
            if (hut.comments && hut.comments !== 'N/A' && hut.comments !== '' && hut.comments.length < 250) {{
                popupParts.push('<div style="margin-top: 8px; padding: 8px; background: #f0f9ff; border-left: 3px solid #3b82f6; font-size: 0.9em; color: #1e3a8a;">💬 ' + escapeHtml(hut.comments) + '</div>');
            }}
            
            if (hut.description && hut.description !== 'N/A' && hut.description !== '' && hut.description.length < 200) {{
                popupParts.push('<div style="margin-top: 8px; font-size: 0.9em; color: #666;">' + escapeHtml(hut.description) + '</div>');
            }}
            
            // Posted by
            if (hut.posted_by && hut.posted_by !== 'N/A' && hut.posted_by !== '') {{
                popupParts.push('<div style="margin-top: 8px; font-size: 0.85em; color: #999;">✍️ Posted by: ' + escapeHtml(hut.posted_by) + '</div>');
            }}
            
            popupParts.push('<div style="margin-top: 8px; font-size: 0.85em; color: #999;">📍 Source: ' + escapeHtml(hut.source) + '</div>');
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
            markerCluster.addLayer(marker);
            markers.push(marker);
        }});
        
        // Update stats
        function updateStats() {{
            var visible = markers.filter(function(m) {{ return markerCluster.hasLayer(m); }}).length;
            document.getElementById('visible-count').textContent = visible;
        }}
        
        // Apply all filters
        function applyAllFilters() {{
            var searchText = document.getElementById('search-input').value.toLowerCase();
            var minAltitude = parseInt(document.getElementById('min-altitude').value) || 0;
            var maxAltitude = parseInt(document.getElementById('max-altitude').value) || 999999;
            var minCapacity = parseInt(document.getElementById('min-capacity').value) || 0;
            
            // Get checked countries
            var checkedCountries = [];
            var countryCheckboxes = document.querySelectorAll('.country-filter');
            countryCheckboxes.forEach(function(cb) {{
                if (cb.checked) {{
                    checkedCountries.push(cb.dataset.country);
                }}
            }});
            
            // Get checked sources
            var checkedSources = [];
            var sourceCheckboxes = document.querySelectorAll('.source-filter');
            sourceCheckboxes.forEach(function(cb) {{
                if (cb.checked) {{
                    checkedSources.push(cb.value);
                }}
            }});
            
            // Filter markers
            markers.forEach(function(marker) {{
                var hut = marker.hutData;
                var show = true;
                
                // Search filter
                if (searchText && hut.name.toLowerCase().indexOf(searchText) === -1) {{
                    show = false;
                }}
                
                // Country filter
                if (checkedCountries.length > 0) {{
                    if (hut.country === 'N/A' || checkedCountries.indexOf(hut.country) === -1) {{
                        show = false;
                    }}
                }}
                
                // Source filter
                if (checkedSources.length > 0 && checkedSources.indexOf(hut.source) === -1) {{
                    show = false;
                }}
                
                // Altitude filter
                var altitude = parseInt(hut.altitude);
                if (!isNaN(altitude)) {{
                    if (altitude < minAltitude || altitude > maxAltitude) {{
                        show = false;
                    }}
                }}
                
                // Capacity filter
                var capacity = parseInt(hut.capacity);
                if (!isNaN(capacity) && capacity < minCapacity) {{
                    show = false;
                }}
                
                // Apply visibility
                // Store the desired visibility state on the marker
                marker._shouldShow = show;
                
                if (show) {{
                    if (!markerCluster.hasLayer(marker)) {{
                        markerCluster.addLayer(marker);
                    }}
                }} else {{
                    if (markerCluster.hasLayer(marker)) {{
                        markerCluster.removeLayer(marker);
                    }}
                }}
            }});
            
            // Refresh the cluster to ensure proper display
            markerCluster.refreshClusters();
            
            updateStats();
        }}
        
        // Reset all filters
        function resetAllFilters() {{
            document.getElementById('search-input').value = '';
            document.getElementById('min-altitude').value = 0;
            document.getElementById('max-altitude').value = 4000;
            document.getElementById('min-altitude-value').textContent = '0 m';
            document.getElementById('max-altitude-value').textContent = '4000 m';
            document.getElementById('min-capacity').value = '';
            document.getElementById('filter-all').checked = true;
            
            document.querySelectorAll('.country-filter').forEach(function(cb) {{
                cb.checked = true;
            }});
            
            document.querySelectorAll('.source-filter').forEach(function(cb) {{
                cb.checked = true;
            }});
            
            applyAllFilters();
        }}
        
        // Event Listeners
        
        // All Countries checkbox
        document.getElementById('filter-all').addEventListener('change', function() {{
            var checkboxes = document.querySelectorAll('.country-filter');
            checkboxes.forEach(function(cb) {{
                cb.checked = this.checked;
            }}, this);
            applyAllFilters();
        }});
        
        // Individual country checkboxes
        document.querySelectorAll('.country-filter').forEach(function(cb) {{
            cb.addEventListener('change', function() {{
                var allChecked = Array.from(document.querySelectorAll('.country-filter')).every(function(c) {{
                    return c.checked;
                }});
                document.getElementById('filter-all').checked = allChecked;
                applyAllFilters();
            }});
        }});
        
        // Source filter checkboxes
        document.querySelectorAll('.source-filter').forEach(function(cb) {{
            cb.addEventListener('change', applyAllFilters);
        }});
        
        // Altitude sliders
        document.getElementById('min-altitude').addEventListener('input', function() {{
            document.getElementById('min-altitude-value').textContent = this.value + ' m';
            applyAllFilters();
        }});
        
        document.getElementById('max-altitude').addEventListener('input', function() {{
            document.getElementById('max-altitude-value').textContent = this.value + ' m';
            applyAllFilters();
        }});
        
        // Capacity filter
        document.getElementById('min-capacity').addEventListener('input', function() {{
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(applyAllFilters, 300);
        }});
        
        // Reset filters button
        document.getElementById('reset-filters').addEventListener('click', resetAllFilters);
        
        // Export KMZ button
        document.getElementById('export-kmz').addEventListener('click', exportToKMZ);
        
        // Search input with debounce
        var searchTimeout;
        document.getElementById('search-input').addEventListener('input', function() {{
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(applyAllFilters, 500);
        }});
        
        // Initial stats
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
