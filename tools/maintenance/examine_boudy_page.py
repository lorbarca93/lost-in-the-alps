"""
Fetch and examine the actual HTML structure of a boudy.info page
"""
import requests
from bs4 import BeautifulSoup

url = "https://www.boudy.info/bouda.php?id=507"
print(f"Fetching: {url}")
print("=" * 80)

response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')

# Save the HTML to a file for examination
with open('debug/boudy_page.html', 'w', encoding='utf-8') as f:
    f.write(soup.prettify())

print("HTML saved to debug/boudy_page.html")
print("\n" + "=" * 80)
print("Page structure analysis:")
print("=" * 80)

# Look for main sections
print("\n1. Finding headers (h1, h2, h3):")
for tag in soup.find_all(['h1', 'h2', 'h3']):
    print(f"  {tag.name}: {tag.get_text(strip=True)[:80]}")

print("\n2. Finding divs with classes:")
for div in soup.find_all('div', class_=True):
    classes = ' '.join(div.get('class', []))
    content = div.get_text(strip=True)[:60]
    print(f"  div.{classes}: {content}")

print("\n3. Looking for description/info text:")
# Look for the subtitle
subtitle = soup.find('p', class_='subtitle')
if subtitle:
    print(f"\nSubtitle found: {subtitle.get_text()}")

# Look for main content area
print("\n4. Finding all text sections:")
for p in soup.find_all('p'):
    text = p.get_text(strip=True)
    if len(text) > 20:
        print(f"  {text[:100]}")

print("\n5. Looking for specific patterns:")
# GPS
if 'GPS WGS84' in response.text:
    print("  ✓ GPS WGS84 found in page")
# Posted by
if 'Posted by' in response.text or 'Vložil' in response.text:
    print("  ✓ Posted by/Vložil found in page")
# Capacity
if 'people' in response.text.lower() or 'osob' in response.text.lower():
    print("  ✓ Capacity info likely present")
