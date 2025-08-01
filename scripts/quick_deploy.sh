#!/bin/bash

# Gator Quick Deploy Script
# This script automates the deployment to Railway and Vercel

set -e

echo "🚀 Starting Gator Quick Deploy..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Check if git is initialized
check_git() {
    if [ ! -d ".git" ]; then
        print_error "Git repository not initialized. Please run:"
        echo "  git init"
        echo "  git remote add origin <your-repo-url>"
        exit 1
    fi
    
    print_status "Git repository found"
}

# Check if all required files exist
check_files() {
    print_step "Checking required files..."
    
    required_files=(
        "backend/requirements.txt"
        "backend/app.py"
        "backend/railway.json"
        "frontend/package.json"
        "frontend/vercel.json"
        "frontend/next.config.js"
    )
    
    for file in "${required_files[@]}"; do
        if [ ! -f "$file" ]; then
            print_error "Required file not found: $file"
            exit 1
        fi
    done
    
    print_status "All required files found"
}

# Setup environment variables
setup_env() {
    print_step "Setting up environment variables..."
    
    # Backend environment variables
    cat > backend/.env << EOF
# Database Configuration
POSTGRES_URL=postgresql://postgres:password@localhost:5432/gator_db
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password

# Security
SECRET_KEY=your-secret-key-here-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30

# API Configuration
CORS_ORIGINS=https://gator.vercel.app,http://localhost:3000

# Environment
ENVIRONMENT=production
EOF

    # Frontend environment variables
    cat > frontend/.env.local << EOF
# API Configuration
NEXT_PUBLIC_API_URL=https://gator-api.up.railway.app

# Environment
NODE_ENV=production
EOF

    print_status "Environment files created"
    print_warning "Please update the environment variables with your actual values"
}

# Deploy to Railway
deploy_railway() {
    print_step "Deploying to Railway..."
    
    # Check if Railway CLI is installed
    if ! command -v railway &> /dev/null; then
        print_warning "Railway CLI not found. Please install it:"
        echo "  npm install -g @railway/cli"
        echo "  railway login"
        echo ""
        print_status "You can also deploy manually:"
        echo "  1. Go to https://railway.app"
        echo "  2. Click 'New Project' → 'Deploy from GitHub Repo'"
        echo "  3. Select your repository"
        echo "  4. Set root directory to 'backend'"
        echo "  5. Add environment variables"
        return
    fi
    
    # Deploy to Railway
    cd backend
    railway up
    cd ..
    
    print_status "Railway deployment completed"
}

# Deploy to Vercel
deploy_vercel() {
    print_step "Deploying to Vercel..."
    
    # Check if Vercel CLI is installed
    if ! command -v vercel &> /dev/null; then
        print_warning "Vercel CLI not found. Please install it:"
        echo "  npm install -g vercel"
        echo "  vercel login"
        echo ""
        print_status "You can also deploy manually:"
        echo "  1. Go to https://vercel.com"
        echo "  2. Click 'New Project'"
        echo "  3. Import your GitHub repository"
        echo "  4. Set root directory to 'frontend'"
        echo "  5. Deploy"
        return
    fi
    
    # Deploy to Vercel
    cd frontend
    vercel --prod
    cd ..
    
    print_status "Vercel deployment completed"
}

# Setup databases
setup_databases() {
    print_step "Setting up databases..."
    
    print_status "Setting up PostgreSQL (Supabase):"
    echo "  1. Go to https://supabase.com"
    echo "  2. Create a new project"
    echo "  3. Get your database URL"
    echo "  4. Add to Railway environment variables:"
    echo "     POSTGRES_URL=your-supabase-url"
    echo ""
    
    print_status "Setting up Neo4j AuraDB:"
    echo "  1. Go to https://neo4j.com/aura"
    echo "  2. Create a free AuraDB instance"
    echo "  3. Get your connection details"
    echo "  4. Add to Railway environment variables:"
    echo "     NEO4J_URI=your-aura-uri"
    echo "     NEO4J_USER=neo4j"
    echo "     NEO4J_PASSWORD=your-password"
    echo ""
    
    print_warning "Please set up your databases and update environment variables"
}

# Test deployment
test_deployment() {
    print_step "Testing deployment..."
    
    # Test backend
    print_status "Testing backend..."
    backend_url="https://gator-api.up.railway.app"
    
    if command -v curl &> /dev/null; then
        response=$(curl -s -o /dev/null -w "%{http_code}" "$backend_url/")
        if [ "$response" = "200" ]; then
            print_status "Backend is responding correctly"
        else
            print_warning "Backend health check failed (HTTP $response)"
        fi
    else
        print_warning "curl not found, skipping backend test"
    fi
    
    # Test frontend
    print_status "Testing frontend..."
    frontend_url="https://gator.vercel.app"
    
    if command -v curl &> /dev/null; then
        response=$(curl -s -o /dev/null -w "%{http_code}" "$frontend_url/")
        if [ "$response" = "200" ]; then
            print_status "Frontend is responding correctly"
        else
            print_warning "Frontend health check failed (HTTP $response)"
        fi
    else
        print_warning "curl not found, skipping frontend test"
    fi
}

# Main deployment function
main() {
    print_status "Starting Gator Quick Deploy..."
    
    # Check prerequisites
    check_git
    check_files
    
    # Setup environment
    setup_env
    
    # Setup databases
    setup_databases
    
    # Deploy to Railway
    deploy_railway
    
    # Deploy to Vercel
    deploy_vercel
    
    # Test deployment
    test_deployment
    
    print_status "Deployment process completed!"
    print_status "Your Gator application should be available at:"
    echo "  Frontend: https://gator.vercel.app"
    echo "  Backend: https://gator-api.up.railway.app"
    echo "  API Docs: https://gator-api.up.railway.app/docs"
    echo ""
    print_warning "Remember to:"
    echo "  1. Update environment variables with your actual database URLs"
    echo "  2. Set up your databases (Supabase + Neo4j AuraDB)"
    echo "  3. Configure CORS settings if needed"
    echo "  4. Test all features thoroughly"
}

# Run main function
main "$@" 