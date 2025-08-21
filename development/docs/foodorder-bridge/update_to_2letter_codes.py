#!/usr/bin/env python3
"""
Update Firestore Language Collections to 2-Letter Codes
======================================================

Updates the collection structure from full language names to 2-letter codes:
- vietnamese -> vi
- english -> en  
- french -> fr
- italian -> it
- chinese -> cn
- japanese -> ja

New Structure: product_translations_v2/{2-letter-code}/products/{product_id}
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


class LanguageCodeUpdater:
    """Updates Firestore collections to use 2-letter language codes"""
    
    def __init__(self, project_id: str = "finiziapp"):
        """Initialize Firestore client"""
        try:
            self.db = firestore.Client(project=project_id)
            self.collection_name = "product_translations_v2"
            logger.info(f"✅ Connected to Firestore project: {project_id}")
        except Exception as e:
            logger.error(f"❌ Failed to connect to Firestore: {e}")
            raise
        
        # Language mapping: full name -> 2-letter code
        self.language_mapping = {
            'vietnamese': 'vi',
            'english': 'en',
            'french': 'fr', 
            'italian': 'it',
            'chinese': 'cn',
            'japanese': 'ja'
        }
        
        # Reverse mapping for display names
        self.code_to_name = {
            'vi': 'Tiếng Việt',
            'en': 'English',
            'fr': 'Français',
            'it': 'Italiano', 
            'cn': '中文',
            'ja': '日本語'
        }
    
    def upload_with_2letter_codes(self) -> Dict[str, int]:
        """Upload translations using 2-letter language codes directly"""
        
        # Translation files mapping to 2-letter codes
        translation_files = {
            'vi': 'cache/products.json',
            'en': 'rebuilt_english_single_product.json',
            'fr': 'rebuilt_french_single_product.json',
            'it': 'rebuilt_italian_single_product.json',
            'cn': 'rebuilt_chinese_single_product.json',
            'ja': 'rebuilt_japanese_single_product.json'
        }
        
        upload_counts = {}
        
        logger.info("🚀 Uploading translations with 2-letter language codes...")
        
        for lang_code, file_path in translation_files.items():
            if not Path(file_path).exists():
                logger.warning(f"⚠️ Missing file: {file_path}")
                continue
                
            if lang_code == 'vi':
                count = self._upload_vietnamese_2letter(file_path, lang_code)
            else:
                count = self._upload_translation_2letter(file_path, lang_code)
            
            upload_counts[lang_code] = count
            logger.info(f"✅ Uploaded {count} {lang_code} products")
        
        return upload_counts
    
    def _upload_vietnamese_2letter(self, file_path: str, lang_code: str) -> int:
        """Upload Vietnamese base data with 2-letter code"""
        logger.info(f"📤 Uploading {lang_code} (Vietnamese base data)...")
        
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
                
                # Process attributes from attribute_lines
                attributes = []
                if product.get('attribute_lines'):
                    for attr_line in product['attribute_lines']:
                        attribute = {
                            'attribute_id': attr_line.get('attribute_id'),
                            'attribute_name': attr_line.get('attribute_name', ''),
                            'display_type': attr_line.get('display_type', ''),
                            'create_variant': attr_line.get('create_variant', ''),
                            'values': attr_line.get('values', [])
                        }
                        attributes.append(attribute)
                
                product_data = {
                    'product_id': int(template_id),
                    'name': product.get('name', ''),
                    'short_description': short_desc,
                    'long_description': long_desc,
                    'price': product.get('list_price', 0),
                    'category': product.get('categ_id', [None, ''])[1] if product.get('categ_id') else '',
                    'category_id': product.get('categ_id', [None, 0])[0] if product.get('categ_id') else 0,
                    'attributes': attributes,
                    'updated_at': firestore.SERVER_TIMESTAMP,
                    'language_code': lang_code,
                    'language_name': self.code_to_name[lang_code],
                    'is_base_language': True
                }
                
                # New structure: product_translations_v2/{lang_code}/products/{product_id}
                doc_ref = (self.db.collection(self.collection_name)
                          .document(lang_code)
                          .collection('products')
                          .document(template_id))
                
                batch.set(doc_ref, product_data)
                uploaded_count += 1
                
                # Commit batch every 100 documents
                if uploaded_count % 100 == 0:
                    batch.commit()
                    batch = self.db.batch()
                    logger.info(f"   Batch committed: {uploaded_count} {lang_code} products")
            
            # Commit remaining documents
            if uploaded_count % 100 != 0:
                batch.commit()
            
            return uploaded_count
            
        except Exception as e:
            logger.error(f"❌ Error uploading {lang_code} base data: {e}")
            raise
    
    def _upload_translation_2letter(self, file_path: str, lang_code: str) -> int:
        """Upload translation file with 2-letter code"""
        logger.info(f"📤 Uploading {lang_code} translations...")
        
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
                    'attributes': product.get('attributes', []),
                    'updated_at': firestore.SERVER_TIMESTAMP,
                    'language_code': lang_code,
                    'language_name': self.code_to_name[lang_code],
                    'is_base_language': False
                }
                
                # New structure: product_translations_v2/{lang_code}/products/{product_id}
                doc_ref = (self.db.collection(self.collection_name)
                          .document(lang_code)
                          .collection('products')
                          .document(product_id))
                
                batch.set(doc_ref, product_data)
                uploaded_count += 1
                
                # Commit batch every 100 documents
                if uploaded_count % 100 == 0:
                    batch.commit()
                    batch = self.db.batch()
                    logger.info(f"   Batch committed: {uploaded_count} {lang_code} products")
            
            # Commit remaining documents
            if uploaded_count % 100 != 0:
                batch.commit()
            
            return uploaded_count
            
        except Exception as e:
            logger.error(f"❌ Error uploading {lang_code} translations: {e}")
            raise
    
    def create_2letter_metadata(self) -> bool:
        """Create metadata document for 2-letter language codes"""
        try:
            metadata = {
                'supported_languages': {
                    'vi': {'name': 'Tiếng Việt', 'code': 'vi', 'is_default': True, 'full_name': 'vietnamese'},
                    'en': {'name': 'English', 'code': 'en', 'is_default': False, 'full_name': 'english'},
                    'fr': {'name': 'Français', 'code': 'fr', 'is_default': False, 'full_name': 'french'},
                    'it': {'name': 'Italiano', 'code': 'it', 'is_default': False, 'full_name': 'italian'},
                    'cn': {'name': '中文', 'code': 'cn', 'is_default': False, 'full_name': 'chinese'},
                    'ja': {'name': '日本語', 'code': 'ja', 'is_default': False, 'full_name': 'japanese'}
                },
                'default_language': 'vi',
                'structure_version': '2.1',
                'collection_name': self.collection_name,
                'language_code_format': '2-letter',
                'last_updated': firestore.SERVER_TIMESTAMP,
                'usage_instructions': {
                    'get_all_products_in_language': f'{self.collection_name}/{{lang_code}}/products',
                    'get_specific_product': f'{self.collection_name}/{{lang_code}}/products/{{product_id}}',
                    'example_queries': {
                        'english_products': f'{self.collection_name}/en/products',
                        'french_product_1186': f'{self.collection_name}/fr/products/1186',
                        'chinese_categories': f'{self.collection_name}/cn/products (filter by category_id)'
                    }
                }
            }
            
            # Save metadata
            doc_ref = self.db.collection(self.collection_name).document('_metadata')
            doc_ref.set(metadata)
            
            logger.info("✅ Created 2-letter language metadata document")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error creating metadata: {e}")
            return False
    
    def test_2letter_retrieval(self, lang_code: str = 'en', limit: int = 3) -> List[Dict]:
        """Test the new 2-letter code retrieval"""
        try:
            logger.info(f"🧪 Testing retrieval for {lang_code} (limit: {limit})")
            
            # Query all products in a specific language using 2-letter code
            products_ref = (self.db.collection(self.collection_name)
                           .document(lang_code)
                           .collection('products')
                           .limit(limit))
            
            docs = products_ref.stream()
            products = []
            
            for doc in docs:
                data = doc.to_dict()
                products.append({
                    'product_id': data.get('product_id'),
                    'name': data.get('name', '')[:50] + '...' if len(data.get('name', '')) > 50 else data.get('name', ''),
                    'language_code': data.get('language_code'),
                    'language_name': data.get('language_name'),
                    'price': data.get('price', 0)
                })
            
            logger.info(f"✅ Retrieved {len(products)} products in {lang_code}")
            return products
            
        except Exception as e:
            logger.error(f"❌ Error testing retrieval for {lang_code}: {e}")
            return []
    
    def cleanup_old_language_names(self, confirm: bool = False) -> Dict[str, int]:
        """Clean up the old full-name language collections"""
        if not confirm:
            logger.warning("⚠️ Cleanup not confirmed. Set confirm=True to delete old language collections")
            return {}
            
        try:
            deleted_counts = {}
            old_language_names = ['vietnamese', 'english', 'french', 'italian', 'chinese', 'japanese']
            
            for old_name in old_language_names:
                logger.info(f"🗑️ Cleaning up old collection: {old_name}")
                
                # Delete products in old language collection
                products_ref = (self.db.collection(self.collection_name)
                               .document(old_name)
                               .collection('products'))
                
                deleted_count = 0
                for product_doc in products_ref.stream():
                    product_doc.reference.delete()
                    deleted_count += 1
                
                # Delete the language document itself
                if deleted_count > 0:
                    lang_doc_ref = self.db.collection(self.collection_name).document(old_name)
                    lang_doc_ref.delete()
                
                deleted_counts[old_name] = deleted_count
                logger.info(f"✅ Deleted {deleted_count} products from {old_name}")
            
            return deleted_counts
            
        except Exception as e:
            logger.error(f"❌ Error cleaning up old collections: {e}")
            return {}
    
    def get_2letter_stats(self) -> Dict[str, Any]:
        """Get statistics for the new 2-letter code structure"""
        try:
            stats = {
                'language_codes': {},
                'total_products_per_language': {},
                'structure_version': '2.1 - 2-letter codes'
            }
            
            # Get language documents
            languages_ref = self.db.collection(self.collection_name)
            
            for lang_doc in languages_ref.stream():
                if lang_doc.id == '_metadata':
                    continue
                    
                lang_code = lang_doc.id
                
                # Only process 2-letter codes
                if len(lang_code) != 2:
                    continue
                
                # Count products in this language
                products_ref = lang_doc.reference.collection('products')
                product_count = len(list(products_ref.stream()))
                
                stats['language_codes'][lang_code] = self.code_to_name.get(lang_code, lang_code)
                stats['total_products_per_language'][lang_code] = product_count
            
            logger.info(f"📊 2-letter code stats: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"❌ Error getting 2-letter code stats: {e}")
            return {}


def main():
    """Main function to update to 2-letter language codes"""
    print("🔄 Updating to 2-Letter Language Codes")
    print("New Structure: Collection -> 2-Letter Codes -> Products")
    print("=" * 60)
    
    # Initialize updater
    updater = LanguageCodeUpdater()
    
    # Upload with 2-letter codes
    print("\n📤 Uploading translations with 2-letter codes...")
    upload_counts = updater.upload_with_2letter_codes()
    
    total_uploaded = sum(upload_counts.values())
    print(f"\n✅ Upload Complete!")
    print(f"📊 Total products uploaded: {total_uploaded}")
    print("📋 By language code:")
    for lang_code, count in upload_counts.items():
        lang_name = updater.code_to_name.get(lang_code, lang_code)
        print(f"   - {lang_code} ({lang_name}): {count} products")
    
    # Create metadata
    print(f"\n📝 Creating 2-letter language metadata...")
    metadata_success = updater.create_2letter_metadata()
    
    # Test new retrieval
    print(f"\n🧪 Testing 2-letter code retrieval...")
    for lang_code in ['vi', 'en', 'fr']:
        products = updater.test_2letter_retrieval(lang_code, limit=2)
        if products:
            print(f"✅ {lang_code}:")
            for product in products:
                print(f"   - #{product['product_id']}: {product['name']} ({product['language_name']})")
        else:
            print(f"❌ {lang_code}: No products found")
    
    # Get collection statistics
    print(f"\n📈 2-Letter Code Statistics:")
    stats = updater.get_2letter_stats()
    if stats:
        print(f"   📦 Language codes available: {list(stats['language_codes'].keys())}")
        print(f"   📊 Products per language:")
        for code, count in stats['total_products_per_language'].items():
            name = stats['language_codes'].get(code, code)
            print(f"      - {code} ({name}): {count}")
    
    print(f"\n🎉 2-Letter Code Update Complete!")
    print(f"🔗 New Frontend Access Pattern:")
    print(f"   Collection: product_translations_v2")
    print(f"   All English products: product_translations_v2/en/products")
    print(f"   Specific French product: product_translations_v2/fr/products/1186")
    print(f"   Chinese categories: product_translations_v2/cn/products (filter by category_id)")
    
    print(f"\n📝 Language Code Mapping:")
    for code, name in updater.code_to_name.items():
        print(f"   {code} = {name}")


if __name__ == "__main__":
    main()