#!/usr/bin/env python3
"""
Woolworths Scraper
Scrapes products from Woolworths categories with pagination support
"""

import requests
from bs4 import BeautifulSoup
import json
import csv
from datetime import datetime
import time
import re
from urllib.parse import urljoin, urlparse


# Available Woolworths categories
WOOLWORTHS_CATEGORIES = {
    'fruit-vegetables': {
        'name': 'Fruit, Vegetables & Salads',
        'url': 'https://www.woolworths.co.za/cat/Food/Fruit-Vegetables-Salads/_/N-lllnam',
        'paginated': 'https://www.woolworths.co.za/cat/Food/Fruit-Vegetables-Salads/_/N-lllnam?No={page}&Nrpp=20'
    },
    'meat-poultry': {
        'name': 'Meat, Poultry & Fish',
        'url': 'https://www.woolworths.co.za/cat/Food/Meat-Poultry-Fish/_/N-d87rb7',
        'paginated': 'https://www.woolworths.co.za/cat/Food/Meat-Poultry-Fish/_/N-d87rb7?No={page}&Nrpp=20'
    },
    'dairy-eggs': {
        'name': 'Milk, Dairy & Eggs',
        'url': 'https://www.woolworths.co.za/cat/Food/Milk-Dairy-Eggs/_/N-1sqo44p',
        'paginated': 'https://www.woolworths.co.za/cat/Food/Milk-Dairy-Eggs/_/N-1sqo44p?No={page}&Nrpp=20'
    },
    'ready-meals': {
        'name': 'Ready Meals',
        'url': 'https://www.woolworths.co.za/cat/Food/Ready-Meals/_/N-s2csbp',
        'paginated': 'https://www.woolworths.co.za/cat/Food/Ready-Meals/_/N-s2csbp?No={page}&Nrpp=20'
    },
    'deli-entertaining': {
        'name': 'Deli & Entertaining',
        'url': 'https://www.woolworths.co.za/cat/Food/Deli-Entertaining/_/N-13b8g51',
        'paginated': 'https://www.woolworths.co.za/cat/Food/Deli-Entertaining/_/N-13b8g51?No={page}&Nrpp=20'
    },
    'food-to-go': {
        'name': 'Food To Go',
        'url': 'https://www.woolworths.co.za/cat/Food/Food-To-Go/_/N-11buko0',
        'paginated': 'https://www.woolworths.co.za/cat/Food/Food-To-Go/_/N-11buko0?No={page}&Nrpp=20'
    },
    'bakery': {
        'name': 'Bakery',
        'url': 'https://www.woolworths.co.za/cat/Food/Bakery/_/N-1bm2new',
        'paginated': 'https://www.woolworths.co.za/cat/Food/Bakery/_/N-1bm2new?No={page}&Nrpp=20'
    },
    'frozen-food': {
        'name': 'Frozen Food',
        'url': 'https://www.woolworths.co.za/cat/Food/Frozen-Food/_/N-j8pkwq',
        'paginated': 'https://www.woolworths.co.za/cat/Food/Frozen-Food/_/N-j8pkwq?No={page}&Nrpp=20'
    },
    'pantry': {
        'name': 'Pantry',
        'url': 'https://www.woolworths.co.za/cat/Food/Pantry/_/N-1lw4dzx',
        'paginated': 'https://www.woolworths.co.za/cat/Food/Pantry/_/N-1lw4dzx?No={page}&Nrpp=20'
    },
    'chocolates-sweets': {
        'name': 'Chocolates, Sweets & Snacks',
        'url': 'https://www.woolworths.co.za/cat/Food/Chocolates-Sweets-Snacks/_/N-1yz1i0m',
        'paginated': 'https://www.woolworths.co.za/cat/Food/Chocolates-Sweets-Snacks/_/N-1yz1i0m?No={page}&Nrpp=20'
    },
    'beverages': {
        'name': 'Beverages & Juices',
        'url': 'https://www.woolworths.co.za/cat/Food/Beverages-Juices/_/N-mnxddc',
        'paginated': 'https://www.woolworths.co.za/cat/Food/Beverages-Juices/_/N-mnxddc?No={page}&Nrpp=20'
    },
    'pets': {
        'name': 'Pets',
        'url': 'https://www.woolworths.co.za/cat/Food/Pets/_/N-l1demz',
        'paginated': 'https://www.woolworths.co.za/cat/Food/Pets/_/N-l1demz?No={page}&Nrpp=20'
    },
    'household': {
        'name': 'Household',
        'url': 'https://www.woolworths.co.za/cat/Food/Household/_/N-vvikef',
        'paginated': 'https://www.woolworths.co.za/cat/Food/Household/_/N-vvikef?No={page}&Nrpp=20'
    },
    'cleaning': {
        'name': 'Cleaning',
        'url': 'https://www.woolworths.co.za/cat/Food/Cleaning/_/N-o1v4pe',
        'paginated': 'https://www.woolworths.co.za/cat/Food/Cleaning/_/N-o1v4pe?No={page}&Nrpp=20'
    },
    'toiletries-health': {
        'name': 'Toiletries & Health',
        'url': 'https://www.woolworths.co.za/cat/Food/Toiletries-Health/_/N-1q1wl1r',
        'paginated': 'https://www.woolworths.co.za/cat/Food/Toiletries-Health/_/N-1q1wl1r?No={page}&Nrpp=20'
    },
    'kids': {
        'name': 'Kids',
        'url': 'https://www.woolworths.co.za/cat/Food/Kids/_/N-ymaf0z',
        'paginated': 'https://www.woolworths.co.za/cat/Food/Kids/_/N-ymaf0z?No={page}&Nrpp=20'
    },
    'flowers-plants': {
        'name': 'Flowers & Plants',
        'url': 'https://www.woolworths.co.za/cat/Food/Flowers-Plants/_/N-1z13rv1',
        'paginated': 'https://www.woolworths.co.za/cat/Food/Flowers-Plants/_/N-1z13rv1?No={page}&Nrpp=20'
    }
}


