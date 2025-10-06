#!/usr/bin/env python3
"""
Inspect Shoprite website structure
"""

import requests
from bs4 import BeautifulSoup

url = "https://www.shoprite.co.za/c-2413/All-Departments/Food"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

print(f"Fetching: {url}\n")
response = requests.get(url, headers=headers, timeout=10)
html = response.text

# Save raw HTML
with open('shoprite_page_source.html', 'w', encoding='utf-8') as f:
    f.write(html)

print(f"✓ Saved raw HTML to: shoprite_page_source.html ({len(html)} bytes)\n")

# Parse and analyze
soup = BeautifulSoup(html, 'html.parser')

print("=" * 80)
print("SHOPRITE HTML STRUCTURE ANALYSIS")
print("=" * 80)

print(f"\nTitle: {soup.title.string if soup.title else 'N/A'}")
print(f"\nTotal length: {len(html)} characters")
print(f"<div> tags: {len(soup.find_all('div'))}")
print(f"<script> tags: {len(soup.find_all('script'))}")

# Look for JavaScript frameworks
print("\n🔍 Checking for JavaScript frameworks:")
html_lower = html.lower()
if 'react' in html_lower or 'ReactDOM' in html:
    print("   ✓ React detected")
if 'vue' in html_lower:
    print("   ✓ Vue detected")
if 'angular' in html_lower:
    print("   ✓ Angular detected")
if '__NEXT_DATA__' in html:
    print("   ✓ Next.js detected")

# Look for product-related elements
print("\n🛒 Looking for product elements:")
product_patterns = ['product', 'item', 'card', 'tile']
for pattern in product_patterns:
    elements = soup.find_all(class_=lambda x: x and pattern in x.lower())
    if elements:
        print(f"   Found {len(elements)} elements with '{pattern}' in class")

# Check for common class patterns
print("\n🎨 Common class patterns:")
all_classes = []
for tag in soup.find_all(class_=True):
    all_classes.extend(tag.get('class', []))

class_counts = {}
for cls in all_classes:
    if any(word in cls.lower() for word in ['product', 'item', 'card', 'price']):
        class_counts[cls] = class_counts.get(cls, 0) + 1

if class_counts:
    print("   Relevant classes found:")
    for cls, count in sorted(class_counts.items(), key=lambda x: x[1], reverse=True)[:15]:
        print(f"   - {cls}: {count} occurrences")
else:
    print("   No obvious product-related classes found")

# Look for data attributes
print("\n📊 Data attributes:")
data_attrs = set()
for tag in soup.find_all(lambda t: any(attr.startswith('data-') for attr in t.attrs)):
    data_attrs.update([attr for attr in tag.attrs if attr.startswith('data-')])

if data_attrs:
    print(f"   Found {len(data_attrs)} unique data-* attributes")
    for attr in sorted(list(data_attrs)[:15]):
        print(f"   - {attr}")

print("\n" + "=" * 80)
print("First 3000 characters of HTML:")
print("=" * 80)
print(html[:3000])
print("\n...")
print("\n" + "=" * 80)
print("✓ Inspect the full HTML in: shoprite_page_source.html")
print("=" * 80)

