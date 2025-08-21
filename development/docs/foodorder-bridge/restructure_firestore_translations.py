#!/usr/bin/env python3
"""
Restructure Firestore Translations for Easier Language Retrieval
================================================================

New Structure: Collection -> Languages -> Products
- product_translations_v2/{language}/{product_id}

This allows:
1. Bulk fetch all products in a language: product_translations_v2/english  
2. Single query for menu in specific language
3. Easier frontend language switching

Old: product_translations/{product_id}/languages/{language}
New: product_translations_v2/{language}/{product_id}
"""

import json
import logging
import sys
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from google.cloud import firestore
    from google.cloud.firestore import Client
except ImportError:
    print("❌ Error: google-cloud-firestore not installed")
    print("Install with: pip3 install google-cloud-firestore")
    sys.exit(1)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class FirestoreRestructurer:
    """Restructures Firestore translations for language-first access"""
    
    def __init__(self, project_id: str = "finiziapp"):
        """Initialize Firestore client"""
        try:
            self.db = firestore.Client(project=project_id)
            self.old_collection = "product_translations"
            self.new_collection = "product_translations_v2"
            logger.info(f"✅ Connected to Firestore project: {project_id}")
        except Exception as e:
            logger.error(f"❌ Failed to connect to Firestore: {e}")
            raise
    
    def upload_language_first_structure(self) -> Dict[str, int]:
        """Upload translations using the new language-first structure"""
        
        # Translation files mapping
        translation_files = {
            'vietnamese': 'cache/products.json',
            'english': 'rebuilt_english_single_product.json',
            'french': 'rebuilt_french_single_product.json',
            'italian': 'rebuilt_italian_single_product.json',
            'chinese': 'rebuilt_chinese_single_product.json',
            'japanese': 'rebuilt_japanese_single_product.json'
        }
        
        upload_counts = {}
        
        logger.info("🚀 Uploading translations with language-first structure...")
        
        for language, file_path in translation_files.items():
            if not Path(file_path).exists():
                logger.warning(f"⚠️ Missing file: {file_path}")
                continue
                
            if language == 'vietnamese':
                count = self._upload_vietnamese_language_first(file_path, language)
            else:
                count = self._upload_translation_language_first(file_path, language)
            
            upload_counts[language] = count
            logger.info(f"✅ Uploaded {count} {language} products")
        
        return upload_counts
    
    def _upload_vietnamese_language_first(self, file_path: str, language: str) -> int:
        """Upload Vietnamese base data with language-first structure"""
        logger.info(f"📤 Uploading {language} (base data)...")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                products = json.load(f)
            
            uploaded_count = 0
            batch = self.db.batch()
            
            for product in products:
                template_id = str(product.get('template_id'))
                if not template_id or template_id == 'None':
                    continue
                
                # Strip HTML tags from descriptions
                import re
                short_desc = product.get('x_studio_short_description_1', '')
                long_desc = product.get('x_studio_long_description_1', '')
                
                if short_desc:
                    short_desc = re.sub('<[^<]+?>', '', short_desc).strip()
                if long_desc:
                    long_desc = re.sub('<[^<]+?>', '', long_desc).strip()
                
                product_data = {
                    'product_id': int(template_id),
                    'name': product.get('name', ''),
                    'short_description': short_desc,
                    'long_description': long_desc,
                    'price': product.get('list_price', 0),
                    'category': product.get('categ_id', [None, ''])[1] if product.get('categ_id') else '',
                    'category_id': product.get('categ_id', [None, 0])[0] if product.get('categ_id') else 0,
                    'updated_at': firestore.SERVER_TIMESTAMP,
                    'language': language,
                    'is_base_language': True
                }
                
                # New structure: product_translations_v2/{language}/{product_id}
                doc_ref = (self.db.collection(self.new_collection)
                          .document(language)
                          .collection('products')
                          .document(template_id))
                
                batch.set(doc_ref, product_data)
                uploaded_count += 1
                
                # Commit batch every 100 documents
                if uploaded_count % 100 == 0:
                    batch.commit()
                    batch = self.db.batch()
                    logger.info(f"   Batch committed: {uploaded_count} {language} products")
            
            # Commit remaining documents
            if uploaded_count % 100 != 0:
                batch.commit()
            
            return uploaded_count
            
        except Exception as e:
            logger.error(f"❌ Error uploading {language} base data: {e}")
            raise
    
    def _upload_translation_language_first(self, file_path: str, language: str) -> int:
        """Upload translation file with language-first structure"""
        logger.info(f"📤 Uploading {language} translations...")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if 'products' not in data:
                logger.error(f"Invalid translation file format: {file_path}")
                return 0
            
            products = data['products']
            uploaded_count = 0
            batch = self.db.batch()
            
            for product in products:
                # Translation files use product_id
                product_id = str(product.get('product_id', product.get('template_id', product.get('id'))))
                if not product_id or product_id == 'None':
                    continue
                
                product_data = {
                    'product_id': int(product_id),
                    'name': product.get('product_name', product.get('name', '')),
                    'short_description': product.get('short_description', ''),
                    'long_description': product.get('long_description', ''),
                    'price': product.get('list_price', 0),
                    'category': product.get('category', ''),
                    'category_id': product.get('category_id', 0),
                    'updated_at': firestore.SERVER_TIMESTAMP,
                    'language': language,
                    'is_base_language': False
                }
                
                # New structure: product_translations_v2/{language}/{product_id}
                doc_ref = (self.db.collection(self.new_collection)
                          .document(language)
                          .collection('products')
                          .document(product_id))
                
                batch.set(doc_ref, product_data)
                uploaded_count += 1
                
                # Commit batch every 100 documents
                if uploaded_count % 100 == 0:
                    batch.commit()
                    batch = self.db.batch()
                    logger.info(f"   Batch committed: {uploaded_count} {language} products")
            
            # Commit remaining documents
            if uploaded_count % 100 != 0:
                batch.commit()
            
            return uploaded_count
            
        except Exception as e:
            logger.error(f"❌ Error uploading {language} translations: {e}")
            raise
    
    def create_language_metadata(self) -> bool:
        """Create metadata document for language support"""
        try:
            metadata = {
                'supported_languages': {
                    'vietnamese': {'name': 'Tiếng Việt', 'code': 'vi', 'is_default': True},
                    'english': {'name': 'English', 'code': 'en', 'is_default': False},
                    'french': {'name': 'Français', 'code': 'fr', 'is_default': False},
                    'italian': {'name': 'Italiano', 'code': 'it', 'is_default': False},
                    'chinese': {'name': '中文', 'code': 'zh', 'is_default': False},
                    'japanese': {'name': '日本語', 'code': 'ja', 'is_default': False}
                },
                'default_language': 'vietnamese',
                'structure_version': '2.0',
                'collection_name': self.new_collection,
                'last_updated': firestore.SERVER_TIMESTAMP,
                'usage_instructions': {
                    'get_all_products_in_language': f'{self.new_collection}/{{language}}/products',
                    'get_specific_product': f'{self.new_collection}/{{language}}/products/{{product_id}}',
                    'example_query': f'{self.new_collection}/english/products'
                }
            }
            
            # Save metadata
            doc_ref = self.db.collection(self.new_collection).document('_metadata')
            doc_ref.set(metadata)
            
            logger.info("✅ Created language metadata document")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error creating metadata: {e}")
            return False
    
    def test_language_retrieval(self, language: str = 'english', limit: int = 3) -> List[Dict]:
        """Test the new language-first retrieval"""
        try:
            logger.info(f"🧪 Testing retrieval for {language} (limit: {limit})")
            
            # Query all products in a specific language
            products_ref = (self.db.collection(self.new_collection)
                           .document(language)
                           .collection('products')
                           .limit(limit))
            
            docs = products_ref.stream()
            products = []
            
            for doc in docs:
                data = doc.to_dict()
                products.append({
                    'product_id': data.get('product_id'),
                    'name': data.get('name', '')[:50] + '...' if len(data.get('name', '')) > 50 else data.get('name', ''),
                    'price': data.get('price', 0),
                    'category': data.get('category', '')
                })
            
            logger.info(f"✅ Retrieved {len(products)} products in {language}")
            return products
            
        except Exception as e:
            logger.error(f"❌ Error testing retrieval for {language}: {e}")
            return []
    
    def get_collection_stats_v2(self) -> Dict[str, Any]:
        """Get statistics for the new collection structure"""
        try:
            stats = {
                'languages': {},
                'total_products_per_language': {},
                'structure_version': '2.0'
            }
            
            # Get language documents
            languages_ref = self.db.collection(self.new_collection)
            
            for lang_doc in languages_ref.stream():
                if lang_doc.id == '_metadata':
                    continue
                    
                language = lang_doc.id
                
                # Count products in this language
                products_ref = lang_doc.reference.collection('products')
                product_count = len(list(products_ref.stream()))
                
                stats['languages'][language] = True
                stats['total_products_per_language'][language] = product_count
            
            logger.info(f"📊 Collection stats: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"❌ Error getting collection stats: {e}")
            return {}
    
    def cleanup_old_collection(self, confirm: bool = False) -> bool:
        """Clean up the old collection structure (use with caution)"""
        if not confirm:
            logger.warning("⚠️ Cleanup not confirmed. Set confirm=True to delete old collection")
            return False
            
        try:
            logger.info(f"🗑️ Cleaning up old collection: {self.old_collection}")
            
            # Delete all documents in old collection
            products_ref = self.db.collection(self.old_collection)
            deleted_count = 0
            
            for product_doc in products_ref.stream():
                # Delete language subcollections first
                languages_ref = product_doc.reference.collection('languages')
                for lang_doc in languages_ref.stream():
                    lang_doc.reference.delete()
                    deleted_count += 1
                
                # Delete the product document
                product_doc.reference.delete()
            
            logger.info(f"✅ Deleted {deleted_count} documents from old collection")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error cleaning up old collection: {e}")
            return False


def main():
    """Main function to restructure Firestore translations"""
    print("🔄 Restructuring Firestore Translations")
    print("New Structure: Collection -> Languages -> Products")
    print("=" * 60)
    
    # Initialize restructurer
    restructurer = FirestoreRestructurer()
    
    # Upload with new structure
    print("\n📤 Uploading translations with new structure...")
    upload_counts = restructurer.upload_language_first_structure()
    
    total_uploaded = sum(upload_counts.values())
    print(f"\n✅ Upload Complete!")
    print(f"📊 Total products uploaded: {total_uploaded}")
    print("📋 By language:")
    for language, count in upload_counts.items():
        print(f"   - {language}: {count} products")
    
    # Create metadata
    print(f"\n📝 Creating language metadata...")
    metadata_success = restructurer.create_language_metadata()
    
    # Test new retrieval
    print(f"\n🧪 Testing new language-first retrieval...")
    for language in ['vietnamese', 'english', 'french']:
        products = restructurer.test_language_retrieval(language, limit=2)
        if products:
            print(f"✅ {language}:")
            for product in products:
                print(f"   - #{product['product_id']}: {product['name']}")
        else:
            print(f"❌ {language}: No products found")
    
    # Get collection statistics
    print(f"\n📈 New Collection Statistics:")
    stats = restructurer.get_collection_stats_v2()
    if stats:
        print(f"   📦 Languages available: {list(stats['languages'].keys())}")
        print(f"   📊 Products per language:")
        for lang, count in stats['total_products_per_language'].items():
            print(f"      - {lang}: {count}")
    
    print(f"\n🎉 Restructure Complete!")
    print(f"🔗 New Frontend Access Pattern:")
    print(f"   Collection: product_translations_v2")
    print(f"   All English products: product_translations_v2/english/products")
    print(f"   Specific product: product_translations_v2/english/products/2477")
    print(f"   Bulk language query: db.collection('product_translations_v2/english/products').get()")


if __name__ == "__main__":
    main()