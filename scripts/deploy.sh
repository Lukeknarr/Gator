#!/bin/bash

# Gator Production Deployment Script
# This script automates the deployment process for the MVP hosting stack

set -e

echo "🚀 Starting Gator Production Deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
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

# Check if required tools are installed
check_dependencies() {
    print_status "Checking dependencies..."
    
    if ! command -v git &> /dev/null; then
        print_error "Git is not installed"
        exit 1
    fi
    
    if ! command -v node &> /dev/null; then
        print_error "Node.js is not installed"
        exit 1
    fi
    
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed"
        exit 1
    fi
    
    print_status "All dependencies are installed"
}

# Validate environment variables
validate_env() {
    print_status "Validating environment variables..."
    
    required_vars=(
        "POSTGRES_URL"
        "NEO4J_URI"
        "NEO4J_USER"
        "NEO4J_PASSWORD"
        "SECRET_KEY"
    )
    
    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            print_error "Environment variable $var is not set"
            exit 1
        fi
    done
    
    print_status "Environment variables are valid"
}

# Initialize database
init_database() {
    print_status "Initializing database..."
    
    cd backend
    python3 migrations/init_db.py
    
    if [ $? -eq 0 ]; then
        print_status "Database initialized successfully"
    else
        print_error "Database initialization failed"
        exit 1
    fi
    
    cd ..
}

# Run data ingestion
run_ingestion() {
    print_status "Running data ingestion pipeline..."
    
    cd data_ingestion
    python3 ingestion_pipeline.py
    
    if [ $? -eq 0 ]; then
        print_status "Data ingestion completed successfully"
    else
        print_warning "Data ingestion had issues, but continuing..."
    fi
    
    cd ..
}

# Test backend deployment
test_backend() {
    print_status "Testing backend deployment..."
    
    # Get the backend URL from environment or use default
    BACKEND_URL=${BACKEND_URL:-"https://gator-backend.railway.app"}
    
    # Test the health endpoint
    response=$(curl -s -o /dev/null -w "%{http_code}" "$BACKEND_URL/")
    
    if [ "$response" = "200" ]; then
        print_status "Backend is responding correctly"
    else
        print_warning "Backend health check failed (HTTP $response)"
        print_warning "This might be normal if the backend is still deploying"
    fi
}

# Test frontend deployment
test_frontend() {
    print_status "Testing frontend deployment..."
    
    # Get the frontend URL from environment or use default
    FRONTEND_URL=${FRONTEND_URL:-"https://gator-frontend.vercel.app"}
    
    # Test the frontend
    response=$(curl -s -o /dev/null -w "%{http_code}" "$FRONTEND_URL/")
    
    if [ "$response" = "200" ]; then
        print_status "Frontend is responding correctly"
    else
        print_warning "Frontend health check failed (HTTP $response)"
        print_warning "This might be normal if the frontend is still deploying"
    fi
}

# Main deployment function
main() {
    print_status "Starting Gator deployment process..."
    
    # Check dependencies
    check_dependencies
    
    # Validate environment
    validate_env
    
    # Initialize database
    init_database
    
    # Run data ingestion
    run_ingestion
    
    # Wait a bit for deployments to complete
    print_status "Waiting for deployments to complete..."
    sleep 30
    
    # Test deployments
    test_backend
    test_frontend
    
    print_status "Deployment process completed!"
    print_status "Your Gator application should be available at:"
    echo "  Frontend: ${FRONTEND_URL:-"https://gator-frontend.vercel.app"}"
    echo "  Backend: ${BACKEND_URL:-"https://gator-backend.railway.app"}"
    echo "  API Docs: ${BACKEND_URL:-"https://gator-backend.railway.app"}/docs"
}

# Run main function
main "$@" 