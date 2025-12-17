"""
Database Quality Inspection Tool
Analyzes 50 random entries for data quality issues and potential improvements
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import re


class DatabaseInspector:
    def __init__(self, db_path: str = "data/mountain_huts.db"):
        self.db_path = db_path
        self.issues = {
            'missing_critical_data': [],
            'coordinate_issues': [],
            'url_issues': [],
            'inconsistent_formatting': [],
            'duplicate_potential': [],
            'data_quality': [],
            'missing_enhancements': []
        }
        self.stats = {
            'total_inspected': 0,
            'entries_with_issues': 0,
            'total_issues_found': 0
        }
    
    def get_random_entries(self, n: int = 50) -> List[Dict]:
        """Get n random entries from the database"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute(f"SELECT * FROM mountain_huts ORDER BY RANDOM() LIMIT {n}")
        rows = cursor.fetchall()
        
        conn.close()
        return [dict(row) for row in rows]
    
    def check_coordinates(self, entry: Dict) -> List[str]:
        """Check if coordinates are valid and reasonable"""
        issues = []
        lat = entry.get('latitude')
        lon = entry.get('longitude')
        
        if lat is None or lon is None:
            issues.append("Missing coordinates")
        else:
            # Alps region roughly: lat 43-48, lon 5-17
            if not (40.0 <= lat <= 50.0):
                issues.append(f"Suspicious latitude: {lat} (expected ~43-48 for Alps)")
            if not (0.0 <= lon <= 20.0):
                issues.append(f"Suspicious longitude: {lon} (expected ~5-17 for Alps)")
            
            # Check for dummy values
            if lat == 0.0 and lon == 0.0:
                issues.append("Coordinates are (0,0) - likely placeholder")
        
        return issues
    
    def check_urls(self, entry: Dict) -> List[str]:
        """Check URL quality and validity"""
        issues = []
        
        website = entry.get('website')
        url = entry.get('url')
        
        # Check for valid URL format
        url_pattern = re.compile(r'^https?://.+\..+')
        
        if website:
            if not url_pattern.match(website):
                issues.append(f"Invalid website format: {website}")
            if website.strip() != website:
                issues.append("Website has leading/trailing whitespace")
        
        if url:
            if not url_pattern.match(url):
                issues.append(f"Invalid URL format: {url}")
            if url.strip() != url:
                issues.append("URL has leading/trailing whitespace")
        
        # Check for duplicates
        if website and url and website == url:
            issues.append("Website and URL are identical - redundant data")
        
        return issues
    
    def check_critical_fields(self, entry: Dict) -> List[str]:
        """Check for missing critical information"""
        issues = []
        
        # Essential fields
        if not entry.get('name') or entry.get('name').strip() == '':
            issues.append("Missing or empty name")
        
        if entry.get('altitude') is None:
            issues.append("Missing altitude")
        elif entry.get('altitude') == 0:
            issues.append("Altitude is 0 - likely missing")
        elif entry.get('altitude') < 0 or entry.get('altitude') > 9000:
            issues.append(f"Suspicious altitude: {entry.get('altitude')}m")
        
        # Important fields that are commonly missing
        missing = []
        if not entry.get('country'):
            missing.append('country')
        if not entry.get('hut_type'):
            missing.append('hut_type')
        if not entry.get('description'):
            missing.append('description')
        
        if missing:
            issues.append(f"Missing fields: {', '.join(missing)}")
        
        return issues
    
    def check_formatting(self, entry: Dict) -> List[str]:
        """Check for formatting inconsistencies"""
        issues = []
        
        name = entry.get('name', '')
        
        # Check for excessive whitespace
        if '  ' in name:
            issues.append("Name contains double spaces")
        
        # Check for weird characters
        if name and any(char in name for char in ['<', '>', '{', '}', '[', ']']):
            issues.append("Name contains suspicious characters")
        
        # Check phone number format
        phone = entry.get('phone', '')
        if phone:
            # Remove common separators
            cleaned_phone = re.sub(r'[\s\-\(\)\.\/]', '', phone)
            if not cleaned_phone.replace('+', '').isdigit():
                issues.append(f"Phone number has invalid format: {phone}")
        
        # Check email format
        email = entry.get('email', '')
        if email:
            email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
            if not email_pattern.match(email):
                issues.append(f"Invalid email format: {email}")
        
        return issues
    
    def check_data_quality(self, entry: Dict) -> List[str]:
        """Check overall data quality and completeness"""
        issues = []
        
        # Count how many fields are populated
        total_fields = len(entry)
        populated_fields = sum(1 for v in entry.values() if v is not None and str(v).strip() != '')
        completeness = (populated_fields / total_fields) * 100
        
        if completeness < 30:
            issues.append(f"Low data completeness: {completeness:.1f}% of fields populated")
        
        # Check for generic/placeholder text
        description = entry.get('description', '')
        if description:
            placeholder_words = ['test', 'todo', 'tbd', 'unknown', 'n/a', 'none']
            if any(word in description.lower() for word in placeholder_words):
                issues.append("Description contains placeholder text")
        
        # Check capacity
        capacity = entry.get('capacity')
        capacity_max = entry.get('capacity_max')
        
        if capacity and capacity_max:
            if capacity > capacity_max:
                issues.append(f"Capacity ({capacity}) exceeds max capacity ({capacity_max})")
        
        return issues
    
    def check_duplicates(self, entry: Dict, all_entries: List[Dict]) -> List[str]:
        """Check for potential duplicates"""
        issues = []
        
        name = entry.get('name', '').lower().strip()
        lat = entry.get('latitude')
        lon = entry.get('longitude')
        
        if not name or not lat or not lon:
            return issues
        
        # Look for very similar entries
        for other in all_entries:
            if other['id'] == entry['id']:
                continue
            
            other_name = other.get('name', '').lower().strip()
            other_lat = other.get('latitude')
            other_lon = other.get('longitude')
            
            if not other_name or not other_lat or not other_lon:
                continue
            
            # Check name similarity
            name_similar = (name == other_name or 
                          name in other_name or 
                          other_name in name)
            
            # Check coordinate proximity (within ~100m)
            if lat and lon and other_lat and other_lon:
                lat_diff = abs(lat - other_lat)
                lon_diff = abs(lon - other_lon)
                coords_close = lat_diff < 0.001 and lon_diff < 0.001
                
                if name_similar and coords_close:
                    issues.append(f"Potential duplicate: ID {other['id']} ('{other.get('name')}')")
                    break  # Only report first duplicate found
        
        return issues
    
    def inspect_entry(self, entry: Dict, all_entries: List[Dict]) -> Dict:
        """Inspect a single entry for all issues"""
        entry_issues = []
        
        # Run all checks
        entry_issues.extend(self.check_critical_fields(entry))
        coord_issues = self.check_coordinates(entry)
        entry_issues.extend(coord_issues)
        
        url_issues = self.check_urls(entry)
        entry_issues.extend(url_issues)
        
        format_issues = self.check_formatting(entry)
        entry_issues.extend(format_issues)
        
        quality_issues = self.check_data_quality(entry)
        entry_issues.extend(quality_issues)
        
        duplicate_issues = self.check_duplicates(entry, all_entries)
        entry_issues.extend(duplicate_issues)
        
        return {
            'id': entry.get('id'),
            'name': entry.get('name'),
            'source': entry.get('source'),
            'issues': entry_issues,
            'issue_count': len(entry_issues),
            'summary': self._create_entry_summary(entry)
        }
    
    def _create_entry_summary(self, entry: Dict) -> Dict:
        """Create a summary of the entry"""
        return {
            'name': entry.get('name'),
            'type': entry.get('hut_type'),
            'country': entry.get('country'),
            'altitude': entry.get('altitude'),
            'coordinates': f"({entry.get('latitude')}, {entry.get('longitude')})" if entry.get('latitude') else None,
            'has_website': bool(entry.get('website')),
            'has_description': bool(entry.get('description')),
            'has_capacity': bool(entry.get('capacity')),
            'source': entry.get('source')
        }
    
    def generate_report(self, inspections: List[Dict]) -> Dict:
        """Generate comprehensive inspection report"""
        
        # Categorize issues
        issue_categories = {
            'Critical Data Missing': 0,
            'Coordinate Problems': 0,
            'URL Issues': 0,
            'Formatting Issues': 0,
            'Data Quality': 0,
            'Potential Duplicates': 0
        }
        
        all_issues = []
        entries_with_issues = 0
        
        for inspection in inspections:
            if inspection['issue_count'] > 0:
                entries_with_issues += 1
                
                for issue in inspection['issues']:
                    all_issues.append({
                        'entry_id': inspection['id'],
                        'entry_name': inspection['name'],
                        'issue': issue
                    })
                    
                    # Categorize
                    if 'Missing' in issue or 'missing' in issue:
                        issue_categories['Critical Data Missing'] += 1
                    elif 'latitude' in issue or 'longitude' in issue or 'Coordinates' in issue:
                        issue_categories['Coordinate Problems'] += 1
                    elif 'URL' in issue or 'website' in issue or 'url' in issue:
                        issue_categories['URL Issues'] += 1
                    elif 'format' in issue or 'whitespace' in issue or 'characters' in issue:
                        issue_categories['Formatting Issues'] += 1
                    elif 'duplicate' in issue or 'Duplicate' in issue:
                        issue_categories['Potential Duplicates'] += 1
                    else:
                        issue_categories['Data Quality'] += 1
        
        # Calculate statistics
        total_inspected = len(inspections)
        total_issues = sum(issue_categories.values())
        
        report = {
            'inspection_metadata': {
                'timestamp': datetime.now().isoformat(),
                'entries_inspected': total_inspected,
                'entries_with_issues': entries_with_issues,
                'entries_clean': total_inspected - entries_with_issues,
                'total_issues_found': total_issues,
                'avg_issues_per_entry': total_issues / total_inspected if total_inspected > 0 else 0
            },
            'issue_summary': issue_categories,
            'top_problematic_entries': sorted(
                inspections, 
                key=lambda x: x['issue_count'], 
                reverse=True
            )[:10],
            'all_issues': all_issues,
            'detailed_inspections': inspections
        }
        
        return report
    
    def print_report(self, report: Dict):
        """Print human-readable report"""
        print("\n" + "="*80)
        print("DATABASE QUALITY INSPECTION REPORT")
        print("="*80)
        
        meta = report['inspection_metadata']
        print(f"\nOverview:")
        print(f"  * Entries Inspected: {meta['entries_inspected']}")
        print(f"  * Entries with Issues: {meta['entries_with_issues']} ({meta['entries_with_issues']/meta['entries_inspected']*100:.1f}%)")
        print(f"  * Clean Entries: {meta['entries_clean']} ({meta['entries_clean']/meta['entries_inspected']*100:.1f}%)")
        print(f"  * Total Issues Found: {meta['total_issues_found']}")
        print(f"  * Average Issues per Entry: {meta['avg_issues_per_entry']:.2f}")
        
        print(f"\nIssue Breakdown:")
        for category, count in report['issue_summary'].items():
            if count > 0:
                percentage = (count / meta['total_issues_found']) * 100 if meta['total_issues_found'] > 0 else 0
                print(f"  * {category}: {count} ({percentage:.1f}%)")
        
        print(f"\nTop 10 Most Problematic Entries:")
        for i, entry in enumerate(report['top_problematic_entries'][:10], 1):
            if entry['issue_count'] > 0:
                # Handle Unicode characters safely
                name = entry['name'].encode('ascii', 'replace').decode('ascii')
                print(f"\n  {i}. {name} (ID: {entry['id']}, Source: {entry['source']})")
                print(f"     Issues found: {entry['issue_count']}")
                for issue in entry['issues'][:3]:  # Show first 3 issues
                    print(f"     - {issue}")
                if len(entry['issues']) > 3:
                    print(f"     ... and {len(entry['issues']) - 3} more")
        
        print("\n" + "="*80)
        print("RECOMMENDATIONS:")
        print("="*80)
        
        recommendations = []
        
        if report['issue_summary']['Critical Data Missing'] > 5:
            recommendations.append(
                "* HIGH PRIORITY: Many entries missing critical data (country, type, description).\n"
                "  -> Run data enrichment scripts or improve scraper data extraction."
            )
        
        if report['issue_summary']['Coordinate Problems'] > 5:
            recommendations.append(
                "* Coordinate validation needed - some entries have invalid or missing GPS data.\n"
                "  -> Verify scraper coordinate extraction logic."
            )
        
        if report['issue_summary']['URL Issues'] > 5:
            recommendations.append(
                "* URL formatting issues detected.\n"
                "  -> Run URL validation and cleanup script."
            )
        
        if report['issue_summary']['Potential Duplicates'] > 0:
            recommendations.append(
                f"* {report['issue_summary']['Potential Duplicates']} potential duplicates found.\n"
                "  -> Review and merge duplicate entries."
            )
        
        if report['issue_summary']['Data Quality'] > 10:
            recommendations.append(
                "* General data quality issues detected (low completeness, placeholder text).\n"
                "  -> Consider AI-assisted data enrichment or manual review."
            )
        
        if recommendations:
            for rec in recommendations:
                print(f"\n{rec}")
        else:
            print("\nOverall data quality looks good! Minor issues detected.")
        
        print("\n" + "="*80)


def main():
    # Set UTF-8 encoding for Windows console
    import sys
    if sys.platform == 'win32':
        import os
        os.system('chcp 65001 > nul')
    
    inspector = DatabaseInspector()
    
    print("Inspecting 50 random database entries...")
    print("This will check for:")
    print("  * Missing critical data")
    print("  * Invalid coordinates")
    print("  * URL issues")
    print("  * Formatting problems")
    print("  * Data quality issues")
    print("  * Potential duplicates")
    print("\nPlease wait...\n")
    
    # Get random entries
    entries = inspector.get_random_entries(50)
    
    # Inspect each entry
    inspections = []
    for entry in entries:
        inspection = inspector.inspect_entry(entry, entries)
        inspections.append(inspection)
    
    # Generate and print report
    report = inspector.generate_report(inspections)
    inspector.print_report(report)
    
    # Save detailed report to file
    output_file = "data/inspection_report.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\nDetailed report saved to: {output_file}")
    print("\nInspection complete!\n")


if __name__ == "__main__":
    main()

