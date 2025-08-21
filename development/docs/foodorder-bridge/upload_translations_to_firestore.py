#!/usr/bin/env python3
"""
Upload All Translation Files to Firestore
==========================================

This script uploads all completed translation files (Vietnamese base + 5 languages)
to Firestore using the proposed architecture from the previous conversation.

Files to upload:
- Vietnamese (base): cache/products.json  
- English: rebuilt_english_single_product.json
- French: rebuilt_french_single_product.json
- Italian: rebuilt_italian_single_product.json
- Chinese: rebuilt_chinese_single_product.json
- Japanese: rebuilt_japanese_single_product.json

Target Firestore structure:
product_translations/{template_id}/languages/{language_code}
"""

import json
import logging
import sys
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
import re

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


class FirestoreTranslationUploader:
    """Uploads translations to Firestore with the approved architecture"""
    
    def __init__(self, project_id: str = "finiziapp"):
        """Initialize Firestore client"""
        try:
            self.db = firestore.Client(project=project_id)
            self.collection_name = "product_translations"
            logger.info(f"✅ Connected to Firestore project: {project_id}")
        except Exception as e:
            logger.error(f"❌ Failed to connect to Firestore: {e}")
            raise
    
    def upload_vietnamese_base(self, file_path: str) -> int:
        """Upload Vietnamese base data from Odoo cache"""
        logger.info("📤 Uploading Vietnamese base data...")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                products = json.load(f)
            
            uploaded_count = 0
            
            for product in products:
                template_id = str(product.get('template_id'))
                if not template_id or template_id == 'None':
                    continue
                
                # Strip HTML tags from descriptions  
                short_desc = product.get('x_studio_short_description_1', '')
                long_desc = product.get('x_studio_long_description_1', '')
                
                if short_desc:
                    short_desc = re.sub('<[^<]+?>', '', short_desc).strip()
                if long_desc:
                    long_desc = re.sub('<[^<]+?>', '', long_desc).strip()
                
                translation_data = {
                    'name': product.get('name', ''),
                    'short_description': short_desc,
                    'long_description': long_desc,
                    'price': product.get('list_price', 0),
                    'category': product.get('categ_id', [None, ''])[1] if product.get('categ_id') else '',
                    'updated_at': firestore.SERVER_TIMESTAMP
                }
                
                # Upload to: product_translations/{template_id}/languages/vietnamese
                doc_ref = (self.db.collection(self.collection_name)
                          .document(template_id)
                          .collection('languages')
                          .document('vietnamese'))
                
                doc_ref.set(translation_data)
                uploaded_count += 1
                
                if uploaded_count % 10 == 0:
                    logger.info(f"   Uploaded {uploaded_count} Vietnamese products...")
            
            logger.info(f"✅ Uploaded {uploaded_count} Vietnamese base products")
            return uploaded_count
            
        except Exception as e:
            logger.error(f"❌ Error uploading Vietnamese base data: {e}")
            raise
    
    def upload_translation_file(self, file_path: str, language: str) -> int:
        """Upload a single translation file to Firestore"""
        logger.info(f"📤 Uploading {language} translations...")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if 'products' not in data:
                logger.error(f"Invalid translation file format: {file_path}")
                return 0
            
            products = data['products']
            logger.info(f"   Found {len(products)} products in {language} file")
            uploaded_count = 0
            
            for product in products:
                # Translation files use product_id, not template_id
                template_id = str(product.get('product_id', product.get('template_id', product.get('id'))))
                if not template_id or template_id == 'None':
                    logger.debug(f"Skipping product with invalid template_id: {product}")
                    continue
                
                translation_data = {
                    'name': product.get('product_name', product.get('name', '')),
                    'short_description': product.get('short_description', ''),
                    'long_description': product.get('long_description', ''),
                    'price': product.get('list_price', 0),
                    'category': product.get('category', ''),
                    'category_id': product.get('category_id', 0),
                    'updated_at': firestore.SERVER_TIMESTAMP
                }
                
                # Upload to: product_translations/{template_id}/languages/{language}
                doc_ref = (self.db.collection(self.collection_name)
                          .document(template_id)
                          .collection('languages')
                          .document(language))
                
                doc_ref.set(translation_data)
                uploaded_count += 1
                
                if uploaded_count % 10 == 0:
                    logger.info(f"   Uploaded {uploaded_count} {language} products...")
            
            logger.info(f"✅ Uploaded {uploaded_count} {language} translations")
            return uploaded_count
            
        except Exception as e:
            logger.error(f"❌ Error uploading {language} translations: {e}")
            raise
    
    def get_product_translation(self, template_id: str, language: str) -> Optional[Dict[str, Any]]:
        """Test retrieval of a single product translation"""
        try:
            doc_ref = (self.db.collection(self.collection_name)
                      .document(template_id)
                      .collection('languages')
                      .document(language))
            
            doc = doc_ref.get()
            if doc.exists:
                return doc.to_dict()
            return None
            
        except Exception as e:
            logger.error(f"Error getting translation for product {template_id} in {language}: {e}")
            return None
    
    def get_available_languages(self, template_id: str) -> List[str]:
        """Get available languages for a specific product"""
        try:
            languages_ref = (self.db.collection(self.collection_name)
                           .document(template_id)
                           .collection('languages'))
            
            docs = languages_ref.stream()
            return [doc.id for doc in docs]
            
        except Exception as e:
            logger.error(f"Error getting languages for product {template_id}: {e}")
            return []
    
    def get_collection_stats(self) -> Dict[str, int]:
        """Get statistics about uploaded translations"""
        try:
            products_ref = self.db.collection(self.collection_name)
            total_products = 0
            total_translations = 0
            language_counts = {}
            
            for product_doc in products_ref.limit(100).stream():  # Limit for performance
                total_products += 1
                
                languages_ref = product_doc.reference.collection('languages')
                for lang_doc in languages_ref.stream():
                    total_translations += 1
                    lang = lang_doc.id
                    language_counts[lang] = language_counts.get(lang, 0) + 1
            
            return {
                'total_products': total_products,
                'total_translations': total_translations,
                'language_counts': language_counts
            }
            
        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            return {}


