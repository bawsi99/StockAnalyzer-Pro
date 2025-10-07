# Production Deployment Path Fix

This document describes the fix implemented for the production deployment path issue that was causing the error:

```
Error getting instruments: [Errno 2] No such file or directory: '/opt/render/project/src/backend/zerodha/../data/zerodha_instruments.csv'
```

## Root Cause

The issue was caused by hardcoded relative path resolution in the ZerodhaClient that worked locally but failed in production environments like Render. The code was using:

```python
csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'zerodha_instruments.csv')
```

This approach doesn't work reliably across different deployment environments.

## Solution Implemented

### 1. Created Centralized Path Utility (`backend/core/path_utils.py`)

- **PathResolver class**: Uses multiple strategies to find the correct backend directory
- **Production-aware**: Handles various deployment scenarios (Render, Docker, Heroku, local)
- **Fallback mechanisms**: Graceful degradation when paths are not writable
- **Singleton pattern**: Ensures consistent path resolution across the application

### 2. Updated ZerodhaClient (`backend/zerodha/client.py`)

- **Replaced manual path construction** with centralized utility functions
- **Added robust error handling** for read-only filesystems
- **Implemented safe write paths** with fallback to temporary directories
- **Enhanced logging** for better debugging in production

### 3. Path Resolution Strategies

The PathResolver tries multiple strategies in order:

1. **Local development**: `backend/core/../` → `backend/`
2. **Render deployment**: `/opt/render/project/src/backend`
3. **Docker/Heroku**: `/app/backend`
4. **Environment variables**: `BACKEND_ROOT`, `PROJECT_ROOT`
5. **Working directory based**: `cwd/backend`
6. **Fallback**: Current directory's parent

## Key Features

### Production-Safe File Operations

- **Write permission checks** before attempting file operations
- **Automatic fallback** to temporary directories for read-only filesystems
- **Graceful error handling** that doesn't break the main functionality
- **Environment variable fallbacks** for configuration persistence

### Robust Path Detection

```python
from core.path_utils import get_config_path, get_zerodha_instruments_csv_path

# These will work in both local and production environments
config_path = get_config_path()  # Gets backend/config/.env
csv_path = get_zerodha_instruments_csv_path()  # Gets backend/data/zerodha_instruments.csv
```

## Deployment Considerations

### Environment Variables

You can override path detection by setting:

- `BACKEND_ROOT`: Direct path to backend directory
- `PROJECT_ROOT`: Path to project root (will look for backend subdirectory)

### File Permissions

The system now handles:

- **Read-only filesystems**: Falls back to temporary storage
- **Permission errors**: Continues operation without file caching
- **Missing directories**: Creates directories when possible

### Logging

Enhanced logging helps debug path resolution issues:

```
PathResolver initialized with backend root: /opt/render/project/src/backend
Using backend directory: /opt/render/project/src/backend
CSV path: /opt/render/project/src/backend/data/zerodha_instruments.csv
```

## Testing the Fix

To test the fix in your deployment:

1. **Check path resolution**:
   ```python
   from core.path_utils import get_backend_root, get_config_path
   print(f"Backend root: {get_backend_root()}")
   print(f"Config path: {get_config_path()}")
   ```

2. **Verify file operations**:
   ```python
   from zerodha.client import ZerodhaDataClient
   client = ZerodhaDataClient()
   # This should now work without path errors
   ```

3. **Check logs** for path resolution messages

## Future-Proofing

This fix makes the application more portable across different deployment environments:

- **Cloud platforms**: Render, Heroku, AWS, GCP
- **Container environments**: Docker, Kubernetes
- **Development environments**: Local, CI/CD pipelines

The centralized path utility can be extended to handle additional deployment scenarios as needed.