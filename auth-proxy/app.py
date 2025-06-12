"""
Authentication Proxy for SearXNG
Sits in front of SearXNG and handles authentication
"""

import os
import jwt
import redis
from datetime import datetime
from flask import Flask, request, redirect, session, render_template_string, make_response
from flask_session import Session
import requests

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_REDIS'] = redis.Redis(
    host=os.environ.get('REDIS_HOST', 'redis-cache'),
    port=6379
)
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = os.environ.get('ENV') == 'production'
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Initialize session
Session(app)

# Service URLs
SEARXNG_URL = os.environ.get('SEARXNG_URL', 'http://searxng:8080')
AUTH_SERVICE_URL = os.environ.get('AUTH_SERVICE_URL', 'http://auth-service:5000')
API_SERVICE_URL = os.environ.get('API_SERVICE_URL', 'http://api-service:5001')
JWT_SECRET = os.environ.get('JWT_SECRET', 'dev-jwt-secret')

# Login page template
LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Digital Salon - Login</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0;
        }
        .container {
            background: white;
            padding: 2rem;
            border-radius: 12px;
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
            width: 100%;
            max-width: 400px;
        }
        h1 {
            text-align: center;
            color: #1a202c;
            margin-bottom: 0.5rem;
        }
        .subtitle {
            text-align: center;
            color: #718096;
            margin-bottom: 2rem;
        }
        .form-group {
            margin-bottom: 1.5rem;
        }
        label {
            display: block;
            color: #4a5568;
            margin-bottom: 0.5rem;
            font-weight: 500;
        }
        input {
            width: 100%;
            padding: 0.75rem;
            border: 1px solid #e2e8f0;
            border-radius: 6px;
            font-size: 1rem;
            transition: border-color 0.2s;
        }
        input:focus {
            outline: none;
            border-color: #667eea;
        }
        button {
            width: 100%;
            padding: 0.75rem;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 6px;
            font-size: 1rem;
            font-weight: 500;
            cursor: pointer;
            transition: background 0.2s;
        }
        button:hover {
            background: #5a67d8;
        }
        .toggle-form {
            text-align: center;
            margin-top: 1.5rem;
            color: #718096;
        }
        .toggle-form a {
            color: #667eea;
            text-decoration: none;
        }
        .error {
            background: #fed7d7;
            color: #c53030;
            padding: 0.75rem;
            border-radius: 6px;
            margin-bottom: 1rem;
        }
        .success {
            background: #c6f6d5;
            color: #2f855a;
            padding: 0.75rem;
            border-radius: 6px;
            margin-bottom: 1rem;
        }
        .friend-count {
            text-align: center;
            color: #718096;
            font-size: 0.875rem;
            margin-top: 1rem;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🌟 Digital Salon</h1>
        <p class="subtitle">{{ 'Join' if is_register else 'Welcome back to' }} your private search circle</p>
        
        {% if error %}
            <div class="error">{{ error }}</div>
        {% endif %}
        
        {% if success %}
            <div class="success">{{ success }}</div>
        {% endif %}
        
        <form method="POST">
            {% if is_register %}
                <div class="form-group">
                    <label for="email">Email</label>
                    <input type="email" id="email" name="email" required>
                </div>
            {% endif %}
            
            <div class="form-group">
                <label for="username">Username</label>
                <input type="text" id="username" name="username" required>
            </div>
            
            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" id="password" name="password" required>
            </div>
            
            {% if is_register %}
                <div class="form-group">
                    <label for="display_name">Display Name (optional)</label>
                    <input type="text" id="display_name" name="display_name">
                </div>
            {% endif %}
            
            <button type="submit">{{ 'Create Account' if is_register else 'Login' }}</button>
        </form>
        
        <div class="toggle-form">
            {% if is_register %}
                Already have an account? <a href="/login">Login</a>
            {% else %}
                New to the salon? <a href="/register">Register</a>
            {% endif %}
        </div>
        
        {% if friend_count is defined %}
            <div class="friend-count">
                {{ friend_count }} of 3 friend slots used
            </div>
        {% endif %}
    </div>
    
    <!-- Include the convivial API -->
    <script src="/static/js/convivial-api.js"></script>
</body>
</html>
"""

def verify_token(token):
    """Verify JWT token with auth service"""
    try:
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get(f"{AUTH_SERVICE_URL}/auth/verify", headers=headers, timeout=5)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def get_friend_count():
    """Get current friend count"""
    try:
        # Create a temporary token for internal use
        response = requests.get(f"{AUTH_SERVICE_URL}/auth/users", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get('count', 0)
    except:
        pass
    return 0

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Authenticate with auth service
        try:
            response = requests.post(
                f"{AUTH_SERVICE_URL}/auth/login",
                json={'username': username, 'password': password},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                session['access_token'] = data['access_token']
                session['refresh_token'] = data['refresh_token']
                session['user'] = data['user']
                
                # Redirect to original URL or home
                next_url = request.args.get('next', '/')
                return redirect(next_url)
            else:
                error = "Invalid username or password"
        except Exception as e:
            error = "Authentication service unavailable"
            
        return render_template_string(LOGIN_TEMPLATE, is_register=False, error=error)
    
    return render_template_string(LOGIN_TEMPLATE, is_register=False)

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Registration page"""
    friend_count = get_friend_count()
    
    if friend_count >= 3:
        return render_template_string(
            LOGIN_TEMPLATE, 
            is_register=False, 
            error="Friend limit reached. This salon has 3 members.",
            friend_count=friend_count
        )
    
    if request.method == 'POST':
        data = {
            'username': request.form.get('username'),
            'email': request.form.get('email'),
            'password': request.form.get('password'),
            'display_name': request.form.get('display_name') or request.form.get('username')
        }
        
        try:
            response = requests.post(
                f"{AUTH_SERVICE_URL}/auth/register",
                json=data,
                timeout=10
            )
            
            if response.status_code == 201:
                result = response.json()
                session['access_token'] = result['access_token']
                session['refresh_token'] = result['refresh_token']
                session['user'] = result['user']
                
                return redirect('/')
            else:
                error = response.json().get('message', 'Registration failed')
        except Exception as e:
            error = "Registration service unavailable"
            
        return render_template_string(
            LOGIN_TEMPLATE, 
            is_register=True, 
            error=error,
            friend_count=friend_count
        )
    
    return render_template_string(
        LOGIN_TEMPLATE, 
        is_register=True,
        friend_count=friend_count
    )

@app.route('/logout')
def logout():
    """Logout user"""
    token = session.get('access_token')
    if token:
        try:
            headers = {'Authorization': f'Bearer {token}'}
            requests.post(f"{AUTH_SERVICE_URL}/auth/logout", headers=headers, timeout=5)
        except:
            pass
    
    session.clear()
    return redirect('/login')

@app.route('/static/js/convivial-api.js')
def serve_convivial_api():
    """Serve the convivial API JavaScript"""
    try:
        with open('/app/static/js/convivial-api.js', 'r') as f:
            content = f.read()
        return content, 200, {'Content-Type': 'application/javascript'}
    except:
        return "console.error('Convivial API not found');", 404

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def proxy(path):
    """Proxy requests to SearXNG with authentication"""
    # Check if user is authenticated
    token = session.get('access_token')
    if not token:
        return redirect(f'/login?next={request.path}')
    
    # Verify token
    user_info = verify_token(token)
    if not user_info:
        session.clear()
        return redirect(f'/login?next={request.path}')
    
    # Proxy the request to SearXNG
    url = f"{SEARXNG_URL}/{path}"
    
    # Forward request
    try:
        # Prepare headers
        headers = dict(request.headers)
        headers['X-User-Id'] = user_info['user_id']
        headers['X-Username'] = user_info['claims']['username']
        headers['X-User-Role'] = user_info['claims']['role']
        
        # Remove hop-by-hop headers
        for header in ['Host', 'Connection', 'Content-Length', 'Transfer-Encoding']:
            headers.pop(header, None)
        
        # Make request
        if request.method == 'GET':
            resp = requests.get(
                url,
                params=request.args,
                headers=headers,
                stream=True,
                timeout=30
            )
        else:
            resp = requests.request(
                method=request.method,
                url=url,
                params=request.args,
                headers=headers,
                data=request.get_data(),
                stream=True,
                timeout=30
            )
        
        # Create response
        response = make_response(resp.content)
        response.status_code = resp.status_code
        
        # Copy headers
        for key, value in resp.headers.items():
            if key.lower() not in ['connection', 'content-encoding', 'content-length', 'transfer-encoding']:
                response.headers[key] = value
        
        # Inject convivial features if it's an HTML page
        if 'text/html' in resp.headers.get('Content-Type', ''):
            content = resp.content.decode('utf-8')
            
            # Inject user info and convivial features
            inject_script = f"""
            <script>
                window.convivialUser = {user_info['claims']};
                window.convivialToken = '{token}';
            </script>
            <script src="/static/js/convivial-api.js"></script>
            """
            
            # Inject before </body>
            content = content.replace('</body>', inject_script + '</body>')
            response.data = content.encode('utf-8')
        
        return response
        
    except requests.exceptions.RequestException as e:
        return f"Error connecting to search service: {str(e)}", 503

@app.route('/health')
def health():
    """Health check"""
    return {'status': 'healthy', 'service': 'auth-proxy'}

if __name__ == '__main__':
    app.run(debug=os.environ.get('ENV') != 'production', host='0.0.0.0', port=8000)