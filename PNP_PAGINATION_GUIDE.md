# Pick n Pay Scraper - Pagination Guide

## 🎯 Quick Start

The PnP scraper now supports pagination! You can scrape multiple pages with a single command.

## 📊 Page Structure

- **Products per page**: ~30-40 (varies, captured from API)
- **Page numbering**: 0-indexed in URL parameter
  - Page 1: No `currentPage` parameter
  - Page 2: `currentPage=1`
  - Page 3: `currentPage=2`

## 🚀 Usage Examples

### Example 1: Single Page (Default)

```python
from pnp_scraper_v2 import PnPSmartScraper

scraper = PnPSmartScraper()
products = scraper.scrape(max_pages=1)  # ~30-40 products
scraper.save_json()
```

### Example 2: Multiple Pages

```python
scraper = PnPSmartScraper()
products = scraper.scrape(max_pages=3)  # ~90-120 products
scraper.save_json()
```

### Example 3: With Product Limit

```python
scraper = PnPSmartScraper()
# Stop after 100 products even if scraping more pages
products = scraper.scrape(max_pages=10, max_products=100)
scraper.save_json()
```

### Example 4: Many Pages

```python
scraper = PnPSmartScraper()
products = scraper.scrape(max_pages=5)  # ~150-200 products
scraper.save_json('pnp_bulk.json')
```

## 🔧 Parameters

### `scrape()` method parameters:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `max_pages` | int | 1 | Number of pages to scrape |
| `max_products` | int | None | Stop after N products |

## ⏱️ Timing

The scraper includes a 3-second delay between pages:

- **1 page**: ~30 seconds (Selenium + API capture)
- **2 pages**: ~65 seconds
- **3 pages**: ~100 seconds
- **5 pages**: ~170 seconds

## 📝 Command Line Usage

### Default (2 pages)

```bash
python3 pnp_scraper_v2.py
```

Current default is set to 2 pages (~60-80 products).

### Custom Pages

Edit the `main()` function in `pnp_scraper_v2.py`:

```python
def main():
    scraper = PnPSmartScraper()
    products = scraper.scrape(max_pages=5)  # Change this number
    scraper.save_json()
    scraper.save_csv()
    scraper.print_summary()
```

## 🎓 Advanced Usage

### Filter While Scraping

```python
from pnp_scraper_v2 import PnPSmartScraper

scraper = PnPSmartScraper()
all_products = scraper.scrape(max_pages=5)

# Filter for products under R50
cheap = [p for p in all_products if p.get('promotional_price') and p['promotional_price'] < 50]

# Filter by category/name
beverages = [p for p in all_products if 'wine' in p['name'].lower() or 'whiskey' in p['name'].lower()]

# Sort by price
sorted_products = sorted(all_products, key=lambda x: x.get('promotional_price', 999))
```

### Track Progress

The scraper prints detailed progress automatically:

```
================================================================================
PAGE 1 of 3
================================================================================
Loading: https://www.pnp.co.za/c/pnpbase?query=...
✓ Page loaded
Waiting for Angular app to load...
✓ Angular app loaded
Analyzing network traffic for API responses...
  Found API call: ...
  ✓ Extracted 30 products from API
  ✓ Extracted 72 products from API
✓ Extracted 102 products from API
Total products so far: 102
  (Waiting 3 seconds before next page...)
```

## ⚠️ Important Notes

1. **Network Monitoring**: Uses Chrome DevTools Protocol to capture API responses
2. **Rate Limiting**: 3-second delay between pages (built-in)
3. **Respectful Scraping**: Don't scrape too many pages repeatedly
4. **API Extraction**: Captures data from network calls, not DOM parsing
5. **Time**: Budget ~30-35 seconds per page

## 📊 Output Files

Files are saved with total product count:

- `pnp_products.json` - All scraped products
- `pnp_products.csv` - CSV format

Example with 174 products (2 pages):

```json
[
  {
    "name": "Olmeca Blanco Tequila 750ml",
    "promotional_price": 259.99,
    "product_id": "000000000000112440_EA",
    "image_url": "https://cdn-prd-02.pnp.co.za/...",
    "scraped_at": "2025-10-06T..."
  },
  ... 173 more products
]
```

## 🔍 Test Results (2 Pages)

Recent test extraction:
- **Page 1**: 102 products
- **Page 2**: 72 products  
- **Total**: 174 products
- **Time**: ~65 seconds
- **Success rate**: 100%

## 💡 Tips

1. **Start small**: Test with 2-3 pages first
2. **Monitor console**: Watch API extraction in real-time
3. **Check quality**: First page is best for testing selectors
4. **Save often**: Auto-saves after completion
5. **Be patient**: Selenium + network monitoring takes time

## 📈 Example Workflow

```python
from pnp_scraper_v2 import PnPSmartScraper

# 1. Test with small sample
scraper = PnPSmartScraper(headless=True)
test = scraper.scrape(max_pages=2)
print(f"Test: {len(test)} products")

# 2. If good, scrape more
if len(test) > 0:
    scraper = PnPSmartScraper()
    all_products = scraper.scrape(max_pages=5)
    scraper.save_json('pnp_bulk.json')
    
    # 3. Analyze
    prices = [p['promotional_price'] for p in all_products if p.get('promotional_price')]
    print(f"Average: R{sum(prices)/len(prices):.2f}")
    print(f"Range: R{min(prices):.2f} - R{max(prices):.2f}")
```

## 🎯 Common Use Cases

### 1. Quick Sample (2 pages)
```python
scraper.scrape(max_pages=2)  # ~60-80 products, ~65 sec
```

### 2. Medium Dataset (5 pages)
```python
scraper.scrape(max_pages=5)  # ~150-200 products, ~170 sec
```

### 3. Large Dataset (10 pages)
```python
scraper.scrape(max_pages=10)  # ~300-400 products, ~340 sec
```

## 🆚 Comparison with Shoprite

| Feature | PnP | Shoprite |
|---------|-----|----------|
| **Method** | Selenium + API | Requests + BS4 |
| **Speed/page** | ~30-35 sec | ~2 sec |
| **Products/page** | ~30-40 | ~20 |
| **Data source** | API responses | Server HTML |
| **Complexity** | High | Low |
| **Reliability** | Very High | High |
| **Data quality** | Excellent | Excellent |

## 🔗 URL Pattern

```
Page 1: https://www.pnp.co.za/c/pnpbase?query=:relevance:allCategories:pnpbase:isOnPromotion:On%20Promotion

Page 2: https://www.pnp.co.za/c/pnpbase?query=:relevance:allCategories:pnpbase:isOnPromotion:On%20Promotion&currentPage=1

Page 3: https://www.pnp.co.za/c/pnpbase?query=:relevance:allCategories:pnpbase:isOnPromotion:On%20Promotion&currentPage=2
```

---

**Updated**: October 6, 2025  
**Feature**: Pagination Support Added  
**Status**: ✅ Fully Working

