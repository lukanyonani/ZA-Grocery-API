# 🗄️ NEW DATABASE-FIRST LOGIC

## 📋 OVERVIEW

The API has been updated with a **database-first approach** for all endpoints. This means:

1. **Check database first** - if data exists, return it immediately
2. **If no data** - scrape fresh data, return JSON immediately
3. **Save to database in background** - store scraped data asynchronously

## 🔄 HOW IT WORKS

### **Step-by-Step Process**

When you call any endpoint (e.g., `https://za-grocery-api-agno.onrender.com/api/shoprite/food-cupboard`):

#### **Step 1: Check Database**
```python
# Check if products already exist in database
db_products = check_database_for_products("shoprite", "Food Cupboard", limit=100)
```

#### **Step 2A: Data Found in Database**
- ✅ **Return immediately** from database
- ⚡ **Super fast** response (no scraping needed)
- 📊 Response includes `"source": "database"`

```json
{
  "message": "Retrieved 20 Food Cupboard products from database",
  "page": 0,
  "products_count": 20,
  "category": "Food Cupboard",
  "source": "database",
  "products": [...]
}
```

#### **Step 2B: No Data in Database**
- 🔄 **Scrape fresh data** from Shoprite website
- ✅ **Return immediately** with scraped data
- 💾 **Save to database in background** (asynchronous)
- 📊 Response includes `"source": "scraper"`

```json
{
  "message": "Successfully scraped 20 Food Cupboard products from page 0",
  "page": 0,
  "products_count": 20,
  "category": "Food Cupboard",
  "source": "scraper",
  "products": [...]
}
```

## ✅ BENEFITS

### **1. Faster Responses**
- First call: Scrapes and returns data
- Subsequent calls: Returns cached data instantly

### **2. Reduced Load**
- Only scrapes when necessary
- Database serves cached data efficiently

### **3. Better User Experience**
- Immediate response (no waiting for database write)
- Background tasks handle storage

### **4. Scalability**
- Database caching reduces website scraping load
- Background tasks don't block responses

## 🔧 NEW FUNCTIONS ADDED

### **1. `check_database_for_products()`**
```python
def check_database_for_products(store: str, category: str, limit: int = 100):
    """Check if products exist in database"""
    # Query database for existing products
    # Return products if found, None otherwise
```

### **2. `store_products_in_background()`**
```python
def store_products_in_background(products: List[Dict], store: str, category: str):
    """Store products in database (for background tasks)"""
    # Save products to database
    # Update scraping cache
    # Run asynchronously
```

## 📊 UPDATED ENDPOINTS

### **Updated Endpoints:**
1. ✅ `/api/shoprite/all-products` - Database-first logic implemented
2. ✅ `/api/shoprite/food-cupboard` - Database-first logic implemented

### **To Be Updated:**
- `/api/shoprite/fresh-meat-poultry`
- `/api/shoprite/frozen-meat-poultry`
- `/api/shoprite/milk-butter-eggs`
- `/api/shoprite/cheese`
- `/api/shoprite/yoghurt`
- `/api/shoprite/fresh-fruit`
- `/api/shoprite/fresh-vegetables`
- `/api/shoprite/fresh-salad-herbs-dip`
- `/api/shoprite/bakery`
- `/api/shoprite/frozen-food`
- `/api/shoprite/chocolates-sweets`
- `/api/shoprite/ready-meals`
- All Woolworths endpoints

## 🎯 USAGE EXAMPLES

### **Example 1: First Call (No Data in Database)**
```bash
GET https://za-grocery-api-agno.onrender.com/api/shoprite/food-cupboard

Response:
{
  "message": "Successfully scraped 20 Food Cupboard products",
  "source": "scraper",  ← Data was scraped
  "products_count": 20,
  "products": [...]
}
```

### **Example 2: Second Call (Data in Database)**
```bash
GET https://za-grocery-api-agno.onrender.com/api/shoprite/food-cupboard

Response:
{
  "message": "Retrieved 20 Food Cupboard products from database",
  "source": "database",  ← Data from database
  "products_count": 20,
  "products": [...]
}
```

## 🔍 RESPONSE SOURCE FIELD

Every response now includes a `"source"` field:

- **`"source": "database"`** - Data retrieved from PostgreSQL database
- **`"source": "scraper"`** - Data freshly scraped from website

## 💡 BEST PRACTICES

1. **Check the `source` field** to know where data came from
2. **First call may be slower** (scraping required)
3. **Subsequent calls will be faster** (database cached)
4. **Use the `/api/products` endpoint** to retrieve all stored data
5. **Use the `/api/clear-cache` endpoint** to force re-scraping

## 🚀 NEXT STEPS

To complete the implementation:

1. Update all remaining Shoprite category endpoints
2. Update all Woolworths endpoints
3. Add same logic to PnP endpoints
4. Test all endpoints thoroughly
5. Deploy to Render

## 📝 TECHNICAL DETAILS

### **Database Schema**
```sql
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name TEXT,
    price NUMERIC,
    store TEXT,
    category TEXT,
    url TEXT,
    image_url TEXT,
    product_code TEXT,
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### **Query Used**
```sql
SELECT * FROM products 
WHERE store = %s AND category = %s 
ORDER BY scraped_at DESC 
LIMIT %s
```

This ensures you always get the most recent products from the database.

## ✅ CONCLUSION

The new database-first logic provides:
- ⚡ Faster responses
- 💾 Efficient caching
- 🔄 Smart scraping
- 🚀 Better scalability
- 😊 Improved user experience

All while maintaining the same API interface!

