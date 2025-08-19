import os
import json
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Any, Optional
from google.cloud import firestore
from google.cloud.firestore import Client


class FirestoreCacheService:
    """Firestore-based cache service for Cloud Run persistence"""
    
    def __init__(self, collection_prefix: str = "foodorder_cache"):
        """Initialize Firestore cache service"""
        self.collection_prefix = collection_prefix
        
        # Initialize Firestore client (uses Application Default Credentials on Cloud Run)
        try:
            self.db: Client = firestore.Client()
            print("✅ Connected to Firestore successfully")
        except Exception as e:
            print(f"❌ Failed to connect to Firestore: {e}")
            raise
        
        # Collection names
        self.metadata_collection = f"{collection_prefix}_metadata"
        self.categories_collection = f"{collection_prefix}_categories"
        self.products_collection = f"{collection_prefix}_products"
        
        # Cache TTL (24 hours)
        self.cache_ttl_hours = 24
    
    def save_cache_data(self, categories: List[Dict], products: List[Dict], 
                       attributes: List[Dict], attribute_values: List[Dict], 
                       product_attributes: Dict) -> Dict[str, Any]:
        """Save all cache data to Firestore"""
        try:
            timestamp = datetime.now(timezone.utc)
            
            # Prepare metadata
            metadata = {
                'last_updated': timestamp,
                'categories_count': len(categories),
                'products_count': len(products),
                'attributes_count': len(attributes),
                'attribute_values_count': len(attribute_values),
                'products_with_attributes_count': len(product_attributes),
                'cache_version': '1.0'
            }
            
            # Use batch to ensure atomicity
            batch = self.db.batch()
            
            # Save metadata
            metadata_ref = self.db.collection(self.metadata_collection).document('info')
            batch.set(metadata_ref, metadata)
            
            # Save categories
            categories_ref = self.db.collection(self.categories_collection).document('all_categories')
            batch.set(categories_ref, {'data': categories, 'updated': timestamp})
            
            # Save products
            products_ref = self.db.collection(self.products_collection).document('all_products')
            batch.set(products_ref, {'data': products, 'updated': timestamp})
            
            # Save attributes and related data
            attributes_ref = self.db.collection(f"{self.collection_prefix}_attributes").document('all_attributes')
            batch.set(attributes_ref, {
                'attributes': attributes,
                'attribute_values': attribute_values,
                'product_attributes': product_attributes,
                'updated': timestamp
            })
            
            # Commit batch
            batch.commit()
            
            print(f"✅ Cache saved to Firestore: {len(categories)} categories, {len(products)} products")
            return metadata
            
        except Exception as e:
            print(f"❌ Error saving cache to Firestore: {e}")
            raise
    
    def get_categories(self) -> List[Dict]:
        """Load categories from Firestore"""
        try:
            doc_ref = self.db.collection(self.categories_collection).document('all_categories')
            doc = doc_ref.get()
            
            if doc.exists:
                data = doc.to_dict()
                if self._is_cache_valid(data.get('updated')):
                    return data.get('data', [])
                else:
                    print("📅 Categories cache expired")
                    return []
            else:
                print("📭 No categories found in Firestore")
                return []
                
        except Exception as e:
            print(f"❌ Error loading categories from Firestore: {e}")
            return []
    
    def get_products(self) -> List[Dict]:
        """Load products from Firestore"""
        try:
            doc_ref = self.db.collection(self.products_collection).document('all_products')
            doc = doc_ref.get()
            
            if doc.exists:
                data = doc.to_dict()
                if self._is_cache_valid(data.get('updated')):
                    return data.get('data', [])
                else:
                    print("📅 Products cache expired")
                    return []
            else:
                print("📭 No products found in Firestore")
                return []
                
        except Exception as e:
            print(f"❌ Error loading products from Firestore: {e}")
            return []
    
    def get_products_by_category(self, category_id: int) -> List[Dict]:
        """Get products filtered by category"""
        products = self.get_products()
        return [
            prod for prod in products 
            if prod.get('pos_categ_id') and prod['pos_categ_id'][0] == category_id
        ]
    
    def get_attributes(self) -> List[Dict]:
        """Load attributes from Firestore"""
        try:
            doc_ref = self.db.collection(f"{self.collection_prefix}_attributes").document('all_attributes')
            doc = doc_ref.get()
            
            if doc.exists:
                data = doc.to_dict()
                if self._is_cache_valid(data.get('updated')):
                    return data.get('attributes', [])
                else:
                    print("📅 Attributes cache expired")
                    return []
            else:
                return []
                
        except Exception as e:
            print(f"❌ Error loading attributes from Firestore: {e}")
            return []
    
    def get_attribute_values(self) -> List[Dict]:
        """Load attribute values from Firestore"""
        try:
            doc_ref = self.db.collection(f"{self.collection_prefix}_attributes").document('all_attributes')
            doc = doc_ref.get()
            
            if doc.exists:
                data = doc.to_dict()
                if self._is_cache_valid(data.get('updated')):
                    return data.get('attribute_values', [])
                else:
                    return []
            else:
                return []
                
        except Exception as e:
            print(f"❌ Error loading attribute values from Firestore: {e}")
            return []
    
    def get_product_attributes(self) -> Dict:
        """Load product attributes from Firestore"""
        try:
            doc_ref = self.db.collection(f"{self.collection_prefix}_attributes").document('all_attributes')
            doc = doc_ref.get()
            
            if doc.exists:
                data = doc.to_dict()
                if self._is_cache_valid(data.get('updated')):
                    return data.get('product_attributes', {})
                else:
                    return {}
            else:
                return {}
                
        except Exception as e:
            print(f"❌ Error loading product attributes from Firestore: {e}")
            return {}
    
    def get_product_attributes_by_id(self, product_id: int) -> Dict:
        """Get attributes for a specific product"""
        product_attributes = self.get_product_attributes()
        return product_attributes.get(str(product_id), {})
    
    def get_cache_status(self) -> Dict:
        """Get cache metadata from Firestore"""
        try:
            doc_ref = self.db.collection(self.metadata_collection).document('info')
            doc = doc_ref.get()
            
            if doc.exists:
                metadata = doc.to_dict()
                # Convert timestamp to string for JSON serialization
                if 'last_updated' in metadata and metadata['last_updated']:
                    metadata['last_updated'] = metadata['last_updated'].isoformat()
                return metadata
            else:
                return {
                    'last_updated': None,
                    'categories_count': 0,
                    'products_count': 0,
                    'cache_source': 'firestore',
                    'cache_status': 'empty'
                }
                
        except Exception as e:
            print(f"❌ Error getting cache status from Firestore: {e}")
            return {
                'error': str(e),
                'cache_source': 'firestore',
                'cache_status': 'error'
            }
    
    def is_cache_empty(self) -> bool:
        """Check if cache is empty or expired"""
        try:
            # Check if categories exist and are valid
            categories = self.get_categories()
            products = self.get_products()
            return len(categories) == 0 or len(products) == 0
        except:
            return True
    
    def clear_cache(self) -> bool:
        """Clear all cache data from Firestore"""
        try:
            # Use batch to delete all documents
            batch = self.db.batch()
            
            # Delete metadata
            metadata_ref = self.db.collection(self.metadata_collection).document('info')
            batch.delete(metadata_ref)
            
            # Delete categories
            categories_ref = self.db.collection(self.categories_collection).document('all_categories')
            batch.delete(categories_ref)
            
            # Delete products
            products_ref = self.db.collection(self.products_collection).document('all_products')
            batch.delete(products_ref)
            
            # Delete attributes
            attributes_ref = self.db.collection(f"{self.collection_prefix}_attributes").document('all_attributes')
            batch.delete(attributes_ref)
            
            # Commit batch
            batch.commit()
            
            print("✅ Cache cleared from Firestore")
            return True
            
        except Exception as e:
            print(f"❌ Error clearing cache from Firestore: {e}")
            return False
    
    def _is_cache_valid(self, updated_timestamp) -> bool:
        """Check if cache is still valid based on TTL"""
        if not updated_timestamp:
            return False
        
        # Handle both datetime objects and strings
        if isinstance(updated_timestamp, str):
            try:
                updated_timestamp = datetime.fromisoformat(updated_timestamp.replace('Z', '+00:00'))
            except:
                return False
        
        # Check if cache is within TTL
        # Make sure both datetimes are timezone-aware for comparison
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=self.cache_ttl_hours)
        
        # If updated_timestamp is naive, make it UTC
        if updated_timestamp.tzinfo is None:
            updated_timestamp = updated_timestamp.replace(tzinfo=timezone.utc)
            
        return updated_timestamp > cutoff_time
    
    def health_check(self) -> Dict[str, Any]:
        """Check Firestore connection health"""
        try:
            # Try to read metadata collection
            doc_ref = self.db.collection(self.metadata_collection).document('info')
            doc_ref.get()
            
            return {
                'firestore_status': 'healthy',
                'collection_prefix': self.collection_prefix,
                'cache_ttl_hours': self.cache_ttl_hours
            }
        except Exception as e:
            return {
                'firestore_status': 'unhealthy',
                'error': str(e)
            }