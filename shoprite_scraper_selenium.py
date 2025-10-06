#!/usr/bin/env python3
"""
Shoprite Products Scraper with Selenium
Handles React-rendered content
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import json
import csv
from datetime import datetime
import time
import re


class ShopriteSeleniumScraper:
    """Scraper for Shoprite using Selenium"""
    
    def __init__(self, headless: bool = True):
        self.base_url = "https://www.shoprite.co.za"
        self.food_url = "https://www.shoprite.co.za/c-2413/All-Departments/Food"
        self.products = []
        self.driver = None
        self.headless = headless
    
    def setup_driver(self):
        """Setup Chrome WebDriver"""
        print("Setting up Chrome WebDriver...")
        
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        print("✓ Chrome WebDriver initialized")
    
    def wait_for_products(self, timeout=20):
        """Wait for products to load"""
        print("Waiting for products to load...")
        
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'item-product'))
            )
            print("✓ Products loaded")
            # Give extra time for lazy-loaded content
            time.sleep(2)
            return True
        except:
            print("⚠️  Timeout waiting for products")
            return False
    
    def scroll_page(self):
        """Scroll to load all products"""
        print("Scrolling page...")
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        
        for i in range(3):
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
            print(f"  Scrolled {i+1}/3...")
        
        self.driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(1)
        print("✓ Finished scrolling")
    
    def extract_products(self):
        """Extract products from page"""
        print("Extracting products...")
        
        products = []
        product_elements = self.driver.find_elements(By.CLASS_NAME, 'item-product')
        print(f"Found {len(product_elements)} product elements")
        
        for idx, elem in enumerate(product_elements):
            try:
                product = {
                    'name': None,
                    'price': None,
                    'original_price': None,
                    'special_price': None,
                    'savings': None,
                    'on_special': False,
                    'product_code': None,
                    'product_url': None,
                    'image_url': None,
                    'in_stock': True,
                    'scraped_at': datetime.now().isoformat()
                }
                
                # Product code
                product['product_code'] = elem.get_attribute('data-product-code')
                
                # Product name
                try:
                    name_elem = elem.find_element(By.CLASS_NAME, '__feature-product-name')
                    product['name'] = name_elem.text.strip()
                except:
                    pass
                
                # Product URL
                try:
                    link = elem.find_element(By.CLASS_NAME, 'product-listening-click')
                    href = link.get_attribute('href')
                    product['product_url'] = href
                except:
                    pass
                
                # Image
                try:
                    img = elem.find_element(By.CLASS_NAME, 'thumb-image')
                    product['image_url'] = img.get_attribute('src') or img.get_attribute('data-src')
                except:
                    pass
                
                # Check for special price
                try:
                    special_container = elem.find_element(By.CLASS_NAME, 'special-price')
                    product['on_special'] = True
                    
                    # Special price
                    try:
                        special_price_elem = special_container.find_element(By.CLASS_NAME, 'special-price__price')
                        price_text = special_price_elem.text
                        product['special_price'] = self.parse_price(price_text)
                        product['price'] = product['special_price']
                    except:
                        pass
                    
                    # Original price
                    try:
                        was_elem = special_container.find_element(By.CLASS_NAME, 'special-price__was')
                        product['original_price'] = self.parse_price(was_elem.text)
                    except:
                        pass
                    
                    # Savings
                    try:
                        save_elem = special_container.find_element(By.CLASS_NAME, 'special-price__save')
                        product['savings'] = save_elem.text.strip()
                    except:
                        pass
                
                except:
                    # No special, get regular price
                    try:
                        price_elem = elem.find_element(By.CLASS_NAME, 'js-item-product-price')
                        product['price'] = self.parse_price(price_elem.text)
                    except:
                        pass
                
                # Check stock
                try:
                    elem.find_element(By.CLASS_NAME, 'out-of-stock')
                    product['in_stock'] = False
                except:
                    pass
                
                if product['name']:
                    products.append(product)
                    if (idx + 1) % 10 == 0:
                        print(f"  Processed {idx + 1}/{len(product_elements)}...")
            
            except Exception as e:
                continue
        
        return products
    
    def parse_price(self, price_text: str) -> float:
        """Parse price from text"""
        if not price_text:
            return None
        
        price_text = price_text.replace('R', '').replace(',', '.').strip()
        match = re.search(r'(\d+\.?\d*)', price_text)
        if match:
            try:
                return float(match.group(1))
            except:
                return None
        return None
    
    def scrape(self, url: str = None):
        """Main scraping method"""
        print("=" * 80)
        print("Shoprite Products Scraper (Selenium)")
        print("=" * 80)
        
        url = url or self.food_url
        print(f"\nTarget: {url}\n")
        
        try:
            self.setup_driver()
            
            print("Loading page...")
            self.driver.get(url)
            print("✓ Page loaded")
            
            self.wait_for_products()
            self.scroll_page()
            
            products = self.extract_products()
            print(f"\n✓ Extracted {len(products)} products")
            
            self.products = products
            return products
        
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return []
        
        finally:
            if self.driver:
                self.driver.quit()
                print("✓ Browser closed")
    
    def save_json(self, filename='shoprite_products.json'):
        """Save to JSON"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.products, f, indent=2, ensure_ascii=False)
        print(f"✓ Saved to {filename}")
    
    def save_csv(self, filename='shoprite_products.csv'):
        """Save to CSV"""
        if not self.products:
            return
        
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
        
        # Stats
        on_special = sum(1 for p in self.products if p.get('on_special'))
        in_stock = sum(1 for p in self.products if p.get('in_stock'))
        
        print(f"\nOn special: {on_special} ({on_special/len(self.products)*100:.1f}%)")
        print(f"In stock: {in_stock}")
        
        # Prices
        prices = [p['price'] for p in self.products if p.get('price')]
        if prices:
            import statistics
            print(f"\nPrice stats:")
            print(f"  Average: R{statistics.mean(prices):.2f}")
            print(f"  Min: R{min(prices):.2f}")
            print(f"  Max: R{max(prices):.2f}")
        
        # Samples
        print(f"\n📦 Sample Products:")
        for i, p in enumerate(self.products[:10], 1):
            print(f"\n{i}. {p.get('name', 'N/A')[:70]}")
            if p.get('price'):
                print(f"   Price: R{p['price']:.2f}")
            if p.get('on_special'):
                print(f"   🔥 ON SPECIAL")
                if p.get('original_price'):
                    print(f"   Was: R{p['original_price']:.2f}")
        
        print("\n" + "=" * 80)


def main():
    scraper = ShopriteSeleniumScraper(headless=True)
    products = scraper.scrape()
    
    if products:
        scraper.save_json()
        scraper.save_csv()
        scraper.print_summary()


if __name__ == "__main__":
    main()

