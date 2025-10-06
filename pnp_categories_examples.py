#!/usr/bin/env python3
"""
Pick n Pay Category Scraper - Usage Examples
Demonstrates how to scrape from different categories
"""

from pnp_scraper_v2 import PnPSmartScraper, list_categories, CATEGORIES


def example_1_list_categories():
    """Example 1: List all available categories"""
    print("\n" + "="*80)
    print("EXAMPLE 1: List All Categories")
    print("="*80)
    
    list_categories()


def example_2_scrape_single_category():
    """Example 2: Scrape from a specific category"""
    print("\n" + "="*80)
    print("EXAMPLE 2: Scrape Beverages (2 pages)")
    print("="*80)
    
    scraper = PnPSmartScraper(category='beverages', headless=True)
    products = scraper.scrape(max_pages=2)
    
    if products:
        scraper.save_json()  # Saves to pnp_beverages_products.json
        print(f"\n✓ Scraped {len(products)} beverage products")


def example_3_scrape_multiple_categories():
    """Example 3: Scrape multiple categories"""
    print("\n" + "="*80)
    print("EXAMPLE 3: Scrape Multiple Categories")
    print("="*80)
    
    categories_to_scrape = ['snacks', 'beverages', 'dairy']
    all_products = {}
    
    for category in categories_to_scrape:
        print(f"\n--- Scraping {category} ---")
        scraper = PnPSmartScraper(category=category, headless=True)
        products = scraper.scrape(max_pages=1)
        
        if products:
            all_products[category] = products
            scraper.save_json()  # Auto-saves with category name
            print(f"✓ {len(products)} products from {category}")
    
    total = sum(len(prods) for prods in all_products.values())
    print(f"\n✓ Total: {total} products from {len(all_products)} categories")


def example_4_food_categories():
    """Example 4: Scrape all food-related categories"""
    print("\n" + "="*80)
    print("EXAMPLE 4: Scrape Food Categories")
    print("="*80)
    
    food_categories = [
        'food-cupboard',
        'snacks',
        'beverages',
        'dairy',
        'frozen',
        'fresh-produce',
        'bakery',
        'meat',
        'ready-meals'
    ]
    
    for category in food_categories:
        scraper = PnPSmartScraper(category=category, headless=True)
        products = scraper.scrape(max_pages=1)
        
        if products:
            scraper.save_json()
            print(f"✓ {category}: {len(products)} products")


def example_5_liquor_store():
    """Example 5: Scrape liquor store"""
    print("\n" + "="*80)
    print("EXAMPLE 5: Scrape Liquor Store (3 pages)")
    print("="*80)
    
    scraper = PnPSmartScraper(category='liquor', headless=True)
    products = scraper.scrape(max_pages=3)
    
    if products:
        scraper.save_json('liquor_products.json')  # Custom filename
        scraper.save_csv('liquor_products.csv')
        
        # Analyze prices
        prices = [p['promotional_price'] for p in products if p.get('promotional_price')]
        if prices:
            print(f"\n✓ {len(products)} liquor products")
            print(f"  Average: R{sum(prices)/len(prices):.2f}")
            print(f"  Range: R{min(prices):.2f} - R{max(prices):.2f}")


def example_6_household_items():
    """Example 6: Scrape household and cleaning products"""
    print("\n" + "="*80)
    print("EXAMPLE 6: Household & Cleaning")
    print("="*80)
    
    scraper = PnPSmartScraper(category='household', headless=True)
    products = scraper.scrape(max_pages=2, max_products=50)  # Limit to 50 products
    
    if products:
        scraper.save_json()
        print(f"✓ Extracted {len(products)} household products")


def example_7_personal_care():
    """Example 7: Scrape personal care products"""
    print("\n" + "="*80)
    print("EXAMPLE 7: Personal Care & Hygiene")
    print("="*80)
    
    scraper = PnPSmartScraper(category='personal-care', headless=True)
    products = scraper.scrape(max_pages=2)
    
    if products:
        scraper.save_json()
        scraper.print_summary()


def example_8_compare_categories():
    """Example 8: Compare product counts across categories"""
    print("\n" + "="*80)
    print("EXAMPLE 8: Compare Categories (1 page each)")
    print("="*80)
    
    categories = ['snacks', 'beverages', 'dairy', 'frozen', 'pet']
    results = {}
    
    for category in categories:
        scraper = PnPSmartScraper(category=category, headless=True)
        products = scraper.scrape(max_pages=1)
        results[category] = len(products)
    
    print("\n📊 Product Count Comparison:")
    print("-" * 40)
    for category, count in sorted(results.items(), key=lambda x: x[1], reverse=True):
        print(f"  {category:20} {count:3} products")


def example_9_scrape_all_categories():
    """Example 9: Scrape from ALL categories (1 page each)"""
    print("\n" + "="*80)
    print("EXAMPLE 9: Scrape ALL Categories (1 page each)")
    print("="*80)
    print("⚠️  This will take ~15 minutes!")
    print()
    
    total_products = 0
    
    for idx, (category_key, category_info) in enumerate(CATEGORIES.items(), 1):
        print(f"\n[{idx}/{len(CATEGORIES)}] Scraping {category_info['name']}...")
        
        scraper = PnPSmartScraper(category=category_key, headless=True)
        products = scraper.scrape(max_pages=1)
        
        if products:
            scraper.save_json()
            total_products += len(products)
            print(f"  ✓ {len(products)} products")
    
    print("\n" + "="*80)
    print(f"✓ COMPLETE: {total_products} total products from {len(CATEGORIES)} categories")
    print("="*80)


def main():
    """Run examples"""
    print("\n" + "="*80)
    print("PICK N PAY CATEGORY SCRAPER - EXAMPLES")
    print("="*80)
    
    # Uncomment the example you want to run:
    
    example_1_list_categories()
    
    # example_2_scrape_single_category()
    
    # example_3_scrape_multiple_categories()
    
    # example_4_food_categories()
    
    # example_5_liquor_store()
    
    # example_6_household_items()
    
    # example_7_personal_care()
    
    # example_8_compare_categories()
    
    # example_9_scrape_all_categories()  # Takes ~15 minutes!


if __name__ == "__main__":
    main()

