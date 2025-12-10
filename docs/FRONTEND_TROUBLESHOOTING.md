# Frontend Troubleshooting Guide

## Issue: Frontend Fails to Load

### Quick Checks

1. **Verify Processes Are Running**
   ```bash
   ps aux | grep -E "(vite|node)" | grep -v grep
   sudo ss -tlnp | grep -E ':(5000|8000)'
   ```

2. **Check HTTP Response**
   ```bash
   curl -I http://localhost:5000
   curl http://localhost:5000 | head -20
   ```

3. **Check Browser Console**
   - Open browser DevTools (F12)
   - Check Console tab for JavaScript errors
   - Check Network tab for failed requests

### Common Issues and Fixes

#### Issue 1: Vite `allowedHosts` Restriction

**Symptoms:**
- Frontend serves HTML but React doesn't load
- Browser console shows connection errors
- Accessing via EC2 public IP fails

**Fix:**
The `vite.config.ts` has been updated to remove the restrictive `allowedHosts` setting. Restart the frontend:

```bash
# Stop current frontend process
pkill -f "vite"

# Restart frontend
cd /home/ec2-user/solutionbuilder_core/frontend
npm run dev -- --host 0.0.0.0 --port 5000
```

#### Issue 2: Missing Dependencies

**Symptoms:**
- Module not found errors in browser console
- Build errors

**Fix:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

#### Issue 3: TypeScript Compilation Errors

**Symptoms:**
- Build fails
- Browser shows blank page

**Fix:**
```bash
cd frontend
npx tsc --noEmit
# Fix any TypeScript errors shown
```

#### Issue 4: CORS Issues

**Symptoms:**
- Network requests fail
- Browser console shows CORS errors

**Fix:**
- Backend CORS is configured to allow all origins
- Check backend is running: `curl http://localhost:8000/health`
- Verify proxy configuration in `vite.config.ts`

#### Issue 5: Port Already in Use

**Symptoms:**
- Frontend won't start
- Port binding errors

**Fix:**
```bash
# Find process using port 5000
sudo lsof -i :5000
# Kill the process
kill -9 <PID>
```

#### Issue 6: Security Group Not Configured

**Symptoms:**
- Can't access from browser
- Connection timeout

**Fix:**
Ensure AWS Security Group allows inbound traffic on port 5000:
- Type: Custom TCP
- Port: 5000
- Source: Your IP or 0.0.0.0/0 (for testing)

### Diagnostic Commands

```bash
# Full diagnostic
cd frontend
./diagnose_frontend.sh

# Check if React is loading
curl -s http://localhost:5000 | grep -i "react\|root"

# Check Vite dev server logs
# (if running in foreground, check terminal output)
# (if running via systemd, check logs)
sudo journalctl -u nebula-frontend.service -f
```

### Browser-Specific Checks

1. **Clear Browser Cache**
   - Hard refresh: Ctrl+Shift+R (Windows/Linux) or Cmd+Shift+R (Mac)
   - Or clear cache in DevTools

2. **Check Network Tab**
   - Look for failed requests (red entries)
   - Check if `/src/main.tsx` loads successfully
   - Verify API proxy requests go to `/api/*`

3. **Check Console Tab**
   - Look for JavaScript errors
   - Check for module loading errors
   - Verify React is mounting: Look for "App component mounted successfully"

### Expected Behavior

When working correctly:
1. HTML loads with `<div id="root"></div>`
2. `/src/main.tsx` loads successfully
3. React mounts and renders App component
4. Console shows: "App component rendering..." and "App component mounted successfully"
5. UI appears with Nebula logo and chat interface

### Still Not Working?

1. **Check Backend Connection**
   ```bash
   curl http://localhost:8000/health
   ```

2. **Test API Proxy**
   ```bash
   curl http://localhost:5000/api/health
   ```

3. **Check Logs**
   ```bash
   # Frontend logs (if using systemd)
   sudo journalctl -u nebula-frontend.service -n 50
   
   # Backend logs
   tail -50 /home/ec2-user/solutionbuilder_core/backend/aws_architect.log
   ```

4. **Restart Services**
   ```bash
   # If using systemd
   sudo systemctl restart nebula-frontend.service
   sudo systemctl restart nebula-backend.service
   
   # If running manually
   # Kill processes and restart
   pkill -f "vite"
   pkill -f "uvicorn"
   # Then restart both services
   ```

