"""
Data Cleaning Utilities for Mountain Huts Scrapers
Ensures consistent, clean data across all sources
"""

import re
import html
from typing import Optional, Dict, Any, Tuple
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# COUNTRY STANDARDIZATION
# ============================================================================

COUNTRY_ALIASES = {
    # ISO codes
    'AUT': 'Austria', 'AT': 'Austria',
    'CHE': 'Switzerland', 'CH': 'Switzerland', 'SUI': 'Switzerland',
    'DEU': 'Germany', 'DE': 'Germany', 'GER': 'Germany',
    'FRA': 'France', 'FR': 'France',
    'ITA': 'Italy', 'IT': 'Italy',
    'SVN': 'Slovenia', 'SI': 'Slovenia', 'SLO': 'Slovenia',
    'HRV': 'Croatia', 'HR': 'Croatia', 'CRO': 'Croatia',
    'POL': 'Poland', 'PL': 'Poland',
    'CZE': 'Czech Republic', 'CZ': 'Czech Republic', 'Czechia': 'Czech Republic',
    'SVK': 'Slovakia', 'SK': 'Slovakia',
    'HUN': 'Hungary', 'HU': 'Hungary',
    'ROU': 'Romania', 'RO': 'Romania', 'ROM': 'Romania',
    'BGR': 'Bulgaria', 'BG': 'Bulgaria', 'BUL': 'Bulgaria', 'BLG': 'Bulgaria',
    'SRB': 'Serbia', 'RS': 'Serbia',
    'MNE': 'Montenegro', 'ME': 'Montenegro',
    'BIH': 'Bosnia and Herzegovina', 'BA': 'Bosnia and Herzegovina',
    'ALB': 'Albania', 'AL': 'Albania',
    'MKD': 'North Macedonia', 'MK': 'North Macedonia', 'MCD': 'North Macedonia',
    'GRC': 'Greece', 'GR': 'Greece', 'GRE': 'Greece',
    'ESP': 'Spain', 'ES': 'Spain',
    'AND': 'Andorra', 'AD': 'Andorra',
    'LIE': 'Liechtenstein', 'LI': 'Liechtenstein',
    'UKR': 'Ukraine', 'UA': 'Ukraine',
    # Common variations
    'Österreich': 'Austria',
    'Schweiz': 'Switzerland', 'Suisse': 'Switzerland', 'Svizzera': 'Switzerland',
    'Deutschland': 'Germany',
    'Italia': 'Italy',
    'Slovenija': 'Slovenia',
    'Hrvatska': 'Croatia',
    'Polska': 'Poland',
    'Česká republika': 'Czech Republic', 'Česko': 'Czech Republic',
    'Slovensko': 'Slovakia',
    'Magyarország': 'Hungary',
    'România': 'Romania',
    'България': 'Bulgaria',
    'Србија': 'Serbia',
    'Crna Gora': 'Montenegro',
    'Bosna i Hercegovina': 'Bosnia and Herzegovina',
    'Shqipëria': 'Albania',
    'Ελλάδα': 'Greece',
    'España': 'Spain',
    'France': 'France',
}


# ============================================================================
# HUT TYPE STANDARDIZATION  
# ============================================================================

# Standard hut types with descriptions:
# 
# 1. STAFFED HUT (Refuge gardé)
#    - Has warden/guardian during season
#    - Provides meals, beds, services
#    - French: "refuge gardé", German: "bewirtschaftete Hütte"
#
# 2. UNSTAFFED CABIN (Cabane non gardée)
#    - No permanent staff
#    - Basic amenities (beds, sometimes kitchen)
#    - Self-service, often donation/payment box
#    - French: "cabane non gardée"
#
# 3. BIVOUAC (Bivacco)
#    - Very basic emergency shelter
#    - Usually just floor space, no beds
#    - High altitude, remote locations
#    - German: "Biwakschachtel", Italian: "bivacco"
#
# 4. SHELTER (Zavetišče/Schutzhütte)
#    - Basic shelter for emergencies
#    - May have bunks, usually no cooking
#    - Slovenian: "zavetišče", German: "Schutzhütte"
#
# 5. GUESTHOUSE (Gîte d'étape)
#    - Valley or lower altitude
#    - More comfortable, hotel-like
#    - Restaurant/meals available
#    - French: "gîte d'étape", "auberge"

