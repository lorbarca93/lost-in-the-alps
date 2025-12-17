#!/usr/bin/env python3
"""
Test if website links are actually working by making HTTP requests
This script validates URLs are reachable and updates database to hide broken links
"""
import sys
import sqlite3
import asyncio
import aiohttp
from pathlib import Path
from urllib.parse import urlparse
import argparse
from typing import List, Tuple

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

class LinkTester:
    def __init__(self, timeout=10, max_concurrent=20):
        self.timeout = timeout
        self.max_concurrent = max_concurrent
        self.results = {
            'tested': 0,
            'working': 0,
            'broken': 0,
            'timeout': 0,
            'error': 0
        }
    
    async def test_url(self, session, url, hut_id, name):
        """Test a single URL"""
        try:
            async with session.head(url, timeout=aiohttp.ClientTimeout(total=self.timeout), allow_redirects=True) as response:
                status = response.status
                self.results['tested'] += 1
                
                if status < 400:
                    self.results['working'] += 1
                    return ('working', status, None)
                else:
                    self.results['broken'] += 1
                    return ('broken', status, f'HTTP {status}')
        
        except asyncio.TimeoutError:
            self.results['tested'] += 1
            self.results['timeout'] += 1
            return ('timeout', None, 'Timeout')
        
        except Exception as e:
            self.results['tested'] += 1
            self.results['error'] += 1
            error_msg = str(e)[:50]
            return ('error', None, error_msg)
    
    async def test_batch(self, urls_to_test: List[Tuple[int, str, str, str]]):
        """Test a batch of URLs concurrently"""
        connector = aiohttp.TCPConnector(limit=self.max_concurrent, force_close=True, enable_cleanup_closed=True)
        timeout = aiohttp.ClientTimeout(total=self.timeout)
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout, headers={
            'User-Agent': 'Mozilla/5.0 (Mountain Huts Explorer Link Validator/1.0)'
        }) as session:
            tasks = []
            for hut_id, name, website, source in urls_to_test:
                task = self.test_url(session, website, hut_id, name)
                tasks.append((hut_id, name, website, source, task))
            
            results = []
            for hut_id, name, website, source, task in tasks:
                result = await task
                results.append((hut_id, name, website, source, result))
                
                # Progress indicator
                if len(results) % 10 == 0:
                    print(f"  Progress: {len(results)}/{len(tasks)} tested...", end='\r')
            
            print(" " * 60, end='\r')  # Clear progress line
            return results

def main(dry_run=True, timeout=10, max_test=None):
    db_path = Path(__file__).parent.parent / "data" / "mountain_huts.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("=" * 80)
    print("WEBSITE LINK TESTING")
    print("=" * 80)
    print(f"Mode: {'DRY RUN (no changes)' if dry_run else 'LIVE (will update database)'}")
    print(f"Timeout: {timeout}s per URL")
    print(f"Max concurrent: 20")
    if max_test:
        print(f"Testing limit: First {max_test} URLs only")
    print("=" * 80)
    
    # Get all huts with websites
    cursor.execute("""
        SELECT id, name, website, source 
        FROM mountain_huts 
        WHERE website IS NOT NULL 
        AND website != '' 
        AND website != 'N/A'
        AND website LIKE 'http%'
        ORDER BY id
    """)
    huts = cursor.fetchall()
    
    if max_test:
        huts = huts[:max_test]
    
    print(f"\nFound {len(huts)} URLs to test")
    print(f"Starting tests...\n")
    
    # Run async tests
    tester = LinkTester(timeout=timeout, max_concurrent=20)
    results = asyncio.run(tester.test_batch(huts))
    
    # Process results
    broken_urls = []
    working_urls = []
    
    for hut_id, name, website, source, (status_type, status_code, error) in results:
        if status_type == 'working':
            working_urls.append((hut_id, name, website))
        else:
            broken_urls.append((hut_id, name, website, source, status_type, error))
            print(f"✗ BROKEN: {name[:40]:40} | {source:20}")
            print(f"  URL: {website[:70]}")
            print(f"  Error: {error}\n")
    
    # Update database
    if not dry_run and broken_urls:
        print(f"\nUpdating database to remove {len(broken_urls)} broken links...")
        for hut_id, _, _, _, _, _ in broken_urls:
            cursor.execute("UPDATE mountain_huts SET website = NULL WHERE id = ?", (hut_id,))
        conn.commit()
        print("✓ Database updated!")
    
    # Print summary
    print("\n" + "=" * 80)
    print("SUMMARY:")
    print("=" * 80)
    print(f"URLs tested: {tester.results['tested']}")
    print(f"  ✓ Working: {tester.results['working']} ({tester.results['working']/tester.results['tested']*100:.1f}%)")
    print(f"  ✗ Broken (HTTP error): {tester.results['broken']}")
    print(f"  ✗ Timeout: {tester.results['timeout']}")
    print(f"  ✗ Connection error: {tester.results['error']}")
    
    if dry_run:
        print(f"\nRun with --apply to remove broken links from database")
    else:
        print(f"\n✓ Removed {len(broken_urls)} broken links from database")
    
    conn.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Test if website links are working')
    parser.add_argument('--apply', action='store_true', help='Apply changes to database (remove broken links)')
    parser.add_argument('--timeout', type=int, default=10, help='Timeout per URL in seconds (default: 10)')
    parser.add_argument('--limit', type=int, help='Test only first N URLs (for testing)')
    
    args = parser.parse_args()
    
    main(dry_run=not args.apply, timeout=args.timeout, max_test=args.limit)

