"""
Authentication Service for SearXNG Convivial Instance
Provides JWT-based authentication with role-based access control
"""

import os
from datetime import datetime, timedelta, timezone
from functools import wraps

from flask import Flask, jsonify, request
from flask_jwt_extended import (
    JWTManager, create_access_token, create_refresh_token,
    get_jwt_identity, jwt_required, get_jwt
)
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from marshmallow import Schema, fields, validate, ValidationError
import redis

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET', 'dev-jwt-secret')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)
app.config['JWT_TOKEN_LOCATION'] = ['headers', 'cookies']
app.config['JWT_COOKIE_SECURE'] = os.environ.get('ENV') == 'production'
app.config['JWT_COOKIE_CSRF_PROTECT'] = True
app.config['JWT_COOKIE_SAMESITE'] = 'Lax'

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{os.environ.get('POSTGRES_USER', 'searxng')}:{os.environ.get('POSTGRES_PASSWORD')}@{os.environ.get('POSTGRES_HOST', 'postgres')}/{os.environ.get('POSTGRES_DB', 'searxng_convivial')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
cors = CORS(app, origins=os.environ.get('ALLOWED_ORIGINS', 'http://localhost:8890').split(','))

# Rate limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri=f"redis://{os.environ.get('REDIS_HOST', 'redis-cache')}:6379"
)

# Redis for token blacklist
redis_client = redis.Redis(
    host=os.environ.get('REDIS_HOST', 'redis-cache'),
    port=6379,
    decode_responses=True
)

# Models
class User(db.Model):
    __tablename__ = 'auth_users'
    
    id = db.Column(db.String(36), primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    display_name = db.Column(db.String(100))
    role = db.Column(db.String(20), default='friend')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'display_name': self.display_name,
            'role': self.role,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

# Schemas for validation
class RegisterSchema(Schema):
    username = fields.Str(required=True, validate=[
        validate.Length(min=3, max=50),
        validate.Regexp('^[a-zA-Z0-9_]+$', error='Username must be alphanumeric')
    ])
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=8))
    display_name = fields.Str(validate=validate.Length(max=100))

class LoginSchema(Schema):
    username = fields.Str(required=True)
    password = fields.Str(required=True)

# JWT callbacks
@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    jti = jwt_payload['jti']
    token_in_redis = redis_client.get(f"blocklist:{jti}")
    return token_in_redis is not None

@jwt.revoked_token_loader
def revoked_token_callback(jwt_header, jwt_payload):
    return jsonify({'message': 'Token has been revoked'}), 401

@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify({'message': 'Token has expired'}), 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({'message': 'Invalid token'}), 401

# Helper decorators
def require_friend_limit(f):
    """Decorator to enforce friend limit (max 3 users)"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_count = User.query.filter_by(is_active=True).count()
        if user_count >= 3:
            return jsonify({'message': 'Friend limit reached (max 3)'}), 403
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'auth-service',
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/auth/register', methods=['POST'])
@limiter.limit("3 per hour")
@require_friend_limit
def register():
    """Register a new user (max 3 friends)"""
    schema = RegisterSchema()
    
    try:
        data = schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({'errors': err.messages}), 400
    
    # Check if user exists
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'message': 'Username already exists'}), 409
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'Email already registered'}), 409
    
    # Create new user
    user = User(
        id=str(datetime.utcnow().timestamp()).replace('.', ''),
        username=data['username'],
        email=data['email'],
        display_name=data.get('display_name', data['username'])
    )
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    # Create tokens
    access_token = create_access_token(
        identity=user.id,
        additional_claims={
            'username': user.username,
            'role': user.role
        }
    )
    refresh_token = create_refresh_token(identity=user.id)
    
    return jsonify({
        'message': 'User created successfully',
        'user': user.to_dict(),
        'access_token': access_token,
        'refresh_token': refresh_token
    }), 201

@app.route('/auth/login', methods=['POST'])
@limiter.limit("10 per hour")
def login():
    """Login with username and password"""
    schema = LoginSchema()
    
    try:
        data = schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({'errors': err.messages}), 400
    
    # Find user
    user = User.query.filter_by(username=data['username']).first()
    
    if not user or not user.check_password(data['password']):
        return jsonify({'message': 'Invalid credentials'}), 401
    
    if not user.is_active:
        return jsonify({'message': 'Account is disabled'}), 403
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.session.commit()
    
    # Create tokens
    access_token = create_access_token(
        identity=user.id,
        additional_claims={
            'username': user.username,
            'role': user.role
        }
    )
    refresh_token = create_refresh_token(identity=user.id)
    
    return jsonify({
        'user': user.to_dict(),
        'access_token': access_token,
        'refresh_token': refresh_token
    })

@app.route('/auth/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token"""
    identity = get_jwt_identity()
    user = User.query.get(identity)
    
    if not user or not user.is_active:
        return jsonify({'message': 'User not found or inactive'}), 404
    
    access_token = create_access_token(
        identity=user.id,
        additional_claims={
            'username': user.username,
            'role': user.role
        }
    )
    
    return jsonify({'access_token': access_token})

@app.route('/auth/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout and revoke token"""
    jti = get_jwt()['jti']
    exp = get_jwt()['exp']
    
    # Calculate token remaining time
    now = datetime.now(timezone.utc)
    expiry_time = datetime.fromtimestamp(exp, timezone.utc)
    remaining_time = int((expiry_time - now).total_seconds())
    
    # Add token to blocklist
    redis_client.setex(f"blocklist:{jti}", remaining_time, 'true')
    
    return jsonify({'message': 'Successfully logged out'})

@app.route('/auth/me', methods=['GET'])
@jwt_required()
def me():
    """Get current user info"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    return jsonify({'user': user.to_dict()})

@app.route('/auth/verify', methods=['GET'])
@jwt_required()
def verify():
    """Verify token validity"""
    return jsonify({
        'valid': True,
        'user_id': get_jwt_identity(),
        'claims': get_jwt()
    })

@app.route('/auth/users', methods=['GET'])
@jwt_required()
def list_users():
    """List all active users (friends)"""
    users = User.query.filter_by(is_active=True).all()
    return jsonify({
        'users': [user.to_dict() for user in users],
        'count': len(users),
        'limit': 3
    })

# Error handlers
@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({'message': f'Rate limit exceeded: {e.description}'}), 429

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({'message': 'Internal server error'}), 500

# Initialize database
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=os.environ.get('ENV') != 'production', host='0.0.0.0', port=5000)