#!/usr/bin/env python3
"""
South African Grocery Scraper API
FastAPI wrapper for PnP, Shoprite, and Woolworths scrapers
Deploy to Render with PostgreSQL database
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import asyncio
import os
from datetime import datetime, timedelta
import psycopg2
from psycopg2.extras import RealDictCursor
import json
import time
import hashlib

# Import your scrapers
from pnp_scraper import PnPScraper
from shoprite_scraper import ShopriteScraper  
from woolworths_scraper import WoolworthsScraper

app = FastAPI(
    title="South African Grocery Scraper API",
    description="Scrape products from PnP, Shoprite, and Woolworths with PostgreSQL storage and hourly smart caching",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database connection
def get_db_connection():
    """Get PostgreSQL connection for Render"""
    try:
        # For Render, use the DATABASE_URL environment variable
        if os.getenv('DATABASE_URL'):
            return psycopg2.connect(os.getenv('DATABASE_URL'))
        else:
            # Local development
            return psycopg2.connect(
                host=os.getenv('DB_HOST', 'localhost'),
                database=os.getenv('DB_NAME', 'scraper_db'),
                user=os.getenv('DB_USER', 'postgres'),
                password=os.getenv('DB_PASSWORD', 'password'),
                port=os.getenv('DB_PORT', '5432')
            )
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

# Initialize database tables
def init_database():
    """Initialize database tables"""
    conn = get_db_connection()
    if not conn:
        return False
    
    cursor = conn.cursor()
    try:
        # Create products table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id SERIAL PRIMARY KEY,
                store VARCHAR(20) NOT NULL,
                category VARCHAR(100) NOT NULL,
                product_id VARCHAR(50),
                name VARCHAR(255) NOT NULL,
                price DECIMAL(10,2),
                image_url TEXT,
                scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_available BOOLEAN DEFAULT true,
                UNIQUE(store, product_id)
            )
        """)
        
        # Create price history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS price_history (
                id SERIAL PRIMARY KEY,
                product_id INTEGER REFERENCES products(id),
                old_price DECIMAL(10,2),
                new_price DECIMAL(10,2),
                changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create scraping cache table for hourly tracking
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scraping_cache (
                id SERIAL PRIMARY KEY,
                store VARCHAR(20) NOT NULL,
                category VARCHAR(100) NOT NULL,
                hour_key VARCHAR(20) NOT NULL,
                scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                products_hash VARCHAR(64),
                products_count INTEGER DEFAULT 0,
                changes_detected INTEGER DEFAULT 0,
                UNIQUE(store, category, hour_key)
            )
        """)
        
        conn.commit()
        return True
    except Exception as e:
        print(f"Database initialization error: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

# Pydantic models
class ScrapeRequest(BaseModel):
    store: str
    category: str
    max_pages: int = 1
    compare_with_existing: bool = True

class ProductResponse(BaseModel):
    id: int
    store: str
    category: str
    product_id: str
    name: str
    price: float
    image_url: str
    scraped_at: datetime
    is_available: bool

class PriceChange(BaseModel):
    product_name: str
    old_price: float
    new_price: float
    change_percent: float
    changed_at: datetime

# Hourly scraping logic
def get_current_hour_key():
    """Get current hour key for caching (YYYY-MM-DD-HH format)"""
    now = datetime.now()
    return now.strftime("%Y-%m-%d-%H")

def should_scrape_now(store: str, category: str) -> bool:
    """Check if we should scrape now (not scraped this hour yet)"""
    conn = get_db_connection()
    if not conn:
        return True  # If no DB, always scrape
    
    cursor = conn.cursor()
    try:
        hour_key = get_current_hour_key()
        cursor.execute("""
            SELECT id FROM scraping_cache 
            WHERE store = %s AND category = %s AND hour_key = %s
        """, (store, category, hour_key))
        
        result = cursor.fetchone()
        return result is None  # Scrape if not found
        
    except Exception as e:
        print(f"Error checking scrape cache: {e}")
        return True  # If error, scrape anyway
    finally:
        cursor.close()
        conn.close()

def create_products_hash(products: List[Dict]) -> str:
    """Create hash of products for change detection"""
    # Create a simple hash based on product names and prices
    product_data = []
    for product in products:
        product_data.append(f"{product.get('name', '')}:{product.get('price', 0)}")
    
    # Sort to ensure consistent hashing
    product_data.sort()
    combined = "|".join(product_data)
    return hashlib.md5(combined.encode()).hexdigest()

def get_previous_products_hash(store: str, category: str) -> str:
    """Get hash of products from previous scrape"""
    conn = get_db_connection()
    if not conn:
        return ""
    
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT products_hash FROM scraping_cache 
            WHERE store = %s AND category = %s 
            ORDER BY scraped_at DESC LIMIT 1
        """, (store, category))
        
        result = cursor.fetchone()
        return result[0] if result else ""
        
    except Exception as e:
        print(f"Error getting previous hash: {e}")
        return ""
    finally:
        cursor.close()
        conn.close()

