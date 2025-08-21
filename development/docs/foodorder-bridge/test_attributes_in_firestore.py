#!/usr/bin/env python3
"""
Test Attributes in Firestore Translation System
==============================================

Test that attributes are properly included in the uploaded translations
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


def test_attributes_in_firestore():
    """Test that attributes are included in Firestore translations"""
    print("🧪 Testing Attributes in Firestore Translations")
    print("=" * 60)
    
    try:
        # Initialize service
        service = FirestoreTranslationService()
        print("✅ Service initialized successfully")
        
        # Test 1: Check if Vietnamese has attributes 
        print("\n1️⃣ Testing Vietnamese attributes...")
        vi_products = service.get_all_products_in_language('vi')
        
        products_with_attributes = [p for p in vi_products if p.get('attributes') and len(p.get('attributes', [])) > 0]
        print(f"Vietnamese products with attributes: {len(products_with_attributes)}/{len(vi_products)}")
        
        if products_with_attributes:
            sample = products_with_attributes[0]
            print(f"Sample Vietnamese product with attributes:")
            print(f"   Product: #{sample.get('product_id')} - {sample.get('name', '')}")
            print(f"   Attributes count: {len(sample.get('attributes', []))}")
            
            # Show first attribute
            first_attr = sample.get('attributes', [])[0]
            print(f"   First attribute: {first_attr.get('attribute_name', '')}")
            print(f"   Values count: {len(first_attr.get('values', []))}")
            if first_attr.get('values'):
                print(f"   First value: {first_attr['values'][0].get('name', '')}")
        
        # Test 2: Check English attributes (should be translated)
        print("\n2️⃣ Testing English attributes...")
        en_products = service.get_all_products_in_language('en')
        
        en_products_with_attributes = [p for p in en_products if p.get('attributes') and len(p.get('attributes', [])) > 0]
        print(f"English products with attributes: {len(en_products_with_attributes)}/{len(en_products)}")
        
        if en_products_with_attributes:
            sample = en_products_with_attributes[0]
            print(f"Sample English product with attributes:")
            print(f"   Product: #{sample.get('product_id')} - {sample.get('name', '')}")
            print(f"   Attributes count: {len(sample.get('attributes', []))}")
            
            # Show first attribute
            first_attr = sample.get('attributes', [])[0]
            print(f"   First attribute: {first_attr.get('attribute_name', '')} (should be translated)")
            if first_attr.get('values'):
                print(f"   First value: {first_attr['values'][0].get('name', '')} (should be translated)")
        
        # Test 3: Compare same product across languages
        print("\n3️⃣ Testing same product across languages...")
        
        # Find a product with attributes in Vietnamese
        if products_with_attributes:
            test_product_id = str(products_with_attributes[0].get('product_id'))
            print(f"Testing product {test_product_id} across all languages:")
            
            for lang_code in ['vi', 'en', 'fr', 'it', 'cn', 'ja']:
                product = service.get_product_in_language(lang_code, test_product_id)
                
                if product:
                    attr_count = len(product.get('attributes', []))
                    lang_name = product.get('language_name', lang_code)
                    
                    print(f"   {lang_code} ({lang_name}): {attr_count} attributes")
                    
                    if attr_count > 0:
                        first_attr = product['attributes'][0]
                        attr_name = first_attr.get('attribute_name', '')
                        values_count = len(first_attr.get('values', []))
                        print(f"      First attribute: '{attr_name}' ({values_count} values)")
                        
                        if values_count > 0:
                            first_value = first_attr['values'][0].get('name', '')
                            print(f"      First value: '{first_value}'")
                else:
                    print(f"   {lang_code}: Product not found")
        
        # Test 4: Check if attributes are properly translated
        print("\n4️⃣ Checking translation quality...")
        
        if products_with_attributes and en_products_with_attributes:
            vi_product = products_with_attributes[0]
            en_product = next((p for p in en_products_with_attributes if p.get('product_id') == vi_product.get('product_id')), None)
            
            if en_product:
                print("Comparing Vietnamese vs English attributes:")
                
                vi_attr = vi_product['attributes'][0]
                en_attr = en_product['attributes'][0]
                
                print(f"   Vietnamese attribute: '{vi_attr.get('attribute_name', '')}'")
                print(f"   English attribute: '{en_attr.get('attribute_name', '')}'")
                
                if vi_attr.get('values') and en_attr.get('values'):
                    vi_value = vi_attr['values'][0].get('name', '')
                    en_value = en_attr['values'][0].get('name', '')
                    
                    print(f"   Vietnamese value: '{vi_value}'")
                    print(f"   English value: '{en_value}'")
                    
                    # Check if translation actually happened
                    if vi_attr.get('attribute_name') == en_attr.get('attribute_name'):
                        print("   ⚠️  Attribute name NOT translated (still in Vietnamese)")
                    else:
                        print("   ✅ Attribute name translated")
                    
                    if vi_value == en_value:
                        print("   ⚠️  Value NOT translated (still in Vietnamese)")
                    else:
                        print("   ✅ Value translated")
        
        print(f"\n🎉 Attributes test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    test_attributes_in_firestore()