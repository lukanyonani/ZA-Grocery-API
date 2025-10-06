# Pick n Pay Promotions Scraper 🛒

A comprehensive Python web scraper for extracting promotional product data from the Pick n Pay website.

## ✅ Working Scraper

**`pnp_scraper_v2.py`** - **RECOMMENDED** - Successfully extracts 100+ products by monitoring API calls!

## Features

- 🛒 Scrapes promotional products from PnP website
- 💰 Extracts prices, discounts, and product details
- 📊 Exports data to JSON and CSV formats
- 🔄 Supports multi-page scraping
- 🛡️ Includes error handling and rate limiting
- 📝 Comprehensive product information extraction

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Install ChromeDriver (for Selenium version)
# Ubuntu/Debian:
sudo apt-get install chromium-chromedriver
# Or download from: https://chromedriver.chromium.org/

# Alternative: Use Firefox with GeckoDriver
sudo apt-get install firefox-geckodriver
```

## Usage

### Basic Usage (Static HTML - Fast but limited)

```bash
python pnp_scraper.py
```

### V2 Scraper (RECOMMENDED - Network Monitoring)

```bash
# Best option - Monitors API calls and extracts from responses
python3 pnp_scraper_v2.py
# or with venv:
/home/luke/StudioProjects/Python/.venv/bin/python pnp_scraper_v2.py
```

### Selenium Version (JavaScript-rendered)

```bash
python3 pnp_scraper_selenium.py
```

### Test/Debug Tools

```bash
# Inspect HTML structure
python3 inspect_html.py

# Interactive test (non-headless mode)
python3 test_scraper.py
```

### Programmatic Usage

**Static scraper:**
```python
from pnp_scraper import PnPScraper

scraper = PnPScraper()
products = scraper.scrape(max_pages=5)
scraper.save_json('my_promotions.json')
scraper.save_csv('my_promotions.csv')
scraper.print_summary()
```

**Selenium scraper (recommended):**
```python
from pnp_scraper_selenium import PnPSeleniumScraper

# Set headless=False to see the browser
scraper = PnPSeleniumScraper(headless=True)
products = scraper.scrape()
scraper.save_json('my_promotions.json')
scraper.save_csv('my_promotions.csv')
scraper.print_summary()
```

## Extracted Data

The scraper extracts the following information for each product:

- **name**: Product name
- **brand**: Brand name (if available)
- **price**: Current price
- **original_price**: Original price before discount
- **promotional_price**: Promotional/sale price
- **discount**: Discount percentage
- **image_url**: Product image URL
- **product_url**: Link to product page
- **product_id**: Unique product identifier
- **description**: Product description
- **in_stock**: Stock availability status
- **scraped_at**: Timestamp of when data was scraped

## Output Files

- `pnp_promotions.json` - JSON format with all product data
- `pnp_promotions.csv` - CSV format for easy analysis in Excel/Sheets

## Configuration

Edit the scraper settings in `pnp_scraper.py`:

```python
# Change the number of pages to scrape
products = scraper.scrape(max_pages=3)  # Default is 3

# Modify delay between requests (in seconds)
time.sleep(2)  # Default is 2 seconds
```

## Notes

- The scraper includes a 2-second delay between page requests to be respectful to the server
- User-Agent headers are set to mimic a real browser
- The scraper uses multiple fallback strategies to find product elements
- If no products are found, the page structure may have changed and selectors need updating

## Legal & Ethical Considerations

- ✅ Use responsibly and respect the website's terms of service
- ✅ Rate limiting is implemented to avoid overwhelming the server
- ✅ For personal/research use only
- ⚠️ Check PnP's robots.txt and terms of service before scraping
- ⚠️ Do not use scraped data for commercial purposes without permission

## Troubleshooting

If the scraper doesn't find products:

1. The website structure may have changed
2. Check if the page requires JavaScript rendering (consider using Selenium)
3. Verify the URL is correct and accessible
4. Check your internet connection

## Requirements

- Python 3.7+
- requests
- beautifulsoup4
- lxml

## License

For educational purposes only.