def update_scraping_cache(store: str, category: str, products: List[Dict], changes_count: int):
    """Update scraping cache with current scrape info"""
    conn = get_db_connection()
    if not conn:
        return
    
    cursor = conn.cursor()
    try:
        hour_key = get_current_hour_key()
        products_hash = create_products_hash(products)
        
        cursor.execute("""
            INSERT INTO scraping_cache (store, category, hour_key, products_hash, products_count, changes_detected)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (store, category, hour_key) DO UPDATE SET
                products_hash = EXCLUDED.products_hash,
                products_count = EXCLUDED.products_count,
                changes_detected = EXCLUDED.changes_detected,
                scraped_at = CURRENT_TIMESTAMP
        """, (store, category, hour_key, products_hash, len(products), changes_count))
        
        conn.commit()
        
    except Exception as e:
        print(f"Error updating scrape cache: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

# Database functions
def store_products(products: List[Dict], store: str, category: str, compare: bool = True):
    """Store scraped products in PostgreSQL"""
    conn = get_db_connection()
    if not conn:
        print("❌ Database connection failed")
        return []
    
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    changes = []
    
    print(f"📊 Storing {len(products)} products for {store} {category}")
    print(f"🔍 First product sample: {products[0] if products else 'No products'}")
    
    try:
        for product in products:
            # Get product ID with fallback
            product_id = product.get('product_code', '') or f"fallback_{hash(product.get('name', ''))}"
            
            # Check if product exists
            cursor.execute("""
                SELECT id, price FROM products 
                WHERE store = %s AND product_id = %s
            """, (store, product_id))
            
            existing = cursor.fetchone()
            
            if existing:
                # Product exists - check for price changes
                # Convert both prices to float for comparison
                old_price_float = float(existing['price']) if existing['price'] is not None else 0.0
                new_price_float = float(product.get('price', 0)) if product.get('price') is not None else 0.0
                
                if compare and old_price_float != new_price_float:
                    # Price changed
                    old_price = old_price_float
                    new_price = new_price_float
                    change_percent = ((new_price - old_price) / old_price) * 100 if old_price > 0 else 0
                    
                    changes.append({
                        'product_name': product.get('name', ''),
                        'old_price': old_price,
                        'new_price': new_price,
                        'change_percent': change_percent,
                        'changed_at': datetime.now()
                    })
                    
                    # Update product
                    cursor.execute("""
                        UPDATE products 
                        SET name = %s, price = %s, image_url = %s, 
                            scraped_at = %s, is_available = %s
                        WHERE id = %s
                    """, (
                        product.get('name', ''),
                        product.get('price', 0),
                        product.get('image_url', ''),
                        datetime.now(),
                        True,
                        existing['id']
                    ))
                    
                    # Log price change
                    cursor.execute("""
                        INSERT INTO price_history (product_id, old_price, new_price, changed_at)
                        VALUES (%s, %s, %s, %s)
                    """, (existing['id'], old_price, new_price, datetime.now()))
                else:
                    # Just update timestamp
                    cursor.execute("""
                        UPDATE products SET scraped_at = %s, is_available = %s
                        WHERE id = %s
                    """, (datetime.now(), True, existing['id']))
            else:
                # New product - use a fallback ID if product_code is empty
                product_id = product.get('product_code', '') or f"fallback_{hash(product.get('name', ''))}"
                
                cursor.execute("""
                    INSERT INTO products (store, category, product_id, name, price, image_url, scraped_at, is_available)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (store, product_id) DO UPDATE SET
                        name = EXCLUDED.name,
                        price = EXCLUDED.price,
                        image_url = EXCLUDED.image_url,
                        scraped_at = EXCLUDED.scraped_at,
                        is_available = EXCLUDED.is_available
                """, (
                    store,
                    category,
                    product_id,
                    product.get('name', ''),
                    product.get('price', 0),
                    product.get('image_url', ''),
                    datetime.now(),
                    True
                ))
        
        conn.commit()
        print(f"✅ Successfully stored {len(products)} products with {len(changes)} changes")
        print(f"🔍 Database commit successful")
        return changes
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        conn.rollback()
        return []
    finally:
        cursor.close()
        conn.close()

# API Endpoints
@app.get("/", 
         summary="API Information",
         description="Get information about the South African Grocery Scraper API",
         tags=["Info"])
async def root():
    return {
        "message": "South African Grocery Scraper API - Hourly Smart Scraping",
        "version": "1.0.0",
        "stores": ["pnp", "shoprite", "woolworths"],
        "features": {
            "hourly_scraping": "Only scrapes once per hour per store/category",
            "change_detection": "Only stores data when changes are detected",
            "smart_caching": "Avoids unnecessary scraping and database writes",
            "price_tracking": "Tracks price changes over time"
        },
        "endpoints": {
            "scrape": "/api/scrape",
            "products": "/api/products",
            "price_changes": "/api/price-changes",
            "categories": "/api/categories",
            "stats": "/api/stats",
            "scrape_status": "/api/scrape-status"
        },
        "documentation": {
            "swagger_ui": "/docs",
            "redoc": "/redoc"
        }
    }

@app.post("/api/scrape",
          summary="Scrape Products",
          description="Scrape products from specified store and category with hourly smart caching. Only scrapes once per hour per store/category and only stores data when changes are detected.",
          response_description="Returns scraping results with product count, changes detected, and caching status",
          tags=["Scraping"])
async def scrape_products(request: ScrapeRequest, background_tasks: BackgroundTasks):
    """
    Scrape products from specified store and category with hourly smart caching.
    
    **Features:**
    - ⏰ **Hourly Caching**: Only scrapes once per hour per store/category
    - 🔍 **Change Detection**: Only stores data when changes are detected
    - 💾 **Smart Storage**: Avoids unnecessary database writes
    - 📊 **Price Tracking**: Tracks price changes over time
    
    **Stores Available:**
    - `pnp` - Pick n Pay
    - `shoprite` - Shoprite
    - `woolworths` - Woolworths
    
    **Response Types:**
    - **First scrape this hour**: Returns products and changes
    - **Already scraped this hour**: Returns cached response
    - **No changes detected**: Returns products but no changes
    - **Changes detected**: Returns products with changes stored
    """
    
    try:
        # Check if we should scrape now (hourly check)
        if not should_scrape_now(request.store, request.category):
            return {
                "message": f"Already scraped {request.store} {request.category} this hour",
                "store": request.store,
                "category": request.category,
                "cached": True,
                "hour_key": get_current_hour_key(),
                "products_count": 0,
                "price_changes": 0,
                "changes": []
            }
        
        # Get previous products hash for change detection
        previous_hash = get_previous_products_hash(request.store, request.category)
        
        # Initialize scraper based on store
        if request.store == "pnp":
            scraper = PnPScraper()  # PnP scraper doesn't use categories
        elif request.store == "shoprite":
            scraper = ShopriteScraper()  # Shoprite scraper doesn't use categories
        elif request.store == "woolworths":
            scraper = WoolworthsScraper(category=request.category)
        else:
            raise HTTPException(status_code=400, detail="Invalid store. Use: pnp, shoprite, woolworths")
        
        # Scrape products
        print(f"🔄 Scraping {request.store} {request.category}...")
        if request.store == "woolworths":
            products = scraper.scrape_category(max_pages=request.max_pages)
        else:
            # PnP and Shoprite use different method names
            products = scraper.scrape(max_pages=request.max_pages)
        
        if not products:
            # Update cache even if no products found
            update_scraping_cache(request.store, request.category, [], 0)
            return {
                "message": "No products found",
                "store": request.store,
                "category": request.category,
                "products_count": 0,
                "price_changes": 0,
                "changes": []
            }
        
        # Check if products have changed (using hash comparison)
        current_hash = create_products_hash(products)
        
        if previous_hash and current_hash == previous_hash:
            # No changes detected, just update cache and return
            update_scraping_cache(request.store, request.category, products, 0)
            return {
                "message": f"No changes detected in {request.store} {request.category}",
                "store": request.store,
                "category": request.category,
                "products_count": len(products),
                "price_changes": 0,
                "changes": [],
                "no_changes": True
            }
        
        # Changes detected, store in database
        print(f"📊 Changes detected, storing {len(products)} products...")
        changes = store_products(products, request.store, request.category, request.compare_with_existing)
        
        # Update cache with changes count
        update_scraping_cache(request.store, request.category, products, len(changes))
        
        return {
            "message": f"Changes detected and stored in {request.store} {request.category}",
            "store": request.store,
            "category": request.category,
            "products_count": len(products),
            "price_changes": len(changes),
            "changes": changes[:10] if changes else [],  # Show first 10 changes
            "hour_key": get_current_hour_key()
        }
        
    except Exception as e:
        print(f"❌ Scraping error: {e}")
        raise HTTPException(status_code=500, detail=f"Scraping failed: {str(e)}")

@app.get("/api/products",
         summary="Get Products",
         description="Retrieve products from the database with optional filtering by store and category",
         response_description="Returns list of products with pagination",
         tags=["Data"])
async def get_products(
    store: Optional[str] = Query(None, description="Filter by store (pnp, shoprite, woolworths)"),
    category: Optional[str] = Query(None, description="Filter by category"),
    limit: int = Query(100, description="Limit number of results (max 1000)")
):
    """
    Get products from the database with optional filtering.
    
    **Filters:**
    - `store`: Filter by store (pnp, shoprite, woolworths)
    - `category`: Filter by category name
    - `limit`: Maximum number of results (default: 100, max: 1000)
    
    **Returns:**
    - List of products with details
    - Total count of matching products
    """
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        query = "SELECT * FROM products WHERE 1=1"
        params = []
        
        if store:
            query += " AND store = %s"
            params.append(store)
        
        if category:
            query += " AND category = %s"
            params.append(category)
        
        query += " ORDER BY scraped_at DESC LIMIT %s"
        params.append(limit)
        
        cursor.execute(query, params)
        products = cursor.fetchall()
        
        return {
            "products": [dict(product) for product in products],
            "count": len(products)
        }
        
    finally:
        cursor.close()
        conn.close()

@app.get("/api/price-changes",
         summary="Get Price Changes",
         description="Retrieve recent price changes from the database",
         response_description="Returns list of price changes with details",
         tags=["Data"])
async def get_price_changes(
    limit: int = Query(50, description="Limit number of results (max 1000)")
):
    """
    Get recent price changes from the database.
    
    **Returns:**
    - List of price changes with product details
    - Old price, new price, and change percentage
    - Timestamp of when change was detected
    - Product name and details
    """
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        cursor.execute("""
            SELECT p.name, ph.old_price, ph.new_price, 
                   ((ph.new_price - ph.old_price) / ph.old_price * 100) as change_percent,
                   ph.changed_at
            FROM price_history ph
            JOIN products p ON ph.product_id = p.id
            ORDER BY ph.changed_at DESC
            LIMIT %s
        """, (limit,))
        
        changes = cursor.fetchall()
        return {
            "price_changes": [dict(change) for change in changes],
            "count": len(changes)
        }
        
    finally:
        cursor.close()
        conn.close()

@app.get("/api/categories",
         summary="Get Categories",
         description="Get available categories for each store",
         response_description="Returns categories organized by store",
         tags=["Info"])
async def get_categories():
    """
    Get available categories for each store.
    
    **Returns:**
    - Categories for PnP (Pick n Pay)
    - Categories for Shoprite
    - Categories for Woolworths
    
    **Usage:**
    Use these categories in the `/api/scrape` endpoint to specify which category to scrape.
    """
    return {
        "pnp": list(PnPScraper.list_categories().keys()),
        "shoprite": list(ShopriteScraper.list_categories().keys()),
        "woolworths": list(WoolworthsScraper.list_categories().keys())
    }

@app.get("/api/scrape-status",
         summary="Get Scrape Status",
         description="Get scraping status and cache information for monitoring hourly scraping activity",
         response_description="Returns scraping cache entries and current hour information",
         tags=["Monitoring"])
async def get_scrape_status(
    store: Optional[str] = Query(None, description="Filter by store (pnp, shoprite, woolworths)"),
    category: Optional[str] = Query(None, description="Filter by category")
):
    """
    Get scraping status and cache information.
    
    **Use Cases:**
    - Monitor which stores/categories have been scraped
    - Check hourly scraping activity
    - View cache entries and timestamps
    - Debug scraping issues
    
    **Returns:**
    - Current hour key (YYYY-MM-DD-HH format)
    - Cache entries with scraping details
    - Products count and changes detected
    - Timestamps of last scrapes
    """
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        query = "SELECT * FROM scraping_cache WHERE 1=1"
        params = []
        
        if store:
            query += " AND store = %s"
            params.append(store)
        
        if category:
            query += " AND category = %s"
            params.append(category)
        
        query += " ORDER BY scraped_at DESC LIMIT 20"
        
        cursor.execute(query, params)
        cache_entries = cursor.fetchall()
        
        return {
            "current_hour": get_current_hour_key(),
            "cache_entries": [dict(entry) for entry in cache_entries],
            "count": len(cache_entries)
        }
        
    finally:
        cursor.close()
        conn.close()

@app.get("/api/stats",
         summary="Get Statistics",
         description="Get comprehensive scraping statistics and metrics",
         response_description="Returns statistics about products, price changes, and scraping activity",
         tags=["Monitoring"])
async def get_stats():
    """
    Get comprehensive scraping statistics and metrics.
    
    **Returns:**
    - Total products by store
    - Recent price changes (last 24 hours)
    - Total products in database
    - Scraping activity statistics
    - Stores and categories scraped
    
    **Use Cases:**
    - Monitor API usage and performance
    - Track data growth over time
    - Analyze scraping effectiveness
    - Debug data quality issues
    """
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # Total products by store
        cursor.execute("""
            SELECT store, COUNT(*) as count 
            FROM products 
            GROUP BY store
        """)
        store_stats = cursor.fetchall()
        
        # Recent price changes
        cursor.execute("""
            SELECT COUNT(*) as recent_changes
            FROM price_history 
            WHERE changed_at > NOW() - INTERVAL '24 hours'
        """)
        recent_changes = cursor.fetchone()
        
        # Total products
        cursor.execute("SELECT COUNT(*) as total_products FROM products")
        total_products = cursor.fetchone()
        
        # Scraping cache stats
        cursor.execute("""
            SELECT COUNT(*) as total_scrapes,
                   COUNT(DISTINCT store) as stores_scraped,
                   COUNT(DISTINCT category) as categories_scraped
            FROM scraping_cache
        """)
        scrape_stats = cursor.fetchone()
        
        return {
            "products_by_store": [dict(stat) for stat in store_stats],
            "total_products": total_products['total_products'] if total_products else 0,
            "recent_price_changes_24h": recent_changes['recent_changes'] if recent_changes else 0,
            "scraping_stats": dict(scrape_stats) if scrape_stats else {}
        }
        
    finally:
        cursor.close()
        conn.close()

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    print("Initializing database...")
    if init_database():
        print("✅ Database initialized successfully")
    else:
        print("❌ Database initialization failed")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))

