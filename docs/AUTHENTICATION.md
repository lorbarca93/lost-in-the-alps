# Authentication & Favorites System

This system allows users to create accounts, log in, and bookmark their favorite mountain huts.

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install Flask and Flask-CORS for the API server.

### 2. Initialize Database

The authentication tables will be created automatically when you first run the API server.

### 3. Start the API Server

```bash
python api.py
```

The server will start at `http://localhost:5000`

### 4. Open the Website

Open `website/login.html` in your browser or navigate from the homepage.

## Features

### User Authentication

- **Register**: Create a new account with email and password
- **Login**: Authenticate with your credentials
- **Logout**: End your session
- **Session Management**: Sessions are maintained server-side

### Favorites System

- **Add Favorites**: Bookmark huts from the interactive map
- **View Favorites**: See all your saved huts in the dashboard
- **Remove Favorites**: Remove huts from your favorites list
- **Add Notes**: Attach personal notes to each favorite hut

## API Endpoints

### Authentication

- `POST /api/register` - Register new user

  ```json
  {
    "email": "user@example.com",
    "password": "securepassword"
  }
  ```

- `POST /api/login` - Login user

  ```json
  {
    "email": "user@example.com",
    "password": "securepassword"
  }
  ```

- `POST /api/logout` - Logout current user

- `GET /api/user` - Get current user info

### Favorites

- `GET /api/favorites` - Get all user favorites

- `POST /api/favorites/<hut_id>` - Add hut to favorites

  ```json
  {
    "notes": "Beautiful view, visited in summer 2024"
  }
  ```

- `DELETE /api/favorites/<hut_id>` - Remove hut from favorites

- `GET /api/favorites/<hut_id>/check` - Check if hut is favorited

## Security Features

- Password hashing with SHA-256 and random salt
- Server-side session management
- CORS protection
- SQL injection prevention with parameterized queries

## Database Schema

### users table

```sql
- id: INTEGER PRIMARY KEY
- email: TEXT UNIQUE
- password_hash: TEXT
- salt: TEXT
- created_at: TIMESTAMP
- last_login: TIMESTAMP
```

### user_favorites table

```sql
- id: INTEGER PRIMARY KEY
- user_id: INTEGER (FK to users)
- hut_id: INTEGER (FK to mountain_huts)
- notes: TEXT
- added_at: TIMESTAMP
```

## Usage Example

### Testing from Command Line

```python
from auth import AuthDatabase

auth = AuthDatabase()

# Register a user
result = auth.register_user("test@example.com", "mypassword")
print(result)  # {'success': True, 'message': 'Registration successful', 'user_id': 1}

# Login
result = auth.login_user("test@example.com", "mypassword")
print(result)  # {'success': True, 'message': 'Login successful', 'user_id': 1, ...}

# Add favorite
result = auth.add_favorite(user_id=1, hut_id=42, notes="Amazing place!")
print(result)  # {'success': True, 'message': 'Hut added to favorites'}

# Get favorites
favorites = auth.get_user_favorites(user_id=1)
print(f"Found {len(favorites)} favorites")
```

## Web Pages

- **login.html** - Login and registration page
- **favorites.html** - User dashboard showing favorite huts
- **map.html** - Interactive map (to be updated with favorite buttons)

## Next Steps

To fully integrate the favorites system:

1. Update `map.html` to add favorite/unfavorite buttons to hut popups
2. Add visual indicators for favorited huts on the map
3. Allow filtering the map to show only favorites
4. Add user profile page
5. Implement password reset functionality
6. Add email verification (optional)

## Troubleshooting

**API Connection Error**

Make sure the API server is running:

```bash
python api.py
```

**Database Error**

Delete and recreate the database:

```bash
rm data/mountain_huts.db
python database.py  # Reinitialize
python api.py  # This will create auth tables
```

**CORS Issues**

The Flask-CORS package is configured to allow all origins in development. For production, configure specific allowed origins in `api.py`.
