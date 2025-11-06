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
    <!-- Fuse.js for fuzzy search -->
    <script src="https://cdn.jsdelivr.net/npm/fuse.js@6.6.2"></script>
    <style>
        * {{ 
            margin: 0; 
            padding: 0; 
            box-sizing: border-box; 
        }}
        
        body {{ 
            margin: 0; 
            padding: 0; 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f5f5f5;
            display: flex;
            overflow: hidden;
            -webkit-tap-highlight-color: rgba(0,0,0,0.1);
            -webkit-touch-callout: none;
        }}
        
        /* Allow text selection in important areas */
        .sidebar-content, .leaflet-popup-content {{
            -webkit-user-select: text;
            user-select: text;
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
            padding: 20px 25px 16px;
            background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
            color: white;
        }}
        
        .sidebar-header h1 {{
            font-size: 22px;
            margin: 0 0 8px 0;
            font-weight: 700;
        }}
        
        .sidebar-header p {{
            margin: 0 0 12px 0;
            font-size: 13px;
            opacity: 0.9;
            line-height: 1.5;
        }}
        
        /* Detail Sidebar - Overlays filter sidebar */
        .detail-sidebar {{
            position: fixed;
            left: 0;
            top: 0;
            width: 350px;
            height: 100vh;
            background: #ffffff;
            z-index: 1002;
            box-shadow: 4px 0 24px rgba(0,0,0,0.12);
            transform: translateX(-100%);
            transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            display: flex;
            flex-direction: column;
        }}
        
        .detail-sidebar.open {{
            transform: translateX(0);
        }}
        
        .detail-header {{
            background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
            color: white;
            padding: 16px 20px;
            display: flex;
            align-items: center;
            gap: 12px;
            border-bottom: 3px solid #475569;
            flex-shrink: 0;
        }}
        
        .back-button {{
            background: rgba(255,255,255,0.2);
            border: none;
            color: white;
            width: 40px;
            height: 40px;
            border-radius: 10px;
            cursor: pointer;
            font-size: 20px;
            font-weight: 700;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.2s ease;
            flex-shrink: 0;
        }}
        
        .back-button:hover {{
            background: rgba(255,255,255,0.3);
            transform: translateX(-2px);
        }}
        
        .back-button:active {{
            transform: translateX(-1px) scale(0.95);
        }}
        
        .detail-title {{
            flex: 1;
            font-size: 18px;
            font-weight: 700;
            line-height: 1.3;
        }}
        
        .detail-content {{
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            -webkit-overflow-scrolling: touch;
        }}
        
        .detail-section {{
            margin-bottom: 20px;
        }}
        
        .detail-section h3 {{
            font-size: 14px;
            font-weight: 700;
            color: #1e293b;
            margin: 0 0 12px 0;
            padding-bottom: 8px;
            border-bottom: 2px solid #e2e8f0;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .detail-badge {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 8px 14px;
            background: #f8fafc;
            border-radius: 8px;
            font-size: 13px;
            font-weight: 600;
            color: #475569;
            margin-right: 8px;
            margin-bottom: 8px;
        }}
        
        .detail-badge .badge-icon {{
            font-size: 18px;
        }}
        
        .detail-info-box {{
            background: #f8fafc;
            border-left: 3px solid #3b82f6;
            border-radius: 6px;
            padding: 12px 16px;
            margin-bottom: 12px;
        }}
        
        .detail-info-box .info-label {{
            font-size: 11px;
            color: #64748b;
            text-transform: uppercase;
            font-weight: 600;
            letter-spacing: 0.5px;
            margin-bottom: 4px;
        }}
        
        .detail-info-box .info-value {{
            font-size: 14px;
            color: #1e293b;
            font-weight: 600;
        }}
        
        .detail-button {{
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            padding: 12px 20px;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            text-decoration: none;
            transition: all 0.2s ease;
            border: none;
            cursor: pointer;
            width: 100%;
            margin-bottom: 10px;
        }}
        
        .detail-button.primary {{
            background: linear-gradient(135deg, #2563eb, #3b82f6);
            color: white;
            box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
        }}
        
        .detail-button.primary:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 16px rgba(37, 99, 235, 0.4);
        }}
        
        .detail-button.secondary {{
            background: #10b981;
            color: white;
        }}
        
        .detail-button.secondary:hover {{
            background: #059669;
        }}
        
        .detail-button.tertiary {{
            background: #8b5cf6;
            color: white;
        }}
        
        .detail-button.tertiary:hover {{
            background: #7c3aed;
        }}
        
        /* Search Box */
        .search-container {{
            position: relative;
            margin-top: 12px;
        }}
        
        .search-box {{
            width: 100%;
            padding: 12px 40px 12px 40px;
            border: 2px solid rgba(255,255,255,0.3);
            border-radius: 10px;
            font-size: 14px;
            background: rgba(255,255,255,0.95);
            color: #1e293b;
            transition: all 0.3s ease;
            font-weight: 500;
        }}
        
        .search-box:focus {{
            outline: none;
            border-color: rgba(255,255,255,0.6);
            background: white;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }}
        
        .search-box::placeholder {{
            color: #94a3b8;
        }}
        
        .search-icon {{
            position: absolute;
            left: 14px;
            top: 50%;
            transform: translateY(-50%);
            font-size: 16px;
            opacity: 0.7;
            pointer-events: none;
        }}
        
        .search-clear {{
            position: absolute;
            right: 12px;
            top: 50%;
            transform: translateY(-50%);
            background: #64748b;
            color: white;
            border: none;
            border-radius: 50%;
            width: 20px;
            height: 20px;
            font-size: 12px;
            cursor: pointer;
            display: none;
            align-items: center;
            justify-content: center;
            transition: all 0.2s;
        }}
        
        .search-clear:hover {{
            background: #475569;
            transform: translateY(-50%) scale(1.1);
        }}
        
        .search-clear.visible {{
            display: flex;
        }}
        
        .search-results {{
            position: absolute;
            top: 100%;
            left: 0;
            right: 0;
            background: white;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            margin-top: 4px;
            max-height: 300px;
            overflow-y: auto;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            z-index: 1000;
            display: none;
        }}
        
        .search-results.visible {{
            display: block;
        }}
        
        .search-result-item {{
            padding: 10px 14px;
            cursor: pointer;
            border-bottom: 1px solid #f1f5f9;
            transition: background 0.2s;
        }}
        
        .search-result-item:hover {{
            background: #f8fafc;
        }}
        
        .search-result-item:last-child {{
            border-bottom: none;
        }}
        
        .search-result-name {{
            font-weight: 600;
            color: #1e293b;
            font-size: 14px;
            margin-bottom: 3px;
        }}
        
        .search-result-meta {{
            font-size: 12px;
            color: #64748b;
        }}
        
        .search-no-results {{
            padding: 20px;
            text-align: center;
            color: #94a3b8;
            font-size: 13px;
        }}
        
        .stats-mini {{
            margin-top: 8px;
            padding: 8px 12px;
            background: rgba(255,255,255,0.15);
            border-radius: 6px;
            font-size: 12px;
            display: flex;
            justify-content: space-around;
            text-align: center;
        }}
        
        .stats-mini-item {{
            flex: 1;
        }}
        
        .stats-mini-value {{
            display: block;
            font-size: 16px;
            font-weight: 700;
            margin-bottom: 2px;
        }}
        
        .stats-mini-label {{
            font-size: 10px;
            opacity: 0.8;
            text-transform: uppercase;
            letter-spacing: 0.5px;
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
        
        /* Mobile Menu Button - Prominent and Always Visible */
        .mobile-menu-btn {{
            display: none;
            position: fixed;
            top: 16px;
            left: 16px;
            z-index: 10001;
            background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
            border: 3px solid white;
            padding: 12px 18px;
            border-radius: 14px;
            box-shadow: 0 6px 24px rgba(0,0,0,0.4);
            cursor: pointer;
            font-size: 16px;
            font-weight: 700;
            transition: all 0.3s ease;
            color: white;
            font-family: 'Segoe UI', sans-serif;
            min-width: 60px;
            min-height: 52px;
            align-items: center;
            justify-content: center;
            gap: 6px;
        }}
        
        .mobile-menu-btn:active {{
            transform: scale(0.95);
            box-shadow: 0 4px 16px rgba(0,0,0,0.3);
        }}
        
        .mobile-menu-btn .menu-icon {{
            font-size: 26px;
            line-height: 1;
        }}
        
        .mobile-menu-btn .menu-text {{
            font-size: 13px;
            font-weight: 700;
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
        
        /* Mobile Optimization - Touch-Friendly */
        @media (max-width: 768px) {{
            body {{
                flex-direction: column;
                overflow: auto;
            }}
            
            /* Show prominent menu button */
            .mobile-menu-btn {{
                display: flex;
            }}
            
            .sidebar {{
                position: fixed;
                width: 100%;
                height: auto;
                max-height: 85vh;
                bottom: 0;
                top: auto;
                left: 0;
                right: 0;
                transform: translateY(100%);
                transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1);
                box-shadow: 0 -8px 32px rgba(0,0,0,0.3);
                border-right: none;
                border-top: 4px solid #334155;
                z-index: 10000;
            }}
            
            .sidebar.open {{
                transform: translateY(0);
            }}
            
            .sidebar-header {{
                padding: 20px;
                cursor: pointer;
                position: relative;
                min-height: 56px;
                display: flex;
                align-items: center;
            }}
            
            .sidebar-header::before {{
                content: '☰';
                position: absolute;
                left: 20px;
                font-size: 28px;
                font-weight: 700;
                opacity: 0.9;
            }}
            
            .sidebar-header::after {{
                content: 'Tap to open filters';
                position: absolute;
                right: 20px;
                top: 50%;
                transform: translateY(-50%);
                font-size: 13px;
                opacity: 0.8;
                font-weight: 600;
                transition: opacity 0.3s ease;
            }}
            
            .sidebar.open .sidebar-header::after {{
                content: 'Tap to close';
            }}
            
            .sidebar-header h1 {{
                font-size: 20px;
                margin-left: 40px;
            }}
            
            .sidebar-header p {{
                display: none;
            }}
            
            .sidebar-content {{
                padding: 20px;
                max-height: calc(85vh - 100px);
                overflow-y: auto;
                -webkit-overflow-scrolling: touch;
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
            
            /* Detail sidebar on mobile - full screen */
            .detail-sidebar {{
                width: 100%;
                max-height: 100vh;
                transform: translateY(100%);
                bottom: 0;
                top: auto;
                left: 0;
                z-index: 10001;
                box-shadow: 0 -8px 32px rgba(0,0,0,0.4);
            }}
            
            .detail-sidebar.open {{
                transform: translateY(0);
            }}
            
            .detail-header {{
                padding: 18px 20px;
                min-height: 60px;
            }}
            
            .back-button {{
                width: 48px;
                height: 48px;
                font-size: 24px;
            }}
            
            .detail-title {{
                font-size: 17px;
            }}
            
            .detail-content {{
                padding: 18px;
                max-height: calc(100vh - 80px);
            }}
            
            .detail-button {{
                min-height: 48px;
                font-size: 15px;
            }}
            
            /* Touch-friendly buttons - larger targets */
            .btn {{
                min-height: 48px;
                font-size: 15px;
                padding: 14px 20px;
            }}
            
            .checkbox-list label {{
                min-height: 44px;
                padding: 10px 12px;
                font-size: 14px;
            }}
            
            input[type="checkbox"] {{
                width: 20px;
                height: 20px;
            }}
            
            /* Larger sliders for touch */
            input[type="range"]::-webkit-slider-thumb {{
                width: 28px;
                height: 28px;
            }}
            
            input[type="range"]::-moz-range-thumb {{
                width: 28px;
                height: 28px;
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
            
            /* Touch-friendly search box */
            .search-box {{
                font-size: 16px;
                padding: 14px 42px;
                min-height: 48px;
            }}
            
            .search-icon {{
                left: 16px;
                font-size: 18px;
            }}
            
            .search-clear {{
                right: 14px;
                width: 28px;
                height: 28px;
                font-size: 16px;
            }}
            
            .search-results {{
                max-height: 40vh;
                font-size: 15px;
            }}
            
            .search-result-item {{
                padding: 14px 16px;
                min-height: 56px;
            }}
            
            .search-result-name {{
                font-size: 15px;
            }}
            
            .search-result-meta {{
                font-size: 13px;
            }}
            
            /* Stats mini - more compact on mobile */
            .stats-mini {{
                padding: 10px;
                margin-top: 10px;
            }}
            
            .stats-mini-value {{
                font-size: 18px;
            }}
            
            .stats-mini-label {{
                font-size: 11px;
            }}
            
            /* Popup improvements for mobile */
            .leaflet-popup-content-wrapper {{
                max-width: calc(100vw - 40px) !important;
            }}
            
            .custom-popup {{
                font-size: 13px !important;
            }}
        }}
        
        /* Small Mobile Phones - Extra Touch Optimization */
        @media (max-width: 480px) {{
            .sidebar {{
                max-height: 90vh;
            }}
            
            .mobile-menu-btn {{
                top: 12px;
                left: 12px;
                padding: 10px 14px;
                min-width: 54px;
                min-height: 48px;
            }}
            
            .mobile-menu-btn .menu-icon {{
                font-size: 24px;
            }}
            
            .mobile-menu-btn .menu-text {{
                font-size: 12px;
            }}
            
            .sidebar-header {{
                padding: 16px 18px;
                min-height: 52px;
            }}
            
            .sidebar-header h1 {{
                font-size: 18px;
                margin-left: 36px;
            }}
            
            .sidebar-content {{
                padding: 16px;
                max-height: calc(90vh - 90px);
            }}
            
            .filter-section h3 {{
                font-size: 14px;
            }}
            
            .btn {{
                padding: 12px 16px;
                font-size: 14px;
                min-height: 48px;
            }}
            
            .search-box {{
                font-size: 16px;
            }}
            
            /* Larger cluster markers for touch */
            .marker-cluster {{
                width: 48px !important;
                height: 48px !important;
                margin-left: -24px !important;
                margin-top: -24px !important;
            }}
            
            .marker-cluster div {{
                width: 44px !important;
                height: 44px !important;
                margin-left: 2px !important;
                margin-top: 2px !important;
                font-size: 16px !important;
            }}
            
            .marker-cluster-small {{
                background-color: rgba(181, 226, 140, 0.7) !important;
            }}
            
            .marker-cluster-small div {{
                background-color: rgba(110, 204, 57, 0.7) !important;
            }}
            
            .marker-cluster-medium {{
                background-color: rgba(241, 211, 87, 0.7) !important;
            }}
            
            .marker-cluster-medium div {{
                background-color: rgba(240, 194, 12, 0.7) !important;
            }}
            
            .marker-cluster-large {{
                background-color: rgba(253, 156, 115, 0.7) !important;
            }}
            
            .marker-cluster-large div {{
                background-color: rgba(241, 128, 23, 0.7) !important;
            }}
        }}
    </style>
</head>
<body>
    <!-- Mobile Menu Button - Visible on mobile only -->
    <button class="mobile-menu-btn" id="mobile-menu-btn" aria-label="Open filters menu">
        <span class="menu-icon">☰</span>
        <span class="menu-text">Filters</span>
    </button>
    
    <div class="sidebar">
        <div class="sidebar-header">
            <h1>🏔️ Mountain Huts Explorer</h1>
            <p>Discover and explore mountain huts across the Alps and beyond. Filter by location, capacity, and more.</p>
            
            <!-- Smart Search with Autocomplete -->
            <div class="search-container">
                <span class="search-icon">🔍</span>
                <input type="text" id="search-box" class="search-box" placeholder="Search huts by name, country, region..." autocomplete="off">
                <button class="search-clear" id="search-clear" type="button">×</button>
                <div class="search-results" id="search-results"></div>
            </div>
            
            <!-- Live Stats Mini Dashboard -->
            <div class="stats-mini">
                <div class="stats-mini-item">
                    <span class="stats-mini-value" id="stats-visible">0</span>
                    <span class="stats-mini-label">Visible</span>
                </div>
                <div class="stats-mini-item">
                    <span class="stats-mini-value" id="stats-avg-alt">0m</span>
                    <span class="stats-mini-label">Avg Alt</span>
                </div>
                <div class="stats-mini-item">
                    <span class="stats-mini-value" id="stats-countries">0</span>
                    <span class="stats-mini-label">Countries</span>
                </div>
            </div>
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
            
            <!-- Detailed Stats Dashboard -->
            <div class="filter-section">
                <h3>📊 Statistics Dashboard</h3>
                <div style="background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%); padding: 16px; border-radius: 10px; border: 1px solid #93c5fd;">
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 12px;">
                        <div style="background: white; padding: 10px; border-radius: 6px; text-align: center;">
                            <div style="font-size: 24px; font-weight: 700; color: #2563eb;" id="stats-total-visible">0</div>
                            <div style="font-size: 11px; color: #64748b; font-weight: 600;">HUTS VISIBLE</div>
                        </div>
                        <div style="background: white; padding: 10px; border-radius: 6px; text-align: center;">
                            <div style="font-size: 24px; font-weight: 700; color: #16a34a;" id="stats-with-contact">0</div>
                            <div style="font-size: 11px; color: #64748b; font-weight: 600;">WITH CONTACT</div>
                        </div>
                    </div>
                    <div style="background: white; padding: 12px; border-radius: 6px; font-size: 12px; color: #475569;">
                        <div style="margin-bottom: 8px;"><strong>Altitude:</strong> <span id="stats-alt-range">N/A</span></div>
                        <div style="margin-bottom: 8px;"><strong>Average:</strong> <span id="stats-avg-altitude">N/A</span></div>
                        <div><strong>Capacity:</strong> <span id="stats-capacity-range">N/A</span></div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Detail Sidebar - Shows selected hut details -->
    <div class="detail-sidebar" id="detail-sidebar">
        <div class="detail-header">
            <button class="back-button" id="back-to-filters" aria-label="Back to filters">
                ←
            </button>
            <div class="detail-title" id="detail-hut-name">Hut Details</div>
        </div>
        <div class="detail-content" id="detail-content">
            <!-- Content will be dynamically populated -->
            <div style="text-align: center; padding: 40px 20px; color: #94a3b8;">
                <div style="font-size: 48px; margin-bottom: 16px;">🏔️</div>
                <div style="font-size: 16px; font-weight: 600;">Select a hut to view details</div>
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
        
        // Store markers and create marker cluster group with mobile-optimized settings
        var markers = [];
        var isMobileDevice = window.innerWidth <= 768;
        
        var markerCluster = L.markerClusterGroup({{
            maxClusterRadius: isMobileDevice ? 70 : 50,  // Larger clusters on mobile
            spiderfyOnMaxZoom: true,
            showCoverageOnHover: !isMobileDevice,  // Disable hover on mobile
            zoomToBoundsOnClick: true,
            disableClusteringAtZoom: isMobileDevice ? 14 : 13,  // Decluster earlier on mobile
            chunkedLoading: true,
            chunkInterval: 200,
            chunkDelay: 50,
            removeOutsideVisibleBounds: true,
            animate: !isMobileDevice,  // Disable animations on mobile for performance
            animateAddingMarkers: false,
            spiderfyDistanceMultiplier: isMobileDevice ? 2.0 : 1.5  // More spacing on mobile
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
            // Build compact, responsive popup content
            var popupParts = [];
            
            // Compact card container - responsive width with max height and scroll
            popupParts.push('<div style="font-family: -apple-system, BlinkMacSystemFont, \\'Segoe UI\\', Roboto, sans-serif; width: 260px; max-width: 90vw; max-height: 70vh; margin: -12px; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 16px rgba(0,0,0,0.1); display: flex; flex-direction: column;">');
            
            // Compact header - fixed at top
            popupParts.push('<div style="background: linear-gradient(135deg, #1e293b 0%, #334155 100%); padding: 12px 14px; color: white; flex-shrink: 0;">');
            popupParts.push('<h3 style="margin: 0 0 6px 0; font-size: 15px; font-weight: 700; line-height: 1.2;">' + escapeHtml(hut.name) + '</h3>');
            
            // Compact badges in one line
            var headerBadges = [];
            if (hut.altitude && hut.altitude !== 'N/A') {{
                headerBadges.push('<span style="font-size: 11px; font-weight: 600;">🏔️ ' + escapeHtml(String(hut.altitude)) + 'm</span>');
            }}
            if (hut.country && hut.country !== 'N/A') {{
                headerBadges.push('<span style="font-size: 11px; font-weight: 600;">🌍 ' + escapeHtml(hut.country) + '</span>');
            }}
            if (headerBadges.length > 0) {{
                popupParts.push('<div style="opacity: 0.9; display: flex; gap: 10px;">' + headerBadges.join(' • ') + '</div>');
            }}
            popupParts.push('</div>');
            
            // Scrollable body section
            popupParts.push('<div style="background: white; padding: 12px 14px; overflow-y: auto; flex: 1;">');
            
            // Compact type and capacity
            var infoItems = [];
            if (hut.type && hut.type !== 'N/A') {{
                infoItems.push('<div style="display: flex; align-items: center; padding: 6px 10px; background: #f8fafc; border-radius: 6px; margin-bottom: 6px;"><span style="font-size: 16px; margin-right: 8px;">🏠</span><div style="flex: 1;"><div style="font-size: 10px; color: #64748b; text-transform: uppercase; font-weight: 600;">Type</div><div style="font-size: 12px; color: #1e293b; font-weight: 600;">' + escapeHtml(hut.type) + '</div></div></div>');
            }}
            
            if (hut.capacity && hut.capacity !== 'N/A' && hut.capacity !== '') {{
                var capacityText = escapeHtml(String(hut.capacity));
                if (hut.capacity_max && hut.capacity_max !== 'N/A' && hut.capacity_max !== '') {{
                    capacityText += '-' + escapeHtml(String(hut.capacity_max));
                }}
                infoItems.push('<div style="display: flex; align-items: center; padding: 6px 10px; background: #f8fafc; border-radius: 6px; margin-bottom: 6px;"><span style="font-size: 16px; margin-right: 8px;">🛏️</span><div style="flex: 1;"><div style="font-size: 10px; color: #64748b; text-transform: uppercase; font-weight: 600;">Capacity</div><div style="font-size: 12px; color: #1e293b; font-weight: 600;">' + capacityText + ' beds</div></div></div>');
            }}
            
            if (infoItems.length > 0) {{
                popupParts.push(infoItems.join(''));
            }}
            
            // Compact details section
            var details = [];
            if (hut.water_source && hut.water_source !== 'N/A' && hut.water_source !== '') {{
                details.push('<div style="display: flex; padding: 4px 0; font-size: 11px;"><span style="min-width: 20px; margin-right: 6px;">💧</span><span style="color: #475569;">' + escapeHtml(hut.water_source) + '</span></div>');
            }}
            if (hut.access && hut.access !== 'N/A' && hut.access !== '') {{
                details.push('<div style="display: flex; padding: 4px 0; font-size: 11px;"><span style="min-width: 20px; margin-right: 6px;">🥾</span><span style="color: #475569;">' + escapeHtml(hut.access) + '</span></div>');
            }}
            if (hut.best_time && hut.best_time !== 'N/A' && hut.best_time !== '') {{
                details.push('<div style="display: flex; padding: 4px 0; font-size: 11px;"><span style="min-width: 20px; margin-right: 6px;">📅</span><span style="color: #475569;">' + escapeHtml(hut.best_time) + '</span></div>');
            }}
            if (details.length > 0) {{
                popupParts.push('<div style="margin: 8px 0; padding: 6px 0; border-top: 1px solid #f1f5f9;">' + details.join('') + '</div>');
            }}
            
            // Compact management info
            if ((hut.owner && hut.owner !== 'N/A' && hut.owner !== '') || (hut.manager && hut.manager !== 'N/A' && hut.manager !== '')) {{
                popupParts.push('<div style="margin: 8px 0; padding: 8px; background: #fef3c7; border-left: 2px solid #f59e0b; border-radius: 4px; font-size: 11px;">');
                if (hut.owner && hut.owner !== 'N/A' && hut.owner !== '') {{
                    popupParts.push('<div style="margin-bottom: 3px; color: #92400e;"><strong>Owner:</strong> ' + escapeHtml(hut.owner) + '</div>');
                }}
                if (hut.manager && hut.manager !== 'N/A' && hut.manager !== '') {{
                    popupParts.push('<div style="color: #92400e;"><strong>Manager:</strong> ' + escapeHtml(hut.manager) + '</div>');
                }}
                popupParts.push('</div>');
            }}
            
            // Compact opening hours
            if (hut.opening && hut.opening !== 'N/A' && hut.opening !== '') {{
                popupParts.push('<div style="margin: 8px 0; padding: 8px; background: #d1fae5; border-left: 2px solid #10b981; border-radius: 4px; font-size: 11px; color: #065f46; font-weight: 500;">🕐 ' + escapeHtml(hut.opening) + '</div>');
            }}
            
            // Compact contact buttons
            var contactButtons = [];
            if (hut.phone && hut.phone !== 'N/A' && hut.phone !== '') {{
                contactButtons.push('<a href="tel:' + escapeHtml(hut.phone) + '" style="flex: 1; display: flex; align-items: center; justify-content: center; gap: 4px; padding: 7px; background: #10b981; color: white; text-decoration: none; border-radius: 6px; font-weight: 600; font-size: 11px; transition: background 0.2s;" onmouseover="this.style.background=\\'#059669\\';" onmouseout="this.style.background=\\'#10b981\\';"><span>📞</span> Call</a>');
            }}
            if (hut.email && hut.email !== 'N/A' && hut.email !== '') {{
                contactButtons.push('<a href="mailto:' + escapeHtml(hut.email) + '" style="flex: 1; display: flex; align-items: center; justify-content: center; gap: 4px; padding: 7px; background: #3b82f6; color: white; text-decoration: none; border-radius: 6px; font-weight: 600; font-size: 11px; transition: background 0.2s;" onmouseover="this.style.background=\\'#2563eb\\';" onmouseout="this.style.background=\\'#3b82f6\\';"><span>📧</span> Email</a>');
            }}
            if (hut.website && hut.website !== 'N/A' && hut.website !== '') {{
                var websiteUrl = hut.website.startsWith('http') ? hut.website : 'http://' + hut.website;
                contactButtons.push('<a href="' + websiteUrl + '" target="_blank" rel="noopener" style="flex: 1; display: flex; align-items: center; justify-content: center; gap: 4px; padding: 7px; background: #8b5cf6; color: white; text-decoration: none; border-radius: 6px; font-weight: 600; font-size: 11px; transition: background 0.2s;" onmouseover="this.style.background=\\'#7c3aed\\';" onmouseout="this.style.background=\\'#8b5cf6\\';"><span>🌐</span> Web</a>');
            }}
            if (contactButtons.length > 0) {{
                popupParts.push('<div style="display: flex; gap: 6px; margin: 8px 0;">' + contactButtons.join('') + '</div>');
            }}
            
            // Compact description (truncate if too long)
            if (hut.description && hut.description !== 'N/A' && hut.description !== '' && hut.description.length < 150) {{
                popupParts.push('<div style="margin: 8px 0; padding: 8px; background: #f0f9ff; border-radius: 4px; font-size: 11px; color: #0c4a6e; line-height: 1.4;">' + escapeHtml(hut.description) + '</div>');
            }} else if (hut.comments && hut.comments !== 'N/A' && hut.comments !== '' && hut.comments.length < 150) {{
                popupParts.push('<div style="margin: 8px 0; padding: 8px; background: #f0f9ff; border-radius: 4px; font-size: 11px; color: #0c4a6e; line-height: 1.4;"><strong>💬</strong> ' + escapeHtml(hut.comments) + '</div>');
            }}
            
            // Compact weather widget
            popupParts.push('<div id="weather-' + hut.lat + '-' + hut.lon + '" style="margin: 8px 0;"></div>');
            
            // Compact nearby huts section
            popupParts.push('<div id="nearby-' + hut.lat + '-' + hut.lon + '" style="margin: 8px 0;"></div>');
            
            popupParts.push('</div>'); // End scrollable body
            
            // Compact footer - fixed at bottom
            popupParts.push('<div style="background: #f8fafc; padding: 10px 12px; border-top: 1px solid #e2e8f0; flex-shrink: 0;">');
            
            // Compact source indicator
            popupParts.push('<div style="text-align: center; font-size: 10px; color: #64748b; margin-bottom: 6px;">Data from <strong>' + escapeHtml(hut.source) + '</strong></div>');
            
            if (hut.url && hut.url !== 'N/A' && hut.url !== '' && hut.url !== 'http://www.mountainhuts.info/map') {{
                popupParts.push('<a href="' + escapeHtml(hut.url) + '" target="_blank" rel="noopener" style="display: flex; align-items: center; justify-content: center; gap: 6px; padding: 8px 14px; background: linear-gradient(135deg, #2563eb, #3b82f6); color: white; text-decoration: none; border-radius: 6px; font-weight: 600; font-size: 12px; box-shadow: 0 2px 8px rgba(37, 99, 235, 0.3); transition: all 0.2s ease; text-align: center;" onmouseover="this.style.transform=\\'translateY(-1px)\\'; this.style.boxShadow=\\'0 4px 12px rgba(37, 99, 235, 0.4)\\';" onmouseout="this.style.transform=\\'translateY(0)\\'; this.style.boxShadow=\\'0 2px 8px rgba(37, 99, 235, 0.3)\\';">📍 Full Details →</a>');
            }} else {{
                popupParts.push('<div style="text-align: center; font-size: 10px; color: #94a3b8;">No URL available</div>');
            }}
            
            // Compact posted by
            if (hut.posted_by && hut.posted_by !== 'N/A' && hut.posted_by !== '') {{
                popupParts.push('<div style="margin-top: 6px; text-align: center; font-size: 9px; color: #94a3b8;">by ' + escapeHtml(hut.posted_by) + '</div>');
            }}
            popupParts.push('</div>'); // End footer
            
            popupParts.push('</div>'); // End container
            
            var popup = popupParts.join('');
            
            // Responsive marker size - larger on mobile for touch
            var isMobile = window.innerWidth <= 768;
            var baseRadius = isMobile ? 8 : 4;  // Double size on mobile
            var hoverRadius = isMobile ? 12 : 6;
            
            var marker = L.circleMarker([hut.lat, hut.lon], {{
                radius: baseRadius,
                fillColor: hut.color,
                color: '#ffffff',
                weight: isMobile ? 2 : 1,
                opacity: 0.8,
                fillOpacity: 0.9
            }});
            
            // Store sizes for hover effects
            marker._baseRadius = baseRadius;
            marker._hoverRadius = hoverRadius;
            
            // Touch and hover effects
            marker.on('mouseover', function(e) {{
                this.setStyle({{
                    radius: this._hoverRadius,
                    weight: isMobile ? 3 : 2,
                    fillOpacity: 1,
                    opacity: 1
                }});
            }});
            
            marker.on('mouseout', function(e) {{
                this.setStyle({{
                    radius: this._baseRadius,
                    weight: isMobile ? 2 : 1,
                    fillOpacity: 0.9,
                    opacity: 0.8
                }});
            }});
            
            // Mobile touch feedback
            if (isMobile) {{
                marker.on('click', function(e) {{
                    // Provide visual feedback on tap
                    this.setStyle({{
                        radius: this._hoverRadius + 2,
                        weight: 3,
                        fillOpacity: 1
                    }});
                    setTimeout(() => {{
                        this.setStyle({{
                            radius: this._hoverRadius,
                            weight: 3
                        }});
                    }}, 100);
                }});
            }}
            
            // Store hut data in marker
            marker.hutData = hut;
            
            // On click, show detail sidebar instead of popup
            marker.on('click', function(e) {{
                showHutDetails(this.hutData);
                // Prevent map click from closing detail sidebar
                L.DomEvent.stopPropagation(e);
            }});
            markerCluster.addLayer(marker);
            markers.push(marker);
        }});
        
        // Calculate distance between two points using Haversine formula
        function calculateDistance(lat1, lon1, lat2, lon2) {{
            var R = 6371; // Radius of the Earth in km
            var dLat = (lat2 - lat1) * Math.PI / 180;
            var dLon = (lon2 - lon1) * Math.PI / 180;
            var a = Math.sin(dLat/2) * Math.sin(dLat/2) +
                    Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
                    Math.sin(dLon/2) * Math.sin(dLon/2);
            var c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
            var distance = R * c;
            return distance;
        }}
        
        // Show hut details in sidebar
        function showHutDetails(hut) {{
            var detailSidebar = document.getElementById('detail-sidebar');
            var detailTitle = document.getElementById('detail-hut-name');
            var detailContent = document.getElementById('detail-content');
            
            // Update title
            detailTitle.textContent = hut.name;
            
            // Build detail content
            var content = [];
            
            // Header badges
            content.push('<div style="margin-bottom: 20px;">');
            if (hut.altitude && hut.altitude !== 'N/A') {{
                content.push('<span class="detail-badge"><span class="badge-icon">🏔️</span>' + escapeHtml(String(hut.altitude)) + ' m</span>');
            }}
            if (hut.country && hut.country !== 'N/A') {{
                content.push('<span class="detail-badge"><span class="badge-icon">🌍</span>' + escapeHtml(hut.country) + '</span>');
            }}
            if (hut.type && hut.type !== 'N/A') {{
                content.push('<span class="detail-badge"><span class="badge-icon">🏠</span>' + escapeHtml(hut.type) + '</span>');
            }}
            content.push('</div>');
            
            // Main Information
            content.push('<div class="detail-section">');
            content.push('<h3>📋 Main Information</h3>');
            
            if (hut.capacity && hut.capacity !== 'N/A' && hut.capacity !== '') {{
                var capacityText = escapeHtml(String(hut.capacity));
                if (hut.capacity_max && hut.capacity_max !== 'N/A' && hut.capacity_max !== '') {{
                    capacityText += ' - ' + escapeHtml(String(hut.capacity_max));
                }}
                content.push('<div class="detail-info-box"><div class="info-label">🛏️ Capacity</div><div class="info-value">' + capacityText + ' beds</div></div>');
            }}
            
            if (hut.opening && hut.opening !== 'N/A' && hut.opening !== '') {{
                content.push('<div class="detail-info-box" style="border-left-color: #10b981;"><div class="info-label">🕐 Opening Hours</div><div class="info-value">' + escapeHtml(hut.opening) + '</div></div>');
            }}
            
            if (hut.water_source && hut.water_source !== 'N/A' && hut.water_source !== '') {{
                content.push('<div class="detail-info-box"><div class="info-label">💧 Water Source</div><div class="info-value">' + escapeHtml(hut.water_source) + '</div></div>');
            }}
            
            if (hut.access && hut.access !== 'N/A' && hut.access !== '') {{
                content.push('<div class="detail-info-box"><div class="info-label">🥾 Access</div><div class="info-value">' + escapeHtml(hut.access) + '</div></div>');
            }}
            
            if (hut.best_time && hut.best_time !== 'N/A' && hut.best_time !== '') {{
                content.push('<div class="detail-info-box"><div class="info-label">📅 Best Time to Visit</div><div class="info-value">' + escapeHtml(hut.best_time) + '</div></div>');
            }}
            content.push('</div>');
            
            // Contact Information
            if ((hut.phone && hut.phone !== 'N/A' && hut.phone !== '') || 
                (hut.email && hut.email !== 'N/A' && hut.email !== '') || 
                (hut.website && hut.website !== 'N/A' && hut.website !== '')) {{
                content.push('<div class="detail-section">');
                content.push('<h3>📞 Contact</h3>');
                
                if (hut.phone && hut.phone !== 'N/A' && hut.phone !== '') {{
                    content.push('<a href="tel:' + escapeHtml(hut.phone) + '" class="detail-button secondary">📞 Call: ' + escapeHtml(hut.phone) + '</a>');
                }}
                if (hut.email && hut.email !== 'N/A' && hut.email !== '') {{
                    content.push('<a href="mailto:' + escapeHtml(hut.email) + '" class="detail-button secondary">📧 Email: ' + escapeHtml(hut.email) + '</a>');
                }}
                if (hut.website && hut.website !== 'N/A' && hut.website !== '') {{
                    var websiteUrl = hut.website.startsWith('http') ? hut.website : 'http://' + hut.website;
                    content.push('<a href="' + websiteUrl + '" target="_blank" rel="noopener" class="detail-button tertiary">🌐 Visit Website</a>');
                }}
                content.push('</div>');
            }}
            
            // Management
            if ((hut.owner && hut.owner !== 'N/A' && hut.owner !== '') || 
                (hut.manager && hut.manager !== 'N/A' && hut.manager !== '')) {{
                content.push('<div class="detail-section">');
                content.push('<h3>👥 Management</h3>');
                if (hut.owner && hut.owner !== 'N/A' && hut.owner !== '') {{
                    content.push('<div class="detail-info-box" style="border-left-color: #f59e0b;"><div class="info-label">Owner</div><div class="info-value">' + escapeHtml(hut.owner) + '</div></div>');
                }}
                if (hut.manager && hut.manager !== 'N/A' && hut.manager !== '') {{
                    content.push('<div class="detail-info-box" style="border-left-color: #f59e0b;"><div class="info-label">Manager</div><div class="info-value">' + escapeHtml(hut.manager) + '</div></div>');
                }}
                content.push('</div>');
            }}
            
            // Description
            if (hut.description && hut.description !== 'N/A' && hut.description !== '') {{
                content.push('<div class="detail-section">');
                content.push('<h3>💬 Description</h3>');
                content.push('<div style="background: #f0f9ff; padding: 14px; border-radius: 8px; font-size: 14px; color: #0c4a6e; line-height: 1.6;">' + escapeHtml(hut.description) + '</div>');
                content.push('</div>');
            }} else if (hut.comments && hut.comments !== 'N/A' && hut.comments !== '') {{
                content.push('<div class="detail-section">');
                content.push('<h3>💬 Comments</h3>');
                content.push('<div style="background: #f0f9ff; padding: 14px; border-radius: 8px; font-size: 14px; color: #0c4a6e; line-height: 1.6;">' + escapeHtml(hut.comments) + '</div>');
                content.push('</div>');
            }}
            
            // Weather Widget
            content.push('<div class="detail-section">');
            content.push('<h3>🌤️ Weather</h3>');
            content.push('<div id="weather-detail-' + hut.lat + '-' + hut.lon + '"></div>');
            content.push('</div>');
            
            // Nearby Huts
            content.push('<div class="detail-section">');
            content.push('<h3>📍 Nearby Huts</h3>');
            content.push('<div id="nearby-detail-' + hut.lat + '-' + hut.lon + '"></div>');
            content.push('</div>');
            
            // Source & Link
            content.push('<div class="detail-section">');
            content.push('<div style="text-align: center; font-size: 12px; color: #64748b; margin-bottom: 12px;">Data from <strong>' + escapeHtml(hut.source) + '</strong></div>');
            if (hut.url && hut.url !== 'N/A' && hut.url !== '' && hut.url !== 'http://www.mountainhuts.info/map') {{
                content.push('<a href="' + escapeHtml(hut.url) + '" target="_blank" rel="noopener" class="detail-button primary">📍 View Full Details on ' + escapeHtml(hut.source) + '</a>');
            }}
            if (hut.posted_by && hut.posted_by !== 'N/A' && hut.posted_by !== '') {{
                content.push('<div style="text-align: center; font-size: 11px; color: #94a3b8; margin-top: 8px;">Posted by ' + escapeHtml(hut.posted_by) + '</div>');
            }}
            content.push('</div>');
            
            // Update content
            detailContent.innerHTML = content.join('');
            
            // Open detail sidebar
            detailSidebar.classList.add('open');
            
            // Load dynamic content
            loadWeatherToDetail(hut.lat, hut.lon);
            loadNearbyHutsToDetail(hut.lat, hut.lon, hut.name);
            
            // Center map on hut
            map.setView([hut.lat, hut.lon], Math.max(map.getZoom(), 13));
        }}
        
        // Load weather data from OpenWeatherMap (for detail sidebar)
        function loadWeatherToDetail(lat, lon) {{
            var weatherDiv = document.getElementById('weather-detail-' + lat + '-' + lon);
            if (!weatherDiv) return;
            
            var apiKey = 'YOUR_OPENWEATHERMAP_API_KEY';
            
            if (apiKey === 'YOUR_OPENWEATHERMAP_API_KEY') {{
                weatherDiv.innerHTML = '<div style="padding: 12px; background: #fef3c7; border-left: 3px solid #f59e0b; border-radius: 6px; font-size: 13px; color: #92400e;">🌤️ <a href="https://openweathermap.org/weathermap?basemap=map&cities=true&layer=temperature&lat=' + lat + '&lon=' + lon + '&zoom=10" target="_blank" style="color: #2563eb; font-weight: 600;">View Weather Forecast →</a><br><small style="opacity: 0.8;">Add OpenWeatherMap API key for live weather data</small></div>');
                return;
            }}
            
            weatherDiv.innerHTML = '<div style="padding: 10px; text-align: center; font-size: 13px; color: #94a3b8;">Loading weather...</div>';
            
            fetch('https://api.openweathermap.org/data/2.5/weather?lat=' + lat + '&lon=' + lon + '&units=metric&appid=' + apiKey)
                .then(response => response.json())
                .then(data => {{
                    var temp = Math.round(data.main.temp);
                    var description = data.weather[0].description;
                    var icon = data.weather[0].icon;
                    var iconUrl = 'https://openweathermap.org/img/wn/' + icon + '@2x.png';
                    var feelsLike = Math.round(data.main.feels_like);
                    var humidity = data.main.humidity;
                    var windSpeed = Math.round(data.wind.speed * 3.6); // m/s to km/h
                    
                    var weatherHtml = '<div style="padding: 16px; background: linear-gradient(135deg, #e0f2fe, #bae6fd); border-radius: 10px; border: 1px solid #7dd3fc;">';
                    weatherHtml += '<div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px;">';
                    weatherHtml += '<img src="' + iconUrl + '" style="width: 64px; height: 64px; margin: -8px 0;">';
                    weatherHtml += '<div style="flex: 1;">';
                    weatherHtml += '<div style="font-size: 32px; font-weight: 700; color: #0c4a6e;">' + temp + '°C</div>';
                    weatherHtml += '<div style="font-size: 14px; color: #075985; text-transform: capitalize;">' + description + '</div>';
                    weatherHtml += '</div>';
                    weatherHtml += '</div>';
                    weatherHtml += '<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; font-size: 12px; color: #0c4a6e;">';
                    weatherHtml += '<div><strong>Feels like:</strong> ' + feelsLike + '°C</div>';
                    weatherHtml += '<div><strong>Humidity:</strong> ' + humidity + '%</div>';
                    weatherHtml += '<div><strong>Wind:</strong> ' + windSpeed + ' km/h</div>';
                    weatherHtml += '<div><a href="https://openweathermap.org/city/' + data.id + '" target="_blank" style="color: #0284c7; text-decoration: none; font-weight: 600;">5-Day Forecast →</a></div>';
                    weatherHtml += '</div>';
                    weatherHtml += '</div>';
                    
                    weatherDiv.innerHTML = weatherHtml;
                }})
                .catch(error => {{
                    console.log('Weather fetch error:', error);
                    weatherDiv.innerHTML = '<div style="padding: 10px; text-align: center; font-size: 12px; color: #94a3b8;">Weather data unavailable</div>';
                }});
        }}
        
        // Load nearby huts for detail sidebar
        function loadNearbyHutsToDetail(lat, lon, currentHutName) {{
            var nearbyDiv = document.getElementById('nearby-detail-' + lat + '-' + lon);
            if (!nearbyDiv) return;
            
            // Find huts within 10km
            var nearbyHuts = [];
            huts.forEach(function(hut) {{
                if (hut.name === currentHutName) return;
                var distance = calculateDistance(lat, lon, hut.lat, hut.lon);
                if (distance <= 10) {{
                    nearbyHuts.push({{
                        name: hut.name,
                        distance: distance,
                        altitude: hut.altitude,
                        country: hut.country,
                        lat: hut.lat,
                        lon: hut.lon
                    }});
                }}
            }});
            
            nearbyHuts.sort(function(a, b) {{ return a.distance - b.distance; }});
            
            if (nearbyHuts.length === 0) {{
                nearbyDiv.innerHTML = '<div style="padding: 14px; text-align: center; font-size: 13px; color: #94a3b8;">No huts within 10km</div>';
                return;
            }}
            
            var nearbyHtml = '<div style="display: flex; flex-direction: column; gap: 10px;">';
            
            nearbyHuts.slice(0, 5).forEach(function(nearby) {{
                nearbyHtml += '<div style="padding: 12px; background: #fef3c7; border-left: 3px solid #f59e0b; border-radius: 6px; cursor: pointer; transition: all 0.2s;" onclick="showHutDetails(huts.find(h => h.lat === ' + nearby.lat + ' && h.lon === ' + nearby.lon + ')); map.setView([' + nearby.lat + ', ' + nearby.lon + '], 14);">';
                nearbyHtml += '<div style="font-weight: 700; color: #92400e; margin-bottom: 4px;">' + escapeHtml(nearby.name) + '</div>';
                nearbyHtml += '<div style="font-size: 12px; color: #78350f;"><strong>' + nearby.distance.toFixed(1) + ' km away</strong>';
                if (nearby.altitude && nearby.altitude !== 'N/A') {{
                    nearbyHtml += ' • ' + escapeHtml(String(nearby.altitude)) + 'm';
                }}
                if (nearby.country && nearby.country !== 'N/A') {{
                    nearbyHtml += ' • ' + escapeHtml(nearby.country);
                }}
                nearbyHtml += '</div>';
                nearbyHtml += '</div>';
            }});
            
            if (nearbyHuts.length > 5) {{
                nearbyHtml += '<div style="padding: 10px; text-align: center; font-size: 12px; color: #64748b;">+ ' + (nearbyHuts.length - 5) + ' more huts within 10km</div>';
            }}
            
            nearbyHtml += '</div>';
            nearbyDiv.innerHTML = nearbyHtml;
        }}
        
        // Load weather data from OpenWeatherMap
        function loadWeather(lat, lon) {{
            var weatherDiv = document.getElementById('weather-' + lat + '-' + lon);
            if (!weatherDiv) return;
            
            // Replace with your OpenWeatherMap API key: https://openweathermap.org/api
            var apiKey = 'YOUR_OPENWEATHERMAP_API_KEY';  // REPLACE THIS
            
            if (apiKey === 'YOUR_OPENWEATHERMAP_API_KEY') {{
                weatherDiv.innerHTML = '<div style="padding: 6px 8px; background: #fef3c7; border-left: 2px solid #f59e0b; border-radius: 4px; font-size: 10px; color: #92400e;">🌤️ <a href="https://openweathermap.org/weathermap?basemap=map&cities=true&layer=temperature&lat=' + lat + '&lon=' + lon + '&zoom=10" target="_blank" style="color: #2563eb; font-weight: 600;">View Forecast →</a></div>';
                return;
            }}
            
            weatherDiv.innerHTML = '<div style="padding: 6px; text-align: center; font-size: 10px; color: #94a3b8;">Loading weather...</div>';
            
            fetch('https://api.openweathermap.org/data/2.5/weather?lat=' + lat + '&lon=' + lon + '&units=metric&appid=' + apiKey)
                .then(response => response.json())
                .then(data => {{
                    var temp = Math.round(data.main.temp);
                    var description = data.weather[0].description;
                    var icon = data.weather[0].icon;
                    var iconUrl = 'https://openweathermap.org/img/wn/' + icon + '@2x.png';
                    
                    var weatherHtml = '<div style="padding: 8px; background: linear-gradient(135deg, #e0f2fe, #bae6fd); border-radius: 6px; display: flex; align-items: center; gap: 8px; border: 1px solid #7dd3fc;">';
                    weatherHtml += '<img src="' + iconUrl + '" style="width: 36px; height: 36px; margin: -4px 0;">';
                    weatherHtml += '<div style="flex: 1;">';
                    weatherHtml += '<div style="font-size: 18px; font-weight: 700; color: #0c4a6e;">' + temp + '°C</div>';
                    weatherHtml += '<div style="font-size: 10px; color: #075985; text-transform: capitalize;">' + description + '</div>';
                    weatherHtml += '</div>';
                    weatherHtml += '<a href="https://openweathermap.org/city/' + data.id + '" target="_blank" style="font-size: 10px; color: #0284c7; text-decoration: none; font-weight: 600;">More →</a>';
                    weatherHtml += '</div>';
                    
                    weatherDiv.innerHTML = weatherHtml;
                }})
                .catch(error => {{
                    console.log('Weather fetch error:', error);
                    weatherDiv.innerHTML = '';
                }});
        }}
        
        // Load nearby huts
        function loadNearbyHuts(lat, lon, currentHutName) {{
            var nearbyDiv = document.getElementById('nearby-' + lat + '-' + lon);
            if (!nearbyDiv) return;
            
            // Find huts within 10km
            var nearbyHuts = [];
            huts.forEach(function(hut) {{
                if (hut.name === currentHutName) return; // Skip current hut
                var distance = calculateDistance(lat, lon, hut.lat, hut.lon);
                if (distance <= 10) {{
                    nearbyHuts.push({{
                        name: hut.name,
                        distance: distance,
                        altitude: hut.altitude,
                        country: hut.country,
                        lat: hut.lat,
                        lon: hut.lon
                    }});
                }}
            }});
            
            // Sort by distance
            nearbyHuts.sort(function(a, b) {{ return a.distance - b.distance; }});
            
            if (nearbyHuts.length === 0) {{
                nearbyDiv.innerHTML = '';
                return;
            }}
            
            // Show top 3 nearest
            var nearbyHtml = '<div style="padding: 6px 8px; background: #fef3c7; border-left: 2px solid #f59e0b; border-radius: 4px; font-size: 10px;">';
            nearbyHtml += '<div style="font-weight: 700; margin-bottom: 4px; color: #92400e;">📍 ' + Math.min(nearbyHuts.length, 3) + ' Nearby</div>';
            
            nearbyHuts.slice(0, 3).forEach(function(nearby) {{
                nearbyHtml += '<div style="padding: 4px 0; border-top: 1px solid rgba(146, 64, 14, 0.2); color: #78350f; cursor: pointer;" onclick="map.setView([' + nearby.lat + ', ' + nearby.lon + '], 14); map.closePopup();">';
                nearbyHtml += '<div style="font-weight: 600; font-size: 11px;">' + escapeHtml(nearby.name) + '</div>';
                nearbyHtml += '<div style="font-size: 9px; opacity: 0.8;">' + nearby.distance.toFixed(1) + ' km';
                if (nearby.altitude && nearby.altitude !== 'N/A') {{
                    nearbyHtml += ' • ' + escapeHtml(String(nearby.altitude)) + 'm';
                }}
                nearbyHtml += '</div>';
                nearbyHtml += '</div>';
            }});
            
            if (nearbyHuts.length > 3) {{
                nearbyHtml += '<div style="margin-top: 4px; font-size: 9px; opacity: 0.7; color: #92400e;">+ ' + (nearbyHuts.length - 3) + ' more</div>';
            }}
            
            nearbyHtml += '</div>';
            nearbyDiv.innerHTML = nearbyHtml;
        }}
        
        // Enhanced stats update with detailed dashboard
        function updateStats() {{
            var visibleMarkers = markers.filter(function(m) {{ return markerCluster.hasLayer(m); }});
            var visible = visibleMarkers.length;
            
            // Update mini stats in header
            document.getElementById('stats-visible').textContent = visible;
            
            // Calculate stats
            var withContact = 0;
            var altitudes = [];
            var capacities = [];
            var countries = {{}};
            
            visibleMarkers.forEach(function(m) {{
                var hut = m.hutData;
                
                // Count contact info
                if ((hut.phone && hut.phone !== 'N/A' && hut.phone !== '') ||
                    (hut.email && hut.email !== 'N/A' && hut.email !== '') ||
                    (hut.website && hut.website !== 'N/A' && hut.website !== '')) {{
                    withContact++;
                }}
                
                // Collect altitudes
                if (hut.altitude && hut.altitude !== 'N/A') {{
                    var alt = parseInt(hut.altitude);
                    if (!isNaN(alt)) altitudes.push(alt);
                }}
                
                // Collect capacities
                if (hut.capacity && hut.capacity !== 'N/A' && hut.capacity !== '') {{
                    var cap = parseInt(hut.capacity);
                    if (!isNaN(cap)) capacities.push(cap);
                }}
                
                // Count countries
                if (hut.country && hut.country !== 'N/A') {{
                    countries[hut.country] = (countries[hut.country] || 0) + 1;
                }}
            }});
            
            // Update header stats
            if (altitudes.length > 0) {{
                var avgAlt = Math.round(altitudes.reduce((a,b) => a + b, 0) / altitudes.length);
                document.getElementById('stats-avg-alt').textContent = avgAlt + 'm';
            }} else {{
                document.getElementById('stats-avg-alt').textContent = 'N/A';
            }}
            
            document.getElementById('stats-countries').textContent = Object.keys(countries).length;
            
            // Update detailed dashboard
            document.getElementById('stats-total-visible').textContent = visible;
            document.getElementById('stats-with-contact').textContent = withContact;
            
            if (altitudes.length > 0) {{
                var minAlt = Math.min(...altitudes);
                var maxAlt = Math.max(...altitudes);
                var avgAlt = Math.round(altitudes.reduce((a,b) => a + b, 0) / altitudes.length);
                document.getElementById('stats-alt-range').textContent = minAlt + 'm - ' + maxAlt + 'm';
                document.getElementById('stats-avg-altitude').textContent = avgAlt + 'm';
            }} else {{
                document.getElementById('stats-alt-range').textContent = 'N/A';
                document.getElementById('stats-avg-altitude').textContent = 'N/A';
            }}
            
            if (capacities.length > 0) {{
                var minCap = Math.min(...capacities);
                var maxCap = Math.max(...capacities);
                document.getElementById('stats-capacity-range').textContent = minCap + ' - ' + maxCap + ' beds';
            }} else {{
                document.getElementById('stats-capacity-range').textContent = 'N/A';
            }}
        }}
        
        // Initialize Fuse.js for fuzzy search
        var fuse = new Fuse(huts, {{
            keys: ['name', 'country', 'type', 'description', 'owner', 'manager'],
            threshold: 0.3,
            minMatchCharLength: 2
        }});
        
        var searchResults = [];
        
        // Apply all filters
        function applyAllFilters() {{
            var searchText = document.getElementById('search-box').value.trim().toLowerCase();
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
            var searchMatches = new Set();
            if (searchText) {{
                // Use fuzzy search
                var results = fuse.search(searchText);
                results.forEach(function(result) {{
                    searchMatches.add(result.item.name);
                }});
            }}
            
            markers.forEach(function(marker) {{
                var hut = marker.hutData;
                var show = true;
                
                // Search filter with fuzzy matching
                if (searchText && searchMatches.size > 0) {{
                    if (!searchMatches.has(hut.name)) {{
                        show = false;
                    }}
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
            document.getElementById('search-box').value = '';
            document.getElementById('search-clear').classList.remove('visible');
            document.getElementById('search-results').classList.remove('visible');
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
        
        // Smart Search with Autocomplete
        var searchBox = document.getElementById('search-box');
        var searchClear = document.getElementById('search-clear');
        var searchResultsDiv = document.getElementById('search-results');
        var searchTimeout;
        
        searchBox.addEventListener('input', function() {{
            var query = this.value.trim();
            
            // Show/hide clear button
            if (query) {{
                searchClear.classList.add('visible');
            }} else {{
                searchClear.classList.remove('visible');
                searchResultsDiv.classList.remove('visible');
            }}
            
            // Debounce search
            clearTimeout(searchTimeout);
            
            if (query.length < 2) {{
                searchResultsDiv.classList.remove('visible');
                applyAllFilters();
                return;
            }}
            
            searchTimeout = setTimeout(function() {{
                // Show autocomplete results
                var results = fuse.search(query).slice(0, 8);
                
                if (results.length === 0) {{
                    searchResultsDiv.innerHTML = '<div class="search-no-results">No huts found matching "' + escapeHtml(query) + '"</div>';
                    searchResultsDiv.classList.add('visible');
                }} else {{
                    var html = '';
                    results.forEach(function(result) {{
                        var hut = result.item;
                        html += '<div class="search-result-item" data-lat="' + hut.lat + '" data-lon="' + hut.lon + '">';
                        html += '<div class="search-result-name">' + escapeHtml(hut.name) + '</div>';
                        html += '<div class="search-result-meta">';
                        if (hut.country && hut.country !== 'N/A') html += '🌍 ' + escapeHtml(hut.country) + ' • ';
                        if (hut.altitude && hut.altitude !== 'N/A') html += '🏔️ ' + escapeHtml(String(hut.altitude)) + 'm • ';
                        html += escapeHtml(hut.source);
                        html += '</div>';
                        html += '</div>';
                    }});
                    searchResultsDiv.innerHTML = html;
                    searchResultsDiv.classList.add('visible');
                    
                    // Add click handlers to results
                    document.querySelectorAll('.search-result-item').forEach(function(item) {{
                        item.addEventListener('click', function() {{
                            var lat = parseFloat(this.dataset.lat);
                            var lon = parseFloat(this.dataset.lon);
                            map.setView([lat, lon], 14);
                            searchResultsDiv.classList.remove('visible');
                            
                            // Find and show hut details in sidebar
                            markers.forEach(function(marker) {{
                                if (marker.hutData.lat === lat && marker.hutData.lon === lon) {{
                                    showHutDetails(marker.hutData);
                                }}
                            }});
                        }});
                    }});
                }}
                
                // Apply filters
                applyAllFilters();
            }}, 300);
        }});
        
        // Clear search button
        searchClear.addEventListener('click', function() {{
            searchBox.value = '';
            searchClear.classList.remove('visible');
            searchResultsDiv.classList.remove('visible');
            applyAllFilters();
            searchBox.focus();
        }});
        
        // Close autocomplete when clicking outside
        document.addEventListener('click', function(e) {{
            if (!searchBox.contains(e.target) && !searchResultsDiv.contains(e.target)) {{
                searchResultsDiv.classList.remove('visible');
            }}
        }});
        
        // Initial stats
        updateStats();
        console.log('Map ready with ' + markers.length + ' markers!');
        
        // Mobile menu handling - Touch-friendly
        var sidebar = document.querySelector('.sidebar');
        var sidebarHeader = document.querySelector('.sidebar-header');
        var mobileMenuBtn = document.getElementById('mobile-menu-btn');
        var detailSidebar = document.getElementById('detail-sidebar');
        var backButton = document.getElementById('back-to-filters');
        
        // Back button - Close detail sidebar
        if (backButton) {{
            backButton.addEventListener('click', function(e) {{
                e.stopPropagation();
                detailSidebar.classList.remove('open');
            }});
        }}
        
        // Keyboard shortcut - Escape closes detail sidebar
        document.addEventListener('keydown', function(e) {{
            if (e.key === 'Escape' && detailSidebar && detailSidebar.classList.contains('open')) {{
                detailSidebar.classList.remove('open');
            }}
        }});
        
        // Mobile menu button click
        if (mobileMenuBtn) {{
            mobileMenuBtn.addEventListener('click', function(e) {{
                e.stopPropagation();
                sidebar.classList.toggle('open');
                // Update button text
                var menuText = this.querySelector('.menu-text');
                if (sidebar.classList.contains('open')) {{
                    menuText.textContent = 'Close';
                }} else {{
                    menuText.textContent = 'Filters';
                }}
            }});
        }}
        
        // Sidebar header click (additional way to toggle)
        if (sidebarHeader) {{
            sidebarHeader.addEventListener('click', function() {{
                if (window.innerWidth <= 768) {{
                    sidebar.classList.toggle('open');
                }}
            }});
        }}
        
        // Close sidebars when clicking on map (mobile only)
        map.on('click', function() {{
            if (window.innerWidth <= 768) {{
                if (sidebar.classList.contains('open')) {{
                    sidebar.classList.remove('open');
                    if (mobileMenuBtn) {{
                        var menuText = mobileMenuBtn.querySelector('.menu-text');
                        if (menuText) menuText.textContent = 'Filters';
                    }}
                }}
                // Also close detail sidebar on map click
                if (detailSidebar.classList.contains('open')) {{
                    detailSidebar.classList.remove('open');
                }}
            }}
        }});
        
        // Handle window resize and orientation change
        var resizeTimeout;
        window.addEventListener('resize', function() {{
            clearTimeout(resizeTimeout);
            resizeTimeout = setTimeout(function() {{
                var newIsMobile = window.innerWidth <= 768;
                var oldIsMobile = isMobileDevice;
                isMobileDevice = newIsMobile;
                
                // Close sidebar on desktop
                if (window.innerWidth > 768) {{
                    sidebar.classList.remove('open');
                    if (mobileMenuBtn) {{
                        var menuText = mobileMenuBtn.querySelector('.menu-text');
                        if (menuText) menuText.textContent = 'Filters';
                    }}
                }}
                
                // Update marker sizes if mobile state changed
                if (newIsMobile !== oldIsMobile) {{
                    var newBaseRadius = newIsMobile ? 8 : 4;
                    var newHoverRadius = newIsMobile ? 12 : 6;
                    var newWeight = newIsMobile ? 2 : 1;
                    
                    markers.forEach(function(marker) {{
                        marker._baseRadius = newBaseRadius;
                        marker._hoverRadius = newHoverRadius;
                        marker.setStyle({{
                            radius: newBaseRadius,
                            weight: newWeight
                        }});
                    }});
                }}
                
                // Invalidate map size
                map.invalidateSize();
            }}, 250);
        }});
        
        // Handle orientation change
        window.addEventListener('orientationchange', function() {{
            setTimeout(function() {{
                map.invalidateSize();
                // Re-detect mobile after orientation change
                var nowMobile = window.innerWidth <= 768;
                if (nowMobile !== isMobileDevice) {{
                    location.reload();  // Reload to re-initialize markers with correct sizes
                }}
            }}, 100);
        }});
        
        }} // End of initializeMap function
    </script>
    
    <!-- Cookie Consent for GDPR Compliance -->
    <script src="js/cookie-consent.js"></script>
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

