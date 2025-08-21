#!/usr/bin/env python3
"""
Translate the full Vietnamese menu to English
"""

import json
import sys
import time
from pathlib import Path
from app.services.base_translation_service import BaseTranslationService

def translate_to_english():
    """Translate full Vietnamese content to English"""
    try:
        print("🔄 Starting full Vietnamese to English translation...")
        translation_service = BaseTranslationService()
        
        if not translation_service.is_translation_enabled():
            print("❌ Translation service not available")
            return False
        
        # Show content stats
        base_content = translation_service.get_base_content()
        categories_count = len(base_content.get('categories', []))
        products_count = len(base_content.get('products', []))
        
        print(f"📊 Vietnamese menu content:")
        print(f"  - Categories: {categories_count}")
        print(f"  - Products: {products_count}")
        
        # Calculate estimates
        estimated_calls = 1 + products_count  # 1 for categories + 1 per product
        estimated_time_minutes = (estimated_calls * 7.2) / 60  # Based on performance test
        
        print(f"\n📏 Translation plan:")
        print(f"  - Total API calls: {estimated_calls}")
        print(f"  - Estimated time: {estimated_time_minutes:.1f} minutes")
        print(f"  - Processing: Categories first, then products one-by-one")
        
        print(f"\n🔄 Starting English translation...")
        start_time = time.time()
        
        # Perform the translation
        result = translation_service.translate_to_language('en')
        
        end_time = time.time()
        duration = end_time - start_time
        
        if result:
            print(f"\n✅ English translation completed successfully!")
            print(f"⏱️  Total time: {duration:.1f} seconds ({duration/60:.1f} minutes)")
            
            # Validate results
            result_categories = len(result.get('categories', []))
            result_products = len(result.get('products', []))
            
            print(f"📊 Translation results:")
            print(f"  - Categories: {result_categories} (expected: {categories_count})")
            print(f"  - Products: {result_products} (expected: {products_count})")
            
            if result_categories == categories_count and result_products == products_count:
                print("✅ All content translated successfully!")
            else:
                print("⚠️  Some content may be missing")
            
            # Show sample translations
            print(f"\n📋 Translated categories:")
            for i, category in enumerate(result.get('categories', [])[:7]):
                original = base_content['categories'][i] if i < len(base_content['categories']) else {}
                print(f"  {i+1}. {original.get('category_name', 'N/A')} → {category.get('category_name', 'N/A')}")
            
            print(f"\n🍽️ Sample translated products:")
            sample_products = result.get('products', [])[:10]
            original_products = base_content.get('products', [])[:10]
            
            for i, (orig, trans) in enumerate(zip(original_products, sample_products)):
                print(f"  {i+1}. {orig.get('product_name', 'N/A')} → {trans.get('product_name', 'N/A')}")
                
                # Show attribute example
                if orig.get('attributes') and trans.get('attributes'):
                    orig_attr = orig['attributes'][0]
                    trans_attr = trans['attributes'][0]
                    print(f"     • {orig_attr.get('attribute_name', 'N/A')} → {trans_attr.get('attribute_name', 'N/A')}")
                    
                    if orig_attr.get('attribute_values') and trans_attr.get('attribute_values'):
                        orig_val = orig_attr['attribute_values'][0]
                        trans_val = trans_attr['attribute_values'][0]
                        print(f"       - {orig_val.get('value_name', 'N/A')} → {trans_val.get('value_name', 'N/A')}")
            
            # Save the English translation
            output_path = Path('app/data/english_menu_translation.json')
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            print(f"\n💾 English translation saved to: {output_path}")
            print(f"📄 File size: {output_path.stat().st_size:,} bytes")
            
            # Also save to root for easy access
            root_output = Path('english_menu_complete.json')
            with open(root_output, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            print(f"💾 Copy also saved to: {root_output}")
            
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
    success = translate_to_english()
    sys.exit(0 if success else 1)