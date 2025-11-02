"""Quick statistics check"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database import MountainHutsDatabase

db = MountainHutsDatabase()
stats = db.get_statistics()

print(f"\n=== DATABASE STATISTICS ===")
print(f"Total huts: {stats['total_huts']}")

print(f"\nBy source:")
for s in stats['by_source']:
    print(f"  {s['source']}: {s['count']} huts")

print(f"\nBy country (top 15):")
for c in stats['by_country'][:15]:
    print(f"  {c['country']}: {c['count']} huts")

print(f"\nBy type:")
for t in stats['by_type']:
    print(f"  {t['type']}: {t['count']} huts")
