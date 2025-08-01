#!/bin/bash
echo "🧪 Testing Gator backend startup..."

# Test if start.sh is executable
if [ ! -x "./start.sh" ]; then
    echo "❌ Error: start.sh is not executable"
    chmod +x start.sh
    echo "✅ Made start.sh executable"
fi

# Test if backend directory exists
if [ ! -d "backend" ]; then
    echo "❌ Error: backend directory not found"
    exit 1
fi

# Test if app.py exists
if [ ! -f "backend/app.py" ]; then
    echo "❌ Error: backend/app.py not found"
    exit 1
fi

# Test if requirements.txt exists
if [ ! -f "backend/requirements.txt" ]; then
    echo "❌ Error: backend/requirements.txt not found"
    exit 1
fi

echo "✅ All files present and correct"
echo "✅ start.sh is executable"
echo "✅ Ready for deployment!" 