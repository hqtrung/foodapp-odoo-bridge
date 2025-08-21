#!/usr/bin/env python3
"""
Test the corrected single-shot translation with increased max_output_tokens
"""

import json
import sys
import time
from pathlib import Path
from app.services.base_translation_service import BaseTranslationService

def test_corrected_translation():
    """Test full Vietnamese to English translation in single API call"""
    try:
        print("🔄 Testing corrected single-shot translation...")
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
        print(f"  - Content size: ~21,647 characters")
        
        print(f"\n🔧 Fixed configuration:")
        print(f"  - max_output_tokens: 8192 (was 2048)")
        print(f"  - Single API call instead of {1 + products_count} chunked calls")
        print(f"  - Expected response: ~25,000 characters")
        
        print(f"\n🔄 Starting single-shot English translation...")
        start_time = time.time()
        
        # Perform the translation
        result = translation_service.translate_to_language('en')
        
        end_time = time.time()
        duration = end_time - start_time
        
        if result:
            print(f"\n✅ English translation completed successfully!")
            print(f"⏱️  Translation time: {duration:.1f} seconds (single API call)")
            
            # Validate results
            result_categories = len(result.get('categories', []))
            result_products = len(result.get('products', []))
            
            print(f"📊 Translation results:")
            print(f"  - Categories: {result_categories}/{categories_count} ✅")
            print(f"  - Products: {result_products}/{products_count} ✅")
            
            if result_categories == categories_count and result_products == products_count:
                print("🎉 Perfect! All content translated in single API call!")
            else:
                print("⚠️  Some content may be missing")
                return False
            
            # Show sample translations
            print(f"\n📋 Translated categories:")
            for i, category in enumerate(result.get('categories', [])):
                original = base_content['categories'][i] if i < len(base_content['categories']) else {}
                print(f"  {i+1}. {original.get('category_name', 'N/A')} → {category.get('category_name', 'N/A')}")
            
            print(f"\n🍽️ Sample translated products:")
            sample_products = result.get('products', [])[:5]
            original_products = base_content.get('products', [])[:5]
            
            for i, (orig, trans) in enumerate(zip(original_products, sample_products)):
                print(f"  {i+1}. {orig.get('product_name', 'N/A')} → {trans.get('product_name', 'N/A')}")
                
                # Show attribute example if available
                if orig.get('attributes') and trans.get('attributes'):
                    orig_attr = orig['attributes'][0]
                    trans_attr = trans['attributes'][0]
                    print(f"     • {orig_attr.get('attribute_name', 'N/A')} → {trans_attr.get('attribute_name', 'N/A')}")
                    
                    if orig_attr.get('attribute_values') and trans_attr.get('attribute_values'):
                        orig_val = orig_attr['attribute_values'][0]
                        trans_val = trans_attr['attribute_values'][0]
                        print(f"       - {orig_val.get('value_name', 'N/A')} → {trans_val.get('value_name', 'N/A')}")
            
            # Performance comparison
            old_approach_time = (1 + products_count) * 7.2  # Estimated chunked approach time
            improvement = old_approach_time / duration
            
            print(f"\n📈 Performance improvement:")
            print(f"  - Old chunked approach: ~{old_approach_time/60:.1f} minutes ({1 + products_count} API calls)")
            print(f"  - New single-shot: {duration:.1f} seconds (1 API call)")
            print(f"  - Speed improvement: {improvement:.0f}x faster!")
            print(f"  - Cost reduction: {1 + products_count}x fewer API calls")
            
            # Save the English translation
            output_path = Path('app/data/english_menu_translation.json')
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            print(f"\n💾 English translation saved to: {output_path}")
            
            # Also save to root for easy access
            root_output = Path('english_menu_complete.json')
            with open(root_output, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            print(f"💾 Copy also saved to: {root_output}")
            print(f"📄 File size: {root_output.stat().st_size:,} bytes")
            
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
    success = test_corrected_translation()
    sys.exit(0 if success else 1)