"""
Pure Vertex AI Gemini 2.0 Flash Translation Service
No Google Translate dependencies - Vertex AI only
"""

import os
import json
import time
import logging
from typing import Dict, List, Optional, Any
from google.cloud import aiplatform
from vertexai.generative_models import GenerativeModel, GenerationConfig
import vertexai
from google.api_core import exceptions as google_exceptions
from app.services.vertex_prompts import get_enhanced_translation_prompt

logger = logging.getLogger(__name__)


class VertexOnlyTranslationService:
    """Pure Vertex AI Gemini 2.0 Flash translation service - no fallbacks"""
    
    def __init__(self, project_id: str = None, location: str = "us-central1", 
                 model_name: str = "gemini-2.5-flash"):
        """
        Initialize pure Vertex AI translation service
        
        Args:
            project_id: Google Cloud project ID
            location: Vertex AI location (region)
            model_name: Gemini model to use
        """
        self.project_id = project_id or os.getenv('GOOGLE_CLOUD_PROJECT')
        self.location = location
        self.model_name = model_name
        self.translation_cache = {}
        self.cache_ttl_days = 7
        
        # Supported languages for Vietnamese restaurant
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
        
        if not self.project_id:
            logger.error("❌ GOOGLE_CLOUD_PROJECT not set - Vertex AI translation disabled")
            self.model = None
            return
            
        try:
            # Initialize Vertex AI
            vertexai.init(project=self.project_id, location=self.location)
            
            # Initialize Gemini model with optimal settings for translation
            generation_config = GenerationConfig(
                temperature=0.2,  # Low temperature for consistent translations
                top_p=0.8,
                top_k=40,
                max_output_tokens=8192,  # Maximum allowed tokens
            )
            
            self.model = GenerativeModel(
                model_name=self.model_name,
                generation_config=generation_config
            )
            
            logger.info(f"✅ Vertex AI Gemini {self.model_name} initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Vertex AI Gemini: {e}")
            self.model = None
    
    def is_enabled(self) -> bool:
        """Check if Vertex AI translation is available"""
        return self.model is not None and self.project_id is not None
    
    def _get_cache_key(self, text: str, source_lang: str, target_lang: str) -> str:
        """Generate cache key for translation"""
        return f"{source_lang}:{target_lang}:{hash(text)}"
    
    def _is_cache_valid(self, cache_entry: Dict) -> bool:
        """Check if cache entry is still valid"""
        if not cache_entry or 'timestamp' not in cache_entry:
            return False
        
        age_days = (time.time() - cache_entry['timestamp']) / (24 * 3600)
        return age_days <= self.cache_ttl_days
    
    def translate_text(self, text: str, target_language: str, 
                      source_language: str = 'vi', context: str = None) -> str:
        """
        Translate single text using Vertex AI Gemini 2.0 Flash only
        
        Args:
            text: Text to translate
            target_language: Target language code
            source_language: Source language code (default: vi)
            context: Additional context (optional)
            
        Returns:
            Translated text or original text if translation fails
        """
        if not self.is_enabled():
            logger.warning("⚠️ Vertex AI not available - returning original text")
            return text
            
        if not text or not text.strip():
            return text
            
        if target_language not in self.supported_languages:
            logger.warning(f"⚠️ Unsupported target language: {target_language}")
            return text
        
        # Check cache first
        cache_key = self._get_cache_key(text, source_language, target_language)
        if cache_key in self.translation_cache:
            cache_entry = self.translation_cache[cache_key]
            if self._is_cache_valid(cache_entry):
                logger.debug(f"Using cached translation for: {text[:50]}...")
                return cache_entry['translation']
        
        try:
            # Create translation items
            items = [{'id': '1', 'text': text, 'type': 'general'}]
            
            # Get enhanced prompt with Vietnamese restaurant context
            target_lang_name = self.supported_languages[target_language]
            source_lang_name = self.supported_languages.get(source_language, source_language.upper())
            
            prompt = get_enhanced_translation_prompt(
                items, target_lang_name, source_language, 'general'
            )
            
            # Generate translation with Gemini
            response = self.model.generate_content(prompt)
            
            if not response or not response.text:
                logger.warning(f"Empty response from Gemini for: {text}")
                return text
            
            # Parse JSON response (handle markdown code blocks)
            try:
                response_text = response.text.strip()
                
                # Remove markdown code blocks if present
                if response_text.startswith('```json'):
                    response_text = response_text[7:]  # Remove ```json
                if response_text.endswith('```'):
                    response_text = response_text[:-3]  # Remove ```
                
                response_text = response_text.strip()
                
                result = json.loads(response_text)
                translations = result.get('translations', [])
                
                if translations and len(translations) > 0:
                    translated_text = translations[0].get('translated_text', text)
                    
                    # Cache the translation
                    self.translation_cache[cache_key] = {
                        'original': text,
                        'translation': translated_text,
                        'source_language': source_language,
                        'target_language': target_language,
                        'timestamp': time.time()
                    }
                    
                    logger.debug(f"✅ Vertex AI translation: {text} → {translated_text}")
                    return translated_text
                else:
                    logger.warning(f"No translations in response for: {text}")
                    return text
                    
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse Gemini response: {e}")
                logger.debug(f"Raw response: {response.text}")
                return text
                
        except Exception as e:
            logger.error(f"❌ Vertex AI translation failed: {e}")
            return text
    
    def translate_batch(self, texts: List[str], target_language: str, 
                       source_language: str = 'vi') -> List[str]:
        """
        Translate multiple texts using Vertex AI Gemini 2.0 Flash only
        
        Args:
            texts: List of texts to translate
            target_language: Target language code
            source_language: Source language code
            
        Returns:
            List of translated texts (same order as input)
        """
        if not self.is_enabled() or not texts:
            return texts
        
        # Convert to items format for batch processing
        items = []
        for i, text in enumerate(texts):
            if text and text.strip():
                items.append({'id': str(i), 'text': text, 'type': 'general'})
        
        if not items:
            return texts
        
        try:
            # Get enhanced prompt with Vietnamese restaurant context
            target_lang_name = self.supported_languages[target_language]
            source_lang_name = self.supported_languages.get(source_language, source_language.upper())
            
            prompt = get_enhanced_translation_prompt(
                items, target_lang_name, source_language, 'general'
            )
            
            # Generate batch translation
            response = self.model.generate_content(prompt)
            
            if not response or not response.text:
                logger.warning("Empty batch response from Gemini")
                return texts
            
            # Parse JSON response (handle markdown code blocks)
            response_text = response.text.strip()
            
            # Remove markdown code blocks if present
            if response_text.startswith('```json'):
                response_text = response_text[7:]  # Remove ```json
            if response_text.endswith('```'):
                response_text = response_text[:-3]  # Remove ```
            
            response_text = response_text.strip()
            
            result = json.loads(response_text)
            translations = result.get('translations', [])
            
            # Map translations back to original order
            translated_texts = texts.copy()
            for translation in translations:
                item_id = translation.get('id')
                translated_text = translation.get('translated_text', '')
                
                if item_id and translated_text:
                    try:
                        index = int(item_id)
                        if 0 <= index < len(translated_texts):
                            translated_texts[index] = translated_text
                    except (ValueError, IndexError):
                        continue
            
            logger.info(f"✅ Vertex AI batch translation: {len(items)} items")
            return translated_texts
            
        except Exception as e:
            logger.error(f"❌ Vertex AI batch translation failed: {e}")
            return texts
    
    def translate_product_data(self, product: Dict, target_languages: List[str] = None) -> Dict:
        """
        Translate product data using Vertex AI only
        
        Args:
            product: Product data dictionary
            target_languages: List of target language codes
            
        Returns:
            Product data with translations
        """
        if not product or not self.is_enabled():
            return product
        
        if not target_languages:
            target_languages = ['en', 'fr', 'it', 'es', 'zh', 'zh-TW', 'th', 'ja']
        
        translated_product = product.copy()
        
        # Get translatable content
        name = product.get('name', '')
        description = product.get('description_sale', '') or ''
        
        if not name:
            return translated_product
        
        # Initialize translation dictionaries
        name_translations = translated_product.get('name_translations', {})
        desc_translations = translated_product.get('description_translations', {})
        
        # Ensure Vietnamese is included
        name_translations['vi'] = name
        if description:
            desc_translations['vi'] = description
        
        # Translate to each target language
        for lang in target_languages:
            if lang == 'vi':  # Skip source language
                continue
                
            try:
                # Translate name
                if name and lang not in name_translations:
                    translated_name = self.translate_text(name, lang, 'vi')
                    name_translations[lang] = translated_name
                
                # Translate description if available
                if description and lang not in desc_translations:
                    translated_desc = self.translate_text(description, lang, 'vi')
                    desc_translations[lang] = translated_desc
                    
            except Exception as e:
                logger.error(f"Failed to translate product {name} to {lang}: {e}")
                continue
        
        translated_product['name_translations'] = name_translations
        translated_product['description_translations'] = desc_translations
        
        return translated_product
    
    def translate_category_data(self, category: Dict, target_languages: List[str] = None) -> Dict:
        """
        Translate category data using Vertex AI only
        
        Args:
            category: Category data dictionary
            target_languages: List of target language codes
            
        Returns:
            Category data with translations
        """
        if not category or not self.is_enabled():
            return category
        
        if not target_languages:
            target_languages = ['en', 'fr', 'it', 'es', 'zh', 'zh-TW', 'th', 'ja']
        
        translated_category = category.copy()
        
        # Get translatable content
        name = category.get('name', '')
        
        if not name:
            return translated_category
        
        # Initialize translation dictionaries
        name_translations = translated_category.get('name_translations', {})
        
        # Ensure Vietnamese is included
        name_translations['vi'] = name
        
        # Translate to each target language
        for lang in target_languages:
            if lang == 'vi':  # Skip source language
                continue
                
            try:
                if name and lang not in name_translations:
                    translated_name = self.translate_text(name, lang, 'vi')
                    name_translations[lang] = translated_name
                    
            except Exception as e:
                logger.error(f"Failed to translate category {name} to {lang}: {e}")
                continue
        
        translated_category['name_translations'] = name_translations
        
        return translated_category
    
    def clear_cache(self):
        """Clear translation cache"""
        self.translation_cache.clear()
        logger.info("🗑️ Translation cache cleared")
    
    def get_service_info(self) -> Dict[str, Any]:
        """Get service information"""
        return {
            'service_type': 'vertex_ai_only',
            'model': self.model_name,
            'project_id': self.project_id,
            'location': self.location,
            'enabled': self.is_enabled(),
            'supported_languages': self.supported_languages,
            'cache_entries': len(self.translation_cache),
            'fallback_available': False  # No fallback in pure Vertex AI service
        }