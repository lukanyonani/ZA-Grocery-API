#!/bin/bash
# Deploy Simple Shoprite API to Render

echo "🚀 DEPLOYING SIMPLE SHOPRITE API"
echo "================================="

# Backup current files
echo "📦 Backing up current files..."
mv api.py api_old.py 2>/dev/null || echo "No api.py to backup"
mv requirements.txt requirements_old.txt 2>/dev/null || echo "No requirements.txt to backup"
mv Procfile Procfile_old 2>/dev/null || echo "No Procfile to backup"

# Use new simple files
echo "🔄 Switching to simple API files..."
mv simple_api.py api.py
mv simple_requirements.txt requirements.txt
mv simple_Procfile Procfile

# Commit and push
echo "📝 Committing changes..."
git add .
git commit -m "Deploy simple Shoprite API - no database, JSON only"

echo "🚀 Pushing to Render..."
git push origin main

echo ""
echo "✅ DEPLOYMENT COMPLETE!"
echo "======================"
echo ""
echo "🌐 Your API will be available at:"
echo "   https://za-grocery-api-agno.onrender.com"
echo ""
echo "📋 Test these endpoints:"
echo "   curl 'https://za-grocery-api-agno.onrender.com/api/shoprite/food-cupboard'"
echo "   curl 'https://za-grocery-api-agno.onrender.com/api/shoprite/cheese'"
echo "   curl 'https://za-grocery-api-agno.onrender.com/api/shoprite/fresh-fruit'"
echo ""
echo "📖 Interactive docs:"
echo "   https://za-grocery-api-agno.onrender.com/docs"
echo ""
echo "🎯 All 14 Shoprite endpoints are ready!"
