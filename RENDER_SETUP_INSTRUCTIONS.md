# Render Setup Instructions

## 1. Create a New Web Service

1. Go to your Render dashboard
2. Click "New +" and select "Web Service"
3. Connect your GitHub repository
4. Configure with the following settings:

## 2. Configuration Settings

### Basic Settings
- **Name**: stockanalyzer-pro (or your preferred name)
- **Region**: Choose the region closest to your users
- **Instance Type**: Start with Standard (512 MB)

### Build & Deploy Settings
- **Runtime**: Python 3
- **Build Command**: `./render_build.sh`
- **Start Command**: `cd backend && python run_production_services.py`

### Environment Variables
- `PYTHON_VERSION`: `3.10.0`
- Add any other environment variables your app needs (API keys, etc.)

## 3. Advanced Settings

### Health Check Path
- `/health`

### Auto-Deploy
- Enable auto-deploy for automatic deployment on git push

## 4. Troubleshooting

If you still encounter issues:

1. Check the build logs for specific error messages
2. Try increasing the instance size if you're running out of memory
3. Consider using a Docker-based deployment instead
4. Contact Render support if the issue persists

## 5. Monitoring

After deployment:
1. Monitor the logs to ensure ML dependencies are loaded correctly
2. Check the `/health` endpoint to verify the service is running
3. Test the ML functionality to confirm it's working properly
