"""
Initialize authentication system
Run this before starting the API server for the first time
"""

from auth import AuthDatabase
from database import MountainHutsDatabase

print("Initializing Lost in the Alps Authentication System...")
print("=" * 60)

# Initialize main database if needed
print("\n1. Checking main database...")
db = MountainHutsDatabase()
db.init_database()
print("   ✓ Main database ready")

# Initialize authentication tables
print("\n2. Initializing authentication tables...")
auth = AuthDatabase()
print("   ✓ Users table created")
print("   ✓ Favorites table created")

print("\n" + "=" * 60)
print("✅ Authentication system ready!")
print("\nNext steps:")
print("  1. Start the API server: python api.py")
print("  2. Open website/login.html in your browser")
print("  3. Register a new account")
print("  4. Start adding your favorite huts!")