def main():
    """Main function to upload all translations"""
    print("🚀 Starting Firestore Translation Upload")
    print("=" * 50)
    
    # Initialize uploader
    uploader = FirestoreTranslationUploader()
    
    # Define translation files
    translation_files = {
        'vietnamese': 'cache/products.json',
        'english': 'rebuilt_english_single_product.json',
        'french': 'rebuilt_french_single_product.json',
        'italian': 'rebuilt_italian_single_product.json',
        'chinese': 'rebuilt_chinese_single_product.json',
        'japanese': 'rebuilt_japanese_single_product.json'
    }
    
    # Check all files exist
    print("\n🔍 Checking translation files...")
    missing_files = []
    for language, file_path in translation_files.items():
        if not Path(file_path).exists():
            missing_files.append(f"{language}: {file_path}")
            print(f"❌ Missing: {file_path}")
        else:
            print(f"✅ Found: {file_path}")
    
    if missing_files:
        print(f"\n❌ Cannot proceed. Missing files:")
        for missing in missing_files:
            print(f"   - {missing}")
        return
    
    # Upload all translation files
    print(f"\n📤 Uploading translations to Firestore...")
    total_uploaded = 0
    
    # Upload Vietnamese base data first
    try:
        count = uploader.upload_vietnamese_base(translation_files['vietnamese'])
        total_uploaded += count
    except Exception as e:
        logger.error(f"Failed to upload Vietnamese base data: {e}")
        return
    
    # Upload other languages
    for language, file_path in translation_files.items():
        if language == 'vietnamese':
            continue  # Already uploaded
            
        try:
            count = uploader.upload_translation_file(file_path, language)
            total_uploaded += count
        except Exception as e:
            logger.error(f"Failed to upload {language}: {e}")
            continue
    
    print(f"\n✅ Upload Complete!")
    print(f"📊 Total translations uploaded: {total_uploaded}")
    
    # Test retrieval
    print(f"\n🧪 Testing translation retrieval...")
    test_template_id = "2477"  # Use a known product ID
    
    for language in ['vietnamese', 'english', 'french']:
        translation = uploader.get_product_translation(test_template_id, language)
        if translation:
            print(f"✅ {language}: {translation['name'][:50]}...")
        else:
            print(f"❌ {language}: No translation found")
    
    # Get collection statistics
    print(f"\n📈 Collection Statistics:")
    stats = uploader.get_collection_stats()
    if stats:
        print(f"   📦 Total products: {stats.get('total_products', 0)}")
        print(f"   🌐 Total translations: {stats.get('total_translations', 0)}")
        print(f"   📊 By language:")
        for lang, count in stats.get('language_counts', {}).items():
            print(f"      - {lang}: {count}")
    
    print(f"\n🎉 Firestore translation upload completed successfully!")
    print(f"🔗 Frontend can now access translations at:")
    print(f"   Collection: product_translations")
    print(f"   Document path: {{template_id}}/languages/{{language_code}}")
    print(f"   Example: product_translations/2477/languages/english")


if __name__ == "__main__":
    main()