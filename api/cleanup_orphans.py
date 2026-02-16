"""
Cleanup orphaned files - files on disk with no database record.

Run this occasionally to free up space from failed deletions.
"""

from pathlib import Path
from api.database import SessionLocal
from api.models import Photo

def cleanup_orphaned_files():
    """
    Find and delete files that have no corresponding database record.
    """
    db = SessionLocal()
    
    try:
        # Get all file hashes from database
        db_hashes = {photo.file_hash for photo in db.query(Photo).all()}
        
        print(f"📊 Found {len(db_hashes)} photos in database")
        
        # Check all files in storage
        storage_path = Path("/app/storage/photos")
        deleted_count = 0
        
        for file_path in storage_path.glob("*"):
            # Skip .gitkeep
            if file_path.name == ".gitkeep":
                continue
            
            # Extract hash from filename (everything before extension)
            file_hash = file_path.stem
            
            # If hash not in database, it's an orphan
            if file_hash not in db_hashes:
                print(f"🗑️  Deleting orphan: {file_path.name}")
                file_path.unlink()
                deleted_count += 1
        
        print(f"✅ Cleanup complete: Deleted {deleted_count} orphaned files")
        
    finally:
        db.close()


if __name__ == "__main__":
    cleanup_orphaned_files()