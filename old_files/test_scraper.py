#!/usr/bin/env python3
"""Test scraper with visual mode and save screenshot"""

from pnp_scraper_selenium import PnPSeleniumScraper

# Run with headless=False to see what's happening
scraper = PnPSeleniumScraper(headless=False)

try:
    scraper.setup_driver()
    print("Loading page...")
    scraper.driver.get(scraper.promotions_url)
    print("Page loaded. Taking screenshot...")
    
    # Wait a bit for content to load
    import time
    time.sleep(5)
    
    # Take screenshot
    scraper.driver.save_screenshot('page_screenshot.png')
    print("✓ Screenshot saved to: page_screenshot.png")
    
    # Save page source after JavaScript execution
    with open('page_source_after_js.html', 'w', encoding='utf-8') as f:
        f.write(scraper.driver.page_source)
    print("✓ Page source saved to: page_source_after_js.html")
    
    # Try to find product elements
    print("\nSearching for product elements...")
    
    # Check for common Angular/SPA product selectors
    selectors = [
        'cx-product-list-item',
        '.product-item',
        '.ProductItem',
        '[data-product]',
        'article',
        '.product-card',
        'a[href*="/p/"]'
    ]
    
    for selector in selectors:
        try:
            from selenium.webdriver.common.by import By
            elements = scraper.driver.find_elements(By.CSS_SELECTOR, selector)
            if elements:
                print(f"  ✓ Found {len(elements)} elements with: {selector}")
                if len(elements) > 0:
                    print(f"    Sample HTML: {elements[0].get_attribute('outerHTML')[:200]}...")
        except:
            pass
    
    input("\nPress Enter to close browser...")

finally:
    if scraper.driver:
        scraper.driver.quit()

