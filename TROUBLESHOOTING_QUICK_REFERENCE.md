# 🚨 Troubleshooting Quick Reference

## 🚀 Quick Start
```bash
# Start all services with validation
./start_services.sh

# Or start manually:
cd backend && python start_with_cors_fix.py &
cd frontend && npm run dev &
```

## 🔍 Common Issues & Solutions

### 1. **CORS Errors in Browser**
**Symptoms**: `Access to fetch at 'http://localhost:8000/...' from origin 'http://localhost:8080' has been blocked by CORS policy`

**Solution**: 
- Ensure backend is running with `start_with_cors_fix.py`
- Check that port 8080 is in CORS origins
- Restart backend service

**Quick Fix**:
```bash
cd backend
pkill -f "python.*consolidated_service.py"
python start_with_cors_fix.py &
```

### 2. **Backend Not Responding**
**Symptoms**: `Failed to fetch` or connection refused errors

**Check**:
```bash
# Test backend health
curl http://localhost:8000/health

# Check if port 8000 is listening
lsof -i :8000

# Check backend logs
ps aux | grep "python.*consolidated_service"
```

**Solution**: Restart backend service

### 3. **Frontend Not Loading**
**Symptoms**: Page not loading or Vite errors

**Check**:
```bash
# Test frontend accessibility
curl http://localhost:8080

# Check if port 8080 is listening
lsof -i :8080

# Check frontend logs
ps aux | grep "npm.*run dev"
```

**Solution**: Restart frontend service

### 4. **Port Already in Use**
**Symptoms**: `Address already in use` errors

**Solution**:
```bash
# Find processes using ports
lsof -i :8000  # Backend port
lsof -i :8080  # Frontend port

# Kill processes
pkill -f "python.*consolidated_service"
pkill -f "npm.*run dev"
```

### 5. **WebSocket Connection Issues**
**Symptoms**: WebSocket connection failures or timeouts

**Check**:
```bash
# Test WebSocket endpoint
curl -H "Upgrade: websocket" -H "Connection: Upgrade" http://localhost:8000/ws/stream
```

**Solution**: Ensure backend is running and WebSocket endpoint is accessible

## 🧪 Validation & Testing

### Run Full Validation
```bash
cd backend
python validate_connections.py
```

### Test Individual Components
```bash
# Backend health
curl http://localhost:8000/health

# CORS test
curl -H "Origin: http://localhost:8080" \
     -H "Access-Control-Request-Method: GET" \
     -X OPTIONS http://localhost:8000/health

# Frontend test
curl http://localhost:8080
```

### Browser Test Page
Open: `http://localhost:8080/test_backend_connection.html`

## 📊 Service Status Check

### Quick Status
```bash
# Check all services
echo "Backend:" && lsof -i :8000 | grep LISTEN
echo "Frontend:" && lsof -i :8080 | grep LISTEN
```

### Detailed Status
```bash
# Backend processes
ps aux | grep -E "(consolidated_service|start_with_cors_fix)" | grep -v grep

# Frontend processes
ps aux | grep -E "(npm|vite)" | grep -v grep
```

## 🔧 Configuration Issues

### CORS Configuration
**File**: `backend/.env`
**Key**: `CORS_ORIGINS`
**Required**: Must include `http://localhost:8080`

**Current Working Config**:
```
CORS_ORIGINS=http://localhost:3000,http://localhost:8080,http://localhost:5173,...
```

### Port Configuration
**Backend**: Port 8000 (configurable via `PORT` env var)
**Frontend**: Port 8080 (set in `vite.config.ts`)

## 🚨 Emergency Reset

### Complete Reset
```bash
# Stop all services
pkill -f "python.*consolidated_service"
pkill -f "npm.*run dev"
pkill -f "start_with_cors_fix"

# Clear ports
lsof -ti:8000 | xargs kill -9
lsof -ti:8080 | xargs kill -9

# Restart
./start_services.sh
```

### Backend Only Reset
```bash
cd backend
pkill -f "python.*consolidated_service"
python start_with_cors_fix.py &
```

### Frontend Only Reset
```bash
cd frontend
pkill -f "npm.*run dev"
npm run dev &
```

## 📞 When to Get Help

**Get help if**:
- Validation script shows < 80% success rate
- CORS errors persist after restart
- Services won't start on expected ports
- WebSocket connections consistently fail
- Database connectivity issues

**Include in help request**:
- Output from `validate_connections.py`
- Browser console errors
- Service logs
- Current port usage (`lsof -i :8000` and `lsof -i :8080`)

## ✅ Success Indicators

**System is healthy when**:
- Backend responds on port 8000
- Frontend loads on port 8080
- CORS preflight requests return 200 OK
- API endpoints respond correctly
- WebSocket connections establish
- Validation script shows > 80% success rate
