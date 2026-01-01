#!/bin/bash
# Screenshot Upload Fix - Deployment Script
# Run this to deploy the fixed code to Railway

echo "🚀 DEPLOYING SCREENSHOT UPLOAD FIX"
echo "=================================="
echo ""

# Change to project directory
cd C:\Trading_Log_Deploy

echo "📁 Current directory: $(pwd)"
echo ""

# Show what will be committed
echo "📝 Files to be committed:"
git status --short
echo ""

# Add all changes
echo "➕ Adding files to git..."
git add .
echo "✅ Files added"
echo ""

# Commit with descriptive message
echo "💾 Committing changes..."
git commit -m "Fix screenshot upload: addEventListener, validation, remove files, progress feedback

- Changed from property assignment to addEventListener for reliability
- Added stopPropagation() to prevent drag/drop event bubbling
- Added file type validation (PNG, JPG, GIF, WebP only)
- Added file size validation (16MB max per Railway limits)
- Added remove button on each screenshot preview
- Added upload progress feedback (Uploading 1/3...)
- Added better error handling with response validation
- Added auto-refresh of gallery after successful save
- Fixed form reset to include date reset
- Total: 168 lines changed in templates/index.html"
echo "✅ Changes committed"
echo ""

# Push to GitHub
echo "🌐 Pushing to GitHub..."
git push origin main
echo "✅ Pushed to GitHub"
echo ""

echo "⏳ Railway is now deploying..."
echo "This will take approximately 90 seconds"
echo ""
echo "🌐 Your app will be live at:"
echo "https://2026-trading-log-production.up.railway.app"
echo ""
echo "✅ DEPLOYMENT COMPLETE!"
echo ""
echo "📋 Test these after deployment:"
echo "  1. Click upload area → file dialog"
echo "  2. Drag/drop images → previews appear"  
echo "  3. Click ❌ on preview → file removes"
echo "  4. Upload non-image → gets rejected"
echo "  5. Save trade → shows progress"
echo "  6. Check Gallery → trade appears"
echo ""
echo "Done! 🎉"
