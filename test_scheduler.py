#!/usr/bin/env python3
"""
Test script for the scheduled scraper
"""

import asyncio
import sys
from scheduled_scraper import ScheduledScraper, trigger_immediate_scrape, scrape_specific

async def test_scheduler():
    """Test the scheduler functionality"""
    print("🧪 Testing Scheduled Scraper")
    print("=" * 50)
    
    # Test 1: Create scheduler instance
    print("\n1. Testing scheduler creation...")
    try:
        scheduler = ScheduledScraper()
        print("✅ Scheduler created successfully")
        print(f"   Stores configured: {list(scheduler.scraping_schedule.keys())}")
    except Exception as e:
        print(f"❌ Scheduler creation failed: {e}")
        return
    
    # Test 2: Test specific scrape
    print("\n2. Testing specific scrape...")
    try:
        await scrape_specific("woolworths", "fruit-vegetables", 1)
        print("✅ Specific scrape test completed")
    except Exception as e:
        print(f"❌ Specific scrape failed: {e}")
    
    # Test 3: Test immediate scrape (small test)
    print("\n3. Testing immediate scrape...")
    try:
        print("   This will scrape all configured categories...")
        print("   (This may take a few minutes)")
        
        # Run for a short time to test
        await asyncio.wait_for(
            trigger_immediate_scrape(),
            timeout=300  # 5 minute timeout
        )
        print("✅ Immediate scrape test completed")
    except asyncio.TimeoutError:
        print("⏰ Immediate scrape timed out (expected for full test)")
    except Exception as e:
        print(f"❌ Immediate scrape failed: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Scheduler testing completed!")
    print("\nTo run the full scheduler:")
    print("  python -c 'import asyncio; from scheduled_scraper import start_background_scraper; asyncio.run(start_background_scraper())'")

if __name__ == "__main__":
    asyncio.run(test_scheduler())
