# Error Fixes - Python 3.13 Compatibility

## Issues Identified

The errors you encountered were caused by:
1. **Python 3.13 compatibility issues** with uvicorn's reloader on Windows
2. **Windows multiprocessing spawn issues** during hot reload
3. **CancelledError and KeyboardInterrupt** during lifespan events
4. **File watching conflicts** causing excessive reload loops

### Root Cause
Python 3.13 was released on October 9, 2024. Some packages like `uvicorn` and its dependencies haven't been fully tested with Python 3.13 yet, particularly the Windows multiprocessing spawn method used by the reloader.

## Fixes Applied

### 1. Modified `main.py`
- Changed default uvicorn.run() to use `reload=False`
- Added comment explaining the change
- Users can still manually use `--reload` if needed

### 2. Created Startup Scripts
- `start.bat` (Windows) - Runs server without reload
- `start.sh` (Unix/Mac) - Runs server without reload
- `start-no-reload.bat` (Alternative for Windows) - Explicit no-reload mode

### 3. Updated Documentation
- Enhanced `README.md` with troubleshooting section
- Added Python version compatibility warnings
- Provided multiple startup options
- Updated setup scripts with instructions

### 4. Updated Setup Scripts
- Enhanced `setup.sh` with Python 3.13 warnings
- Created `setup.bat` for Windows users
- Added clear instructions for each Python version

## How to Use

### For Python 3.13 (Current Setup)
```bash
# Windows
start.bat

# Unix/Mac  
bash start.sh
```

### For Python 3.11 or 3.12
```bash
# Can use reload mode
uvicorn main:app --reload --port 8000
```

### Production Mode
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --no-reload
```

## Alternative Solutions

If you still encounter issues:

### Option 1: Downgrade to Python 3.11 or 3.12
```bash
# Recommended versions
python --version  # Should show 3.11.x or 3.12.x
```

### Option 2: Use Docker
Create a Dockerfile with Python 3.11 or 3.12 to avoid compatibility issues.

### Option 3: Wait for Package Updates
Monitor these packages for Python 3.13 support:
- `uvicorn` (especially `[standard]` extras)
- `starlette` (FastAPI dependency)
- `strands-agents` (if using)

## Testing

After applying these fixes, you should see:
```
INFO:     Started server process [XXXX]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

Instead of the previous error loops. The server will run stably without the reloader issues.

## Notes

- The application now starts without reload by default
- File changes won't trigger auto-restart (restart manually if needed)
- All API endpoints work normally
- MCP servers initialize correctly
- No performance impact from these changes

