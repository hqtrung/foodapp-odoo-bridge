"""
Vertex AI Translation Service using Gemini for context-aware translation

This service replaces Google Cloud Translation API with Vertex AI's Gemini models
for improved translation quality in food/restaurant contexts.
"""

import os
import json
import time
import logging
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from google.cloud import aiplatform
from vertexai.generative_models import GenerativeModel, GenerationConfig
import vertexai
from google.api_core import exceptions as google_exceptions

logger = logging.getLogger(__name__)


class VertexTranslationService:
    """Service for translating text using Vertex AI Gemini models"""
    
    def __init__(self, project_id: str = None, location: str = "us-central1", 
                 model_name: str = "gemini-1.5-flash-002", cache_dir: str = "cache"):
        """
        Initialize Vertex AI translation service
        
        Args:
            project_id: Google Cloud project ID
            location: Vertex AI location (region)
            model_name: Gemini model to use (gemini-1.5-flash-002 for speed, gemini-1.5-pro-002 for quality)
            cache_dir: Directory for translation cache
        """
        self.project_id = project_id or os.getenv('GOOGLE_CLOUD_PROJECT')
        self.location = location or os.getenv('VERTEX_AI_LOCATION', 'us-central1')
        self.model_name = model_name or os.getenv('VERTEX_AI_MODEL', 'gemini-1.5-flash-002')
        
        if not self.project_id:
            logger.warning("GOOGLE_CLOUD_PROJECT not set - translation service disabled")
            self.model = None
        else:
            try:
                # Initialize Vertex AI
                vertexai.init(project=self.project_id, location=self.location)
                
                # Initialize the model with optimized settings
                self.model = GenerativeModel(
                    model_name=self.model_name,
                    generation_config=GenerationConfig(
                        temperature=0.2,  # Low temperature for consistent translation
                        top_p=0.8,
                        top_k=40,
                        max_output_tokens=8192,
                        response_mime_type="application/json",  # Request JSON response
                    )
                )
                logger.info(f"✅ Vertex AI Gemini model initialized: {self.model_name}")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Vertex AI: {e}")
                self.model = None
        
        # Cache configuration
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        
        # Supported languages (same as original)
        self.supported_languages = {
            'vi': 'Vietnamese',
            'en': 'English',
            'fr': 'French',
            'it': 'Italian',
            'es': 'Spanish',
            'zh': 'Chinese (Simplified)',
            'zh-TW': 'Chinese (Traditional)',
            'th': 'Thai',
            'ja': 'Japanese'
        }
        
        self.default_language = 'vi'
        
        # Load translation cache
        self.translation_cache = self._load_translation_cache()
        
        # Vietnamese food glossary integration
        try:
            from app.services.translation_glossary import VietnameseFoodGlossary
            self.glossary = VietnameseFoodGlossary()
        except:
            self.glossary = None
            
    def is_enabled(self) -> bool:
        """Check if translation service is enabled"""
        return self.model is not None
    
    def _load_translation_cache(self) -> Dict[str, Any]:
        """Load existing translation cache from file"""
        cache_file = self.cache_dir / 'vertex_translations_cache.json'
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load translation cache: {e}")
        return {}
    
    def _save_translation_cache(self):
        """Save translation cache to file"""
        cache_file = self.cache_dir / 'vertex_translations_cache.json'
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.translation_cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Failed to save translation cache: {e}")
    
    def _get_cache_key(self, text: str, source_lang: str, target_lang: str) -> str:
        """Generate cache key for translation"""
        import hashlib
        content = f"{text}:{source_lang}:{target_lang}:vertex"
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def _is_cache_valid(self, cache_entry: Dict, max_age_days: int = 7) -> bool:
        """Check if cached translation is still valid"""
        if 'timestamp' not in cache_entry:
            return False
        
        cache_time = cache_entry['timestamp']
        current_time = time.time()
        max_age_seconds = max_age_days * 24 * 60 * 60
        
        return (current_time - cache_time) < max_age_seconds
    
    def _create_translation_prompt(self, items: List[Dict[str, str]], 
                                  target_language: str, 
                                  source_language: str = 'vi') -> str:
        """
        Create optimized prompt for Gemini translation
        
        Args:
            items: List of dicts with 'id', 'text', and 'type' keys
            target_language: Target language code
            source_language: Source language code
            
        Returns:
            Formatted prompt for Gemini
        """
        target_lang_name = self.supported_languages.get(target_language, target_language)
        source_lang_name = self.supported_languages.get(source_language, source_language)
        
        prompt = f"""You are a professional translator specializing in Vietnamese cuisine and restaurant menus.

Context: This is the translation for Vietnamese Bánh Mì (Baguette) Restaurant menu from {source_lang_name} to {target_lang_name}.

CRITICAL TRANSLATION RULES:
1. Preserve product codes in parentheses like (A1), (B2), (C3) exactly as they appear
2. Do NOT translate "Bánh Mì" as "Sandwich" - prefer "Baguette" and translate from "Baguette" for other languages
3. "Bánh Mì Pate Trứng Double" = "Baguette with Pâté and Eggs"
4. "Thập cẩm" = "Mixed Meat" (not "assorted" or "combination")
5. Keep "Bánh Mì" in original Vietnamese form when possible, but use "Baguette" concept for translations

SPECIFIC VIETNAMESE FOOD TRANSLATIONS:
- Bánh Mì → Keep as "Bánh Mì" or use "Baguette" if translation needed
- Pate → "Pâté" (with accent)
- Trứng → "Eggs" 
- Thập cẩm → "Mixed Meat"
- Chả lụa → "Vietnamese ham" or "Pork roll"
- Xá xíu → "Char siu" or "BBQ pork"
- Đồ chua → "Pickled vegetables"
- Rau thơm → "Fresh herbs"

ADDITIONAL GUIDELINES:
6. Maintain Vietnamese food authenticity and cultural identity
7. Use appetizing, professional restaurant language
8. Do not translate brand names (Coca Cola, Pepsi, etc.)
9. Maintain a friendly tone appropriate for a Vietnamese baguette restaurant

Please translate the following Vietnamese baguette restaurant menu items to {target_lang_name}.

Return ONLY a valid JSON object with this exact structure:
{{
  "translations": [
    {{
      "id": "item_id",
      "translated_text": "translated text here"
    }}
  ]
}}

Items to translate:
"""
        
        # Add items to translate
        for item in items:
            item_type = item.get('type', 'product')
            prompt += f'\n- ID: {item["id"]}, Type: {item_type}, Text: "{item["text"]}"'
        
        return prompt
    
    def translate_batch_with_vertex(self, items: List[Dict[str, str]], 
                                   target_language: str, 
                                   source_language: str = 'vi') -> Dict[str, str]:
        """
        Translate multiple items using Vertex AI Gemini
        
        Args:
            items: List of dicts with 'id' and 'text' keys
            target_language: Target language code
            source_language: Source language code
            
        Returns:
            Dictionary mapping item IDs to translated texts
        """
        if not self.is_enabled():
            logger.warning("Vertex AI translation not available")
            return {item['id']: item['text'] for item in items}
        
        if target_language not in self.supported_languages:
            logger.warning(f"Unsupported target language: {target_language}")
            return {item['id']: item['text'] for item in items}
        
        try:
            # Create the prompt
            prompt = self._create_translation_prompt(items, target_language, source_language)
            
            # Generate translation
            response = self.model.generate_content(prompt)
            
            # Parse JSON response
            try:
                result = json.loads(response.text)
                translations = {}
                
                for translation in result.get('translations', []):
                    item_id = translation.get('id')
                    translated_text = translation.get('translated_text', '')
                    
                    # Apply glossary post-processing if available
                    if self.glossary and translated_text:
                        # Find original text
                        original = next((item['text'] for item in items if item['id'] == item_id), '')
                        translated_text = self.glossary.postprocess_text(
                            original, translated_text, target_language
                        )
                    
                    translations[item_id] = translated_text
                
                return translations
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse Gemini response as JSON: {e}")
                logger.debug(f"Response text: {response.text}")
                # Fallback: return original texts
                return {item['id']: item['text'] for item in items}
                
        except Exception as e:
            logger.error(f"Vertex AI translation failed: {e}")
            return {item['id']: item['text'] for item in items}
    
    def translate_text(self, text: str, target_language: str, 
                      source_language: str = None, context: str = None) -> str:
        """
        Translate single text (compatible with original interface)
        
        Args:
            text: Text to translate
            target_language: Target language code
            source_language: Source language code (default: vi)
            context: Translation context (optional)
            
        Returns:
            Translated text or original if translation fails
        """
        if not self.is_enabled() or not text or not text.strip():
            return text
        
        if target_language == source_language or target_language == self.default_language:
            return text
        
        # Check cache first
        cache_key = self._get_cache_key(text, source_language or 'vi', target_language)
        if cache_key in self.translation_cache:
            cache_entry = self.translation_cache[cache_key]
            if self._is_cache_valid(cache_entry):
                logger.debug(f"Using cached translation for: {text[:50]}...")
                return cache_entry['translation']
        
        # Translate using batch method with single item
        items = [{'id': '1', 'text': text, 'type': context or 'menu_item'}]
        translations = self.translate_batch_with_vertex(items, target_language, source_language or 'vi')
        
        translated_text = translations.get('1', text)
        
        # Cache the translation
        self.translation_cache[cache_key] = {
            'original': text,
            'translation': translated_text,
            'source_language': source_language or 'vi',
            'target_language': target_language,
            'timestamp': time.time()
        }
        
        return translated_text
    
    def translate_batch(self, texts: List[str], target_language: str, 
                       source_language: str = None) -> List[str]:
        """
        Translate multiple texts (compatible with original interface)
        
        Args:
            texts: List of texts to translate
            target_language: Target language code
            source_language: Source language code
            
        Returns:
            List of translated texts
        """
        if not self.is_enabled() or not texts:
            return texts
        
        # Convert to items format
        items = []
        cached_translations = {}
        
        for i, text in enumerate(texts):
            if not text or not text.strip():
                cached_translations[str(i)] = text
                continue
            
            # Check cache
            cache_key = self._get_cache_key(text, source_language or 'vi', target_language)
            if cache_key in self.translation_cache:
                cache_entry = self.translation_cache[cache_key]
                if self._is_cache_valid(cache_entry):
                    cached_translations[str(i)] = cache_entry['translation']
                    continue
            
            items.append({'id': str(i), 'text': text})
        
        # Translate uncached items
        if items:
            # Process in batches of 25 for optimal Gemini performance
            batch_size = 25
            for batch_start in range(0, len(items), batch_size):
                batch = items[batch_start:batch_start + batch_size]
                translations = self.translate_batch_with_vertex(batch, target_language, source_language or 'vi')
                
                # Cache translations
                for item in batch:
                    translated = translations.get(item['id'], item['text'])
                    cached_translations[item['id']] = translated
                    
                    # Save to cache
                    cache_key = self._get_cache_key(item['text'], source_language or 'vi', target_language)
                    self.translation_cache[cache_key] = {
                        'original': item['text'],
                        'translation': translated,
                        'source_language': source_language or 'vi',
                        'target_language': target_language,
                        'timestamp': time.time()
                    }
        
        # Save cache after batch operation
        self._save_translation_cache()
        
        # Reconstruct ordered list
        return [cached_translations.get(str(i), texts[i]) for i in range(len(texts))]
    
    def translate_product_data(self, product: Dict, target_languages: List[str] = None) -> Dict:
        """
        Translate product data (compatible with original interface)
        
        Optimized to translate all languages in single Gemini call
        """
        if target_languages is None:
            target_languages = list(self.supported_languages.keys())
        
        translated_product = product.copy()
        
        # Initialize translation dictionaries
        name_translations = {self.default_language: product.get('name', '')}
        desc_translations = {self.default_language: product.get('description_sale', '') or ''}
        
        # Prepare items for batch translation
        items_to_translate = []
        
        for lang in target_languages:
            if lang == self.default_language:
                continue
            
            if product.get('name'):
                items_to_translate.append({
                    'id': f"name_{lang}",
                    'text': product['name'],
                    'type': 'product_name',
                    'target_lang': lang
                })
            
            if product.get('description_sale'):
                items_to_translate.append({
                    'id': f"desc_{lang}",
                    'text': product['description_sale'],
                    'type': 'product_description',
                    'target_lang': lang
                })
        
        # Group by target language and translate
        for lang in target_languages:
            if lang == self.default_language:
                continue
            
            lang_items = [item for item in items_to_translate if item.get('target_lang') == lang]
            if lang_items:
                # Remove target_lang from items before translation
                clean_items = [{k: v for k, v in item.items() if k != 'target_lang'} 
                              for item in lang_items]
                
                translations = self.translate_batch_with_vertex(clean_items, lang, self.default_language)
                
                for item_id, translated_text in translations.items():
                    if item_id.startswith('name_'):
                        name_translations[lang] = translated_text
                    elif item_id.startswith('desc_'):
                        desc_translations[lang] = translated_text
        
        translated_product['name_translations'] = name_translations
        translated_product['description_translations'] = desc_translations
        
        return translated_product
    
    def translate_category_data(self, category: Dict, target_languages: List[str] = None) -> Dict:
        """
        Translate category data (compatible with original interface)
        """
        if target_languages is None:
            target_languages = list(self.supported_languages.keys())
        
        translated_category = category.copy()
        
        # Initialize translation dictionaries
        name_translations = {self.default_language: category.get('name', '')}
        desc_translations = {self.default_language: category.get('description', '') or ''}
        
        # Similar approach as translate_product_data
        items_to_translate = []
        
        for lang in target_languages:
            if lang == self.default_language:
                continue
            
            if category.get('name'):
                items_to_translate.append({
                    'id': f"name_{lang}",
                    'text': category['name'],
                    'type': 'category_name',
                    'target_lang': lang
                })
            
            if category.get('description'):
                items_to_translate.append({
                    'id': f"desc_{lang}",
                    'text': category['description'],
                    'type': 'category_description',
                    'target_lang': lang
                })
        
        # Group by target language and translate
        for lang in target_languages:
            if lang == self.default_language:
                continue
            
            lang_items = [item for item in items_to_translate if item.get('target_lang') == lang]
            if lang_items:
                clean_items = [{k: v for k, v in item.items() if k != 'target_lang'} 
                              for item in lang_items]
                
                translations = self.translate_batch_with_vertex(clean_items, lang, self.default_language)
                
                for item_id, translated_text in translations.items():
                    if item_id.startswith('name_'):
                        name_translations[lang] = translated_text
                    elif item_id.startswith('desc_'):
                        desc_translations[lang] = translated_text
        
        translated_category['name_translations'] = name_translations
        translated_category['description_translations'] = desc_translations
        
        return translated_category
    
    def get_translation_status(self) -> Dict[str, Any]:
        """Get translation service status"""
        return {
            'service_type': 'Vertex AI Gemini',
            'model': self.model_name if self.model else 'Not initialized',
            'total_cached_translations': len(self.translation_cache),
            'supported_languages': self.supported_languages,
            'default_language': self.default_language,
            'service_enabled': self.is_enabled(),
            'cache_file_exists': (self.cache_dir / 'vertex_translations_cache.json').exists(),
            'project_id': self.project_id,
            'location': self.location
        }
    
    def clear_cache(self, older_than_days: int = None):
        """Clear translation cache"""
        if older_than_days is None:
            self.translation_cache = {}
            logger.info("Cleared all Vertex AI translation cache")
        else:
            current_time = time.time()
            max_age_seconds = older_than_days * 24 * 60 * 60
            
            old_keys = []
            for key, entry in self.translation_cache.items():
                if 'timestamp' in entry:
                    if (current_time - entry['timestamp']) > max_age_seconds:
                        old_keys.append(key)
            
            for key in old_keys:
                del self.translation_cache[key]
            
            logger.info(f"Cleared {len(old_keys)} old cache entries")
        
        self._save_translation_cache()