HUT_TYPE_ALIASES = {
    # ===== STAFFED MOUNTAIN HUT =====
    # Huts with wardens providing meals and services
    'staffed hut': 'Staffed hut',
    'staffed mountain hut': 'Staffed hut',
    'managed hut': 'Staffed hut',
    'manned hut': 'Staffed hut',
    'refuge gardé': 'Staffed hut',
    'cabane gardée': 'Staffed hut',
    'bewirtschaftete hütte': 'Staffed hut',
    'rifugio con gestore': 'Staffed hut',
    
    # Generic terms that usually mean staffed
    'mountain hut': 'Staffed hut',
    'alpine hut': 'Staffed hut',
    'rifugio': 'Staffed hut',
    'hütte': 'Staffed hut',
    'hutte': 'Staffed hut',
    'hut': 'Staffed hut',
    
    # ===== UNSTAFFED CABIN =====
    # Self-service huts without staff
    'unstaffed cabin': 'Unstaffed cabin',
    'unstaffed hut': 'Unstaffed cabin',
    'unmanned cabin': 'Unstaffed cabin',
    'unmanned hut': 'Unstaffed cabin',
    'self-service hut': 'Unstaffed cabin',
    'cabane non gardée': 'Unstaffed cabin',
    'refuge non gardé': 'Unstaffed cabin',
    'cabane': 'Unstaffed cabin',
    'selbstversorgerhütte': 'Unstaffed cabin',
    'chata': 'Unstaffed cabin',
    'koča': 'Unstaffed cabin',
    'dom': 'Unstaffed cabin',
    'hiža': 'Unstaffed cabin',
    
    # ===== BIVOUAC =====
    # Emergency shelters, very basic
    'bivouac': 'Bivouac',
    'bivacco': 'Bivouac',
    'bivak': 'Bivouac',
    'biwak': 'Bivouac',
    'biwakschachtel': 'Bivouac',
    'emergency shelter': 'Bivouac',
    'abri d\'urgence': 'Bivouac',
    'notbiwak': 'Bivouac',
    
    # ===== SHELTER =====
    # Basic shelters for bad weather
    'shelter': 'Shelter',
    'zavetišče': 'Shelter',
    'schutzhütte': 'Shelter',
    'notunterkunft': 'Shelter',
    'abri': 'Shelter',
    'riparo': 'Shelter',
    'basic shelter': 'Shelter',
    
    # ===== GUESTHOUSE =====
    # More comfortable valley accommodations
    'guesthouse': 'Guesthouse',
    "gîte d'étape": 'Guesthouse',
    'gîte': 'Guesthouse',
    'gite': 'Guesthouse',
    'auberge': 'Guesthouse',
    'pension': 'Guesthouse',
    'gasthaus': 'Guesthouse',
    'gasthof': 'Guesthouse',
    'albergo': 'Guesthouse',
    'hotel': 'Guesthouse',
    'berggasthaus': 'Guesthouse',
    
    # ===== UNKNOWN =====
    'unknown': 'Unknown',
    '': 'Unknown',
}


# ============================================================================
# TEXT CLEANING
# ============================================================================

def clean_text(text: Optional[str], max_length: int = None) -> str:
    """
    Clean and normalize text with security-focused sanitization
    
    - Decode HTML entities
    - Normalize whitespace
    - Remove control characters
    - Remove potentially dangerous patterns (XSS prevention)
    - Optionally truncate (DoS protection)
    """
    if not text:
        return ''
    
    # Convert to string if not already
    text = str(text)
    
    # Security: Prevent extremely long inputs (DoS protection)
    MAX_INPUT_LENGTH = 100000  # 100KB max
    if len(text) > MAX_INPUT_LENGTH:
        logger.warning(f"Input text exceeds maximum length ({len(text)} > {MAX_INPUT_LENGTH}), truncating")
        text = text[:MAX_INPUT_LENGTH]
    
    # Decode HTML entities
    text = html.unescape(text)
    
    # Remove HTML tags (XSS prevention)
    text = re.sub(r'<[^>]+>', ' ', text)
    
    # Remove JavaScript event handlers and dangerous patterns
    dangerous_patterns = [
        r'javascript:', r'on\w+\s*=', r'<script', r'</script>',
        r'<iframe', r'<object', r'<embed', r'data:text/html'
    ]
    for pattern in dangerous_patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)
    
    # Remove control characters (except newlines and tabs)
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
    
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    
    # Remove common artifacts
    text = text.replace('\\n', ' ')
    text = text.replace('\\r', '')
    text = text.replace('\\t', ' ')
    
    # Truncate if needed (additional DoS protection)
    if max_length and len(text) > max_length:
        text = text[:max_length-3] + '...'
    
    return text


