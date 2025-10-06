#!/usr/bin/env python3
"""
Shoprite Food Products Scraper
Server-side rendered React app - products in HTML!
"""

import requests
from bs4 import BeautifulSoup
import json
import csv
from datetime import datetime
from typing import List, Dict
import re
import time


class ShopriteScraper:
    """Scraper for Shoprite products"""
    
    def __init__(self):
        self.base_url = "https://www.shoprite.co.za"
        self.food_url = "https://www.shoprite.co.za/c-2413/All-Departments/Food"
        self.food_url_paginated = "https://www.shoprite.co.za/c-2413/All-Departments/Food?q=%3Arelevance%3AbrowseAllStoresFacetOff%3AbrowseAllStoresFacetOff&page={page}"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        }
        self.session = requests.Session()
        self.products = []
    
    def fetch_page(self, url: str) -> str:
        """Fetch HTML content from URL"""
        try:
            print(f"Fetching: {url}")
            response = self.session.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()
            print(f"✓ Page fetched successfully ({len(response.text)} bytes)")
            return response.text
        except requests.RequestException as e:
            print(f"❌ Error fetching page: {e}")
            return None
    
    def parse_price(self, price_text: str) -> float:
        """Parse price from text"""
        if not price_text:
            return None
        
        # Remove whitespace and common text
        price_text = price_text.replace('\n', '').replace('\r', '').strip()
        price_text = price_text.replace('R', '').replace(',', '.')
        
        # Extract numbers
        match = re.search(r'(\d+\.?\d*)', price_text)
        if match:
            try:
                return float(match.group(1))
            except:
                return None
        return None
    
    def extract_products(self, html: str) -> List[Dict]:
        """Extract product information from HTML"""
        soup = BeautifulSoup(html, 'html.parser')
        products = []
        
        # Find all product containers
        product_containers = soup.find_all('div', class_='item-product')
        print(f"\nFound {len(product_containers)} product containers")
        
        for idx, container in enumerate(product_containers):
            try:
                product = self.extract_product_data(container)
                if product and product.get('name'):
                    products.append(product)
                    if (idx + 1) % 10 == 0:
                        print(f"  Processed {idx + 1}/{len(product_containers)} products...")
            except Exception as e:
                print(f"  Error parsing product {idx}: {e}")
                continue
        
        return products
    
    def extract_product_data(self, container) -> Dict:
        """Extract product data from container element"""
        product = {
            'name': None,
            'brand': None,
            'price': None,
            'original_price': None,
            'special_price': None,
            'savings': None,
            'image_url': None,
            'product_url': None,
            'product_code': None,
            'category': None,
            'in_stock': True,
            'on_special': False,
            'scraped_at': datetime.now().isoformat()
        }
        
        # Extract product code
        product['product_code'] = container.get('data-product-code')
        
        # Extract product name (from link title attribute since the div is empty)
        link_elem = container.find('a', class_='product-listening-click')
        if link_elem:
            product['name'] = link_elem.get('title', '').strip()
        
        # Extract product URL (already have link_elem from name extraction)
        if link_elem and link_elem.get('href'):
            href = link_elem['href']
            product['product_url'] = href if href.startswith('http') else f"{self.base_url}{href}"
            
            # Extract category from URL
            # URL pattern: https://www.shoprite.co.za/All-Departments/Food/{Category}/...
            try:
                url_parts = product['product_url'].split('/')
                if 'Food' in url_parts:
                    food_index = url_parts.index('Food')
                    # Category is the next segment after 'Food'
                    if food_index + 1 < len(url_parts):
                        category = url_parts[food_index + 1]
                        # Clean up category name (replace hyphens with spaces, title case)
                        product['category'] = category.replace('-', ' ').title()
            except (ValueError, IndexError):
                # If parsing fails, leave category as None
                pass
        
        # Extract image (check multiple attributes for lazy-loaded images)
        img_elem = container.find('img')
        if img_elem:
            img_src = img_elem.get('src') or img_elem.get('data-src') or img_elem.get('data-original-src')
            if img_src:
                product['image_url'] = img_src if img_src.startswith('http') else f"{self.base_url}{img_src}"
        
        # Extract prices (look for js-item-product-price first - always present)
        price_elem = container.find('div', class_='js-item-product-price')
        if price_elem:
            price_text = price_elem.get_text()
            product['price'] = self.parse_price(price_text)
        
        # Check if it's a special (has special-price div)
        special_elem = container.find('div', class_='special-price')
        if special_elem:
            product['on_special'] = True
            
            # Special price (current price)
            special_price_elem = special_elem.find('div', class_='special-price__price')
            if special_price_elem:
                price_text = special_price_elem.get_text()
                product['special_price'] = self.parse_price(price_text)
                product['price'] = product['special_price']  # Override with special price
            
            # Original price (was price)
            was_price_elem = special_elem.find('div', class_='special-price__was')
            if was_price_elem:
                was_text = was_price_elem.get_text()
                product['original_price'] = self.parse_price(was_text)
            
            # Savings
            save_elem = special_elem.find('div', class_='special-price__save')
            if save_elem:
                product['savings'] = save_elem.get_text(strip=True)
        
        # Check stock status
        out_of_stock = container.find(class_='out-of-stock')
        if out_of_stock:
            product['in_stock'] = False
        
        return product
    
    def scrape(self, url: str = None, max_pages: int = 1, max_products: int = None) -> List[Dict]:
        """Main scraping method with pagination support
        
        Args:
            url: Custom URL (if provided, ignores max_pages)
            max_pages: Number of pages to scrape (default: 1)
            max_products: Limit total products (optional)
        """
        print("=" * 80)
        print("Shoprite Food Products Scraper")
        print("=" * 80)
        
        all_products = []
        
        if url:
            # Single custom URL
            print(f"\nTarget URL: {url}\n")
            html = self.fetch_page(url)
            if html:
                products = self.extract_products(html)
                all_products.extend(products)
        else:
            # Paginated scraping
            print(f"\nScraping {max_pages} page(s) from Food section\n")
            
            for page_num in range(max_pages):
                # Page numbering is 0-indexed (page 0, page 1, etc.)
                if page_num == 0:
                    # First page doesn't need page parameter
                    page_url = self.food_url
                else:
                    page_url = self.food_url_paginated.format(page=page_num)
                
                print(f"\n--- Page {page_num + 1} of {max_pages} ---")
                html = self.fetch_page(page_url)
                
                if not html:
                    print(f"Failed to fetch page {page_num + 1}, stopping...")
                    break
                
                products = self.extract_products(html)
                print(f"✓ Extracted {len(products)} products from page {page_num + 1}")
                all_products.extend(products)
                
                # Check if we should stop early
                if max_products and len(all_products) >= max_products:
                    all_products = all_products[:max_products]
                    print(f"\n✓ Reached max_products limit ({max_products})")
                    break
                
                # Be respectful - add delay between pages
                if page_num < max_pages - 1:
                    import time
                    time.sleep(2)
                    print("  (Waiting 2 seconds before next page...)")
        
        print(f"\n{'=' * 80}")
        print(f"✓ Total products extracted: {len(all_products)}")
        print(f"{'=' * 80}")
        
        if max_products and len(all_products) > max_products:
            all_products = all_products[:max_products]
            print(f"  Limited to {max_products} products")
        
        self.products = all_products
        return all_products
    
    def save_json(self, filename: str = 'shoprite_products.json'):
        """Save products to JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.products, f, indent=2, ensure_ascii=False)
        print(f"✓ Saved {len(self.products)} products to {filename}")
    
    def save_csv(self, filename: str = 'shoprite_products.csv'):
        """Save products to CSV file"""
        if not self.products:
            print("No products to save")
            return
        
        fieldnames = list(self.products[0].keys())
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.products)
        
        print(f"✓ Saved {len(self.products)} products to {filename}")
    
    def print_summary(self):
        """Print summary of scraped data"""
        if not self.products:
            print("\n⚠️  No products found")
            return
        
        print("\n" + "=" * 80)
        print("SCRAPING SUMMARY")
        print("=" * 80)
        print(f"Total products: {len(self.products)}")
        
        # Count specials
        on_special = sum(1 for p in self.products if p.get('on_special'))
        print(f"Products on special: {on_special} ({on_special/len(self.products)*100:.1f}%)")
        
        # Count in stock
        in_stock = sum(1 for p in self.products if p.get('in_stock'))
        print(f"Products in stock: {in_stock}")
        
        # Price stats
        prices = [p['price'] for p in self.products if p.get('price')]
        if prices:
            import statistics
            print(f"\nPrice statistics:")
            print(f"  Average: R{statistics.mean(prices):.2f}")
            print(f"  Median: R{statistics.median(prices):.2f}")
            print(f"  Min: R{min(prices):.2f}")
            print(f"  Max: R{max(prices):.2f}")
        
        # Show sample products
        print(f"\n📦 Sample Products (first 5):")
        for i, product in enumerate(self.products[:5], 1):
            print(f"\n{i}. {product.get('name', 'N/A')}")
            if product.get('price'):
                print(f"   Price: R{product['price']:.2f}")
            if product.get('on_special'):
                print(f"   🔥 ON SPECIAL!")
                if product.get('original_price'):
                    print(f"   Was: R{product['original_price']:.2f}")
                if product.get('savings'):
                    print(f"   Savings: {product['savings']}")
            if product.get('product_url'):
                print(f"   URL: {product['product_url'][:70]}...")
        
        print("\n" + "=" * 80)


def main():
    """Main function"""
    scraper = ShopriteScraper()
    
    # Scrape products from multiple pages
    # Change max_pages to scrape more pages (default: 1)
    # Each page has ~20 products
    products = scraper.scrape(max_pages=3)  # Scrape 3 pages (~60 products)
    
    if products:
        # Save to both JSON and CSV
        scraper.save_json()
        scraper.save_csv()
        
        # Print summary
        scraper.print_summary()
    else:
        print("\n⚠️  No products were extracted.")


if __name__ == "__main__":
    main()

