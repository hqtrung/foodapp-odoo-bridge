#!/usr/bin/env python3
"""
Debug script to understand why our cache has wrong template attribute values
"""

import os
import xmlrpc.client
from app.config import get_settings

def debug_current_fetch():
    """Debug the current fetching logic to see what we're actually getting"""
    
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
    
    # Step 1: Get POS products (like our cache does)
    print("\n=== Step 1: Getting POS products ===")
    odoo_products = models.execute_kw(
        settings.ODOO_DB, uid, settings.ODOO_API_KEY,
        'product.product', 'search_read',
        [[['available_in_pos', '=', True]]],
        {'fields': ['id', 'name', 'product_tmpl_id']}
    )
    
    print(f"Found {len(odoo_products)} POS products")
    
    # Find product 2478
    product_2478 = next((p for p in odoo_products if p['id'] == 2478), None)
    if product_2478:
        print(f"Product 2478: {product_2478['name']}, Template: {product_2478['product_tmpl_id']}")
    else:
        print("❌ Product 2478 not found in POS products!")
        return
    
    # Step 2: Get template IDs (like our cache does)
    pos_template_ids = list(set([prod['product_tmpl_id'][0] for prod in odoo_products if prod.get('product_tmpl_id')]))
    print(f"\nFound {len(pos_template_ids)} unique template IDs")
    print(f"Template 2507 in list: {2507 in pos_template_ids}")
    
    # Step 3: Get template lines (like our cache does)
    print("\n=== Step 3: Getting template attribute lines ===")
    template_lines = models.execute_kw(
        settings.ODOO_DB, uid, settings.ODOO_API_KEY,
        'product.template.attribute.line', 'search_read',
        [[['product_tmpl_id', 'in', pos_template_ids]]],
        {'fields': ['id', 'product_tmpl_id', 'attribute_id', 'value_ids']}
    )
    
    print(f"Found {len(template_lines)} template attribute lines")
    
    # Find lines for template 2507
    lines_2507 = [line for line in template_lines if line['product_tmpl_id'][0] == 2507]
    print(f"Template 2507 has {len(lines_2507)} attribute lines:")
    
    template_value_ids = []
    for line in lines_2507:
        print(f"  Line {line['id']}: Attribute {line['attribute_id']}, Values: {line['value_ids']}")
        template_value_ids.extend(line.get('value_ids', []))
    
    print(f"Total template value IDs from template 2507: {template_value_ids}")
    
    # Step 4: Get template attribute values (like our cache does)
    print("\n=== Step 4: Getting template attribute values ===")
    if template_value_ids:
        template_attribute_values = models.execute_kw(
            settings.ODOO_DB, uid, settings.ODOO_API_KEY,
            'product.template.attribute.value', 'search_read',
            [[['id', 'in', template_value_ids]]],
            {'fields': ['id', 'name', 'price_extra', 'product_tmpl_id', 
                       'attribute_id', 'product_attribute_value_id', 'product_packaging_id']}
        )
        
        print(f"Found {len(template_attribute_values)} template attribute values:")
        for val in template_attribute_values:
            print(f"  ID: {val['id']} - Name: {val['name']} - Template: {val.get('product_tmpl_id')} - Packaging: {val.get('product_packaging_id')}")
    else:
        print("❌ No template value IDs found!")
    
    # Step 5: Compare with what we know should be there
    print("\n=== Step 5: What should be there vs what we got ===")
    expected_ids = [58, 59, 60, 61, 62]  # From our direct query
    actual_ids = [val['id'] for val in template_attribute_values] if template_value_ids else []
    
    print(f"Expected template attribute value IDs: {expected_ids}")
    print(f"Actually fetched IDs: {actual_ids}")
    print(f"Missing IDs: {set(expected_ids) - set(actual_ids)}")
    print(f"Extra IDs: {set(actual_ids) - set(expected_ids)}")

if __name__ == "__main__":
    debug_current_fetch()