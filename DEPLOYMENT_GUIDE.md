# South African Grocery Scraper API - Deployment Guide

## 🚀 Deploy to Render

### Step 1: Prepare Your Repository
1. Push all files to GitHub
2. Ensure you have these files in your repo:
   - `api.py` (main FastAPI application)
   - `requirements_api.txt` (dependencies)
   - `pnp_scraper.py` (PnP scraper)
   - `shoprite_scraper.py` (Shoprite scraper)
   - `woolworths_scraper.py` (Woolworths scraper)
   - `render.yaml` (Render configuration)

### Step 2: Create Render Account
1. Go to [render.com](https://render.com)
2. Sign up with GitHub
3. Connect your repository

### Step 3: Create PostgreSQL Database
1. In Render dashboard, click "New +"
2. Select "PostgreSQL"
3. Name: `sa-grocery-db`
4. Plan: Free
5. Click "Create Database"
6. Copy the connection string

### Step 4: Deploy Web Service
1. In Render dashboard, click "New +"
2. Select "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name**: `sa-grocery-api`
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements_api.txt`
   - **Start Command**: `python api.py`
   - **Plan**: Free

### Step 5: Set Environment Variables
In your web service settings, add:
- `DATABASE_URL`: (from your PostgreSQL service)
- `PORT`: 8000

### Step 6: Deploy
1. Click "Create Web Service"
2. Wait for deployment (5-10 minutes)
3. Your API will be available at: `https://sa-grocery-api.onrender.com`

## 🔗 API Endpoints

### Base URL
```
https://your-app-name.onrender.com
```

### Available Endpoints

#### 1. Root
```
GET /
```
Returns API information and available endpoints.

#### 2. Scrape Products
```
POST /api/scrape
```
**Body:**
```json
{
    "store": "woolworths",
    "category": "fruit-vegetables",
    "max_pages": 3,
    "compare_with_existing": true
}
```

#### 3. Get Products
```
GET /api/products?store=woolworths&category=fruit-vegetables&limit=100
```

#### 4. Get Price Changes
```
GET /api/price-changes?limit=50
```

#### 5. Get Categories
```
GET /api/categories
```

#### 6. Get Statistics
```
GET /api/stats
```

## 🧪 Testing Your API

### Local Testing
```bash
# Install dependencies
pip install -r requirements_api.txt

# Run locally
python api.py

# Test endpoints
python test_api.py
```

### Production Testing
```bash
# Test your deployed API
curl https://your-app-name.onrender.com/

# Scrape some products
curl -X POST https://your-app-name.onrender.com/api/scrape \
  -H "Content-Type: application/json" \
  -d '{"store": "woolworths", "category": "fruit-vegetables", "max_pages": 1}'
```

## 📊 Database Access

### Via API
- All data accessible via API endpoints
- No direct database access needed

### Direct Database Access (Optional)
- Use pgAdmin or similar PostgreSQL client
- Connection string provided by Render
- Access from Render dashboard

## 🔧 Configuration

### Environment Variables
- `DATABASE_URL`: PostgreSQL connection string (auto-provided by Render)
- `PORT`: Port number (default: 8000)

### Supported Stores
- **pnp**: Pick n Pay
- **shoprite**: Shoprite
- **woolworths**: Woolworths

### Supported Categories
Each store has different categories. Use `/api/categories` to see available options.

## 🚨 Important Notes

1. **Free Tier Limits**:
   - 750 hours/month for web service
   - 1GB PostgreSQL storage
   - Service sleeps after 15 minutes of inactivity

2. **Database**:
   - Tables created automatically on first run
   - Data persists between deployments
   - Price history tracked automatically

3. **Scraping**:
   - Respects website rate limits
   - Built-in delays between requests
   - Handles errors gracefully

## 🎯 Usage Examples

### Scrape Woolworths Fruit & Vegetables
```bash
curl -X POST https://your-app-name.onrender.com/api/scrape \
  -H "Content-Type: application/json" \
  -d '{
    "store": "woolworths",
    "category": "fruit-vegetables",
    "max_pages": 5,
    "compare_with_existing": true
  }'
```

### Get All Products
```bash
curl https://your-app-name.onrender.com/api/products
```

### Get Price Changes
```bash
curl https://your-app-name.onrender.com/api/price-changes
```

### Get Statistics
```bash
curl https://your-app-name.onrender.com/api/stats
```

## 🎉 Success!

Your South African Grocery Scraper API is now live and ready to use!
