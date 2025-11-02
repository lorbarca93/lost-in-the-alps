"""
Simple Flask API for authentication and favorites management
Run with: python api.py
"""

from flask import Flask, request, jsonify, session
from flask_cors import CORS
from auth import AuthDatabase
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)
CORS(app)  # Enable CORS for frontend requests

auth_db = AuthDatabase()


@app.route('/api/register', methods=['POST'])
def register():
    """Register a new user"""
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'success': False, 'message': 'Email and password required'}), 400
    
    result = auth_db.register_user(email, password)
    
    if result['success']:
        session['user_id'] = result['user_id']
        session['email'] = email
        return jsonify(result), 201
    else:
        return jsonify(result), 400


@app.route('/api/login', methods=['POST'])
def login():
    """Login user"""
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'success': False, 'message': 'Email and password required'}), 400
    
    result = auth_db.login_user(email, password)
    
    if result['success']:
        session['user_id'] = result['user_id']
        session['email'] = email
        return jsonify(result), 200
    else:
        return jsonify(result), 401


@app.route('/api/logout', methods=['POST'])
def logout():
    """Logout user"""
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out successfully'}), 200


@app.route('/api/favorites', methods=['GET'])
def get_favorites():
    """Get user's favorite huts"""
    user_id = session.get('user_id')
    
    if not user_id:
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401
    
    favorites = auth_db.get_user_favorites(user_id)
    return jsonify({'success': True, 'favorites': favorites}), 200


@app.route('/api/favorites/<int:hut_id>', methods=['POST'])
def add_favorite(hut_id):
    """Add hut to favorites"""
    user_id = session.get('user_id')
    
    if not user_id:
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401
    
    data = request.get_json() or {}
    notes = data.get('notes', '')
    
    result = auth_db.add_favorite(user_id, hut_id, notes)
    
    if result['success']:
        return jsonify(result), 201
    else:
        return jsonify(result), 400


@app.route('/api/favorites/<int:hut_id>', methods=['DELETE'])
def remove_favorite(hut_id):
    """Remove hut from favorites"""
    user_id = session.get('user_id')
    
    if not user_id:
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401
    
    result = auth_db.remove_favorite(user_id, hut_id)
    
    if result['success']:
        return jsonify(result), 200
    else:
        return jsonify(result), 404


@app.route('/api/favorites/<int:hut_id>/check', methods=['GET'])
def check_favorite(hut_id):
    """Check if hut is favorited"""
    user_id = session.get('user_id')
    
    if not user_id:
        return jsonify({'is_favorite': False}), 200
    
    is_fav = auth_db.is_favorite(user_id, hut_id)
    return jsonify({'is_favorite': is_fav}), 200


@app.route('/api/user', methods=['GET'])
def get_user():
    """Get current user info"""
    user_id = session.get('user_id')
    email = session.get('email')
    
    if not user_id:
        return jsonify({'authenticated': False}), 200
    
    return jsonify({
        'authenticated': True,
        'user_id': user_id,
        'email': email
    }), 200


if __name__ == '__main__':
    print("Starting Lost in the Alps API server...")
    print("API available at: http://localhost:5000")
    print("\nEndpoints:")
    print("  POST /api/register - Register new user")
    print("  POST /api/login - Login user")
    print("  POST /api/logout - Logout user")
    print("  GET  /api/user - Get current user")
    print("  GET  /api/favorites - Get user favorites")
    print("  POST /api/favorites/<hut_id> - Add favorite")
    print("  DELETE /api/favorites/<hut_id> - Remove favorite")
    print("  GET  /api/favorites/<hut_id>/check - Check if favorited")
    
    app.run(debug=False, use_reloader=False, port=5000)
