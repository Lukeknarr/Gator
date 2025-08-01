#!/usr/bin/env python3
"""
Test script to verify mock services work without heavy dependencies
"""

def test_premium_service():
    """Test premium service without heavy dependencies"""
    try:
        from services.premium_service import PremiumService
        
        service = PremiumService()
        
        # Test academic paper search
        papers = service.search_academic_papers("machine learning", 5)
        print(f"✓ Premium service: Found {len(papers)} mock papers")
        
        # Test expert recommendations
        interests = [{'name': 'technology', 'weight': 0.9}]
        experts = service.get_expert_recommendations(interests)
        print(f"✓ Premium service: Found {len(experts)} mock experts")
        
        return True
        
    except Exception as e:
        print(f"✗ Premium service error: {e}")
        return False

def test_connection_map_service():
    """Test connection map service without heavy dependencies"""
    try:
        from services.connection_map_service import connection_map_service
        
        # Test novel connections
        interests = [
            {'name': 'machine learning', 'weight': 0.9},
            {'name': 'climate change', 'weight': 0.7}
        ]
        content_data = [
            {'id': 1, 'title': 'Test Content', 'tags': ['test']}
        ]
        
        connections = connection_map_service.find_novel_connections(interests, content_data)
        print(f"✓ Connection map: Found {len(connections)} mock connections")
        
        # Test exploration paths
        paths = connection_map_service.suggest_exploration_paths(interests, content_data)
        print(f"✓ Connection map: Found {len(paths)} mock exploration paths")
        
        return True
        
    except Exception as e:
        print(f"✗ Connection map error: {e}")
        return False

def main():
    """Run all tests"""
    print("Testing mock services without heavy dependencies...")
    print()
    
    premium_ok = test_premium_service()
    connection_ok = test_connection_map_service()
    
    print()
    if premium_ok and connection_ok:
        print("✓ All mock services working correctly!")
        print("✓ No heavy dependencies required!")
        return True
    else:
        print("✗ Some services have issues")
        return False

if __name__ == "__main__":
    main() 