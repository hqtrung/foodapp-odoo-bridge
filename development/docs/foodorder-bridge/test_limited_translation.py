#!/usr/bin/env python3
"""
Test translation with limited number of products to verify scalability
"""

import json
import sys
from pathlib import Path
from app.services.base_translation_service import BaseTranslationService

def test_limited_translation():
    """Test translation with first 5 products only"""
    try:
        print("🔄 Testing limited translation (5 products)...")
        translation_service = BaseTranslationService()
        
        if not translation_service.is_translation_enabled():
            print("❌ Translation service not available")
            return False
        
        # Get limited content
        base_content = translation_service.get_base_content()
        all_products = base_content.get('products', [])
        
        # Take only first 5 products
        limited_products = all_products[:5]
        
        print(f"📊 Limited content:")
        print(f"  - Categories: {len(base_content.get('categories', []))}")
        print(f"  - Products: {len(limited_products)} (out of {len(all_products)} total)")
        
        # Show which products we're testing
        print(f"\n📝 Products to translate:")
        for i, product in enumerate(limited_products):
            attrs_count = len(product.get('attributes', []))
            print(f"  {i+1}. {product.get('product_name', 'Unknown')} ({attrs_count} attributes)")
        
        # Create limited content
        limited_content = {
            'source_language': 'vi',
            'categories': base_content.get('categories', []),
            'products': limited_products
        }
        
        # Temporarily override base content
        original_content = translation_service.base_content
        translation_service.base_content = limited_content
        
        try:
            print(f"\n🔄 Testing English translation with chunked approach...")
            result = translation_service.translate_to_language('en')
            
            if result:
                print(f"✅ English translation successful!")
                print(f"  - Categories: {len(result.get('categories', []))}")
                print(f"  - Products: {len(result.get('products', []))}")
                
                # Show translated products
                if result.get('products'):
                    print(f"\n🍽️ Translated products:")
                    for i, (orig, trans) in enumerate(zip(limited_products, result['products'])):
                        print(f"  {i+1}. {orig.get('product_name', 'N/A')} → {trans.get('product_name', 'N/A')}")
                
                # Save result
                output_path = Path('limited_translation_result.json')
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
                print(f"\n💾 Translation saved to {output_path}")
                
                return True
            else:
                print("❌ English translation failed")
                return False
        
        finally:
            # Restore original content
            translation_service.base_content = original_content
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_limited_translation()
    sys.exit(0 if success else 1)