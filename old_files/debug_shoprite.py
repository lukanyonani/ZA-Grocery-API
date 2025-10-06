#!/usr/bin/env python3
"""Debug Shoprite HTML structure"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

chrome_options = Options()
chrome_options.add_argument('--headless=new')
chrome_options.add_argument('--no-sandbox')

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

try:
    url = "https://www.shoprite.co.za/c-2413/All-Departments/Food"
    print(f"Loading: {url}\n")
    driver.get(url)
    
    time.sleep(5)
    
    # Save full HTML
    with open('shoprite_rendered.html', 'w', encoding='utf-8') as f:
        f.write(driver.page_source)
    print("✓ Saved rendered HTML to shoprite_rendered.html\n")
    
    # Find product elements
    products = driver.find_elements(By.CLASS_NAME, 'item-product')
    print(f"Found {len(products)} product elements\n")
    
    if products:
        print("=" * 80)
        print("FIRST PRODUCT HTML:")
        print("=" * 80)
        print(products[0].get_attribute('outerHTML')[:2000])
        print("\n...")
        
        print("\n" + "=" * 80)
        print("FIRST PRODUCT TEXT:")
        print("=" * 80)
        print(products[0].text)
        
        print("\n" + "=" * 80)
        print("TRYING DIFFERENT SELECTORS:")
        print("=" * 80)
        
        # Try to find elements within first product
        selectors = [
            ('CLASS_NAME', '__feature-product-name'),
            ('CLASS_NAME', 'product-listening-click'),
            ('CLASS_NAME', 'special-price__price'),
            ('CLASS_NAME', 'js-item-product-price'),
            ('TAG_NAME', 'h3'),
            ('TAG_NAME', 'a'),
        ]
        
        for method, selector in selectors:
            try:
                if method == 'CLASS_NAME':
                    elems = products[0].find_elements(By.CLASS_NAME, selector)
                else:
                    elems = products[0].find_elements(By.TAG_NAME, selector)
                
                if elems:
                    print(f"\n✓ Found {len(elems)} elements with {method}: {selector}")
                    print(f"  First element text: {elems[0].text[:100]}")
                else:
                    print(f"\n✗ No elements found with {method}: {selector}")
            except Exception as e:
                print(f"\n❌ Error with {method}: {selector} - {e}")

finally:
    driver.quit()
    print("\n✓ Done")

