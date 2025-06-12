"""
API Service for SearXNG Convivial Instance
Provides RESTful API with OpenAPI documentation for all convivial features
"""

import os
import json
from datetime import datetime, timedelta
from functools import wraps
import uuid

from flask import Flask, request, jsonify
from flask_restx import Api, Resource, fields, Namespace
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity, get_jwt
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text, and_, or_
from sqlalchemy.dialects.postgresql import UUID
import redis
from minio import Minio
from werkzeug.datastructures import FileStorage
import requests

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET', 'dev-jwt-secret')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
app.config['JWT_TOKEN_LOCATION'] = ['headers']
app.config['JWT_HEADER_NAME'] = 'Authorization'
app.config['JWT_HEADER_TYPE'] = 'Bearer'

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{os.environ.get('POSTGRES_USER', 'searxng')}:{os.environ.get('POSTGRES_PASSWORD')}@{os.environ.get('POSTGRES_HOST', 'postgres')}/{os.environ.get('POSTGRES_DB', 'searxng_convivial')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
jwt = JWTManager(app)
cors = CORS(app, origins=os.environ.get('ALLOWED_ORIGINS', 'http://localhost:8890').split(','))

# Redis clients
redis_cache = redis.Redis(
    host=os.environ.get('REDIS_CACHE_HOST', 'redis-cache'),
    port=6379,
    decode_responses=True
)

redis_pubsub = redis.Redis(
    host=os.environ.get('REDIS_PUBSUB_HOST', 'redis-pubsub'),
    port=6380,
    decode_responses=True
)

# MinIO client for file storage
minio_client = None
if os.environ.get('MINIO_ENDPOINT'):
    minio_client = Minio(
        os.environ.get('MINIO_ENDPOINT'),
        access_key=os.environ.get('MINIO_ACCESS_KEY'),
        secret_key=os.environ.get('MINIO_SECRET_KEY'),
        secure=os.environ.get('MINIO_SECURE', 'false').lower() == 'true'
    )

# API Documentation
api = Api(app, version='1.0', title='SearXNG Convivial API',
    description='API for social search features and collaborative discovery',
    doc='/docs'
)

# Namespaces
ns_discoveries = api.namespace('discoveries', description='Discovery operations')
ns_collections = api.namespace('collections', description='Collection management')
ns_presence = api.namespace('presence', description='Real-time presence')
ns_social = api.namespace('social', description='Social features')
ns_files = api.namespace('files', description='File uploads')

# Models for API documentation
discovery_model = api.model('Discovery', {
    'id': fields.String(description='Discovery ID'),
    'user_id': fields.String(description='User who made the discovery'),
    'query': fields.String(description='Search query'),
    'url': fields.String(description='Result URL'),
    'title': fields.String(description='Result title'),
    'snippet': fields.String(description='Result snippet'),
    'engine': fields.String(description='Search engine used'),
    'discovered_at': fields.DateTime(description='Discovery timestamp'),
    'is_gift': fields.Boolean(description='Is this a gift?'),
    'annotations': fields.Raw(description='User annotations')
})

collection_model = api.model('Collection', {
    'id': fields.String(description='Collection ID'),
    'name': fields.String(required=True, description='Collection name'),
    'description': fields.String(description='Collection description'),
    'type': fields.String(description='Collection type'),
    'owner_id': fields.String(description='Owner user ID'),
    'is_shared': fields.Boolean(description='Is shared with friends?'),
    'created_at': fields.DateTime(description='Creation timestamp')
})

# Authentication decorator with role checking
def require_auth(roles=None):
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def decorated_function(*args, **kwargs):
            if roles:
                claims = get_jwt()
                user_role = claims.get('role', 'friend')
                if user_role not in roles:
                    return {'message': 'Insufficient permissions'}, 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Helper function to get current user
def get_current_user():
    user_id = get_jwt_identity()
    claims = get_jwt()
    return {
        'id': user_id,
        'username': claims.get('username'),
        'role': claims.get('role', 'friend')
    }

# Health check
@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'service': 'api-service',
        'timestamp': datetime.utcnow().isoformat()
    })

