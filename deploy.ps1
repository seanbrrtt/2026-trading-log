# Screenshot Upload Fix - Deployment Script
# Run this to deploy the fixed code to Railway

Write-Host "🚀 DEPLOYING SCREENSHOT UPLOAD FIX" -ForegroundColor Green
Write-Host "==================================" -ForegroundColor Green
Write-Host ""

# Change to project directory
Set-Location C:\Trading_Log_Deploy

Write-Host "📁 Current directory: $(Get-Location)" -ForegroundColor Cyan
Write-Host ""

# Show what will be committed
Write-Host "📝 Files to be committed:" -ForegroundColor Yellow
git status --short
Write-Host ""

# Add all changes
Write-Host "➕ Adding files to git..." -ForegroundColor Yellow
git add .
Write-Host "✅ Files added" -ForegroundColor Green
Write-Host ""

# Commit with descriptive message
Write-Host "💾 Committing changes..." -ForegroundColor Yellow
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
Write-Host "✅ Changes committed" -ForegroundColor Green
Write-Host ""

# Push to GitHub
Write-Host "🌐 Pushing to GitHub..." -ForegroundColor Yellow
git push origin main
Write-Host "✅ Pushed to GitHub" -ForegroundColor Green
Write-Host ""

Write-Host "⏳ Railway is now deploying..." -ForegroundColor Cyan
Write-Host "This will take approximately 90 seconds" -ForegroundColor Cyan
Write-Host ""
Write-Host "🌐 Your app will be live at:" -ForegroundColor Magenta
Write-Host "https://2026-trading-log-production.up.railway.app" -ForegroundColor White
Write-Host ""
Write-Host "✅ DEPLOYMENT COMPLETE!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Test these after deployment:" -ForegroundColor Yellow
Write-Host "  1. Click upload area → file dialog" -ForegroundColor White
Write-Host "  2. Drag/drop images → previews appear" -ForegroundColor White
Write-Host "  3. Click ❌ on preview → file removes" -ForegroundColor White
Write-Host "  4. Upload non-image → gets rejected" -ForegroundColor White
Write-Host "  5. Save trade → shows progress" -ForegroundColor White
Write-Host "  6. Check Gallery → trade appears" -ForegroundColor White
Write-Host ""
Write-Host "Done! 🎉" -ForegroundColor Green
