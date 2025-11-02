"""Database migration to add detailed boudy.info columns."""
import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = PROJECT_ROOT / "data" / "mountain_huts.db"


def migrate_database() -> None:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # List of columns to add
    new_columns = [
        ("capacity_max", "INTEGER"),
        ("comments", "TEXT"),
        ("water_source", "TEXT"),
        ("best_time_to_visit", "TEXT"),
        ("access", "TEXT"),
        ("posted_by", "TEXT"),
        ("posted_date", "TEXT"),
    ]
    
    # Get existing columns
    cursor.execute("PRAGMA table_info(mountain_huts)")
    existing_columns = {row[1] for row in cursor.fetchall()}
    
    print(f"Existing columns: {len(existing_columns)}")
    print("Adding missing columns...")
    
    # Add each new column if it doesn't exist
    for column_name, column_type in new_columns:
        if column_name not in existing_columns:
            try:
                cursor.execute(
                    f"ALTER TABLE mountain_huts ADD COLUMN {column_name} {column_type}"
                )
                print(f"✓ Added column: {column_name} ({column_type})")
            except sqlite3.OperationalError as exc:
                print(f"✗ Could not add {column_name}: {exc}")
        else:
            print(f"  Column {column_name} already exists")
    
    conn.commit()
    
    # Verify
    cursor.execute("PRAGMA table_info(mountain_huts)")
    all_columns = [row[1] for row in cursor.fetchall()]
    print(f"\nTotal columns now: {len(all_columns)}")
    print("All columns:", ", ".join(all_columns))
    
    conn.close()
    print("\n✅ Migration complete!")


if __name__ == "__main__":
    migrate_database()
