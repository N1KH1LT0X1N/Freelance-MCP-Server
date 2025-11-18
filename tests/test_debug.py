"""
Comprehensive debug test for Freelance MCP Server
Tests all major components and functions
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")
    try:
        import freelance_server
        # Only test modules that are actually used by the server
        from database import db_manager, models
        from mcp_extensions import capabilities, prompts, resource_templates
        from utils import config, logger, monitoring
        print("✓ All imports successful")
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False

def test_server_module():
    """Test server module loads correctly"""
    print("\nTesting server module...")
    try:
        import freelance_server
        
        # Check key components exist
        assert hasattr(freelance_server, 'mcp'), "MCP instance missing"
        assert hasattr(freelance_server, 'db'), "Database instance missing"
        assert hasattr(freelance_server, 'FreelanceDatabase'), "FreelanceDatabase class missing"
        
        print("✓ Server module structure valid")
        return True
    except Exception as e:
        print(f"✗ Server module test failed: {e}")
        return False

def test_database():
    """Test database initialization"""
    print("\nTesting database...")
    try:
        import freelance_server
        db = freelance_server.FreelanceDatabase()
        
        assert len(db.gigs) > 0, "No sample gigs loaded"
        assert len(db.user_profiles) >= 0, "User profiles dict not initialized"
        
        print(f"✓ Database initialized with {len(db.gigs)} sample gigs")
        return True
    except Exception as e:
        print(f"✗ Database test failed: {e}")
        return False

def test_helper_functions():
    """Test helper functions"""
    print("\nTesting helper functions...")
    try:
        from freelance_server import calculate_match_score, check_rate_compatibility
        
        # Test skill matching
        score = calculate_match_score(["Python", "JavaScript"], ["Python", "React"])
        assert 0 <= score <= 1, "Match score out of range"
        
        # Test rate compatibility
        compat = check_rate_compatibility(50, 100, 800, 1500, None)
        assert 0 <= compat <= 1, "Rate compatibility out of range"
        
        print("✓ Helper functions working")
        return True
    except Exception as e:
        print(f"✗ Helper functions test failed: {e}")
        return False

def test_tool_decorators():
    """Test that tools are properly decorated"""
    print("\nTesting MCP tools...")
    try:
        import freelance_server
        
        # Tools should be functions with tool decorator
        tools = [
            'search_gigs',
            'validate',
            'analyze_profile_fit',
            'generate_proposal',
            'negotiate_rate',
            'create_user_profile',
            'code_review',
            'code_debug',
            'optimize_profile',
            'track_application_status'
        ]
        
        for tool_name in tools:
            assert hasattr(freelance_server, tool_name), f"Tool {tool_name} not found"
        
        print(f"✓ All {len(tools)} tools found")
        return True
    except Exception as e:
        print(f"✗ Tool decorator test failed: {e}")
        return False

def test_environment():
    """Test environment configuration"""
    print("\nTesting environment...")
    try:
        from dotenv import load_dotenv
        import os
        
        load_dotenv()
        
        has_groq = bool(os.getenv("GROQ_API_KEY"))
        has_phone = bool(os.getenv("OWNER_PHONE_NUMBER"))
        
        if has_groq:
            print("✓ GROQ_API_KEY configured")
        else:
            print("⚠ GROQ_API_KEY not set (LLM features will not work)")
        
        if has_phone:
            print("✓ OWNER_PHONE_NUMBER configured")
        else:
            print("⚠ OWNER_PHONE_NUMBER not set (validate tool will fail)")
        
        return True
    except Exception as e:
        print(f"✗ Environment test failed: {e}")
        return False

def run_all_tests():
    """Run all diagnostic tests"""
    print("=" * 60)
    print("FREELANCE MCP SERVER - COMPREHENSIVE DEBUG TEST")
    print("=" * 60)
    
    results = []
    
    results.append(("Imports", test_imports()))
    results.append(("Server Module", test_server_module()))
    results.append(("Database", test_database()))
    results.append(("Helper Functions", test_helper_functions()))
    results.append(("MCP Tools", test_tool_decorators()))
    results.append(("Environment", test_environment()))
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "PASS" if result else "FAIL"
        symbol = "✓" if result else "✗"
        print(f"{symbol} {name:.<45} {status}")
    
    print("=" * 60)
    print(f"RESULTS: {passed}/{total} tests passed")
    print("=" * 60)
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED - Server is ready!")
        return 0
    else:
        print(f"\n⚠ {total - passed} test(s) failed - Check errors above")
        return 1

if __name__ == "__main__":
    sys.exit(run_all_tests())
