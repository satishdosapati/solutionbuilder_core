"""
Pytest configuration file
Ensures project root and backend directory are in Python path for imports
"""
import sys
from pathlib import Path

# Add project root to Python path (for tests importing backend.*)
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Add backend directory to Python path (for backend code using 'from services.*')
backend_dir = project_root / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

