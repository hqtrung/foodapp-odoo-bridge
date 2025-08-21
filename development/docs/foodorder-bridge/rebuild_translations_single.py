#!/usr/bin/env python3
"""
Rebuild translations one product at a time to avoid token limits
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Any
from app.services.base_translation_service import BaseTranslationService


class SingleProductTranslator:
    """Translate menu one product at a time"""
    
    def __init__(self):
        self.translation_service = BaseTranslationService()
        
    def create_single_product_prompt(self, product: Dict[str, Any], target_language: str) -> str:
        """Create translation prompt for a single product"""
        
        lang_map = {
            'en': 'English',
            'fr': 'French',
            'it': 'Italian',
            'zh': 'Chinese (Simplified)',
            'ja': 'Japanese'
        }
        
        target_lang_name = lang_map.get(target_language, target_language)
        
        return f"""You are translating a Vietnamese bánh mì restaurant menu item from Vietnamese to {target_lang_name}.

**CRITICAL**: Return ONLY valid JSON. No markdown, no code blocks, no explanations.

Translation Rules:
- "Bánh Mì" → "Baguette" (always use "Baguette")
- "Xá Xíu" → "Cha Siu BBQ Pork" 
- "Dưa hấu" → "Watermelon"
- "Thập Cẩm" → "Mixed"
- Keep all IDs, numbers unchanged
- Translate only text content, not field names

Input product:
{json.dumps(product, ensure_ascii=False, indent=2)}

Return the translated product in the same JSON structure:"""

    def translate_single_product(self, product: Dict[str, Any], target_language: str) -> Dict[str, Any]:
        """Translate a single product"""
        try:
            prompt = self.create_single_product_prompt(product, target_language)
            
            # Use vertex service directly for single product
            vertex_service = self.translation_service.vertex_service
            if not vertex_service or not vertex_service.is_enabled():
                print(f"❌ Vertex AI not available")
                return product
            
            response = vertex_service.model.generate_content(prompt)
            
            if not response or not response.text:
                print(f"❌ Empty response for product {product.get('product_id')}")
                return product
            
            # Parse response
            response_text = response.text.strip()
            
            # Remove markdown code blocks if present
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            
            response_text = response_text.strip()
            
            # Parse JSON
            translated_product = json.loads(response_text)
            return translated_product
            
        except Exception as e:
            print(f"❌ Error translating product {product.get('product_id')}: {e}")
            return product
    
    def translate_categories(self, categories: List[Dict], target_language: str) -> List[Dict]:
        """Translate categories (these are small, can do together)"""
        try:
            lang_map = {
                'en': 'English',
                'fr': 'French', 
                'it': 'Italian',
                'zh': 'Chinese (Simplified)',
                'ja': 'Japanese'
            }
            
            target_lang_name = lang_map.get(target_language, target_language)
            
            prompt = f"""Translate these Vietnamese category names to {target_lang_name}.
Return ONLY valid JSON, no markdown:

{json.dumps(categories, ensure_ascii=False, indent=2)}

Keep same structure, translate only category_name and description fields:"""

            vertex_service = self.translation_service.vertex_service
            response = vertex_service.model.generate_content(prompt)
            
            if response and response.text:
                response_text = response.text.strip()
                if response_text.startswith('```json'):
                    response_text = response_text[7:]
                if response_text.endswith('```'):
                    response_text = response_text[:-3]
                
                return json.loads(response_text.strip())
            
            return categories
            
        except Exception as e:
            print(f"❌ Error translating categories: {e}")
            return categories
    
    def rebuild_language(self, target_language: str) -> bool:
        """Rebuild translation for a single language"""
        lang_names = {
            'en': 'English',
            'fr': 'French',
            'it': 'Italian', 
            'zh': 'Chinese',
            'ja': 'Japanese'
        }
        
        lang_name = lang_names.get(target_language, target_language)
        print(f"\n🌐 Rebuilding {lang_name} translation (one product at a time)...")
        
        # Get base content
        base_content = self.translation_service.get_base_content()
        categories = base_content.get('categories', [])
        products = base_content.get('products', [])
        
        if not products:
            print(f"❌ No products found in base content")
            return False
        
        print(f"📊 Processing {len(categories)} categories and {len(products)} products")
        
        # Translate categories first (small payload)
        print(f"🏷️ Translating categories...")
        translated_categories = self.translate_categories(categories, target_language)
        time.sleep(1)  # Small delay
        
        # Translate products one by one
        translated_products = []
        failed_products = []
        
        for i, product in enumerate(products):
            product_id = product.get('product_id', 'Unknown')
            product_name = product.get('product_name', 'Unknown')
            
            print(f"🔄 [{i+1}/{len(products)}] Translating: {product_name} (ID: {product_id})")
            
            translated_product = self.translate_single_product(product, target_language)
            
            # Check if translation worked
            if translated_product.get('product_name') != product.get('product_name'):
                translated_products.append(translated_product)
                print(f"   ✅ Success: {translated_product.get('product_name', 'N/A')}")
            else:
                # Translation failed, keep original
                translated_products.append(product)
                failed_products.append(product_id)
                print(f"   ⚠️ Failed, kept original")
            
            # Small delay between requests
            time.sleep(0.5)
        
        # Build final result
        result = {
            'source_language': 'vi',
            'categories': translated_categories,
            'products': translated_products
        }
        
        # Save result
        filename = f'rebuilt_{lang_name.lower()}_single_product.json'
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        # Report results
        successful = len(products) - len(failed_products)
        products_with_descriptions = sum(1 for p in translated_products 
                                       if p.get('short_description', '').strip() or p.get('long_description', '').strip())
        
        print(f"\n✅ {lang_name} translation completed!")
        print(f"📊 Results:")
        print(f"   Categories: {len(translated_categories)}")
        print(f"   Products: {successful}/{len(products)} successful")
        print(f"   With descriptions: {products_with_descriptions}")
        if failed_products:
            print(f"   Failed: {failed_products}")
        print(f"💾 Saved: {filename}")
        
        return len(failed_products) == 0


def main():
    """Main function"""
    translator = SingleProductTranslator()
    
    if not translator.translation_service.is_translation_enabled():
        print("❌ Translation service not available")
        return
    
    languages = ['en', 'fr', 'it', 'zh', 'ja']
    
    print("🚀 Starting single-product translation rebuild...")
    start_time = time.time()
    
    results = {}
    for lang in languages:
        success = translator.rebuild_language(lang)
        results[lang] = success
    
    total_time = time.time() - start_time
    
    print(f"\n🎉 All translations completed in {total_time:.1f} seconds")
    print(f"📊 Results summary:")
    for lang, success in results.items():
        status = "✅ Success" if success else "⚠️ Partial"
        print(f"   {lang.upper()}: {status}")


if __name__ == "__main__":
    main()