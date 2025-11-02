"""
Authentication and user management system for Lost in the Alps
Handles user registration, login, and favorite huts bookmarking
"""

import sqlite3
import hashlib
import secrets
from typing import Optional, List, Dict
from datetime import datetime
from pathlib import Path


class AuthDatabase:
    """Handle user authentication and favorites"""
    
    def __init__(self, db_path: str = "data/mountain_huts.db"):
        self.db_path = db_path
        self.init_auth_tables()
    
    def init_auth_tables(self):
        """Create user and favorites tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        """)
        
        # Favorite huts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_favorites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                hut_id INTEGER NOT NULL,
                notes TEXT,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (hut_id) REFERENCES mountain_huts(id) ON DELETE CASCADE,
                UNIQUE(user_id, hut_id)
            )
        """)
        
        # Create indexes
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_user_email ON users(email)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_favorites_user ON user_favorites(user_id)
        """)
        
        conn.commit()
        conn.close()
    
    def _hash_password(self, password: str, salt: str) -> str:
        """Hash password with salt using SHA-256"""
        return hashlib.sha256((password + salt).encode()).hexdigest()
    
    def register_user(self, email: str, password: str) -> Dict[str, any]:
        """
        Register a new user
        Returns: {'success': bool, 'message': str, 'user_id': int}
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Check if user exists
            cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
            if cursor.fetchone():
                return {
                    'success': False,
                    'message': 'Email already registered'
                }
            
            # Generate salt and hash password
            salt = secrets.token_hex(32)
            password_hash = self._hash_password(password, salt)
            
            # Insert user
            cursor.execute("""
                INSERT INTO users (email, password_hash, salt)
                VALUES (?, ?, ?)
            """, (email, password_hash, salt))
            
            user_id = cursor.lastrowid
            conn.commit()
            
            return {
                'success': True,
                'message': 'Registration successful',
                'user_id': user_id
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Registration error: {str(e)}'
            }
        finally:
            conn.close()
    
    def login_user(self, email: str, password: str) -> Dict[str, any]:
        """
        Authenticate user login
        Returns: {'success': bool, 'message': str, 'user_id': int, 'session_token': str}
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Get user
            cursor.execute("""
                SELECT id, password_hash, salt FROM users WHERE email = ?
            """, (email,))
            
            result = cursor.fetchone()
            if not result:
                return {
                    'success': False,
                    'message': 'Invalid email or password'
                }
            
            user_id, stored_hash, salt = result
            
            # Verify password
            password_hash = self._hash_password(password, salt)
            if password_hash != stored_hash:
                return {
                    'success': False,
                    'message': 'Invalid email or password'
                }
            
            # Update last login
            cursor.execute("""
                UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?
            """, (user_id,))
            conn.commit()
            
            # Generate session token
            session_token = secrets.token_urlsafe(32)
            
            return {
                'success': True,
                'message': 'Login successful',
                'user_id': user_id,
                'session_token': session_token,
                'email': email
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Login error: {str(e)}'
            }
        finally:
            conn.close()
    
    def add_favorite(self, user_id: int, hut_id: int, notes: str = "") -> Dict[str, any]:
        """
        Add a hut to user's favorites
        Returns: {'success': bool, 'message': str}
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO user_favorites (user_id, hut_id, notes)
                VALUES (?, ?, ?)
            """, (user_id, hut_id, notes))
            
            conn.commit()
            
            return {
                'success': True,
                'message': 'Hut added to favorites'
            }
            
        except sqlite3.IntegrityError:
            return {
                'success': False,
                'message': 'Hut already in favorites'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error adding favorite: {str(e)}'
            }
        finally:
            conn.close()
    
    def remove_favorite(self, user_id: int, hut_id: int) -> Dict[str, any]:
        """
        Remove a hut from user's favorites
        Returns: {'success': bool, 'message': str}
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                DELETE FROM user_favorites 
                WHERE user_id = ? AND hut_id = ?
            """, (user_id, hut_id))
            
            if cursor.rowcount == 0:
                return {
                    'success': False,
                    'message': 'Hut not in favorites'
                }
            
            conn.commit()
            
            return {
                'success': True,
                'message': 'Hut removed from favorites'
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error removing favorite: {str(e)}'
            }
        finally:
            conn.close()
    
    def get_user_favorites(self, user_id: int) -> List[Dict]:
        """
        Get all favorite huts for a user
        Returns list of huts with details
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                h.id, h.name, h.latitude, h.longitude, h.altitude,
                h.country, h.website, h.source, h.description,
                f.notes, f.added_at
            FROM user_favorites f
            JOIN mountain_huts h ON f.hut_id = h.id
            WHERE f.user_id = ?
            ORDER BY f.added_at DESC
        """, (user_id,))
        
        favorites = []
        for row in cursor.fetchall():
            favorites.append({
                'id': row[0],
                'name': row[1],
                'latitude': row[2],
                'longitude': row[3],
                'altitude': row[4],
                'country': row[5],
                'website': row[6],
                'source': row[7],
                'description': row[8],
                'notes': row[9],
                'added_at': row[10]
            })
        
        conn.close()
        return favorites
    
    def is_favorite(self, user_id: int, hut_id: int) -> bool:
        """Check if a hut is in user's favorites"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 1 FROM user_favorites 
            WHERE user_id = ? AND hut_id = ?
        """, (user_id, hut_id))
        
        result = cursor.fetchone() is not None
        conn.close()
        return result


# Example usage
if __name__ == "__main__":
    auth = AuthDatabase()
    
    # Test registration
    result = auth.register_user("test@example.com", "securepassword123")
    print(f"Registration: {result}")
    
    # Test login
    result = auth.login_user("test@example.com", "securepassword123")
    print(f"Login: {result}")
    
    if result['success']:
        user_id = result['user_id']
        
        # Test add favorite (hut_id 1 must exist in mountain_huts table)
        result = auth.add_favorite(user_id, 1, "Beautiful mountain refuge!")
        print(f"Add favorite: {result}")
        
        # Test get favorites
        favorites = auth.get_user_favorites(user_id)
        print(f"Favorites: {len(favorites)} huts")
        for fav in favorites:
            print(f"  - {fav['name']} ({fav['country']})")