def clean_name(name: Optional[str]) -> str:
    """Clean hut name"""
    if not name:
        return 'Unknown'
    
    name = clean_text(name, max_length=200)
    
    # Remove common prefixes that don't add value
    prefixes_to_remove = ['the ', 'le ', 'la ', 'il ', 'el ', 'die ', 'der ', 'das ']
    name_lower = name.lower()
    for prefix in prefixes_to_remove:
        if name_lower.startswith(prefix) and len(name) > len(prefix) + 3:
            name = name[len(prefix):]
            break
    
    # Capitalize properly
    if name.isupper() or name.islower():
        name = name.title()
    
    return name if name else 'Unknown'


# ============================================================================
# COORDINATE VALIDATION
# ============================================================================

def validate_coordinates(lat: Any, lon: Any) -> Tuple[Optional[float], Optional[float], bool]:
    """
    Validate and clean coordinates
    
    Returns:
        (latitude, longitude, is_valid)
    """
    try:
        lat = float(lat)
        lon = float(lon)
    except (TypeError, ValueError):
        return None, None, False
    
    # Check ranges
    if not (-90 <= lat <= 90):
        logger.warning(f"Invalid latitude: {lat}")
        return None, None, False
    
    if not (-180 <= lon <= 180):
        logger.warning(f"Invalid longitude: {lon}")
        return None, None, False
    
    # Check for obviously wrong coordinates (null island, etc.)
    if lat == 0 and lon == 0:
        return None, None, False
    
    # Round to reasonable precision (6 decimal places = ~10cm accuracy)
    lat = round(lat, 6)
    lon = round(lon, 6)
    
    return lat, lon, True


def validate_altitude(altitude: Any) -> Optional[int]:
    """Validate and clean altitude"""
    if altitude is None or altitude == '':
        return None
    
    try:
        # Handle string formats like "2,500m" or "2 500"
        if isinstance(altitude, str):
            altitude = altitude.replace(',', '').replace(' ', '').replace('m', '').strip()
        
        alt = int(float(altitude))
        
        # Reasonable altitude range for Earth (-500m to 9000m)
        if -500 <= alt <= 9000:
            return alt
        else:
            logger.warning(f"Altitude out of range: {alt}m")
            return None
    except (ValueError, TypeError):
        return None


# ============================================================================
# CONTACT INFO CLEANING
# ============================================================================

def clean_phone(phone: Optional[str]) -> str:
    """Clean and validate phone number"""
    if not phone:
        return ''
    
    phone = clean_text(phone)
    
    # Remove common non-phone text
    invalid_patterns = ['n/a', 'none', 'unknown', '-', 'tel:', 'phone:', 'fax:', 'fax']
    if phone.lower().strip() in invalid_patterns:
        return ''
    
    # Extract phone number pattern
    # International format: +XX XXX XXX XXXX or similar
    phone_match = re.search(r'(\+?\d[\d\s\-\(\)]{7,20})', phone)
    if phone_match:
        phone = phone_match.group(1)
        
        # Normalize: remove extra spaces, keep + at start
        phone = re.sub(r'[\s\-\(\)]', '', phone)
        
        # Must have at least 8 digits
        digits = re.sub(r'\D', '', phone)
        if len(digits) >= 8:
            # Reformat with spaces for readability
            if phone.startswith('+'):
                return f"+{digits[0:2]} {digits[2:5]} {digits[5:8]} {digits[8:]}"
            return phone
    
    return ''


def clean_email(email: Optional[str]) -> str:
    """Clean and validate email address"""
    if not email:
        return ''
    
    email = clean_text(email).lower()
    
    # Remove mailto: prefix
    email = email.replace('mailto:', '')
    
    # Basic email validation
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if re.match(email_pattern, email):
        # Filter out obviously fake/placeholder emails
        invalid_emails = ['example.com', 'test.com', 'email.com', 'mail.com', 
                          'your@email', 'info@info', 'contact@contact']
        if not any(inv in email for inv in invalid_emails):
            return email
    
    return ''


