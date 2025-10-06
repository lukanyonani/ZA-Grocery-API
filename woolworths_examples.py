#!/usr/bin/env python3
"""
Woolworths Scraper - Usage Examples
Demonstrates how to scrape from different Woolworths categories
"""

from woolworths_scraper import WoolworthsScraper, list_categories, WOOLWORTHS_CATEGORIES


def example_1_list_categories():
    """Example 1: List all available categories"""
    print("\n" + "="*80)
    print("EXAMPLE 1: List All Categories")
    print("="*80)
    
    list_categories()


def example_2_scrape_single_category():
    """Example 2: Scrape from a specific category"""
    print("\n" + "="*80)
    print("EXAMPLE 2: Scrape Dairy & Eggs (2 pages)")
    print("="*80)
    
    scraper = WoolworthsScraper(category='dairy-eggs')
    products = scraper.scrape_category(max_pages=2)
    
    if products:
        scraper.save_json()  # Saves to woolworths_dairy-eggs_products.json
        print(f"\n✓ Scraped {len(products)} dairy products")


def example_3_scrape_multiple_categories():
    """Example 3: Scrape multiple categories"""
    print("\n" + "="*80)
    print("EXAMPLE 3: Scrape Multiple Categories")
    print("="*80)
    
    categories_to_scrape = ['dairy-eggs', 'fruit-vegetables', 'ready-meals']
    all_products = {}
    
    for category in categories_to_scrape:
        print(f"\n--- Scraping {category} ---")
        scraper = WoolworthsScraper(category=category)
        products = scraper.scrape_category(max_pages=1)
        
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
        'fruit-vegetables',
        'dairy-eggs',
        'meat-poultry',
        'ready-meals',
        'bakery',
        'frozen-food',
        'pantry',
        'chocolates-sweets',
        'beverages'
    ]
    
    for category in food_categories:
        scraper = WoolworthsScraper(category=category)
        products = scraper.scrape_category(max_pages=1)
        
        if products:
            scraper.save_json()
            print(f"✓ {category}: {len(products)} products")


def example_5_household_categories():
    """Example 5: Scrape household categories"""
    print("\n" + "="*80)
    print("EXAMPLE 5: Household Categories")
    print("="*80")
    
    household_categories = ['household', 'cleaning', 'toiletries-health']
    
    for category in household_categories:
        scraper = WoolworthsScraper(category=category)
        products = scraper.scrape_category(max_pages=1)
        
        if products:
            scraper.save_json()
            print(f"✓ {category}: {len(products)} products")


def example_6_compare_categories():
    """Example 6: Compare product counts across categories"""
    print("\n" + "="*80)
    print("EXAMPLE 6: Compare Categories (1 page each)")
    print("="*80)
    
    categories = ['dairy-eggs', 'fruit-vegetables', 'ready-meals', 'bakery']
    results = {}
    
    for category in categories:
        scraper = WoolworthsScraper(category=category)
        products = scraper.scrape_category(max_pages=1)
        results[category] = len(products)
    
    print("\n📊 Product Count Comparison:")
    print("-" * 40)
    for category, count in sorted(results.items(), key=lambda x: x[1], reverse=True):
        print(f"  {category:20} {count:3} products")


def example_7_scrape_with_limits():
    """Example 7: Scrape with product limits"""
    print("\n" + "="*80)
    print("EXAMPLE 7: Scrape with Limits")
    print("="*80)
    
    scraper = WoolworthsScraper(category='dairy-eggs')
    products = scraper.scrape_category(max_pages=3, max_products=10)
    
    if products:
        scraper.save_json('dairy_sample.json')
        print(f"✓ Scraped {len(products)} dairy products (limited to 10)")


def example_8_analyze_prices():
    """Example 8: Analyze prices by category"""
    print("\n" + "="*80)
    print("EXAMPLE 8: Price Analysis")
    print("="*80)
    
    scraper = WoolworthsScraper(category='dairy-eggs')
    products = scraper.scrape_category(max_pages=1)
    
    if products:
        prices = [p['price'] for p in products if p.get('price')]
        
        if prices:
            print(f"\nDairy & Eggs Price Analysis ({len(prices)} products):")
            print(f"  Average: R{sum(prices)/len(prices):.2f}")
            print(f"  Range: R{min(prices):.2f} - R{max(prices):.2f}")
            
            # Show price distribution
            price_ranges = {
                'Under R20': len([p for p in prices if p < 20]),
                'R20-R50': len([p for p in prices if 20 <= p < 50]),
                'R50-R100': len([p for p in prices if 50 <= p < 100]),
                'Over R100': len([p for p in prices if p >= 100])
            }
            
            print(f"\nPrice Distribution:")
            for range_name, count in price_ranges.items():
                print(f"  {range_name}: {count} products")


def example_9_scrape_all_categories():
    """Example 9: Scrape from ALL categories (1 page each)"""
    print("\n" + "="*80)
    print("EXAMPLE 9: Scrape ALL Categories (1 page each)")
    print("="*80)
    print("⚠️  This will take ~10 minutes!")
    print()
    
    total_products = 0
    
    for idx, (category_key, category_info) in enumerate(WOOLWORTHS_CATEGORIES.items(), 1):
        print(f"\n[{idx}/{len(WOOLWORTHS_CATEGORIES)}] Scraping {category_info['name']}...")
        
        scraper = WoolworthsScraper(category=category_key)
        products = scraper.scrape_category(max_pages=1)
        
        if products:
            scraper.save_json()
            total_products += len(products)
            print(f"  ✓ {len(products)} products")
        else:
            print(f"  ⚠️  No products found")
    
    print("\n" + "="*80)
    print(f"✓ COMPLETE: {total_products} total products from {len(WOOLWORTHS_CATEGORIES)} categories")
    print("="*80)


def main():
    """Run examples"""
    print("\n" + "="*80)
    print("WOOLWORTHS SCRAPER - EXAMPLES")
    print("="*80)
    
    # Uncomment the example you want to run:
    
    example_1_list_categories()
    
    # example_2_scrape_single_category()
    
    # example_3_scrape_multiple_categories()
    
    # example_4_food_categories()
    
    # example_5_household_categories()
    
    # example_6_compare_categories()
    
    # example_7_scrape_with_limits()
    
    # example_8_analyze_prices()
    
    # example_9_scrape_all_categories()  # Takes ~10 minutes!


if __name__ == "__main__":
    main()