# Discovery endpoints
@ns_discoveries.route('/')
class DiscoveryList(Resource):
    @require_auth()
    @ns_discoveries.doc('list_discoveries')
    @ns_discoveries.marshal_list_with(discovery_model)
    def get(self):
        """List recent discoveries from all friends"""
        query = text("""
            SELECT d.*, u.username, u.display_name
            FROM discoveries d
            JOIN users u ON d.user_id = u.id
            ORDER BY d.discovered_at DESC
            LIMIT 50
        """)
        
        result = db.session.execute(query)
        discoveries = []
        for row in result:
            disc = dict(row._mapping)
            disc['user'] = {
                'username': disc.pop('username'),
                'display_name': disc.pop('display_name')
            }
            discoveries.append(disc)
        
        return discoveries
    
    @require_auth()
    @ns_discoveries.doc('create_discovery')
    @ns_discoveries.expect(discovery_model)
    def post(self):
        """Share a new discovery"""
        user = get_current_user()
        data = request.json
        
        discovery_id = str(uuid.uuid4())
        
        query = text("""
            INSERT INTO discoveries 
            (id, user_id, query, result_url, result_title, result_snippet, engine, is_gift, gifted_to, gift_message)
            VALUES (:id, :user_id, :query, :url, :title, :snippet, :engine, :is_gift, :gifted_to, :gift_message)
            RETURNING id
        """)
        
        result = db.session.execute(query, {
            'id': discovery_id,
            'user_id': user['id'],
            'query': data.get('query'),
            'url': data.get('url'),
            'title': data.get('title'),
            'snippet': data.get('snippet'),
            'engine': data.get('engine'),
            'is_gift': data.get('is_gift', False),
            'gifted_to': data.get('gifted_to'),
            'gift_message': data.get('gift_message')
        })
        db.session.commit()
        
        # Publish to Redis for real-time updates
        redis_pubsub.publish('discoveries:new', json.dumps({
            'id': discovery_id,
            'user': user['username'],
            'title': data.get('title'),
            'timestamp': datetime.utcnow().isoformat()
        }))
        
        return {'id': discovery_id, 'message': 'Discovery shared'}, 201

# Collection endpoints  
@ns_collections.route('/')
class CollectionList(Resource):
    @require_auth()
    @ns_collections.doc('list_collections')
    @ns_collections.marshal_list_with(collection_model)
    def get(self):
        """List all collections"""
        query = text("""
            SELECT c.*, u.username, u.display_name, COUNT(ci.discovery_id) as item_count
            FROM collections c
            JOIN users u ON c.owner_id = u.id
            LEFT JOIN collection_items ci ON c.id = ci.collection_id
            WHERE c.is_shared = true OR c.owner_id = :user_id
            GROUP BY c.id, u.username, u.display_name
            ORDER BY c.created_at DESC
        """)
        
        user = get_current_user()
        result = db.session.execute(query, {'user_id': user['id']})
        
        collections = []
        for row in result:
            coll = dict(row._mapping)
            coll['owner'] = {
                'username': coll.pop('username'),
                'display_name': coll.pop('display_name')
            }
            collections.append(coll)
        
        return collections
    
    @require_auth()
    @ns_collections.doc('create_collection')
    @ns_collections.expect(collection_model)
    def post(self):
        """Create a new collection"""
        user = get_current_user()
        data = request.json
        
        collection_id = str(uuid.uuid4())
        
        query = text("""
            INSERT INTO collections (id, name, description, type, owner_id, is_shared)
            VALUES (:id, :name, :description, :type, :owner_id, :is_shared)
            RETURNING id
        """)
        
        result = db.session.execute(query, {
            'id': collection_id,
            'name': data.get('name'),
            'description': data.get('description'),
            'type': data.get('type', 'general'),
            'owner_id': user['id'],
            'is_shared': data.get('is_shared', True)
        })
        db.session.commit()
        
        return {'id': collection_id, 'message': 'Collection created'}, 201

# Morning Coffee endpoint
@ns_social.route('/morning-coffee')
class MorningCoffee(Resource):
    @require_auth()
    @ns_social.doc('get_morning_coffee')
    def get(self):
        """Get today's morning coffee digest"""
        today = datetime.utcnow().date()
        
        # Check cache first
        cached = redis_cache.get(f'morning_coffee:{today}')
        if cached:
            return json.loads(cached)
        
        # Generate digest
        query = text("""
            SELECT d.*, u.username, u.display_name
            FROM discoveries d
            JOIN users u ON d.user_id = u.id
            WHERE DATE(d.discovered_at) = :date
            ORDER BY d.discovered_at DESC
        """)
        
        result = db.session.execute(query, {'date': today})
        discoveries = list(result)
        
        digest = {
            'date': today.isoformat(),
            'discoveries': len(discoveries),
            'summary': f"☕ {len(discoveries)} discoveries yesterday",
            'highlights': discoveries[:5] if discoveries else []
        }
        
        # Cache for 1 hour
        redis_cache.setex(f'morning_coffee:{today}', 3600, json.dumps(digest))
        
        return digest

