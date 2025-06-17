from flask import Flask, request, jsonify, redirect, url_for, session
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
import sqlite3
import os
from functools import wraps
import requests
from urllib.parse import urlencode
import secrets

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-change-this')
CORS(app, origins=["http://localhost:3000"], supports_credentials=True)

# Configuration
JWT_SECRET = os.getenv('JWT_SECRET', 'your-jwt-secret-change-this')
JWT_ALGORITHM = 'HS256'

# OAuth Configuration
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID', 'your-google-client-id')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET', 'your-google-client-secret')
GOOGLE_REDIRECT_URI = 'http://localhost:8000/api/auth/google/callback'

MICROSOFT_CLIENT_ID = os.getenv('MICROSOFT_CLIENT_ID', 'your-microsoft-client-id')
MICROSOFT_CLIENT_SECRET = os.getenv('MICROSOFT_CLIENT_SECRET', 'your-microsoft-client-secret')
MICROSOFT_REDIRECT_URI = 'http://localhost:8000/api/auth/microsoft/callback'

# Database setup
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            name TEXT,
            password_hash TEXT,
            provider TEXT DEFAULT 'email',
            provider_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Token management
def generate_token(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def verify_token(token):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload['user_id']
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

# Authentication decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        
        if auth_header:
            try:
                token = auth_header.split(' ')[1]
            except IndexError:
                return jsonify({'error': 'Invalid token format'}), 401
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        user_id = verify_token(token)
        if user_id is None:
            return jsonify({'error': 'Token is invalid or expired'}), 401
        
        # Get user from database
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        user = c.fetchone()
        conn.close()
        
        if not user:
            return jsonify({'error': 'User not found'}), 401
        
        # Pass user data to the route
        return f(user, *args, **kwargs)
    
    return decorated

# Helper functions
def get_user_by_email(email):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE email = ?', (email,))
    user = c.fetchone()
    conn.close()
    return user

def create_user(email, name=None, password=None, provider='email', provider_id=None):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    
    password_hash = generate_password_hash(password) if password else None
    
    try:
        c.execute('''
            INSERT INTO users (email, name, password_hash, provider, provider_id)
            VALUES (?, ?, ?, ?, ?)
        ''', (email, name, password_hash, provider, provider_id))
        user_id = c.lastrowid
        conn.commit()
        conn.close()
        return user_id
    except sqlite3.IntegrityError:
        conn.close()
        return None

# Routes
@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400
    
    # Check if user already exists
    if get_user_by_email(email):
        return jsonify({'error': 'User already exists'}), 400
    
    # Create new user
    user_id = create_user(email, password=password)
    if not user_id:
        return jsonify({'error': 'Failed to create user'}), 500
    
    # Generate token
    token = generate_token(user_id)
    
    return jsonify({
        'message': 'User created successfully',
        'token': token,
        'user': {
            'id': user_id,
            'email': email,
            'provider': 'email'
        }
    }), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400
    
    # Get user from database
    user = get_user_by_email(email)
    if not user:
        return jsonify({'error': 'Invalid email or password'}), 401
    
    # Check password
    if not user[3] or not check_password_hash(user[3], password):
        return jsonify({'error': 'Invalid email or password'}), 401
    
    # Generate token
    token = generate_token(user[0])
    
    return jsonify({
        'message': 'Login successful',
        'token': token,
        'user': {
            'id': user[0],
            'email': user[1],
            'name': user[2],
            'provider': user[4]
        }
    })

@app.route('/api/profile', methods=['GET'])
@token_required
def profile(user):
    return jsonify({
        'id': user[0],
        'email': user[1],
        'name': user[2],
        'provider': user[4]
    })

@app.route('/api/logout', methods=['POST'])
@token_required
def logout(user):
    # In a real application, you might want to blacklist the token
    return jsonify({'message': 'Logged out successfully'})

# Google OAuth
@app.route('/api/auth/google')
def google_auth():
    # Generate state for CSRF protection
    state = secrets.token_urlsafe(32)
    session['oauth_state'] = state
    
    params = {
        'client_id': GOOGLE_CLIENT_ID,
        'redirect_uri': GOOGLE_REDIRECT_URI,
        'scope': 'openid email profile',
        'response_type': 'code',
        'state': state
    }
    
    auth_url = 'https://accounts.google.com/o/oauth2/auth?' + urlencode(params)
    return redirect(auth_url)

@app.route('/api/auth/google/callback')
def google_callback():
    # Verify state parameter
    if request.args.get('state') != session.get('oauth_state'):
        return redirect('http://localhost:3000?error=invalid_state')
    
    code = request.args.get('code')
    if not code:
        return redirect('http://localhost:3000?error=no_code')
    
    # Exchange code for token
    token_data = {
        'client_id': GOOGLE_CLIENT_ID,
        'client_secret': GOOGLE_CLIENT_SECRET,
        'code': code,
        'grant_type': 'authorization_code',
        'redirect_uri': GOOGLE_REDIRECT_URI
    }
    
    token_response = requests.post('https://oauth2.googleapis.com/token', data=token_data)
    token_json = token_response.json()
    
    if 'access_token' not in token_json:
        return redirect('http://localhost:3000?error=token_error')
    
    # Get user info
    headers = {'Authorization': f'Bearer {token_json["access_token"]}'}
    user_response = requests.get('https://www.googleapis.com/oauth2/v2/userinfo', headers=headers)
    user_info = user_response.json()
    
    email = user_info.get('email')
    name = user_info.get('name')
    provider_id = user_info.get('id')
    
    # Check if user exists
    user = get_user_by_email(email)
    if user:
        user_id = user[0]
    else:
        # Create new user
        user_id = create_user(email, name=name, provider='google', provider_id=provider_id)
        if not user_id:
            return redirect('http://localhost:3000?error=user_creation_failed')
    
    # Generate JWT token
    jwt_token = generate_token(user_id)
    
    # Redirect to frontend with token
    return redirect(f'http://localhost:3000?token={jwt_token}')

# Microsoft OAuth
@app.route('/api/auth/microsoft')
def microsoft_auth():
    # Generate state for CSRF protection
    state = secrets.token_urlsafe(32)
    session['oauth_state'] = state
    
    params = {
        'client_id': MICROSOFT_CLIENT_ID,
        'response_type': 'code',
        'redirect_uri': MICROSOFT_REDIRECT_URI,
        'scope': 'openid email profile',
        'state': state
    }
    
    auth_url = 'https://login.microsoftonline.com/common/oauth2/v2.0/authorize?' + urlencode(params)
    return redirect(auth_url)

@app.route('/api/auth/microsoft/callback')
def microsoft_callback():
    # Verify state parameter
    if request.args.get('state') != session.get('oauth_state'):
        return redirect('http://localhost:3000?error=invalid_state')
    
    code = request.args.get('code')
    if not code:
        return redirect('http://localhost:3000?error=no_code')
    
    # Exchange code for token
    token_data = {
        'client_id': MICROSOFT_CLIENT_ID,
        'client_secret': MICROSOFT_CLIENT_SECRET,
        'code': code,
        'grant_type': 'authorization_code',
        'redirect_uri': MICROSOFT_REDIRECT_URI
    }
    
    token_response = requests.post('https://login.microsoftonline.com/common/oauth2/v2.0/token', data=token_data)
    token_json = token_response.json()
    
    if 'access_token' not in token_json:
        return redirect('http://localhost:3000?error=token_error')
    
    # Get user info
    headers = {'Authorization': f'Bearer {token_json["access_token"]}'}
    user_response = requests.get('https://graph.microsoft.com/v1.0/me', headers=headers)
    user_info = user_response.json()
    
    email = user_info.get('mail') or user_info.get('userPrincipalName')
    name = user_info.get('displayName')
    provider_id = user_info.get('id')
    
    # Check if user exists
    user = get_user_by_email(email)
    if user:
        user_id = user[0]
    else:
        # Create new user
        user_id = create_user(email, name=name, provider='microsoft', provider_id=provider_id)
        if not user_id:
            return redirect('http://localhost:3000?error=user_creation_failed')
    
    # Generate JWT token
    jwt_token = generate_token(user_id)
    
    # Redirect to frontend with token
    return redirect(f'http://localhost:3000?token={jwt_token}')

@app.route('/api/health')
def health_check():
    return jsonify({'status': 'healthy', 'message': 'Backend is running'})

if __name__ == '__main__':
    # Initialize database
    init_db()
    
    # Run the app
    app.run(debug=True, port=8000, host='0.0.0.0')
        