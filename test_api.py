#!/usr/bin/env python3
"""
Test script for the South African Grocery Scraper API
"""

import requests
import json
import time

# Test configuration
API_BASE = "http://localhost:8000"  # Change to your Render URL when deployed

def test_api():
    """Test all API endpoints"""
    print("🧪 Testing South African Grocery Scraper API")
    print("=" * 60)
    
    # Test 1: Root endpoint
    print("\n1. Testing root endpoint...")
    try:
        response = requests.get(f"{API_BASE}/")
        if response.status_code == 200:
            print("✅ Root endpoint working")
            print(f"   Response: {json.dumps(response.json(), indent=2)}")
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Root endpoint error: {e}")
    
    # Test 2: Categories endpoint
    print("\n2. Testing categories endpoint...")
    try:
        response = requests.get(f"{API_BASE}/api/categories")
        if response.status_code == 200:
            print("✅ Categories endpoint working")
            categories = response.json()
            for store, cats in categories.items():
                print(f"   {store}: {len(cats)} categories")
        else:
            print(f"❌ Categories endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Categories endpoint error: {e}")
    
    # Test 3: Scrape endpoint (small test)
    print("\n3. Testing scrape endpoint...")
    try:
        scrape_data = {
            "store": "woolworths",
            "category": "fruit-vegetables",
            "max_pages": 1,
            "compare_with_existing": True
        }
        response = requests.post(f"{API_BASE}/api/scrape", json=scrape_data)
        if response.status_code == 200:
            print("✅ Scrape endpoint working")
            result = response.json()
            print(f"   Scraped {result.get('products_count', 0)} products")
            print(f"   Price changes: {result.get('price_changes', 0)}")
        else:
            print(f"❌ Scrape endpoint failed: {response.status_code}")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Scrape endpoint error: {e}")
    
    # Test 4: Products endpoint
    print("\n4. Testing products endpoint...")
    try:
        response = requests.get(f"{API_BASE}/api/products?limit=5")
        if response.status_code == 200:
            print("✅ Products endpoint working")
            result = response.json()
            print(f"   Found {result.get('count', 0)} products")
        else:
            print(f"❌ Products endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Products endpoint error: {e}")
    
    # Test 5: Stats endpoint
    print("\n5. Testing stats endpoint...")
    try:
        response = requests.get(f"{API_BASE}/api/stats")
        if response.status_code == 200:
            print("✅ Stats endpoint working")
            stats = response.json()
            print(f"   Total products: {stats.get('total_products', 0)}")
            print(f"   Recent price changes: {stats.get('recent_price_changes_24h', 0)}")
        else:
            print(f"❌ Stats endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Stats endpoint error: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 API testing completed!")

if __name__ == "__main__":
    test_api()
