#!/usr/bin/env python3
"""
Debug script to check available fields on pos.category and product.product models
"""
import xmlrpc.client
import sys

# Add current directory to Python path
sys.path.insert(0, '.')

def check_model_fields():
    print("🔍 Checking Model Fields")
    print("=" * 50)
    
    # Connection details from environment
    from app.config import get_settings
    settings = get_settings()
    url = settings.ODOO_URL
    db_name = settings.ODOO_DB
    username = settings.ODOO_USERNAME
    api_key = settings.ODOO_API_KEY
    
    try:
        # Authenticate
        common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
        uid = common.authenticate(db_name, username, api_key, {})
        print(f"✅ Authenticated (User ID: {uid})")
        
        models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
        
        # Check pos.category fields
        print("\n📋 pos.category model fields:")
        try:
            category_fields = models.execute_kw(
                db_name, uid, api_key,
                'pos.category', 'fields_get',
                [], {}
            )
            
            # Look for image-related fields
            image_fields = []
            for field, info in category_fields.items():
                if 'image' in field.lower():
                    image_fields.append(field)
                    print(f"   🖼️  {field}: {info.get('type', 'unknown')} - {info.get('string', 'No description')}")
            
            if not image_fields:
                print("   ❌ No image fields found")
                print("   Available fields sample:")
                for i, (field, info) in enumerate(category_fields.items()):
                    if i < 10:  # Show first 10 fields
                        print(f"      - {field}: {info.get('type', 'unknown')}")
                    
        except Exception as e:
            print(f"   ❌ Error checking pos.category fields: {e}")
        
        # Check product.product fields
        print("\n📦 product.product model fields (image-related):")
        try:
            product_fields = models.execute_kw(
                db_name, uid, api_key,
                'product.product', 'fields_get',
                [], {}
            )
            
            # Look for image-related fields
            product_image_fields = []
            for field, info in product_fields.items():
                if 'image' in field.lower():
                    product_image_fields.append(field)
                    print(f"   🖼️  {field}: {info.get('type', 'unknown')} - {info.get('string', 'No description')}")
            
            if not product_image_fields:
                print("   ❌ No image fields found")
                
        except Exception as e:
            print(f"   ❌ Error checking product.product fields: {e}")
            
        # Try to get a sample record to see actual field structure
        print("\n📝 Sample pos.category record:")
        try:
            sample_categories = models.execute_kw(
                db_name, uid, api_key,
                'pos.category', 'search_read',
                [[]], {'fields': ['id', 'name'], 'limit': 1}
            )
            
            if sample_categories:
                cat_id = sample_categories[0]['id']
                # Get full record to see all available data
                full_record = models.execute_kw(
                    db_name, uid, api_key,
                    'pos.category', 'read',
                    [[cat_id]], {}
                )
                
                print(f"   Category '{sample_categories[0]['name']}' fields:")
                for key, value in full_record[0].items():
                    if 'image' in key.lower() or key in ['id', 'name']:
                        print(f"      {key}: {type(value).__name__} = {str(value)[:50]}...")
                        
        except Exception as e:
            print(f"   ❌ Error getting sample category: {e}")
            
    except Exception as e:
        print(f"❌ Connection failed: {e}")

if __name__ == "__main__":
    check_model_fields()