#!/usr/bin/env python3
"""
Test script to verify app startup without blocking operations
"""

import asyncio
import sys
import os

# Add current directory to path
sys.path.append('.')

async def test_app_startup():
    """Test that the app can be created and started"""
    try:
        # Import the app
        from app import app
        print("✅ App imported successfully")
        
        # Test that we can create a test client
        from fastapi.testclient import TestClient
        client = TestClient(app)
        print("✅ Test client created successfully")
        
        # Test the root endpoint
        response = client.get("/")
        print(f"✅ Root endpoint responds: {response.status_code}")
        print(f"   Response: {response.json()}")
        
        # Test the health endpoint
        response = client.get("/health")
        print(f"✅ Health endpoint responds: {response.status_code}")
        print(f"   Response: {response.json()}")
        
        print("✅ All startup tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Startup test failed: {e}")
        return False

if __name__ == "__main__":
    # Run the test
    success = asyncio.run(test_app_startup())
    sys.exit(0 if success else 1) 