#!/usr/bin/env python3
"""
Simple test script to verify the server can start
"""
import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # Test importing our modules
    from app.config import get_settings
    print("✅ Config module imported")
    
    from app.services.odoo_cache_service import OdooCacheService
    print("✅ OdooCacheService imported")
    
    from app.controllers.menu import router
    print("✅ Menu controller imported")
    
    from app.main import app
    print("✅ FastAPI app imported")
    
    # Test settings
    settings = get_settings()
    print(f"✅ Settings loaded - Odoo URL: {settings.ODOO_URL}")
    
    # Test cache service instantiation
    if settings.ODOO_API_KEY:
        cache_service = OdooCacheService(
            odoo_url=settings.ODOO_URL,
            db=settings.ODOO_DB,
            username=settings.ODOO_USERNAME,
            api_key=settings.ODOO_API_KEY
        )
        print(f"✅ Using API key authentication (ending in ...{settings.ODOO_API_KEY[-4:]})")
    else:
        cache_service = OdooCacheService(
            odoo_url=settings.ODOO_URL,
            db=settings.ODOO_DB,
            username=settings.ODOO_USERNAME,
            password=settings.ODOO_PASSWORD
        )
        print("✅ Using username/password authentication")
    print("✅ Cache service created")
    
    print("\n🎉 All tests passed! Server should start correctly.")
    print("To start the server, run:")
    print("  python3 test_server.py --server")
    
    # Check if we should start the server
    if len(sys.argv) > 1 and sys.argv[1] == '--server':
        print("\n🚀 Starting server...")
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure all dependencies are installed:")
    print("  pip3 install fastapi uvicorn pydantic-settings python-dotenv Pillow")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()