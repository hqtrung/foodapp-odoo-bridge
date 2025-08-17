import json
import os
import base64
from datetime import datetime
from pathlib import Path
import xmlrpc.client
from typing import Dict, List, Any, Optional
from PIL import Image
from io import BytesIO


class OdooCacheService:
    def __init__(self, odoo_url: str, db: str, username: str = None, password: str = None, api_key: str = None):
        self.odoo_url = odoo_url
        self.db = db
        self.username = username
        self.password = password
        self.api_key = api_key
        
        # Validate authentication method
        if api_key:
            # When using API key, username is required but password should be the API key
            if not username:
                raise ValueError("Username is required when using API key authentication")
            self.auth_method = "api_key"
            self.password = api_key  # Use API key as password for XML-RPC
        elif username and password:
            self.auth_method = "username_password"
        else:
            raise ValueError("Either provide (username + api_key) or (username + password)")
        self.cache_dir = Path("cache")
        self.cache_dir.mkdir(exist_ok=True)
        
        # Setup image directories
        self.images_dir = Path("public/images")
        self.categories_img_dir = self.images_dir / "categories"
        self.products_img_dir = self.images_dir / "products"
        
        # Create directories
        self.categories_img_dir.mkdir(parents=True, exist_ok=True)
        self.products_img_dir.mkdir(parents=True, exist_ok=True)
        
    def reload_cache(self) -> Dict[str, Any]:
        """Fetch data from Odoo, save images locally, and update JSON cache"""
        print(f"Connecting to Odoo at {self.odoo_url} using {self.auth_method} authentication...")
        
        # Connect to Odoo
        common = xmlrpc.client.ServerProxy(f'{self.odoo_url}/xmlrpc/2/common')
        
        # Authenticate with Odoo (API key is used as password)
        uid = common.authenticate(self.db, self.username, self.password, {})
        
        if not uid:
            auth_info = f"API key ending in {'...' + self.api_key[-4:] if self.api_key else 'password'}"
            raise ValueError(f"Failed to authenticate with Odoo using {self.auth_method}. Check credentials: {auth_info}")
        
        print(f"✅ Authenticated successfully with Odoo (User ID: {uid})")
        
        models = xmlrpc.client.ServerProxy(f'{self.odoo_url}/xmlrpc/2/object')
        
        # Fetch categories with images
        print("Fetching POS categories from Odoo...")
        odoo_categories = models.execute_kw(
            self.db, uid, self.password,
            'pos.category', 'search_read',
            [[]],
            {'fields': ['id', 'name', 'parent_id', 'sequence', 'image_128']}
        )
        
        # Process categories and save images
        categories = []
        for cat in odoo_categories:
            image_url = None
            if cat.get('image_128'):
                image_url = self._save_image(
                    cat['image_128'], 
                    'category', 
                    cat['id']
                )
            
            categories.append({
                'id': cat['id'],
                'name': cat['name'],
                'parent_id': cat['parent_id'],
                'sequence': cat['sequence'],
                'image_url': image_url  # Relative URL instead of base64
            })
        
        print(f"Processed {len(categories)} categories")
        
        # Fetch products with images
        print("Fetching POS products from Odoo...")
        odoo_products = models.execute_kw(
            self.db, uid, self.password,
            'product.product', 'search_read',
            [[['available_in_pos', '=', True]]],
            {'fields': ['id', 'name', 'pos_categ_id', 
                       'description_sale', 'image_512', 'barcode', 'product_tmpl_id',
                       'available_in_pos', 'categ_id']}
        )
        
        # Get unique template IDs to fetch list_price from product.template
        template_ids = list(set([prod['product_tmpl_id'][0] for prod in odoo_products if prod.get('product_tmpl_id')]))
        
        # Fetch list_price from product templates
        template_prices = {}
        if template_ids:
            print("Fetching template prices from Odoo...")
            odoo_templates = models.execute_kw(
                self.db, uid, self.password,
                'product.template', 'search_read',
                [[['id', 'in', template_ids]]],
                {'fields': ['id', 'list_price']}
            )
            template_prices = {tmpl['id']: tmpl['list_price'] for tmpl in odoo_templates}
        
        # Store basic product data for later attribute enrichment
        basic_products = []
        for prod in odoo_products:
            image_url = None
            if prod.get('image_512'):
                image_url = self._save_image(
                    prod['image_512'], 
                    'product', 
                    prod['id']
                )
            
            # Get list_price from template
            template_id = prod['product_tmpl_id'][0] if prod.get('product_tmpl_id') else None
            list_price = template_prices.get(template_id, 0.0) if template_id else 0.0
            
            basic_products.append({
                'id': prod['id'],
                'name': prod['name'],
                'pos_categ_id': prod['pos_categ_id'],
                'list_price': list_price,
                'description_sale': prod['description_sale'],
                'barcode': prod['barcode'],
                'image_url': image_url,  # Relative URL instead of base64
                'product_tmpl_id': prod.get('product_tmpl_id'),
                'available_in_pos': prod.get('available_in_pos', True),
                'categ_id': prod.get('categ_id')
            })
        
        print(f"Processed {len(basic_products)} products")
        
        # Fetch product attributes and attribute values for toppings/options
        print("Fetching product attributes from Odoo...")
        attributes = models.execute_kw(
            self.db, uid, self.password,
            'product.attribute', 'search_read',
            [[]],
            {'fields': ['id', 'name', 'create_variant', 'display_type']}
        )
        
        print("Fetching attribute values from Odoo...")
        attribute_values = models.execute_kw(
            self.db, uid, self.password,
            'product.attribute.value', 'search_read',
            [[]],
            {'fields': ['id', 'name', 'attribute_id']}
        )
        
        print("Fetching product template attribute lines from Odoo...")
        # Get attribute lines for POS products only
        pos_template_ids = list(set([prod['product_tmpl_id'][0] for prod in odoo_products if prod.get('product_tmpl_id')]))
        
        if pos_template_ids:
            template_lines = models.execute_kw(
                self.db, uid, self.password,
                'product.template.attribute.line', 'search_read',
                [[['product_tmpl_id', 'in', pos_template_ids]]],
                {'fields': ['id', 'product_tmpl_id', 'attribute_id', 'value_ids']}
            )
        else:
            template_lines = []
        
        print("Fetching template attribute values with price extras...")
        # Get template attribute values directly by template IDs (more reliable than attribute lines)
        # This fixes the issue where attribute lines may reference wrong template attribute values
        if pos_template_ids:
            template_attribute_values = models.execute_kw(
                self.db, uid, self.password,
                'product.template.attribute.value', 'search_read',
                [[['product_tmpl_id', 'in', pos_template_ids]]],
                {'fields': ['id', 'name', 'price_extra', 'product_tmpl_id', 
                           'attribute_id', 'product_attribute_value_id', 'product_packaging_id']}
            )
        else:
            template_attribute_values = []
            
        # Get packaging data for attribute values that have product_packaging_id
        packaging_ids = []
        for val in template_attribute_values:
            if val.get('product_packaging_id'):
                packaging_ids.append(val['product_packaging_id'][0])
        
        packaging_data = {}
        if packaging_ids:
            print("Fetching product packaging data for attribute values...")
            packagings = models.execute_kw(
                self.db, uid, self.password,
                'product.packaging', 'search_read',
                [[['id', 'in', packaging_ids]]],
                {'fields': ['id', 'product_id']}
            )
            packaging_data = {pkg['id']: pkg for pkg in packagings}
            
            # Get linked product data
            linked_product_ids = [pkg['product_id'][0] for pkg in packagings if pkg.get('product_id')]
            linked_products_data = {}
            if linked_product_ids:
                print("Fetching linked product data...")
                linked_products = models.execute_kw(
                    self.db, uid, self.password,
                    'product.product', 'search_read',
                    [[['id', 'in', linked_product_ids]]],
                    {'fields': ['id', 'name', 'product_tmpl_id']}
                )
                linked_products_data = {prod['id']: prod for prod in linked_products}
                
                # Get linked product template prices
                linked_template_ids = [prod['product_tmpl_id'][0] for prod in linked_products if prod.get('product_tmpl_id')]
                linked_template_prices = {}
                if linked_template_ids:
                    print("Fetching linked product template prices...")
                    linked_templates = models.execute_kw(
                        self.db, uid, self.password,
                        'product.template', 'search_read',
                        [[['id', 'in', linked_template_ids]]],
                        {'fields': ['id', 'list_price']}
                    )
                    linked_template_prices = {tmpl['id']: tmpl['list_price'] for tmpl in linked_templates}
        
        # Process attributes into structured data
        attributes_data = self._process_attributes(
            attributes, 
            attribute_values, 
            template_lines, 
            template_attribute_values,
            basic_products,
            packaging_data,
            linked_products_data,
            linked_template_prices
        )
        
        # Enrich products with their attribute data and frontend-required fields
        products_with_attributes = self._enrich_products_with_attributes(basic_products, attributes_data['product_attributes'])
        products = self._enrich_products_with_frontend_fields(products_with_attributes)
        
        # Enrich categories with frontend-required fields
        enriched_categories = self._enrich_categories_with_frontend_fields(categories, products)
        
        print(f"Processed {len(attributes)} attributes, {len(attribute_values)} attribute values")
        print(f"Enriched {len([p for p in products if p.get('attribute_lines')])} products with attributes")
        
        # Save to JSON files
        self._save_json('categories.json', enriched_categories)
        self._save_json('products.json', products)
        self._save_json('attributes.json', attributes_data['attributes'])
        self._save_json('attribute_values.json', attributes_data['attribute_values'])
        self._save_json('product_attributes.json', attributes_data['product_attributes'])
        
        # Clean up old images not in current data
        self._cleanup_old_images(enriched_categories, products)
        
        # Save metadata
        metadata = {
            'last_updated': datetime.now().isoformat(),
            'categories_count': len(enriched_categories),
            'products_count': len(products),
            'attributes_count': len(attributes_data['attributes']),
            'attribute_values_count': len(attributes_data['attribute_values']),
            'products_with_attributes_count': len(attributes_data['product_attributes']),
            'total_images': self._count_images()
        }
        self._save_json('metadata.json', metadata)
        
        print(f"Cache reload completed. Categories: {len(categories)}, Products: {len(products)}, Attributes: {len(attributes_data['attributes'])}, Images: {metadata['total_images']}")
        return metadata
    
    def _save_image(self, base64_data: str, image_type: str, item_id: int) -> Optional[str]:
        """Save base64 image to file and return relative URL"""
        if not base64_data:
            return None
        
        try:
            # Decode base64
            image_data = base64.b64decode(base64_data)
            
            # Open image with PIL to validate and optimize
            img = Image.open(BytesIO(image_data))
            
            # Convert RGBA to RGB if needed (for JPEG)
            if img.mode in ('RGBA', 'LA', 'P'):
                # Create a white background
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            
            # Resize if too large (max 800x800)
            max_size = (800, 800)
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Determine directory and filename
            if image_type == 'category':
                img_dir = self.categories_img_dir
                url_path = f"/images/categories/{item_id}.jpg"
            else:  # product
                img_dir = self.products_img_dir
                url_path = f"/images/products/{item_id}.jpg"
            
            # Save optimized image
            img_path = img_dir / f"{item_id}.jpg"
            img.save(img_path, 'JPEG', quality=85, optimize=True)
            
            return url_path
            
        except Exception as e:
            print(f"Error saving image for {image_type} {item_id}: {e}")
            return None
    
    def _cleanup_old_images(self, categories: List[Dict], products: List[Dict]):
        """Remove images that are no longer in use"""
        # Get current IDs
        category_ids = {str(cat['id']) for cat in categories}
        product_ids = {str(prod['id']) for prod in products}
        
        # Clean category images
        cleaned_categories = 0
        for img_file in self.categories_img_dir.glob("*.jpg"):
            img_id = img_file.stem
            if img_id not in category_ids:
                img_file.unlink()
                cleaned_categories += 1
        
        # Clean product images
        cleaned_products = 0
        for img_file in self.products_img_dir.glob("*.jpg"):
            img_id = img_file.stem
            if img_id not in product_ids:
                img_file.unlink()
                cleaned_products += 1
        
        if cleaned_categories > 0 or cleaned_products > 0:
            print(f"Cleaned up {cleaned_categories} category images and {cleaned_products} product images")
    
    def _count_images(self) -> int:
        """Count total number of cached images"""
        cat_images = len(list(self.categories_img_dir.glob("*.jpg")))
        prod_images = len(list(self.products_img_dir.glob("*.jpg")))
        return cat_images + prod_images
    
    def get_categories(self) -> List[Dict]:
        """Load categories from cache"""
        return self._load_json('categories.json', default=[])
    
    def get_products(self) -> List[Dict]:
        """Load products from cache"""
        return self._load_json('products.json', default=[])
    
    def get_products_by_category(self, category_id: int) -> List[Dict]:
        """Get products filtered by category"""
        products = self.get_products()
        return [
            prod for prod in products 
            if prod.get('pos_categ_id') and prod['pos_categ_id'][0] == category_id
        ]
    
    def get_attributes(self) -> List[Dict]:
        """Load attributes from cache"""
        return self._load_json('attributes.json', default=[])
    
    def get_attribute_values(self) -> List[Dict]:
        """Load attribute values from cache"""
        return self._load_json('attribute_values.json', default=[])
    
    def get_product_attributes(self) -> Dict:
        """Load product attributes from cache"""
        return self._load_json('product_attributes.json', default={})
    
    def get_product_attributes_by_id(self, product_id: int) -> Dict:
        """Get attributes for a specific product"""
        product_attributes = self.get_product_attributes()
        return product_attributes.get(str(product_id), {})
    
    def get_cache_status(self) -> Dict:
        """Get cache metadata"""
        metadata = self._load_json('metadata.json', default={
            'last_updated': None,
            'categories_count': 0,
            'products_count': 0,
            'total_images': 0
        })
        metadata['current_images'] = self._count_images()
        
        # Add cache file sizes
        try:
            categories_size = (self.cache_dir / 'categories.json').stat().st_size if (self.cache_dir / 'categories.json').exists() else 0
            products_size = (self.cache_dir / 'products.json').stat().st_size if (self.cache_dir / 'products.json').exists() else 0
            metadata['cache_size_bytes'] = categories_size + products_size
        except Exception:
            metadata['cache_size_bytes'] = 0
        
        return metadata
    
    def _save_json(self, filename: str, data: Any):
        """Save data to JSON file"""
        filepath = self.cache_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def _load_json(self, filename: str, default: Any = None):
        """Load data from JSON file"""
        filepath = self.cache_dir / filename
        if not filepath.exists():
            return default
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def test_connection(self) -> Dict[str, Any]:
        """Test connection to Odoo server"""
        try:
            common = xmlrpc.client.ServerProxy(f'{self.odoo_url}/xmlrpc/2/common')
            version = common.version()
            
            # Test authentication
            uid = common.authenticate(self.db, self.username, self.password, {})
            
            return {
                'status': 'success',
                'odoo_version': version.get('server_version', 'unknown'),
                'authenticated': uid is not False,
                'user_id': uid,
                'auth_method': self.auth_method,
                'database': self.db,
                'username': self.username,
                'server_url': self.odoo_url
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'authenticated': False,
                'auth_method': self.auth_method,
                'database': self.db,
                'username': self.username,
                'server_url': self.odoo_url
            }
    
    def _process_attributes(self, attributes, attribute_values, template_lines, template_attribute_values, products, packaging_data={}, linked_products_data={}, linked_template_prices={}):
        """Process attribute data into structured format for caching"""
        
        # Create lookup dictionaries
        attributes_by_id = {attr['id']: attr for attr in attributes}
        values_by_id = {val['id']: val for val in attribute_values}
        template_values_by_id = {tval['id']: tval for tval in template_attribute_values}
        
        # Process attributes list
        processed_attributes = []
        for attr in attributes:
            processed_attributes.append({
                'id': attr['id'],
                'name': attr['name'],
                'create_variant': attr['create_variant'],
                'display_type': attr['display_type']
            })
        
        # Process attribute values with base info
        processed_attribute_values = []
        for val in attribute_values:
            processed_attribute_values.append({
                'id': val['id'],
                'name': val['name'],
                'attribute_id': val['attribute_id'][0] if val['attribute_id'] else None,
                'attribute_name': val['attribute_id'][1] if val['attribute_id'] else None
            })
        
        # Process product-specific attribute information
        product_attributes = {}
        
        # Group template attribute values by template and attribute
        values_by_template_and_attr = {}
        for template_val in template_attribute_values:
            template_id = template_val['product_tmpl_id'][0] if template_val.get('product_tmpl_id') else None
            attr_id = template_val['attribute_id'][0] if template_val.get('attribute_id') else None
            
            if template_id and attr_id:
                if template_id not in values_by_template_and_attr:
                    values_by_template_and_attr[template_id] = {}
                if attr_id not in values_by_template_and_attr[template_id]:
                    values_by_template_and_attr[template_id][attr_id] = []
                values_by_template_and_attr[template_id][attr_id].append(template_val)
        
        # Map products to their templates and build attribute data directly from template attribute values
        for product in products:
            product_id = product['id']
            template_id = product['product_tmpl_id'][0] if product.get('product_tmpl_id') else None
            
            if template_id and template_id in values_by_template_and_attr:
                attribute_lines = []
                
                for attr_id, template_vals in values_by_template_and_attr[template_id].items():
                    if attr_id in attributes_by_id:
                        attribute = attributes_by_id[attr_id]
                        
                        # Process template attribute values for this attribute
                        line_values = []
                        for template_val in template_vals:
                            base_val_id = template_val.get('product_attribute_value_id')
                            base_val_id = base_val_id[0] if isinstance(base_val_id, list) else base_val_id
                            
                            if base_val_id and base_val_id in values_by_id:
                                base_val = values_by_id[base_val_id]
                                
                                # Build value data structure
                                value_data = {
                                    'id': template_val['id'],
                                    'name': template_val['name'],
                                    'price_extra': template_val.get('price_extra', 0),
                                    'base_value_id': base_val_id,
                                    'base_value_name': base_val['name']
                                }
                                
                                # Add linked product data if available
                                packaging_id = template_val.get('product_packaging_id')
                                if packaging_id:
                                    pkg_id = packaging_id[0] if isinstance(packaging_id, list) else packaging_id
                                    if pkg_id in packaging_data:
                                        pkg = packaging_data[pkg_id]
                                        linked_product_id = pkg['product_id'][0] if pkg.get('product_id') else None
                                        
                                        if linked_product_id and linked_product_id in linked_products_data:
                                            linked_product = linked_products_data[linked_product_id]
                                            linked_template_id = linked_product['product_tmpl_id'][0] if linked_product.get('product_tmpl_id') else None
                                            linked_price = linked_template_prices.get(linked_template_id, 0.0) if linked_template_id else 0.0
                                            
                                            value_data.update({
                                                'product_packaging_id': pkg_id,
                                                'linked_product_id': linked_product_id,
                                                'linked_product_name': linked_product['name'],
                                                'linked_product_price': linked_price
                                            })
                                
                                line_values.append(value_data)
                        
                        if line_values:  # Only include attributes that have values
                            attribute_lines.append({
                                'attribute_id': attr_id,
                                'attribute_name': attribute['name'],
                                'display_type': attribute['display_type'],
                                'create_variant': attribute['create_variant'],
                                'values': line_values
                            })
                
                if attribute_lines:  # Only include products that have attributes
                    product_attributes[str(product_id)] = {
                        'product_id': product_id,
                        'product_name': product['name'],
                        'template_id': template_id,
                        'attribute_lines': attribute_lines
                    }
        
        return {
            'attributes': processed_attributes,
            'attribute_values': processed_attribute_values,
            'product_attributes': product_attributes
        }
    
    def _enrich_products_with_attributes(self, basic_products, product_attributes):
        """Enrich basic product data with attribute information"""
        enriched_products = []
        
        for product in basic_products:
            enriched_product = product.copy()
            product_id = str(product['id'])
            
            # Add attribute data if it exists for this product
            if product_id in product_attributes:
                attr_data = product_attributes[product_id]
                enriched_product['attribute_lines'] = attr_data['attribute_lines']
                
                # Add convenience fields for frontend
                enriched_product['has_attributes'] = True
                enriched_product['has_toppings'] = any(
                    attr_line['display_type'] == 'check_box' or 
                    'topping' in attr_line['attribute_name'].lower()
                    for attr_line in attr_data['attribute_lines']
                )
                
                # Calculate min/max price including extras
                base_price = enriched_product['list_price']
                max_extra = 0
                for attr_line in attr_data['attribute_lines']:
                    if attr_line['display_type'] == 'check_box':
                        # For checkboxes, sum all possible extras
                        max_extra += sum(val['price_extra'] for val in attr_line['values'])
                    else:
                        # For radio/select, take the highest extra
                        max_extra += max((val['price_extra'] for val in attr_line['values']), default=0)
                
                enriched_product['price_range'] = {
                    'min': base_price,
                    'max': base_price + max_extra
                }
            else:
                enriched_product['attribute_lines'] = []
                enriched_product['has_attributes'] = False
                enriched_product['has_toppings'] = False
                enriched_product['price_range'] = {
                    'min': enriched_product['list_price'],
                    'max': enriched_product['list_price']
                }
            
            # Keep template_id for reference (rename for cleaner API)
            if 'product_tmpl_id' in enriched_product:
                template_data = enriched_product['product_tmpl_id']
                enriched_product['template_id'] = template_data[0] if isinstance(template_data, list) else template_data
                del enriched_product['product_tmpl_id']  # Remove the tuple, keep clean ID
                
            enriched_products.append(enriched_product)
        
        return enriched_products
    
    def _enrich_products_with_frontend_fields(self, products):
        """Enrich products with frontend-required fields"""
        enriched_products = []
        
        # Category-based preparation time mapping
        category_prep_times = {
            'combo': 20,
            'bánh mì': 10,
            'đồ uống': 5,
            'mì trộn': 15,
            'salad': 8,
            'xôi': 12,
            'default': 15
        }
        
        # Category-based tags mapping
        category_tags = {
            'combo': ['combo', 'meal'],
            'bánh mì': ['sandwich', 'traditional'],
            'đồ uống': ['drink', 'beverage'],
            'mì trộn': ['noodles', 'mixed'],
            'salad': ['healthy', 'fresh'],
            'xôi': ['rice', 'traditional'],
            'default': []
        }
        
        for product in products:
            enriched_product = product.copy()
            
            # Get category name for categorization
            category_name = ''
            if product.get('pos_categ_id') and len(product['pos_categ_id']) > 1:
                category_name = product['pos_categ_id'][1].lower()
            
            # Add critical fields
            enriched_product['is_available'] = product.get('available_in_pos', True)
            
            # Add important fields
            prep_time = category_prep_times.get(category_name, category_prep_times['default'])
            enriched_product['preparation_time'] = prep_time
            
            # Generate tags based on category and product name
            tags = category_tags.get(category_name, category_tags['default']).copy()
            product_name_lower = product['name'].lower()
            if 'combo' in product_name_lower or 'cmb' in product_name_lower:
                tags.append('combo')
            if any(word in product_name_lower for word in ['thập cẩm', 'đặc biệt', 'premium']):
                tags.append('popular')
            if any(word in product_name_lower for word in ['double', 'lớn', 'size']):
                tags.append('large')
            
            enriched_product['tags'] = list(set(tags))  # Remove duplicates
            
            # Pricing fields - using list_price as both current and original price
            # Note: standard_price is cost price, not original selling price
            list_price = product['list_price']
            
            # For now, no discount calculation since we don't have original price data
            # In the future, could fetch from price history or promotion fields
            enriched_product['original_price'] = list_price
            enriched_product['discount_percentage'] = 0
            
            # Add nice-to-have fields with defaults
            enriched_product['allergens'] = []
            enriched_product['nutritional_info'] = None
            
            # Remove internal fields not needed by frontend
            fields_to_remove = ['available_in_pos', 'categ_id']
            for field in fields_to_remove:
                if field in enriched_product:
                    del enriched_product[field]
            
            enriched_products.append(enriched_product)
        
        return enriched_products
    
    def _enrich_categories_with_frontend_fields(self, categories, products):
        """Enrich categories with frontend-required fields"""
        enriched_categories = []
        
        # Category icon mapping
        category_icons = {
            'combo': '🍽️',
            'bánh mì': '🥪',
            'đồ uống': '🥤',
            'mì trộn': '🍜',
            'salad': '🥗',
            'xôi': '🍚',
            'topping': '🧄',
            'vật phẩm': '🍴',
            'default': '🍽️'
        }
        
        # Category description mapping
        category_descriptions = {
            'combo': 'Value meal combinations with drinks and sides',
            'bánh mì': 'Traditional Vietnamese sandwiches with fresh ingredients',
            'đồ uống': 'Refreshing beverages including coffee, tea, and soft drinks',
            'mì trộn': 'Mixed noodle dishes with various toppings',
            'salad': 'Fresh and healthy salad options',
            'xôi': 'Traditional Vietnamese sticky rice dishes',
            'topping': 'Extra toppings and add-ons for your meals',
            'vật phẩm': 'Utensils and additional items',
            'default': 'Delicious food items'
        }
        
        # Count products per category
        product_counts = {}
        for product in products:
            if product.get('pos_categ_id') and len(product['pos_categ_id']) > 0:
                category_id = product['pos_categ_id'][0]
                product_counts[category_id] = product_counts.get(category_id, 0) + 1
        
        for category in categories:
            enriched_category = category.copy()
            
            # Get category name for mapping
            category_name = category['name'].lower()
            category_key = None
            for key in category_icons.keys():
                if key in category_name:
                    category_key = key
                    break
            if not category_key:
                category_key = 'default'
            
            # Add important fields
            enriched_category['description'] = category.get('description') or category_descriptions.get(category_key, category_descriptions['default'])
            enriched_category['is_active'] = True  # All fetched categories are active
            enriched_category['product_count'] = product_counts.get(category['id'], 0)
            enriched_category['icon'] = category_icons.get(category_key, category_icons['default'])
            
            enriched_categories.append(enriched_category)
        
        return enriched_categories