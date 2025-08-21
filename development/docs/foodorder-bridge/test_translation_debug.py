#!/usr/bin/env python3
"""
Debug script for translation service
"""

import json
import sys
from pathlib import Path
from app.services.base_translation_service import BaseTranslationService

def test_small_translation():
    """Test translation with a very small subset"""
    try:
        print("🔄 Testing with minimal content...")
        translation_service = BaseTranslationService()
        
        # Create minimal test content
        minimal_content = {
            "source_language": "vi",
            "categories": [
                {
                    "category_id": 1,
                    "category_name": "Bánh Mì Truyền Thống",
                    "description": "Traditional Vietnamese sandwiches"
                }
            ],
            "products": [
                {
                    "product_id": 1186,
                    "product_name": "Bánh Mì Không",
                    "short_description": "",
                    "long_description": "",
                    "category_id": 5,
                    "attributes": []
                },
                {
                    "product_id": 2715,
                    "product_name": "(C2) CMB Happy Lunchset",
                    "short_description": "",
                    "long_description": "",
                    "category_id": 8,
                    "attributes": [
                        {
                            "attribute_id": 4,
                            "attribute_name": "Bánh Mì",
                            "display_type": "radio",
                            "attribute_values": [
                                {
                                    "value_id": 2,
                                    "value_name": "Bánh Mì Thập Cẩm",
                                    "price_extra": 0.0
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        
        # Replace the base content temporarily
        original_content = translation_service.base_content
        translation_service.base_content = minimal_content
        
        print("📝 Minimal content structure:")
        print(f"  - Categories: {len(minimal_content['categories'])}")
        print(f"  - Products: {len(minimal_content['products'])}")
        
        # Create prompt
        prompt = translation_service._create_single_language_translation_prompt('en')
        prompt += f"\n\n{json.dumps(minimal_content, ensure_ascii=False, indent=2)}"
        
        print(f"\n📏 Prompt length: {len(prompt)} characters")
        
        # Call Vertex AI
        print("🔄 Calling Vertex AI Gemini...")
        response = translation_service.vertex_service.model.generate_content(prompt)
        
        if response and response.text:
            print(f"✅ Got response from Gemini")
            print(f"📏 Response length: {len(response.text)} characters")
            
            # Save raw response to file for inspection
            with open('debug_response.txt', 'w', encoding='utf-8') as f:
                f.write(response.text)
            print("💾 Raw response saved to debug_response.txt")
            
            print(f"\n🔍 Raw response (first 1000 chars):")
            print(response.text[:1000])
            print("...")
            
            # Try to clean and parse
            response_text = response.text.strip()
            
            # Remove markdown code blocks if present
            if response_text.startswith('```json'):
                response_text = response_text[7:]
                print("✅ Removed ```json prefix")
            if response_text.endswith('```'):
                response_text = response_text[:-3]
                print("✅ Removed ``` suffix")
            
            response_text = response_text.strip()
            
            print(f"\n📏 Cleaned response length: {len(response_text)} characters")
            
            try:
                result = json.loads(response_text)
                print("✅ Successfully parsed JSON!")
                print(f"📊 Result structure: {list(result.keys())}")
                
                if 'categories' in result:
                    categories = result['categories']
                    print(f"✅ Found {len(categories)} categories")
                    if categories:
                        print(f"  - First category: {categories[0].get('category_name', 'N/A')}")
                
                if 'products' in result:
                    products = result['products']
                    print(f"✅ Found {len(products)} products")
                    if products:
                        print(f"  - First product: {products[0].get('product_name', 'N/A')}")
                
                return True
                
            except json.JSONDecodeError as e:
                print(f"❌ JSON parsing failed: {e}")
                print(f"🔍 Error at position {e.pos}")
                
                # Show context around error
                if e.pos < len(response_text):
                    start = max(0, e.pos - 100)
                    end = min(len(response_text), e.pos + 100)
                    print(f"Context around error:")
                    print(repr(response_text[start:end]))
                
                # Save problematic response
                with open('debug_error_response.txt', 'w', encoding='utf-8') as f:
                    f.write(response_text)
                print("💾 Problematic response saved to debug_error_response.txt")
                
                return False
        else:
            print("❌ No response from Gemini")
            return False
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Restore original content
        if 'original_content' in locals():
            translation_service.base_content = original_content

if __name__ == "__main__":
    success = test_small_translation()
    sys.exit(0 if success else 1)