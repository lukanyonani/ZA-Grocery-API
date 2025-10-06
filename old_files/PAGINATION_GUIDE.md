# Shoprite Scraper - Pagination Guide

## 🎯 Quick Start

The Shoprite scraper now supports pagination! You can scrape multiple pages with a single command.

## 📊 Page Structure

- **Total products available**: 3,578
- **Products per page**: ~20
- **Total pages**: ~179
- **Page numbering**: 0-indexed (page 0, page 1, page 2, etc.)

## 🚀 Usage Examples

### Example 1: Single Page (Default)

```python
from shoprite_scraper import ShopriteScraper

scraper = ShopriteScraper()
products = scraper.scrape(max_pages=1)  # 20 products
scraper.save_json()
```

### Example 2: Multiple Pages

```python
scraper = ShopriteScraper()
products = scraper.scrape(max_pages=5)  # 100 products (5 × 20)
scraper.save_json()
```

### Example 3: With Product Limit

```python
scraper = ShopriteScraper()
# Stop after 50 products even if scraping more pages
products = scraper.scrape(max_pages=10, max_products=50)
scraper.save_json()
```

### Example 4: Scrape Specific Page

```python
scraper = ShopriteScraper()
# Scrape page 5 directly
url = "https://www.shoprite.co.za/c-2413/All-Departments/Food?q=%3Arelevance%3AbrowseAllStoresFacetOff%3AbrowseAllStoresFacetOff&page=4"
products = scraper.scrape(url=url)
scraper.save_json()
```

### Example 5: Scrape Many Products

```python
scraper = ShopriteScraper()
products = scraper.scrape(max_pages=20)  # ~400 products
scraper.save_json('shoprite_bulk.json')
```

### Example 6: All Products (Warning: ~179 pages!)

```python
scraper = ShopriteScraper()
# This will take a while! 3,578 products
products = scraper.scraper(max_pages=179)
scraper.save_json('shoprite_all.json')
```

## 🔧 Parameters

### `scrape()` method parameters:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `url` | str | None | Custom URL to scrape (overrides pagination) |
| `max_pages` | int | 1 | Number of pages to scrape |
| `max_products` | int | None | Stop after N products |

## ⏱️ Timing

The scraper includes a 2-second delay between pages to be respectful to the server:

- **1 page**: ~2 seconds
- **5 pages**: ~12 seconds (2s fetch + 2s delay × 4)
- **20 pages**: ~42 seconds
- **179 pages**: ~6 minutes

## 📝 Command Line Usage

### Quick Test (3 pages)

```bash
python3 shoprite_scraper.py
```

Default is set to 3 pages (~60 products).

### Custom Pages

Edit the `main()` function in `shoprite_scraper.py`:

```python
def main():
    scraper = ShopriteScraper()
    products = scraper.scrape(max_pages=10)  # Change this number
    scraper.save_json()
    scraper.save_csv()
    scraper.print_summary()
```

## 🎓 Advanced Usage

### Filter While Scraping

```python
from shoprite_scraper import ShopriteScraper

scraper = ShopriteScraper()
all_products = scraper.scrape(max_pages=10)

# Filter for products under R20
cheap = [p for p in all_products if p.get('price') and p['price'] < 20]

# Filter for specific category
bread = [p for p in all_products if 'bread' in p['name'].lower()]

# Sort by price
sorted_products = sorted(all_products, key=lambda x: x.get('price', 999))
```

### Scrape by Category

The URL pattern works for any category:

```python
scraper = ShopriteScraper()

# Scrape Bakery category
url = "https://www.shoprite.co.za/c-123/Bakery?q=:relevance&page=0"
products = scraper.scrape(url=url)
```

### Track Progress

The scraper prints progress automatically:

```
--- Page 1 of 5 ---
Fetching: https://...
✓ Page fetched successfully
✓ Extracted 20 products from page 1
  (Waiting 2 seconds before next page...)

--- Page 2 of 5 ---
...
```

## ⚠️ Important Notes

1. **Rate Limiting**: 2-second delay between pages (built-in)
2. **Respectful Scraping**: Don't scrape all 179 pages repeatedly
3. **Data Size**: 20 pages = ~400 products = ~600KB JSON
4. **Time**: Budget ~2 seconds per page + delays
5. **Errors**: Scraper stops if a page fails to load

## 📊 Output Files

Files are saved with total product count:

- `shoprite_products.json` - All scraped products
- `shoprite_products.csv` - CSV format

Example with 60 products (3 pages):

```json
[
  {
    "name": "Product Name",
    "price": 19.99,
    "on_special": true,
    ...
  },
  ... 59 more products
]
```

## 🔍 Finding Specific Products

### By Name

```python
scraper = ShopriteScraper()
products = scraper.scrape(max_pages=20)

# Search for "chicken"
chicken_products = [p for p in products if 'chicken' in p['name'].lower()]
print(f"Found {len(chicken_products)} chicken products")
```

### By Price Range

```python
# Find products between R10-R50
mid_range = [p for p in products 
             if p.get('price') and 10 <= p['price'] <= 50]
```

### On Special Only

```python
# Get all specials
specials = [p for p in products if p.get('on_special')]
```

## 💡 Tips

1. **Start small**: Test with 2-3 pages first
2. **Use limits**: Set `max_products` to avoid over-scraping
3. **Save often**: The scraper auto-saves after completion
4. **Check data**: Review JSON/CSV before scraping more
5. **Be patient**: Large scrapes take time

## 📈 Example Workflow

```python
from shoprite_scraper import ShopriteScraper

# 1. Test with small sample
scraper = ShopriteScraper()
test = scraper.scrape(max_pages=2)
print(f"Test: {len(test)} products")

# 2. If good, scrape more
if len(test) > 0:
    scraper = ShopriteScraper()
    all_products = scraper.scrape(max_pages=20)
    scraper.save_json('shoprite_bulk.json')
    
    # 3. Analyze
    prices = [p['price'] for p in all_products if p.get('price')]
    print(f"Average: R{sum(prices)/len(prices):.2f}")
    print(f"Range: R{min(prices):.2f} - R{max(prices):.2f}")
```

## 🎯 Common Use Cases

### 1. Price Monitoring (Daily)
```python
scraper.scrape(max_pages=5)  # Quick sample
```

### 2. Product Research (Weekly)
```python
scraper.scrape(max_pages=50)  # Comprehensive
```

### 3. Full Catalog (Monthly)
```python
scraper.scrape(max_pages=179)  # Everything
```

---

**Updated**: October 6, 2025  
**Feature**: Pagination Support Added