# File upload endpoints
@ns_files.route('/upload')
class FileUpload(Resource):
    @require_auth()
    @ns_files.doc('upload_file')
    def post(self):
        """Upload a file (avatar, voice note, etc.)"""
        if not minio_client:
            return {'message': 'File storage not configured'}, 503
        
        if 'file' not in request.files:
            return {'message': 'No file provided'}, 400
        
        file = request.files['file']
        if file.filename == '':
            return {'message': 'No file selected'}, 400
        
        user = get_current_user()
        file_type = request.form.get('type', 'general')
        
        # Generate unique filename
        ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else 'bin'
        filename = f"{user['id']}/{file_type}/{uuid.uuid4()}.{ext}"
        
        # Upload to MinIO
        bucket = os.environ.get('MINIO_BUCKET', 'convivial-files')
        
        try:
            # Ensure bucket exists
            if not minio_client.bucket_exists(bucket):
                minio_client.make_bucket(bucket)
            
            # Upload file
            minio_client.put_object(
                bucket,
                filename,
                file.stream,
                length=-1,
                part_size=10*1024*1024
            )
            
            # Generate presigned URL (valid for 7 days)
            url = minio_client.presigned_get_object(bucket, filename, expires=timedelta(days=7))
            
            return {
                'filename': filename,
                'url': url,
                'type': file_type
            }, 201
            
        except Exception as e:
            return {'message': f'Upload failed: {str(e)}'}, 500

# Presence endpoints
@ns_presence.route('/online')
class OnlineUsers(Resource):
    @require_auth()
    @ns_presence.doc('get_online_users')
    def get(self):
        """Get currently online users"""
        # Get from Redis
        online_users = []
        for key in redis_cache.scan_iter('presence:*'):
            user_data = redis_cache.get(key)
            if user_data:
                online_users.append(json.loads(user_data))
        
        return {'users': online_users, 'count': len(online_users)}

# Search collision detection
@ns_social.route('/collisions')
class SearchCollisions(Resource):
    @require_auth()
    @ns_social.doc('get_collisions')
    def get(self):
        """Get recent search collisions"""
        query = text("""
            SELECT c.*, u1.username as user1_name, u2.username as user2_name
            FROM collisions c
            JOIN users u1 ON c.user1_id = u1.id
            JOIN users u2 ON c.user2_id = u2.id
            WHERE c.occurred_at > NOW() - INTERVAL '24 hours'
            ORDER BY c.occurred_at DESC
            LIMIT 10
        """)
        
        result = db.session.execute(query)
        collisions = []
        for row in result:
            collision = dict(row._mapping)
            collisions.append(collision)
        
        return {'collisions': collisions}

# Gift endpoints
@ns_social.route('/gifts/pending')
class PendingGifts(Resource):
    @require_auth()
    @ns_social.doc('get_pending_gifts')
    def get(self):
        """Get pending gifts for current user"""
        user = get_current_user()
        
        query = text("""
            SELECT d.*, u.username as from_user
            FROM discoveries d
            JOIN users u ON d.user_id = u.id
            WHERE d.is_gift = true 
            AND d.gifted_to = :user_id
            AND d.discovered_at + INTERVAL '24 hours' > NOW()
            ORDER BY d.discovered_at DESC
        """)
        
        result = db.session.execute(query, {'user_id': user['id']})
        gifts = [dict(row._mapping) for row in result]
        
        return {'gifts': gifts, 'count': len(gifts)}

# Error handlers
@app.errorhandler(401)
def unauthorized(error):
    return {'message': 'Unauthorized'}, 401

@app.errorhandler(403)
def forbidden(error):
    return {'message': 'Forbidden'}, 403

@app.errorhandler(404)
def not_found(error):
    return {'message': 'Not found'}, 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return {'message': 'Internal server error'}, 500

if __name__ == '__main__':
    app.run(debug=os.environ.get('ENV') != 'production', host='0.0.0.0', port=5001)