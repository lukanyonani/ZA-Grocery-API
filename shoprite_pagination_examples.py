#!/usr/bin/env python3
"""
Shoprite Scraper - Pagination Examples
Shows different ways to use the pagination feature
"""

from shoprite_scraper import ShopriteScraper


def example_1_single_page():
    """Example 1: Scrape just the first page (20 products)"""
    print("\n" + "=" * 80)
    print("EXAMPLE 1: Single Page (Default)")
    print("=" * 80)
    
    scraper = ShopriteScraper()
    products = scraper.scrape(max_pages=1)
    
    print(f"\nExtracted {len(products)} products")
    scraper.save_json('shoprite_page1.json')
    return products


def example_2_multiple_pages():
    """Example 2: Scrape multiple pages"""
    print("\n" + "=" * 80)
    print("EXAMPLE 2: Multiple Pages")
    print("=" * 80)
    
    scraper = ShopriteScraper()
    products = scraper.scrape(max_pages=5)  # 5 pages = ~100 products
    
    print(f"\nExtracted {len(products)} products from 5 pages")
    scraper.save_json('shoprite_5pages.json')
    return products


def example_3_with_limit():
    """Example 3: Scrape with product limit"""
    print("\n" + "=" * 80)
    print("EXAMPLE 3: With Product Limit")
    print("=" * 80)
    
    scraper = ShopriteScraper()
    # Will stop after getting 50 products (even if more pages available)
    products = scraper.scrape(max_pages=10, max_products=50)
    
    print(f"\nExtracted {len(products)} products (limited to 50)")
    scraper.save_json('shoprite_limited.json')
    return products


def example_4_specific_page():
    """Example 4: Scrape a specific page URL"""
    print("\n" + "=" * 80)
    print("EXAMPLE 4: Specific Page URL")
    print("=" * 80)
    
    scraper = ShopriteScraper()
    # Scrape page 5 specifically
    url = "https://www.shoprite.co.za/c-2413/All-Departments/Food?q=%3Arelevance%3AbrowseAllStoresFacetOff%3AbrowseAllStoresFacetOff&page=4"
    products = scraper.scrape(url=url)
    
    print(f"\nExtracted {len(products)} products from page 5")
    scraper.save_json('shoprite_page5.json')
    return products


def example_5_scrape_all():
    """Example 5: Scrape many pages (careful - 3,578 products available!)"""
    print("\n" + "=" * 80)
    print("EXAMPLE 5: Scrape Many Pages")
    print("=" * 80)
    print("\n⚠️  WARNING: This will scrape 20 pages (~400 products)")
    print("Total available: 3,578 products (179 pages)")
    
    scraper = ShopriteScraper()
    products = scraper.scrape(max_pages=20)
    
    print(f"\nExtracted {len(products)} products from 20 pages")
    scraper.save_json('shoprite_20pages.json')
    
    # Calculate stats
    if products:
        prices = [p['price'] for p in products if p.get('price')]
        print(f"\nPrice range: R{min(prices):.2f} - R{max(prices):.2f}")
        print(f"Average price: R{sum(prices)/len(prices):.2f}")
    
    return products


def example_6_programmatic():
    """Example 6: Programmatic usage with custom logic"""
    print("\n" + "=" * 80)
    print("EXAMPLE 6: Programmatic Usage")
    print("=" * 80)
    
    scraper = ShopriteScraper()
    
    # Scrape and filter for cheap products
    products = scraper.scrape(max_pages=5)
    
    # Filter products under R20
    cheap_products = [p for p in products if p.get('price') and p['price'] < 20]
    
    print(f"\nFound {len(cheap_products)} products under R20")
    
    # Show cheapest 5
    sorted_products = sorted(cheap_products, key=lambda x: x.get('price', 999))
    print("\n🏆 Top 5 Cheapest:")
    for i, p in enumerate(sorted_products[:5], 1):
        print(f"  {i}. R{p['price']:.2f} - {p['name']}")
    
    return cheap_products


def main():
    """Run all examples (comment out the ones you don't want)"""
    
    print("\n" + "=" * 80)
    print("SHOPRITE SCRAPER - PAGINATION EXAMPLES")
    print("=" * 80)
    
    # Uncomment the examples you want to run:
    
    # example_1_single_page()
    # example_2_multiple_pages()
    example_3_with_limit()
    # example_4_specific_page()
    # example_5_scrape_all()  # Careful - takes time!
    # example_6_programmatic()
    
    print("\n✅ Done!")


if __name__ == "__main__":
    main()

