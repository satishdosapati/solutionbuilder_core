"""
Diagram Storage Service - Saves and serves architecture diagrams
Minimalist Mode 🧭
"""
import os
import base64
import logging
import uuid
from pathlib import Path
from typing import Optional, Tuple
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Directory to store diagrams
DIAGRAMS_DIR = Path(__file__).parent.parent / "generated-diagrams"

# Cleanup configuration
CLEANUP_MAX_AGE_HOURS = 24  # Delete files older than 24 hours

def ensure_diagrams_directory():
    """Ensure the diagrams directory exists"""
    DIAGRAMS_DIR.mkdir(parents=True, exist_ok=True)
    return DIAGRAMS_DIR

def save_diagram_from_base64(base64_data: str, diagram_name: Optional[str] = None) -> Tuple[str, str]:
    """
    Save diagram from base64 data to file and return filename and URL path
    
    Args:
        base64_data: Base64 encoded image data (with or without data URI prefix)
        diagram_name: Optional name for the diagram file
    
    Returns:
        Tuple of (filename, url_path) where url_path is relative URL like /api/diagrams/filename.png
    """
    ensure_diagrams_directory()
    
    # Extract base64 data and image type
    if base64_data.startswith('data:image/'):
        # Extract type and data from data URI
        header, data = base64_data.split(',', 1)
        image_type = header.split('/')[1].split(';')[0]  # Extract png, svg, etc.
    else:
        # Assume PNG if no prefix
        data = base64_data
        image_type = 'png'
    
    # Generate filename
    if diagram_name:
        # Sanitize diagram name for filename
        safe_name = "".join(c for c in diagram_name if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_name = safe_name.replace(' ', '_').lower()
        filename = f"{safe_name}_{uuid.uuid4().hex[:8]}.{image_type}"
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"diagram_{timestamp}_{uuid.uuid4().hex[:8]}.{image_type}"
    
    filepath = DIAGRAMS_DIR / filename
    
    try:
        # Decode and save
        image_bytes = base64.b64decode(data)
        with open(filepath, 'wb') as f:
            f.write(image_bytes)
        
        logger.info(f"Saved diagram to {filepath} ({len(image_bytes)} bytes)")
        
        # Return relative URL path
        url_path = f"/api/diagrams/{filename}"
        return filename, url_path
    
    except Exception as e:
        logger.error(f"Failed to save diagram: {e}")
        raise

def get_diagram_path(filename: str) -> Optional[Path]:
    """Get full path to diagram file if it exists"""
    filepath = DIAGRAMS_DIR / filename
    if filepath.exists() and filepath.is_file():
        return filepath
    return None

def cleanup_old_diagrams(max_age_hours: int = CLEANUP_MAX_AGE_HOURS) -> dict:
    """
    Clean up diagrams older than max_age_hours
    
    Args:
        max_age_hours: Maximum age in hours before deletion (default: 24)
    
    Returns:
        Dictionary with cleanup statistics
    """
    ensure_diagrams_directory()
    
    cutoff_time = datetime.now().timestamp() - (max_age_hours * 60 * 60)
    
    deleted_count = 0
    deleted_size = 0
    errors = []
    
    try:
        for filepath in DIAGRAMS_DIR.glob("*"):
            if filepath.is_file():
                try:
                    file_mtime = filepath.stat().st_mtime
                    file_size = filepath.stat().st_size
                    
                    if file_mtime < cutoff_time:
                        filepath.unlink()
                        deleted_count += 1
                        deleted_size += file_size
                        logger.debug(f"Deleted old diagram: {filepath.name} (age: {(datetime.now().timestamp() - file_mtime) / 3600:.1f} hours)")
                except Exception as e:
                    error_msg = f"Failed to delete {filepath.name}: {e}"
                    errors.append(error_msg)
                    logger.warning(error_msg)
        
        if deleted_count > 0:
            logger.info(f"Cleaned up {deleted_count} old diagram files ({deleted_size / 1024:.1f} KB freed)")
        
        return {
            "success": True,
            "deleted_count": deleted_count,
            "deleted_size_bytes": deleted_size,
            "deleted_size_kb": round(deleted_size / 1024, 2),
            "errors": errors
        }
    
    except Exception as e:
        logger.error(f"Error during diagram cleanup: {e}")
        return {
            "success": False,
            "error": str(e),
            "deleted_count": deleted_count,
            "deleted_size_bytes": deleted_size
        }

def get_diagram_stats() -> dict:
    """Get statistics about stored diagrams"""
    ensure_diagrams_directory()
    
    total_files = 0
    total_size = 0
    files_by_age = {
        "less_than_1_hour": 0,
        "1_to_6_hours": 0,
        "6_to_12_hours": 0,
        "12_to_24_hours": 0,
        "older_than_24_hours": 0
    }
    
    now = datetime.now().timestamp()
    
    try:
        for filepath in DIAGRAMS_DIR.glob("*"):
            if filepath.is_file():
                total_files += 1
                total_size += filepath.stat().st_size
                
                age_hours = (now - filepath.stat().st_mtime) / 3600
                
                if age_hours < 1:
                    files_by_age["less_than_1_hour"] += 1
                elif age_hours < 6:
                    files_by_age["1_to_6_hours"] += 1
                elif age_hours < 12:
                    files_by_age["6_to_12_hours"] += 1
                elif age_hours < 24:
                    files_by_age["12_to_24_hours"] += 1
                else:
                    files_by_age["older_than_24_hours"] += 1
        
        return {
            "total_files": total_files,
            "total_size_bytes": total_size,
            "total_size_kb": round(total_size / 1024, 2),
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "files_by_age": files_by_age
        }
    
    except Exception as e:
        logger.error(f"Error getting diagram stats: {e}")
        return {
            "total_files": 0,
            "total_size_bytes": 0,
            "error": str(e)
        }

