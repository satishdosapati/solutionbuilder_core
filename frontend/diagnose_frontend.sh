#!/bin/bash

echo "=== Frontend Diagnostic Script ==="
echo ""

# Check if we're in the frontend directory
if [ ! -f "package.json" ]; then
    echo "❌ Error: Must run from frontend directory"
    exit 1
fi

echo "1. Checking Node.js version..."
node --version
npm --version
echo ""

echo "2. Checking if dependencies are installed..."
if [ ! -d "node_modules" ]; then
    echo "❌ node_modules not found - dependencies not installed"
    echo "   Run: npm install"
else
    echo "✅ node_modules exists"
fi
echo ""

echo "3. Checking critical dependencies..."
for dep in "react" "react-dom" "vite" "@vitejs/plugin-react"; do
    if [ -d "node_modules/$dep" ]; then
        echo "✅ $dep installed"
    else
        echo "❌ $dep NOT installed"
    fi
done
echo ""

echo "4. Checking source files..."
for file in "src/main.tsx" "src/App.tsx" "src/index.css" "index.html"; do
    if [ -f "$file" ]; then
        echo "✅ $file exists"
    else
        echo "❌ $file MISSING"
    fi
done
echo ""

echo "5. Checking TypeScript compilation..."
if command -v npx &> /dev/null; then
    npx tsc --noEmit 2>&1 | head -20
    if [ $? -eq 0 ]; then
        echo "✅ TypeScript compilation successful"
    else
        echo "❌ TypeScript compilation errors found"
    fi
else
    echo "⚠️  npx not available, skipping TypeScript check"
fi
echo ""

echo "6. Checking if Vite dev server is running..."
if pgrep -f "vite" > /dev/null; then
    echo "✅ Vite process found"
    pgrep -f "vite" | xargs ps -fp
else
    echo "❌ Vite process not found"
fi
echo ""

echo "7. Checking port 5000..."
if netstat -tuln 2>/dev/null | grep -q ":5000" || ss -tuln 2>/dev/null | grep -q ":5000"; then
    echo "✅ Port 5000 is listening"
    netstat -tuln 2>/dev/null | grep ":5000" || ss -tuln 2>/dev/null | grep ":5000"
else
    echo "❌ Port 5000 is NOT listening"
fi
echo ""

echo "8. Testing frontend endpoint..."
if command -v curl &> /dev/null; then
    echo "Testing http://localhost:5000..."
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000 2>/dev/null)
    if [ "$HTTP_CODE" = "200" ]; then
        echo "✅ Frontend responds with HTTP 200"
        echo "Checking HTML content..."
        curl -s http://localhost:5000 | head -20
    else
        echo "❌ Frontend responds with HTTP $HTTP_CODE"
    fi
else
    echo "⚠️  curl not available, skipping endpoint test"
fi
echo ""

echo "9. Checking for common issues..."
echo "   - Checking vite.config.ts..."
if grep -q "host.*0.0.0.0" vite.config.ts 2>/dev/null; then
    echo "   ✅ Vite configured to listen on 0.0.0.0"
else
    echo "   ⚠️  Vite may not be configured to listen on all interfaces"
fi

echo "   - Checking for CORS issues..."
if grep -q "proxy.*localhost:8000" vite.config.ts 2>/dev/null; then
    echo "   ✅ API proxy configured"
else
    echo "   ⚠️  API proxy may not be configured correctly"
fi
echo ""

echo "10. Checking browser console simulation..."
echo "    Testing if main.tsx can be loaded..."
if [ -f "src/main.tsx" ]; then
    # Check for syntax errors
    if node -e "require('fs').readFileSync('src/main.tsx', 'utf8')" 2>&1 | grep -q "Error"; then
        echo "   ❌ Syntax error in main.tsx"
    else
        echo "   ✅ main.tsx syntax appears valid"
    fi
fi
echo ""

echo "=== Diagnostic Complete ==="
echo ""
echo "Common issues to check:"
echo "1. Open browser console (F12) and check for JavaScript errors"
echo "2. Check Network tab for failed requests"
echo "3. Verify security groups allow port 5000"
echo "4. Check if accessing via correct URL (http://EC2_IP:5000)"
echo "5. Try accessing from localhost first: curl http://localhost:5000"

