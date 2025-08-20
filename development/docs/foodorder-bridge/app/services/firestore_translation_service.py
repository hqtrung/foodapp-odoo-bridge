"""
Firestore Translation Service for Direct Frontend Access

This service manages translation collections optimized for direct frontend access,
separate from the main cache collections. Provides indexed, language-specific
access to product and category translations.
"""

import os
import json
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Union
from google.cloud import firestore
from google.cloud.firestore import Client
import logging

logger = logging.getLogger(__name__)


class FirestoreTranslationService:
    """Firestore service optimized for frontend translation access"""
    
    def __init__(self, collection_prefix: str = "foodorder_translations"):
        """Initialize Firestore translation service"""
        self.collection_prefix = collection_prefix
        
        # Initialize Firestore client (uses Application Default Credentials on Cloud Run)
        try:
            self.db: Client = firestore.Client()
            logger.info("✅ Connected to Firestore for translations")
        except Exception as e:
            logger.error(f"❌ Failed to connect to Firestore: {e}")
            raise
        
        # Translation collection names
        self.products_collection = f"{collection_prefix}_products"
        self.categories_collection = f"{collection_prefix}_categories"
        self.metadata_collection = f"{collection_prefix}_metadata"
        
        # Supported languages
        self.supported_languages = ["vi", "en", "fr", "it", "es", "zh", "zh-TW", "th", "ja"]
        
    def save_product_translations(self, products: List[Dict]) -> Dict[str, Any]:
        """Save product translations to optimized Firestore collections"""
        try:
            timestamp = datetime.now(timezone.utc)
            batch = self.db.batch()
            saved_count = 0
            
            for product in products:
                product_id = str(product.get('id'))
                if not product_id or product_id == 'None':
                    continue
                    
                # Extract translations
                name_translations = product.get('name_translations', {})
                desc_translations = product.get('description_translations', {})
                
                # Create translation document
                # Handle description_sale that can be False/None
                description_sale = product.get('description_sale', '')
                if not isinstance(description_sale, str):
                    description_sale = ''
                    
                # Handle pos_categ_id safely
                pos_categ_id = product.get('pos_categ_id')
                category_id = None
                category_name = ''
                
                if pos_categ_id and isinstance(pos_categ_id, list) and len(pos_categ_id) > 0:
                    category_id = pos_categ_id[0]
                    if len(pos_categ_id) > 1:
                        category_name = pos_categ_id[1] if isinstance(pos_categ_id[1], str) else ''
                
                translation_doc = {
                    'product_id': int(product.get('id')),
                    'base_name': product.get('name', ''),
                    'base_description': description_sale,
                    'category_id': category_id,
                    'category_name': category_name,
                    'translations': {},
                    'last_updated': timestamp,
                    'version': '1.0'
                }
                
                # Add language translations
                for lang in self.supported_languages:
                    if lang in name_translations or lang in desc_translations:
                        translation_doc['translations'][lang] = {
                            'name': name_translations.get(lang, product.get('name', '')),
                            'description': desc_translations.get(lang, description_sale)
                        }
                
                # Only save if we have translations
                if translation_doc['translations']:
                    doc_ref = self.db.collection(self.products_collection).document(product_id)
                    batch.set(doc_ref, translation_doc)
                    saved_count += 1
            
            # Commit batch
            if saved_count > 0:
                batch.commit()
                logger.info(f"✅ Saved {saved_count} product translations to Firestore")
            
            return {
                'products_saved': saved_count,
                'timestamp': timestamp
            }
            
        except Exception as e:
            logger.error(f"❌ Error saving product translations to Firestore: {e}")
            raise
            
    def save_category_translations(self, categories: List[Dict]) -> Dict[str, Any]:
        """Save category translations to optimized Firestore collections"""
        try:
            timestamp = datetime.now(timezone.utc)
            batch = self.db.batch()
            saved_count = 0
            
            for category in categories:
                category_id = str(category.get('id'))
                if not category_id or category_id == 'None':
                    continue
                    
                # Extract translations
                name_translations = category.get('name_translations', {})
                desc_translations = category.get('description_translations', {})
                
                # Create translation document
                translation_doc = {
                    'category_id': int(category.get('id')),
                    'base_name': category.get('name', ''),
                    'base_description': category.get('description', '') or '',
                    'sequence': category.get('sequence', 0),
                    'icon': category.get('icon', ''),
                    'product_count': category.get('product_count', 0),
                    'translations': {},
                    'last_updated': timestamp,
                    'version': '1.0'
                }
                
                # Add language translations
                for lang in self.supported_languages:
                    if lang in name_translations or lang in desc_translations:
                        translation_doc['translations'][lang] = {
                            'name': name_translations.get(lang, category.get('name', '')),
                            'description': desc_translations.get(lang, category.get('description', '') or '')
                        }
                
                # Only save if we have translations
                if translation_doc['translations']:
                    doc_ref = self.db.collection(self.categories_collection).document(category_id)
                    batch.set(doc_ref, translation_doc)
                    saved_count += 1
            
            # Commit batch
            if saved_count > 0:
                batch.commit()
                logger.info(f"✅ Saved {saved_count} category translations to Firestore")
            
            return {
                'categories_saved': saved_count,
                'timestamp': timestamp
            }
            
        except Exception as e:
            logger.error(f"❌ Error saving category translations to Firestore: {e}")
            raise
    
    def save_translation_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Save translation metadata for frontend configuration"""
        try:
            timestamp = datetime.now(timezone.utc)
            
            translation_metadata = {
                'supported_languages': {
                    'vi': 'Vietnamese',
                    'en': 'English', 
                    'fr': 'French',
                    'it': 'Italian',
                    'es': 'Spanish',
                    'zh': 'Chinese (Simplified)',
                    'zh-TW': 'Chinese (Traditional)',
                    'th': 'Thai',
                    'ja': 'Japanese'
                },
                'default_language': 'vi',
                'language_codes': self.supported_languages,
                'last_cache_update': metadata.get('last_updated', timestamp),
                'products_count': metadata.get('products_count', 0),
                'categories_count': metadata.get('categories_count', 0),
                'translation_version': '1.0',
                'updated': timestamp
            }
            
            # Save metadata
            doc_ref = self.db.collection(self.metadata_collection).document('config')
            doc_ref.set(translation_metadata)
            
            logger.info("✅ Saved translation metadata to Firestore")
            return translation_metadata
            
        except Exception as e:
            logger.error(f"❌ Error saving translation metadata to Firestore: {e}")
            raise
    
    def get_product_translations(self, product_id: Union[int, str], language: Optional[str] = None) -> Optional[Dict]:
        """Get translations for a specific product"""
        try:
            doc_ref = self.db.collection(self.products_collection).document(str(product_id))
            doc = doc_ref.get()
            
            if doc.exists:
                data = doc.to_dict()
                if language and language in data.get('translations', {}):
                    return {
                        'product_id': data['product_id'],
                        'language': language,
                        **data['translations'][language]
                    }
                return data
            return None
            
        except Exception as e:
            logger.error(f"❌ Error getting product {product_id} translations: {e}")
            return None
    
    def get_category_translations(self, category_id: Union[int, str], language: Optional[str] = None) -> Optional[Dict]:
        """Get translations for a specific category"""
        try:
            doc_ref = self.db.collection(self.categories_collection).document(str(category_id))
            doc = doc_ref.get()
            
            if doc.exists:
                data = doc.to_dict()
                if language and language in data.get('translations', {}):
                    return {
                        'category_id': data['category_id'],
                        'language': language,
                        **data['translations'][language]
                    }
                return data
            return None
            
        except Exception as e:
            logger.error(f"❌ Error getting category {category_id} translations: {e}")
            return None
    
    def get_all_product_translations(self, language: Optional[str] = None) -> List[Dict]:
        """Get translations for all products, optionally filtered by language"""
        try:
            collection_ref = self.db.collection(self.products_collection)
            docs = collection_ref.stream()
            
            results = []
            for doc in docs:
                data = doc.to_dict()
                if language and language in data.get('translations', {}):
                    results.append({
                        'product_id': data['product_id'],
                        'language': language,
                        **data['translations'][language]
                    })
                elif not language:
                    results.append(data)
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Error getting all product translations: {e}")
            return []
    
    def get_all_category_translations(self, language: Optional[str] = None) -> List[Dict]:
        """Get translations for all categories, optionally filtered by language"""
        try:
            collection_ref = self.db.collection(self.categories_collection)
            docs = collection_ref.stream()
            
            results = []
            for doc in docs:
                data = doc.to_dict()
                if language and language in data.get('translations', {}):
                    results.append({
                        'category_id': data['category_id'],
                        'language': language,
                        **data['translations'][language]
                    })
                elif not language:
                    results.append(data)
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Error getting all category translations: {e}")
            return []
    
    def get_translation_metadata(self) -> Optional[Dict]:
        """Get translation metadata for frontend configuration"""
        try:
            doc_ref = self.db.collection(self.metadata_collection).document('config')
            doc = doc_ref.get()
            
            if doc.exists:
                return doc.to_dict()
            return None
            
        except Exception as e:
            logger.error(f"❌ Error getting translation metadata: {e}")
            return None
    
    def get_supported_languages(self) -> Dict[str, str]:
        """Get list of supported languages with names"""
        metadata = self.get_translation_metadata()
        if metadata and 'supported_languages' in metadata:
            return metadata['supported_languages']
        
        # Fallback to hardcoded languages
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
    
    def clear_translations(self) -> Dict[str, int]:
        """Clear all translation collections (for testing/reset)"""
        try:
            deleted_counts = {'products': 0, 'categories': 0, 'metadata': 0}
            
            # Delete products
            products_ref = self.db.collection(self.products_collection)
            for doc in products_ref.stream():
                doc.reference.delete()
                deleted_counts['products'] += 1
            
            # Delete categories  
            categories_ref = self.db.collection(self.categories_collection)
            for doc in categories_ref.stream():
                doc.reference.delete()
                deleted_counts['categories'] += 1
                
            # Delete metadata
            metadata_ref = self.db.collection(self.metadata_collection)
            for doc in metadata_ref.stream():
                doc.reference.delete()
                deleted_counts['metadata'] += 1
            
            logger.info(f"✅ Cleared translation collections: {deleted_counts}")
            return deleted_counts
            
        except Exception as e:
            logger.error(f"❌ Error clearing translations: {e}")
            raise