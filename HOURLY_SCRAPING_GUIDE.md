# Hourly Smart Scraping API - Implementation Guide

## 🎯 **What Was Implemented**

### **⏰ Hourly Scraping Logic**
- ✅ **Once per hour**: Only scrapes each store/category once per hour
- ✅ **Smart caching**: Checks if already scraped this hour before scraping
- ✅ **Change detection**: Only stores data when actual changes are detected
- ✅ **Efficient storage**: Avoids unnecessary database writes

### **🔍 How It Works**

#### **1. Hour Check**
```python
# Before scraping, check if already scraped this hour
if not should_scrape_now(store, category):
    return {"cached": True, "message": "Already scraped this hour"}
```

#### **2. Change Detection**
```python
# Compare current products with previous scrape
current_hash = create_products_hash(products)
if current_hash == previous_hash:
    return {"no_changes": True, "message": "No changes detected"}
```

#### **3. Smart Storage**
```python
# Only store in database if changes detected
if changes_detected:
    store_products(products, store, category)
    update_scraping_cache(store, category, products, changes_count)
```

## 📊 **Database Schema**

### **New Table: `scraping_cache`**
```sql
CREATE TABLE scraping_cache (
    id SERIAL PRIMARY KEY,
    store VARCHAR(20) NOT NULL,
    category VARCHAR(100) NOT NULL,
    hour_key VARCHAR(20) NOT NULL,        -- YYYY-MM-DD-HH format
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    products_hash VARCHAR(64),            -- MD5 hash of products
    products_count INTEGER DEFAULT 0,
    changes_detected INTEGER DEFAULT 0,
    UNIQUE(store, category, hour_key)     -- Prevents duplicate hourly scrapes
);
```

## 🚀 **API Endpoints**

### **Enhanced Scrape Endpoint**
```bash
POST /api/scrape
{
    "store": "woolworths",
    "category": "fruit-vegetables",
    "max_pages": 3,
    "compare_with_existing": true
}
```

**Response Examples:**

#### **First Scrape (This Hour)**
```json
{
    "message": "Changes detected and stored in woolworths fruit-vegetables",
    "store": "woolworths",
    "category": "fruit-vegetables",
    "products_count": 24,
    "price_changes": 3,
    "changes": [...],
    "hour_key": "2025-10-06-03"
}
```

#### **Second Scrape (Same Hour)**
```json
{
    "message": "Already scraped woolworths fruit-vegetables this hour",
    "cached": true,
    "hour_key": "2025-10-06-03",
    "products_count": 0,
    "price_changes": 0
}
```

#### **No Changes Detected**
```json
{
    "message": "No changes detected in woolworths fruit-vegetables",
    "products_count": 24,
    "price_changes": 0,
    "no_changes": true
}
```

### **New Endpoints**

#### **Scrape Status**
```bash
GET /api/scrape-status?store=woolworths
```
Returns cache information and scraping history.

#### **Enhanced Stats**
```bash
GET /api/stats
```
Includes scraping statistics and cache information.

## 🎯 **Key Benefits**

### **1. Efficiency**
- ✅ **No duplicate scraping** - Once per hour per store/category
- ✅ **No unnecessary database writes** - Only when changes detected
- ✅ **Smart caching** - Avoids redundant operations

### **2. Resource Optimization**
- ✅ **Reduced server load** - Less scraping and processing
- ✅ **Lower database usage** - Only stores meaningful changes
- ✅ **Bandwidth savings** - Fewer HTTP requests to stores

### **3. Data Quality**
- ✅ **Change tracking** - Only stores actual changes
- ✅ **Price history** - Tracks price changes over time
- ✅ **Audit trail** - Complete scraping history

## 🧪 **Testing**

### **Local Testing**
```bash
# Start API
source .venv/bin/activate
python api.py

# Test hourly scraping
python test_hourly_api.py
```

### **Production Testing**
```bash
# First scrape (should work)
curl -X POST https://your-api.onrender.com/api/scrape \
  -H "Content-Type: application/json" \
  -d '{"store": "woolworths", "category": "fruit-vegetables", "max_pages": 1}'

# Second scrape (should be cached)
curl -X POST https://your-api.onrender.com/api/scrape \
  -H "Content-Type: application/json" \
  -d '{"store": "woolworths", "category": "fruit-vegetables", "max_pages": 1}'

# Check status
curl https://your-api.onrender.com/api/scrape-status
```

## 📈 **Monitoring**

### **Scrape Status**
- Monitor which stores/categories have been scraped
- Track hourly scraping activity
- View cache entries and timestamps

### **Statistics**
- Total products by store
- Recent price changes
- Scraping activity metrics
- Change detection rates

## 🎉 **Success Metrics**

Your API now provides:
- ✅ **Hourly scraping** - Once per hour per store/category
- ✅ **Change detection** - Only stores when changes found
- ✅ **Smart caching** - Avoids unnecessary operations
- ✅ **Price tracking** - Complete price history
- ✅ **Efficient storage** - Only meaningful data stored
- ✅ **Resource optimization** - Minimal server load

## 🚀 **Ready for Production**

The hourly scraping API is now ready for Render deployment with:
- ✅ **PostgreSQL database** with caching tables
- ✅ **Smart scraping logic** with hourly limits
- ✅ **Change detection** with hash comparison
- ✅ **Efficient storage** with change tracking
- ✅ **Complete monitoring** with status endpoints

**Your API will now scrape efficiently, only when needed, and track all changes!** 🎯
