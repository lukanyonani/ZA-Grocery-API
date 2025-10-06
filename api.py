#!/usr/bin/env python3
"""
Simple Shoprite API - No Database, JSON Only
FastAPI wrapper for Shoprite scraper with direct JSON responses
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import asyncio
import os
from shoprite_scraper import ShopriteScraper
from pnp_scraper import PnPScraper

app = FastAPI(
    title="Simple Grocery API",
    description="Simple API for Shoprite and Pick n Pay products - JSON responses only, no database",
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

@app.get("/", 
         summary="API Information",
         description="Get information about the Simple Grocery API",
         tags=["Info"])
async def root():
    return {
        "message": "Simple Grocery API - JSON responses only",
        "version": "1.0.0",
        "stores": {
            "shoprite": {
                "all_products": "/api/shoprite/all-products",
                "food_cupboard": "/api/shoprite/food-cupboard",
                "fresh_meat_poultry": "/api/shoprite/fresh-meat-poultry",
                "frozen_meat_poultry": "/api/shoprite/frozen-meat-poultry",
                "milk_butter_eggs": "/api/shoprite/milk-butter-eggs",
                "cheese": "/api/shoprite/cheese",
                "yoghurt": "/api/shoprite/yoghurt",
                "fresh_fruit": "/api/shoprite/fresh-fruit",
                "fresh_vegetables": "/api/shoprite/fresh-vegetables",
                "fresh_salad_herbs_dip": "/api/shoprite/fresh-salad-herbs-dip",
                "bakery": "/api/shoprite/bakery",
                "frozen_food": "/api/shoprite/frozen-food",
                "chocolates_sweets": "/api/shoprite/chocolates-sweets",
                "ready_meals": "/api/shoprite/ready-meals"
            },
            "picknpay": {
                "all_products": "/api/picknpay/all-products",
                "promotions": "/api/picknpay/promotions"
            }
        },
        "parameters": {
            "page": "Page number (0-indexed, default: 0)",
            "max_products": "Maximum number of products (optional)"
        }
    }

# All Shoprite Endpoints
@app.get("/api/shoprite/all-products",
         summary="Get All Shoprite Products",
         description="Get all products from Shoprite with pagination support",
         tags=["Shoprite"])
async def get_shoprite_all_products(
    page: int = Query(0, description="Page number (0-indexed, default: 0)", ge=0),
    max_products: Optional[int] = Query(None, description="Maximum number of products to return (optional)")
):
    """Get all products from Shoprite"""
    try:
        scraper = ShopriteScraper()
        
        if page == 0:
            url = "https://www.shoprite.co.za/c-2413/All-Departments/Food"
        else:
            url = f"https://www.shoprite.co.za/c-2413/All-Departments/Food?q=%3Arelevance%3AbrowseAllStoresFacetOff%3AbrowseAllStoresFacetOff&page={page}"
        
        products = scraper.scrape(url=url, max_pages=1, max_products=max_products)
        
        return {
            "message": f"Successfully scraped {len(products)} products from page {page}",
            "page": page,
            "products_count": len(products),
            "category": "All Products",
            "products": products,
            "url": url
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scraping failed: {str(e)}")

@app.get("/api/shoprite/food-cupboard",
         summary="Get Shoprite Food Cupboard Products",
         description="Get products from Shoprite Food Cupboard category",
         tags=["Shoprite"])
async def get_shoprite_food_cupboard(
    page: int = Query(0, description="Page number (0-indexed, default: 0)", ge=0),
    max_products: Optional[int] = Query(None, description="Maximum number of products to return (optional)")
):
    """Get products from Shoprite Food Cupboard category"""
    try:
        scraper = ShopriteScraper()
        
        if page == 0:
            url = "https://www.shoprite.co.za/c-2413/All-Departments/Food?q=%3Arelevance%3AallCategories%3Afood_cupboard%3AbrowseAllStoresFacetOff%3AbrowseAllStoresFacetOff&page=0"
        else:
            url = f"https://www.shoprite.co.za/c-2413/All-Departments/Food?q=%3Arelevance%3AallCategories%3Afood_cupboard%3AbrowseAllStoresFacetOff%3AbrowseAllStoresFacetOff&page={page}"
        
        products = scraper.scrape(url=url, max_pages=1, max_products=max_products)
        
        return {
            "message": f"Successfully scraped {len(products)} Food Cupboard products from page {page}",
            "page": page,
            "products_count": len(products),
            "category": "Food Cupboard",
            "products": products,
            "url": url
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Food Cupboard scraping failed: {str(e)}")

@app.get("/api/shoprite/fresh-meat-poultry",
         summary="Get Shoprite Fresh Meat & Poultry Products",
         description="Get products from Shoprite Fresh Meat & Poultry category",
         tags=["Shoprite"])
async def get_shoprite_fresh_meat_poultry(
    page: int = Query(0, description="Page number (0-indexed, default: 0)", ge=0),
    max_products: Optional[int] = Query(None, description="Maximum number of products to return (optional)")
):
    """Get products from Shoprite Fresh Meat & Poultry category"""
    try:
        scraper = ShopriteScraper()
        
        if page == 0:
            url = "https://www.shoprite.co.za/c-2413/All-Departments/Food?q=%3Arelevance%3AallCategories%3Afresh_meat_and_poultry%3AbrowseAllStoresFacetOff%3AbrowseAllStoresFacetOff&page=0"
        else:
            url = f"https://www.shoprite.co.za/c-2413/All-Departments/Food?q=%3Arelevance%3AallCategories%3Afresh_meat_and_poultry%3AbrowseAllStoresFacetOff%3AbrowseAllStoresFacetOff&page={page}"
        
        products = scraper.scrape(url=url, max_pages=1, max_products=max_products)
        
        return {
            "message": f"Successfully scraped {len(products)} Fresh Meat & Poultry products from page {page}",
            "page": page,
            "products_count": len(products),
            "category": "Fresh Meat & Poultry",
            "products": products,
            "url": url
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fresh Meat & Poultry scraping failed: {str(e)}")

@app.get("/api/shoprite/frozen-meat-poultry",
         summary="Get Shoprite Frozen Meat & Poultry Products",
         description="Get products from Shoprite Frozen Meat & Poultry category",
         tags=["Shoprite"])
async def get_shoprite_frozen_meat_poultry(
    page: int = Query(0, description="Page number (0-indexed, default: 0)", ge=0),
    max_products: Optional[int] = Query(None, description="Maximum number of products to return (optional)")
):
    """Get products from Shoprite Frozen Meat & Poultry category"""
    try:
        scraper = ShopriteScraper()
        
        if page == 0:
            url = "https://www.shoprite.co.za/c-2413/All-Departments/Food?q=%3Arelevance%3AallCategories%3Afrozen_meat_and_poultry%3AbrowseAllStoresFacetOff%3AbrowseAllStoresFacetOff&page=0"
        else:
            url = f"https://www.shoprite.co.za/c-2413/All-Departments/Food?q=%3Arelevance%3AallCategories%3Afrozen_meat_and_poultry%3AbrowseAllStoresFacetOff%3AbrowseAllStoresFacetOff&page={page}"
        
        products = scraper.scrape(url=url, max_pages=1, max_products=max_products)
        
        return {
            "message": f"Successfully scraped {len(products)} Frozen Meat & Poultry products from page {page}",
            "page": page,
            "products_count": len(products),
            "category": "Frozen Meat & Poultry",
            "products": products,
            "url": url
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Frozen Meat & Poultry scraping failed: {str(e)}")

@app.get("/api/shoprite/milk-butter-eggs",
         summary="Get Shoprite Milk, Butter & Eggs Products",
         description="Get products from Shoprite Milk, Butter & Eggs category",
         tags=["Shoprite"])
async def get_shoprite_milk_butter_eggs(
    page: int = Query(0, description="Page number (0-indexed, default: 0)", ge=0),
    max_products: Optional[int] = Query(None, description="Maximum number of products to return (optional)")
):
    """Get products from Shoprite Milk, Butter & Eggs category"""
    try:
        scraper = ShopriteScraper()
        
        if page == 0:
            url = "https://www.shoprite.co.za/c-2413/All-Departments/Food?q=%3Arelevance%3AallCategories%3Amilk_butter_and_eggs%3AbrowseAllStoresFacetOff%3AbrowseAllStoresFacetOff&page=0"
        else:
            url = f"https://www.shoprite.co.za/c-2413/All-Departments/Food?q=%3Arelevance%3AallCategories%3Amilk_butter_and_eggs%3AbrowseAllStoresFacetOff%3AbrowseAllStoresFacetOff&page={page}"
        
        products = scraper.scrape(url=url, max_pages=1, max_products=max_products)
        
        return {
            "message": f"Successfully scraped {len(products)} Milk, Butter & Eggs products from page {page}",
            "page": page,
            "products_count": len(products),
            "category": "Milk, Butter & Eggs",
            "products": products,
            "url": url
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Milk, Butter & Eggs scraping failed: {str(e)}")

@app.get("/api/shoprite/cheese",
         summary="Get Shoprite Cheese Products",
         description="Get products from Shoprite Cheese category",
         tags=["Shoprite"])
async def get_shoprite_cheese(
    page: int = Query(0, description="Page number (0-indexed, default: 0)", ge=0),
    max_products: Optional[int] = Query(None, description="Maximum number of products to return (optional)")
):
    """Get products from Shoprite Cheese category"""
    try:
        scraper = ShopriteScraper()
        
        if page == 0:
            url = "https://www.shoprite.co.za/c-2413/All-Departments/Food?q=%3Arelevance%3AallCategories%3Acheese%3AbrowseAllStoresFacetOff%3AbrowseAllStoresFacetOff&page=0"
        else:
            url = f"https://www.shoprite.co.za/c-2413/All-Departments/Food?q=%3Arelevance%3AallCategories%3Acheese%3AbrowseAllStoresFacetOff%3AbrowseAllStoresFacetOff&page={page}"
        
        products = scraper.scrape(url=url, max_pages=1, max_products=max_products)
        
        return {
            "message": f"Successfully scraped {len(products)} Cheese products from page {page}",
            "page": page,
            "products_count": len(products),
            "category": "Cheese",
            "products": products,
            "url": url
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cheese scraping failed: {str(e)}")

@app.get("/api/shoprite/yoghurt",
         summary="Get Shoprite Yoghurt Products",
         description="Get products from Shoprite Yoghurt category",
         tags=["Shoprite"])
async def get_shoprite_yoghurt(
    page: int = Query(0, description="Page number (0-indexed, default: 0)", ge=0),
    max_products: Optional[int] = Query(None, description="Maximum number of products to return (optional)")
):
    """Get products from Shoprite Yoghurt category"""
    try:
        scraper = ShopriteScraper()
        
        if page == 0:
            url = "https://www.shoprite.co.za/c-2413/All-Departments/Food?q=%3Arelevance%3AallCategories%3Ayoghurt%3AbrowseAllStoresFacetOff%3AbrowseAllStoresFacetOff&page=0"
        else:
            url = f"https://www.shoprite.co.za/c-2413/All-Departments/Food?q=%3Arelevance%3AallCategories%3Ayoghurt%3AbrowseAllStoresFacetOff%3AbrowseAllStoresFacetOff&page={page}"
        
        products = scraper.scrape(url=url, max_pages=1, max_products=max_products)
        
        return {
            "message": f"Successfully scraped {len(products)} Yoghurt products from page {page}",
            "page": page,
            "products_count": len(products),
            "category": "Yoghurt",
            "products": products,
            "url": url
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Yoghurt scraping failed: {str(e)}")

@app.get("/api/shoprite/fresh-fruit",
         summary="Get Shoprite Fresh Fruit Products",
         description="Get products from Shoprite Fresh Fruit category",
         tags=["Shoprite"])
async def get_shoprite_fresh_fruit(
    page: int = Query(0, description="Page number (0-indexed, default: 0)", ge=0),
    max_products: Optional[int] = Query(None, description="Maximum number of products to return (optional)")
):
    """Get products from Shoprite Fresh Fruit category"""
    try:
        scraper = ShopriteScraper()
        
        if page == 0:
            url = "https://www.shoprite.co.za/c-2413/All-Departments/Food?q=%3Arelevance%3AallCategories%3Afresh_fruit%3AbrowseAllStoresFacetOff%3AbrowseAllStoresFacetOff&page=0"
        else:
            url = f"https://www.shoprite.co.za/c-2413/All-Departments/Food?q=%3Arelevance%3AallCategories%3Afresh_fruit%3AbrowseAllStoresFacetOff%3AbrowseAllStoresFacetOff&page={page}"
        
        products = scraper.scrape(url=url, max_pages=1, max_products=max_products)
        
        return {
            "message": f"Successfully scraped {len(products)} Fresh Fruit products from page {page}",
            "page": page,
            "products_count": len(products),
            "category": "Fresh Fruit",
            "products": products,
            "url": url
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fresh Fruit scraping failed: {str(e)}")

@app.get("/api/shoprite/fresh-vegetables",
         summary="Get Shoprite Fresh Vegetables Products",
         description="Get products from Shoprite Fresh Vegetables category",
         tags=["Shoprite"])
async def get_shoprite_fresh_vegetables(
    page: int = Query(0, description="Page number (0-indexed, default: 0)", ge=0),
    max_products: Optional[int] = Query(None, description="Maximum number of products to return (optional)")
):
    """Get products from Shoprite Fresh Vegetables category"""
    try:
        scraper = ShopriteScraper()
        
        if page == 0:
            url = "https://www.shoprite.co.za/c-2413/All-Departments/Food?q=%3Arelevance%3AallCategories%3Afresh_vegetables%3AbrowseAllStoresFacetOff%3AbrowseAllStoresFacetOff&page=0"
        else:
            url = f"https://www.shoprite.co.za/c-2413/All-Departments/Food?q=%3Arelevance%3AallCategories%3Afresh_vegetables%3AbrowseAllStoresFacetOff%3AbrowseAllStoresFacetOff&page={page}"
        
        products = scraper.scrape(url=url, max_pages=1, max_products=max_products)
        
        return {
            "message": f"Successfully scraped {len(products)} Fresh Vegetables products from page {page}",
            "page": page,
            "products_count": len(products),
            "category": "Fresh Vegetables",
            "products": products,
            "url": url
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fresh Vegetables scraping failed: {str(e)}")

@app.get("/api/shoprite/fresh-salad-herbs-dip",
         summary="Get Shoprite Fresh Salad, Herbs & Dip Products",
         description="Get products from Shoprite Fresh Salad, Herbs & Dip category",
         tags=["Shoprite"])
async def get_shoprite_fresh_salad_herbs_dip(
    page: int = Query(0, description="Page number (0-indexed, default: 0)", ge=0),
    max_products: Optional[int] = Query(None, description="Maximum number of products to return (optional)")
):
    """Get products from Shoprite Fresh Salad, Herbs & Dip category"""
    try:
        scraper = ShopriteScraper()
        
        if page == 0:
            url = "https://www.shoprite.co.za/c-2413/All-Departments/Food?q=%3Arelevance%3AallCategories%3Afresh_salad_herbs_and_dip%3AbrowseAllStoresFacetOff%3AbrowseAllStoresFacetOff&page=0"
        else:
            url = f"https://www.shoprite.co.za/c-2413/All-Departments/Food?q=%3Arelevance%3AallCategories%3Afresh_salad_herbs_and_dip%3AbrowseAllStoresFacetOff%3AbrowseAllStoresFacetOff&page={page}"
        
        products = scraper.scrape(url=url, max_pages=1, max_products=max_products)
        
        return {
            "message": f"Successfully scraped {len(products)} Fresh Salad, Herbs & Dip products from page {page}",
            "page": page,
            "products_count": len(products),
            "category": "Fresh Salad, Herbs & Dip",
            "products": products,
            "url": url
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fresh Salad, Herbs & Dip scraping failed: {str(e)}")

@app.get("/api/shoprite/bakery",
         summary="Get Shoprite Bakery Products",
         description="Get products from Shoprite Bakery category",
         tags=["Shoprite"])
async def get_shoprite_bakery(
    page: int = Query(0, description="Page number (0-indexed, default: 0)", ge=0),
    max_products: Optional[int] = Query(None, description="Maximum number of products to return (optional)")
):
    """Get products from Shoprite Bakery category"""
    try:
        scraper = ShopriteScraper()
        
        if page == 0:
            url = "https://www.shoprite.co.za/c-2413/All-Departments/Food?q=%3Arelevance%3AallCategories%3Abakery%3AbrowseAllStoresFacetOff%3AbrowseAllStoresFacetOff&page=0"
        else:
            url = f"https://www.shoprite.co.za/c-2413/All-Departments/Food?q=%3Arelevance%3AallCategories%3Abakery%3AbrowseAllStoresFacetOff%3AbrowseAllStoresFacetOff&page={page}"
        
        products = scraper.scrape(url=url, max_pages=1, max_products=max_products)
        
        return {
            "message": f"Successfully scraped {len(products)} Bakery products from page {page}",
            "page": page,
            "products_count": len(products),
            "category": "Bakery",
            "products": products,
            "url": url
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bakery scraping failed: {str(e)}")

@app.get("/api/shoprite/frozen-food",
         summary="Get Shoprite Frozen Food Products",
         description="Get products from Shoprite Frozen Food category",
         tags=["Shoprite"])
async def get_shoprite_frozen_food(
    page: int = Query(0, description="Page number (0-indexed, default: 0)", ge=0),
    max_products: Optional[int] = Query(None, description="Maximum number of products to return (optional)")
):
    """Get products from Shoprite Frozen Food category"""
    try:
        scraper = ShopriteScraper()
        
        if page == 0:
            url = "https://www.shoprite.co.za/c-2413/All-Departments/Food?q=%3Arelevance%3AallCategories%3Afrozen_food%3AbrowseAllStoresFacetOff%3AbrowseAllStoresFacetOff&page=0"
        else:
            url = f"https://www.shoprite.co.za/c-2413/All-Departments/Food?q=%3Arelevance%3AallCategories%3Afrozen_food%3AbrowseAllStoresFacetOff%3AbrowseAllStoresFacetOff&page={page}"
        
        products = scraper.scrape(url=url, max_pages=1, max_products=max_products)
        
        return {
            "message": f"Successfully scraped {len(products)} Frozen Food products from page {page}",
            "page": page,
            "products_count": len(products),
            "category": "Frozen Food",
            "products": products,
            "url": url
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Frozen Food scraping failed: {str(e)}")

@app.get("/api/shoprite/chocolates-sweets",
         summary="Get Shoprite Chocolates & Sweets Products",
         description="Get products from Shoprite Chocolates & Sweets category",
         tags=["Shoprite"])
async def get_shoprite_chocolates_sweets(
    page: int = Query(0, description="Page number (0-indexed, default: 0)", ge=0),
    max_products: Optional[int] = Query(None, description="Maximum number of products to return (optional)")
):
    """Get products from Shoprite Chocolates & Sweets category"""
    try:
        scraper = ShopriteScraper()
        
        if page == 0:
            url = "https://www.shoprite.co.za/c-2413/All-Departments/Food?q=%3Arelevance%3AallCategories%3Achocolates_and_sweets%3AbrowseAllStoresFacetOff%3AbrowseAllStoresFacetOff&page=0"
        else:
            url = f"https://www.shoprite.co.za/c-2413/All-Departments/Food?q=%3Arelevance%3AallCategories%3Achocolates_and_sweets%3AbrowseAllStoresFacetOff%3AbrowseAllStoresFacetOff&page={page}"
        
        products = scraper.scrape(url=url, max_pages=1, max_products=max_products)
        
        return {
            "message": f"Successfully scraped {len(products)} Chocolates & Sweets products from page {page}",
            "page": page,
            "products_count": len(products),
            "category": "Chocolates & Sweets",
            "products": products,
            "url": url
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chocolates & Sweets scraping failed: {str(e)}")

@app.get("/api/shoprite/ready-meals",
         summary="Get Shoprite Ready Meals Products",
         description="Get products from Shoprite Ready Meals category",
         tags=["Shoprite"])
async def get_shoprite_ready_meals(
    page: int = Query(0, description="Page number (0-indexed, default: 0)", ge=0),
    max_products: Optional[int] = Query(None, description="Maximum number of products to return (optional)")
):
    """Get products from Shoprite Ready Meals category"""
    try:
        scraper = ShopriteScraper()
        
        if page == 0:
            url = "https://www.shoprite.co.za/c-2413/All-Departments/Food?q=%3Arelevance%3AallCategories%3Aready_meals%3AbrowseAllStoresFacetOff%3AbrowseAllStoresFacetOff&page=0"
        else:
            url = f"https://www.shoprite.co.za/c-2413/All-Departments/Food?q=%3Arelevance%3AallCategories%3Aready_meals%3AbrowseAllStoresFacetOff%3AbrowseAllStoresFacetOff&page={page}"
        
        products = scraper.scrape(url=url, max_pages=1, max_products=max_products)
        
        return {
            "message": f"Successfully scraped {len(products)} Ready Meals products from page {page}",
            "page": page,
            "products_count": len(products),
            "category": "Ready Meals",
            "products": products,
            "url": url
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ready Meals scraping failed: {str(e)}")

# Pick n Pay Endpoints
@app.get("/api/picknpay/all-products",
         summary="Get All Pick n Pay Products",
         description="Get all products from Pick n Pay with pagination support",
         tags=["Pick n Pay"])
async def get_picknpay_all_products(
    page: int = Query(0, description="Page number (0-indexed, default: 0)", ge=0),
    max_products: Optional[int] = Query(None, description="Maximum number of products to return (optional)")
):
    """Get all products from Pick n Pay"""
    try:
        scraper = PnPScraper()
        
        # Use the scraper with the correct URL
        url = "https://www.pnp.co.za/c/pnpbase?query=:relevance:allCategories:pnpbase"
        products = scraper.scrape(max_pages=1, url=url)
        
        # Limit products if max_products is specified
        if max_products and len(products) > max_products:
            products = products[:max_products]
        
        return {
            "message": f"Successfully scraped {len(products)} Pick n Pay products from page {page}",
            "page": page,
            "products_count": len(products),
            "category": "All Products",
            "products": products,
            "url": "https://www.pnp.co.za/c/pnpbase?query=:relevance:allCategories:pnpbase"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pick n Pay scraping failed: {str(e)}")

@app.get("/api/picknpay/promotions",
         summary="Get Pick n Pay Promotions",
         description="Get promotional products from Pick n Pay",
         tags=["Pick n Pay"])
async def get_picknpay_promotions(
    page: int = Query(0, description="Page number (0-indexed, default: 0)", ge=0),
    max_products: Optional[int] = Query(None, description="Maximum number of products to return (optional)")
):
    """Get promotional products from Pick n Pay"""
    try:
        scraper = PnPScraper()
        
        # Use the promotions scraper (this is what it's designed for)
        products = scraper.scrape(max_pages=1)
        
        # Limit products if max_products is specified
        if max_products and len(products) > max_products:
            products = products[:max_products]
        
        return {
            "message": f"Successfully scraped {len(products)} Pick n Pay promotional products from page {page}",
            "page": page,
            "products_count": len(products),
            "category": "Promotions",
            "products": products,
            "url": "https://www.pnp.co.za/c/pnpbase?query=:relevance:allCategories:pnpbase:isOnPromotion:On%20Promotion"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pick n Pay promotions scraping failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