# Add these imports at the top
import asyncio
from scheduled_scraper import start_background_scraper, trigger_immediate_scrape, scrape_specific

# Add these endpoints before the startup event
@app.post("/api/trigger-scrape")
async def trigger_scrape():
    """Manually trigger immediate scrape of all categories"""
    try:
        await trigger_immediate_scrape()
        return {"message": "Scrape triggered successfully", "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scrape trigger failed: {str(e)}")

@app.post("/api/scrape-specific")
async def scrape_specific_endpoint(
    store: str,
    category: str,
    max_pages: int = 2
):
    """Scrape a specific store and category"""
    try:
        await scrape_specific(store, category, max_pages)
        return {
            "message": f"Scraped {store} - {category}",
            "store": store,
            "category": category,
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scrape failed: {str(e)}")

@app.get("/api/scheduler-status")
async def get_scheduler_status():
    """Get scheduler status and next scrape times"""
    from scheduled_scraper import scheduler
    
    status = {
        "is_running": scheduler.is_running,
        "last_scrape_times": scheduler.last_scrape,
        "schedule": scheduler.scraping_schedule
    }
    
    return status

@app.delete("/api/clear-cache")
async def clear_scraping_cache(
    store: Optional[str] = Query(None, description="Clear cache for specific store"),
    category: Optional[str] = Query(None, description="Clear cache for specific category")
):
    """Clear scraping cache for debugging purposes"""
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    cursor = conn.cursor()
    try:
        if store and category:
            # Clear specific store/category
            cursor.execute("""
                DELETE FROM scraping_cache 
                WHERE store = %s AND category = %s
            """, (store, category))
            message = f"Cleared cache for {store} - {category}"
        elif store:
            # Clear all categories for store
            cursor.execute("DELETE FROM scraping_cache WHERE store = %s", (store,))
            message = f"Cleared cache for {store}"
        else:
            # Clear all cache
            cursor.execute("DELETE FROM scraping_cache")
            message = "Cleared all scraping cache"
        
        conn.commit()
        return {"message": message, "status": "success"}
        
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to clear cache: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@app.post("/api/force-scrape")
async def force_scrape(
    store: str,
    category: str,
    max_pages: int = 1,
    clear_cache: bool = True
):
    """Force a fresh scrape bypassing the hourly cache"""
    try:
        # Clear cache if requested
        if clear_cache:
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute("""
                    DELETE FROM scraping_cache 
                    WHERE store = %s AND category = %s
                """, (store, category))
                conn.commit()
                cursor.close()
                conn.close()
        
        # Initialize scraper based on store
        if store == "pnp":
            scraper = PnPScraper()  # PnP scraper doesn't use categories
        elif store == "shoprite":
            scraper = ShopriteScraper()  # Shoprite scraper doesn't use categories
        elif store == "woolworths":
            scraper = WoolworthsScraper(category=category)
        else:
            raise HTTPException(status_code=400, detail="Invalid store. Use: pnp, shoprite, woolworths")
        
        # Scrape products
        print(f"🔄 Force scraping {store} {category}...")
        if store == "woolworths":
            products = scraper.scrape_category(max_pages=max_pages)
        else:
            # PnP and Shoprite use different method names
            products = scraper.scrape(max_pages=max_pages)
        
        if not products:
            return {
                "message": "No products found",
                "store": store,
                "category": category,
                "products_count": 0,
                "price_changes": 0,
                "changes": []
            }
        
        # Store products in database
        print(f"📊 Storing {len(products)} products...")
        changes = store_products(products, store, category, True)
        
        # Update cache
        update_scraping_cache(store, category, products, len(changes))
        
        return {
            "message": f"Force scrape completed for {store} {category}",
            "store": store,
            "category": category,
            "products_count": len(products),
            "price_changes": len(changes),
            "changes": changes[:10] if changes else []
        }
        
    except Exception as e:
        print(f"❌ Force scraping error: {e}")
        raise HTTPException(status_code=500, detail=f"Force scraping failed: {str(e)}")

# Update the startup event
@app.on_event("startup")
async def startup_event():
    """Initialize database and start background scraper"""
    print("Initializing database...")
    if init_database():
        print("✅ Database initialized successfully")
    else:
        print("❌ Database initialization failed")
    
    print("Starting background scraper...")
    # Start background scraper in a separate task
    asyncio.create_task(start_background_scraper())
    print("✅ Background scraper started")

