-- Gator Database Schema
-- PostgreSQL database schema for the personalized media discovery engine

-- Create database
CREATE DATABASE gator_db;
\c gator_db;

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- User interests table
CREATE TABLE user_interests (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    topic VARCHAR(255) NOT NULL,
    weight FLOAT DEFAULT 1.0,
    source VARCHAR(50) DEFAULT 'manual', -- 'manual', 'passive', 'onboarding'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Content table
CREATE TABLE content (
    id SERIAL PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    url VARCHAR(1000) UNIQUE NOT NULL,
    source VARCHAR(100) NOT NULL, -- 'rss', 'substack', 'arxiv', 'youtube'
    author VARCHAR(255),
    published_at TIMESTAMP WITH TIME ZONE,
    summary TEXT,
    content_type VARCHAR(50) NOT NULL, -- 'article', 'podcast', 'video', 'paper'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tags table
CREATE TABLE tags (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    category VARCHAR(50), -- 'topic', 'domain', 'skill'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Content-Tags association table (many-to-many)
CREATE TABLE content_tags (
    content_id INTEGER REFERENCES content(id) ON DELETE CASCADE,
    tag_id INTEGER REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY (content_id, tag_id)
);

-- User interactions table
CREATE TABLE user_interactions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    content_id INTEGER REFERENCES content(id) ON DELETE CASCADE,
    interaction_type VARCHAR(50) NOT NULL, -- 'view', 'like', 'dislike', 'share', 'bookmark'
    duration INTEGER, -- seconds spent on content
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Recommendations table
CREATE TABLE recommendations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    content_id INTEGER REFERENCES content(id) ON DELETE CASCADE,
    score FLOAT NOT NULL,
    algorithm VARCHAR(50) NOT NULL, -- 'tfidf', 'collaborative', 'graph', 'hybrid'
    served_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    clicked BOOLEAN DEFAULT FALSE
);

-- Create indexes for better performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_user_interests_user_id ON user_interests(user_id);
CREATE INDEX idx_user_interests_topic ON user_interests(topic);
CREATE INDEX idx_content_url ON content(url);
CREATE INDEX idx_content_source ON content(source);
CREATE INDEX idx_content_type ON content(content_type);
CREATE INDEX idx_content_published_at ON content(published_at);
CREATE INDEX idx_tags_name ON tags(name);
CREATE INDEX idx_content_tags_content_id ON content_tags(content_id);
CREATE INDEX idx_content_tags_tag_id ON content_tags(tag_id);
CREATE INDEX idx_user_interactions_user_id ON user_interactions(user_id);
CREATE INDEX idx_user_interactions_content_id ON user_interactions(content_id);
CREATE INDEX idx_user_interactions_type ON user_interactions(interaction_type);
CREATE INDEX idx_recommendations_user_id ON recommendations(user_id);
CREATE INDEX idx_recommendations_content_id ON recommendations(content_id);
CREATE INDEX idx_recommendations_algorithm ON recommendations(algorithm);

-- Create composite indexes
CREATE INDEX idx_user_interactions_user_content ON user_interactions(user_id, content_id);
CREATE INDEX idx_recommendations_user_content ON recommendations(user_id, content_id);

-- Create full-text search index for content
CREATE INDEX idx_content_search ON content USING gin(to_tsvector('english', title || ' ' || COALESCE(summary, '')));

-- Create views for common queries
CREATE VIEW content_with_tags AS
SELECT 
    c.*,
    array_agg(t.name) as tags
FROM content c
LEFT JOIN content_tags ct ON c.id = ct.content_id
LEFT JOIN tags t ON ct.tag_id = t.id
GROUP BY c.id;

CREATE VIEW user_interest_summary AS
SELECT 
    u.id as user_id,
    u.username,
    COUNT(ui.topic) as interest_count,
    AVG(ui.weight) as avg_interest_weight
FROM users u
LEFT JOIN user_interests ui ON u.id = ui.user_id
GROUP BY u.id, u.username;

CREATE VIEW content_popularity AS
SELECT 
    c.id,
    c.title,
    c.source,
    COUNT(ui.id) as interaction_count,
    COUNT(CASE WHEN ui.interaction_type = 'like' THEN 1 END) as like_count,
    COUNT(CASE WHEN ui.interaction_type = 'dislike' THEN 1 END) as dislike_count
FROM content c
LEFT JOIN user_interactions ui ON c.id = ui.content_id
GROUP BY c.id, c.title, c.source;

-- Create functions for common operations
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers to automatically update updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_interests_updated_at BEFORE UPDATE ON user_interests
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to get user recommendations
CREATE OR REPLACE FUNCTION get_user_recommendations(
    p_user_id INTEGER,
    p_limit INTEGER DEFAULT 20
)
RETURNS TABLE(
    content_id INTEGER,
    title VARCHAR(500),
    url VARCHAR(1000),
    source VARCHAR(100),
    score FLOAT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        c.id,
        c.title,
        c.url,
        c.source,
        r.score
    FROM recommendations r
    JOIN content c ON r.content_id = c.id
    WHERE r.user_id = p_user_id
    ORDER BY r.score DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;

-- Function to get content similarity
CREATE OR REPLACE FUNCTION get_content_similarity(
    p_content_id INTEGER
)
RETURNS TABLE(
    similar_content_id INTEGER,
    title VARCHAR(500),
    similarity_score FLOAT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        c2.id,
        c2.title,
        COUNT(ct2.tag_id)::FLOAT / NULLIF(COUNT(DISTINCT ct1.tag_id), 0) as similarity_score
    FROM content c1
    JOIN content_tags ct1 ON c1.id = ct1.content_id
    JOIN content_tags ct2 ON ct1.tag_id = ct2.tag_id
    JOIN content c2 ON ct2.content_id = c2.id
    WHERE c1.id = p_content_id AND c2.id != p_content_id
    GROUP BY c2.id, c2.title
    HAVING COUNT(ct2.tag_id) > 0
    ORDER BY similarity_score DESC
    LIMIT 10;
END;
$$ LANGUAGE plpgsql;

-- Insert sample data for testing
INSERT INTO users (email, username, hashed_password) VALUES
('admin@gator.com', 'admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/RK.sUyGm'), -- password: admin123
('test@gator.com', 'testuser', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/RK.sUyGm'); -- password: admin123

INSERT INTO tags (name, category) VALUES
('technology', 'topic'),
('politics', 'topic'),
('science', 'topic'),
('business', 'topic'),
('health', 'topic'),
('artificial intelligence', 'domain'),
('machine learning', 'domain'),
('data science', 'domain'),
('startups', 'domain'),
('climate change', 'topic');

-- Grant permissions (adjust as needed for your setup)
GRANT ALL PRIVILEGES ON DATABASE gator_db TO gator;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO gator;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO gator;
