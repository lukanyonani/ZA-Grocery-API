#!/usr/bin/env python3
"""
Pick n Pay Promotions Scraper with Selenium
Handles JavaScript-rendered content from Angular SPA
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import json
import csv
from datetime import datetime
from typing import List, Dict
import time
import re


class PnPSeleniumScraper:
    """Scraper for Pick n Pay promotional products using Selenium"""
    
    def __init__(self, headless: bool = True):
        self.base_url = "https://www.pnp.co.za"
        self.promotions_url = "https://www.pnp.co.za/c/pnpbase?query=:relevance:allCategories:pnpbase:isOnPromotion:On%20Promotion"
        self.products = []
        self.driver = None
        self.headless = headless
    
    def setup_driver(self):
        """Setup Selenium WebDriver"""
        print("Setting up Chrome WebDriver...")
        
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # Disable images for faster loading (optional)
        # prefs = {"profile.managed_default_content_settings.images": 2}
        # chrome_options.add_experimental_option("prefs", prefs)
        
        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            print("✓ Chrome WebDriver initialized")
        except Exception as e:
            print(f"❌ Error initializing Chrome: {e}")
            print("\nTrying Firefox as fallback...")
            try:
                from selenium.webdriver.firefox.options import Options as FirefoxOptions
                firefox_options = FirefoxOptions()
                if self.headless:
                    firefox_options.add_argument('--headless')
                self.driver = webdriver.Firefox(options=firefox_options)
                print("✓ Firefox WebDriver initialized")
            except Exception as e2:
                print(f"❌ Error initializing Firefox: {e2}")
                raise Exception("Could not initialize any WebDriver. Install ChromeDriver or GeckoDriver.")
    
    def wait_for_products(self, timeout: int = 20):
        """Wait for products to load on the page"""
        print("Waiting for products to load...")
        
        # Try multiple selectors that might contain products
        selectors = [
            (By.CSS_SELECTOR, '[data-test="product-item"]'),
            (By.CSS_SELECTOR, '.product-item'),
            (By.CSS_SELECTOR, '.product-card'),
            (By.CSS_SELECTOR, '.product-tile'),
            (By.CSS_SELECTOR, '[class*="product"]'),
            (By.CSS_SELECTOR, 'cx-product-list-item'),
            (By.CSS_SELECTOR, 'app-product-card'),
            (By.CSS_SELECTOR, '[class*="ProductCard"]'),
            (By.TAG_NAME, 'cx-product-list-item'),
        ]
        
        for by, selector in selectors:
            try:
                WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_element_located((by, selector))
                )
                print(f"✓ Products found using selector: {selector}")
                return True
            except TimeoutException:
                continue
        
        print("⚠️  Standard selectors didn't find products. Trying to detect dynamically...")
        time.sleep(5)  # Give page more time to render
        return True
    
    def scroll_page(self):
        """Scroll to load lazy-loaded products"""
        print("Scrolling to load all products...")
        
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        scroll_attempts = 0
        max_scrolls = 10
        
        while scroll_attempts < max_scrolls:
            # Scroll down
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            # Calculate new height
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            
            if new_height == last_height:
                break
            
            last_height = new_height
            scroll_attempts += 1
            print(f"  Scrolled {scroll_attempts}/{max_scrolls}...")
        
        # Scroll back to top
        self.driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(1)
        print("✓ Finished scrolling")
    
    def extract_products(self) -> List[Dict]:
        """Extract product information from the loaded page"""
        products = []
        
        # Get page source and find all potential product elements
        print("Extracting product data...")
        
        # Try to find product containers
        product_containers = []
        
        # Multiple strategies to find products
        selectors_to_try = [
            'cx-product-list-item',
            '[data-test="product-item"]',
            '.product-item',
            '.product-card',
            '[class*="product"]',
            'app-product-card',
            '[class*="ProductCard"]',
        ]
        
        for selector in selectors_to_try:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    product_containers = elements
                    print(f"✓ Found {len(elements)} elements using: {selector}")
                    break
            except:
                continue
        
        if not product_containers:
            print("⚠️  No product containers found with standard selectors")
            print("Analyzing page structure...")
            
            # Save page source for debugging
            with open('debug_page_source.html', 'w', encoding='utf-8') as f:
                f.write(self.driver.page_source)
            print("✓ Saved page source to debug_page_source.html")
            
            # Try to find any links that might be products
            all_links = self.driver.find_elements(By.TAG_NAME, 'a')
            product_containers = [link for link in all_links if '/p/' in link.get_attribute('href') or '']
            
            if product_containers:
                print(f"✓ Found {len(product_containers)} product links")
        
        # Extract data from each container
        for idx, container in enumerate(product_containers):
            try:
                product = self.extract_product_from_element(container)
                if product and product.get('name'):
                    products.append(product)
                    if (idx + 1) % 10 == 0:
                        print(f"  Processed {idx + 1} products...")
            except Exception as e:
                continue
        
        return products
    
    def extract_product_from_element(self, element) -> Dict:
        """Extract product data from a WebElement"""
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
            'scraped_at': datetime.now().isoformat()
        }
        
        try:
            # Extract product URL
            try:
                if element.tag_name == 'a':
                    product['product_url'] = element.get_attribute('href')
                else:
                    link = element.find_element(By.TAG_NAME, 'a')
                    product['product_url'] = link.get_attribute('href')
            except:
                pass
            
            # Extract product name
            try:
                name_selectors = [
                    '.product-name',
                    '.product-title',
                    '[class*="product-name"]',
                    '[class*="ProductName"]',
                    'h2', 'h3', 'h4',
                    '[data-test="product-name"]'
                ]
                for selector in name_selectors:
                    try:
                        name_elem = element.find_element(By.CSS_SELECTOR, selector)
                        product['name'] = name_elem.text.strip()
                        if product['name']:
                            break
                    except:
                        continue
            except:
                pass
            
            # Extract price
            try:
                price_selectors = [
                    '.price',
                    '[class*="price"]',
                    '[class*="Price"]',
                    '[data-test="product-price"]'
                ]
                for selector in price_selectors:
                    try:
                        price_elem = element.find_element(By.CSS_SELECTOR, selector)
                        price_text = price_elem.text
                        prices = re.findall(r'R?\s*(\d+[.,]?\d*)', price_text)
                        if prices:
                            product['promotional_price'] = float(prices[-1].replace(',', '.'))
                            if len(prices) > 1:
                                product['original_price'] = float(prices[0].replace(',', '.'))
                                discount = ((product['original_price'] - product['promotional_price']) / product['original_price']) * 100
                                product['discount'] = f"{discount:.1f}%"
                            break
                    except:
                        continue
            except:
                pass
            
            # Extract image
            try:
                img = element.find_element(By.TAG_NAME, 'img')
                product['image_url'] = img.get_attribute('src') or img.get_attribute('data-src')
            except:
                pass
            
            # Extract brand
            try:
                brand_selectors = ['.brand', '[class*="brand"]', '[class*="Brand"]']
                for selector in brand_selectors:
                    try:
                        brand_elem = element.find_element(By.CSS_SELECTOR, selector)
                        product['brand'] = brand_elem.text.strip()
                        if product['brand']:
                            break
                    except:
                        continue
            except:
                pass
            
        except Exception as e:
            pass
        
        return product
    
    def scrape(self, max_pages: int = 1) -> List[Dict]:
        """Main scraping method"""
        print("=" * 80)
        print("Pick n Pay Promotions Scraper (Selenium)")
        print("=" * 80)
        print(f"\nTarget URL: {self.promotions_url}")
        print(f"Headless mode: {self.headless}\n")
        
        try:
            self.setup_driver()
            
            # Navigate to page
            print(f"Loading page...")
            self.driver.get(self.promotions_url)
            print("✓ Page loaded")
            
            # Wait for products to load
            self.wait_for_products()
            
            # Scroll to load all products
            self.scroll_page()
            
            # Extract products
            products = self.extract_products()
            print(f"\n✓ Extracted {len(products)} products")
            
            self.products = products
            return products
            
        except Exception as e:
            print(f"❌ Error during scraping: {e}")
            return []
        
        finally:
            if self.driver:
                self.driver.quit()
                print("✓ WebDriver closed")
    
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
        
        with_prices = sum(1 for p in self.products if p.get('promotional_price'))
        print(f"Products with prices: {with_prices}")
        
        with_images = sum(1 for p in self.products if p.get('image_url'))
        print(f"Products with images: {with_images}")
        
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
                print(f"   URL: {product['product_url'][:70]}...")
        
        print("\n" + "=" * 80)


def main():
    """Main function"""
    # Set headless=False to see the browser in action
    scraper = PnPSeleniumScraper(headless=True)
    
    # Scrape products
    products = scraper.scrape()
    
    if products:
        # Save to both JSON and CSV
        scraper.save_json('pnp_promotions_selenium.json')
        scraper.save_csv('pnp_promotions_selenium.csv')
        
        # Print summary
        scraper.print_summary()
    else:
        print("\n⚠️  No products were extracted.")
        print("Tips:")
        print("  1. Run with headless=False to see what's happening")
        print("  2. Check debug_page_source.html for the actual HTML")
        print("  3. The site might be using anti-bot protection")


if __name__ == "__main__":
    main()

