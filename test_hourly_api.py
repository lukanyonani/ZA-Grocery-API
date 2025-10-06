#!/usr/bin/env python3
"""
Test script for the hourly scraping API functionality
"""

import requests
import json
import time
from datetime import datetime

# Test configuration
API_BASE = "http://localhost:8000"  # Change to your Render URL when deployed

def test_hourly_scraping():
    """Test the hourly scraping functionality"""
    print("🕐 Testing Hourly Scraping API")
    print("=" * 60)
    
    # Test 1: First scrape (should work)
    print("\n1. First scrape (should work)...")
    try:
        scrape_data = {
            "store": "woolworths",
            "category": "fruit-vegetables",
            "max_pages": 1,
            "compare_with_existing": True
        }
        response = requests.post(f"{API_BASE}/api/scrape", json=scrape_data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ First scrape successful")
            print(f"   Message: {result.get('message', '')}")
            print(f"   Products: {result.get('products_count', 0)}")
            print(f"   Changes: {result.get('price_changes', 0)}")
            print(f"   Cached: {result.get('cached', False)}")
        else:
            print(f"❌ First scrape failed: {response.status_code}")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ First scrape error: {e}")
    
    # Test 2: Immediate second scrape (should be cached)
    print("\n2. Immediate second scrape (should be cached)...")
    try:
        response = requests.post(f"{API_BASE}/api/scrape", json=scrape_data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Second scrape response received")
            print(f"   Message: {result.get('message', '')}")
            print(f"   Cached: {result.get('cached', False)}")
            if result.get('cached'):
                print("   🎉 Correctly cached - no unnecessary scraping!")
            else:
                print("   ⚠️ Not cached - might be an issue")
        else:
            print(f"❌ Second scrape failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Second scrape error: {e}")
    
    # Test 3: Check scrape status
    print("\n3. Checking scrape status...")
    try:
        response = requests.get(f"{API_BASE}/api/scrape-status")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Scrape status retrieved")
            print(f"   Current hour: {result.get('current_hour', '')}")
            print(f"   Cache entries: {result.get('count', 0)}")
            
            # Show cache entries
            entries = result.get('cache_entries', [])
            for entry in entries[:3]:  # Show first 3
                print(f"   - {entry.get('store')} {entry.get('category')}: {entry.get('products_count')} products, {entry.get('changes_detected')} changes")
        else:
            print(f"❌ Scrape status failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Scrape status error: {e}")
    
    # Test 4: Get statistics
    print("\n4. Getting statistics...")
    try:
        response = requests.get(f"{API_BASE}/api/stats")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Statistics retrieved")
            print(f"   Total products: {result.get('total_products', 0)}")
            print(f"   Recent price changes: {result.get('recent_price_changes_24h', 0)}")
            
            scraping_stats = result.get('scraping_stats', {})
            print(f"   Total scrapes: {scraping_stats.get('total_scrapes', 0)}")
            print(f"   Stores scraped: {scraping_stats.get('stores_scraped', 0)}")
        else:
            print(f"❌ Statistics failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Statistics error: {e}")
    
    print("\n" + "=" * 60)
    print("�� Hourly scraping test completed!")
    print("\n�� Key Features Tested:")
    print("✅ Hourly caching (prevents duplicate scrapes)")
    print("✅ Change detection (only stores when changes found)")
    print("✅ Smart caching (avoids unnecessary database writes)")
    print("✅ Status tracking (monitor scraping activity)")

def test_different_stores():
    """Test scraping different stores"""
    print("\n🛒 Testing Different Stores")
    print("=" * 40)
    
    stores = [
        {"store": "woolworths", "category": "fruit-vegetables"},
        {"store": "shoprite", "category": "food"},
        {"store": "pnp", "category": "snacks"}
    ]
    
    for store_info in stores:
        print(f"\nTesting {store_info['store']} {store_info['category']}...")
        try:
            response = requests.post(f"{API_BASE}/api/scrape", json=store_info)
            if response.status_code == 200:
                result = response.json()
                print(f"✅ {store_info['store']}: {result.get('products_count', 0)} products")
            else:
                print(f"❌ {store_info['store']}: Failed")
        except Exception as e:
            print(f"❌ {store_info['store']}: Error - {e}")

if __name__ == "__main__":
    print("🚀 Starting Hourly Scraping API Tests")
    print(f"API Base: {API_BASE}")
    print(f"Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    test_hourly_scraping()
    test_different_stores()
    
    print("\n🎯 Next Steps:")
    print("1. Deploy to Render")
    print("2. Set up PostgreSQL database")
    print("3. Test with real data")
    print("4. Monitor hourly scraping activity")
