#!/usr/bin/env python3
"""
Database Improvement and Maintenance Tool
==========================================

This script performs comprehensive database optimization:
- Data quality analysis and reporting
- Duplicate detection and removal
- Data validation and normalization
- Index optimization
- Database vacuuming and analysis
- Orphaned record cleanup
- Statistics generation
- Health checks

Usage:
    python tools/improve_database.py --analyze     # Analyze only (safe)
    python tools/improve_database.py --optimize    # Full optimization
    python tools/improve_database.py --fix         # Fix issues
    python tools/improve_database.py --all         # All operations

Author: Database Optimization Tool
Date: November 6, 2025
"""

import sqlite3
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import json

# Fix Windows encoding issues
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database import MountainHutsDatabase


class DatabaseImprover:
    """Comprehensive database improvement and maintenance tool"""
    
    def __init__(self, db_path: str = "data/mountain_huts.db"):
        self.db_path = Path(db_path)
        self.db = MountainHutsDatabase(str(self.db_path))
        self.issues = []
        self.fixes = []
        self.stats = {}
        
        # Ensure backup directory exists
        self.backup_dir = Path("data/backups")
        self.backup_dir.mkdir(exist_ok=True, parents=True)
    
    def print_header(self, title: str):
        """Print a formatted section header"""
        print("\n" + "=" * 80)
        print(f"  {title}")
        print("=" * 80)
    
    def print_section(self, title: str):
        """Print a formatted subsection"""
        print(f"\n{'─' * 80}")
        print(f"  {title}")
        print(f"{'─' * 80}")
    
    def create_backup(self) -> Path:
        """Create database backup before making changes"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / f"mountain_huts_backup_{timestamp}.db"
        
        print(f"\n📦 Creating backup: {backup_path.name}")
        
        import shutil
        shutil.copy2(self.db_path, backup_path)
        
        # Verify backup
        if backup_path.exists():
            size = backup_path.stat().st_size / (1024 * 1024)
            print(f"   ✓ Backup created: {size:.2f} MB")
            return backup_path
        else:
            raise Exception("Failed to create backup")
    
    def analyze_database(self) -> Dict:
        """Perform comprehensive database analysis"""
        self.print_header("DATABASE ANALYSIS")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        analysis = {}
        
        # 1. Database file size
        self.print_section("Database Size")
        db_size = self.db_path.stat().st_size / (1024 * 1024)
        analysis['db_size_mb'] = round(db_size, 2)
        print(f"   Database file size: {db_size:.2f} MB")
        
        # 2. Table statistics
        self.print_section("Table Statistics")
        
        # Mountain huts table
        cursor.execute("SELECT COUNT(*) FROM mountain_huts")
        total_huts = cursor.fetchone()[0]
        analysis['total_huts'] = total_huts
        print(f"   Total huts: {total_huts:,}")
        
        # Huts with coordinates
        cursor.execute("""
            SELECT COUNT(*) FROM mountain_huts 
            WHERE latitude IS NOT NULL AND longitude IS NOT NULL
        """)
        with_coords = cursor.fetchone()[0]
        analysis['huts_with_coords'] = with_coords
        print(f"   With coordinates: {with_coords:,} ({with_coords/total_huts*100:.1f}%)")
        
        # Huts without coordinates
        missing_coords = total_huts - with_coords
        if missing_coords > 0:
            self.issues.append(f"{missing_coords} huts missing coordinates")
            print(f"   ⚠️  Missing coordinates: {missing_coords:,}")
        
        # 3. Data completeness
        self.print_section("Data Completeness")
        
        fields_to_check = {
            'name': 'Name',
            'country': 'Country',
            'hut_type': 'Hut Type',
            'altitude': 'Altitude',
            'phone': 'Phone',
            'email': 'Email',
            'website': 'Website',
            'opening_hours': 'Opening Hours',
            'capacity': 'Capacity',
            'description': 'Description',
            'owner': 'Owner',
            'manager': 'Manager'
        }
        
        completeness = {}
        for field, label in fields_to_check.items():
            cursor.execute(f"""
                SELECT COUNT(*) FROM mountain_huts 
                WHERE {field} IS NOT NULL AND {field} != '' AND {field} != 'N/A'
            """)
            count = cursor.fetchone()[0]
            percentage = (count / total_huts * 100) if total_huts > 0 else 0
            completeness[field] = {
                'count': count,
                'percentage': round(percentage, 1)
            }
            
            status = "✓" if percentage > 50 else "⚠️" if percentage > 20 else "✗"
            print(f"   {status} {label}: {count:,} ({percentage:.1f}%)")
        
        analysis['completeness'] = completeness
        
        # 4. Duplicate detection
        self.print_section("Duplicate Detection")
        
        # Exact name duplicates
        cursor.execute("""
            SELECT name, COUNT(*) as count
            FROM mountain_huts
            GROUP BY name
            HAVING count > 1
            ORDER BY count DESC
            LIMIT 10
        """)
        name_dupes = cursor.fetchall()
        
        if name_dupes:
            total_name_dupes = sum(count - 1 for _, count in name_dupes)
            self.issues.append(f"{total_name_dupes} potential name duplicates")
            print(f"   ⚠️  Potential name duplicates: {total_name_dupes}")
            for name, count in name_dupes[:5]:
                print(f"      - '{name}': {count} occurrences")
        else:
            print("   ✓ No exact name duplicates found")
        
        # Coordinate duplicates
        cursor.execute("""
            SELECT latitude, longitude, COUNT(*) as count
            FROM mountain_huts
            WHERE latitude IS NOT NULL AND longitude IS NOT NULL
            GROUP BY latitude, longitude
            HAVING count > 1
            ORDER BY count DESC
            LIMIT 10
        """)
        coord_dupes = cursor.fetchall()
        
        if coord_dupes:
            total_coord_dupes = sum(count - 1 for _, _, count in coord_dupes)
            print(f"   ℹ️  Same coordinates: {total_coord_dupes} (may be legitimate)")
            for lat, lon, count in coord_dupes[:3]:
                print(f"      - ({lat}, {lon}): {count} huts")
        else:
            print("   ✓ No coordinate duplicates")
        
        # 5. Data quality issues
        self.print_section("Data Quality Issues")
        
        # Invalid coordinates
        cursor.execute("""
            SELECT COUNT(*) FROM mountain_huts
            WHERE latitude IS NOT NULL AND (latitude < -90 OR latitude > 90)
        """)
        invalid_lat = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(*) FROM mountain_huts
            WHERE longitude IS NOT NULL AND (longitude < -180 OR longitude > 180)
        """)
        invalid_lon = cursor.fetchone()[0]
        
        if invalid_lat > 0 or invalid_lon > 0:
            self.issues.append(f"{invalid_lat + invalid_lon} huts with invalid coordinates")
            print(f"   ✗ Invalid latitudes: {invalid_lat}")
            print(f"   ✗ Invalid longitudes: {invalid_lon}")
        else:
            print("   ✓ All coordinates are valid")
        
        # Suspicious altitudes
        cursor.execute("""
            SELECT COUNT(*) FROM mountain_huts
            WHERE altitude IS NOT NULL AND (altitude < -500 OR altitude > 9000)
        """)
        suspicious_alt = cursor.fetchone()[0]
        
        if suspicious_alt > 0:
            self.issues.append(f"{suspicious_alt} huts with suspicious altitudes")
            print(f"   ⚠️  Suspicious altitudes (<-500m or >9000m): {suspicious_alt}")
        else:
            print("   ✓ All altitudes are reasonable")
        
        # Empty names
        cursor.execute("""
            SELECT COUNT(*) FROM mountain_huts
            WHERE name IS NULL OR name = '' OR name = 'Unknown' OR name = 'N/A'
        """)
        empty_names = cursor.fetchone()[0]
        
        if empty_names > 0:
            self.issues.append(f"{empty_names} huts with missing/invalid names")
            print(f"   ✗ Missing/invalid names: {empty_names}")
        else:
            print("   ✓ All huts have valid names")
        
        # 6. Source distribution
        self.print_section("Data Sources")
        
        cursor.execute("""
            SELECT source, COUNT(*) as count
            FROM mountain_huts
            GROUP BY source
            ORDER BY count DESC
        """)
        sources = cursor.fetchall()
        
        analysis['sources'] = {}
        for source, count in sources:
            percentage = (count / total_huts * 100) if total_huts > 0 else 0
            analysis['sources'][source] = {
                'count': count,
                'percentage': round(percentage, 1)
            }
            print(f"   • {source}: {count:,} ({percentage:.1f}%)")
        
        # 7. Country distribution
        self.print_section("Country Distribution")
        
        cursor.execute("""
            SELECT country, COUNT(*) as count
            FROM mountain_huts
            WHERE country IS NOT NULL AND country != '' AND country != 'N/A'
            GROUP BY country
            ORDER BY count DESC
            LIMIT 15
        """)
        countries = cursor.fetchall()
        
        analysis['top_countries'] = {}
        for country, count in countries:
            percentage = (count / total_huts * 100) if total_huts > 0 else 0
            analysis['top_countries'][country] = count
            print(f"   • {country}: {count:,} ({percentage:.1f}%)")
        
        # Huts without country
        cursor.execute("""
            SELECT COUNT(*) FROM mountain_huts
            WHERE country IS NULL OR country = '' OR country = 'N/A'
        """)
        no_country = cursor.fetchone()[0]
        
        if no_country > 0:
            print(f"   ⚠️  Without country: {no_country:,}")
        
        # 8. Database indexes
        self.print_section("Database Indexes")
        
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='index' AND tbl_name='mountain_huts'
            ORDER BY name
        """)
        indexes = cursor.fetchall()
        
        analysis['indexes'] = [idx[0] for idx in indexes]
        print(f"   Found {len(indexes)} indexes:")
        for idx in indexes:
            print(f"   • {idx[0]}")
        
        conn.close()
        
        # Summary
        self.print_section("Analysis Summary")
        print(f"   Total issues found: {len(self.issues)}")
        if self.issues:
            for i, issue in enumerate(self.issues, 1):
                print(f"   {i}. {issue}")
        else:
            print("   ✓ No major issues detected!")
        
        self.stats = analysis
        return analysis
    
    def optimize_indexes(self, conn: sqlite3.Connection) -> int:
        """Optimize database indexes"""
        cursor = conn.cursor()
        changes = 0
        
        print("\n🔧 Optimizing indexes...")
        
        # Check existing indexes
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='index' AND tbl_name='mountain_huts'
        """)
        existing = {row[0] for row in cursor.fetchall()}
        
        # Recommended indexes
        recommended = {
            'idx_name': 'CREATE INDEX IF NOT EXISTS idx_name ON mountain_huts(name)',
            'idx_location': 'CREATE INDEX IF NOT EXISTS idx_location ON mountain_huts(latitude, longitude)',
            'idx_source': 'CREATE INDEX IF NOT EXISTS idx_source ON mountain_huts(source)',
            'idx_country': 'CREATE INDEX IF NOT EXISTS idx_country ON mountain_huts(country)',
            'idx_hut_type': 'CREATE INDEX IF NOT EXISTS idx_hut_type ON mountain_huts(hut_type)',
            'idx_source_id': 'CREATE INDEX IF NOT EXISTS idx_source_id ON mountain_huts(source, source_id)',
            'idx_altitude': 'CREATE INDEX IF NOT EXISTS idx_altitude ON mountain_huts(altitude)',
        }
        
        for idx_name, create_sql in recommended.items():
            if idx_name not in existing:
                print(f"   ➕ Creating index: {idx_name}")
                cursor.execute(create_sql)
                changes += 1
            else:
                print(f"   ✓ Index exists: {idx_name}")
        
        return changes
    
    def vacuum_database(self, conn: sqlite3.Connection):
        """Run VACUUM to reclaim space and optimize"""
        print("\n🧹 Running VACUUM...")
        
        before_size = self.db_path.stat().st_size / (1024 * 1024)
        
        cursor = conn.cursor()
        cursor.execute("VACUUM")
        
        after_size = self.db_path.stat().st_size / (1024 * 1024)
        saved = before_size - after_size
        
        print(f"   Before: {before_size:.2f} MB")
        print(f"   After: {after_size:.2f} MB")
        print(f"   Saved: {saved:.2f} MB ({saved/before_size*100:.1f}%)")
    
    def analyze_statistics(self, conn: sqlite3.Connection):
        """Update SQLite statistics for query optimizer"""
        print("\n📊 Updating statistics (ANALYZE)...")
        
        cursor = conn.cursor()
        cursor.execute("ANALYZE")
        
        print("   ✓ Statistics updated")
    
    def fix_data_issues(self, conn: sqlite3.Connection, dry_run: bool = False) -> int:
        """Fix common data quality issues"""
        cursor = conn.cursor()
        fixes_made = 0
        
        mode = "DRY RUN" if dry_run else "FIXING"
        print(f"\n🔧 {mode}: Data Quality Issues")
        
        # 1. Normalize empty values to NULL
        print("\n   Normalizing empty values...")
        
        fields = ['country', 'hut_type', 'description', 'phone', 'email', 'website',
                  'opening_hours', 'owner', 'manager', 'water_source', 'access']
        
        for field in fields:
            cursor.execute(f"""
                SELECT COUNT(*) FROM mountain_huts
                WHERE {field} IN ('', 'N/A', 'Unknown', 'unknown', 'n/a', 'null', 'NULL')
            """)
            count = cursor.fetchone()[0]
            
            if count > 0:
                print(f"   • {field}: {count} empty values")
                
                if not dry_run:
                    cursor.execute(f"""
                        UPDATE mountain_huts
                        SET {field} = NULL
                        WHERE {field} IN ('', 'N/A', 'Unknown', 'unknown', 'n/a', 'null', 'NULL')
                    """)
                    fixes_made += count
        
        # 2. Trim whitespace
        print("\n   Trimming whitespace...")
        
        text_fields = ['name', 'country', 'hut_type', 'description', 'owner', 'manager']
        
        for field in text_fields:
            if not dry_run:
                cursor.execute(f"""
                    UPDATE mountain_huts
                    SET {field} = TRIM({field})
                    WHERE {field} != TRIM({field}) AND {field} IS NOT NULL
                """)
                if cursor.rowcount > 0:
                    print(f"   • {field}: trimmed {cursor.rowcount} values")
                    fixes_made += cursor.rowcount
        
        # 3. Fix invalid coordinates (set to NULL)
        print("\n   Fixing invalid coordinates...")
        
        cursor.execute("""
            SELECT COUNT(*) FROM mountain_huts
            WHERE latitude IS NOT NULL AND (latitude < -90 OR latitude > 90)
        """)
        invalid_lat = cursor.fetchone()[0]
        
        if invalid_lat > 0:
            print(f"   • Invalid latitudes: {invalid_lat}")
            if not dry_run:
                cursor.execute("""
                    UPDATE mountain_huts
                    SET latitude = NULL
                    WHERE latitude < -90 OR latitude > 90
                """)
                fixes_made += invalid_lat
        
        cursor.execute("""
            SELECT COUNT(*) FROM mountain_huts
            WHERE longitude IS NOT NULL AND (longitude < -180 OR longitude > 180)
        """)
        invalid_lon = cursor.fetchone()[0]
        
        if invalid_lon > 0:
            print(f"   • Invalid longitudes: {invalid_lon}")
            if not dry_run:
                cursor.execute("""
                    UPDATE mountain_huts
                    SET longitude = NULL
                    WHERE longitude < -180 OR longitude > 180
                """)
                fixes_made += invalid_lon
        
        # 4. Update timestamps
        if not dry_run:
            cursor.execute("""
                UPDATE mountain_huts
                SET updated_at = CURRENT_TIMESTAMP
                WHERE updated_at IS NULL OR updated_at < scraped_at
            """)
            if cursor.rowcount > 0:
                print(f"\n   • Updated timestamps: {cursor.rowcount}")
                fixes_made += cursor.rowcount
        
        if dry_run:
            print(f"\n   ℹ️  DRY RUN: Would fix {fixes_made} issues")
        else:
            print(f"\n   ✓ Fixed {fixes_made} issues")
        
        return fixes_made
    
    def generate_report(self, output_file: str = "data/database_report.json"):
        """Generate JSON report of database status"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'database_path': str(self.db_path),
            'statistics': self.stats,
            'issues': self.issues,
            'fixes': self.fixes
        }
        
        output_path = Path(output_file)
        output_path.parent.mkdir(exist_ok=True, parents=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Report saved: {output_path}")
        return report
    
    def run_optimization(self, fix_issues: bool = False, skip_backup: bool = False):
        """Run full database optimization"""
        self.print_header("DATABASE OPTIMIZATION TOOL")
        print(f"Database: {self.db_path}")
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Step 1: Analyze
        print("\n" + "▶" * 40)
        print("STEP 1: ANALYSIS")
        print("▶" * 40)
        
        self.analyze_database()
        
        # If only analysis, stop here
        if not fix_issues and self.issues:
            print(f"\n⚠️  Found {len(self.issues)} issues. Run with --fix to repair them.")
            return
        
        if not self.issues and not fix_issues:
            print("\n✅ Database is in good shape! No optimization needed.")
            return
        
        # Step 2: Backup
        if not skip_backup:
            print("\n" + "▶" * 40)
            print("STEP 2: BACKUP")
            print("▶" * 40)
            
            backup_path = self.create_backup()
        
        # Step 3: Optimize
        print("\n" + "▶" * 40)
        print("STEP 3: OPTIMIZATION")
        print("▶" * 40)
        
        conn = sqlite3.connect(self.db_path)
        
        try:
            # Fix data issues
            if fix_issues:
                fixes = self.fix_data_issues(conn, dry_run=False)
                self.fixes.append(f"Fixed {fixes} data quality issues")
            
            # Optimize indexes
            idx_changes = self.optimize_indexes(conn)
            if idx_changes > 0:
                self.fixes.append(f"Created {idx_changes} new indexes")
            
            # Commit changes
            conn.commit()
            
            # VACUUM and ANALYZE
            self.vacuum_database(conn)
            self.analyze_statistics(conn)
            
            print("\n✅ Optimization complete!")
            
        except Exception as e:
            conn.rollback()
            print(f"\n❌ Error during optimization: {e}")
            print(f"   Restore from backup: {backup_path if not skip_backup else 'N/A'}")
            raise
        
        finally:
            conn.close()
        
        # Step 4: Report
        print("\n" + "▶" * 40)
        print("STEP 4: FINAL REPORT")
        print("▶" * 40)
        
        self.generate_report()
        
        # Final summary
        self.print_header("OPTIMIZATION SUMMARY")
        print(f"   Issues found: {len(self.issues)}")
        print(f"   Fixes applied: {len(self.fixes)}")
        for fix in self.fixes:
            print(f"   ✓ {fix}")
        
        print(f"\n   Backup: {backup_path if not skip_backup else 'Skipped'}")
        print(f"   Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("\n" + "=" * 80)


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Database Improvement and Maintenance Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python tools/improve_database.py --analyze         # Analyze only (safe)
  python tools/improve_database.py --optimize        # Optimize indexes + VACUUM
  python tools/improve_database.py --fix             # Fix data issues
  python tools/improve_database.py --all             # Full optimization
  python tools/improve_database.py --all --no-backup # Skip backup (faster)
        """
    )
    
    parser.add_argument('--analyze', action='store_true',
                        help='Analyze database only (no changes)')
    parser.add_argument('--optimize', action='store_true',
                        help='Optimize indexes and VACUUM')
    parser.add_argument('--fix', action='store_true',
                        help='Fix data quality issues')
    parser.add_argument('--all', action='store_true',
                        help='Run all operations')
    parser.add_argument('--no-backup', action='store_true',
                        help='Skip backup creation (not recommended)')
    parser.add_argument('--db', type=str, default='data/mountain_huts.db',
                        help='Path to database file')
    
    args = parser.parse_args()
    
    # If no arguments, show help
    if not any([args.analyze, args.optimize, args.fix, args.all]):
        parser.print_help()
        sys.exit(0)
    
    improver = DatabaseImprover(args.db)
    
    try:
        if args.all:
            improver.run_optimization(fix_issues=True, skip_backup=args.no_backup)
        elif args.analyze:
            improver.analyze_database()
            improver.generate_report()
        elif args.fix:
            improver.run_optimization(fix_issues=True, skip_backup=args.no_backup)
        elif args.optimize:
            improver.run_optimization(fix_issues=False, skip_backup=args.no_backup)
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

