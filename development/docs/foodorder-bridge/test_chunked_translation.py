#!/usr/bin/env python3
"""
Test chunked translation service
"""

import json
import sys
from pathlib import Path
from app.services.base_translation_service import BaseTranslationService

def test_chunked_translation():
    """Test chunked translation with single language"""
    try:
        print("🔄 Testing chunked translation service...")
        translation_service = BaseTranslationService()
        
        if not translation_service.is_translation_enabled():
            print("❌ Translation service not available")
            return False
        
        # Show base content stats
        base_content = translation_service.get_base_content()
        print(f"📊 Vietnamese base content:")
        print(f"  - Categories: {len(base_content.get('categories', []))}")
        print(f"  - Products: {len(base_content.get('products', []))}")
        
        # Test English translation
        print(f"\n🔄 Testing chunked translation to English...")
        result = translation_service.translate_to_language('en')
        
        if result:
            print(f"✅ English translation successful")
            print(f"  - Categories: {len(result.get('categories', []))}")
            print(f"  - Products: {len(result.get('products', []))}")
            
            # Show samples
            if result.get('categories'):
                print(f"\n📋 Sample translated categories:")
                for i, cat in enumerate(result['categories'][:3]):
                    print(f"  {i+1}. {cat.get('category_name', 'N/A')}")
            
            if result.get('products'):
                print(f"\n🍽️ Sample translated products:")
                for i, prod in enumerate(result['products'][:5]):
                    print(f"  {i+1}. {prod.get('product_name', 'N/A')}")
                    if prod.get('attributes'):
                        for attr in prod['attributes'][:1]:  # Show first attribute
                            print(f"      - {attr.get('attribute_name', 'N/A')}")
                            if attr.get('attribute_values'):
                                for val in attr['attribute_values'][:2]:  # Show first 2 values
                                    print(f"        * {val.get('value_name', 'N/A')}")
            
            # Save result to file for inspection
            output_path = Path('english_translation_result.json')
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"\n💾 English translation saved to {output_path}")
            
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
    success = test_chunked_translation()
    sys.exit(0 if success else 1)