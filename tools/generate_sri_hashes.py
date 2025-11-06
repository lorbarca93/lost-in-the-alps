#!/usr/bin/env python3
"""
Generate SRI (Subresource Integrity) hashes for external CDN resources
Run this script to get integrity hashes for all external libraries
"""

import sys
import hashlib
import base64
import urllib.request
import ssl

# Fix Windows encoding issues
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Create unverified SSL context for older Python versions
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

def generate_sri_hash(url, algorithm='sha384'):
    """
    Generate SRI hash for a given URL
    
    Args:
        url: URL of the resource
        algorithm: Hash algorithm (sha256, sha384, or sha512)
    
    Returns:
        Integrity string in format "sha384-xxxxx"
    """
    print(f"\nFetching: {url}")
    
    try:
        # Fetch the resource
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        with urllib.request.urlopen(req, context=ssl_context, timeout=30) as response:
            content = response.read()
        
        # Generate hash
        if algorithm == 'sha256':
            hasher = hashlib.sha256()
        elif algorithm == 'sha384':
            hasher = hashlib.sha384()
        elif algorithm == 'sha512':
            hasher = hashlib.sha512()
        else:
            raise ValueError(f"Unsupported algorithm: {algorithm}")
        
        hasher.update(content)
        hash_bytes = hasher.digest()
        hash_base64 = base64.b64encode(hash_bytes).decode('ascii')
        
        sri_string = f'{algorithm}-{hash_base64}'
        
        print(f"✓ Generated: {sri_string}")
        return sri_string
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return None


def main():
    """Generate SRI hashes for all external resources used in the project"""
    
    print("=" * 80)
    print("SRI Hash Generator for Lost in the Alps")
    print("=" * 80)
    
    # List of all external resources
    resources = [
        {
            'name': 'Leaflet CSS',
            'url': 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css',
            'type': 'stylesheet'
        },
        {
            'name': 'Leaflet JS',
            'url': 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js',
            'type': 'script'
        },
        {
            'name': 'Leaflet MarkerCluster CSS',
            'url': 'https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.css',
            'type': 'stylesheet'
        },
        {
            'name': 'Leaflet MarkerCluster Default CSS',
            'url': 'https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.Default.css',
            'type': 'stylesheet'
        },
        {
            'name': 'Leaflet MarkerCluster JS',
            'url': 'https://unpkg.com/leaflet.markercluster@1.5.3/dist/leaflet.markercluster.js',
            'type': 'script'
        },
        {
            'name': 'Fuse.js',
            'url': 'https://cdn.jsdelivr.net/npm/fuse.js@6.6.2',
            'type': 'script'
        }
    ]
    
    results = []
    
    for resource in resources:
        print(f"\n{'-' * 80}")
        print(f"Processing: {resource['name']}")
        print(f"URL: {resource['url']}")
        
        sri = generate_sri_hash(resource['url'])
        
        if sri:
            results.append({
                'name': resource['name'],
                'url': resource['url'],
                'type': resource['type'],
                'integrity': sri
            })
    
    # Print summary
    print("\n" + "=" * 80)
    print("SUMMARY - Copy these into your HTML:")
    print("=" * 80)
    
    for result in results:
        if result['type'] == 'stylesheet':
            print(f"\n<!-- {result['name']} -->")
            print(f'<link rel="stylesheet" href="{result["url"]}"')
            print(f'      integrity="{result["integrity"]}" crossorigin="anonymous" />')
        else:
            print(f"\n<!-- {result['name']} -->")
            print(f'<script src="{result["url"]}"')
            print(f'        integrity="{result["integrity"]}" crossorigin="anonymous"></script>')
    
    print("\n" + "=" * 80)
    print("✓ Done! Copy the above code into tools/create_ultra_simple_map.py")
    print("=" * 80)


if __name__ == '__main__':
    main()

