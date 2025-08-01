# Gator - Personalized Media Discovery Engine

Gator is a sophisticated personalized media discovery engine that passively learns user interests and curates high-quality, cross-domain recommendations. The system balances depth (niche content) and breadth (connecting seemingly unrelated interests) while reducing cognitive load through transparency and efficiency gains.

## Features

### Core Functionality
- **Personalized Recommendations**: LJK recommendation engine combining TF-IDF, collaborative filtering, and graph-based algorithms
- **Interest Graph Visualization**: Interactive D3.js visualization of user interest connections
- **Cross-domain Discovery**: Find content that bridges different topics and interests
- **Passive Learning**: System learns from user interactions to improve recommendations
- **Content Aggregation**: RSS feeds, Substack newsletters, Arxiv papers, and more
- **NLP-powered Tagging**: Advanced content analysis using spaCy and Transformers

### User Experience
- **Modern Dashboard**: Clean, responsive interface with real-time updates
- **Onboarding Flow**: Guided setup for new users to establish initial interests
- **Feedback System**: Like, dislike, share, and save content with immediate feedback
- **Data Transparency**: Export user data and understand recommendation reasoning
- **Exploration Tools**: Discover new topics and cross-domain connections

## Technology Stack

### Backend
- **FastAPI**: Modern Python web framework with automatic API documentation
- **PostgreSQL**: Primary database for user data and content
- **Neo4j**: Graph database for interest relationships and recommendations
- **Redis**: Caching and session management
- **SQLAlchemy**: ORM for database operations
- **JWT**: Secure authentication with bcrypt password hashing

### Data Processing
- **spaCy**: Named Entity Recognition and text processing
- **Transformers**: Zero-shot classification for topic detection
- **feedparser**: RSS feed processing
- **BeautifulSoup**: HTML parsing and content extraction
- **scikit-learn**: TF-IDF and similarity calculations

### Frontend
- **Next.js 14**: React framework with SSR and static generation
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Utility-first styling
- **Framer Motion**: Smooth animations and transitions
- **D3.js**: Interactive data visualizations
- **React Query**: Server state management
- **Zustand**: Client state management

## Quick Start

### Prerequisites
- Python 3.8+
- Node.js 18+
- PostgreSQL
- Neo4j
- Redis

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd Gator_Project
```

2. **Set up the backend**
```bash
cd backend
pip install -r requirements.txt

# Set environment variables
export POSTGRES_URL="postgresql://gator:gator123@localhost:5432/gator_db"
export NEO4J_URI="bolt://localhost:7687"
export NEO4J_USER="neo4j"
export NEO4J_PASSWORD="password"
export SECRET_KEY="your-secret-key-here"

# Run the backend
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

3. **Set up the frontend**
```bash
cd frontend
npm install
npm run dev
```

4. **Initialize the database**
```bash
# Run the database schema
psql -U gator -d gator_db -f database/schema.sql

# Run the data ingestion pipeline
cd data_ingestion
python ingestion_pipeline.py
```

5. **Access the application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## Usage

### For Users

1. **Registration**: Create an account with email and username
2. **Onboarding**: Complete the guided setup to establish initial interests
3. **Dashboard**: Explore personalized recommendations and your interest graph
4. **Interaction**: Like, dislike, share, or save content to improve recommendations
5. **Exploration**: Discover new topics and cross-domain connections

### For Developers

#### Backend Development
```bash
cd backend
pip install -r requirements.txt
uvicorn app:app --reload
```

#### Frontend Development
```bash
cd frontend
npm install
npm run dev
```

#### Data Ingestion
```bash
cd data_ingestion
python ingestion_pipeline.py
```

#### Testing
```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## API Documentation

The complete API documentation is available at `/docs` when running the FastAPI server. Key endpoints include:

- `POST /register` - User registration
- `POST /login` - User authentication
- `POST /onboarding` - Complete user onboarding
- `GET /interests` - Get user interest graph
- `GET /recommendations` - Get personalized recommendations
- `POST /feedback` - Submit user feedback
- `GET /content/search` - Search content
- `POST /user/export` - Export user data

## Architecture

### System Components

1. **Backend API Layer**: FastAPI with JWT authentication
2. **Data Ingestion Pipeline**: RSS, Substack, and Arxiv crawlers
3. **LJK Recommendation Engine**: Hybrid algorithms for personalized content
4. **Database Layer**: PostgreSQL for structured data, Neo4j for graph relationships
5. **Frontend Dashboard**: Next.js with interactive visualizations

### Data Flow

1. **Content Ingestion**: Crawlers fetch and process content from various sources
2. **NLP Processing**: Content is tagged and categorized using advanced NLP
3. **User Interaction**: System learns from user feedback and interactions
4. **Recommendation Generation**: LJK engine combines multiple algorithms
5. **Feedback Loop**: Continuous improvement based on user behavior

## Configuration

### Environment Variables

```bash
# Database
POSTGRES_URL=postgresql://user:password@localhost:5432/gator_db
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password

# Security
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# API
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Content Sources

Edit `data_ingestion/ingestion_pipeline.py` to add or modify content sources:

```python
self.rss_feeds = [
    "https://feeds.feedburner.com/TechCrunch",
    "https://rss.cnn.com/rss/edition.rss",
    # Add more RSS feeds
]

self.substack_feeds = [
    "https://stratechery.com/feed/",
    # Add more Substack feeds
]

self.arxiv_categories = [
    "cs.AI", "cs.LG", "cs.CV",
    # Add more Arxiv categories
]
```

## Deployment

### Development
```bash
# Start all services
docker-compose up -d
cd backend && uvicorn app:app --reload
cd frontend && npm run dev
```

### Production
```bash
# Build and deploy
docker build -t gator-backend ./backend
docker build -t gator-frontend ./frontend
docker-compose -f docker-compose.prod.yml up -d
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

### Development Guidelines

- Follow PEP 8 for Python code
- Use TypeScript for frontend components
- Write comprehensive tests
- Update documentation for new features
- Follow the existing code style

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue on GitHub
- Check the documentation in `/docs`
- Review the architecture documentation

## Roadmap

### Phase 1 (Current)
- ✅ User registration and onboarding
- ✅ Interest graph backend
- ✅ RSS + Substack + Arxiv ingestion
- ✅ Basic recommendation engine
- ✅ Dashboard UI with graph visualization
- ✅ Feedback system
- ✅ Data export functionality

### Phase 2 (Planned)
- 🔹 Browser extension for passive tracking
- 🔹 Multi-modal content ingestion
- 🔹 Advanced NLP for content understanding
- 🔹 Social features and content sharing

### Phase 3 (Future)
- 🔹 Cross-domain semantic bridges
- 🔹 AI-powered content summarization
- 🔹 Expert curation integration
- 🔹 Premium subscription tiers

## Acknowledgments

- Built with modern web technologies
- Inspired by knowledge management systems like Obsidian
- Uses state-of-the-art NLP and recommendation algorithms
- Designed for user privacy and data transparency
# Gator
