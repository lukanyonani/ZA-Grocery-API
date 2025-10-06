# Pick n Pay Scraper - Usage Guide

## Quick Start

```bash
# Run the working scraper
/home/luke/StudioProjects/Python/.venv/bin/python pnp_scraper_v2.py
```

That's it! The scraper will automatically:
1. Open a headless Chrome browser
2. Load the PnP promotions page
3. Wait for the Angular app to render
4. Capture API responses containing product data
5. Extract and save 100+ products to JSON and CSV files

## Output Files

After running, you'll get:

- **`pnp_products.json`** - Full product data in JSON format
- **`pnp_products.csv`** - Spreadsheet-friendly CSV format
- **`rendered_page.html`** - The fully rendered page HTML (for debugging)

## Sample Output

```json
{
  "name": "Olmeca Blanco Tequila 750ml",
  "brand": null,
  "promotional_price": 259.99,
  "image_url": "https://cdn-prd-02.pnp.co.za/...",
  "product_id": "000000000000112440_EA",
  "scraped_at": "2025-10-06T01:26:02.171365"
}
```

## How It Works

The PnP website is an Angular Single Page Application (SPA) that:

1. Loads with an empty `<pnp-root>` element
2. Executes JavaScript to render the UI
3. Makes API calls to fetch product data
4. Displays products dynamically

**Our scraper:**
- Uses Selenium with Chrome
- Monitors network traffic using Chrome DevTools Protocol
- Captures API responses containing product data
- Parses the JSON responses directly (no DOM scraping needed!)

## API Details

The scraper captures calls to:
```
https://www.pnp.co.za/pnphybris/v2/pnp-spa/products/search?fields=products(...)
```

This is the SAP Commerce Cloud (Hybris) API that PnP uses for their product catalog.

## Customization

### Change Number of Products

The API returns products in batches. The scraper automatically captures all API calls made during page load. To get more products:

1. Increase wait time
2. Scroll the page (lazy loading)
3. Navigate to next page

```python
# In pnp_scraper_v2.py, modify:
time.sleep(5)  # Change to time.sleep(10) for more time
```

### Run in Visible Mode (Debug)

```python
scraper = PnPSmartScraper(headless=False)
```

### Filter Products

```python
# After scraping
products = scraper.scrape()
filtered = [p for p in products if p['promotional_price'] < 100]
```

## Troubleshooting

### No products extracted

1. **Check internet connection**
2. **Update ChromeDriver**: `pip install --upgrade webdriver-manager`
3. **Run in visible mode** to see what's happening
4. **Check rendered_page.html** to see what was loaded

### ChromeDriver errors

```bash
# Reinstall webdriver-manager
pip install --force-reinstall webdriver-manager selenium
```

### "No module named..." errors

```bash
# Make sure you're using the venv
/home/luke/StudioProjects/Python/.venv/bin/python pnp_scraper_v2.py
```

## Advanced: Scraping Other Pages

To scrape different categories:

```python
scraper = PnPSmartScraper()
scraper.promotions_url = "https://www.pnp.co.za/c/dairy"
scraper.scrape()
```

## Performance

- **Speed**: ~30 seconds for 100+ products
- **API calls captured**: 2-3 product API responses
- **Memory**: ~200MB Chrome process
- **Bandwidth**: ~5MB per run

## Data Quality

From the 102 products extracted:
- ✅ **100%** have names
- ✅ **100%** have prices
- ✅ **100%** have product IDs
- ✅ **100%** have image URLs
- ⚠️ **Some** missing: product URLs, brands, original prices

## Legal & Ethics

- ✅ For personal/educational use
- ✅ Respects rate limiting (waits between requests)
- ✅ Uses standard browser (no stealth tactics)
- ⚠️ Check PnP's Terms of Service before commercial use
- ⚠️ Don't overwhelm their servers (use responsibly)

## Next Steps

Want to enhance the scraper? Ideas:

1. **Add pagination** - Scrape multiple pages
2. **Store in database** - SQLite, PostgreSQL, MongoDB
3. **Price tracking** - Run daily and track price changes
4. **Notifications** - Alert when favorite products go on sale
5. **Data analysis** - Visualize pricing trends

## Support

Having issues? Check:
1. Python version: `python3 --version` (should be 3.7+)
2. Dependencies: `/home/luke/StudioProjects/Python/.venv/bin/python -m pip list`
3. Chrome installed: `google-chrome --version`

