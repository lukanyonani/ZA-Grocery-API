#!/usr/bin/env python3
"""
Scheduled scraper for automatic hourly updates
Runs in background and updates database with changes
"""

import asyncio
import time
from datetime import datetime, timedelta
import logging
from typing import Dict, List
import json

# Import your scrapers
from pnp_scraper import PnPScraper
from shoprite_scraper import ShopriteScraper  
from woolworths_scraper import WoolworthsScraper

# Import database functions from api.py
from api import get_db_connection, store_products

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ScheduledScraper:
    def __init__(self):
        self.is_running = False
        self.scraping_schedule = {
            # Store: (category, max_pages, frequency_hours)
            'woolworths': [
                ('fruit-vegetables', 3, 1),  # Every hour
                ('meat-poultry', 2, 2),     # Every 2 hours
                ('dairy-eggs', 2, 2),       # Every 2 hours
            ],
            'shoprite': [
                ('food', 2, 1),              # Every hour
                ('beverages', 2, 3),        # Every 3 hours
            ],
            'pnp': [
                ('snacks', 2, 1),           # Every hour
                ('beverages', 2, 2),        # Every 2 hours
            ]
        }
        
        # Track last scrape times
        self.last_scrape = {}
        
    async def scrape_store_category(self, store: str, category: str, max_pages: int):
        """Scrape a specific store and category"""
        try:
            logger.info(f"🔄 Starting scrape: {store} - {category}")
            
            # Initialize scraper
            if store == "pnp":
                scraper = PnPScraper(category=category)
            elif store == "shoprite":
                scraper = ShopriteScraper(category=category)
            elif store == "woolworths":
                scraper = WoolworthsScraper(category=category)
            else:
                logger.error(f"❌ Unknown store: {store}")
                return False
            
            # Scrape products
            products = scraper.scrape_category(max_pages=max_pages)
            
            if not products:
                logger.warning(f"⚠️ No products found for {store} - {category}")
                return False
            
            # Store in database and get changes
            changes = store_products(products, store, category, compare=True)
            
            logger.info(f"✅ Scraped {len(products)} products from {store} - {category}")
            if changes:
                logger.info(f"📊 Found {len(changes)} price changes")
                for change in changes[:3]:  # Show first 3 changes
                    logger.info(f"   💰 {change['product_name']}: R{change['old_price']} → R{change['new_price']} ({change['change_percent']:+.1f}%)")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Scraping failed for {store} - {category}: {e}")
            return False
    
    def should_scrape(self, store: str, category: str, frequency_hours: int) -> bool:
        """Check if it's time to scrape this category"""
        key = f"{store}_{category}"
        now = datetime.now()
        
        if key not in self.last_scrape:
            return True
        
        time_since_last = now - self.last_scrape[key]
        return time_since_last >= timedelta(hours=frequency_hours)
    
    async def run_scheduled_scrapes(self):
        """Run all scheduled scrapes"""
        logger.info("🕐 Starting scheduled scrape cycle")
        
        for store, categories in self.scraping_schedule.items():
            for category, max_pages, frequency_hours in categories:
                if self.should_scrape(store, category, frequency_hours):
                    await self.scrape_store_category(store, category, max_pages)
                    self.last_scrape[f"{store}_{category}"] = datetime.now()
                    
                    # Wait between scrapes to be respectful
                    await asyncio.sleep(30)
                else:
                    logger.info(f"⏰ Skipping {store} - {category} (not due yet)")
    
    async def start_scheduler(self):
        """Start the background scheduler"""
        logger.info("🚀 Starting scheduled scraper...")
        self.is_running = True
        
        while self.is_running:
            try:
                await self.run_scheduled_scrapes()
                
                # Wait 1 hour before next cycle
                logger.info("😴 Sleeping for 1 hour...")
                await asyncio.sleep(3600)  # 1 hour
                
            except Exception as e:
                logger.error(f"❌ Scheduler error: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes on error
    
    def stop_scheduler(self):
        """Stop the scheduler"""
        logger.info("🛑 Stopping scheduled scraper...")
        self.is_running = False

# Global scheduler instance
scheduler = ScheduledScraper()

async def start_background_scraper():
    """Start the background scraper (called from main API)"""
    await scheduler.start_scheduler()

def stop_background_scraper():
    """Stop the background scraper"""
    scheduler.stop_scheduler()

# Manual trigger functions for testing
async def trigger_immediate_scrape():
    """Trigger immediate scrape of all categories"""
    logger.info("🔥 Triggering immediate scrape...")
    await scheduler.run_scheduled_scrapes()

async def scrape_specific(store: str, category: str, max_pages: int = 2):
    """Scrape a specific store and category"""
    logger.info(f"🎯 Scraping {store} - {category}")
    await scheduler.scrape_store_category(store, category, max_pages)
