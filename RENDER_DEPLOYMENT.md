# Render Deployment Guide

## ✅ All Fixes Applied

Your project is now **READY** for Render deployment.

## Changes Made

### 1. ✅ Created `runtime.txt`
- Specifies Python 3.9.18 for Render

### 2. ✅ Created `Procfile`
- Defines start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### 3. ✅ Updated `requirements.txt`
- Added `onnxruntime>=1.16.0` (CPU-only version)

### 4. ✅ Updated `app/main.py`
- Added CORS middleware for Flutter app
- Added startup event to preload CLIP model
- Prevents first-request timeout

### 5. ✅ Updated `app/api/cloth.py`
- Added ThreadPoolExecutor for async processing
- Added 10MB file size limit
- Moved CPU-intensive tasks to thread pool

### 6. ✅ Updated `app/services/inventory_generator.py`
- Changed to absolute paths for wardrobe.json
- Creates directory if it doesn't exist

## Render Deployment Steps

### 1. Push to Git
```bash
git add .
git commit -m "Prepare for Render deployment"
git push origin main
```

### 2. Create Render Service
1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **New** → **Web Service**
3. Connect your GitHub/GitLab repository
4. Select your repository

### 3. Configure Service
- **Name:** `ai-stylist-backend` (or your choice)
- **Environment:** `Python 3`
- **Build Command:** (leave empty - auto-detected)
- **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **Plan:** Free

### 4. Environment Variables
Add these in Render dashboard:
```
OMP_NUM_THREADS=1
```

### 5. Deploy
Click **Create Web Service** and wait for deployment.

## Important Notes

### Memory Constraints (Free Tier)
- Render Free Tier: **512MB RAM**
- CLIP model: ~150MB
- rembg: ~50MB
- PyTorch: ~200MB
- **Total: ~400MB** (within limit, but tight)

### First Deployment
- First build may take **15-20 minutes** (downloading dependencies)
- CLIP model downloads on first startup (~150MB)
- Subsequent deployments are faster

### Monitoring
- Watch memory usage in Render dashboard
- If you see OOM errors, consider:
  - Upgrading to paid tier
  - Optimizing model loading
  - Using smaller CLIP model variant

## Testing After Deployment

### 1. Health Check
```bash
curl https://your-app.onrender.com/
```

Expected:
```json
{"status": "ok", "message": "AI Stylist Backend is running"}
```

### 2. Test API Endpoint
```bash
curl -X POST "https://your-app.onrender.com/api/extract-cloth" \
  -F "file=@test_image.jpg"
```

### 3. Update Flutter App
Update your Flutter app's API base URL:
```dart
const String apiBaseUrl = 'https://your-app.onrender.com';
```

## Troubleshooting

### Build Fails
- Check build logs in Render dashboard
- Verify all dependencies in `requirements.txt`
- Ensure `runtime.txt` has correct Python version

### Service Crashes
- Check logs in Render dashboard
- Verify `Procfile` has correct command
- Check memory usage (may need upgrade)

### CORS Errors
- Verify CORS middleware in `app/main.py`
- Update `allow_origins` with your Flutter app domain

### Timeout on First Request
- CLIP model should preload at startup
- Check startup logs for "CLIP model loaded successfully"
- If missing, check startup event in `app/main.py`

## Production Recommendations

1. **CORS Origins:** Update `allow_origins` in `app/main.py` to your Flutter app domain
2. **File Size:** Adjust `MAX_FILE_SIZE` in `app/api/cloth.py` if needed
3. **Thread Pool:** Adjust `max_workers` in `app/api/cloth.py` based on performance
4. **Monitoring:** Set up Render alerts for memory/CPU usage
5. **Database:** Consider PostgreSQL for wardrobe.json (future enhancement)

## Status

✅ **READY FOR DEPLOYMENT**

All fixes have been applied. Your project is production-ready for Render.

