"""Add validation to prevent duplicate hut_type inconsistencies"""
import sqlite3
from pathlib import Path

VALID_HUT_TYPES = [
    'Mountain hut',
    'Unmanned cabin',
    'Bivouac',
    'Guesthouse',
    'Shelter',
    'Unknown'
]

def validate_hut_types():
    """Check for and fix any hut_type inconsistencies"""
    db_path = Path(__file__).parent.parent / "data" / "mountain_huts.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("Validating hut_type values...")
    
    # Get all unique hut_types
    cursor.execute("SELECT DISTINCT hut_type FROM mountain_huts ORDER BY hut_type")
    current_types = [row[0] for row in cursor.fetchall()]
    
    print(f"\nFound {len(current_types)} unique hut_type values:")
    for ht in current_types:
        print(f"  - {ht}")
    
    # Check for case variations
    issues_found = []
    for ht in current_types:
        if ht and ht not in VALID_HUT_TYPES:
            # Check if lowercase version exists in valid types
            normalized = None
            for valid in VALID_HUT_TYPES:
                if valid.lower() == ht.lower():
                    normalized = valid
                    break
            
            if normalized:
                issues_found.append((ht, normalized))
                print(f"\n[ISSUE] Found case mismatch: '{ht}' should be '{normalized}'")
    
    # Fix issues
    if issues_found:
        print("\nFixing inconsistencies...")
        for wrong, correct in issues_found:
            cursor.execute("UPDATE mountain_huts SET hut_type = ? WHERE hut_type = ?", 
                         (correct, wrong))
            print(f"  Fixed: '{wrong}' -> '{correct}' ({cursor.rowcount} rows)")
        
        conn.commit()
        print("\n[OK] All inconsistencies fixed!")
    else:
        print("\n[OK] No inconsistencies found!")
    
    # Show final distribution
    cursor.execute("""
        SELECT hut_type, COUNT(*) as count
        FROM mountain_huts
        GROUP BY hut_type
        ORDER BY count DESC
    """)
    
    print("\nFinal hut_type distribution:")
    for row in cursor.fetchall():
        print(f"  {row[0] or 'NULL'}: {row[1]} huts")
    
    conn.close()
    return len(issues_found) == 0

if __name__ == "__main__":
    validate_hut_types()

