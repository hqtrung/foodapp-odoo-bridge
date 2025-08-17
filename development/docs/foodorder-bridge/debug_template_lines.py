#!/usr/bin/env python3
"""
Debug template attribute lines for template 2507 specifically
"""

import os
import xmlrpc.client
from app.config import get_settings

def debug_template_lines():
    """Debug template 2507 attribute lines in detail"""
    
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
    
    # Get ALL attribute lines for template 2507
    print("\n=== ALL attribute lines for template 2507 ===")
    all_lines_2507 = models.execute_kw(
        settings.ODOO_DB, uid, settings.ODOO_API_KEY,
        'product.template.attribute.line', 'search_read',
        [[['product_tmpl_id', '=', 2507]]],
        {'fields': ['id', 'product_tmpl_id', 'attribute_id', 'value_ids']}
    )
    
    print(f"Found {len(all_lines_2507)} attribute lines for template 2507:")
    all_value_ids = []
    for line in all_lines_2507:
        print(f"  Line {line['id']}: Attribute {line['attribute_id']}, Values: {line['value_ids']}")
        all_value_ids.extend(line.get('value_ids', []))
    
    # Get template attribute values that SHOULD belong to template 2507
    print(f"\n=== Template attribute values that should belong to template 2507 ===")
    direct_values_2507 = models.execute_kw(
        settings.ODOO_DB, uid, settings.ODOO_API_KEY,
        'product.template.attribute.value', 'search_read',
        [[['product_tmpl_id', '=', 2507]]],
        {'fields': ['id', 'name', 'price_extra', 'product_tmpl_id', 
                   'attribute_id', 'product_attribute_value_id', 'product_packaging_id']}
    )
    
    print(f"Found {len(direct_values_2507)} template attribute values directly for template 2507:")
    direct_ids = []
    for val in direct_values_2507:
        print(f"  ID: {val['id']} - Name: {val['name']} - Packaging: {val.get('product_packaging_id')}")
        direct_ids.append(val['id'])
    
    # Compare the two approaches
    print(f"\n=== Comparison ===")
    print(f"Value IDs from attribute lines: {all_value_ids}")
    print(f"Value IDs directly from template: {direct_ids}")
    print(f"Missing from lines: {set(direct_ids) - set(all_value_ids)}")
    print(f"Extra in lines: {set(all_value_ids) - set(direct_ids)}")
    
    # Check if the line value_ids point to wrong template
    print(f"\n=== Checking where line value_ids actually belong ===")
    if all_value_ids:
        line_values = models.execute_kw(
            settings.ODOO_DB, uid, settings.ODOO_API_KEY,
            'product.template.attribute.value', 'search_read',
            [[['id', 'in', all_value_ids]]],
            {'fields': ['id', 'name', 'product_tmpl_id']}
        )
        
        for val in line_values:
            template_info = val.get('product_tmpl_id', [None, ''])[1] if val.get('product_tmpl_id') else 'None'
            correct = val.get('product_tmpl_id', [None])[0] == 2507 if val.get('product_tmpl_id') else False
            print(f"  ID {val['id']} ({val['name']}) belongs to template {template_info} - {'✅' if correct else '❌'}")

if __name__ == "__main__":
    debug_template_lines()