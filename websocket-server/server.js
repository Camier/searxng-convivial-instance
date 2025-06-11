/**
 * WebSocket Server for Searxng Convivial Instance
 * Handles real-time presence, collisions, and collaborative features
 */

const express = require('express');
const { createServer } = require('http');
const { Server } = require('socket.io');
const { createAdapter } = require('@socket.io/redis-adapter');
const { createClient } = require('redis');
const jwt = require('jsonwebtoken');
const { Pool } = require('pg');
const winston = require('winston');
require('dotenv').config();

// Logger setup
const logger = winston.createLogger({
  level: process.env.NODE_ENV === 'production' ? 'info' : 'debug',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.json()
  ),
  transports: [
    new winston.transports.Console({
      format: winston.format.simple()
    })
  ]
});

// Express app for health checks
const app = express();
const httpServer = createServer(app);

// Socket.io setup with CORS
const io = new Server(httpServer, {
  cors: {
    origin: process.env.SEARXNG_URL || 'http://localhost:8080',
    credentials: true
  },
  connectionStateRecovery: {
    maxDisconnectionDuration: 2 * 60 * 1000, // 2 minutes
    skipMiddlewares: true
  }
});

// PostgreSQL connection
const pgPool = new Pool({
  host: process.env.POSTGRES_HOST || 'postgres',
  database: process.env.POSTGRES_DB || 'searxng_convivial',
  user: process.env.POSTGRES_USER || 'searxng',
  password: process.env.POSTGRES_PASSWORD,
  max: 10,
  idleTimeoutMillis: 30000
});

// Redis adapter for Socket.io clustering
async function setupRedisAdapter() {
  const pubClient = createClient({
    socket: {
      host: process.env.REDIS_PUBSUB_HOST || 'redis-pubsub',
      port: parseInt(process.env.REDIS_PUBSUB_PORT) || 6380
    }
  });
  
  const subClient = pubClient.duplicate();
  
  await Promise.all([
    pubClient.connect(),
    subClient.connect()
  ]);
  
  io.adapter(createAdapter(pubClient, subClient));
  logger.info('Redis adapter connected');
  
  return { pubClient, subClient };
}

// Authentication middleware
io.use(async (socket, next) => {
  try {
    const token = socket.handshake.auth.token;
    if (!token) {
      return next(new Error('Authentication required'));
    }
    
    // For development, accept any token
    // In production, verify JWT
    if (process.env.NODE_ENV === 'production') {
      const decoded = jwt.verify(token, process.env.JWT_SECRET);
      socket.userId = decoded.userId;
      socket.username = decoded.username;
    } else {
      // Dev mode: extract from token directly
      socket.userId = socket.handshake.auth.userId || 'dev-user';
      socket.username = socket.handshake.auth.username || 'Developer';
    }
    
    next();
  } catch (err) {
    next(new Error('Invalid token'));
  }
});

