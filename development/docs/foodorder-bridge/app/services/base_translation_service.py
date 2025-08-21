"""
Base Translation Service for Vietnamese Food Menu
Manages Vietnamese base content and provides translation capabilities
"""

import json
import logging
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
from app.services.vertex_only_translation_service import VertexOnlyTranslationService
from app.config import get_settings

logger = logging.getLogger(__name__)


class BaseTranslationService:
    """Translation service that uses Vietnamese base content as source"""
    
    def __init__(self):
        """Initialize the base translation service"""
        self.settings = get_settings()
        self.base_language = 'vi'
        self.supported_languages = ['en', 'it', 'fr', 'zh', 'ja']
        
        # Load Vietnamese base content
        self.base_content = self._load_base_content()
        
        # Initialize Vertex AI translation service
        try:
            self.vertex_service = VertexOnlyTranslationService(
                project_id=self.settings.GOOGLE_CLOUD_PROJECT,
                location=self.settings.VERTEX_AI_LOCATION,
                model_name=self.settings.VERTEX_AI_MODEL
            )
            
            if self.vertex_service.is_enabled():
                logger.info("✅ Base Translation Service initialized with Vertex AI")
            else:
                logger.warning("⚠️ Vertex AI translation not available")
                self.vertex_service = None
        except Exception as e:
            logger.error(f"❌ Failed to initialize Vertex AI for base translation: {e}")
            self.vertex_service = None
        
        # Translation cache
        self.translation_cache = {}
        self.cache_ttl_hours = 24 * 7  # 1 week
    
    def _load_base_content(self) -> Dict[str, Any]:
        """Load Vietnamese base content from Odoo cache with descriptions"""
        try:
            # First try to load from Odoo cache (has updated descriptions)
            cache_path = Path(__file__).parent.parent.parent / 'cache' / 'products.json'
            categories_cache_path = Path(__file__).parent.parent.parent / 'cache' / 'categories.json'
            
            if cache_path.exists() and categories_cache_path.exists():
                logger.info("📦 Loading Vietnamese base content from Odoo cache...")
                
                # Load categories
                with open(categories_cache_path, 'r', encoding='utf-8') as f:
                    odoo_categories = json.load(f)
                
                # Load products with descriptions
                with open(cache_path, 'r', encoding='utf-8') as f:
                    odoo_products = json.load(f)
                
                # Convert Odoo format to translation service format
                categories = []
                for cat in odoo_categories:
                    categories.append({
                        'category_id': cat['id'],
                        'category_name': cat['name'],
                        'description': cat.get('description', '')
                    })
                
                products = []
                for prod in odoo_products:
                    # Clean HTML tags from descriptions if present
                    import re
                    short_desc = prod.get('short_description', '') or ''
                    long_desc = prod.get('long_description', '') or ''
                    
                    # Remove HTML tags
                    if short_desc:
                        short_desc = re.sub('<[^<]+?>', '', short_desc).strip()
                    if long_desc:
                        long_desc = re.sub('<[^<]+?>', '', long_desc).strip()
                    
                    # Map category ID
                    category_id = None
                    if prod.get('pos_categ_id') and isinstance(prod['pos_categ_id'], list):
                        category_id = prod['pos_categ_id'][0]
                    
                    product_data = {
                        'product_id': prod['id'],
                        'product_name': prod['name'],
                        'short_description': short_desc,
                        'long_description': long_desc,
                        'category_id': category_id,
                        'attributes': prod.get('attribute_lines', [])
                    }
                    products.append(product_data)
                
                content = {
                    'source_language': 'vi',
                    'categories': categories,
                    'products': products
                }
                
                logger.info(f"✅ Loaded Vietnamese base content from cache: {len(categories)} categories, {len(products)} products")
                return content
            
            # Fallback to static JSON file if cache not available
            logger.warning("⚠️ Cache not available, falling back to static JSON file")
            base_content_path = Path(__file__).parent.parent / 'data' / 'vietnamese_base_content.json'
            
            if not base_content_path.exists():
                logger.error(f"❌ Vietnamese base content not found at {base_content_path}")
                return {'categories': [], 'products': []}
            
            with open(base_content_path, 'r', encoding='utf-8') as f:
                content = json.load(f)
            
            logger.info(f"✅ Loaded Vietnamese base content from static file: {len(content.get('categories', []))} categories, {len(content.get('products', []))} products")
            return content
            
        except Exception as e:
            logger.error(f"❌ Failed to load Vietnamese base content: {e}")
            return {'categories': [], 'products': []}
    
    def get_base_content(self) -> Dict[str, Any]:
        """Get the Vietnamese base content"""
        return self.base_content
    
    def is_translation_enabled(self) -> bool:
        """Check if translation service is available"""
        return self.vertex_service is not None and self.vertex_service.is_enabled()
    
    def _get_cache_key(self, content_type: str, content_id: str, target_language: str) -> str:
        """Generate cache key for translation"""
        return f"base_trans:{content_type}:{content_id}:{target_language}"
    
    def _is_cache_valid(self, cache_entry: Dict) -> bool:
        """Check if cache entry is still valid"""
        if not cache_entry or 'timestamp' not in cache_entry:
            return False
        
        age_hours = (time.time() - cache_entry['timestamp']) / 3600
        return age_hours <= self.cache_ttl_hours
    
    def _fix_json_issues(self, json_text: str) -> str:
        """Fix common JSON formatting issues from LLM responses"""
        import re
        
        # Fix missing commas between array elements and object properties
        # Pattern: } followed by whitespace and then { (missing comma between objects)
        json_text = re.sub(r'}\s*\n\s*{', '},\n{', json_text)
        
        # Pattern: } followed by whitespace and then ] (end of array - this is correct)
        # Pattern: ] followed by whitespace and then { (missing comma between array elements)
        json_text = re.sub(r']\s*\n\s*{', '],\n{', json_text)
        
        # Pattern: } followed by whitespace and then "field": (missing comma between object properties)
        json_text = re.sub(r'}\s*\n\s*"', '},\n"', json_text)
        
        # Fix trailing commas before closing braces/brackets
        json_text = re.sub(r',\s*}', '}', json_text)
        json_text = re.sub(r',\s*]', ']', json_text)
        
        return json_text
    
    def get_category_base_content(self, category_id: int = None) -> List[Dict]:
        """Get Vietnamese base content for categories"""
        categories = self.base_content.get('categories', [])
        
        if category_id is not None:
            return [cat for cat in categories if cat['category_id'] == category_id]
        
        return categories
    
    def get_product_base_content(self, product_id: int = None, category_id: int = None) -> List[Dict]:
        """Get Vietnamese base content for products"""
        products = self.base_content.get('products', [])
        
        if product_id is not None:
            return [prod for prod in products if prod['product_id'] == product_id]
        
        if category_id is not None:
            return [prod for prod in products if prod.get('category_id') == category_id]
        
        return products
    
    def get_attribute_base_content(self) -> Dict[str, List[str]]:
        """Get Vietnamese base content for attributes and their values"""
        attributes = {}
        
        for product in self.base_content.get('products', []):
            for attr in product.get('attributes', []):
                attr_name = attr['attribute_name']
                if attr_name not in attributes:
                    attributes[attr_name] = set()
                
                for value in attr['attribute_values']:
                    attributes[attr_name].add(value['value_name'])
        
        # Convert sets to sorted lists
        return {attr_name: sorted(list(values)) for attr_name, values in attributes.items()}
    
    def get_service_info(self) -> Dict[str, Any]:
        """Get service information"""
        return {
            'service_type': 'base_translation_service',
            'base_language': self.base_language,
            'supported_languages': self.supported_languages,
            'base_content_categories': len(self.base_content.get('categories', [])),
            'base_content_products': len(self.base_content.get('products', [])),
            'vertex_ai_enabled': self.is_translation_enabled(),
            'vertex_model': self.settings.VERTEX_AI_MODEL if self.is_translation_enabled() else None,
            'cache_entries': len(self.translation_cache)
        }
    
    def clear_cache(self):
        """Clear translation cache"""
        self.translation_cache.clear()
        logger.info("🗑️ Base translation cache cleared")
    
    def _create_single_language_translation_prompt(self, target_language: str) -> str:
        """Create comprehensive prompt for Vietnamese menu translation using the improved system prompt"""
        return f"""## Context
You are translating a Vietnamese bánh mì restaurant menu from Vietnamese to English. The menu includes categories, product names, descriptions, and various attributes like toppings and drink options.

**CRITICAL REQUIREMENT**: The output must maintain the exact same JSON structure as the input. Only translate the VALUES within text fields - never modify field names, IDs, or the JSON structure itself.

## Translation Guidelines

### 1. **JSON Structure Requirements**
- **CRITICAL**: Maintain the exact same JSON structure as the input
- Keep all field names in English (e.g., "category_id", "product_name", "attributes")
- Preserve all IDs, numbers, and structural elements unchanged
- Only translate the VALUES within text fields, not the field names themselves
- Maintain array structures, nesting levels, and data types
- Ensure the output is valid, properly formatted JSON

### 2. **Fields to Translate**
- `category_name` - Translate to English
- `description` - Translate to English  
- `product_name` - Translate to English
- `short_description` - Translate to English
- `long_description` - Translate to English
- `attribute_name` - Translate to English
- `value_name` - Translate to English

### 3. **Fields to Keep Unchanged**
- All IDs (`category_id`, `product_id`, `attribute_id`, `value_id`)
- `source_language` - Keep as "vi" 
- `display_type` - Keep as is ("radio", "check_box")
- `price_extra` - Keep numerical values unchanged
- All structural elements and brackets

### 4. **Specific Translation Rules**

#### **Vietnamese Term Translations:**
- **"Bánh Mì" → "Baguette"** (Use "Baguette" for all instances)
- **"Xá Xíu" → "Cha Siu BBQ Pork"** (Vietnamese-style BBQ pork, avoid "Chinese")
- **"Dưa hấu" → "Watermelon"**
- **"Trà Dưa Lưới" → "Golden Melon Tea"**
- **"Chả lụa" → "Vietnamese pork sausage"**
- **"Gà xé" → "Shredded chicken"**
- **"Pate" → "Pâté"**
- **"Thập Cẩm" → "Mixed"** (traditional combination)

#### **Cultural Food Context**
- Use "Baguette" consistently instead of "Bánh Mì" in product names
- Translate Vietnamese food terms to their English equivalents
- Provide brief explanations for uniquely Vietnamese ingredients when necessary
- Maintain authenticity while ensuring English speakers can understand

### 5. **Menu Categories**
- Translate category names clearly and appetizingly
- Use standard English food category terminology
- Examples:
  - "Bánh Mì Truyền Thống" → "Traditional Vietnamese Baguettes"
  - "Đồ Uống" → "Beverages"
  - "Mì trộn & Xôi" → "Mixed Noodles & Sticky Rice"

### 6. **Product Names**
- **Option A**: Keep Vietnamese names with English descriptions
  - "Baguette Thập Cẩm (Mixed Vietnamese Baguette)"
- **Option B**: Full English translation with Vietnamese in parentheses
  - "Mixed Vietnamese Baguette (Thập Cẩm)"
- Choose the approach that best serves English-speaking customers

### 7. **Ingredients & Toppings**
- Translate common ingredients: "Jambon" → "Ham"
- Explain Vietnamese-specific items: "Chả lụa" → "Vietnamese pork sausage"
- **"Xá xíu" → "Cha Siu BBQ Pork"** (Vietnamese-style BBQ pork)
- "Gà xé" → "Shredded chicken"

### 8. **Beverages**
- "Cà phê" → "Coffee"
- "Trà" → "Tea"  
- "Sữa chua" → "Yogurt" or "Vietnamese yogurt drink"
- **"Trà Dưa Lưới" → "Golden Melon Tea"**
- **"Dưa hấu" → "Watermelon"**
- Keep brand names as original

### 9. **Descriptions**
- Write appetizing, clear descriptions
- Focus on flavors, cooking methods, and key ingredients
- Keep descriptions concise but informative
- Use food industry standard terminology

### 10. **Consistency Rules**
- Maintain consistent translation choices throughout
- Use the same English term for the same Vietnamese ingredient across all items
- **Always use "Baguette" instead of "Bánh Mì"**
- **Always use "Cha Siu BBQ Pork" instead of "Chinese BBQ Pork"**
- Ensure pricing format remains clear (convert "15000.0" to "$15.00" or appropriate currency)

### 11. **Special Considerations**
- **Combos**: Clearly explain what's included
- **Attributes**: Translate option names clearly (radio buttons, checkboxes)
- **Portion sizes**: Include size descriptions when mentioned
- **Dietary notes**: Clearly mark vegetarian items ("Veggy", "Chay")

## Quality Checklist
- [ ] **JSON structure identical to input** - no fields added, removed, or renamed
- [ ] **Valid JSON syntax** - proper brackets, commas, and quotation marks
- [ ] **All IDs preserved unchanged** - category_id, product_id, attribute_id, value_id
- [ ] **Numerical values maintained** - price_extra, IDs remain as numbers
- [ ] **"Bánh Mì" consistently replaced with "Baguette"**
- [ ] **"Xá Xíu" consistently translated as "Cha Siu BBQ Pork"**
- [ ] **"Dưa hấu" translated as "Watermelon"**
- [ ] All Vietnamese text translated or appropriately kept
- [ ] Food descriptions are appetizing and clear
- [ ] Ingredient explanations provided where needed
- [ ] Consistent terminology throughout
- [ ] Cultural authenticity maintained
- [ ] English speakers can easily understand and order
- [ ] **Output can be parsed as valid JSON**

**Note**: Prioritize clarity and customer understanding while respecting the authentic Vietnamese culinary tradition. Use "Baguette" and "Cha Siu BBQ Pork" consistently throughout the translation.

## Final Output Requirements

1. **Return the complete JSON structure** with all original fields preserved
2. **Translate only the text values** in the specified fields
3. **Apply specific translation rules consistently** (Baguette, Cha Siu BBQ Pork, Watermelon)
4. **Validate JSON syntax** before submitting - ensure it can be parsed
5. **Double-check all IDs and numbers** remain unchanged
6. **Maintain exact nesting and array structures** as provided in input

The output should be a valid JSON that can replace the original Vietnamese menu while preserving all structural integrity and database compatibility.

IMPORTANT: Return ONLY the translated JSON object, no additional text or explanations.

Vietnamese Menu Data to Translate:"""
    
    def _translate_chunked_content(self, content_chunk: Dict[str, Any], target_language: str) -> Optional[Dict[str, Any]]:
        """
        Translate a smaller chunk of content to avoid JSON parsing issues
        
        Args:
            content_chunk: Chunk of Vietnamese content to translate
            target_language: Target language code
            
        Returns:
            Translated chunk or None if failed
        """
        try:
            # Create the translation prompt for single language
            prompt = self._create_single_language_translation_prompt(target_language)
            
            # Add the chunk as JSON
            prompt += f"\n\n{json.dumps(content_chunk, ensure_ascii=False, indent=2)}"
            
            logger.debug(f"📏 Chunk prompt size: {len(prompt):,} characters")
            
            # Call Vertex AI Gemini for translation
            response = self.vertex_service.model.generate_content(prompt)
            
            if not response or not response.text:
                logger.error(f"❌ Empty response from Gemini for {target_language} chunk translation")
                return None
            
            logger.debug(f"📏 Chunk response size: {len(response.text):,} characters")
            
            # Parse JSON response (handle markdown code blocks)
            response_text = response.text.strip()
            
            # Remove markdown code blocks if present
            if response_text.startswith('```json'):
                response_text = response_text[7:]  # Remove ```json
                logger.debug("✅ Removed ```json prefix from chunk")
            if response_text.endswith('```'):
                response_text = response_text[:-3]  # Remove ```
                logger.debug("✅ Removed ``` suffix from chunk")
            
            response_text = response_text.strip()
            
            # Additional cleaning for common issues
            # Remove any text before the first {
            first_brace = response_text.find('{')
            if first_brace > 0:
                response_text = response_text[first_brace:]
                logger.debug(f"✅ Removed {first_brace} characters before first brace in chunk")
            
            # Find last } and remove anything after it
            last_brace = response_text.rfind('}')
            if last_brace > 0 and last_brace < len(response_text) - 1:
                response_text = response_text[:last_brace + 1]
                logger.debug("✅ Removed text after last brace in chunk")
            
            # Try to fix common JSON issues
            response_text = self._fix_json_issues(response_text)
            
            # Parse the response
            translated_chunk = json.loads(response_text)
            
            # Validate chunk structure
            if not isinstance(translated_chunk, dict):
                logger.error(f"❌ Chunk response is not a dictionary")
                return None
            
            return translated_chunk
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ Failed to parse Gemini response for {target_language} chunk: {e}")
            logger.error(f"❌ Chunk error position: {e.pos}")
            
            # Save problematic chunk response for debugging
            if 'response_text' in locals():
                chunk_error_file = f"debug_chunk_error_{target_language}_{int(time.time())}.txt"
                with open(chunk_error_file, 'w', encoding='utf-8') as f:
                    f.write(f"Error: {e}\n")
                    f.write(f"Position: {e.pos}\n")
                    f.write(f"Chunk content preview: {str(content_chunk)[:500]}...\n")
                    f.write(f"\nFull response:\n{response_text}")
                logger.error(f"💾 Chunk error details saved to {chunk_error_file}")
            
            return None
        except Exception as e:
            logger.error(f"❌ Chunk translation to {target_language} failed: {e}")
            return None

    def translate_to_language(self, target_language: str) -> Optional[Dict[str, Any]]:
        """
        Translate Vietnamese base content to a single target language (single-shot approach)
        
        Args:
            target_language: Target language code (e.g., 'en', 'fr', 'it', 'zh', 'ja')
            
        Returns:
            Translated content for the language, or None if failed
        """
        if not self.is_translation_enabled():
            logger.warning("⚠️ Translation service not available")
            return None
        
        if target_language not in self.supported_languages:
            logger.warning(f"⚠️ Unsupported target language: {target_language}")
            return None
        
        # Check if we have cached translation for this language
        cache_key = f"translation_{target_language}"
        if cache_key in self.translation_cache:
            cache_entry = self.translation_cache[cache_key]
            if self._is_cache_valid(cache_entry):
                logger.info(f"📖 Using cached translation for {target_language}")
                return cache_entry['translation']
        
        try:
            logger.info(f"🔄 Starting single-shot translation to {target_language}...")
            
            # Create the translation prompt for single language
            prompt = self._create_single_language_translation_prompt(target_language)
            
            # Add the Vietnamese base content as JSON
            prompt += f"\n\n{json.dumps(self.base_content, ensure_ascii=False, indent=2)}"
            
            logger.info(f"📏 Prompt size: {len(prompt):,} characters")
            
            # Call Vertex AI Gemini for translation
            response = self.vertex_service.model.generate_content(prompt)
            
            if not response or not response.text:
                logger.error(f"❌ Empty response from Gemini for {target_language} translation")
                return None
            
            logger.info(f"📏 Response size: {len(response.text):,} characters")
            
            # Save raw response for debugging
            debug_file = f"debug_response_{target_language}.txt"
            with open(debug_file, 'w', encoding='utf-8') as f:
                f.write(response.text)
            logger.info(f"💾 Raw response saved to {debug_file}")
            
            # Parse JSON response (handle markdown code blocks)
            response_text = response.text.strip()
            
            # Remove markdown code blocks if present
            if response_text.startswith('```json'):
                response_text = response_text[7:]  # Remove ```json
                logger.info("✅ Removed ```json prefix")
            if response_text.endswith('```'):
                response_text = response_text[:-3]  # Remove ```
                logger.info("✅ Removed ``` suffix")
            
            response_text = response_text.strip()
            
            # Additional cleaning for common issues
            # Remove any text before the first {
            first_brace = response_text.find('{')
            if first_brace > 0:
                response_text = response_text[first_brace:]
                logger.info(f"✅ Removed {first_brace} characters before first brace")
            
            # Find last } and remove anything after it
            last_brace = response_text.rfind('}')
            if last_brace > 0 and last_brace < len(response_text) - 1:
                response_text = response_text[:last_brace + 1]
                logger.info("✅ Removed text after last brace")
            
            logger.info(f"📏 Cleaned response size: {len(response_text):,} characters")
            
            # Save cleaned response for debugging
            cleaned_debug_file = f"debug_cleaned_{target_language}.txt"
            with open(cleaned_debug_file, 'w', encoding='utf-8') as f:
                f.write(response_text)
            logger.info(f"💾 Cleaned response saved to {cleaned_debug_file}")
            
            # Try to fix common JSON issues
            response_text = self._fix_json_issues(response_text)
            
            # Parse the response
            translated_content = json.loads(response_text)
            
            # Validate the structure
            if not isinstance(translated_content, dict):
                logger.error(f"❌ Response is not a dictionary")
                return None
            
            if 'categories' not in translated_content or 'products' not in translated_content:
                logger.error(f"❌ Response missing required fields")
                return None
            
            categories_count = len(translated_content.get('categories', []))
            products_count = len(translated_content.get('products', []))
            
            logger.info(f"✅ Parsed translation: {categories_count} categories, {products_count} products")
            
            # Cache the translation
            self.translation_cache[cache_key] = {
                'translation': translated_content,
                'timestamp': time.time()
            }
            
            logger.info(f"✅ Translation to {target_language} completed successfully")
            return translated_content
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ Failed to parse Gemini response for {target_language}: {e}")
            logger.error(f"❌ Error position: {e.pos}")
            
            # Show context around error
            if 'response_text' in locals() and e.pos < len(response_text):
                start = max(0, e.pos - 100)
                end = min(len(response_text), e.pos + 100)
                context = response_text[start:end]
                logger.error(f"❌ Context around error: {repr(context)}")
                
                # Save error context
                error_file = f"debug_error_{target_language}.txt"
                with open(error_file, 'w', encoding='utf-8') as f:
                    f.write(f"Error: {e}\n")
                    f.write(f"Position: {e.pos}\n")
                    f.write(f"Context: {context}\n")
                    f.write(f"\nFull response:\n{response_text}")
                logger.error(f"💾 Error details saved to {error_file}")
            
            return None
        except Exception as e:
            logger.error(f"❌ Translation to {target_language} failed: {e}")
            return None
    
    def translate_all_content(self) -> Optional[Dict[str, Any]]:
        """
        Translate entire Vietnamese base content to all target languages (one language per call)
        
        Returns:
            Dictionary with translations for all languages, or None if failed
        """
        if not self.is_translation_enabled():
            logger.warning("⚠️ Translation service not available")
            return None
        
        all_translations = {}
        
        for language in self.supported_languages:
            logger.info(f"🔄 Translating to {language}...")
            translated_content = self.translate_to_language(language)
            
            if translated_content:
                all_translations[language] = translated_content
                logger.info(f"✅ {language} translation completed")
            else:
                logger.error(f"❌ Failed to translate to {language}")
        
        if all_translations:
            # Cache the complete set
            cache_key = "full_translation_batch"
            self.translation_cache[cache_key] = {
                'translation': all_translations,
                'timestamp': time.time()
            }
            
            logger.info(f"✅ All translations completed for {len(all_translations)} languages")
            return all_translations
        else:
            logger.error("❌ No translations were successful")
            return None
    
    def get_translated_content(self, target_language: str) -> Optional[Dict[str, Any]]:
        """
        Get translated content for a specific language
        
        Args:
            target_language: Target language code
            
        Returns:
            Translated content or None if not available
        """
        if target_language not in self.supported_languages:
            logger.warning(f"⚠️ Unsupported target language: {target_language}")
            return None
        
        # Get all translations
        all_translations = self.translate_all_content()
        if not all_translations:
            return None
        
        return all_translations.get(target_language)
    
    def save_translations_to_file(self, filename: str = None) -> bool:
        """
        Save all translated content to JSON file
        
        Args:
            filename: Optional filename (defaults to translated_menu_content.json)
            
        Returns:
            True if saved successfully, False otherwise
        """
        if not filename:
            filename = "translated_menu_content.json"
        
        try:
            # Get all translations
            all_translations = self.translate_all_content()
            if not all_translations:
                logger.error("❌ No translations available to save")
                return False
            
            # Create complete structure with Vietnamese base + translations
            complete_data = {
                'base_language': self.base_language,
                'source_content': self.base_content,
                'target_languages': self.supported_languages,
                'translations': all_translations,
                'generated_at': time.time(),
                'generated_date': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # Save to data directory
            output_path = Path(__file__).parent.parent / 'data' / filename
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(complete_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"✅ Translations saved to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to save translations: {e}")
            return False
    
    def load_translations_from_file(self, filename: str = None) -> Optional[Dict[str, Any]]:
        """
        Load translated content from JSON file
        
        Args:
            filename: Optional filename (defaults to translated_menu_content.json)
            
        Returns:
            Dictionary with translations or None if failed
        """
        if not filename:
            filename = "translated_menu_content.json"
        
        try:
            input_path = Path(__file__).parent.parent / 'data' / filename
            
            if not input_path.exists():
                logger.warning(f"⚠️ Translation file not found: {input_path}")
                return None
            
            with open(input_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Update cache with loaded translations
            if 'translations' in data:
                cache_key = "full_translation_batch"
                self.translation_cache[cache_key] = {
                    'translation': data['translations'],
                    'timestamp': data.get('generated_at', time.time())
                }
            
            logger.info(f"✅ Translations loaded from {input_path}")
            return data.get('translations')
            
        except Exception as e:
            logger.error(f"❌ Failed to load translations: {e}")
            return None
    
    def get_translation_summary(self) -> Dict[str, Any]:
        """
        Get summary of available translations
        
        Returns:
            Dictionary with translation statistics
        """
        all_translations = self.translate_all_content()
        if not all_translations:
            return {
                'status': 'no_translations',
                'base_content_stats': {
                    'categories': len(self.base_content.get('categories', [])),
                    'products': len(self.base_content.get('products', []))
                }
            }
        
        # Calculate statistics
        stats = {
            'status': 'translations_available',
            'base_language': self.base_language,
            'target_languages': list(all_translations.keys()),
            'base_content_stats': {
                'categories': len(self.base_content.get('categories', [])),
                'products': len(self.base_content.get('products', []))
            },
            'translation_stats': {}
        }
        
        # Calculate stats for each language
        for lang, content in all_translations.items():
            if content and isinstance(content, dict):
                stats['translation_stats'][lang] = {
                    'categories': len(content.get('categories', [])),
                    'products': len(content.get('products', []))
                }
        
        return stats