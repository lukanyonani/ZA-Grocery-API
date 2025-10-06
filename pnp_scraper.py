#!/usr/bin/env python3
"""
Pick n Pay Promotions Scraper
Scrapes promotional products from PnP website
"""

import requests
from bs4 import BeautifulSoup
import json
import csv
from datetime import datetime
from typing import List, Dict
import time
import re


class PnPScraper:
    """Scraper for Pick n Pay promotional products"""
    
    def __init__(self):
        self.base_url = "https://www.pnp.co.za"
        self.promotions_url = "https://www.pnp.co.za/c/pnpbase?query=:relevance:allCategories:pnpbase:isOnPromotion:On%20Promotion"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        self.session = requests.Session()
        self.products = []
    
    def fetch_page(self, url: str, page: int = 1) -> str:
        """Fetch HTML content from URL"""
        try:
            # Add pagination if needed
            if page > 1:
                url = f"{url}&page={page}"
            
            print(f"Fetching page {page}...")
            response = self.session.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()
            print(f"✓ Page {page} fetched successfully ({len(response.text)} bytes)")
            return response.text
        except requests.RequestException as e:
            print(f"❌ Error fetching page: {e}")
            return None
    
    def parse_price(self, price_text: str) -> Dict:
        """Parse price from text"""
        if not price_text:
            return {'original': None, 'promotional': None, 'currency': 'R'}
        
        # Remove whitespace and newlines
        price_text = ' '.join(price_text.split())
        
        # Try to find prices with R prefix
        prices = re.findall(r'R?\s*(\d+[.,]?\d*)', price_text)
        
        if len(prices) >= 2:
            # Likely has both original and promotional price
            return {
                'original': float(prices[0].replace(',', '.')),
                'promotional': float(prices[1].replace(',', '.')),
                'currency': 'R'
            }
        elif len(prices) == 1:
            return {
                'original': None,
                'promotional': float(prices[0].replace(',', '.')),
                'currency': 'R'
            }
        
        return {'original': None, 'promotional': None, 'currency': 'R'}
    
    def parse_products(self, html: str) -> List[Dict]:
        """Parse product information from HTML"""
        soup = BeautifulSoup(html, 'html.parser')
        products = []
        
        # Try multiple selector strategies
        # Strategy 1: Look for product cards/tiles
        product_containers = soup.find_all(['div', 'article'], class_=re.compile(r'product|item|card|tile', re.I))
        
        if not product_containers:
            # Strategy 2: Look for common e-commerce patterns
            product_containers = soup.find_all('div', {'data-product-id': True})
        
        if not product_containers:
            # Strategy 3: Look for links containing product info
            product_containers = soup.find_all('a', href=re.compile(r'/p/'))
        
        print(f"Found {len(product_containers)} potential product containers")
        
        for idx, container in enumerate(product_containers):
            try:
                product = self.extract_product_data(container)
                if product and product.get('name'):
                    products.append(product)
            except Exception as e:
                print(f"Error parsing product {idx}: {e}")
                continue
        
        return products
    
    def extract_product_data(self, container) -> Dict:
        """Extract product data from container element"""
        product = {
            'name': None,
            'brand': None,
            'price': None,
            'original_price': None,
            'promotional_price': None,
            'discount': None,
            'image_url': None,
            'product_url': None,
            'product_id': None,
            'description': None,
            'in_stock': True,
            'scraped_at': datetime.now().isoformat()
        }
        
        # Extract product name
        name_elem = (
            container.find(['h1', 'h2', 'h3', 'h4'], class_=re.compile(r'title|name|product', re.I)) or
            container.find('a', class_=re.compile(r'title|name', re.I)) or
            container.find(class_=re.compile(r'product.*name|title', re.I))
        )
        if name_elem:
            product['name'] = name_elem.get_text(strip=True)
        
        # Extract brand
        brand_elem = container.find(class_=re.compile(r'brand', re.I))
        if brand_elem:
            product['brand'] = brand_elem.get_text(strip=True)
        
        # Extract prices
        price_container = container.find(class_=re.compile(r'price', re.I))
        if price_container:
            price_text = price_container.get_text()
            price_data = self.parse_price(price_text)
            product['original_price'] = price_data['original']
            product['promotional_price'] = price_data['promotional']
            
            # Calculate discount
            if price_data['original'] and price_data['promotional']:
                discount_percent = ((price_data['original'] - price_data['promotional']) / price_data['original']) * 100
                product['discount'] = f"{discount_percent:.1f}%"
        
        # Extract image
        img_elem = container.find('img')
        if img_elem:
            product['image_url'] = img_elem.get('src') or img_elem.get('data-src') or img_elem.get('data-lazy-src')
            if product['image_url'] and product['image_url'].startswith('/'):
                product['image_url'] = self.base_url + product['image_url']
        
        # Extract product URL
        link_elem = container.find('a', href=True)
        if link_elem:
            product['product_url'] = link_elem['href']
            if product['product_url'].startswith('/'):
                product['product_url'] = self.base_url + product['product_url']
        
        # Extract product ID
        product['product_id'] = (
            container.get('data-product-id') or
            container.get('data-id') or
            container.get('id')
        )
        
        # Extract description
        desc_elem = container.find(class_=re.compile(r'description|desc', re.I))
        if desc_elem:
            product['description'] = desc_elem.get_text(strip=True)
        
        # Check stock status
        stock_elem = container.find(class_=re.compile(r'stock|availability', re.I))
        if stock_elem:
            stock_text = stock_elem.get_text().lower()
            product['in_stock'] = 'out' not in stock_text and 'unavailable' not in stock_text
        
        return product
    
    def scrape(self, max_pages: int = 1) -> List[Dict]:
        """Main scraping method"""
        print("=" * 80)
        print("Pick n Pay Promotions Scraper")
        print("=" * 80)
        print(f"\nTarget URL: {self.promotions_url}")
        print(f"Max pages to scrape: {max_pages}\n")
        
        all_products = []
        
        for page in range(1, max_pages + 1):
            html = self.fetch_page(self.promotions_url, page)
            
            if not html:
                print(f"Failed to fetch page {page}, stopping...")
                break
            
            products = self.parse_products(html)
            print(f"✓ Extracted {len(products)} products from page {page}\n")
            
            all_products.extend(products)
            
            # Be respectful - add delay between requests
            if page < max_pages:
                time.sleep(2)
        
        self.products = all_products
        return all_products
    
    def save_json(self, filename: str = 'pnp_promotions.json'):
        """Save products to JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.products, f, indent=2, ensure_ascii=False)
        print(f"✓ Saved {len(self.products)} products to {filename}")
    
    def save_csv(self, filename: str = 'pnp_promotions.csv'):
        """Save products to CSV file"""
        if not self.products:
            print("No products to save")
            return
        
        # Get all unique keys
        fieldnames = list(self.products[0].keys())
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.products)
        
        print(f"✓ Saved {len(self.products)} products to {filename}")
    
    def print_summary(self):
        """Print summary of scraped data"""
        if not self.products:
            print("No products found")
            return
        
        print("\n" + "=" * 80)
        print("SCRAPING SUMMARY")
        print("=" * 80)
        print(f"Total products: {len(self.products)}")
        
        # Count products with prices
        with_prices = sum(1 for p in self.products if p.get('promotional_price'))
        print(f"Products with prices: {with_prices}")
        
        # Count products with images
        with_images = sum(1 for p in self.products if p.get('image_url'))
        print(f"Products with images: {with_images}")
        
        # Show sample products
        print(f"\n📦 Sample Products (first 5):")
        for i, product in enumerate(self.products[:5], 1):
            print(f"\n{i}. {product.get('name', 'N/A')}")
            if product.get('brand'):
                print(f"   Brand: {product['brand']}")
            if product.get('promotional_price'):
                print(f"   Price: R{product['promotional_price']}")
            if product.get('original_price'):
                print(f"   Was: R{product['original_price']} (Save: {product.get('discount', 'N/A')})")
            if product.get('product_url'):
                print(f"   URL: {product['product_url'][:60]}...")
        
        print("\n" + "=" * 80)


def main():
    """Main function"""
    scraper = PnPScraper()
    
    # Scrape products (change max_pages to scrape more pages)
    products = scraper.scrape(max_pages=3)
    
    if products:
        # Save to both JSON and CSV
        scraper.save_json('pnp_promotions.json')
        scraper.save_csv('pnp_promotions.csv')
        
        # Print summary
        scraper.print_summary()
    else:
        print("\n⚠️  No products were extracted. The page structure might have changed.")
        print("Consider inspecting the HTML manually to update the selectors.")


if __name__ == "__main__":
    main()

