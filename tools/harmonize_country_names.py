"""
Harmonize country names to English across the entire database
Maps various language versions to standard English names
"""
import sqlite3
from pathlib import Path


def get_country_mapping():
    """
    Map of various country name variants to standard English names
    """
    return {
        # Switzerland variants
        'Schweiz/Suisse/Svizzera/Svizra': 'Switzerland',
        'Schweiz': 'Switzerland',
        'Suisse': 'Switzerland',
        'Svizzera': 'Switzerland',
        'Svizra': 'Switzerland',
        
        # Austria variants
        'Österreich': 'Austria',
        'Oesterreich': 'Austria',
        
        # Italy variants
        'Italia': 'Italy',
        'Italie': 'Italy',
        
        # Germany variants
        'Deutschland': 'Germany',
        'Allemagne': 'Germany',
        'Germania': 'Germany',
        
        # France - already in English
        'France': 'France',
        
        # Slovenia variants
        'Slovenija': 'Slovenia',
        'Slovénie': 'Slovenia',
        
        # Czech Republic variants
        'Česko': 'Czech Republic',
        'Czechia': 'Czech Republic',
        'Tschechien': 'Czech Republic',
        'Tchéquie': 'Czech Republic',
        
        # Slovakia variants
        'Slovensko': 'Slovakia',
        'Slowakei': 'Slovakia',
        'Slovaquie': 'Slovakia',
        
        # Poland variants
        'Polska': 'Poland',
        'Polen': 'Poland',
        'Pologne': 'Poland',
        'Polonia': 'Poland',
        
        # Liechtenstein variants
        'Liechtenstein': 'Liechtenstein',
        
        # Belgium variants
        'België / Belgique / Belgien': 'Belgium',
        'België': 'Belgium',
        'Belgique': 'Belgium',
        'Belgien': 'Belgium',
        
        # Monaco variants
        'Monaco': 'Monaco',
        
        # Hungary variants
        'Magyarország': 'Hungary',
        'Ungarn': 'Hungary',
        'Hongrie': 'Hungary',
        'Ungheria': 'Hungary',
        
        # Romania variants
        'România': 'Romania',
        'Rumänien': 'Romania',
        'Roumanie': 'Romania',
        'Romania': 'Romania',
    }


def harmonize_countries():
    """
    Update all country names to English equivalents
    """
    db_path = Path(__file__).parent.parent / "data" / "mountain_huts.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all unique countries
    cursor.execute("""
        SELECT DISTINCT country, COUNT(*) as count
        FROM mountain_huts
        WHERE country IS NOT NULL AND country != '' AND country != 'N/A'
        GROUP BY country
        ORDER BY count DESC
    """)
    
    current_countries = cursor.fetchall()
    
    print("Current country names in database:")
    print("=" * 60)
    for country, count in current_countries:
        print(f"  {country:40} {count:4} huts")
    
    # Get mapping
    mapping = get_country_mapping()
    
    print("\n" + "=" * 60)
    print("Harmonizing country names to English...")
    print("=" * 60)
    
    updated_total = 0
    
    for old_name, new_name in mapping.items():
        cursor.execute("""
            SELECT COUNT(*)
            FROM mountain_huts
            WHERE country = ?
        """, (old_name,))
        
        count = cursor.fetchone()[0]
        
        if count > 0:
            cursor.execute("""
                UPDATE mountain_huts
                SET country = ?, updated_at = CURRENT_TIMESTAMP
                WHERE country = ?
            """, (new_name, old_name))
            
            updated_total += count
            print(f"  {old_name:40} -> {new_name:20} ({count} huts)")
    
    conn.commit()
    
    print(f"\n[OK] Updated {updated_total} huts with harmonized country names")
    
    # Show final distribution
    print("\n" + "=" * 60)
    print("Final country distribution (in English):")
    print("=" * 60)
    
    cursor.execute("""
        SELECT country, COUNT(*) as count
        FROM mountain_huts
        WHERE country IS NOT NULL AND country != '' AND country != 'N/A'
        GROUP BY country
        ORDER BY count DESC
    """)
    
    for country, count in cursor.fetchall():
        print(f"  {country:40} {count:4} huts")
    
    cursor.execute("""
        SELECT COUNT(*)
        FROM mountain_huts
        WHERE country IS NULL OR country = '' OR country = 'N/A'
    """)
    missing = cursor.fetchone()[0]
    if missing > 0:
        print(f"  {'(No country)':40} {missing:4} huts")
    
    conn.close()


if __name__ == "__main__":
    print("Mountain Huts Country Name Harmonization")
    print("=" * 60)
    harmonize_countries()
    print("\n[OK] Country harmonization complete!")
