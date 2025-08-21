#!/usr/bin/env python3
"""
Test the 2-Letter Language Code API
=================================

Tests the updated API endpoints with 2-letter language codes
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from app.controllers.translations import FirestoreTranslationService
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_2letter_api():
    """Test the API with 2-letter language codes"""
    print("🧪 Testing 2-Letter Language Code API")
    print("=" * 50)
    
    try:
        # Initialize service
        service = FirestoreTranslationService()
        print("✅ Service initialized successfully")
        
        # Test 1: Get available languages (should now be 2-letter codes)
        print("\n1️⃣ Testing available 2-letter language codes...")
        languages = service.get_available_languages()
        print(f"Available language codes: {languages}")
        
        # Filter to only 2-letter codes
        two_letter_codes = [lang for lang in languages if len(lang) == 2]
        print(f"2-letter codes only: {two_letter_codes}")
        
        # Test 2: Get products using 2-letter codes
        print("\n2️⃣ Testing bulk fetch with 2-letter codes...")
        for lang_code in ['vi', 'en', 'fr']:
            products = service.get_all_products_in_language(lang_code)
            print(f"✅ {lang_code}: {len(products)} products")
            
            if products:
                sample = products[0]
                print(f"   Sample: #{sample.get('product_id')} - {sample.get('name', '')[:40]}...")
        
        # Test 3: Get specific product in multiple 2-letter codes
        print("\n3️⃣ Testing specific product across languages...")
        test_product_id = "1186"
        
        for lang_code in ['vi', 'en', 'fr', 'it', 'cn', 'ja']:
            product = service.get_product_in_language(lang_code, test_product_id)
            if product:
                lang_name = product.get('language_name', lang_code)
                print(f"✅ {lang_code} ({lang_name}): {product.get('name', '')}")
            else:
                print(f"❌ {lang_code}: Not found")
        
        # Test 4: Performance test
        print("\n4️⃣ Testing performance with 2-letter codes...")
        import time
        
        start_time = time.time()
        en_products = service.get_all_products_in_language('en')
        en_time = time.time() - start_time
        
        start_time = time.time()
        fr_products = service.get_all_products_in_language('fr')
        fr_time = time.time() - start_time
        
        print(f"English (en): {len(en_products)} products in {en_time:.3f}s")
        print(f"French (fr): {len(fr_products)} products in {fr_time:.3f}s")
        
        # Test 5: Verify data structure
        print("\n5️⃣ Verifying 2-letter code data structure...")
        if en_products:
            sample_product = en_products[0]
            print(f"Sample product structure:")
            print(f"   product_id: {sample_product.get('product_id')}")
            print(f"   language_code: {sample_product.get('language_code')}")
            print(f"   language_name: {sample_product.get('language_name')}")
            print(f"   name: {sample_product.get('name', '')[:30]}...")
            print(f"   price: {sample_product.get('price')}")
        
        print(f"\n🎉 2-Letter Code API Test Complete!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def demonstrate_2letter_usage():
    """Demonstrate the new 2-letter code usage"""
    print(f"\n🎯 2-Letter Code Usage Examples")
    print("=" * 50)
    
    print("✅ Firebase SDK (Direct Access):")
    print("   // Get all English products")
    print("   const products = await db.collection('product_translations_v2/en/products').get();")
    print("   ")
    print("   // Get specific product in French")
    print("   const product = await db.doc('product_translations_v2/fr/products/1186').get();")
    print("   ")
    print("   // Get all Chinese products")
    print("   const cnProducts = await db.collection('product_translations_v2/cn/products').get();")
    
    print("\n✅ API Endpoints:")
    print("   GET /api/v1/translations-v2/products?language=en     # All English products")
    print("   GET /api/v1/translations-v2/products/1186?language=fr  # French product 1186")
    print("   GET /api/v1/translations-v2/categories?language=it     # Italian categories")
    print("   GET /api/v1/translations-v2/categories/5/products?language=cn  # Chinese category 5")
    
    print("\n✅ Language Code Mapping:")
    codes = {
        'vi': 'Tiếng Việt (Vietnamese)',
        'en': 'English', 
        'fr': 'Français (French)',
        'it': 'Italiano (Italian)',
        'cn': '中文 (Chinese)',
        'ja': '日本語 (Japanese)'
    }
    
    for code, name in codes.items():
        print(f"   {code} = {name}")
    
    print("\n🚀 Benefits:")
    print("   ✅ Consistent with international language standards")
    print("   ✅ Shorter, cleaner URLs and collection names")
    print("   ✅ Easier integration with i18n libraries")
    print("   ✅ Standard format for frontend language switching")
    print("   ✅ Reduced payload size in API responses")


if __name__ == "__main__":
    success = test_2letter_api()
    
    if success:
        demonstrate_2letter_usage()
    else:
        print("❌ 2-Letter code tests failed")
        sys.exit(1)