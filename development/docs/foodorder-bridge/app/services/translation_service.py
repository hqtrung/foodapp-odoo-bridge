import os
import json
import time
from typing import Dict, List, Optional, Any
from google.cloud import translate_v2 as translate
from google.api_core import exceptions as google_exceptions
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class TranslationService:
    """Service for translating text using Google Cloud Translation API"""
    
    def __init__(self, project_id: str = None, cache_dir: str = "cache"):
        self.project_id = project_id or os.getenv('GOOGLE_CLOUD_PROJECT', 'finiziapp')
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        
        # Supported languages for FoodOrder app
        self.supported_languages = {
            'vi': 'Vietnamese',
            'en': 'English', 
            'zh': 'Chinese (Simplified)',
            'zh-TW': 'Chinese (Traditional)',
            'th': 'Thai'
        }
        
        self.default_language = 'vi'  # Vietnamese is the base language
        
        # Initialize translation client
        try:
            self.translate_client = translate.Client()
            logger.info("✅ Google Cloud Translation client initialized")
        except Exception as e:
            logger.warning(f"⚠️ Translation client initialization failed: {e}")
            self.translate_client = None
            
        # Load translation cache
        self.translation_cache = self._load_translation_cache()
        
    def is_enabled(self) -> bool:
        """Check if translation service is enabled and available"""
        return self.translate_client is not None
        
    def get_supported_languages(self) -> Dict[str, str]:
        """Get list of supported languages"""
        return self.supported_languages.copy()
        
    def _load_translation_cache(self) -> Dict[str, Any]:
        """Load existing translation cache from file"""
        cache_file = self.cache_dir / 'translations_cache.json'
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load translation cache: {e}")
        return {}
        
    def _save_translation_cache(self):
        """Save translation cache to file"""
        cache_file = self.cache_dir / 'translations_cache.json'
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.translation_cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Failed to save translation cache: {e}")
            
    def _get_cache_key(self, text: str, source_lang: str, target_lang: str) -> str:
        """Generate cache key for translation"""
        import hashlib
        content = f"{text}:{source_lang}:{target_lang}"
        return hashlib.md5(content.encode('utf-8')).hexdigest()
        
    def _is_cache_valid(self, cache_entry: Dict, max_age_days: int = 7) -> bool:
        """Check if cached translation is still valid"""
        if 'timestamp' not in cache_entry:
            return False
        
        cache_time = cache_entry['timestamp']
        current_time = time.time()
        max_age_seconds = max_age_days * 24 * 60 * 60
        
        return (current_time - cache_time) < max_age_seconds
        
    def translate_text(self, text: str, target_language: str, source_language: str = None) -> str:
        """
        Translate text to target language
        
        Args:
            text: Text to translate
            target_language: Target language code (e.g., 'en', 'zh', 'th')
            source_language: Source language code (auto-detect if None)
            
        Returns:
            Translated text or original text if translation fails
        """
        if not self.is_enabled():
            logger.warning("Translation service not available, returning original text")
            return text
            
        if not text or not text.strip():
            return text
            
        # If target language is the same as source, return original
        if target_language == source_language:
            return text
            
        # If target language is not supported, return original
        if target_language not in self.supported_languages:
            logger.warning(f"Unsupported target language: {target_language}")
            return text
            
        # Check cache first
        cache_key = self._get_cache_key(text, source_language or 'auto', target_language)
        if cache_key in self.translation_cache:
            cache_entry = self.translation_cache[cache_key]
            if self._is_cache_valid(cache_entry):
                logger.debug(f"Using cached translation for: {text[:50]}...")
                return cache_entry['translation']
                
        try:
            # Translate using Google Cloud Translation API
            result = self.translate_client.translate(
                text,
                target_language=target_language,
                source_language=source_language
            )
            
            translated_text = result['translatedText']
            detected_source = result.get('detectedSourceLanguage', source_language)
            
            # Cache the translation
            self.translation_cache[cache_key] = {
                'original': text,
                'translation': translated_text,
                'source_language': detected_source,
                'target_language': target_language,
                'timestamp': time.time()
            }
            
            logger.info(f"Translated '{text[:50]}...' from {detected_source} to {target_language}")
            return translated_text
            
        except google_exceptions.GoogleAPICallError as e:
            logger.error(f"Google API error during translation: {e}")
        except Exception as e:
            logger.error(f"Unexpected error during translation: {e}")
            
        # Return original text if translation fails
        return text
        
    def translate_batch(self, texts: List[str], target_language: str, source_language: str = None) -> List[str]:
        """
        Translate multiple texts in batch for efficiency
        
        Args:
            texts: List of texts to translate
            target_language: Target language code
            source_language: Source language code (auto-detect if None)
            
        Returns:
            List of translated texts
        """
        if not self.is_enabled():
            return texts
            
        if not texts:
            return []
            
        # Filter out empty texts and check cache
        texts_to_translate = []
        cached_translations = {}
        
        for i, text in enumerate(texts):
            if not text or not text.strip():
                cached_translations[i] = text
                continue
                
            cache_key = self._get_cache_key(text, source_language or 'auto', target_language)
            if cache_key in self.translation_cache:
                cache_entry = self.translation_cache[cache_key]
                if self._is_cache_valid(cache_entry):
                    cached_translations[i] = cache_entry['translation']
                    continue
                    
            texts_to_translate.append((i, text))
            
        if not texts_to_translate:
            # All texts were cached
            return [cached_translations.get(i, texts[i]) for i in range(len(texts))]
            
        try:
            # Translate uncached texts in batch
            texts_for_api = [item[1] for item in texts_to_translate]
            
            # Google Cloud Translation API batch translate
            results = self.translate_client.translate(
                texts_for_api,
                target_language=target_language,
                source_language=source_language
            )
            
            # Process results and cache translations
            for (original_index, original_text), result in zip(texts_to_translate, results):
                translated_text = result['translatedText']
                detected_source = result.get('detectedSourceLanguage', source_language)
                
                # Cache the translation
                cache_key = self._get_cache_key(original_text, detected_source, target_language)
                self.translation_cache[cache_key] = {
                    'original': original_text,
                    'translation': translated_text,
                    'source_language': detected_source,
                    'target_language': target_language,
                    'timestamp': time.time()
                }
                
                cached_translations[original_index] = translated_text
                
            logger.info(f"Batch translated {len(texts_to_translate)} texts to {target_language}")
            
        except Exception as e:
            logger.error(f"Batch translation failed: {e}")
            # Fill remaining with original texts
            for original_index, original_text in texts_to_translate:
                if original_index not in cached_translations:
                    cached_translations[original_index] = original_text
                    
        # Reconstruct the full results list
        results = [cached_translations.get(i, texts[i]) for i in range(len(texts))]
        
        # Save cache after batch operation
        self._save_translation_cache()
        
        return results
        
    def translate_product_data(self, product: Dict, target_languages: List[str] = None) -> Dict:
        """
        Translate product name and description to multiple languages
        
        Args:
            product: Product dictionary with 'name' and 'description_sale'
            target_languages: List of target language codes
            
        Returns:
            Product dictionary with translation fields added
        """
        if target_languages is None:
            target_languages = list(self.supported_languages.keys())
            
        # Create a copy to avoid modifying original
        translated_product = product.copy()
        
        # Initialize translation dictionaries
        name_translations = {self.default_language: product.get('name', '')}
        desc_translations = {self.default_language: product.get('description_sale', '') or ''}
        
        # Get texts to translate
        name = product.get('name', '')
        description = product.get('description_sale', '') or ''
        
        for lang in target_languages:
            if lang == self.default_language:
                continue
                
            # Translate name and description together for efficiency
            texts_to_translate = []
            if name:
                texts_to_translate.append(name)
            if description:
                texts_to_translate.append(description)
                
            if texts_to_translate:
                translated_texts = self.translate_batch(texts_to_translate, lang, self.default_language)
                
                if name:
                    name_translations[lang] = translated_texts[0]
                if description and len(translated_texts) > 1:
                    desc_translations[lang] = translated_texts[1]
                elif description:
                    # Only description was translated
                    desc_translations[lang] = translated_texts[0]
                    
        # Add translations to product
        translated_product['name_translations'] = name_translations
        translated_product['description_translations'] = desc_translations
        
        return translated_product
        
    def translate_category_data(self, category: Dict, target_languages: List[str] = None) -> Dict:
        """
        Translate category name and description to multiple languages
        
        Args:
            category: Category dictionary with 'name' and 'description'
            target_languages: List of target language codes
            
        Returns:
            Category dictionary with translation fields added
        """
        if target_languages is None:
            target_languages = list(self.supported_languages.keys())
            
        # Create a copy to avoid modifying original
        translated_category = category.copy()
        
        # Initialize translation dictionaries
        name_translations = {self.default_language: category.get('name', '')}
        desc_translations = {self.default_language: category.get('description', '') or ''}
        
        # Get texts to translate
        name = category.get('name', '')
        description = category.get('description', '') or ''
        
        for lang in target_languages:
            if lang == self.default_language:
                continue
                
            # Translate name and description together for efficiency
            texts_to_translate = []
            if name:
                texts_to_translate.append(name)
            if description:
                texts_to_translate.append(description)
                
            if texts_to_translate:
                translated_texts = self.translate_batch(texts_to_translate, lang, self.default_language)
                
                if name:
                    name_translations[lang] = translated_texts[0]
                if description and len(translated_texts) > 1:
                    desc_translations[lang] = translated_texts[1]
                elif description:
                    # Only description was translated
                    desc_translations[lang] = translated_texts[0]
                    
        # Add translations to category
        translated_category['name_translations'] = name_translations
        translated_category['description_translations'] = desc_translations
        
        return translated_category
        
    def get_translation_status(self) -> Dict[str, Any]:
        """Get translation service status and cache statistics"""
        cache_stats = {
            'total_cached_translations': len(self.translation_cache),
            'supported_languages': self.supported_languages,
            'default_language': self.default_language,
            'service_enabled': self.is_enabled(),
            'cache_file_exists': (self.cache_dir / 'translations_cache.json').exists()
        }
        
        # Count translations by language pair
        language_pairs = {}
        for cache_entry in self.translation_cache.values():
            source = cache_entry.get('source_language', 'unknown')
            target = cache_entry.get('target_language', 'unknown')
            pair = f"{source}->{target}"
            language_pairs[pair] = language_pairs.get(pair, 0) + 1
            
        cache_stats['language_pairs'] = language_pairs
        
        return cache_stats
        
    def clear_cache(self, older_than_days: int = None):
        """Clear translation cache, optionally only entries older than specified days"""
        if older_than_days is None:
            # Clear all cache
            self.translation_cache = {}
            logger.info("Cleared all translation cache")
        else:
            # Clear only old entries
            current_time = time.time()
            max_age_seconds = older_than_days * 24 * 60 * 60
            
            old_keys = []
            for key, entry in self.translation_cache.items():
                if 'timestamp' in entry:
                    if (current_time - entry['timestamp']) > max_age_seconds:
                        old_keys.append(key)
                        
            for key in old_keys:
                del self.translation_cache[key]
                
            logger.info(f"Cleared {len(old_keys)} translation cache entries older than {older_than_days} days")
            
        # Save updated cache
        self._save_translation_cache()