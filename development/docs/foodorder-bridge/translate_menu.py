#!/usr/bin/env python3
"""
Vietnamese Restaurant Menu Translation Workflow Script

Automates the complete translation process using Vertex AI Gemini 2.0 Flash
for Vietnamese restaurant menus to multiple languages.

Author: Claude Code Assistant
Version: 1.0.0
"""

import os
import sys
import json
import time
import argparse
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from app.config import get_settings
    from app.services.cache_factory import HybridCacheService
    from app.services.vertex_only_translation_service import VertexOnlyTranslationService
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running this script from the project root directory")
    sys.exit(1)


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('translation_workflow.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


class TranslationWorkflow:
    """Main class for managing the translation workflow"""
    
    def __init__(self, args):
        self.args = args
        self.settings = get_settings()
        self.cache_service = None
        self.translation_service = None
        self.statistics = {
            'total_products': 0,
            'products_translated': 0,
            'total_translations': 0,
            'failed_translations': 0,
            'processing_time': 0,
            'languages_processed': []
        }
        
    def print_header(self):
        """Print colorful header"""
        print(f"{Colors.CYAN}{'=' * 70}{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.BLUE}🍽️  Vietnamese Restaurant Menu Translation Workflow{Colors.ENDC}")
        print(f"{Colors.CYAN}{'=' * 70}{Colors.ENDC}")
        print(f"{Colors.GREEN}🚀 Powered by Vertex AI Gemini 2.0 Flash{Colors.ENDC}")
        print()
    
    def initialize_services(self):
        """Initialize cache and translation services"""
        print(f"{Colors.YELLOW}🔧 Initializing services...{Colors.ENDC}")
        
        try:
            # Initialize cache service
            self.cache_service = HybridCacheService(
                odoo_url=self.settings.ODOO_URL,
                db=self.settings.ODOO_DB,
                username=self.settings.ODOO_USERNAME,
                password=self.settings.ODOO_PASSWORD,
                api_key=self.settings.ODOO_API_KEY
            )
            
            # Initialize translation service
            self.translation_service = CompatibilityTranslationService()
            
            # Check translation service status
            status = self.translation_service.get_translation_status()
            active_service = status.get('migration_info', {}).get('active_service', 'unknown')
            
            print(f"{Colors.GREEN}✅ Cache service initialized{Colors.ENDC}")
            print(f"{Colors.GREEN}✅ Translation service initialized: {active_service}{Colors.ENDC}")
            
            return True
            
        except Exception as e:
            print(f"{Colors.RED}❌ Service initialization failed: {e}{Colors.ENDC}")
            logger.error(f"Service initialization failed: {e}")
            return False
    
    def load_products(self) -> List[Dict]:
        """Load products from cache or Odoo"""
        print(f"{Colors.YELLOW}📦 Loading product data...{Colors.ENDC}")
        
        try:
            if self.args.reload:
                print(f"{Colors.BLUE}🔄 Force reloading from Odoo...{Colors.ENDC}")
                self.cache_service.reload_cache()
            
            products = self.cache_service.get_products()
            categories = self.cache_service.get_categories()
            
            self.statistics['total_products'] = len(products)
            
            print(f"{Colors.GREEN}✅ Loaded {len(products)} products and {len(categories)} categories{Colors.ENDC}")
            
            # Filter active products only
            active_products = [p for p in products if p.get('active', True)]
            print(f"{Colors.BLUE}📊 Active products: {len(active_products)}/{len(products)}{Colors.ENDC}")
            
            return active_products
            
        except Exception as e:
            print(f"{Colors.RED}❌ Failed to load products: {e}{Colors.ENDC}")
            logger.error(f"Failed to load products: {e}")
            return []
    
    def get_target_languages(self) -> List[str]:
        """Get list of target languages"""
        if self.args.languages:
            languages = [lang.strip() for lang in self.args.languages.split(',')]
            # Validate languages
            valid_languages = []
            for lang in languages:
                if lang in self.settings.SUPPORTED_LANGUAGES:
                    valid_languages.append(lang)
                else:
                    print(f"{Colors.YELLOW}⚠️ Skipping unsupported language: {lang}{Colors.ENDC}")
            return valid_languages
        else:
            # All supported languages except Vietnamese (source)
            return [lang for lang in self.settings.SUPPORTED_LANGUAGES if lang != 'vi']
    
    def translate_products(self, products: List[Dict], target_languages: List[str]) -> List[Dict]:
        """Translate products to target languages"""
        if self.args.dry_run:
            print(f"{Colors.YELLOW}🧪 DRY RUN: Would translate {len(products)} products to {len(target_languages)} languages{Colors.ENDC}")
            return products
        
        print(f"{Colors.YELLOW}🌐 Translating {len(products)} products to {len(target_languages)} languages...{Colors.ENDC}")
        
        start_time = time.time()
        translated_products = []
        
        for product in products:
            translated_product = product.copy()
            
            # Initialize translation dictionaries if not present
            if 'name_translations' not in translated_product:
                translated_product['name_translations'] = {'vi': product.get('name', '')}
            
            if 'description_translations' not in translated_product:
                desc = product.get('description_sale', '')
                if desc:
                    translated_product['description_translations'] = {'vi': desc}
            
            translated_products.append(translated_product)
        
        # Process translations by language
        for lang in target_languages:
            print(f"\n{Colors.BLUE}🌍 Processing {self._get_language_flag(lang)} {lang.upper()} translations...{Colors.ENDC}")
            
            try:
                self._translate_to_language(translated_products, lang)
                self.statistics['languages_processed'].append(lang)
                
            except Exception as e:
                print(f"{Colors.RED}❌ Failed to translate to {lang}: {e}{Colors.ENDC}")
                logger.error(f"Failed to translate to {lang}: {e}")
                self.statistics['failed_translations'] += 1
        
        self.statistics['processing_time'] = time.time() - start_time
        return translated_products
    
    def _translate_to_language(self, products: List[Dict], target_lang: str):
        """Translate products to a specific language"""
        # Prepare items for translation
        items_to_translate = []
        
        for product in products:
            # Add name for translation
            if product.get('name') and target_lang not in product.get('name_translations', {}):
                items_to_translate.append({
                    'id': f"prod_{product['id']}_name",
                    'text': product['name'],
                    'type': 'product_name',
                    'product_id': product['id']
                })
            
            # Add description for translation
            if (product.get('description_sale') and 
                'description_translations' in product and 
                target_lang not in product.get('description_translations', {})):
                items_to_translate.append({
                    'id': f"prod_{product['id']}_desc",
                    'text': product['description_sale'],
                    'type': 'product_description',
                    'product_id': product['id']
                })
        
        if not items_to_translate:
            print(f"  {Colors.GREEN}✅ All products already translated to {target_lang}{Colors.ENDC}")
            return
        
        print(f"  📝 Translating {len(items_to_translate)} items...")
        
        # Process in batches
        batch_size = self.args.batch_size
        all_translations = {}
        
        for i in range(0, len(items_to_translate), batch_size):
            batch = items_to_translate[i:i+batch_size]
            batch_num = i//batch_size + 1
            total_batches = (len(items_to_translate)-1)//batch_size + 1
            
            print(f"    Batch {batch_num}/{total_batches} ({len(batch)} items)... ", end='', flush=True)
            
            try:
                # Prepare items for translation API
                api_items = [
                    {'id': item['id'], 'text': item['text'], 'type': item['type']}
                    for item in batch
                ]
                
                # Translate with retry logic
                translations = self._translate_with_retry(api_items, target_lang)
                all_translations.update(translations)
                
                print(f"{Colors.GREEN}✅{Colors.ENDC}")
                
                # Small delay between batches
                if i + batch_size < len(items_to_translate):
                    time.sleep(0.5)
                    
            except Exception as e:
                print(f"{Colors.RED}❌ {str(e)[:50]}...{Colors.ENDC}")
                logger.error(f"Batch {batch_num} failed: {e}")
                self.statistics['failed_translations'] += len(batch)
        
        # Apply translations to products
        translation_count = 0
        for product in products:
            # Apply name translation
            name_key = f"prod_{product['id']}_name"
            if name_key in all_translations:
                product['name_translations'][target_lang] = all_translations[name_key]
                translation_count += 1
            
            # Apply description translation
            desc_key = f"prod_{product['id']}_desc"
            if desc_key in all_translations:
                product['description_translations'][target_lang] = all_translations[desc_key]
                translation_count += 1
        
        self.statistics['total_translations'] += translation_count
        print(f"  {Colors.GREEN}✅ Applied {translation_count} translations{Colors.ENDC}")
    
    def _translate_with_retry(self, items: List[Dict], target_lang: str, max_retries: int = 3) -> Dict:
        """Translate with retry logic"""
        for attempt in range(max_retries):
            try:
                if hasattr(self.translation_service, 'migrator'):
                    vertex_service = self.translation_service.migrator.vertex_service
                    if vertex_service and vertex_service.is_enabled():
                        return vertex_service.translate_batch_with_vertex(items, target_lang, 'vi')
                
                # Fallback to regular translation service
                texts = [item['text'] for item in items]
                translated_texts = self.translation_service.translate_batch(texts, target_lang, 'vi')
                
                return {item['id']: translated_texts[i] for i, item in enumerate(items)}
                
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"⚠️ Retry {attempt + 1}/{max_retries}... ", end='', flush=True)
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    raise e
    
    def save_translations(self, products: List[Dict]):
        """Save translations to all storage systems"""
        if self.args.dry_run:
            print(f"{Colors.YELLOW}🧪 DRY RUN: Would save {len(products)} translated products{Colors.ENDC}")
            return
        
        print(f"{Colors.YELLOW}💾 Saving translations...{Colors.ENDC}")
        
        try:
            # Create backup of current cache
            backup_file = Path('cache/products_backup.json')
            products_file = Path('cache/products.json')
            
            if products_file.exists():
                import shutil
                shutil.copy2(products_file, backup_file)
                print(f"  {Colors.BLUE}📁 Backup created: {backup_file}{Colors.ENDC}")
            
            # Save to main cache
            with open(products_file, 'w', encoding='utf-8') as f:
                json.dump(products, f, ensure_ascii=False, indent=2)
            print(f"  {Colors.GREEN}✅ Saved to cache: {products_file}{Colors.ENDC}")
            
            # Save to Firestore if available
            if hasattr(self.cache_service, 'firestore_service') and self.cache_service.firestore_service:
                try:
                    categories = self.cache_service.get_categories()
                    attributes = self.cache_service.get_attributes()
                    attribute_values = self.cache_service.get_attribute_values()
                    product_attributes = self.cache_service.get_product_attributes()
                    
                    # Update Firestore main cache
                    firestore_metadata = self.cache_service.firestore_service.save_cache_data(
                        categories=categories,
                        products=products,
                        attributes=attributes,
                        attribute_values=attribute_values,
                        product_attributes=product_attributes
                    )
                    
                    # Update translation-optimized collections
                    if hasattr(self.cache_service, 'translation_service') and self.cache_service.translation_service:
                        self.cache_service.translation_service.save_product_translations(products, product_attributes)
                        self.cache_service.translation_service.save_category_translations(categories)
                        self.cache_service.translation_service.save_translation_metadata(firestore_metadata)
                    
                    print(f"  {Colors.GREEN}✅ Saved to Firestore{Colors.ENDC}")
                    
                except Exception as e:
                    print(f"  {Colors.YELLOW}⚠️ Firestore save failed: {e}{Colors.ENDC}")
                    logger.warning(f"Firestore save failed: {e}")
            
            self.statistics['products_translated'] = len(products)
            
        except Exception as e:
            print(f"{Colors.RED}❌ Save failed: {e}{Colors.ENDC}")
            logger.error(f"Save failed: {e}")
            raise
    
    def generate_report(self, products: List[Dict], target_languages: List[str]):
        """Generate comprehensive translation report"""
        print(f"\n{Colors.CYAN}📊 TRANSLATION REPORT{Colors.ENDC}")
        print(f"{Colors.CYAN}{'=' * 50}{Colors.ENDC}")
        
        # Basic statistics
        print(f"{Colors.BOLD}📈 Statistics:{Colors.ENDC}")
        print(f"  Total products: {self.statistics['total_products']}")
        print(f"  Products processed: {len(products)}")
        print(f"  Total translations: {self.statistics['total_translations']}")
        print(f"  Failed translations: {self.statistics['failed_translations']}")
        print(f"  Processing time: {self.statistics['processing_time']:.1f}s")
        
        # Language coverage
        print(f"\n{Colors.BOLD}🌍 Language Coverage:{Colors.ENDC}")
        for lang in target_languages:
            translated_count = sum(1 for p in products if p.get('name_translations', {}).get(lang))
            coverage = (translated_count / len(products) * 100) if products else 0
            flag = self._get_language_flag(lang)
            print(f"  {flag} {lang.upper()}: {translated_count}/{len(products)} ({coverage:.1f}%)")
        
        # Sample translations
        if not self.args.dry_run and products:
            print(f"\n{Colors.BOLD}🍽️ Sample Translations:{Colors.ENDC}")
            sample_products = [p for p in products if p.get('name_translations')][:3]
            
            for product in sample_products:
                code = product.get('code', 'No code')
                vi_name = product.get('name', 'N/A')
                print(f"\n  📍 {code} - {vi_name}")
                
                for lang in target_languages:
                    if lang in product.get('name_translations', {}):
                        translated = product['name_translations'][lang]
                        flag = self._get_language_flag(lang)
                        print(f"    {flag} {lang}: {translated}")
        
        # Save detailed report if requested
        if self.args.report:
            self._save_detailed_report(products, target_languages)
    
    def _save_detailed_report(self, products: List[Dict], target_languages: List[str]):
        """Save detailed report to JSON file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = Path(f'translation_report_{timestamp}.json')
        
        report_data = {
            'timestamp': timestamp,
            'statistics': self.statistics,
            'languages': target_languages,
            'products': []
        }
        
        for product in products:
            product_report = {
                'id': product['id'],
                'code': product.get('code'),
                'name': product.get('name'),
                'translations': {}
            }
            
            for lang in target_languages:
                name_translation = product.get('name_translations', {}).get(lang)
                desc_translation = product.get('description_translations', {}).get(lang)
                
                if name_translation or desc_translation:
                    product_report['translations'][lang] = {
                        'name': name_translation,
                        'description': desc_translation
                    }
            
            report_data['products'].append(product_report)
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        print(f"  {Colors.GREEN}✅ Detailed report saved: {report_file}{Colors.ENDC}")
    
    def _get_language_flag(self, lang_code: str) -> str:
        """Get flag emoji for language"""
        flags = {
            'en': '🇺🇸', 'fr': '🇫🇷', 'es': '🇪🇸', 'it': '🇮🇹',
            'zh': '🇨🇳', 'zh-TW': '🇹🇼', 'th': '🇹🇭', 'ja': '🇯🇵', 'vi': '🇻🇳'
        }
        return flags.get(lang_code, '🌍')
    
    def validate_translations(self, products: List[Dict], target_languages: List[str]) -> bool:
        """Validate translation quality"""
        if self.args.dry_run:
            return True
        
        print(f"\n{Colors.YELLOW}🔍 Validating translations...{Colors.ENDC}")
        
        issues = []
        
        for product in products:
            # Check for missing translations
            for lang in target_languages:
                if product.get('name') and lang not in product.get('name_translations', {}):
                    issues.append(f"Missing {lang} name translation for product {product['id']}")
        
        # Check for code preservation
        for product in products:
            original_name = product.get('name', '')
            code_match = None
            
            # Extract code pattern (A1, B2, C3, etc.)
            import re
            code_pattern = r'\([A-Z]\d+\)'
            code_match = re.search(code_pattern, original_name)
            
            if code_match:
                code = code_match.group()
                for lang in target_languages:
                    translated_name = product.get('name_translations', {}).get(lang, '')
                    if code not in translated_name:
                        issues.append(f"Code {code} missing from {lang} translation of product {product['id']}")
        
        if issues:
            print(f"{Colors.YELLOW}⚠️ Found {len(issues)} validation issues:{Colors.ENDC}")
            for issue in issues[:10]:  # Show first 10 issues
                print(f"    • {issue}")
            if len(issues) > 10:
                print(f"    • ... and {len(issues) - 10} more issues")
            
            return False
        else:
            print(f"{Colors.GREEN}✅ All translations validated successfully{Colors.ENDC}")
            return True
    
    def run(self):
        """Run the complete translation workflow"""
        self.print_header()
        
        # Initialize services
        if not self.initialize_services():
            return False
        
        # Load products
        products = self.load_products()
        if not products:
            print(f"{Colors.RED}❌ No products to translate{Colors.ENDC}")
            return False
        
        # Get target languages
        target_languages = self.get_target_languages()
        if not target_languages:
            print(f"{Colors.RED}❌ No target languages specified{Colors.ENDC}")
            return False
        
        print(f"{Colors.BLUE}🎯 Target languages: {', '.join(target_languages)}{Colors.ENDC}")
        
        # Translate products
        translated_products = self.translate_products(products, target_languages)
        
        # Validate translations
        validation_passed = self.validate_translations(translated_products, target_languages)
        
        # Save translations
        if validation_passed or self.args.force:
            self.save_translations(translated_products)
        else:
            print(f"{Colors.YELLOW}⚠️ Validation failed. Use --force to save anyway.{Colors.ENDC}")
        
        # Generate report
        self.generate_report(translated_products, target_languages)
        
        # Final status
        if self.statistics['failed_translations'] == 0:
            print(f"\n{Colors.GREEN}🎉 Translation workflow completed successfully!{Colors.ENDC}")
            return True
        else:
            print(f"\n{Colors.YELLOW}⚠️ Translation workflow completed with {self.statistics['failed_translations']} failures{Colors.ENDC}")
            return False


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Vietnamese Restaurant Menu Translation Workflow',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python translate_menu.py                          # Translate to all languages
  python translate_menu.py --languages en,fr       # Translate to English and French
  python translate_menu.py --reload --languages en # Force reload and translate to English
  python translate_menu.py --dry-run --report      # Test run with detailed report
        """
    )
    
    parser.add_argument(
        '--languages', '-l',
        type=str,
        help='Comma-separated list of target languages (e.g., en,fr,es)'
    )
    
    parser.add_argument(
        '--reload', '-r',
        action='store_true',
        help='Force reload products from Odoo before translation'
    )
    
    parser.add_argument(
        '--batch-size', '-b',
        type=int,
        default=20,
        help='Number of items to process per batch (default: 20)'
    )
    
    parser.add_argument(
        '--dry-run', '-d',
        action='store_true',
        help='Test run without making changes'
    )
    
    parser.add_argument(
        '--report', '-R',
        action='store_true',
        help='Generate detailed JSON report'
    )
    
    parser.add_argument(
        '--force', '-f',
        action='store_true',
        help='Save translations even if validation fails'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        workflow = TranslationWorkflow(args)
        success = workflow.run()
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}🛑 Translation workflow interrupted by user{Colors.ENDC}")
        sys.exit(130)
        
    except Exception as e:
        print(f"\n{Colors.RED}❌ Translation workflow failed: {e}{Colors.ENDC}")
        logger.error(f"Workflow failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()