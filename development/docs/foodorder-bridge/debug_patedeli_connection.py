#!/usr/bin/env python3
"""
Debug script for Patedeli ERP connection
This script helps diagnose connection issues with the Patedeli Odoo instance
"""
import sys
import xmlrpc.client
import ssl
import traceback

# Add current directory to Python path
sys.path.insert(0, '.')

def test_patedeli_connection():
    print("🚀 Patedeli ERP Connection Diagnostic Tool")
    print("=" * 50)
    
    # Connection details
    url = 'https://erp.patedeli.com'
    api_key = '5e4e018a4d525609eb91730162a0818a76a0460c'
    
    print(f"Target URL: {url}")
    print(f"API Key: ...{api_key[-8:]}")
    print()
    
    try:
        # Step 1: Test basic connectivity
        print("📡 Step 1: Testing basic connectivity...")
        common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
        version = common.version()
        print(f"✅ Server reachable")
        print(f"   Odoo Version: {version.get('server_version', 'unknown')}")
        print(f"   Protocol Version: {version.get('protocol_version', 'unknown')}")
        print()
        
        # Step 2: Test authentication with correct credentials
        print("🔍 Step 2: Testing authentication with provided credentials...")
        db_name = 'patedeli'
        username = 'trung@patedeli.com'
        
        print(f"   Database: {db_name}")
        print(f"   Username: {username}")
        print(f"   API Key: ...{api_key[-8:]}")
        
        try:
            print(f"   Authenticating...", end="")
            uid = common.authenticate(db_name, username, api_key, {})
            if uid and uid != False:
                print(f" ✅ SUCCESS! User ID: {uid}")
                found_db = db_name
            else:
                print(" ❌ Authentication failed")
                found_db = None
        except Exception as e:
            print(f" ❌ Error: {e}")
            found_db = None
        
        if found_db:
            print(f"\\n🎉 Successfully connected to database: {found_db}")
            
            # Step 3: Test API access
            print("\\n🔌 Step 3: Testing API access...")
            models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
            
            try:
                # Test reading user info
                user_info = models.execute_kw(
                    found_db, uid, api_key,
                    'res.users', 'read',
                    [[uid]], {'fields': ['name', 'login', 'groups_id']}
                )
                print(f"✅ API access working")
                print(f"   User: {user_info[0].get('name', 'Unknown')}")
                print(f"   Login: {user_info[0].get('login', 'Unknown')}")
                
                # Test POS access
                print("\\n🛍️  Step 4: Testing POS module access...")
                try:
                    pos_categories = models.execute_kw(
                        found_db, uid, api_key,
                        'pos.category', 'search_read',
                        [[]], {'fields': ['id', 'name'], 'limit': 5}
                    )
                    print(f"✅ POS Categories accessible ({len(pos_categories)} found)")
                    for cat in pos_categories:
                        print(f"   - {cat['name']} (ID: {cat['id']})")
                except Exception as e:
                    print(f"❌ POS Categories error: {e}")
                
                try:
                    pos_products = models.execute_kw(
                        found_db, uid, api_key,
                        'product.product', 'search_read',
                        [[['available_in_pos', '=', True]]], 
                        {'fields': ['id', 'name', 'list_price'], 'limit': 5}
                    )
                    print(f"✅ POS Products accessible ({len(pos_products)} found)")
                    for prod in pos_products:
                        print(f"   - {prod['name']}: {prod['list_price']} (ID: {prod['id']})")
                except Exception as e:
                    print(f"❌ POS Products error: {e}")
                
                print("\\n🎯 Step 5: Creating .env configuration...")
                env_content = f"""# Patedeli ERP Configuration
ODOO_URL=https://erp.patedeli.com
ODOO_DB={found_db}
ODOO_USERNAME={username}
ODOO_API_KEY={api_key}

# API Settings
API_TITLE=FoodOrder Bridge API - Patedeli
API_VERSION=1.0.0
"""
                
                with open('.env', 'w') as f:
                    f.write(env_content)
                
                print(f"✅ Updated .env file with working configuration")
                print(f"   Database: {found_db}")
                print(f"   Username: {username}")
                print(f"   API Key: ...{api_key[-4:]}")
                
                return True
                
            except Exception as e:
                print(f"❌ API access failed: {e}")
                traceback.print_exc()
        else:
            print("\\n❌ No accessible database found")
            print("\\n🔧 Troubleshooting suggestions:")
            print("1. Verify the API key is correct and active")
            print("2. Check if external API access is enabled")
            print("3. Confirm the username (might not be 'admin')")
            print("4. Contact system administrator for:")
            print("   - Correct database name")
            print("   - Valid API credentials")
            print("   - Required permissions for API access")
            
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_patedeli_connection()