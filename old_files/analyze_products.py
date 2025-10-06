#!/usr/bin/env python3
"""
Analyze scraped PnP product data
"""

import json
import csv
from collections import Counter
import statistics

def load_products(filename='pnp_products.json'):
    """Load products from JSON file"""
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

def analyze_products(products):
    """Analyze product data"""
    print("=" * 80)
    print("PICK N PAY PROMOTIONS ANALYSIS")
    print("=" * 80)
    
    # Basic stats
    print(f"\n📊 Total Products: {len(products)}")
    
    # Price statistics
    prices = [p['promotional_price'] for p in products if p.get('promotional_price')]
    if prices:
        print(f"\n💰 Price Statistics:")
        print(f"   Average: R{statistics.mean(prices):.2f}")
        print(f"   Median: R{statistics.median(prices):.2f}")
        print(f"   Min: R{min(prices):.2f}")
        print(f"   Max: R{max(prices):.2f}")
        print(f"   Std Dev: R{statistics.stdev(prices):.2f}" if len(prices) > 1 else "")
    
    # Price ranges
    print(f"\n💵 Price Ranges:")
    under_50 = len([p for p in prices if p < 50])
    range_50_100 = len([p for p in prices if 50 <= p < 100])
    range_100_200 = len([p for p in prices if 100 <= p < 200])
    over_200 = len([p for p in prices if p >= 200])
    
    print(f"   Under R50: {under_50} products ({under_50/len(prices)*100:.1f}%)")
    print(f"   R50-R100: {range_50_100} products ({range_50_100/len(prices)*100:.1f}%)")
    print(f"   R100-R200: {range_100_200} products ({range_100_200/len(prices)*100:.1f}%)")
    print(f"   Over R200: {over_200} products ({over_200/len(prices)*100:.1f}%)")
    
    # Top 10 cheapest
    print(f"\n🏆 Top 10 Cheapest Products:")
    sorted_by_price = sorted(products, key=lambda x: x.get('promotional_price', float('inf')))
    for i, p in enumerate(sorted_by_price[:10], 1):
        print(f"   {i}. R{p['promotional_price']:.2f} - {p['name'][:60]}")
    
    # Top 10 most expensive
    print(f"\n💎 Top 10 Most Expensive Products:")
    sorted_by_price_desc = sorted(products, key=lambda x: x.get('promotional_price', 0), reverse=True)
    for i, p in enumerate(sorted_by_price_desc[:10], 1):
        print(f"   {i}. R{p['promotional_price']:.2f} - {p['name'][:60]}")
    
    # Product name analysis
    print(f"\n🔤 Common Words in Product Names:")
    all_words = []
    for p in products:
        if p.get('name'):
            words = p['name'].lower().split()
            # Filter out common words and numbers
            words = [w for w in words if len(w) > 3 and not w.isdigit()]
            all_words.extend(words)
    
    word_counts = Counter(all_words)
    for word, count in word_counts.most_common(15):
        print(f"   {word}: {count}")
    
    # Data completeness
    print(f"\n✅ Data Completeness:")
    with_names = len([p for p in products if p.get('name')])
    with_prices = len([p for p in products if p.get('promotional_price')])
    with_images = len([p for p in products if p.get('image_url')])
    with_ids = len([p for p in products if p.get('product_id')])
    with_brands = len([p for p in products if p.get('brand')])
    
    print(f"   Names: {with_names}/{len(products)} ({with_names/len(products)*100:.1f}%)")
    print(f"   Prices: {with_prices}/{len(products)} ({with_prices/len(products)*100:.1f}%)")
    print(f"   Images: {with_images}/{len(products)} ({with_images/len(products)*100:.1f}%)")
    print(f"   Product IDs: {with_ids}/{len(products)} ({with_ids/len(products)*100:.1f}%)")
    print(f"   Brands: {with_brands}/{len(products)} ({with_brands/len(products)*100:.1f}%)")
    
    print("\n" + "=" * 80)

def export_bargains(products, max_price=100, output='bargains.csv'):
    """Export products under a certain price"""
    bargains = [p for p in products if p.get('promotional_price', float('inf')) <= max_price]
    
    if not bargains:
        print(f"No products found under R{max_price}")
        return
    
    fieldnames = list(bargains[0].keys())
    with open(output, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(bargains)
    
    print(f"✓ Exported {len(bargains)} bargains (under R{max_price}) to {output}")

def main():
    try:
        products = load_products()
        analyze_products(products)
        export_bargains(products, max_price=100)
    except FileNotFoundError:
        print("❌ Error: pnp_products.json not found")
        print("Run the scraper first: python3 pnp_scraper_v2.py")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()

