"""
Simple test script to validate the RSS News Agent setup
"""
import sys
import os

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test basic imports without external dependencies"""
    print("🧪 Testing RSS News Agent imports...")
    
    try:
        # Test basic Python imports
        import json
        import logging
        import datetime
        print("✓ Basic Python modules imported")
    except Exception as e:
        print(f"✗ Basic Python modules failed: {e}")
        return False
    
    try:
        # Test project structure
        import rss_agent
        print("✓ RSS Agent package structure valid")
    except Exception as e:
        print(f"✗ RSS Agent package structure invalid: {e}")
        return False
    
    print("✅ Basic imports successful!")
    return True

def test_files():
    """Test that all required files exist"""
    print("📁 Testing file structure...")
    
    required_files = [
        "rss_agent/__init__.py",
        "rss_agent/config.py",
        "rss_agent/scraper.py", 
        "rss_agent/analyzer.py",
        "rss_agent/email_service.py",
        "rss_agent/mcp_integration.py",
        "rss_agent/agent.py",
        "main.py",
        "requirements.txt",
        ".env.example",
        ".gitignore",
        "setup.sh",
        "README.md"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print(f"✗ Missing files: {missing_files}")
        return False
    
    print("✓ All required files present")
    return True

def main():
    """Run all tests"""
    print("🚀 RSS News Agent - Setup Validation")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 2
    
    if test_files():
        tests_passed += 1
    
    if test_imports():
        tests_passed += 1
    
    print("=" * 50)
    print(f"Tests passed: {tests_passed}/{total_tests}")
    
    if tests_passed == total_tests:
        print("✅ Setup validation complete!")
        print("\nNext steps:")
        print("1. Run: ./setup.sh")
        print("2. Edit .env file with your credentials")
        print("3. Test: python main.py --test")
        return True
    else:
        print("❌ Setup validation failed!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)