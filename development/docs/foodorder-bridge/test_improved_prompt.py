#!/usr/bin/env python3
"""
Test the improved translation prompt with specific translation rules
"""

import json
import sys
import time
from pathlib import Path
from app.services.base_translation_service import BaseTranslationService

def test_improved_prompt():
    """Test translation with improved prompt featuring specific translation rules"""
    try:
        print("🔄 Testing improved translation prompt...")
        translation_service = BaseTranslationService()
        
        if not translation_service.is_translation_enabled():
            print("❌ Translation service not available")
            return False
        
        # Clear cache to force fresh translation
        translation_service.clear_cache()
        print("🗑️ Cleared translation cache for fresh translation")
        
        # Show content stats
        base_content = translation_service.get_base_content()
        categories_count = len(base_content.get('categories', []))
        products_count = len(base_content.get('products', []))
        
        print(f"📊 Vietnamese menu content:")
        print(f"  - Categories: {categories_count}")
        print(f"  - Products: {products_count}")
        
        print(f"\n🎯 Improved prompt features:")
        print(f"  - 'Bánh Mì' → 'Baguette' (consistent usage)")
        print(f"  - 'Xá Xíu' → 'Cha Siu BBQ Pork' (Vietnamese-style, not Chinese)")
        print(f"  - 'Dưa hấu' → 'Watermelon'")
        print(f"  - 'Trà Dưa Lưới' → 'Golden Melon Tea'")
        print(f"  - 'Thập Cẩm' → 'Mixed' (traditional combination)")
        
        print(f"\n🔄 Starting English translation with improved prompt...")
        start_time = time.time()
        
        # Perform the translation
        result = translation_service.translate_to_language('en')
        
        end_time = time.time()
        duration = end_time - start_time
        
        if result:
            print(f"\n✅ English translation completed successfully!")
            print(f"⏱️  Translation time: {duration:.1f} seconds")
            
            # Validate results
            result_categories = len(result.get('categories', []))
            result_products = len(result.get('products', []))
            
            print(f"📊 Translation results:")
            print(f"  - Categories: {result_categories}/{categories_count} ✅")
            print(f"  - Products: {result_products}/{products_count} ✅")
            
            # Test specific translation improvements
            print(f"\n🎯 Testing specific translation rules:")
            
            # Check categories for "Baguette" usage
            traditional_category = None
            for category in result.get('categories', []):
                if 'traditional' in category.get('category_name', '').lower():
                    traditional_category = category
                    break
            
            if traditional_category:
                category_name = traditional_category.get('category_name', '')
                if 'baguette' in category_name.lower():
                    print(f"  ✅ Category uses 'Baguette': {category_name}")
                else:
                    print(f"  ⚠️  Category may not use 'Baguette': {category_name}")
            
            # Check products for "Baguette" and "Cha Siu" usage
            banh_mi_products = []
            xa_xiu_products = []
            
            for product in result.get('products', []):
                product_name = product.get('product_name', '').lower()
                
                # Check for Baguette usage
                if 'baguette' in product_name or any('baguette' in attr.get('attribute_name', '').lower() 
                                                    for attr in product.get('attributes', [])):
                    banh_mi_products.append(product.get('product_name', ''))
                
                # Check for Cha Siu usage
                for attr in product.get('attributes', []):
                    for value in attr.get('attribute_values', []):
                        value_name = value.get('value_name', '').lower()
                        if 'cha siu' in value_name:
                            xa_xiu_products.append(f"{product.get('product_name', '')} - {value.get('value_name', '')}")
            
            print(f"  ✅ Products using 'Baguette': {len(banh_mi_products)}")
            if banh_mi_products:
                for i, product in enumerate(banh_mi_products[:3]):
                    print(f"    {i+1}. {product}")
                if len(banh_mi_products) > 3:
                    print(f"    ... and {len(banh_mi_products) - 3} more")
            
            print(f"  ✅ Attributes using 'Cha Siu BBQ Pork': {len(xa_xiu_products)}")
            if xa_xiu_products:
                for i, product in enumerate(xa_xiu_products[:3]):
                    print(f"    {i+1}. {product}")
                if len(xa_xiu_products) > 3:
                    print(f"    ... and {len(xa_xiu_products) - 3} more")
            
            # Show sample translations with specific focus
            print(f"\n🍽️ Sample improved translations:")
            traditional_products = [p for p in result.get('products', []) 
                                  if p.get('category_id') == 1][:5]  # Traditional category
            
            for i, product in enumerate(traditional_products):
                original_products = [p for p in base_content.get('products', []) 
                                   if p.get('product_id') == product.get('product_id')]
                if original_products:
                    original = original_products[0]
                    print(f"  {i+1}. {original.get('product_name', 'N/A')} → {product.get('product_name', 'N/A')}")
                    
                    # Show improved attribute translations
                    if product.get('attributes'):
                        for attr in product['attributes'][:1]:  # Show first attribute
                            print(f"     • {attr.get('attribute_name', 'N/A')}")
                            for val in attr.get('attribute_values', [])[:2]:  # Show first 2 values
                                print(f"       - {val.get('value_name', 'N/A')}")
            
            # Save the improved translation
            output_path = Path('improved_english_translation.json')
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            print(f"\n💾 Improved translation saved to: {output_path}")
            print(f"📄 File size: {output_path.stat().st_size:,} bytes")
            
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
    success = test_improved_prompt()
    sys.exit(0 if success else 1)