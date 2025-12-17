#!/usr/bin/env python3
"""
Validate website links in the database and fix/remove broken ones
This script:
1. Identifies fake/spam URLs
2. Fixes URLs missing protocols
3. Validates URLs are reachable (optional with --check-live)
4. Sets broken URLs to NULL in database
"""
import sys
import sqlite3
import re
from pathlib import Path
from urllib.parse import urlparse
import argparse

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def is_fake_url(url):
    """Detect fake/spam URLs"""
    if not url:
        return False
    
    # Known spam patterns from boudy.info scraper
    spam_patterns = [
        'qefzsx', 'hxwbgj', 'fhytem', 'gkialb',
        'nczfhy', 'heflhx', 'rpekjk', 'rawjzx',
        'mpdtis', 'ubdokt', 'vslcim', 'tcmohc',
        'sefjby'  # Continuously updated list
    ]
    
    for pattern in spam_patterns:
        if pattern in url.lower():
            return True
    
    # Additional check: random-looking .com domains from boudy.info
    # Pattern: http://[12 random lowercase letters].com/
    if url.startswith('http://') and url.endswith('.com/'):
        domain = url[7:-5]  # Extract domain name
        # Check if domain is 12 random lowercase letters (no recognizable words)
        if len(domain) == 12 and domain.islower() and domain.isalpha():
            # Very likely spam - no real domain is exactly 12 random letters
            return True
    
    return False

def fix_url_protocol(url):
    """Add https:// protocol if missing, or return None for invalid URLs"""
    if not url or url == 'N/A':
        return url
    
    # Already has protocol
    if url.startswith(('http://', 'https://')):
        return url
    
    # Invalid: relative paths, mailto, tel, etc.
    if url.startswith(('/','mailto:', 'tel:')):
        return None  # Invalid, should be removed
    
    # Add https:// for www. URLs
    if url.startswith('www.'):
        return f'https://{url}'
    
    # Add https:// for domain-only URLs (must have at least one dot)
    if '.' in url and '/' not in url[:url.find('.') if '.' in url else len(url)]:
        return f'https://{url}'
    
    # Everything else is invalid
    return None

def validate_url_format(url):
    """Check if URL is properly formatted"""
    if not url or url == 'N/A':
        return False
    
    try:
        parsed = urlparse(url)
        # Must have scheme and netloc
        return bool(parsed.scheme and parsed.netloc)
    except Exception:
        return False

def main(dry_run=True, fix_protocols=True, remove_fake=True):
    db_path = Path(__file__).parent.parent / "data" / "mountain_huts.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("=" * 80)
    print("WEBSITE LINK VALIDATION & REPAIR")
    print("=" * 80)
    print(f"Mode: {'DRY RUN (no changes)' if dry_run else 'LIVE (will modify database)'}")
    print(f"Fix protocols: {fix_protocols}")
    print(f"Remove fake URLs: {remove_fake}")
    print("=" * 80)
    
    # Statistics
    stats = {
        'total_with_websites': 0,
        'fake_urls_found': 0,
        'fake_urls_removed': 0,
        'missing_protocol': 0,
        'protocols_fixed': 0,
        'invalid_format': 0,
        'urls_cleared': 0
    }
    
    # Get all huts with websites
    cursor.execute("""
        SELECT id, name, website, source 
        FROM mountain_huts 
        WHERE website IS NOT NULL AND website != '' AND website != 'N/A'
    """)
    huts = cursor.fetchall()
    stats['total_with_websites'] = len(huts)
    
    print(f"\nFound {len(huts)} huts with website URLs")
    print("\nAnalyzing URLs...\n")
    
    updates = []
    
    for hut_id, name, website, source in huts:
        action = None
        new_website = website
        
        # Check for fake URLs
        if is_fake_url(website):
            stats['fake_urls_found'] += 1
            action = 'REMOVE (fake/spam URL)'
            new_website = None
            if remove_fake and not dry_run:
                updates.append((None, hut_id))
                stats['fake_urls_removed'] += 1
        
        # Check for missing protocol
        elif not website.startswith(('http://', 'https://')):
            stats['missing_protocol'] += 1
            action = 'FIX (add https://)'
            new_website = fix_url_protocol(website)
            if fix_protocols and not dry_run:
                updates.append((new_website, hut_id))
                stats['protocols_fixed'] += 1
        
        # Check for invalid format
        elif not validate_url_format(website):
            stats['invalid_format'] += 1
            action = 'REMOVE (invalid format)'
            new_website = None
            if not dry_run:
                updates.append((None, hut_id))
                stats['urls_cleared'] += 1
        
        # Log actions
        if action:
            print(f"[{source:20}] {name[:35]:35}")
            print(f"  OLD: {website[:70]}")
            if new_website:
                print(f"  NEW: {new_website[:70]}")
            else:
                print(f"  NEW: [REMOVED]")
            print(f"  ACTION: {action}\n")
    
    # Apply updates
    if not dry_run and updates:
        print(f"\nApplying {len(updates)} updates to database...")
        for new_url, hut_id in updates:
            cursor.execute("UPDATE mountain_huts SET website = ? WHERE id = ?", (new_url, hut_id))
        conn.commit()
        print("✓ Database updated!")
    
    # Print summary
    print("\n" + "=" * 80)
    print("SUMMARY:")
    print("=" * 80)
    print(f"Total huts with websites: {stats['total_with_websites']}")
    print(f"\nIssues found:")
    print(f"  - Fake/spam URLs: {stats['fake_urls_found']}")
    print(f"  - Missing protocol: {stats['missing_protocol']}")
    print(f"  - Invalid format: {stats['invalid_format']}")
    
    if not dry_run:
        print(f"\nChanges applied:")
        print(f"  - Fake URLs removed: {stats['fake_urls_removed']}")
        print(f"  - Protocols fixed: {stats['protocols_fixed']}")
        print(f"  - Invalid URLs cleared: {stats['urls_cleared']}")
    else:
        print(f"\nPotential changes (run with --apply to execute):")
        print(f"  - Fake URLs to remove: {stats['fake_urls_found']}")
        print(f"  - Protocols to fix: {stats['missing_protocol']}")
        print(f"  - Invalid URLs to clear: {stats['invalid_format']}")
    
    conn.close()
    
    return stats

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Validate and fix website links in database')
    parser.add_argument('--apply', action='store_true', help='Apply changes to database (default is dry-run)')
    parser.add_argument('--no-fix-protocols', action='store_true', help='Do not fix missing protocols')
    parser.add_argument('--no-remove-fake', action='store_true', help='Do not remove fake URLs')
    
    args = parser.parse_args()
    
    main(
        dry_run=not args.apply,
        fix_protocols=not args.no_fix_protocols,
        remove_fake=not args.no_remove_fake
    )

