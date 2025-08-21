#!/usr/bin/env python3
"""
Test full translation service for all 5 target languages
"""

import json
import sys
from pathlib import Path
from app.services.base_translation_service import BaseTranslationService

def test_full_translation():
    """Test translation with full Vietnamese content"""
    try:
        print("🔄 Testing full translation service...")
        translation_service = BaseTranslationService()
        
        if not translation_service.is_translation_enabled():
            print("❌ Translation service not available")
            return False
        
        # Show base content stats
        base_content = translation_service.get_base_content()
        print(f"📊 Vietnamese base content:")
        print(f"  - Categories: {len(base_content.get('categories', []))}")
        print(f"  - Products: {len(base_content.get('products', []))}")
        
        # Test each language
        target_languages = ['en', 'it', 'fr', 'zh', 'ja']
        success_count = 0
        
        for lang in target_languages:
            print(f"\n🔄 Testing translation to {lang.upper()}...")
            try:
                result = translation_service.translate_to_language(lang)
                
                if result:
                    print(f"✅ {lang.upper()} translation successful")
                    print(f"  - Categories: {len(result.get('categories', []))}")
                    print(f"  - Products: {len(result.get('products', []))}")
                    
                    # Show sample translation
                    if result.get('categories'):
                        first_category = result['categories'][0]
                        print(f"  - Sample category: {first_category.get('category_name', 'N/A')}")
                    
                    if result.get('products'):
                        first_product = result['products'][0]
                        print(f"  - Sample product: {first_product.get('product_name', 'N/A')}")
                    
                    success_count += 1
                else:
                    print(f"❌ {lang.upper()} translation failed")
                    
            except Exception as e:
                print(f"❌ Error translating to {lang.upper()}: {e}")
        
        print(f"\n📊 Translation results: {success_count}/{len(target_languages)} languages successful")
        
        if success_count == len(target_languages):
            print("✅ All translations completed successfully!")
            
            # Test saving to file
            print("\n💾 Testing save to file...")
            if translation_service.save_translations_to_file("test_translations.json"):
                print("✅ Translations saved successfully")
                
                # Check file exists
                output_path = Path(__file__).parent / 'app' / 'data' / 'test_translations.json'
                if output_path.exists():
                    file_size = output_path.stat().st_size
                    print(f"📄 File created: {output_path} ({file_size:,} bytes)")
                    return True
                else:
                    print("❌ Translation file was not created")
                    return False
            else:
                print("❌ Failed to save translations")
                return False
        else:
            print(f"⚠️ Only {success_count} out of {len(target_languages)} translations were successful")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_full_translation()
    sys.exit(0 if success else 1)