#!/usr/bin/env python3
"""
Debug script to check product.template.attribute.value ID 21
and understand the many-to-many relationships
"""

import os
import xmlrpc.client
from app.config import get_settings

def debug_template_attr_value():
    """Debug template attribute value ID 21"""
    
    settings = get_settings()
    
    # Connect to Odoo
    print(f"Connecting to Odoo at {settings.ODOO_URL}...")
    common = xmlrpc.client.ServerProxy(f'{settings.ODOO_URL}/xmlrpc/2/common')
    
    # Authenticate
    uid = common.authenticate(settings.ODOO_DB, settings.ODOO_USERNAME, settings.ODOO_API_KEY, {})
    if not uid:
        print("❌ Authentication failed")
        return
    
    print(f"✅ Authenticated (User ID: {uid})")
    
    models = xmlrpc.client.ServerProxy(f'{settings.ODOO_URL}/xmlrpc/2/object')
    
    # 1. Check template attribute value ID 21 specifically
    print("\n=== Checking template attribute value ID 21 ===")
    template_attr_value_21 = models.execute_kw(
        settings.ODOO_DB, uid, settings.ODOO_API_KEY,
        'product.template.attribute.value', 'search_read',
        [[['id', '=', 21]]],
        {'fields': ['id', 'name', 'price_extra', 'product_tmpl_id', 
                   'attribute_id', 'product_attribute_value_id', 'product_packaging_id']}
    )
    
    if template_attr_value_21:
        print(f"Found template attribute value ID 21:")
        for attr_val in template_attr_value_21:
            print(f"  ID: {attr_val['id']}")
            print(f"  Name: {attr_val['name']}")
            print(f"  Template ID: {attr_val.get('product_tmpl_id')}")
            print(f"  Attribute ID: {attr_val.get('attribute_id')}")
            print(f"  Base Value ID: {attr_val.get('product_attribute_value_id')}")
            print(f"  Packaging ID: {attr_val.get('product_packaging_id')}")
            print(f"  Price Extra: {attr_val.get('price_extra')}")
            print()
    else:
        print("❌ Template attribute value ID 21 not found")
    
    # 2. Check if there are multiple template attribute values with same base value
    print("=== Checking for 'Thêm Pate' or similar values ===")
    pate_values = models.execute_kw(
        settings.ODOO_DB, uid, settings.ODOO_API_KEY,
        'product.template.attribute.value', 'search_read',
        [[['name', 'ilike', 'pate']]],
        {'fields': ['id', 'name', 'price_extra', 'product_tmpl_id', 
                   'attribute_id', 'product_attribute_value_id', 'product_packaging_id']}
    )
    
    print(f"Found {len(pate_values)} template attribute values containing 'pate':")
    for val in pate_values:
        print(f"  ID: {val['id']} - Name: {val['name']} - Template: {val.get('product_tmpl_id')} - Packaging: {val.get('product_packaging_id')}")
    
    # 3. Check packaging ID 4471
    print("\n=== Checking packaging ID 4471 ===")
    packaging_4471 = models.execute_kw(
        settings.ODOO_DB, uid, settings.ODOO_API_KEY,
        'product.packaging', 'search_read',
        [[['id', '=', 4471]]],
        {'fields': ['id', 'name', 'product_id']}
    )
    
    if packaging_4471:
        print(f"Found packaging ID 4471:")
        for pkg in packaging_4471:
            print(f"  ID: {pkg['id']}")
            print(f"  Name: {pkg.get('name')}")
            print(f"  Product ID: {pkg.get('product_id')}")
    else:
        print("❌ Packaging ID 4471 not found")
    
    # 4. Check what template attribute values exist for template 2507 (product 2478's template)
    print("\n=== Checking all template attribute values for template 2507 ===")
    template_2507_values = models.execute_kw(
        settings.ODOO_DB, uid, settings.ODOO_API_KEY,
        'product.template.attribute.value', 'search_read',
        [[['product_tmpl_id', '=', 2507]]],
        {'fields': ['id', 'name', 'price_extra', 'product_tmpl_id', 
                   'attribute_id', 'product_attribute_value_id', 'product_packaging_id']}
    )
    
    print(f"Found {len(template_2507_values)} template attribute values for template 2507:")
    for val in template_2507_values:
        print(f"  ID: {val['id']} - Name: {val['name']} - Packaging: {val.get('product_packaging_id')} - Base Value: {val.get('product_attribute_value_id')}")
    
    # 5. Check if there are template attribute values linking to product 2499
    print("\n=== Checking template attribute values linking to product 2499 ===")
    
    # First get packaging IDs that link to product 2499
    packagings_2499 = models.execute_kw(
        settings.ODOO_DB, uid, settings.ODOO_API_KEY,
        'product.packaging', 'search_read',
        [[['product_id', '=', 2499]]],
        {'fields': ['id', 'name', 'product_id']}
    )
    
    if packagings_2499:
        print(f"Found {len(packagings_2499)} packaging records for product 2499:")
        packaging_ids = []
        for pkg in packagings_2499:
            print(f"  Packaging ID: {pkg['id']} - Name: {pkg.get('name')}")
            packaging_ids.append(pkg['id'])
        
        # Now find template attribute values using these packaging IDs
        if packaging_ids:
            template_vals_with_2499 = models.execute_kw(
                settings.ODOO_DB, uid, settings.ODOO_API_KEY,
                'product.template.attribute.value', 'search_read',
                [[['product_packaging_id', 'in', packaging_ids]]],
                {'fields': ['id', 'name', 'price_extra', 'product_tmpl_id', 
                           'attribute_id', 'product_attribute_value_id', 'product_packaging_id']}
            )
            
            print(f"\nFound {len(template_vals_with_2499)} template attribute values linking to product 2499:")
            for val in template_vals_with_2499:
                print(f"  ID: {val['id']} - Name: {val['name']} - Template: {val.get('product_tmpl_id')} - Packaging: {val.get('product_packaging_id')}")
    else:
        print("❌ No packaging records found for product 2499")

if __name__ == "__main__":
    debug_template_attr_value()