def clean_url(url: Optional[str]) -> str:
    """Clean and validate URL with security checks"""
    if not url:
        return ''
    
    url = clean_text(url, max_length=2048)  # Limit URL length (RFC 7231)
    
    # Invalid values
    invalid_values = ['n/a', 'none', '-', '#', 'javascript:', 'mailto:', 'data:', 'vbscript:']
    if url.lower() in invalid_values or any(url.lower().startswith(inv) for inv in invalid_values):
        return ''
    
    # Security: Block dangerous protocols
    dangerous_protocols = ['javascript:', 'data:', 'vbscript:', 'file:', 'about:']
    if any(url.lower().startswith(proto) for proto in dangerous_protocols):
        logger.warning(f"Blocked dangerous URL protocol: {url[:50]}")
        return ''
    
    # Add protocol if missing
    if url and not url.startswith(('http://', 'https://')):
        if '@' in url:  # Probably an email
            return ''
        url = 'https://' + url
    
    # Basic URL validation (only http/https allowed)
    url_pattern = r'^https?://[^\s<>"\']+$'
    if re.match(url_pattern, url):
        # Additional security: ensure no encoded dangerous patterns
        import urllib.parse
        try:
            parsed = urllib.parse.urlparse(url)
            # Block javascript: in any part of URL
            if 'javascript:' in parsed.geturl().lower():
                return ''
            return url
        except Exception:
            return ''
    
    return ''


# ============================================================================
# COUNTRY AND TYPE STANDARDIZATION
# ============================================================================

def standardize_country(country: Optional[str]) -> str:
    """Standardize country name"""
    if not country:
        return ''
    
    country = clean_text(country)
    
    # Check aliases
    if country in COUNTRY_ALIASES:
        return COUNTRY_ALIASES[country]
    
    # Check case-insensitive
    country_lower = country.lower()
    for alias, standard in COUNTRY_ALIASES.items():
        if alias.lower() == country_lower:
            return standard
    
    # Return original if no match (will be geocoded later)
    return country


def standardize_hut_type(hut_type: Optional[str]) -> str:
    """
    Standardize hut type to one of:
    - Staffed hut: Has warden, provides meals/services
    - Unstaffed cabin: Self-service, basic amenities
    - Bivouac: Emergency shelter, very basic
    - Shelter: Basic shelter for bad weather
    - Guesthouse: Comfortable valley accommodation
    - Unknown: Fallback
    """
    if not hut_type:
        return 'Unknown'
    
    hut_type_lower = clean_text(hut_type).lower()
    
    # Direct match in aliases
    if hut_type_lower in HUT_TYPE_ALIASES:
        return HUT_TYPE_ALIASES[hut_type_lower]
    
    # Partial match in aliases (longest match first to avoid false positives)
    for alias, standard in sorted(HUT_TYPE_ALIASES.items(), key=lambda x: -len(x[0])):
        if alias and alias in hut_type_lower:
            return standard
    
    # Keyword-based classification (order matters - most specific first)
    
    # 1. Bivouac - emergency shelters
    if any(kw in hut_type_lower for kw in ['bivouac', 'bivak', 'bivacco', 'biwak', 'biwakschachtel', 'notbiwak']):
        return 'Bivouac'
    
    # 2. Guesthouse - valley/comfortable accommodation
    if any(kw in hut_type_lower for kw in ['gîte', 'gite', 'auberge', 'pension', 'gasthaus', 'gasthof', 'albergo', 'hotel', 'berggasthaus']):
        return 'Guesthouse'
    
    # 3. Shelter - basic weather shelter
    if any(kw in hut_type_lower for kw in ['zavetišče', 'schutzhütte', 'notunterkunft', 'riparo']):
        return 'Shelter'
    if 'shelter' in hut_type_lower and 'bivouac' not in hut_type_lower:
        return 'Shelter'
    if 'abri' in hut_type_lower and 'urgence' not in hut_type_lower:
        return 'Shelter'
    
    # 4. Unstaffed cabin - self-service, no staff
    if any(kw in hut_type_lower for kw in ['unmanned', 'unstaffed', 'self-service', 'non gardé', 'non gardée', 'selbstversorger']):
        return 'Unstaffed cabin'
    if any(kw in hut_type_lower for kw in ['cabane', 'chata', 'koča', 'dom', 'hiža']) and 'gardé' not in hut_type_lower:
        return 'Unstaffed cabin'
    
    # 5. Staffed hut - managed, with services
    if any(kw in hut_type_lower for kw in ['gardé', 'gardée', 'staffed', 'managed', 'manned', 'bewirtschaftet', 'con gestore']):
        return 'Staffed hut'
    if any(kw in hut_type_lower for kw in ['refuge', 'rifugio', 'hütte', 'hutte', 'hut', 'mountain hut', 'alpine hut']):
        return 'Staffed hut'
    
    return 'Unknown'


