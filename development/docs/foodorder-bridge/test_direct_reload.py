#!/usr/bin/env python3
"""
Direct test of OdooCacheService reload functionality
"""
import sys
sys.path.insert(0, '.')

from app.services.odoo_cache_service import OdooCacheService
from app.config import get_settings

def test_direct_reload():
    print("🧪 Testing OdooCacheService directly")
    print("=" * 50)
    
    # Get settings
    settings = get_settings()
    print(f"Odoo URL: {settings.ODOO_URL}")
    print(f"Database: {settings.ODOO_DB}")
    print(f"Username: {settings.ODOO_USERNAME}")
    print(f"Using API Key: {'Yes' if settings.ODOO_API_KEY else 'No'}")
    print()
    
    try:
        # Create service instance
        service = OdooCacheService(
            odoo_url=settings.ODOO_URL,
            db=settings.ODOO_DB,
            username=settings.ODOO_USERNAME,
            api_key=settings.ODOO_API_KEY
        )
        
        print("✅ Service created successfully")
        print("🔄 Starting cache reload...")
        
        # Attempt reload
        result = service.reload_cache()
        
        print(f"✅ Cache reload successful!")
        print(f"   Categories: {result.get('categories_count', 0)}")
        print(f"   Products: {result.get('products_count', 0)}")
        print(f"   Updated: {result.get('updated_at', 'unknown')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during reload: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_direct_reload()