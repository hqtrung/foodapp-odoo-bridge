#!/usr/bin/env python3
"""
Test full English translation with optimized chunking and rate limiting
"""

import json
import sys
import time
from pathlib import Path
from app.services.base_translation_service import BaseTranslationService

def test_full_english_translation():
    """Test full English translation with proper rate limiting"""
    try:
        print("🔄 Testing full English translation with chunked approach...")
        translation_service = BaseTranslationService()
        
        if not translation_service.is_translation_enabled():
            print("❌ Translation service not available")
            return False
        
        # Show full content stats
        base_content = translation_service.get_base_content()
        all_products = base_content.get('products', [])
        
        print(f"📊 Full Vietnamese content:")
        print(f"  - Categories: {len(base_content.get('categories', []))}")
        print(f"  - Products: {len(all_products)}")
        
        # Calculate estimated time (1 call for categories + 53 calls for products + 5s delay each = ~4.5 minutes)
        estimated_calls = 1 + len(all_products)  # 1 for categories + 1 per product
        estimated_time_minutes = (estimated_calls * 5) / 60  # 5 seconds per call
        
        print(f"📏 Translation plan:")
        print(f"  - Total API calls needed: {estimated_calls}")
        print(f"  - Estimated time: {estimated_time_minutes:.1f} minutes")
        print(f"  - Chunk size: 1 product per call")
        print(f"  - Rate limit delay: 5 seconds between calls")
        
        # Ask user if they want to proceed (in a real scenario)
        print(f"\n⚠️  This will make {estimated_calls} API calls to Vertex AI Gemini")
        print(f"⚠️  This may consume significant quota and take {estimated_time_minutes:.1f} minutes")
        
        # For demo purposes, let's translate just 10 products
        demo_limit = 10
        print(f"\n🎯 For this demo, translating first {demo_limit} products only...")
        
        limited_products = all_products[:demo_limit]
        
        # Create limited content for demo
        demo_content = {
            'source_language': 'vi',
            'categories': base_content.get('categories', []),
            'products': limited_products
        }
        
        # Temporarily override base content
        original_content = translation_service.base_content
        translation_service.base_content = demo_content
        
        try:
            print(f"\n🔄 Starting English translation...")
            start_time = time.time()
            
            result = translation_service.translate_to_language('en')
            
            end_time = time.time()
            duration = end_time - start_time
            
            if result:
                print(f"\n✅ English translation completed successfully!")
                print(f"⏱️  Total time: {duration:.1f} seconds ({duration/60:.1f} minutes)")
                print(f"📊 Results:")
                print(f"  - Categories: {len(result.get('categories', []))}")
                print(f"  - Products: {len(result.get('products', []))}")
                
                # Show sample translations
                if result.get('categories'):
                    print(f"\n📋 Sample translated categories:")
                    for i, (orig, trans) in enumerate(zip(demo_content['categories'][:3], result['categories'][:3])):
                        print(f"  {i+1}. {orig.get('category_name', 'N/A')} → {trans.get('category_name', 'N/A')}")
                
                if result.get('products'):
                    print(f"\n🍽️ Sample translated products:")
                    for i, (orig, trans) in enumerate(zip(limited_products[:5], result['products'][:5])):
                        print(f"  {i+1}. {orig.get('product_name', 'N/A')} → {trans.get('product_name', 'N/A')}")
                        
                        # Show attribute translation example
                        if orig.get('attributes') and trans.get('attributes'):
                            orig_attr = orig['attributes'][0]
                            trans_attr = trans['attributes'][0]
                            print(f"     - Attribute: {orig_attr.get('attribute_name', 'N/A')} → {trans_attr.get('attribute_name', 'N/A')}")
                
                # Calculate performance stats
                calls_made = 1 + len(limited_products)  # 1 for categories + 1 per product
                avg_time_per_call = duration / calls_made
                
                print(f"\n📈 Performance stats:")
                print(f"  - API calls made: {calls_made}")
                print(f"  - Average time per call: {avg_time_per_call:.1f}s")
                print(f"  - Estimated time for full {len(all_products)} products: {(1 + len(all_products)) * avg_time_per_call / 60:.1f} minutes")
                
                # Save result
                output_path = Path('full_english_translation_demo.json')
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
    success = test_full_english_translation()
    sys.exit(0 if success else 1)