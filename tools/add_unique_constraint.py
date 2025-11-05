"""Add unique constraint to prevent duplicate entries"""

import sqlite3

def add_unique_constraint(db_path='data/mountain_huts.db'):
    """Add unique constraint on source + source_id"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print('Adding unique constraint on (source, source_id)...')
    
    try:
        # Check if index already exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name='idx_source_source_id_unique'")
        if cursor.fetchone():
            print('[INFO] Unique index already exists')
            conn.close()
            return
        
        # Create unique index
        cursor.execute('''
            CREATE UNIQUE INDEX idx_source_source_id_unique 
            ON mountain_huts(source, source_id)
        ''')
        
        conn.commit()
        print('[SUCCESS] Added unique constraint to prevent duplicates')
        
        # Verify
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name='idx_source_source_id_unique'")
        if cursor.fetchone():
            print('[VERIFIED] Unique index is active')
        
    except sqlite3.IntegrityError as e:
        print(f'[ERROR] Could not add constraint: {e}')
        print('This might mean there are still duplicate entries in the database')
    except Exception as e:
        print(f'[ERROR] Unexpected error: {e}')
    
    conn.close()

if __name__ == '__main__':
    print('=' * 60)
    print('ADDING DATABASE CONSTRAINTS')
    print('=' * 60)
    add_unique_constraint()

