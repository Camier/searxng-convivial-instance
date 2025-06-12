"""
SearXNG Authentication Middleware
Integrates JWT authentication with SearXNG without modifying core
"""

import os
import json
from functools import wraps
from flask import request, redirect, url_for, session, g
import requests
from urllib.parse import quote_plus

# Configuration
AUTH_SERVICE_URL = os.environ.get('AUTH_SERVICE_URL', 'http://auth-service:5000')
API_SERVICE_URL = os.environ.get('API_SERVICE_URL', 'http://api-service:5001')

class ConvivialAuthMiddleware:
    """Middleware to add authentication to SearXNG"""
    
    def __init__(self, app):
        self.app = app
        self.setup_routes()
        self.setup_before_request()
    
    def setup_routes(self):
        """Add authentication routes"""
        
        @self.app.route('/login', methods=['GET'])
        def login_page():
            """Render login page"""
            return '''
            <!DOCTYPE html>
            <html>
            <head>
                <title>Login - Digital Salon</title>
                <link rel="stylesheet" href="/static/themes/simple/css/searxng.min.css">
                <style>
                    .login-container {
                        max-width: 400px;
                        margin: 100px auto;
                        padding: 20px;
                        background: #f9f9f9;
                        border-radius: 10px;
                        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    }
                    .login-form input {
                        width: 100%;
                        padding: 10px;
                        margin: 10px 0;
                        border: 1px solid #ddd;
                        border-radius: 5px;
                    }
                    .login-form button {
                        width: 100%;
                        padding: 12px;
                        background: #7fb069;
                        color: white;
                        border: none;
                        border-radius: 5px;
                        cursor: pointer;
                    }
                    .error {
                        color: #e74c3c;
                        margin: 10px 0;
                    }
                </style>
            </head>
            <body>
                <div class="login-container">
                    <h1>🌟 Welcome to the Digital Salon</h1>
                    <p>A convivial search experience for friends</p>
                    <form class="login-form" method="POST" action="/login">
                        <input type="text" name="username" placeholder="Username" required>
                        <input type="password" name="password" placeholder="Password" required>
                        <button type="submit">Enter the Salon</button>
                    </form>
                    <p style="text-align: center; margin-top: 20px;">
                        <a href="/register">Join as a new friend</a>
                    </p>
                </div>
            </body>
            </html>
            '''
        
        @self.app.route('/login', methods=['POST'])
        def login():
            """Handle login"""
            username = request.form.get('username')
            password = request.form.get('password')
            
            # Call auth service
            try:
                response = requests.post(f'{AUTH_SERVICE_URL}/auth/login', json={
                    'username': username,
                    'password': password
                })
                
                if response.status_code == 200:
                    data = response.json()
                    session['access_token'] = data['access_token']
                    session['refresh_token'] = data['refresh_token']
                    session['user'] = data['user']
                    
                    # Redirect to search
                    return redirect(url_for('index'))
                else:
                    return redirect(url_for('login_page') + '?error=invalid_credentials')
                    
            except Exception as e:
                return redirect(url_for('login_page') + '?error=service_unavailable')
        
        @self.app.route('/register', methods=['GET'])
        def register_page():
            """Render registration page"""
            return '''
            <!DOCTYPE html>
            <html>
            <head>
                <title>Join - Digital Salon</title>
                <link rel="stylesheet" href="/static/themes/simple/css/searxng.min.css">
                <style>
                    .register-container {
                        max-width: 400px;
                        margin: 50px auto;
                        padding: 20px;
                        background: #f9f9f9;
                        border-radius: 10px;
                        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    }
                    .register-form input {
                        width: 100%;
                        padding: 10px;
                        margin: 10px 0;
                        border: 1px solid #ddd;
                        border-radius: 5px;
                    }
                    .register-form button {
                        width: 100%;
                        padding: 12px;
                        background: #7fb069;
                        color: white;
                        border: none;
                        border-radius: 5px;
                        cursor: pointer;
                    }
                    .info {
                        background: #e8f4f8;
                        padding: 15px;
                        border-radius: 5px;
                        margin: 20px 0;
                    }
                </style>
            </head>
            <body>
                <div class="register-container">
                    <h1>🌱 Join the Digital Salon</h1>
                    <div class="info">
                        <p><strong>Note:</strong> This is a small convivial space limited to 3 friends.</p>
                        <p>Registration requires approval from existing members.</p>
                    </div>
                    <form class="register-form" method="POST" action="/register">
                        <input type="text" name="username" placeholder="Choose a username" pattern="[a-zA-Z0-9_]+" required>
                        <input type="email" name="email" placeholder="Email address" required>
                        <input type="password" name="password" placeholder="Password (min 8 chars)" minlength="8" required>
                        <input type="text" name="display_name" placeholder="Display name (optional)">
                        <button type="submit">Request to Join</button>
                    </form>
                    <p style="text-align: center; margin-top: 20px;">
                        <a href="/login">Already a member? Login</a>
                    </p>
                </div>
            </body>
            </html>
            '''
        
        @self.app.route('/register', methods=['POST'])
        def register():
            """Handle registration"""
            data = {
                'username': request.form.get('username'),
                'email': request.form.get('email'),
                'password': request.form.get('password'),
                'display_name': request.form.get('display_name')
            }
            
            try:
                response = requests.post(f'{AUTH_SERVICE_URL}/auth/register', json=data)
                
                if response.status_code == 201:
                    # Auto-login after registration
                    data = response.json()
                    session['access_token'] = data['access_token']
                    session['refresh_token'] = data['refresh_token']
                    session['user'] = data['user']
                    
                    return redirect(url_for('index'))
                elif response.status_code == 403:
                    return redirect(url_for('register_page') + '?error=friend_limit')
                else:
                    return redirect(url_for('register_page') + '?error=registration_failed')
                    
            except Exception as e:
                return redirect(url_for('register_page') + '?error=service_unavailable')
        
        @self.app.route('/logout', methods=['GET', 'POST'])
        def logout():
            """Handle logout"""
            token = session.get('access_token')
            if token:
                try:
                    requests.post(f'{AUTH_SERVICE_URL}/auth/logout', 
                                headers={'Authorization': f'Bearer {token}'})
                except:
                    pass
            
            session.clear()
            return redirect(url_for('login_page'))
    
    def setup_before_request(self):
        """Setup request authentication"""
        
        @self.app.before_request
        def require_login():
            """Check if user is authenticated"""
            # Skip auth for static files and auth endpoints
            if request.path.startswith('/static') or \
               request.path.startswith('/login') or \
               request.path.startswith('/register') or \
               request.path == '/health':
                return
            
            # Check for valid session
            token = session.get('access_token')
            if not token:
                return redirect(url_for('login_page'))
            
            # Verify token
            try:
                response = requests.get(f'{AUTH_SERVICE_URL}/auth/verify',
                                      headers={'Authorization': f'Bearer {token}'})
                
                if response.status_code == 200:
                    g.user = session.get('user')
                    g.token = token
                else:
                    # Token invalid, clear session
                    session.clear()
                    return redirect(url_for('login_page'))
                    
            except Exception as e:
                # Auth service unavailable, allow through for now
                g.user = session.get('user', {'username': 'anonymous'})
                g.token = None
    
    def inject_user_context(self):
        """Inject user info into templates"""
        
        @self.app.context_processor
        def inject_user():
            return {
                'current_user': g.get('user'),
                'is_authenticated': g.get('token') is not None
            }

def init_middleware(app):
    """Initialize the authentication middleware"""
    return ConvivialAuthMiddleware(app)