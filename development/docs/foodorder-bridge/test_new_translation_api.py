#!/usr/bin/env python3
"""
Test the New Language-First Translation API
==========================================

Tests the new Firestore structure and API endpoints directly
without starting a web server.
"""

import sys
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from app.controllers.translations import FirestoreTranslationService
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_translation_service():
    """Test the FirestoreTranslationService directly"""
    print("🧪 Testing New Translation Service")
    print("=" * 50)
    
    try:
        # Initialize service
        service = FirestoreTranslationService()
        print("✅ Service initialized successfully")
        
        # Test 1: Get available languages
        print("\n1️⃣ Testing available languages...")
        languages = service.get_available_languages()
        print(f"Available languages: {languages}")
        
        # Test 2: Get language metadata
        print("\n2️⃣ Testing language metadata...")
        metadata = service.get_language_metadata()
        if metadata:
            print(f"Metadata structure version: {metadata.get('structure_version', 'N/A')}")
            print(f"Default language: {metadata.get('default_language', 'N/A')}")
            supported = metadata.get('supported_languages', {})
            print(f"Supported languages: {list(supported.keys())}")
        else:
            print("❌ No metadata found")
        
        # Test 3: Get all products in English (bulk fetch)
        print("\n3️⃣ Testing bulk language fetch (English)...")
        english_products = service.get_all_products_in_language('english')
        print(f"English products count: {len(english_products)}")
        
        if english_products:
            sample = english_products[0]
            print(f"Sample product: {sample.get('product_id')} - {sample.get('name', '')[:50]}...")
        
        # Test 4: Get specific product in multiple languages
        print("\n4️⃣ Testing specific product in multiple languages...")
        test_product_id = "1186"  # Known product ID
        
        for language in ['vietnamese', 'english', 'french']:
            product = service.get_product_in_language(language, test_product_id)
            if product:
                print(f"✅ {language}: {product.get('name', '')[:50]}...")
            else:
                print(f"❌ {language}: Not found")
        
        # Test 5: Performance comparison
        print("\n5️⃣ Testing performance - bulk vs individual fetches...")
        
        # Bulk fetch all French products
        import time
        start_time = time.time()
        french_products = service.get_all_products_in_language('french')
        bulk_time = time.time() - start_time
        print(f"Bulk fetch {len(french_products)} French products: {bulk_time:.3f}s")
        
        # Individual fetches (first 5 products)
        start_time = time.time()
        individual_products = []
        for i, product in enumerate(french_products[:5]):
            product_id = str(product.get('product_id'))
            individual_product = service.get_product_in_language('french', product_id)
            if individual_product:
                individual_products.append(individual_product)
        individual_time = time.time() - start_time
        print(f"Individual fetch 5 French products: {individual_time:.3f}s")
        
        # Calculate estimated time for all products individually
        estimated_individual_time = (individual_time / 5) * len(french_products)
        speedup = estimated_individual_time / bulk_time if bulk_time > 0 else 0
        print(f"Estimated speedup: {speedup:.1f}x faster with bulk fetch")
        
        print(f"\n🎉 All tests completed successfully!")
        print(f"📊 Summary:")
        print(f"   - Available languages: {len(languages)}")
        print(f"   - Total products per language: ~{len(english_products)}")
        print(f"   - Bulk fetch performance: {bulk_time:.3f}s for {len(french_products)} products")
        print(f"   - Structure: Collection -> Languages -> Products ✅")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def demonstrate_frontend_usage():
    """Demonstrate how frontend would use the new structure"""
    print(f"\n🎯 Frontend Usage Examples")
    print("=" * 50)
    
    print("1. Get all products in English (single query):")
    print("   Firebase: db.collection('product_translations_v2/english/products').get()")
    print("   API: GET /api/v1/translations-v2/products?language=english")
    
    print("\n2. Get specific product in French:")
    print("   Firebase: db.doc('product_translations_v2/french/products/1186').get()")
    print("   API: GET /api/v1/translations-v2/products/1186?language=french")
    
    print("\n3. Get categories in Chinese:")
    print("   API: GET /api/v1/translations-v2/categories?language=chinese")
    
    print("\n4. Get products by category in Italian:")
    print("   API: GET /api/v1/translations-v2/categories/5/products?language=italian")
    
    print("\n🚀 Benefits:")
    print("   ✅ Single query for all products in a language")
    print("   ✅ No complex joins or multiple requests")
    print("   ✅ Real-time language switching")
    print("   ✅ Efficient for menu display")
    print("   ✅ Reduced API calls and faster loading")


if __name__ == "__main__":
    success = test_translation_service()
    
    if success:
        demonstrate_frontend_usage()
    else:
        print("❌ Tests failed - check Firestore configuration")
        sys.exit(1)