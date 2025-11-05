"""
Create a super simple HTML map with NO special characters in embedded data
"""
import sqlite3
from pathlib import Path
import json

def clean_string(s):
    """Remove any problematic characters - keep it simple, JSON will handle escaping"""
    if not s:
        return "N/A"
    # Convert to string and normalize whitespace
    s = str(s)
    s = s.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
    # Remove any control characters except spaces
    s = ''.join(char for char in s if ord(char) >= 32 or char == ' ')
    return s.strip() or "N/A"

def create_simple_map():
    # Connect to database
    db_path = Path(__file__).parent.parent / "data" / "mountain_huts.db"
    conn = sqlite3.connect(db_path)
    
    # Get all huts with coordinates
    cursor = conn.execute("""
        SELECT name, latitude, longitude, altitude, country, hut_type, website, source,
               owner, manager, phone, email, opening_hours, description,
               capacity, capacity_max, comments, water_source, best_time_to_visit, access, posted_by, url
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
        
        # Minimal color scheme - simple and clean
        if source == 'boudy.info':
            color = '#2563eb'  # clean blue
        elif source == 'mountain-huts.net':
            color = '#dc2626'  # clean red
        elif source == 'mountainhuts.info':
            color = '#16a34a'  # clean green
        elif source == 'refuges.info':
            color = '#ea580c'  # clean orange
        else:
            color = '#64748b'  # clean gray
        
        # Get URL (last field - index 21)
        url = clean_string(hut[21]) if len(hut) > 21 and hut[21] else ""
        
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
            'posted_by': posted_by,
            'url': url
        })
    
    # Write JSON to separate file to avoid embedding issues
    json_path = Path(__file__).parent.parent / "website" / "huts_data.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(huts_data, f, indent=2, ensure_ascii=True)
    
    print(f"Created JSON data file at {json_path}")
    
    # Create HTML that loads data via fetch
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
            background: #ffffff;
            color: #1e293b;
            overflow-y: auto;
            box-shadow: 4px 0 20px rgba(0,0,0,0.08);
            z-index: 1001;
            display: flex;
            flex-direction: column;
            border-right: 1px solid #e2e8f0;
        }}
        
        .sidebar-header {{
            padding: 30px 25px 20px;
            background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
            color: white;
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
            border-bottom: 2px solid #e2e8f0;
            padding-bottom: 8px;
            color: #0f172a;
        }}
        
        .filter-group {{
            margin-bottom: 20px;
        }}
        
        .filter-group label {{
            display: block;
            margin-bottom: 8px;
            font-size: 13px;
            color: #475569;
            font-weight: 500;
        }}
        
        .filter-group input[type="text"],
        .filter-group input[type="number"],
        .filter-group select {{
            width: 100%;
            padding: 10px;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            font-size: 14px;
            background: #f8fafc;
            color: #1e293b;
            transition: all 0.2s ease;
        }}
        
        .filter-group input[type="text"]::placeholder {{
            color: #94a3b8;
        }}
        
        .filter-group input[type="text"]:focus,
        .filter-group input[type="number"]:focus,
        .filter-group select:focus {{
            outline: none;
            background: #ffffff;
            border-color: #334155;
            box-shadow: 0 0 0 3px rgba(51, 65, 85, 0.1);
        }}
        
        .checkbox-list {{
            max-height: 250px;
            overflow-y: auto;
            background: #f8fafc;
            padding: 10px;
            border-radius: 8px;
            border: 1px solid #e2e8f0;
        }}
        
        .checkbox-list label {{
            display: flex;
            align-items: center;
            padding: 6px 8px;
            cursor: pointer;
            border-radius: 6px;
            transition: background 0.2s ease;
            font-size: 13px;
            color: #475569;
        }}
        
        .checkbox-list label:hover {{
            background: #e2e8f0;
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
            background: #1e293b;
            color: white;
            border: none;
            box-shadow: 0 2px 8px rgba(30, 41, 59, 0.15);
        }}
        
        .btn-primary:hover {{
            background: #334155;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(30, 41, 59, 0.25);
        }}
        
        .btn-secondary {{
            background: #ffffff;
            color: #1e293b;
            border: 1px solid #e2e8f0;
        }}
        
        .btn-secondary:hover {{
            background: #f8fafc;
            border-color: #cbd5e1;
            transform: translateY(-2px);
        }}
        
        /* Altitude Slider - Enhanced Visibility */
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
            height: 8px;
            border-radius: 4px;
            background: #e2e8f0;
            outline: none;
            margin: 8px 0;
            cursor: pointer;
        }}
        
        input[type="range"]::-webkit-slider-thumb {{
            -webkit-appearance: none;
            appearance: none;
            width: 20px;
            height: 20px;
            border-radius: 50%;
            background: #334155;
            cursor: pointer;
            box-shadow: 0 2px 8px rgba(0,0,0,0.25);
            transition: all 0.2s ease;
            border: 2px solid white;
        }}
        
        input[type="range"]::-webkit-slider-thumb:hover {{
            background: #1e293b;
            transform: scale(1.15);
            box-shadow: 0 3px 12px rgba(0,0,0,0.35);
        }}
        
        input[type="range"]::-moz-range-thumb {{
            width: 20px;
            height: 20px;
            border-radius: 50%;
            background: #334155;
            cursor: pointer;
            border: 2px solid white;
            box-shadow: 0 2px 8px rgba(0,0,0,0.25);
            transition: all 0.2s ease;
        }}
        
        input[type="range"]::-moz-range-thumb:hover {{
            background: #1e293b;
            transform: scale(1.15);
            box-shadow: 0 3px 12px rgba(0,0,0,0.35);
        }}
        
        input[type="range"]::-moz-range-track {{
            background: #e2e8f0;
            height: 8px;
            border-radius: 4px;
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
        
        /* Modern Minimal Marker Cluster Styling */
        .marker-cluster-small {{
            background-color: rgba(100, 116, 139, 0.3);
            border: 2px solid rgba(71, 85, 105, 0.5);
        }}
        .marker-cluster-small div {{
            background-color: rgba(71, 85, 105, 0.9);
            color: white;
            font-weight: 600;
            font-size: 13px;
        }}
        .marker-cluster-medium {{
            background-color: rgba(51, 65, 85, 0.3);
            border: 2px solid rgba(30, 41, 59, 0.5);
        }}
        .marker-cluster-medium div {{
            background-color: rgba(30, 41, 59, 0.9);
            color: white;
            font-weight: 600;
            font-size: 14px;
        }}
        .marker-cluster-large {{
            background-color: rgba(30, 41, 59, 0.3);
            border: 2px solid rgba(15, 23, 42, 0.6);
        }}
        .marker-cluster-large div {{
            background-color: rgba(15, 23, 42, 0.95);
            color: white;
            font-weight: 600;
            font-size: 15px;
        }}
        
        /* Toggle Button for Mobile */
        .toggle-panel {{
            display: none;
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 10000;
            background: white;
            border: none;
            padding: 14px 18px;
            border-radius: 12px;
            box-shadow: 0 4px 16px rgba(0,0,0,0.2);
            cursor: pointer;
            font-size: 20px;
            font-weight: 600;
            transition: all 0.2s ease;
            color: #1e293b;
        }}
        
        .toggle-panel:hover {{
            transform: scale(1.08);
            box-shadow: 0 6px 20px rgba(0,0,0,0.3);
        }}
        
        .toggle-panel:active {{
            transform: scale(0.98);
        }}
        
        /* Tablet Optimization */
        @media (max-width: 1024px) {{
            .sidebar {{
                width: 320px;
            }}
            .sidebar-header h1 {{
                font-size: 20px;
            }}
            .sidebar-header p {{
                font-size: 13px;
            }}
        }}
        
        /* Mobile Optimization */
        @media (max-width: 768px) {{
            body {{
                flex-direction: column;
                overflow: auto;
            }}
            
            .sidebar {{
                position: fixed;
                width: 100%;
                height: auto;
                max-height: 70vh;
                bottom: 0;
                top: auto;
                left: 0;
                right: 0;
                transform: translateY(calc(100% - 60px));
                transition: transform 0.3s ease;
                box-shadow: 0 -4px 20px rgba(0,0,0,0.15);
                border-right: none;
                border-top: 3px solid #334155;
                z-index: 9999;
            }}
            
            .sidebar.open {{
                transform: translateY(0);
            }}
            
            .sidebar-header {{
                padding: 16px 20px;
                cursor: pointer;
                position: relative;
            }}
            
            .sidebar-header::after {{
                content: '▼';
                position: absolute;
                right: 20px;
                top: 50%;
                transform: translateY(-50%);
                font-size: 20px;
                transition: transform 0.3s ease;
            }}
            
            .sidebar.open .sidebar-header::after {{
                transform: translateY(-50%) rotate(180deg);
            }}
            
            .sidebar-header h1 {{
                font-size: 18px;
            }}
            
            .sidebar-header p {{
                display: none;
            }}
            
            .sidebar-content {{
                padding: 20px;
                max-height: calc(70vh - 60px);
                overflow-y: auto;
            }}
            
            #map {{
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                width: 100%;
                height: 100vh;
                z-index: 1;
            }}
            
            .toggle-panel {{
                display: block;
            }}
            
            .filter-section {{
                margin-bottom: 20px;
            }}
            
            .filter-section h3 {{
                font-size: 14px;
            }}
            
            .checkbox-list {{
                max-height: 200px;
            }}
            
            .action-buttons {{
                position: sticky;
                bottom: 0;
                background: white;
                padding: 15px 0 0;
                margin-top: 20px;
                border-top: 2px solid #e2e8f0;
            }}
        }}
        
        /* Small Mobile Phones */
        @media (max-width: 480px) {{
            .sidebar {{
                max-height: 80vh;
            }}
            
            .sidebar-header h1 {{
                font-size: 16px;
            }}
            
            .filter-section h3 {{
                font-size: 13px;
            }}
            
            .btn {{
                padding: 10px 16px;
                font-size: 13px;
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
            <!-- Map Layer Selector -->
            <div class="filter-section">
                <h3>🗺️ Map Layer</h3>
                <div class="filter-group" style="display: flex; flex-direction: column; gap: 8px;">
                    <label style="display: flex; align-items: center; padding: 10px; border: 1px solid #e2e8f0; border-radius: 8px; cursor: pointer; transition: all 0.2s; background: #f8fafc;">
                        <input type="radio" name="map-layer" value="openstreetmap" style="margin-right: 10px; width: 18px; height: 18px; cursor: pointer;">
                        <span style="font-weight: 500; color: #1e293b;">OpenStreetMap</span>
                    </label>
                    <label style="display: flex; align-items: center; padding: 10px; border: 1px solid #e2e8f0; border-radius: 8px; cursor: pointer; transition: all 0.2s; background: #f8fafc;">
                        <input type="radio" name="map-layer" value="topo" style="margin-right: 10px; width: 18px; height: 18px; cursor: pointer;">
                        <span style="font-weight: 500; color: #1e293b;">Topographic</span>
                    </label>
                    <label style="display: flex; align-items: center; padding: 10px; border: 1px solid #e2e8f0; border-radius: 8px; cursor: pointer; transition: all 0.2s; background: #f8fafc;">
                        <input type="radio" name="map-layer" value="cyclosm" style="margin-right: 10px; width: 18px; height: 18px; cursor: pointer;">
                        <span style="font-weight: 500; color: #1e293b;">Outdoor/Hiking</span>
                    </label>
                    <label style="display: flex; align-items: center; padding: 10px; border: 1px solid #e2e8f0; border-radius: 8px; cursor: pointer; transition: all 0.2s; background: #f8fafc;">
                        <input type="radio" name="map-layer" value="humanitarian" style="margin-right: 10px; width: 18px; height: 18px; cursor: pointer;">
                        <span style="font-weight: 500; color: #1e293b;">Humanitarian</span>
                    </label>
                    <label style="display: flex; align-items: center; padding: 10px; border: 1px solid #334155; border-radius: 8px; cursor: pointer; transition: all 0.2s; background: #334155;">
                        <input type="radio" name="map-layer" value="relief" checked style="margin-right: 10px; width: 18px; height: 18px; cursor: pointer;">
                        <span style="font-weight: 500; color: white;">Relief Shading ⭐</span>
                    </label>
                    <label style="display: flex; align-items: center; padding: 10px; border: 1px solid #e2e8f0; border-radius: 8px; cursor: pointer; transition: all 0.2s; background: #f8fafc;">
                        <input type="radio" name="map-layer" value="light" style="margin-right: 10px; width: 18px; height: 18px; cursor: pointer;">
                        <span style="font-weight: 500; color: #1e293b;">Light (Minimal)</span>
                    </label>
                    <label style="display: flex; align-items: center; padding: 10px; border: 1px solid #e2e8f0; border-radius: 8px; cursor: pointer; transition: all 0.2s; background: #f8fafc;">
                        <input type="radio" name="map-layer" value="satellite" style="margin-right: 10px; width: 18px; height: 18px; cursor: pointer;">
                        <span style="font-weight: 500; color: #1e293b;">Satellite</span>
                    </label>
                </div>
            </div>
            
            <!-- Quick Presets -->
            <div class="filter-section">
                <h3>⚡ Quick Filters</h3>
                <div class="filter-group" style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px;">
                    <button class="btn btn-secondary" onclick="applyPreset('high-altitude')" style="font-size: 12px; padding: 8px;">🏔️ High Alt</button>
                    <button class="btn btn-secondary" onclick="applyPreset('large-capacity')" style="font-size: 12px; padding: 8px;">🏨 Large</button>
                    <button class="btn btn-secondary" onclick="applyPreset('with-contact')" style="font-size: 12px; padding: 8px;">📞 Contact</button>
                    <button class="btn btn-secondary" onclick="applyPreset('open-now')" style="font-size: 12px; padding: 8px;">🟢 Open</button>
                </div>
            </div>
            
            <!-- Hut Type Filter - MOVED UP AS FIRST FILTER -->
            <div class="filter-section">
                <h3>🏠 Hut Type</h3>
                <div class="filter-group">
                    <label><input type="checkbox" class="type-filter" value="Mountain hut" checked> Mountain Hut</label>
                    <label><input type="checkbox" class="type-filter" value="Bivouac" checked> Bivouac</label>
                    <label><input type="checkbox" class="type-filter" value="Unmanned cabin" checked> Basic Shelter</label>
                    <label><input type="checkbox" class="type-filter" value="Shelter" checked> Shelter</label>
                    <label><input type="checkbox" class="type-filter" value="Guesthouse" checked> Guesthouse</label>
                    <label><input type="checkbox" class="type-filter" value="Unknown" checked> Unknown</label>
                </div>
            </div>
            
            <!-- Contact & Info Filter - MERGED WITH ADVANCED -->
            <div class="filter-section">
                <h3>📞 Contact & Info</h3>
                <div class="filter-group">
                    <label><input type="checkbox" id="filter-has-phone"> Has Phone Number</label>
                    <label><input type="checkbox" id="filter-has-email"> Has Email</label>
                    <label><input type="checkbox" id="filter-has-website"> Has Website</label>
                    <label><input type="checkbox" id="filter-has-hours"> Has Opening Hours</label>
                    <label><input type="checkbox" id="filter-has-manager"> Has Manager Info</label>
                    <label><input type="checkbox" id="filter-has-owner"> Has Owner Info</label>
                    <label><input type="checkbox" id="filter-has-description"> Has Description</label>
                </div>
            </div>
            
            <!-- Altitude Filter -->
            <div class="filter-section">
                <h3>⛰️ Altitude</h3>
                <div class="filter-group">
                    <label style="font-weight: 600; margin-bottom: 12px;">Range: <span id="altitude-range" style="color: #334155;">0 - 4000 m</span></label>
                    <div class="slider-container">
                        <div style="margin-bottom: 8px;">
                            <label style="font-size: 12px; color: #64748b;">Minimum</label>
                            <input type="range" id="min-altitude" min="0" max="4000" value="0" step="50" style="width: 100%; height: 8px; background: linear-gradient(to right, #334155 0%, #334155 0%, #e2e8f0 0%, #e2e8f0 100%); border-radius: 4px; outline: none; -webkit-appearance: none;">
                        </div>
                        <div>
                            <label style="font-size: 12px; color: #64748b;">Maximum</label>
                            <input type="range" id="max-altitude" min="0" max="4000" value="4000" step="50" style="width: 100%; height: 8px; background: linear-gradient(to right, #334155 0%, #334155 100%, #e2e8f0 100%, #e2e8f0 100%); border-radius: 4px; outline: none; -webkit-appearance: none;">
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Capacity Filter -->
            <div class="filter-section">
                <h3>🛏️ Capacity</h3>
                <div class="filter-group">
                    <label for="min-capacity">Minimum Beds</label>
                    <input type="number" id="min-capacity" placeholder="Any" min="0" style="width: 100%;">
                </div>
                <div class="filter-group">
                    <label for="max-capacity">Maximum Beds</label>
                    <input type="number" id="max-capacity" placeholder="Any" min="0" style="width: 100%;">
                </div>
            </div>
            
            <!-- Country Filter - MOVED DOWN -->
            <div class="filter-section">
                <h3>🌍 Countries <span id="country-count" style="opacity: 0.6; font-size: 12px;"></span></h3>
                <div class="filter-group">
                    <label><input type="checkbox" id="filter-all" checked> <strong>All Countries</strong></label>
                </div>
                <div class="checkbox-list" id="country-filters"></div>
            </div>
            
            <!-- Data Source Filter -->
            <div class="filter-section">
                <h3>📍 Data Sources</h3>
                <div class="filter-group">
                    <label><input type="checkbox" class="source-filter" value="mountainhuts.info" checked> <span class="legend-color" style="background: #16a34a;"></span> Mountainhuts.info</label>
                    <label><input type="checkbox" class="source-filter" value="boudy.info" checked> <span class="legend-color" style="background: #2563eb;"></span> Boudy.info</label>
                    <label><input type="checkbox" class="source-filter" value="mountain-huts.net" checked> <span class="legend-color" style="background: #dc2626;"></span> Mountain-huts.net</label>
                    <label><input type="checkbox" class="source-filter" value="refuges.info" checked> <span class="legend-color" style="background: #ea580c;"></span> Refuges.info</label>
                </div>
            </div>
            
            <!-- Active Filters Summary -->
            <div class="filter-section" id="active-filters-section" style="display: none;">
                <h3>🎯 Active Filters</h3>
                <div id="active-filters-list" style="font-size: 11px; color: rgba(255,255,255,0.8);"></div>
            </div>
            
            <!-- Action Buttons -->
            <div class="action-buttons">
                <button class="btn btn-secondary" id="reset-filters">🔄 Reset All</button>
                <button class="btn btn-primary" id="export-kmz">📥 Export KMZ</button>
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
        
        // Define all available map layers - all tested and working
        var layers = {{
            'openstreetmap': L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
                maxZoom: 19,
                attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            }}),
            'topo': L.tileLayer('https://{{s}}.tile.opentopomap.org/{{z}}/{{x}}/{{y}}.png', {{
                maxZoom: 17,
                attribution: 'Map data: &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, <a href="http://viewfinderpanoramas.org">SRTM</a> | Map style: &copy; <a href="https://opentopomap.org">OpenTopoMap</a> (<a href="https://creativecommons.org/licenses/by-sa/3.0/">CC-BY-SA</a>)'
            }}),
            'cyclosm': L.tileLayer('https://{{s}}.tile-cyclosm.openstreetmap.fr/cyclosm/{{z}}/{{x}}/{{y}}.png', {{
                maxZoom: 20,
                attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors | Tiles style by <a href="https://www.cyclosm.org">CyclOSM</a>'
            }}),
            'humanitarian': L.tileLayer('https://{{s}}.tile.openstreetmap.fr/hot/{{z}}/{{x}}/{{y}}.png', {{
                maxZoom: 19,
                attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors | Tiles style by <a href="https://www.hotosm.org/">Humanitarian OpenStreetMap Team</a>'
            }}),
            'relief': L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Shaded_Relief/MapServer/tile/{{z}}/{{y}}/{{x}}', {{
                maxZoom: 13,
                attribution: 'Tiles &copy; Esri &mdash; Source: Esri'
            }}),
            'light': L.tileLayer('https://{{s}}.basemaps.cartocdn.com/light_all/{{z}}/{{x}}/{{y}}.png', {{
                maxZoom: 19,
                attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
            }}),
            'satellite': L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{{z}}/{{y}}/{{x}}', {{
                maxZoom: 19,
                attribution: 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'
            }})
        }};
        
        // Add default layer (Relief Shading - known to work)
        var currentLayer = layers['relief'];
        currentLayer.addTo(map);
        
        // Map layer radio button functionality
        var layerRadios = document.querySelectorAll('input[name="map-layer"]');
        layerRadios.forEach(function(radio) {{
            radio.addEventListener('change', function(e) {{
                if (e.target.checked) {{
                    var selectedLayer = e.target.value;
                    
                    // Remove current layer
                    if (currentLayer) {{
                        map.removeLayer(currentLayer);
                    }}
                    
                    // Add new layer
                    currentLayer = layers[selectedLayer];
                    currentLayer.addTo(map);
                    
                    // Update visual feedback
                    layerRadios.forEach(function(r) {{
                        var label = r.closest('label');
                        if (r.checked) {{
                            label.style.background = '#334155';
                            label.style.borderColor = '#334155';
                            label.querySelector('span').style.color = 'white';
                        }} else {{
                            label.style.background = '#f8fafc';
                            label.style.borderColor = '#e2e8f0';
                            label.querySelector('span').style.color = '#1e293b';
                        }}
                    }});
                }}
            }});
        }});
        
        // Load huts data from external JSON file
        fetch('huts_data.json')
            .then(response => response.json())
            .then(data => {{
                initializeMap(data);
            }})
            .catch(error => {{
                console.error('Error loading huts data:', error);
                alert('Error loading map data. Please refresh the page.');
            }});
        
        function initializeMap(huts) {{
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
            // Build beautiful modern popup content
            var popupParts = [];
            
            // Modern card container with rounded corners and shadow
            popupParts.push('<div style="font-family: -apple-system, BlinkMacSystemFont, \\'Segoe UI\\', Roboto, sans-serif; min-width: 280px; max-width: 320px; margin: -12px; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.08);">');
            
            // Header section with gradient background
            popupParts.push('<div style="background: linear-gradient(135deg, #1e293b 0%, #334155 100%); padding: 16px 20px; color: white;">');
            popupParts.push('<h3 style="margin: 0 0 8px 0; font-size: 18px; font-weight: 700; line-height: 1.3;">' + escapeHtml(hut.name) + '</h3>');
            
            // Key info badges in header
            var headerBadges = [];
            if (hut.altitude && hut.altitude !== 'N/A') {{
                headerBadges.push('<span style="display: inline-block; background: rgba(255,255,255,0.2); padding: 4px 10px; border-radius: 12px; font-size: 12px; font-weight: 600; margin-right: 6px;">🏔️ ' + escapeHtml(String(hut.altitude)) + ' m</span>');
            }}
            if (hut.country && hut.country !== 'N/A') {{
                headerBadges.push('<span style="display: inline-block; background: rgba(255,255,255,0.2); padding: 4px 10px; border-radius: 12px; font-size: 12px; font-weight: 600;">🌍 ' + escapeHtml(hut.country) + '</span>');
            }}
            if (headerBadges.length > 0) {{
                popupParts.push('<div style="margin-top: 4px;">' + headerBadges.join('') + '</div>');
            }}
            popupParts.push('</div>');
            
            // Body section with white background
            popupParts.push('<div style="background: white; padding: 16px 20px;">');
            
            // Type and capacity in a nice grid
            var infoItems = [];
            if (hut.type && hut.type !== 'N/A') {{
                infoItems.push('<div style="display: flex; align-items: center; padding: 8px 12px; background: #f8fafc; border-radius: 8px; margin-bottom: 8px;"><span style="font-size: 20px; margin-right: 10px;">🏠</span><div style="flex: 1;"><div style="font-size: 11px; color: #64748b; text-transform: uppercase; font-weight: 600; letter-spacing: 0.5px;">Type</div><div style="font-size: 14px; color: #1e293b; font-weight: 600;">' + escapeHtml(hut.type) + '</div></div></div>');
            }}
            
            if (hut.capacity && hut.capacity !== 'N/A' && hut.capacity !== '') {{
                var capacityText = escapeHtml(String(hut.capacity));
                if (hut.capacity_max && hut.capacity_max !== 'N/A' && hut.capacity_max !== '') {{
                    capacityText += ' (max: ' + escapeHtml(String(hut.capacity_max)) + ')';
                }}
                infoItems.push('<div style="display: flex; align-items: center; padding: 8px 12px; background: #f8fafc; border-radius: 8px; margin-bottom: 8px;"><span style="font-size: 20px; margin-right: 10px;">🛏️</span><div style="flex: 1;"><div style="font-size: 11px; color: #64748b; text-transform: uppercase; font-weight: 600; letter-spacing: 0.5px;">Capacity</div><div style="font-size: 14px; color: #1e293b; font-weight: 600;">' + capacityText + ' beds</div></div></div>');
            }}
            
            if (infoItems.length > 0) {{
                popupParts.push(infoItems.join(''));
            }}
            
            // Additional details section
            var details = [];
            if (hut.water_source && hut.water_source !== 'N/A' && hut.water_source !== '') {{
                details.push('<div style="display: flex; padding: 6px 0; border-bottom: 1px solid #f1f5f9; font-size: 13px;"><span style="min-width: 24px; margin-right: 8px;">💧</span><span style="color: #475569;">' + escapeHtml(hut.water_source) + '</span></div>');
            }}
            if (hut.access && hut.access !== 'N/A' && hut.access !== '') {{
                details.push('<div style="display: flex; padding: 6px 0; border-bottom: 1px solid #f1f5f9; font-size: 13px;"><span style="min-width: 24px; margin-right: 8px;">🥾</span><span style="color: #475569;">' + escapeHtml(hut.access) + '</span></div>');
            }}
            if (hut.best_time && hut.best_time !== 'N/A' && hut.best_time !== '') {{
                details.push('<div style="display: flex; padding: 6px 0; border-bottom: 1px solid #f1f5f9; font-size: 13px;"><span style="min-width: 24px; margin-right: 8px;">📅</span><span style="color: #475569;">' + escapeHtml(hut.best_time) + '</span></div>');
            }}
            if (details.length > 0) {{
                popupParts.push('<div style="margin: 12px 0; padding: 8px 0;">' + details.join('') + '</div>');
            }}
            
            // Management info
            if ((hut.owner && hut.owner !== 'N/A' && hut.owner !== '') || (hut.manager && hut.manager !== 'N/A' && hut.manager !== '')) {{
                popupParts.push('<div style="margin: 12px 0; padding: 10px; background: #fef3c7; border-left: 3px solid #f59e0b; border-radius: 6px; font-size: 12px;">');
                if (hut.owner && hut.owner !== 'N/A' && hut.owner !== '') {{
                    popupParts.push('<div style="margin-bottom: 4px; color: #92400e;"><strong>Owner:</strong> ' + escapeHtml(hut.owner) + '</div>');
                }}
                if (hut.manager && hut.manager !== 'N/A' && hut.manager !== '') {{
                    popupParts.push('<div style="color: #92400e;"><strong>Manager:</strong> ' + escapeHtml(hut.manager) + '</div>');
                }}
                popupParts.push('</div>');
            }}
            
            // Opening hours - prominent if available
            if (hut.opening && hut.opening !== 'N/A' && hut.opening !== '') {{
                popupParts.push('<div style="margin: 12px 0; padding: 10px; background: #d1fae5; border-left: 3px solid #10b981; border-radius: 6px; font-size: 13px; color: #065f46; font-weight: 500;">🕐 ' + escapeHtml(hut.opening) + '</div>');
            }}
            
            // Contact buttons - modern icon buttons
            var contactButtons = [];
            if (hut.phone && hut.phone !== 'N/A' && hut.phone !== '') {{
                contactButtons.push('<a href="tel:' + escapeHtml(hut.phone) + '" style="flex: 1; display: flex; align-items: center; justify-content: center; gap: 6px; padding: 10px; background: #10b981; color: white; text-decoration: none; border-radius: 8px; font-weight: 600; font-size: 13px; transition: background 0.2s;" onmouseover="this.style.background=\\'#059669\\';" onmouseout="this.style.background=\\'#10b981\\';"><span style="font-size: 16px;">📞</span> Call</a>');
            }}
            if (hut.email && hut.email !== 'N/A' && hut.email !== '') {{
                contactButtons.push('<a href="mailto:' + escapeHtml(hut.email) + '" style="flex: 1; display: flex; align-items: center; justify-content: center; gap: 6px; padding: 10px; background: #3b82f6; color: white; text-decoration: none; border-radius: 8px; font-weight: 600; font-size: 13px; transition: background 0.2s;" onmouseover="this.style.background=\\'#2563eb\\';" onmouseout="this.style.background=\\'#3b82f6\\';"><span style="font-size: 16px;">📧</span> Email</a>');
            }}
            if (hut.website && hut.website !== 'N/A' && hut.website !== '') {{
                var websiteUrl = hut.website.startsWith('http') ? hut.website : 'http://' + hut.website;
                contactButtons.push('<a href="' + websiteUrl + '" target="_blank" rel="noopener" style="flex: 1; display: flex; align-items: center; justify-content: center; gap: 6px; padding: 10px; background: #8b5cf6; color: white; text-decoration: none; border-radius: 8px; font-weight: 600; font-size: 13px; transition: background 0.2s;" onmouseover="this.style.background=\\'#7c3aed\\';" onmouseout="this.style.background=\\'#8b5cf6\\';"><span style="font-size: 16px;">🌐</span> Web</a>');
            }}
            if (contactButtons.length > 0) {{
                popupParts.push('<div style="display: flex; gap: 8px; margin: 12px 0;">' + contactButtons.join('') + '</div>');
            }}
            
            // Description or comments
            if (hut.description && hut.description !== 'N/A' && hut.description !== '' && hut.description.length < 200) {{
                popupParts.push('<div style="margin: 12px 0; padding: 10px; background: #f0f9ff; border-radius: 6px; font-size: 13px; color: #0c4a6e; line-height: 1.5;">' + escapeHtml(hut.description) + '</div>');
            }} else if (hut.comments && hut.comments !== 'N/A' && hut.comments !== '' && hut.comments.length < 200) {{
                popupParts.push('<div style="margin: 12px 0; padding: 10px; background: #f0f9ff; border-radius: 6px; font-size: 13px; color: #0c4a6e; line-height: 1.5;"><strong>💬</strong> ' + escapeHtml(hut.comments) + '</div>');
            }}
            
            popupParts.push('</div>'); // End body
            
            // Footer section with source link - PROMINENT
            popupParts.push('<div style="background: #f8fafc; padding: 14px 20px; border-top: 1px solid #e2e8f0;">');
            if (hut.url && hut.url !== 'N/A' && hut.url !== '' && hut.url !== 'http://www.mountainhuts.info/map') {{
                popupParts.push('<a href="' + escapeHtml(hut.url) + '" target="_blank" rel="noopener" style="display: flex; align-items: center; justify-content: center; gap: 8px; padding: 12px 20px; background: linear-gradient(135deg, #2563eb, #3b82f6); color: white; text-decoration: none; border-radius: 10px; font-weight: 700; font-size: 14px; box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3); transition: all 0.3s ease; text-align: center;" onmouseover="this.style.transform=\\'translateY(-2px) scale(1.02)\\'; this.style.boxShadow=\\'0 6px 20px rgba(37, 99, 235, 0.4)\\';" onmouseout="this.style.transform=\\'translateY(0) scale(1)\\'; this.style.boxShadow=\\'0 4px 12px rgba(37, 99, 235, 0.3)\\';">📍 View Full Details on ' + escapeHtml(hut.source) + ' <span style="font-size: 16px;">→</span></a>');
            }} else {{
                popupParts.push('<div style="text-align: center; font-size: 12px; color: #94a3b8; padding: 4px;">Data from <strong>' + escapeHtml(hut.source) + '</strong></div>');
            }}
            
            // Posted by (if available)
            if (hut.posted_by && hut.posted_by !== 'N/A' && hut.posted_by !== '') {{
                popupParts.push('<div style="margin-top: 8px; text-align: center; font-size: 11px; color: #94a3b8;">Posted by ' + escapeHtml(hut.posted_by) + '</div>');
            }}
            popupParts.push('</div>'); // End footer
            
            popupParts.push('</div>'); // End container
            
            var popup = popupParts.join('');
            
            var marker = L.circleMarker([hut.lat, hut.lon], {{
                radius: 4,
                fillColor: hut.color,
                color: '#ffffff',
                weight: 1,
                opacity: 0.8,
                fillOpacity: 0.9
            }});
            
            // Minimal hover effects
            marker.on('mouseover', function(e) {{
                this.setStyle({{
                    radius: 6,
                    weight: 2,
                    fillOpacity: 1,
                    opacity: 1
                }});
            }});
            
            marker.on('mouseout', function(e) {{
                this.setStyle({{
                    radius: 4,
                    weight: 1,
                    fillOpacity: 0.9,
                    opacity: 0.8
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
            var searchText = '';  // Search removed from UI
            var minAltitude = parseInt(document.getElementById('min-altitude').value) || 0;
            var maxAltitude = parseInt(document.getElementById('max-altitude').value) || 999999;
            var minCapacity = parseInt(document.getElementById('min-capacity').value) || 0;
            var maxCapacity = parseInt(document.getElementById('max-capacity').value) || 999999;
            
            // Get checked countries
            var checkedCountries = [];
            var countryCheckboxes = document.querySelectorAll('.country-filter');
            countryCheckboxes.forEach(function(cb) {{
                if (cb.checked) {{
                    checkedCountries.push(cb.dataset.country);
                }}
            }});
            
            // Get checked hut types
            var checkedTypes = [];
            var typeCheckboxes = document.querySelectorAll('.type-filter');
            typeCheckboxes.forEach(function(cb) {{
                if (cb.checked) {{
                    checkedTypes.push(cb.value);
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
            
            // Get contact/info filters
            var filterHasPhone = document.getElementById('filter-has-phone').checked;
            var filterHasEmail = document.getElementById('filter-has-email').checked;
            var filterHasWebsite = document.getElementById('filter-has-website').checked;
            var filterHasHours = document.getElementById('filter-has-hours').checked;
            
            // Get advanced filters
            var filterHasManager = document.getElementById('filter-has-manager').checked;
            var filterHasOwner = document.getElementById('filter-has-owner').checked;
            var filterHasDescription = document.getElementById('filter-has-description').checked;
            
            // Build active filters list
            var activeFilters = [];
            
            // Filter markers
            markers.forEach(function(marker) {{
                var hut = marker.hutData;
                var show = true;
                
                // Search filter
                if (searchText && hut.name.toLowerCase().indexOf(searchText) === -1) {{
                    show = false;
                }}
                
                // Country filter
                // Only apply if some (but not all) countries are selected
                var allCountriesChecked = document.getElementById('filter-all').checked;
                if (!allCountriesChecked && checkedCountries.length > 0) {{
                    // Filtering is active
                    if (hut.country && hut.country !== 'N/A' && hut.country !== '') {{
                        // Hut has a country - check if it's in the selected list
                        if (checkedCountries.indexOf(hut.country) === -1) {{
                            show = false;
                        }}
                    }}
                    // Huts without country data: always show them (can't be filtered by country)
                }}
                
                // Hut type filter
                if (checkedTypes.length > 0) {{
                    if (hut.type && hut.type !== 'N/A' && hut.type !== '') {{
                        if (checkedTypes.indexOf(hut.type) === -1) {{
                            show = false;
                        }}
                    }}
                    // Huts without type: keep visible (can't be filtered by type)
                }}
                
                // Source filter
                if (checkedSources.length > 0) {{
                    if (hut.source && hut.source !== 'N/A' && hut.source !== '') {{
                        if (checkedSources.indexOf(hut.source) === -1) {{
                            show = false;
                        }}
                    }}
                    // Huts without source: keep visible
                }}
                
                // Altitude filter
                var altitude = parseInt(hut.altitude);
                if (!isNaN(altitude)) {{
                    if (altitude < minAltitude || altitude > maxAltitude) {{
                        show = false;
                    }}
                }}
                
                // Capacity filter (min and max)
                var capacity = parseInt(hut.capacity);
                if (!isNaN(capacity)) {{
                    if (capacity < minCapacity || capacity > maxCapacity) {{
                        show = false;
                    }}
                }}
                
                // Contact/Info filters
                if (filterHasPhone && (!hut.phone || hut.phone === '' || hut.phone === 'N/A')) {{
                    show = false;
                }}
                if (filterHasEmail && (!hut.email || hut.email === '' || hut.email === 'N/A')) {{
                    show = false;
                }}
                if (filterHasWebsite && (!hut.website || hut.website === '' || hut.website === 'N/A')) {{
                    show = false;
                }}
                if (filterHasHours && (!hut.opening || hut.opening === '' || hut.opening === 'N/A')) {{
                    show = false;
                }}
                
                // Advanced filters
                if (filterHasManager && (!hut.manager || hut.manager === '' || hut.manager === 'N/A')) {{
                    show = false;
                }}
                if (filterHasOwner && (!hut.owner || hut.owner === '' || hut.owner === 'N/A')) {{
                    show = false;
                }}
                if (filterHasDescription && (!hut.description || hut.description === '' || hut.description === 'N/A')) {{
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
        
        // Quick preset filters
        function applyPreset(preset) {{
            resetAllFilters();
            
            if (preset === 'high-altitude') {{
                document.getElementById('min-altitude').value = 2000;
                document.getElementById('altitude-range').textContent = '2000 - 4000 m';
            }} else if (preset === 'large-capacity') {{
                document.getElementById('min-capacity').value = 50;
            }} else if (preset === 'with-contact') {{
                document.getElementById('filter-has-phone').checked = true;
                document.getElementById('filter-has-email').checked = true;
            }} else if (preset === 'open-now') {{
                document.getElementById('filter-has-hours').checked = true;
            }}
            
            applyAllFilters();
        }}
        
        // Reset all filters
        function resetAllFilters() {{
            // Search removed: document.getElementById('search-input').value = '';
            document.getElementById('min-altitude').value = 0;
            document.getElementById('max-altitude').value = 4000;
            document.getElementById('altitude-range').textContent = '0 - 4000 m';
            document.getElementById('min-capacity').value = '';
            document.getElementById('max-capacity').value = '';
            document.getElementById('filter-all').checked = true;
            
            // Reset type filters
            document.querySelectorAll('.type-filter').forEach(function(cb) {{
                cb.checked = true;
            }});
            
            // Reset country filters
            document.querySelectorAll('.country-filter').forEach(function(cb) {{
                cb.checked = true;
            }});
            
            // Reset source filters
            document.querySelectorAll('.source-filter').forEach(function(cb) {{
                cb.checked = true;
            }});
            
            // Reset contact/info filters
            document.getElementById('filter-has-phone').checked = false;
            document.getElementById('filter-has-email').checked = false;
            document.getElementById('filter-has-website').checked = false;
            document.getElementById('filter-has-hours').checked = false;
            
            // Reset advanced filters
            document.getElementById('filter-has-manager').checked = false;
            document.getElementById('filter-has-owner').checked = false;
            document.getElementById('filter-has-description').checked = false;
            
            applyAllFilters();
        }}
        
        // Update altitude range display
        function updateAltitudeRange() {{
            var min = document.getElementById('min-altitude').value;
            var max = document.getElementById('max-altitude').value;
            document.getElementById('altitude-range').textContent = min + ' - ' + max + ' m';
        }}
        
        // Update country count
        function updateCountryCount() {{
            var checked = document.querySelectorAll('.country-filter:checked').length;
            var total = document.querySelectorAll('.country-filter').length;
            if (checked === total) {{
                document.getElementById('country-count').textContent = '';
            }} else {{
                document.getElementById('country-count').textContent = '(' + checked + '/' + total + ')';
            }}
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
                updateCountryCount();
                applyAllFilters();
            }});
        }});
        
        // Hut type filter checkboxes
        document.querySelectorAll('.type-filter').forEach(function(cb) {{
            cb.addEventListener('change', applyAllFilters);
        }});
        
        // Source filter checkboxes
        document.querySelectorAll('.source-filter').forEach(function(cb) {{
            cb.addEventListener('change', applyAllFilters);
        }});
        
        // Contact/Info filter checkboxes
        document.getElementById('filter-has-phone').addEventListener('change', applyAllFilters);
        document.getElementById('filter-has-email').addEventListener('change', applyAllFilters);
        document.getElementById('filter-has-website').addEventListener('change', applyAllFilters);
        document.getElementById('filter-has-hours').addEventListener('change', applyAllFilters);
        
        // Advanced filter checkboxes
        document.getElementById('filter-has-manager').addEventListener('change', applyAllFilters);
        document.getElementById('filter-has-owner').addEventListener('change', applyAllFilters);
        document.getElementById('filter-has-description').addEventListener('change', applyAllFilters);
        
        // Altitude sliders
        document.getElementById('min-altitude').addEventListener('input', function() {{
            updateAltitudeRange();
            applyAllFilters();
        }});
        
        document.getElementById('max-altitude').addEventListener('input', function() {{
            updateAltitudeRange();
            applyAllFilters();
        }});
        
        // Capacity filters
        document.getElementById('min-capacity').addEventListener('input', function() {{
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(applyAllFilters, 300);
        }});
        
        document.getElementById('max-capacity').addEventListener('input', function() {{
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(applyAllFilters, 300);
        }});
        
        // Reset filters button
        document.getElementById('reset-filters').addEventListener('click', resetAllFilters);
        
        // Export KMZ button
        document.getElementById('export-kmz').addEventListener('click', exportToKMZ);
        
        // Search removed from UI - no event listener needed
        
        // Initial stats
        updateStats();
        console.log('Map ready with ' + markers.length + ' markers!');
        
        // Mobile sidebar toggle
        var sidebar = document.querySelector('.sidebar');
        var sidebarHeader = document.querySelector('.sidebar-header');
        
        // Toggle sidebar on header click (mobile only)
        if (sidebarHeader) {{
            sidebarHeader.addEventListener('click', function() {{
                if (window.innerWidth <= 768) {{
                    sidebar.classList.toggle('open');
                }}
            }});
        }}
        
        // Close sidebar when clicking on map (mobile only)
        map.on('click', function() {{
            if (window.innerWidth <= 768 && sidebar.classList.contains('open')) {{
                sidebar.classList.remove('open');
            }}
        }});
        
        // Handle window resize
        window.addEventListener('resize', function() {{
            if (window.innerWidth > 768) {{
                sidebar.classList.remove('open');
                sidebar.style.transform = '';
            }}
        }});
        
        }} // End of initializeMap function
    </script>
    
    <!-- Cookie Consent for GDPR Compliance -->
    <script src="website/js/cookie-consent.js"></script>
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

