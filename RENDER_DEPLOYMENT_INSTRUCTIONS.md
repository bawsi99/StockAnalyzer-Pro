# Render Deployment Instructions

## Installing ML Dependencies

When deploying on Render, you'll need to manually install CatBoost with the `--no-deps` flag to avoid compilation issues. Here's how to do it:

### Option 1: Using Render's Start Command

You can modify your Start Command in the Render dashboard to install CatBoost before starting the application:

```
pip install catboost==1.2.5 --no-deps && cd backend && python run_production_services.py
```

### Option 2: Using Render's Build Command

Alternatively, you can add this to your Build Command in the Render dashboard:

```
pip install catboost==1.2.5 --no-deps && pip install -r requirements.txt
```

## Potential Issues and Solutions

### 1. Compilation Errors

If you see errors related to compilation or read-only filesystem:
- Make sure you're using the `--no-deps` flag with CatBoost
- Consider using CPU-only versions of PyTorch if needed

### 2. Memory Limits

If you encounter memory issues during installation:
- Upgrade to a higher tier Render plan
- Split the installation into smaller steps

### 3. Missing ML Functionality

If ML features are still not working after deployment:
- Check the logs for specific error messages
- Verify that both CatBoost and PyTorch are properly installed
- Consider installing only the specific ML components you need

## Verifying Installation

After deployment, you can verify that the ML dependencies are properly installed by checking the logs. You should no longer see these warnings:

```
CatBoost not available. Pattern ML will not work.
PyTorch not available. LSTM models will not work.
```

Instead, you should see successful initialization of the ML systems.
