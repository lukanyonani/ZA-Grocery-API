#!/usr/bin/env python3
"""
Enhanced Pick n Pay Scraper
Waits for Angular app to render and captures API responses
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
import json
import csv
from datetime import datetime
import time
import re


# Available categories
CATEGORIES = {
    'promotions': {
        'name': 'Promotions',
        'base': 'https://www.pnp.co.za/c/pnpbase?query=:relevance:allCategories:pnpbase:isOnPromotion:On%20Promotion',
        'paginated': 'https://www.pnp.co.za/c/pnpbase?query=:relevance:allCategories:pnpbase:isOnPromotion:On%20Promotion&currentPage={page}'
    },
    'food-cupboard': {
        'name': 'Food Cupboard',
        'base': 'https://www.pnp.co.za/c/pnpbase?query=:relevance:allCategories:pnpbase:category:food-cupboard-423144840',
        'paginated': 'https://www.pnp.co.za/c/pnpbase?query=:relevance:allCategories:pnpbase:category:food-cupboard-423144840&currentPage={page}'
    },
    'personal-care': {
        'name': 'Personal Care & Hygiene',
        'base': 'https://www.pnp.co.za/c/pnpbase?query=:relevance:allCategories:pnpbase:category:personal-care-and-hygiene-423144840',
        'paginated': 'https://www.pnp.co.za/c/pnpbase?query=:relevance:allCategories:pnpbase:category:personal-care-and-hygiene-423144840&currentPage={page}'
    },
    'liquor': {
        'name': 'Liquor Store',
        'base': 'https://www.pnp.co.za/c/pnpbase?query=:relevance:allCategories:pnpbase:category:liquor-store-423144840',
        'paginated': 'https://www.pnp.co.za/c/pnpbase?query=:relevance:allCategories:pnpbase:category:liquor-store-423144840&currentPage={page}'
    },
    'home-appliances': {
        'name': 'Home, Appliances & Outdoor',
        'base': 'https://www.pnp.co.za/c/pnpbase?query=:relevance:allCategories:pnpbase:category:home-appliances-and-outdoor-423144840',
        'paginated': 'https://www.pnp.co.za/c/pnpbase?query=:relevance:allCategories:pnpbase:category:home-appliances-and-outdoor-423144840&currentPage={page}'
    },
    'snacks': {
        'name': 'Chocolates, Chips & Snacks',
        'base': 'https://www.pnp.co.za/c/pnpbase?query=:relevance:allCategories:pnpbase:category:chocolates-chips-and-snacks-423144840',
        'paginated': 'https://www.pnp.co.za/c/pnpbase?query=:relevance:allCategories:pnpbase:category:chocolates-chips-and-snacks-423144840&currentPage={page}'
    },
    'beverages': {
        'name': 'Beverages',
        'base': 'https://www.pnp.co.za/c/pnpbase?query=:relevance:allCategories:pnpbase:category:beverages-423144840',
        'paginated': 'https://www.pnp.co.za/c/pnpbase?query=:relevance:allCategories:pnpbase:category:beverages-423144840&currentPage={page}'
    },
    'home': {
        'name': 'Home & Appliances',
        'base': 'https://www.pnp.co.za/c/pnpbase?query=:relevance:allCategories:pnpbase:category:home-and-appliances-423144840',
        'paginated': 'https://www.pnp.co.za/c/pnpbase?query=:relevance:allCategories:pnpbase:category:home-and-appliances-423144840&currentPage={page}'
    },
    'household': {
        'name': 'Household & Cleaning',
        'base': 'https://www.pnp.co.za/c/pnpbase?query=:relevance:allCategories:pnpbase:category:household-and-cleaning-423144840',
        'paginated': 'https://www.pnp.co.za/c/pnpbase?query=:relevance:allCategories:pnpbase:category:household-and-cleaning-423144840&currentPage={page}'
    },
    'outdoor': {
        'name': 'Outdoor & DIY',
        'base': 'https://www.pnp.co.za/c/pnpbase?query=:relevance:allCategories:pnpbase:category:outdoor-and-diy-423144840',
        'paginated': 'https://www.pnp.co.za/c/pnpbase?query=:relevance:allCategories:pnpbase:category:outdoor-and-diy-423144840&currentPage={page}'
    },
    'dairy': {
        'name': 'Milk, Dairy & Eggs',
        'base': 'https://www.pnp.co.za/c/pnpbase?query=:relevance:allCategories:pnpbase:category:milk-dairy-and-eggs-423144840',
        'paginated': 'https://www.pnp.co.za/c/pnpbase?query=:relevance:allCategories:pnpbase:category:milk-dairy-and-eggs-423144840&currentPage={page}'
    },
    'health': {
        'name': 'Health & Wellness',
        'base': 'https://www.pnp.co.za/c/pnpbase?query=:relevance:allCategories:pnpbase:category:health-and-wellness-423144840',
        'paginated': 'https://www.pnp.co.za/c/pnpbase?query=:relevance:allCategories:pnpbase:category:health-and-wellness-423144840&currentPage={page}'
    },
    'pet': {
        'name': 'Pet Care',
        'base': 'https://www.pnp.co.za/c/pnpbase?query=:relevance:allCategories:pnpbase:category:pet-care-423144840',
        'paginated': 'https://www.pnp.co.za/c/pnpbase?query=:relevance:allCategories:pnpbase:category:pet-care-423144840&currentPage={page}'
    },
    'frozen': {
        'name': 'Frozen Food',
        'base': 'https://www.pnp.co.za/c/pnpbase?query=:relevance:allCategories:pnpbase:category:frozen-food-423144840',
        'paginated': 'https://www.pnp.co.za/c/pnpbase?query=:relevance:allCategories:pnpbase:category:frozen-food-423144840&currentPage={page}'
    },
    'stationery': {
        'name': 'Stationery',
        'base': 'https://www.pnp.co.za/c/pnpbase?query=:relevance:allCategories:pnpbase:category:stationery-423144840',
        'paginated': 'https://www.pnp.co.za/c/pnpbase?query=:relevance:allCategories:pnpbase:category:stationery-423144840&currentPage={page}'
    },
    'baby': {
        'name': 'Baby',
        'base': 'https://www.pnp.co.za/c/pnpbase?query=:relevance:allCategories:pnpbase:category:baby-423144840',
        'paginated': 'https://www.pnp.co.za/c/pnpbase?query=:relevance:allCategories:pnpbase:category:baby-423144840&currentPage={page}'
    },
    'coffee-tea': {
        'name': 'Coffee, Tea & Hot Drinks',
        'base': 'https://www.pnp.co.za/c/pnpbase?query=:relevance:allCategories:pnpbase:category:coffee-tea-and-hot-drinks-423144840',
        'paginated': 'https://www.pnp.co.za/c/pnpbase?query=:relevance:allCategories:pnpbase:category:coffee-tea-and-hot-drinks-423144840&currentPage={page}'
    },
    'fresh-produce': {
        'name': 'Fresh Fruit & Vegetables',
        'base': 'https://www.pnp.co.za/c/pnpbase?query=:relevance:allCategories:pnpbase:category:fresh-fruit-and-vegetables-423144840',
        'paginated': 'https://www.pnp.co.za/c/pnpbase?query=:relevance:allCategories:pnpbase:category:fresh-fruit-and-vegetables-423144840&currentPage={page}'
    },
    'electronics': {
        'name': 'Electronics & Office',
        'base': 'https://www.pnp.co.za/c/pnpbase?query=:relevance:allCategories:pnpbase:category:electronics-and-office-423144840',
        'paginated': 'https://www.pnp.co.za/c/pnpbase?query=:relevance:allCategories:pnpbase:category:electronics-and-office-423144840&currentPage={page}'
    },
    'bakery': {
        'name': 'Bakery',
        'base': 'https://www.pnp.co.za/c/pnpbase?query=:relevance:allCategories:pnpbase:category:bakery-423144840',
        'paginated': 'https://www.pnp.co.za/c/pnpbase?query=:relevance:allCategories:pnpbase:category:bakery-423144840&currentPage={page}'
    },
    'meat': {
        'name': 'Fresh Meat, Poultry & Seafood',
        'base': 'https://www.pnp.co.za/c/pnpbase?query=:relevance:allCategories:pnpbase:category:fresh-meat-poultry-and-seafood-423144840',
        'paginated': 'https://www.pnp.co.za/c/pnpbase?query=:relevance:allCategories:pnpbase:category:fresh-meat-poultry-and-seafood-423144840&currentPage={page}'
    },
    'deli': {
        'name': 'Deli & Party',
        'base': 'https://www.pnp.co.za/c/pnpbase?query=:relevance:allCategories:pnpbase:category:deli-and-party-423144840',
        'paginated': 'https://www.pnp.co.za/c/pnpbase?query=:relevance:allCategories:pnpbase:category:deli-and-party-423144840&currentPage={page}'
    },
    'toys': {
        'name': 'Toys & Games',
        'base': 'https://www.pnp.co.za/c/pnpbase?query=:relevance:allCategories:pnpbase:category:toys-and-games-423144840',
        'paginated': 'https://www.pnp.co.za/c/pnpbase?query=:relevance:allCategories:pnpbase:category:toys-and-games-423144840&currentPage={page}'
    },
    'ready-meals': {
        'name': 'Ready Meals & Desserts',
        'base': 'https://www.pnp.co.za/c/pnpbase?query=:relevance:allCategories:pnpbase:category:ready-meals-and-desserts-423144840',
        'paginated': 'https://www.pnp.co.za/c/pnpbase?query=:relevance:allCategories:pnpbase:category:ready-meals-and-desserts-423144840&currentPage={page}'
    },
    'flowers': {
        'name': 'Flowers & Plants',
        'base': 'https://www.pnp.co.za/c/pnpbase?query=:relevance:allCategories:pnpbase:category:flowers-and-plants-423144840',
        'paginated': 'https://www.pnp.co.za/c/pnpbase?query=:relevance:allCategories:pnpbase:category:flowers-and-plants-423144840&currentPage={page}'
    }
}


class PnPSmartScraper:
    """Smart scraper that waits for Angular to render and supports multiple categories"""
    
    def __init__(self, category: str = 'promotions', headless: bool = True):
        """Initialize scraper
        
        Args:
            category: Category to scrape (see CATEGORIES dict for options)
            headless: Run Chrome in headless mode
        """
        self.base_url = "https://www.pnp.co.za"
        
        # Validate and set category
        if category not in CATEGORIES:
            available = ', '.join(CATEGORIES.keys())
            raise ValueError(f"Invalid category '{category}'. Available: {available}")
        
        self.category = category
        self.category_info = CATEGORIES[category]
        self.category_name = self.category_info['name']
        self.base_category_url = self.category_info['base']
        self.paginated_category_url = self.category_info['paginated']
        
        # Legacy attributes (for backwards compatibility)
        self.promotions_url = CATEGORIES['promotions']['base']
        self.promotions_url_paginated = CATEGORIES['promotions']['paginated']
        
        self.products = []
        self.driver = None
        self.headless = headless
    
    def setup_driver(self):
        """Setup Chrome with network monitoring"""
        print("Setting up Chrome WebDriver...")
        
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        # Enable performance logging to capture network requests
        chrome_options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.set_page_load_timeout(30)
        print("✓ Chrome WebDriver initialized")
    
    def wait_for_angular(self, timeout=30):
        """Wait for Angular app to load"""
        print("Waiting for Angular app to load...")
        
        try:
            # Wait for the pnp-root to have children (Angular renders)
            WebDriverWait(self.driver, timeout).until(
                lambda d: len(d.find_element(By.TAG_NAME, 'pnp-root').find_elements(By.XPATH, './/*')) > 1
            )
            print("✓ Angular app loaded")
            
            # Give it extra time to render products
            time.sleep(5)
            return True
        except TimeoutException:
            print("⚠️  Timeout waiting for Angular")
            return False
    
    def extract_api_data(self):
        """Extract product data from network logs (API responses)"""
        print("Analyzing network traffic for API responses...")
        
        products = []
        logs = self.driver.get_log('performance')
        
        for entry in logs:
            try:
                log = json.loads(entry['message'])['message']
                
                # Look for network responses
                if log.get('method') == 'Network.responseReceived':
                    response_url = log['params']['response']['url']
                    
                    # Check if this is a product API call
                    if any(keyword in response_url.lower() for keyword in ['product', 'search', 'cnstrc.com', 'api']):
                        print(f"  Found API call: {response_url[:80]}...")
                        
                        # Try to get the response body
                        request_id = log['params']['requestId']
                        try:
                            response_body = self.driver.execute_cdp_cmd('Network.getResponseBody', {'requestId': request_id})
                            body_data = json.loads(response_body['body'])
                            
                            # Try to extract products from various API response formats
                            extracted = self.parse_api_response(body_data)
                            if extracted:
                                products.extend(extracted)
                                print(f"    ✓ Extracted {len(extracted)} products from API")
                        except:
                            pass
            except:
                continue
        
        return products
    
    def parse_api_response(self, data):
        """Parse product data from API response"""
        products = []
        
        # Handle different API response structures
        if isinstance(data, dict):
            # Constructor.io format
            if 'response' in data and 'results' in data['response']:
                for item in data['response']['results']:
                    product = self.normalize_product_data(item)
                    if product:
                        products.append(product)
            
            # SAP Commerce Cloud format
            elif 'products' in data:
                for item in data['products']:
                    product = self.normalize_product_data(item)
                    if product:
                        products.append(product)
            
            # Direct results array
            elif 'results' in data:
                for item in data['results']:
                    product = self.normalize_product_data(item)
                    if product:
                        products.append(product)
        
        elif isinstance(data, list):
            for item in data:
                product = self.normalize_product_data(item)
                if product:
                    products.append(product)
        
        return products
    
    def normalize_product_data(self, item):
        """Normalize product data from various API formats"""
        try:
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
                'scraped_at': datetime.now().isoformat()
            }
            
            # Extract name
            product['name'] = item.get('value') or item.get('name') or item.get('title') or item.get('description')
            
            # Extract ID
            product['product_id'] = item.get('data', {}).get('id') or item.get('id') or item.get('code')
            
            # Extract image
            image = item.get('data', {}).get('image_url') or item.get('image') or item.get('imageUrl') or item.get('images', [{}])[0].get('url')
            if image:
                product['image_url'] = image if image.startswith('http') else f"https:{image}"
            
            # Extract URL
            url = item.get('data', {}).get('url') or item.get('url') or item.get('link')
            if url:
                product['product_url'] = url if url.startswith('http') else f"{self.base_url}{url}"
            
            # Extract price
            price_data = item.get('data', {}).get('price') or item.get('price') or item.get('priceInfo', {})
            if isinstance(price_data, (int, float)):
                product['promotional_price'] = float(price_data)
            elif isinstance(price_data, dict):
                product['promotional_price'] = price_data.get('value') or price_data.get('currentPrice', {}).get('value')
                product['original_price'] = price_data.get('was') or price_data.get('originalPrice', {}).get('value')
            
            # Extract brand
            product['brand'] = item.get('data', {}).get('brand') or item.get('brand') or item.get('manufacturer')
            
            # Calculate discount
            if product['original_price'] and product['promotional_price']:
                discount = ((product['original_price'] - product['promotional_price']) / product['original_price']) * 100
                product['discount'] = f"{discount:.1f}%"
            
            return product if product['name'] else None
        except:
            return None
    
    def extract_from_dom(self):
        """Fallback: extract from rendered DOM"""
        print("Extracting from rendered DOM...")
        
        products = []
        
        # Save the fully rendered page
        with open('rendered_page.html', 'w', encoding='utf-8') as f:
            f.write(self.driver.page_source)
        print("  ✓ Saved rendered HTML to: rendered_page.html")
        
        # Try multiple selectors
        selectors = [
            'a[href*="/p/"]',  # Product links
            '[class*="product"]',
            '[data-product]',
            'article',
        ]
        
        all_elements = []
        for selector in selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    print(f"  Found {len(elements)} elements with: {selector}")
                    all_elements.extend(elements)
            except:
                pass
        
        # Remove duplicates
        seen = set()
        unique_elements = []
        for elem in all_elements:
            try:
                html = elem.get_attribute('outerHTML')[:100]
                if html not in seen:
                    seen.add(html)
                    unique_elements.append(elem)
            except:
                pass
        
        print(f"  Processing {len(unique_elements)} unique elements...")
        
        for elem in unique_elements:
            try:
                product = {
                    'name': None,
                    'price': None,
                    'promotional_price': None,
                    'original_price': None,
                    'product_url': None,
                    'image_url': None,
                    'scraped_at': datetime.now().isoformat()
                }
                
                # Get URL
                if elem.tag_name == 'a':
                    product['product_url'] = elem.get_attribute('href')
                else:
                    try:
                        link = elem.find_element(By.TAG_NAME, 'a')
                        product['product_url'] = link.get_attribute('href')
                    except:
                        pass
                
                # Get text content
                text = elem.text.strip()
                if text and len(text) > 3:
                    # Try to extract name and price from text
                    lines = [l.strip() for l in text.split('\n') if l.strip()]
                    if lines:
                        product['name'] = lines[0]
                        
                        # Look for prices in remaining lines
                        for line in lines[1:]:
                            if 'R' in line or any(c.isdigit() for c in line):
                                prices = re.findall(r'R?\s*(\d+[.,]?\d*)', line)
                                if prices:
                                    product['promotional_price'] = float(prices[-1].replace(',', '.'))
                                    if len(prices) > 1:
                                        product['original_price'] = float(prices[0].replace(',', '.'))
                
                # Get image
                try:
                    img = elem.find_element(By.TAG_NAME, 'img')
                    product['image_url'] = img.get_attribute('src') or img.get_attribute('data-src')
                except:
                    pass
                
                if product['name'] and len(product['name']) > 3:
                    products.append(product)
            except:
                pass
        
        return products
    
    def scrape(self, max_pages: int = 1, max_products: int = None):
        """Main scraping method with pagination support
        
        Args:
            max_pages: Number of pages to scrape (default: 1)
            max_products: Stop after N products (optional)
        """
        print("=" * 80)
        print("Pick n Pay Smart Scraper")
        print("=" * 80)
        print(f"Category: {self.category_name}")
        print("=" * 80)
        
        all_products = []
        
        try:
            self.setup_driver()
            
            print(f"\nScraping {max_pages} page(s) from {self.category_name}\n")
            
            for page_num in range(max_pages):
                # Page numbering: Page 1 has no param, Page 2 is currentPage=1, etc.
                if page_num == 0:
                    page_url = self.base_category_url
                else:
                    page_url = self.paginated_category_url.format(page=page_num)
                
                print(f"\n{'=' * 80}")
                print(f"PAGE {page_num + 1} of {max_pages}")
                print(f"{'=' * 80}")
                
                print(f"Loading: {page_url}")
                self.driver.get(page_url)
                print("✓ Page loaded")
                
                # Wait for Angular
                self.wait_for_angular()
                
                # Strategy 1: Extract from API responses
                api_products = self.extract_api_data()
                if api_products:
                    print(f"✓ Extracted {len(api_products)} products from API")
                    all_products.extend(api_products)
                else:
                    # Strategy 2: Extract from DOM if API didn't work
                    print("⚠️  No products from API, trying DOM extraction...")
                    dom_products = self.extract_from_dom()
                    if dom_products:
                        print(f"✓ Extracted {len(dom_products)} products from DOM")
                        all_products.extend(dom_products)
                    else:
                        print(f"❌ No products found on page {page_num + 1}")
                        break
                
                print(f"Total products so far: {len(all_products)}")
                
                # Check if we should stop early
                if max_products and len(all_products) >= max_products:
                    all_products = all_products[:max_products]
                    print(f"\n✓ Reached max_products limit ({max_products})")
                    break
                
                # Be respectful - add delay between pages
                if page_num < max_pages - 1:
                    print("  (Waiting 3 seconds before next page...)")
                    time.sleep(3)
            
            print(f"\n{'=' * 80}")
            print(f"✓ Total products extracted: {len(all_products)}")
            print(f"{'=' * 80}")
            
            self.products = all_products
            return all_products
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return all_products if all_products else []
        
        finally:
            if self.driver:
                self.driver.quit()
                print("\n✓ Browser closed")
    
    def save_json(self, filename: str = None):
        """Save to JSON"""
        if filename is None:
            filename = f'pnp_{self.category}_products.json'
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.products, f, indent=2, ensure_ascii=False)
        print(f"✓ Saved to {filename}")
    
    def save_csv(self, filename: str = None):
        """Save to CSV"""
        if not self.products:
            return
        
        if filename is None:
            filename = f'pnp_{self.category}_products.csv'
        
        fieldnames = list(self.products[0].keys())
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.products)
        print(f"✓ Saved to {filename}")
    
    def print_summary(self):
        """Print summary"""
        if not self.products:
            print("\n⚠️  No products found")
            return
        
        print("\n" + "=" * 80)
        print(f"FOUND {len(self.products)} PRODUCTS")
        print("=" * 80)
        
        for i, p in enumerate(self.products[:10], 1):
            print(f"\n{i}. {p.get('name', 'N/A')[:70]}")
            if p.get('promotional_price'):
                print(f"   Price: R{p['promotional_price']}")
            if p.get('original_price'):
                print(f"   Was: R{p['original_price']}")
            if p.get('product_url'):
                print(f"   URL: {p['product_url'][:70]}...")
        
        if len(self.products) > 10:
            print(f"\n... and {len(self.products) - 10} more")
        print("=" * 80)


def list_categories():
    """List all available categories"""
    print("\n" + "=" * 80)
    print("AVAILABLE CATEGORIES")
    print("=" * 80)
    for key, info in CATEGORIES.items():
        print(f"  {key:20} - {info['name']}")
    print("=" * 80 + "\n")


def main():
    # Example: Scrape from beverages category
    # Change category parameter to scrape different categories
    # Run list_categories() to see all available categories
    
    scraper = PnPSmartScraper(category='beverages', headless=True)
    
    # Scrape multiple pages
    # Each page has ~30-40 products
    # Change max_pages to scrape more pages
    products = scraper.scrape(max_pages=2)  # 2 pages (~60-80 products)
    
    if products:
        scraper.save_json()
        scraper.save_csv()
        scraper.print_summary()
    else:
        print("\n❌ Failed to extract products")
        print("Try running with headless=False to debug")


if __name__ == "__main__":
    main()

