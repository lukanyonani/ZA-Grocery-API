#!/usr/bin/env python3
"""
Quick script to inspect the HTML structure of PnP promotions page
"""

import requests
from bs4 import BeautifulSoup

url = "https://www.pnp.co.za/c/pnpbase?query=:relevance:allCategories:pnpbase:isOnPromotion:On%20Promotion"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

print(f"Fetching: {url}\n")
response = requests.get(url, headers=headers, timeout=10)
html = response.text

# Save raw HTML
with open('pnp_page_source.html', 'w', encoding='utf-8') as f:
    f.write(html)

print(f"✓ Saved raw HTML to: pnp_page_source.html ({len(html)} bytes)\n")

# Parse and analyze
soup = BeautifulSoup(html, 'html.parser')

print("=" * 80)
print("HTML STRUCTURE ANALYSIS")
print("=" * 80)

print(f"\nTitle: {soup.title.string if soup.title else 'N/A'}")
print(f"\nTotal length: {len(html)} characters")
print(f"<div> tags: {len(soup.find_all('div'))}")
print(f"<script> tags: {len(soup.find_all('script'))}")

# Look for JavaScript apps or SPAs
print("\n🔍 Checking for JavaScript frameworks:")
if 'react' in html.lower() or 'ReactDOM' in html:
    print("   ✓ React detected")
if 'vue' in html.lower():
    print("   ✓ Vue detected")
if 'angular' in html.lower():
    print("   ✓ Angular detected")
if 'ng-app' in html or 'data-ng-app' in html:
    print("   ✓ AngularJS detected")

# Check for common SPA patterns
if '__NEXT_DATA__' in html:
    print("   ✓ Next.js detected")
if 'window.__INITIAL_STATE__' in html or 'window.__PRELOADED_STATE__' in html:
    print("   ✓ Server-side rendered state detected")

# Look for data in script tags
print("\n📊 Script tag analysis:")
for i, script in enumerate(soup.find_all('script')[:10]):
    src = script.get('src', 'inline')
    script_type = script.get('type', 'text/javascript')
    content_preview = script.string[:100] if script.string else 'No content'
    print(f"   {i+1}. {script_type} - {src}")
    if script.string and len(script.string) > 50:
        print(f"      Preview: {content_preview}...")

# Check for common class patterns
print("\n🎨 Common class patterns:")
all_classes = []
for tag in soup.find_all(class_=True):
    all_classes.extend(tag.get('class', []))

class_patterns = {}
for cls in all_classes[:100]:
    if 'product' in cls.lower():
        class_patterns[cls] = class_patterns.get(cls, 0) + 1
    if 'item' in cls.lower():
        class_patterns[cls] = class_patterns.get(cls, 0) + 1
    if 'card' in cls.lower():
        class_patterns[cls] = class_patterns.get(cls, 0) + 1

if class_patterns:
    print("   Relevant classes found:")
    for cls, count in sorted(class_patterns.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"   - {cls}: {count} occurrences")
else:
    print("   No obvious product-related classes found")

print("\n" + "=" * 80)
print("First 3000 characters of HTML:")
print("=" * 80)
print(html[:3000])
print("\n...")
print("\n" + "=" * 80)
print("✓ Inspect the full HTML in: pnp_page_source.html")
print("=" * 80)