# ============================================================================
# CAPACITY CLEANING
# ============================================================================

def clean_capacity(capacity: Any) -> Optional[int]:
    """Clean and validate capacity"""
    if capacity is None or capacity == '':
        return None
    
    try:
        if isinstance(capacity, str):
            # Extract first number from string like "24 beds" or "24-30"
            match = re.search(r'(\d+)', capacity)
            if match:
                capacity = match.group(1)
        
        cap = int(capacity)
        
        # Reasonable capacity range (1 to 500)
        if 1 <= cap <= 500:
            return cap
        else:
            logger.warning(f"Capacity out of range: {cap}")
            return None
    except (ValueError, TypeError):
        return None


# ============================================================================
# MAIN CLEANING FUNCTION
# ============================================================================

def clean_hut_data(hut: Dict[str, Any]) -> Dict[str, Any]:
    """
    Clean and validate all fields in a hut dictionary
    
    Returns cleaned hut data with standardized fields
    """
    # Validate coordinates first (required)
    lat, lon, coords_valid = validate_coordinates(
        hut.get('latitude') or hut.get('lat'),
        hut.get('longitude') or hut.get('lon')
    )
    
    if not coords_valid:
        logger.warning(f"Invalid coordinates for hut: {hut.get('name', 'Unknown')}")
    
    cleaned = {
        # Required fields
        'source_id': str(hut.get('source_id') or hut.get('id') or ''),
        'name': clean_name(hut.get('name')),
        'latitude': lat,
        'longitude': lon,
        
        # Location
        'altitude': validate_altitude(hut.get('altitude')),
        'country': standardize_country(hut.get('country')),
        'region': clean_text(hut.get('region'), max_length=100),
        
        # Classification
        'hut_type': standardize_hut_type(hut.get('hut_type') or hut.get('type')),
        'status': clean_text(hut.get('status'), max_length=50),
        'status_description': clean_text(hut.get('status_description'), max_length=200),
        
        # Contact
        'phone': clean_phone(hut.get('phone')),
        'email': clean_email(hut.get('email')),
        'website': clean_url(hut.get('website')),
        'url': clean_url(hut.get('url')),
        
        # Capacity
        'capacity': clean_capacity(hut.get('capacity')),
        'capacity_max': clean_capacity(hut.get('capacity_max')),
        
        # Details
        'description': clean_text(hut.get('description'), max_length=2000),
        'amenities': clean_text(hut.get('amenities'), max_length=500),
        'opening_hours': clean_text(hut.get('opening_hours'), max_length=500),
        'access': clean_text(hut.get('access'), max_length=1000),
        'water_source': clean_text(hut.get('water_source'), max_length=200),
        'best_time_to_visit': clean_text(hut.get('best_time_to_visit'), max_length=200),
        
        # Management
        'owner': clean_text(hut.get('owner'), max_length=200),
        'manager': clean_text(hut.get('manager'), max_length=200),
        
        # Metadata
        'comments': clean_text(hut.get('comments'), max_length=2000),
        'posted_by': clean_text(hut.get('posted_by'), max_length=100),
        'posted_date': clean_text(hut.get('posted_date'), max_length=50),
        'image_url': clean_url(hut.get('image_url')),
    }
    
    return cleaned


def validate_hut_data(hut: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    Validate that hut data meets minimum requirements
    
    Returns:
        (is_valid, error_message)
    """
    # Must have source_id
    if not hut.get('source_id'):
        return False, "Missing source_id"
    
    # Must have name
    if not hut.get('name') or hut['name'] == 'Unknown':
        return False, "Missing or invalid name"
    
    # Must have valid coordinates
    if hut.get('latitude') is None or hut.get('longitude') is None:
        return False, "Missing or invalid coordinates"
    
    return True, None

