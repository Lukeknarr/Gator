#!/bin/bash
set -e  # Exit on any error

echo "🚀 Starting Gator backend..."

# Change to backend directory
cd backend

# Set default port if not provided
PORT=${PORT:-8000}
echo "📍 Using port: $PORT"

# Check if app.py exists
if [ ! -f "app.py" ]; then
    echo "❌ Error: app.py not found in backend directory"
    ls -la
    exit 1
fi

echo "✅ Found app.py, starting uvicorn..."

# Use exec for proper signal handling and explicit python path
exec python3 -m uvicorn app:app --host 0.0.0.0 --port $PORT 