// Main connection handler
io.on('connection', async (socket) => {
  logger.info(`User connected: ${socket.username} (${socket.userId})`);
  
  // Join personal room and friend group room
  socket.join(`user:${socket.userId}`);
  socket.join('convivial-salon'); // Main friend group room
  
  // Broadcast presence
  socket.to('convivial-salon').emit('friend:online', {
    userId: socket.userId,
    username: socket.username,
    timestamp: new Date().toISOString()
  });
  
  // Update user status in database
  try {
    await pgPool.query(
      'UPDATE users SET last_seen = NOW() WHERE id = $1',
      [socket.userId]
    );
  } catch (err) {
    logger.error('Failed to update user status:', err);
  }
  
  // Handle search presence
  socket.on('search:start', async (data) => {
    const searchData = {
      userId: socket.userId,
      username: socket.username,
      mood: data.mood,
      queryHint: anonymizeQuery(data.query),
      timestamp: new Date().toISOString()
    };
    
    // Broadcast to friends
    socket.to('convivial-salon').emit('friend:searching', searchData);
    
    // Check for collisions
    checkCollisions(socket, data.query);
  });
  
  // Handle discovery sharing
  socket.on('discovery:share', async (data) => {
    try {
      const result = await pgPool.query(
        `INSERT INTO discoveries (user_id, query, result_url, result_title, result_snippet, engine, is_gift, gifted_to, gift_message)
         VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
         RETURNING id`,
        [
          socket.userId,
          data.query,
          data.url,
          data.title,
          data.snippet,
          data.engine,
          data.isGift || false,
          data.giftTo || null,
          data.giftMessage || null
        ]
      );
      
      const discoveryId = result.rows[0].id;
      
      if (data.isGift) {
        // Schedule gift reveal
        io.to(`user:${data.giftTo}`).emit('gift:pending', {
          from: socket.username,
          hint: data.giftMessage,
          revealIn: '24 hours'
        });
      } else {
        // Broadcast to discovery feed
        socket.to('convivial-salon').emit('discovery:new', {
          id: discoveryId,
          user: socket.username,
          title: data.title,
          url: data.url,
          timestamp: new Date().toISOString()
        });
      }
    } catch (err) {
      logger.error('Failed to share discovery:', err);
      socket.emit('error', { message: 'Failed to share discovery' });
    }
  });
  
  // Handle voice notes
  socket.on('voice:upload', async (data) => {
    // This would integrate with S3 upload
    socket.to('convivial-salon').emit('voice:new', {
      from: socket.username,
      discoveryId: data.discoveryId,
      duration: data.duration
    });
  });
  
  // Handle disconnection
  socket.on('disconnect', () => {
    logger.info(`User disconnected: ${socket.username}`);
    
    socket.to('convivial-salon').emit('friend:offline', {
      userId: socket.userId,
      username: socket.username,
      timestamp: new Date().toISOString()
    });
  });
});

// Collision detection
async function checkCollisions(socket, query) {
  try {
    const result = await pgPool.query(
      `SELECT u.id, u.username 
       FROM search_sessions ss
       JOIN users u ON u.id = ss.user_id
       WHERE ss.user_id != $1 
       AND ss.query = $2
       AND ss.session_start > NOW() - INTERVAL '1 hour'`,
      [socket.userId, query]
    );
    
    if (result.rows.length > 0) {
      const collision = {
        users: [socket.username, ...result.rows.map(r => r.username)],
        query: query,
        type: 'simultaneous',
        timestamp: new Date().toISOString()
      };
      
      io.to('convivial-salon').emit('collision:detected', collision);
      
      // Store collision
      for (const user of result.rows) {
        await pgPool.query(
          `INSERT INTO collisions (user1_id, user2_id, query, collision_type)
           VALUES ($1, $2, $3, 'simultaneous')`,
          [socket.userId, user.id, query]
        );
      }
    }
  } catch (err) {
    logger.error('Collision check failed:', err);
  }
}

// Query anonymization
function anonymizeQuery(query) {
  if (!query || query.length < 5) return '✨';
  
  const words = query.split(' ');
  if (words.length === 1) {
    return `${query[0]}${'*'.repeat(Math.min(query.length - 1, 5))}`;
  }
  return `${words.length} words about ${words[0]}...`;
}

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    connections: io.engine.clientsCount,
    timestamp: new Date().toISOString()
  });
});

// Start server
async function start() {
  try {
    await setupRedisAdapter();
    
    const PORT = process.env.PORT || 3000;
    httpServer.listen(PORT, () => {
      logger.info(`WebSocket server listening on port ${PORT}`);
    });
  } catch (err) {
    logger.error('Failed to start server:', err);
    process.exit(1);
  }
}

// Graceful shutdown
process.on('SIGTERM', async () => {
  logger.info('SIGTERM received, shutting down gracefully');
  io.close();
  await pgPool.end();
  process.exit(0);
});

start();