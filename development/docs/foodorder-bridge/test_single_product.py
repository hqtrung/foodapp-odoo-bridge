#!/usr/bin/env python3
"""
Test translation with just one product to verify the approach works
"""

import json
import sys
from pathlib import Path
from app.services.base_translation_service import BaseTranslationService

def test_single_product():
    """Test translation with just one product"""
    try:
        print("🔄 Testing single product translation...")
        translation_service = BaseTranslationService()
        
        if not translation_service.is_translation_enabled():
            print("❌ Translation service not available")
            return False
        
        # Get a simple product from the base content
        base_content = translation_service.get_base_content()
        all_products = base_content.get('products', [])
        
        # Find a simple product with minimal attributes
        simple_product = None
        for product in all_products:
            if len(product.get('attributes', [])) == 0:  # Product with no attributes
                simple_product = product
                break
        
        if not simple_product:
            # Use the first product if no simple one found
            simple_product = all_products[0] if all_products else None
        
        if not simple_product:
            print("❌ No products found in base content")
            return False
        
        print(f"📝 Testing with product: {simple_product.get('product_name', 'Unknown')}")
        print(f"    - Attributes: {len(simple_product.get('attributes', []))}")
        
        # Create test content with just categories and one product
        test_content = {
            'source_language': 'vi',
            'categories': base_content.get('categories', []),
            'products': [simple_product]
        }
        
        print(f"📊 Test content:")
        print(f"  - Categories: {len(test_content['categories'])}")
        print(f"  - Products: {len(test_content['products'])}")
        
        # Test translation to English
        translation_service.base_content = test_content  # Temporarily override
        
        print(f"\n🔄 Testing English translation...")
        result = translation_service.translate_to_language('en')
        
        if result:
            print(f"✅ English translation successful!")
            print(f"  - Categories: {len(result.get('categories', []))}")
            print(f"  - Products: {len(result.get('products', []))}")
            
            # Show translated product
            if result.get('products'):
                translated_product = result['products'][0]
                print(f"\n🍽️ Translated product:")
                print(f"  - Original: {simple_product.get('product_name', 'N/A')}")
                print(f"  - Translated: {translated_product.get('product_name', 'N/A')}")
            
            # Show translated categories
            if result.get('categories'):
                print(f"\n📋 Sample translated categories:")
                for i, cat in enumerate(result['categories'][:3]):
                    original_cat = test_content['categories'][i] if i < len(test_content['categories']) else {}
                    print(f"  {i+1}. {original_cat.get('category_name', 'N/A')} → {cat.get('category_name', 'N/A')}")
            
            # Save result
            output_path = Path('single_product_translation.json')
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"\n💾 Translation saved to {output_path}")
            
            return True
        else:
            print("❌ English translation failed")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_single_product()
    sys.exit(0 if success else 1)