class WoolworthsScraper:
    """Woolworths scraper with category and pagination support"""
    
    def __init__(self, category: str = 'fruit-vegetables'):
        """Initialize scraper
        
        Args:
            category: Category to scrape (see WOOLWORTHS_CATEGORIES dict)
        """
        self.base_url = "https://www.woolworths.co.za"
        
        # Validate and set category
        if category not in WOOLWORTHS_CATEGORIES:
            available = ', '.join(WOOLWORTHS_CATEGORIES.keys())
            raise ValueError(f"Invalid category '{category}'. Available: {available}")
        
        self.category = category
        self.category_info = WOOLWORTHS_CATEGORIES[category]
        self.category_name = self.category_info['name']
        self.base_category_url = self.category_info['url']
        self.paginated_category_url = self.category_info['paginated']
        
        self.products = []
        
        # Headers to mimic a real browser
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
    
    def fetch_page(self, url: str) -> BeautifulSoup:
        """Fetch and parse a page"""
        try:
            print(f"Fetching: {url}")
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            print(f"✓ Page fetched successfully ({len(response.content)} bytes)")
            return BeautifulSoup(response.content, 'html.parser')
            
        except requests.RequestException as e:
            print(f"❌ Error fetching page: {e}")
            return None
    
    def parse_price(self, price_text: str) -> float:
        """Parse price from text"""
        if not price_text:
            return None
        
        # Remove currency symbols and extract number
        price_clean = re.sub(r'[^\d.,]', '', price_text)
        price_clean = price_clean.replace(',', '.')
        
        try:
            return float(price_clean)
        except ValueError:
            return None
    
    def extract_product_data(self, product_element) -> dict:
        """Extract product data from product element"""
        product = {
            'name': None,
            'price': None,
            'original_price': None,
            'special_price': None,
            'savings': None,
            'image_url': None,
            'product_url': None,
            'product_code': None,
            'category': self.category_name,
            'in_stock': True,
            'on_special': False,
            'scraped_at': datetime.now().isoformat()
        }
        
        try:
            # Extract product name - try multiple approaches
            name = None
            
            # Try to find name in various elements (Woolworths specific)
            name_selectors = [
                '.product-card__name a',  # Woolworths specific
                '.range--title',  # Woolworths specific
                '.product-card__name',  # Woolworths specific
                'h3', 'h2', 'h4', 'a[title]', 'span[title]',
                '.product-name', '.product-title', '.item-name',
                '[data-testid*="name"]', '[data-testid*="title"]'
            ]
            
            for selector in name_selectors:
                name_elem = product_element.select_one(selector)
                if name_elem:
                    name = name_elem.get_text().strip()
                    if name and len(name) > 3:  # Valid name
                        break
            
            # If no name found, try getting text from the element itself
            if not name:
                text = product_element.get_text().strip()
                # Look for text that might be a product name (not too long, not just numbers)
                lines = [line.strip() for line in text.split('\n') if line.strip()]
                for line in lines:
                    if 5 < len(line) < 100 and not line.isdigit() and 'R' not in line:
                        name = line
                        break
            
            product['name'] = name
            
            # Extract product URL
            link_elem = product_element.find('a', href=True)
            if link_elem:
                href = link_elem['href']
                product['product_url'] = href if href.startswith('http') else f"{self.base_url}{href}"
            
            # Extract image - try multiple approaches for Woolworths
            img_url = None
            
            # Try to find image in various elements (Woolworths specific)
            img_selectors = [
                '.product--image img',  # Woolworths specific
                '.product-card__img',  # Woolworths specific
                '.lazyload-wrapper img',  # Woolworths specific
                'img[src]',
                'img[data-src]',
                'img[data-original]',
                'img[data-lazy-src]',
                '.product-image img',
                '.product-card img',
                '.product-item img',
                'img'
            ]
            
            for selector in img_selectors:
                img_elem = product_element.select_one(selector)
                if img_elem:
                    # Try multiple attributes for image source
                    img_src = (img_elem.get('src') or 
                              img_elem.get('data-src') or 
                              img_elem.get('data-original') or
                              img_elem.get('data-lazy-src'))
                    
                    if img_src and not img_src.startswith('data:'):
                        # Clean up the URL - handle HTML entities
                        img_src = img_src.replace('&amp;', '&')
                        
                        # Clean up the URL
                        if img_src.startswith('//'):
                            img_src = 'https:' + img_src
                        elif not img_src.startswith('http'):
                            img_src = f"{self.base_url}{img_src}"
                        
                        img_url = img_src
                        break
            
            # If no image found in elements, try to extract from script tags
            if not img_url:
                # Get product ID for matching
                product_id = (product_element.get('data-cnstrc-item-id') or 
                             product_element.get('data-product-id') or
                             product_element.get('data-item-id'))
                
                # Also check for SKU ID in icon elements
                if not product_id:
                    icon_elem = product_element.select_one('.icon[data-id]')
                    if icon_elem:
                        product_id = icon_elem.get('data-id')
                
                if product_id:
                    # Look for image URLs in script tags that match this product
                    import re
                    for script in product_element.find_all('script'):
                        if script.string:
                            # Look for woolworthsstatic.co.za URLs in script content
                            matches = re.findall(r'https://assets\.woolworthsstatic\.co\.za/[^"\']*', script.string)
                            for match in matches:
                                if product_id in match:
                                    img_url = match
                                    break
                            if img_url:
                                break
                    
                    # If still no image, try to find in parent scripts
                    if not img_url:
                        parent = product_element.parent
                        while parent and not img_url:
                            for script in parent.find_all('script'):
                                if script.string:
                                    matches = re.findall(r'https://assets\.woolworthsstatic\.co\.za/[^"\']*', script.string)
                                    for match in matches:
                                        if product_id in match:
                                            img_url = match
                                            break
                                    if img_url:
                                        break
                            parent = parent.parent
            
            product['image_url'] = img_url
            
            # Extract price - look for price patterns in text
            text = product_element.get_text()
            
            # Try to get price from data attributes first (Woolworths specific)
            price_attr = product_element.get('data-cnstrc-item-price')
            if price_attr:
                product['price'] = self.parse_price(price_attr)
            
            # Try to find price in specific Woolworths elements
            if not product['price']:
                price_selectors = [
                    '.product__price .price',  # Woolworths specific
                    '.product-card__actions .price',  # Woolworths specific
                    '.font-graphic .price',  # Woolworths specific
                    '.product-price-combined .price',  # Woolworths specific
                    '.price',  # Generic price class
                    '.product-price',  # Generic product price
                ]
                
                for selector in price_selectors:
                    price_elem = product_element.select_one(selector)
                    if price_elem:
                        price_text = price_elem.get_text().strip()
                        price = self.parse_price(price_text)
                        if price and price > 0:
                            product['price'] = price
                            break
            
            # If no price from specific elements, look in text
            if not product['price']:
                price_patterns = [
                    r'R\s*(\d+(?:\.\d{2})?)',  # R 19.99
                    r'(\d+(?:\.\d{2})?)\s*R',  # 19.99 R
                    r'R\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',  # R 1,234.56
                ]
                
                for pattern in price_patterns:
                    matches = re.findall(pattern, text)
                    if matches:
                        # Get the first valid price
                        for match in matches:
                            price = self.parse_price(match)
                            if price and price > 0:
                                product['price'] = price
                                break
                        if product['price']:
                            break
            
            # Check for special pricing indicators
            special_indicators = ['special', 'sale', 'discount', 'reduced', 'save']
            text_lower = text.lower()
            for indicator in special_indicators:
                if indicator in text_lower:
                    product['on_special'] = True
                    break
            
            # Extract product code if available
            code_patterns = [
                r'\((\d+)\)',  # (123) format
                r'Code:\s*(\w+)',
                r'SKU:\s*(\w+)'
            ]
            
            for pattern in code_patterns:
                match = re.search(pattern, text)
                if match:
                    product['product_code'] = match.group(1)
                    break
            
        except Exception as e:
            print(f"⚠️  Error extracting product data: {e}")
        
        return product
    
    def scrape_category(self, max_pages: int = 1, max_products: int = None) -> list:
        """Scrape products from the category with pagination
        
        Args:
            max_pages: Number of pages to scrape
            max_products: Stop after N products (optional)
        """
        print("=" * 80)
        print("Woolworths Scraper")
        print("=" * 80)
        print(f"Category: {self.category_name}")
        print("=" * 80)
        
        all_products = []
        
        print(f"\nScraping {max_pages} page(s) from {self.category_name}\n")
        
        for page_num in range(max_pages):
            # Calculate page offset (Woolworths uses No parameter)
            page_offset = page_num * 20  # 20 products per page
            
            if page_num == 0:
                page_url = self.base_category_url
            else:
                page_url = self.paginated_category_url.format(page=page_offset)
            
            print(f"\n--- Page {page_num + 1} of {max_pages} ---")
            soup = self.fetch_page(page_url)
            
            if not soup:
                print(f"❌ Failed to fetch page {page_num + 1}")
                continue
            
            # Find product containers - Woolworths uses various selectors
            product_containers = []
            
            # Try different selectors for product containers
            selectors = [
                'article.product-card',  # Woolworths specific - main product cards
                'div.product-list__item',  # Woolworths specific
                'div[data-cnstrc-item-id]',  # Woolworths specific
                'div[data-testid*="product"]',
                'div.product-item',
                'div.product-tile', 
                'div[class*="product"]',
                'article[class*="product"]',
                'div[class*="item"]',
                'div[class*="tile"]',
                'div[class*="card"]',
                'div[class*="grid"] > div',
                'div[class*="list"] > div'
            ]
            
            for selector in selectors:
                containers = soup.select(selector)
                if containers and len(containers) > 5:  # Reasonable number of products
                    product_containers = containers
                    print(f"Found {len(containers)} product containers using selector: {selector}")
                    break
            
            if not product_containers:
                print("⚠️  No product containers found, trying alternative approach...")
                # Try to find any elements that might contain products
                product_containers = soup.find_all(['div', 'article'], class_=re.compile(r'product|item|tile|card'))
                print(f"Found {len(product_containers)} potential product elements")
            
            # Filter out containers that are too small or don't have meaningful content
            if product_containers:
                filtered_containers = []
                for container in product_containers:
                    text = container.get_text().strip()
                    # Skip containers that are too small or don't have product-like content
                    if len(text) > 10 and ('R' in text or any(word in text.lower() for word in ['kg', 'g', 'ml', 'l', 'pack', 'pk'])):
                        filtered_containers.append(container)
                
                if filtered_containers:
                    product_containers = filtered_containers
                    print(f"Filtered to {len(product_containers)} meaningful product containers")
            
            # Extract products
            page_products = []
            for i, container in enumerate(product_containers):
                if max_products and len(all_products) >= max_products:
                    break
                
                product = self.extract_product_data(container)
                
                # Only add if we have a name
                if product['name']:
                    page_products.append(product)
                    all_products.append(product)
                
                if (i + 1) % 10 == 0:
                    print(f"  Processed {i + 1}/{len(product_containers)} products...")
            
            print(f"✓ Extracted {len(page_products)} products from page {page_num + 1}")
            print(f"Total products so far: {len(all_products)}")
            
            # Check if we should stop early
            if max_products and len(all_products) >= max_products:
                all_products = all_products[:max_products]
                print(f"\n✓ Reached max_products limit ({max_products})")
                break
            
            # Be respectful - add delay between pages
            if page_num < max_pages - 1:
                print("  (Waiting 2 seconds before next page...)")
                time.sleep(2)
        
        print(f"\n{'=' * 80}")
        print(f"✓ Total products extracted: {len(all_products)}")
        print(f"{'=' * 80}")
        
        self.products = all_products
        return all_products
    
    def save_json(self, filename: str = None):
        """Save products to JSON"""
        if not self.products:
            print("⚠️  No products to save")
            return
        
        if filename is None:
            filename = f'woolworths_{self.category}_products.json'
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.products, f, indent=2, ensure_ascii=False)
        print(f"✓ Saved to {filename}")
    
    def save_csv(self, filename: str = None):
        """Save products to CSV"""
        if not self.products:
            return
        
        if filename is None:
            filename = f'woolworths_{self.category}_products.csv'
        
        fieldnames = list(self.products[0].keys())
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.products)
        print(f"✓ Saved to {filename}")
    
    def print_summary(self):
        """Print scraping summary"""
        if not self.products:
            print("\n⚠️  No products found")
            return
        
        print(f"\n{'=' * 80}")
        print(f"FOUND {len(self.products)} PRODUCTS")
        print(f"{'=' * 80}")
        
        # Price statistics
        prices = [p['price'] for p in self.products if p.get('price')]
        if prices:
            print(f"\nPrice statistics:")
            print(f"  Average: R{sum(prices)/len(prices):.2f}")
            print(f"  Median: R{sorted(prices)[len(prices)//2]:.2f}")
            print(f"  Min: R{min(prices):.2f}")
            print(f"  Max: R{max(prices):.2f}")
        
        # Show sample products
        print(f"\n📦 Sample Products (first 5):")
        for i, product in enumerate(self.products[:5], 1):
            price = product.get('price', 'N/A')
            name = product['name'][:60] + '...' if len(product['name']) > 60 else product['name']
            print(f"\n{i}. {name}")
            print(f"   Price: R{price}")
            if product.get('on_special'):
                print(f"   🔥 ON SPECIAL!")
            print(f"   URL: {product.get('product_url', 'N/A')[:80]}...")
        
        if len(self.products) > 5:
            print(f"\n... and {len(self.products) - 5} more")
        print("=" * 80)


def list_categories():
    """List all available categories"""
    print("\n" + "=" * 80)
    print("AVAILABLE WOOLWORTHS CATEGORIES")
    print("=" * 80)
    for key, info in WOOLWORTHS_CATEGORIES.items():
        print(f"  {key:20} - {info['name']}")
    print("=" * 80 + "\n")


def main():
    # Example: Scrape from fruit-vegetables category
    scraper = WoolworthsScraper(category='fruit-vegetables')
    
    # Scrape 2 pages
    products = scraper.scrape_category(max_pages=2)
    
    if products:
        scraper.save_json()
        scraper.save_csv()
        scraper.print_summary()
    else:
        print("\n❌ Failed to extract products")


if __name__ == "__main__":
    main()
