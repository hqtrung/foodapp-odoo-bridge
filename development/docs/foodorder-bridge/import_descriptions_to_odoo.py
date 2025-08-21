#!/usr/bin/env python3
"""
Import Vietnamese menu descriptions to Odoo product templates
Uses product.template model to update x_studio_short_description_1 and x_studio_long_description_1 fields
"""

import json
import sys
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from app.services.odoo_cache_service import OdooCacheService
from app.config import get_settings


class MenuDescriptionImporter:
    """Import menu descriptions from JSON to Odoo product templates"""
    
    def __init__(self, dry_run: bool = True):
        """
        Initialize the importer
        
        Args:
            dry_run: If True, show what would be updated without making changes
        """
        self.dry_run = dry_run
        self.settings = get_settings()
        
        # Initialize Odoo connection
        self.odoo_service = OdooCacheService(
            odoo_url=self.settings.ODOO_URL,
            db=self.settings.ODOO_DB,
            username=self.settings.ODOO_USERNAME,
            api_key=self.settings.ODOO_API_KEY
        )
        
        # Statistics
        self.stats = {
            'total_products': 0,
            'successful_updates': 0,
            'failed_updates': 0,
            'skipped_products': 0,
            'templates_not_found': 0
        }
        
        # Track operations for logging
        self.operations = []
        
    def load_descriptions_file(self, file_path: str) -> Dict[str, Any]:
        """Load Vietnamese menu descriptions from JSON file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            products = data.get('products', [])
            print(f"✅ Loaded {len(products)} products from {file_path}")
            return data
            
        except FileNotFoundError:
            print(f"❌ File not found: {file_path}")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in {file_path}: {e}")
            sys.exit(1)
            
    def load_template_mapping(self) -> Dict[int, int]:
        """Load product_id to template_id mapping from cache"""
        cache_file = Path("cache/products.json")
        
        if not cache_file.exists():
            print(f"❌ Cache file not found: {cache_file}")
            print("💡 Run the application first to generate cache files")
            sys.exit(1)
            
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                products = json.load(f)
                
            # Create mapping of product_id -> template_id
            mapping = {}
            for product in products:
                product_id = product.get('id')
                template_id = product.get('template_id')
                
                if product_id and template_id:
                    mapping[product_id] = template_id
                    
            print(f"✅ Loaded template mapping for {len(mapping)} products")
            return mapping
            
        except Exception as e:
            print(f"❌ Error loading template mapping: {e}")
            sys.exit(1)
            
    def validate_template_exists(self, template_id: int) -> bool:
        """Check if template exists in Odoo"""
        try:
            result = self.odoo_service.connection_pool.execute_kw(
                'product.template', 'search',
                [[['id', '=', template_id]]],
                {'limit': 1}
            )
            return len(result) > 0
        except Exception as e:
            print(f"⚠️ Error checking template {template_id}: {e}")
            return False
            
    def backup_current_descriptions(self, template_ids: List[int]) -> Dict[int, Dict[str, str]]:
        """Backup current descriptions before updating"""
        if not template_ids:
            return {}
            
        try:
            print(f"📦 Creating backup of current descriptions for {len(template_ids)} templates...")
            
            current_data = self.odoo_service.connection_pool.execute_kw(
                'product.template', 'search_read',
                [[['id', 'in', template_ids]]],
                {'fields': ['id', 'x_studio_short_description_1', 'x_studio_long_description_1']}
            )
            
            backup = {}
            for template in current_data:
                backup[template['id']] = {
                    'short_description': template.get('x_studio_short_description_1', ''),
                    'long_description': template.get('x_studio_long_description_1', '')
                }
                
            # Save backup to file
            backup_file = f"backup_descriptions_{int(time.time())}.json"
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(backup, f, ensure_ascii=False, indent=2)
                
            print(f"✅ Backup saved to: {backup_file}")
            return backup
            
        except Exception as e:
            print(f"⚠️ Error creating backup: {e}")
            return {}
            
    def update_template_descriptions(self, updates: List[Dict[str, Any]]) -> None:
        """Update product templates with new descriptions"""
        if not updates:
            print("ℹ️ No updates to process")
            return
            
        batch_size = 10
        total_batches = (len(updates) + batch_size - 1) // batch_size
        
        print(f"🔄 Processing {len(updates)} updates in {total_batches} batches...")
        
        for i in range(0, len(updates), batch_size):
            batch = updates[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            
            print(f"📝 Processing batch {batch_num}/{total_batches} ({len(batch)} templates)...")
            
            for update in batch:
                template_id = update['template_id']
                values = update['values']
                
                try:
                    if self.dry_run:
                        print(f"  [DRY RUN] Would update template {template_id}:")
                        print(f"    Short: {values.get('x_studio_short_description_1', '')[:50]}...")
                        print(f"    Long: {values.get('x_studio_long_description_1', '')[:50]}...")
                        self.stats['successful_updates'] += 1
                    else:
                        # Perform actual update
                        self.odoo_service.connection_pool.execute_kw(
                            'product.template', 'write',
                            [[template_id], values]
                        )
                        print(f"  ✅ Updated template {template_id}")
                        self.stats['successful_updates'] += 1
                        
                    # Log the operation
                    self.operations.append({
                        'template_id': template_id,
                        'action': 'updated' if not self.dry_run else 'dry_run',
                        'short_description': values.get('x_studio_short_description_1', ''),
                        'long_description': values.get('x_studio_long_description_1', ''),
                        'timestamp': time.time()
                    })
                    
                except Exception as e:
                    print(f"  ❌ Failed to update template {template_id}: {e}")
                    self.stats['failed_updates'] += 1
                    
            # Small delay between batches to avoid overwhelming Odoo
            if not self.dry_run and batch_num < total_batches:
                time.sleep(0.5)
                
    def import_descriptions(self, descriptions_file: str = "app/data/vietnamese_menu_descriptions.json") -> None:
        """Main import process"""
        print(f"🚀 Starting menu descriptions import...")
        print(f"📂 Source file: {descriptions_file}")
        print(f"🔧 Mode: {'DRY RUN' if self.dry_run else 'LIVE UPDATE'}")
        print(f"🔗 Odoo URL: {self.settings.ODOO_URL}")
        print(f"🗄️ Database: {self.settings.ODOO_DB}")
        print()
        
        # Load descriptions from JSON
        descriptions_data = self.load_descriptions_file(descriptions_file)
        products = descriptions_data.get('products', [])
        self.stats['total_products'] = len(products)
        
        # Load template mapping from cache
        template_mapping = self.load_template_mapping()
        
        # Prepare updates
        updates = []
        missing_templates = []
        
        print(f"🔍 Preparing updates for {len(products)} products...")
        
        for product in products:
            product_id = product.get('product_id')
            short_desc = product.get('short_description', '')
            long_desc = product.get('long_description', '')
            
            if not product_id:
                print(f"⚠️ Skipping product without ID: {product.get('product_name', 'Unknown')}")
                self.stats['skipped_products'] += 1
                continue
                
            # Find template ID
            template_id = template_mapping.get(product_id)
            if not template_id:
                print(f"⚠️ No template mapping found for product ID {product_id}")
                self.stats['templates_not_found'] += 1
                missing_templates.append(product_id)
                continue
                
            # Validate template exists
            if not self.validate_template_exists(template_id):
                print(f"⚠️ Template {template_id} not found in Odoo for product {product_id}")
                self.stats['templates_not_found'] += 1
                missing_templates.append(product_id)
                continue
                
            # Prepare update
            update_values = {}
            if short_desc:
                update_values['x_studio_short_description_1'] = short_desc
            if long_desc:
                update_values['x_studio_long_description_1'] = long_desc
                
            if update_values:
                updates.append({
                    'template_id': template_id,
                    'product_id': product_id,
                    'product_name': product.get('product_name', ''),
                    'values': update_values
                })
            else:
                print(f"ℹ️ No descriptions to update for product {product_id}")
                self.stats['skipped_products'] += 1
                
        print(f"✅ Prepared {len(updates)} updates")
        
        if missing_templates:
            print(f"⚠️ Missing templates for product IDs: {missing_templates}")
            
        if not updates:
            print("❌ No valid updates to process")
            return
            
        # Create backup if not dry run
        if not self.dry_run and updates:
            template_ids = [update['template_id'] for update in updates]
            self.backup_current_descriptions(template_ids)
            
        # Perform updates
        self.update_template_descriptions(updates)
        
        # Print summary
        self.print_summary()
        
        # Save operation log
        self.save_operation_log()
        
    def print_summary(self) -> None:
        """Print import summary"""
        print()
        print("=" * 60)
        print("📊 IMPORT SUMMARY")
        print("=" * 60)
        print(f"📦 Total products in file: {self.stats['total_products']}")
        print(f"✅ Successful updates: {self.stats['successful_updates']}")
        print(f"❌ Failed updates: {self.stats['failed_updates']}")
        print(f"⏭️ Skipped products: {self.stats['skipped_products']}")
        print(f"🔍 Templates not found: {self.stats['templates_not_found']}")
        print()
        
        if self.dry_run:
            print("💡 This was a DRY RUN - no actual changes were made")
            print("💡 Run with --live to perform actual updates")
        else:
            print("✅ Live updates completed successfully!")
            
        print("=" * 60)
        
    def save_operation_log(self) -> None:
        """Save detailed operation log"""
        if not self.operations:
            return
            
        log_file = f"description_import_log_{int(time.time())}.json"
        
        log_data = {
            'timestamp': time.time(),
            'mode': 'dry_run' if self.dry_run else 'live',
            'summary': self.stats,
            'operations': self.operations
        }
        
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, ensure_ascii=False, indent=2)
            
        print(f"📄 Operation log saved to: {log_file}")


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Import Vietnamese menu descriptions to Odoo')
    parser.add_argument('--live', action='store_true', 
                       help='Perform live updates (default is dry run)')
    parser.add_argument('--file', default='app/data/vietnamese_menu_descriptions.json',
                       help='Path to descriptions JSON file')
    
    args = parser.parse_args()
    
    # Initialize importer
    dry_run = not args.live
    importer = MenuDescriptionImporter(dry_run=dry_run)
    
    try:
        # Run import
        importer.import_descriptions(args.file)
        
    except KeyboardInterrupt:
        print("\n🛑 Import interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()