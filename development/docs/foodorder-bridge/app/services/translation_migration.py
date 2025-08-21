"""
Migration utilities for transitioning from Google Translate to Vertex AI
"""

import logging
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class TranslationMigrator:
    """Handles migration from Google Translate to Vertex AI"""
    
    def __init__(self, use_vertex: bool = True, fallback_enabled: bool = True):
        """
        Initialize migrator with fallback support
        
        Args:
            use_vertex: Whether to use Vertex AI as primary
            fallback_enabled: Whether to fallback to Google Translate if Vertex fails
        """
        self.use_vertex = use_vertex
        self.fallback_enabled = fallback_enabled
        
        # Initialize both services
        self.vertex_service = None
        self.google_service = None
        
        if use_vertex:
            try:
                from app.services.vertex_translation_service import VertexTranslationService
                self.vertex_service = VertexTranslationService()
                if self.vertex_service.is_enabled():
                    logger.info("✅ Vertex AI translation service initialized")
                else:
                    logger.warning("⚠️ Vertex AI service created but not enabled")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Vertex AI: {e}")
                self.vertex_service = None
        
        if fallback_enabled or not use_vertex:
            try:
                from app.services.translation_service import TranslationService
                self.google_service = TranslationService()
                if self.google_service.is_enabled():
                    logger.info("✅ Google Translate service initialized as fallback")
                else:
                    logger.warning("⚠️ Google Translate service created but not enabled")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Google Translate: {e}")
                self.google_service = None
    
    def get_active_service(self):
        """Get the active translation service"""
        if self.use_vertex and self.vertex_service and self.vertex_service.is_enabled():
            return self.vertex_service
        elif self.google_service and self.google_service.is_enabled():
            return self.google_service
        else:
            logger.warning("No translation service available")
            return None
    
    def get_service_info(self) -> Dict[str, Any]:
        """Get information about available services"""
        return {
            'primary_service': 'vertex_ai' if self.use_vertex else 'google_translate',
            'vertex_available': self.vertex_service and self.vertex_service.is_enabled(),
            'google_available': self.google_service and self.google_service.is_enabled(),
            'fallback_enabled': self.fallback_enabled,
            'active_service': 'vertex_ai' if (self.vertex_service and self.vertex_service.is_enabled() and self.use_vertex) else 'google_translate'
        }
    
    def translate_text(self, text: str, target_language: str, 
                      source_language: str = None, context: str = None) -> str:
        """
        Translate text with automatic fallback
        
        Args:
            text: Text to translate
            target_language: Target language code
            source_language: Source language code
            context: Translation context
            
        Returns:
            Translated text
        """
        if not text or not text.strip():
            return text
        
        # Try Vertex AI first if enabled
        if self.use_vertex and self.vertex_service and self.vertex_service.is_enabled():
            try:
                result = self.vertex_service.translate_text(
                    text, target_language, source_language, context
                )
                logger.debug(f"✅ Vertex AI translation successful for: {text[:50]}...")
                return result
            except Exception as e:
                logger.warning(f"⚠️ Vertex AI translation failed: {e}")
        
        # Fallback to Google Translate
        if self.fallback_enabled and self.google_service and self.google_service.is_enabled():
            try:
                result = self.google_service.translate_text(
                    text, target_language, source_language, context
                )
                logger.debug(f"✅ Google Translate fallback successful for: {text[:50]}...")
                return result
            except Exception as e:
                logger.error(f"❌ Google Translate fallback also failed: {e}")
        
        # Return original text if all fails
        logger.warning(f"⚠️ All translation services failed, returning original text")
        return text
    
    def translate_batch(self, texts: list, target_language: str, 
                       source_language: str = None) -> list:
        """
        Translate multiple texts with automatic fallback
        
        Args:
            texts: List of texts to translate
            target_language: Target language code
            source_language: Source language code
            
        Returns:
            List of translated texts
        """
        if not texts:
            return texts
        
        # Try Vertex AI first if enabled
        if self.use_vertex and self.vertex_service and self.vertex_service.is_enabled():
            try:
                result = self.vertex_service.translate_batch(
                    texts, target_language, source_language
                )
                logger.debug(f"✅ Vertex AI batch translation successful for {len(texts)} items")
                return result
            except Exception as e:
                logger.warning(f"⚠️ Vertex AI batch translation failed: {e}")
        
        # Fallback to Google Translate
        if self.fallback_enabled and self.google_service and self.google_service.is_enabled():
            try:
                result = self.google_service.translate_batch(
                    texts, target_language, source_language
                )
                logger.debug(f"✅ Google Translate batch fallback successful for {len(texts)} items")
                return result
            except Exception as e:
                logger.error(f"❌ Google Translate batch fallback also failed: {e}")
        
        # Return original texts if all fails
        logger.warning(f"⚠️ All translation services failed, returning original texts")
        return texts
    
    def translate_product_data(self, product: Dict, target_languages: list = None) -> Dict:
        """
        Translate product data with automatic fallback
        
        Args:
            product: Product data dictionary
            target_languages: List of target language codes
            
        Returns:
            Product data with translations
        """
        if not product:
            return product
        
        # Try Vertex AI first if enabled
        if self.use_vertex and self.vertex_service and self.vertex_service.is_enabled():
            try:
                result = self.vertex_service.translate_product_data(
                    product, target_languages
                )
                logger.debug(f"✅ Vertex AI product translation successful")
                return result
            except Exception as e:
                logger.warning(f"⚠️ Vertex AI product translation failed: {e}")
        
        # Fallback to Google Translate
        if self.fallback_enabled and self.google_service and self.google_service.is_enabled():
            try:
                result = self.google_service.translate_product_data(
                    product, target_languages
                )
                logger.debug(f"✅ Google Translate product fallback successful")
                return result
            except Exception as e:
                logger.error(f"❌ Google Translate product fallback also failed: {e}")
        
        # Return original product if all fails
        logger.warning(f"⚠️ All translation services failed, returning original product")
        return product
    
    def translate_category_data(self, category: Dict, target_languages: list = None) -> Dict:
        """
        Translate category data with automatic fallback
        
        Args:
            category: Category data dictionary
            target_languages: List of target language codes
            
        Returns:
            Category data with translations
        """
        if not category:
            return category
        
        # Try Vertex AI first if enabled
        if self.use_vertex and self.vertex_service and self.vertex_service.is_enabled():
            try:
                result = self.vertex_service.translate_category_data(
                    category, target_languages
                )
                logger.debug(f"✅ Vertex AI category translation successful")
                return result
            except Exception as e:
                logger.warning(f"⚠️ Vertex AI category translation failed: {e}")
        
        # Fallback to Google Translate
        if self.fallback_enabled and self.google_service and self.google_service.is_enabled():
            try:
                result = self.google_service.translate_category_data(
                    category, target_languages
                )
                logger.debug(f"✅ Google Translate category fallback successful")
                return result
            except Exception as e:
                logger.error(f"❌ Google Translate category fallback also failed: {e}")
        
        # Return original category if all fails
        logger.warning(f"⚠️ All translation services failed, returning original category")
        return category
    
    def get_translation_status(self) -> Dict[str, Any]:
        """Get comprehensive translation status"""
        status = {
            'migration_info': self.get_service_info(),
            'services': {}
        }
        
        # Get Vertex AI status
        if self.vertex_service:
            try:
                status['services']['vertex_ai'] = self.vertex_service.get_translation_status()
            except Exception as e:
                status['services']['vertex_ai'] = {'error': str(e)}
        
        # Get Google Translate status
        if self.google_service:
            try:
                status['services']['google_translate'] = self.google_service.get_translation_status()
            except Exception as e:
                status['services']['google_translate'] = {'error': str(e)}
        
        return status
    
    def migrate_cache(self) -> bool:
        """
        Migrate existing Google Translate cache to Vertex AI format
        
        Returns:
            True if migration successful, False otherwise
        """
        if not self.google_service or not self.vertex_service:
            logger.error("Both services required for cache migration")
            return False
        
        try:
            # Check if migration already completed
            migration_marker = Path('cache/.vertex_cache_migrated')
            if migration_marker.exists():
                logger.info("Cache migration already completed")
                return True
            
            # Load Google Translate cache
            if hasattr(self.google_service, 'translation_cache'):
                google_cache = self.google_service.translation_cache
                
                # Migrate to Vertex cache with updated keys
                migrated_count = 0
                for key, entry in google_cache.items():
                    if isinstance(entry, dict) and 'translation' in entry and 'original' in entry:
                        # Create new cache entry for Vertex
                        vertex_key = self.vertex_service._get_cache_key(
                            entry['original'],
                            entry.get('source_language', 'vi'),
                            entry.get('target_language', 'en')
                        )
                        
                        self.vertex_service.translation_cache[vertex_key] = {
                            'original': entry['original'],
                            'translation': entry['translation'],
                            'source_language': entry.get('source_language', 'vi'),
                            'target_language': entry.get('target_language', 'en'),
                            'timestamp': entry.get('timestamp', 0),
                            'migrated_from': 'google_translate'
                        }
                        migrated_count += 1
                
                # Save migrated cache
                self.vertex_service._save_translation_cache()
                
                # Create migration marker
                migration_marker.touch()
                
                logger.info(f"✅ Migrated {migrated_count} cached translations to Vertex AI")
                return True
            else:
                logger.warning("No Google Translate cache found to migrate")
                migration_marker.touch()  # Mark as completed anyway
                return True
                
        except Exception as e:
            logger.error(f"❌ Cache migration failed: {e}")
            return False
    
    def clear_all_caches(self, older_than_days: int = None):
        """Clear caches from both services"""
        cleared = []
        
        if self.vertex_service:
            try:
                self.vertex_service.clear_cache(older_than_days)
                cleared.append('vertex_ai')
            except Exception as e:
                logger.error(f"Failed to clear Vertex AI cache: {e}")
        
        if self.google_service:
            try:
                self.google_service.clear_cache(older_than_days)
                cleared.append('google_translate')
            except Exception as e:
                logger.error(f"Failed to clear Google Translate cache: {e}")
        
        logger.info(f"Cleared caches for: {', '.join(cleared)}")
    
    def is_enabled(self) -> bool:
        """Check if any translation service is available"""
        vertex_enabled = self.vertex_service and self.vertex_service.is_enabled()
        google_enabled = self.google_service and self.google_service.is_enabled()
        
        if self.use_vertex:
            return vertex_enabled or (self.fallback_enabled and google_enabled)
        else:
            return google_enabled
    
    def get_supported_languages(self) -> Dict[str, str]:
        """Get supported languages from active service"""
        active_service = self.get_active_service()
        if active_service and hasattr(active_service, 'supported_languages'):
            return active_service.supported_languages
        
        # Fallback to default language set
        return {
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


class CompatibilityTranslationService:
    """
    Compatibility wrapper that provides the same interface as original TranslationService
    but uses the new migration system underneath
    """
    
    def __init__(self, use_vertex: bool = None, fallback_enabled: bool = None):
        """Initialize with settings from config"""
        # Import settings here to avoid circular imports
        try:
            from app.config import get_settings
            settings = get_settings()
            
            use_vertex = use_vertex if use_vertex is not None else getattr(settings, 'USE_VERTEX_TRANSLATION', True)
            fallback_enabled = fallback_enabled if fallback_enabled is not None else getattr(settings, 'TRANSLATION_FALLBACK_ENABLED', True)
        except Exception:
            # Fallback to defaults if config not available
            use_vertex = use_vertex if use_vertex is not None else False
            fallback_enabled = fallback_enabled if fallback_enabled is not None else True
        
        self.migrator = TranslationMigrator(
            use_vertex=use_vertex,
            fallback_enabled=fallback_enabled
        )
        
        # Run cache migration on first initialization
        if use_vertex and not Path('cache/.vertex_cache_migrated').exists():
            logger.info("Running cache migration on first startup...")
            self.migrator.migrate_cache()
    
    def translate_text(self, text: str, target_language: str, 
                      source_language: str = None, context: str = None) -> str:
        """Translate single text"""
        return self.migrator.translate_text(text, target_language, source_language, context)
    
    def translate_batch(self, texts: list, target_language: str, 
                       source_language: str = None) -> list:
        """Translate multiple texts"""
        return self.migrator.translate_batch(texts, target_language, source_language)
    
    def translate_product_data(self, product: Dict, target_languages: list = None) -> Dict:
        """Translate product data"""
        return self.migrator.translate_product_data(product, target_languages)
    
    def translate_category_data(self, category: Dict, target_languages: list = None) -> Dict:
        """Translate category data"""
        return self.migrator.translate_category_data(category, target_languages)
    
    def is_enabled(self) -> bool:
        """Check if translation is enabled"""
        return self.migrator.is_enabled()
    
    def get_translation_status(self) -> Dict[str, Any]:
        """Get translation status"""
        return self.migrator.get_translation_status()
    
    def clear_cache(self, older_than_days: int = None):
        """Clear translation cache"""
        self.migrator.clear_all_caches(older_than_days)
    
    @property
    def supported_languages(self) -> Dict[str, str]:
        """Get supported languages"""
        return self.migrator.get_supported_languages()
    
    @property
    def default_language(self) -> str:
        """Get default language"""
        return 'vi'