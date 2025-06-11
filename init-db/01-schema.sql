-- Searxng Convivial Instance Database Schema
-- PostgreSQL 15+ with JSONB support

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) UNIQUE NOT NULL,
    display_name VARCHAR(100),
    current_mood VARCHAR(50),
    current_fascination TEXT,
    avatar_url TEXT,
    is_ghost BOOLEAN DEFAULT FALSE,
    last_seen TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Discoveries table
CREATE TABLE discoveries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    query TEXT NOT NULL,
    result_url TEXT,
    result_title TEXT,
    result_snippet TEXT,
    result_data JSONB,
    engine VARCHAR(50),
    annotations JSONB,
    is_gift BOOLEAN DEFAULT FALSE,
    gifted_to UUID REFERENCES users(id),
    gift_message TEXT,
    discovered_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Collections table
CREATE TABLE collections (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    type VARCHAR(50) NOT NULL, -- cabinet, grimoire, time_machine, etc.
    owner_id UUID REFERENCES users(id) ON DELETE CASCADE,
    description TEXT,
    cover_image_url TEXT,
    metadata JSONB,
    growth_data JSONB, -- visualization data
    season VARCHAR(20),
    is_shared BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Collection items junction table
CREATE TABLE collection_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    collection_id UUID REFERENCES collections(id) ON DELETE CASCADE,
    discovery_id UUID REFERENCES discoveries(id) ON DELETE CASCADE,
    added_by UUID REFERENCES users(id),
    notes TEXT,
    position INTEGER,
    added_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(collection_id, discovery_id)
);

-- Voice notes table
CREATE TABLE voice_notes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    discovery_id UUID REFERENCES discoveries(id) ON DELETE CASCADE,
    s3_url TEXT NOT NULL,
    duration_seconds INTEGER,
    transcript TEXT,
    is_greeting BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Time capsules table
CREATE TABLE time_capsules (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    creator_id UUID REFERENCES users(id) ON DELETE CASCADE,
    recipient_id UUID REFERENCES users(id),
    discovery_id UUID REFERENCES discoveries(id) ON DELETE CASCADE,
    message TEXT,
    reveal_at TIMESTAMP WITH TIME ZONE NOT NULL,
    revealed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Search sessions table (for collision detection)
CREATE TABLE search_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    query TEXT NOT NULL,
    mood VARCHAR(50),
    session_start TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    session_end TIMESTAMP WITH TIME ZONE
);

-- Collisions table
CREATE TABLE collisions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user1_id UUID REFERENCES users(id) ON DELETE CASCADE,
    user2_id UUID REFERENCES users(id) ON DELETE CASCADE,
    query TEXT,
    discovery_url TEXT,
    collision_type VARCHAR(50), -- simultaneous, sequential, thematic
    celebrated BOOLEAN DEFAULT FALSE,
    occurred_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Morning coffee digests
CREATE TABLE morning_coffee (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    digest_date DATE NOT NULL,
    discoveries JSONB NOT NULL, -- array of discovery IDs with metadata
    generated_summary TEXT,
    coffee_reactions JSONB, -- {user_id: "☕☕☕"}
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(digest_date)
);

-- Indexes for performance
CREATE INDEX idx_discoveries_user_id ON discoveries(user_id);
CREATE INDEX idx_discoveries_discovered_at ON discoveries(discovered_at);
CREATE INDEX idx_discoveries_query ON discoveries(query);
CREATE INDEX idx_collections_owner_id ON collections(owner_id);
CREATE INDEX idx_collection_items_collection_id ON collection_items(collection_id);
CREATE INDEX idx_voice_notes_discovery_id ON voice_notes(discovery_id);
CREATE INDEX idx_time_capsules_reveal_at ON time_capsules(reveal_at) WHERE NOT revealed;
CREATE INDEX idx_search_sessions_user_query ON search_sessions(user_id, query);
CREATE INDEX idx_collisions_occurred_at ON collisions(occurred_at);

-- Triggers for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_collections_updated_at BEFORE UPDATE ON collections
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Sample data for development
INSERT INTO users (username, display_name, current_mood, current_fascination) VALUES
    ('alice', 'Alice', '🌺 Sunday morning botanical', 'Medicinal plants of the Alps'),
    ('bob', 'Bob', '🎵 Vinyl digging simulation', '70s French jazz'),
    ('carol', 'Carol', '📚 Serious research mode', 'Revolutionary pamphlets');