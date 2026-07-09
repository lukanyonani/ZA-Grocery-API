# ZA Grocery API

A FastAPI service that scrapes and serves live South African grocery prices from **Shoprite**, **Pick n Pay**, and **Woolworths** — no manual data entry, just JSON responses pulled straight from each retailer's site.

## Features

- Category-level product endpoints for Shoprite (bakery, dairy, meat, produce, frozen, sweets, ready meals, and more)
- Pick n Pay all-products and promotions endpoints
- Woolworths scraper for category and product data
- Optional scheduled background scraping to keep data fresh
- Interactive API docs via FastAPI's built-in Swagger UI (`/docs`) and ReDoc (`/redoc`)

## Tech stack

- **FastAPI** + **Uvicorn** for the API layer
- **BeautifulSoup4** / **Selenium** for scraping
- **PostgreSQL** (via `render.yaml`) for optional persistent storage

## Getting started

```bash
pip install -r requirements.txt
python api.py
```

The API starts with interactive docs at `http://localhost:8000/docs`.

## Example endpoints

| Store | Endpoint |
|---|---|
| Shoprite | `GET /api/shoprite/all-products` |
| Shoprite | `GET /api/shoprite/fresh-fruit` |
| Shoprite | `GET /api/shoprite/bakery` |
| Pick n Pay | `GET /api/picknpay/all-products` |
| Pick n Pay | `GET /api/picknpay/promotions` |

Most list endpoints accept `page` (0-indexed) and `max_products` query parameters.

## Deployment

Configured for [Render](https://render.com) via `render.yaml` (web service + PostgreSQL). See `DEPLOYMENT_GUIDE.md` for step-by-step deployment notes.

## Project layout

```
api.py                  # Main FastAPI app and route definitions
pnp_scraper.py           # Pick n Pay scraper
shoprite_scraper.py      # Shoprite scraper
woolworths_scraper.py    # Woolworths scraper
scheduled_scraper.py     # Background job for periodic re-scraping
old_files/                # Earlier scraper iterations and exploratory scripts, kept for reference
```
