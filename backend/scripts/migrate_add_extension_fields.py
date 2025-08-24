#!/usr/bin/env python3
"""
Migration script to add extension-specific fields to JobApplication table.
Run this script to add the new columns: job_board, captured_at, extraction_data
"""

import sqlite3
import os
import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from config.settings import settings

def migrate_database():
    """Add new columns to the JobApplication table"""
    
    # Get the database path from settings
    if "sqlite" in settings.database_url:
        # Extract the database file path from the URL
        db_path = settings.database_url.replace("sqlite:///", "")
        if not os.path.isabs(db_path):
            db_path = os.path.join(backend_dir, db_path)
    else:
        print("❌ This migration script only supports SQLite databases")
        return False
    
    print(f"🔧 Starting migration for database: {db_path}")
    
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if the columns already exist
        cursor.execute("PRAGMA table_info(job_applications)")
        columns = [column[1] for column in cursor.fetchall()]
        
        print(f"📋 Current columns: {columns}")
        
        # Add new columns if they don't exist
        new_columns = [
            ("job_board", "TEXT"),
            ("captured_at", "DATETIME"),
            ("extraction_data", "TEXT")
        ]
        
        for column_name, column_type in new_columns:
            if column_name not in columns:
                print(f"➕ Adding column: {column_name} ({column_type})")
                cursor.execute(f"ALTER TABLE job_applications ADD COLUMN {column_name} {column_type}")
                print(f"✅ Added column: {column_name}")
            else:
                print(f"ℹ️  Column {column_name} already exists, skipping...")
        
        # Commit the changes
        conn.commit()
        print("✅ Migration completed successfully!")
        
        # Verify the new structure
        cursor.execute("PRAGMA table_info(job_applications)")
        final_columns = [column[1] for column in cursor.fetchall()]
        print(f"📋 Final columns: {final_columns}")
        
        return True
        
    except sqlite3.Error as e:
        print(f"❌ SQLite error during migration: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error during migration: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("🚀 Starting JobApplication table migration...")
    success = migrate_database()
    
    if success:
        print("🎉 Migration completed successfully!")
        sys.exit(0)
    else:
        print("💥 Migration failed!")
        sys.exit(1)
