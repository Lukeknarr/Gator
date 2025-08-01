# Gator Architecture Documentation

## System Overview

Gator is a personalized media discovery engine that uses advanced recommendation algorithms to curate high-quality, cross-domain content for users. The system is built with a modern, scalable architecture that supports real-time learning and adaptation.

## Architecture Components

### 1. Backend (FastAPI)

**Technology Stack:**
- FastAPI (Python web framework)
- SQLAlchemy (ORM)
- PostgreSQL (Primary database)
- Neo4j (Graph database for interest relationships)
- Redis (Caching and session management)

**Key Services:**
- **AuthService**: JWT-based authentication and user management
- **InterestService**: Manages user interest graphs and onboarding
- **RecommendationService**: LJK recommendation engine with hybrid algorithms
- **ContentService**: Content retrieval and search functionality

**API Endpoints:**
```
POST /register          - User registration
POST /login            - User authentication
POST /onboarding       - Complete user onboarding
GET  /interests        - Get user interest graph
POST /interests        - Add new interest
GET  /recommendations  - Get personalized recommendations
POST /feedback         - Submit user feedback
GET  /content/{id}     - Get specific content
GET  /content/search   - Search content
POST /user/export      - Export user data
```

### 2. Data Ingestion Pipeline

**Sources:**
- RSS feeds (TechCrunch, CNN, BBC, NPR, NYTimes)
- Substack newsletters (Stratechery, The Information, Axios)
- Arxiv papers (AI, ML, Computer Vision, NLP, etc.)

**Processing:**
- Content normalization and deduplication
- NLP-based tagging using spaCy and Transformers
- Topic classification and keyword extraction
- Metadata enrichment

**Technologies:**
- feedparser (RSS parsing)
- BeautifulSoup (HTML parsing)
- spaCy (Named Entity Recognition)
- Transformers (Zero-shot classification)

### 3. LJK Recommendation Engine

**Algorithms:**
1. **TF-IDF Similarity**: Content-based filtering using text analysis
2. **Collaborative Filtering**: User-based recommendations
3. **Graph-based Recommendations**: Using interest graph relationships
4. **Cross-domain Discovery**: Finding connections between different topics

**Features:**
- Hybrid scoring combining multiple algorithms
- Real-time interest weight updates
- Exploration vs. exploitation balancing
- Novelty detection for diverse recommendations

### 4. Frontend (Next.js)

**Technology Stack:**
- Next.js 14 (React framework)
- TypeScript
- Tailwind CSS (Styling)
- Framer Motion (Animations)
- D3.js (Graph visualizations)
- React Query (Data fetching)
- Zustand (State management)

**Key Components:**
- **Dashboard**: Main user interface with tabs
- **InterestGraph**: D3.js visualization of user interests
- **RecommendationFeed**: Content display with feedback
- **OnboardingModal**: New user setup flow

**Features:**
- Responsive design
- Real-time updates
- Interactive visualizations
- Progressive Web App capabilities

## Database Schema

### PostgreSQL Tables

```sql
-- Users and authentication
users (id, email, username, hashed_password, is_active, created_at, updated_at)

-- Interest management
user_interests (id, user_id, topic, weight, source, created_at, updated_at)

-- Content storage
content (id, title, url, source, author, published_at, summary, content_type, created_at)
tags (id, name, category, created_at)
content_tags (content_id, tag_id) -- Many-to-many relationship

-- User interactions
user_interactions (id, user_id, content_id, interaction_type, duration, created_at)

-- Recommendations
recommendations (id, user_id, content_id, score, algorithm, served_at, clicked)
```

### Neo4j Graph Database

**Nodes:**
- User nodes
- Interest nodes (with weights)
- Content nodes
- Tag nodes

**Relationships:**
- `INTERESTED_IN` (User -> Interest, weight)
- `TAGGED_AS` (Content -> Tag, weight)
- `RELATED_TO` (Interest -> Interest, similarity)
- `CONSUMED` (User -> Content, interaction_type)

## Data Flow

### 1. User Onboarding
1. User registers/logs in
2. Completes onboarding questionnaire
3. Interests are added to graph
4. Initial recommendations generated

### 2. Content Ingestion
1. Scheduled crawlers fetch new content
2. NLP processing extracts tags and topics
3. Content stored in PostgreSQL
4. Graph relationships updated in Neo4j

### 3. Recommendation Generation
1. User requests recommendations
2. LJK engine combines multiple algorithms
3. Scores calculated for each content item
4. Top recommendations returned to user

### 4. Feedback Loop
1. User interacts with content (like, dislike, view)
2. Interaction recorded in database
3. Interest weights updated
4. Graph relationships refined
5. Future recommendations improved

## Security & Privacy

### Authentication
- JWT tokens with configurable expiration
- Password hashing with bcrypt
- Secure session management

### Data Protection
- User data encryption at rest
- Secure API communication (HTTPS)
- GDPR-compliant data export
- User control over data collection

### Privacy Features
- Local-first option for sensitive data
- Transparent data usage
- User consent management
- Data anonymization capabilities

## Scalability Considerations

### Performance
- Database indexing for fast queries
- Redis caching for frequently accessed data
- CDN for static content delivery
- Horizontal scaling capabilities

### Monitoring
- Application performance monitoring
- Database query optimization
- User engagement metrics
- Recommendation quality tracking

## Deployment

### Development Setup
```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn app:app --reload

# Frontend
cd frontend
npm install
npm run dev

# Database
docker-compose up -d postgres neo4j redis
```

### Production Deployment
- Containerized with Docker
- Kubernetes orchestration
- Load balancing with nginx
- Automated CI/CD pipeline

## Future Enhancements

### Phase 2 Features
- Browser extension for passive tracking
- Multi-modal content ingestion (video, audio)
- Advanced NLP for better content understanding
- Social features and content sharing

### Phase 3 Features
- Cross-domain semantic bridges
- AI-powered content summarization
- Expert curation integration
- Premium subscription tiers

## API Documentation

Complete API documentation is available at `/docs` when running the FastAPI server, providing interactive testing and detailed endpoint specifications.

## Contributing

The Gator system is designed with modularity in mind, making it easy to:
- Add new content sources
- Implement new recommendation algorithms
- Extend the frontend with new features
- Integrate with external services

For detailed development guidelines, see the CONTRIBUTING.md file.
