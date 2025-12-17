#!/usr/bin/env python3
"""
Investigate website links in the database to understand why some don't work
"""
import sys
import sqlite3
from pathlib import Path
from urllib.parse import urlparse

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Add src directory to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / 'src'))

from database import MountainHutsDatabase

def investigate_links():
    # Connect directly to database
    db_path = Path(__file__).parent.parent / "data" / "mountain_huts.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("=" * 80)
    print("INVESTIGATING WEBSITE LINKS IN DATABASE")
    print("=" * 80)
    
    # Get all websites
    cursor.execute("""
        SELECT COUNT(*) FROM mountain_huts WHERE website IS NOT NULL AND website != '' AND website != 'N/A'
    """)
    total_with_websites = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM mountain_huts")
    total_huts = cursor.fetchone()[0]
    
    print(f"\nTotal huts: {total_huts}")
    print(f"Huts with websites: {total_with_websites} ({total_with_websites/total_huts*100:.1f}%)")
    
    # Sample websites by source
    print("\n" + "=" * 80)
    print("SAMPLE WEBSITES BY SOURCE:")
    print("=" * 80)
    
    cursor.execute("""
        SELECT DISTINCT source FROM mountain_huts
    """)
    sources = [row[0] for row in cursor.fetchall()]
    
    for source in sources:
        print(f"\n--- {source} ---")
        cursor.execute("""
            SELECT name, website 
            FROM mountain_huts 
            WHERE source = ? AND website IS NOT NULL AND website != '' AND website != 'N/A'
            LIMIT 5
        """, (source,))
        
        rows = cursor.fetchall()
        if rows:
            for i, (name, website) in enumerate(rows, 1):
                print(f"{i}. {name[:45]:45} -> {website[:70]}")
        else:
            print("   No websites for this source")
    
    # Analyze URL patterns
    print("\n" + "=" * 80)
    print("URL PATTERN ANALYSIS:")
    print("=" * 80)
    
    cursor.execute("""
        SELECT website FROM mountain_huts 
        WHERE website IS NOT NULL AND website != '' AND website != 'N/A'
    """)
    
    urls = [row[0] for row in cursor.fetchall()]
    
    # Check for common issues
    issues = {
        'no_protocol': 0,
        'http_not_https': 0,
        'invalid_format': 0,
        'valid_https': 0,
        'valid_http': 0
    }
    
    problematic_urls = []
    
    for url in urls[:100]:  # Sample first 100
        try:
            parsed = urlparse(url)
            
            if not parsed.scheme:
                issues['no_protocol'] += 1
                problematic_urls.append(('no_protocol', url))
            elif parsed.scheme == 'http':
                issues['http_not_https'] += 1
            elif parsed.scheme == 'https':
                issues['valid_https'] += 1
            else:
                issues['invalid_format'] += 1
                problematic_urls.append(('invalid_format', url))
        except Exception as e:
            issues['invalid_format'] += 1
            problematic_urls.append(('exception', url))
    
    print(f"\nSample of {min(100, len(urls))} URLs:")
    print(f"  - Valid HTTPS: {issues['valid_https']}")
    print(f"  - HTTP (not HTTPS): {issues['http_not_https']}")
    print(f"  - Missing protocol: {issues['no_protocol']}")
    print(f"  - Invalid format: {issues['invalid_format']}")
    
    if problematic_urls:
        print(f"\nProblematic URLs (first 10):")
        for issue_type, url in problematic_urls[:10]:
            print(f"  [{issue_type}] {url[:70]}")
    
    conn.close()

if __name__ == "__main__":
    investigate_links()

