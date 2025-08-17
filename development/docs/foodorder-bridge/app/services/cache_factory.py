import os
from typing import Union
from app.services.odoo_cache_service import OdooCacheService
from app.services.firestore_cache_service import FirestoreCacheService


class HybridCacheService:
    """Hybrid cache service that uses Firestore on Cloud Run and file cache locally"""
    
    def __init__(self, odoo_url: str, db: str, username: str = None, password: str = None, api_key: str = None):
        """Initialize hybrid cache service"""
        self.odoo_url = odoo_url
        self.db = db
        self.username = username
        self.password = password
        self.api_key = api_key
        
        # Detect if running on Cloud Run
        self.is_cloud_run = self._is_running_on_cloud_run()
        
        # Initialize appropriate cache service
        self.odoo_service = OdooCacheService(
            odoo_url=odoo_url,
            db=db,
            username=username,
            password=password,
            api_key=api_key
        )
        
        # Always try to initialize Firestore service (for both local and Cloud Run)
        try:
            self.firestore_service = FirestoreCacheService()
            if self.is_cloud_run:
                print("✅ Using Firestore cache for persistence on Cloud Run")
            else:
                print("✅ Using file-based cache for local development + Firestore sync")
        except Exception as e:
            print(f"❌ Failed to initialize Firestore, using file cache only: {e}")
            self.firestore_service = None
            if self.is_cloud_run:
                print("⚠️ Running on Cloud Run without Firestore - cache won't persist!")
            else:
                print("✅ Using file-based cache for local development")
    
    def _is_running_on_cloud_run(self) -> bool:
        """Detect if running on Google Cloud Run"""
        # Cloud Run sets K_SERVICE environment variable
        return os.getenv('K_SERVICE') is not None
    
    def reload_cache(self) -> dict:
        """Reload cache from Odoo and save to appropriate backend"""
        # Always fetch from Odoo using the OdooService
        metadata = self.odoo_service.reload_cache()
        
        # Always save to Firestore if available (for both local development and Cloud Run)
        if self.firestore_service:
            try:
                categories = self.odoo_service.get_categories()
                products = self.odoo_service.get_products()
                attributes = self.odoo_service.get_attributes()
                attribute_values = self.odoo_service.get_attribute_values()
                product_attributes = self.odoo_service.get_product_attributes()
                
                # Save to Firestore
                firestore_metadata = self.firestore_service.save_cache_data(
                    categories=categories,
                    products=products,
                    attributes=attributes,
                    attribute_values=attribute_values,
                    product_attributes=product_attributes
                )
                
                print("✅ Cache saved to both file system and Firestore")
                return firestore_metadata
                
            except Exception as e:
                print(f"❌ Error saving to Firestore, using file cache: {e}")
        
        return metadata
    
    def get_categories(self) -> list:
        """Get categories from appropriate cache backend"""
        if self.is_cloud_run and self.firestore_service:
            categories = self.firestore_service.get_categories()
            if categories:
                return categories
            else:
                # Fallback to file cache if Firestore is empty
                return self.odoo_service.get_categories()
        else:
            return self.odoo_service.get_categories()
    
    def get_products(self) -> list:
        """Get products from appropriate cache backend"""
        if self.is_cloud_run and self.firestore_service:
            products = self.firestore_service.get_products()
            if products:
                return products
            else:
                # Fallback to file cache if Firestore is empty
                return self.odoo_service.get_products()
        else:
            return self.odoo_service.get_products()
    
    def get_products_by_category(self, category_id: int) -> list:
        """Get products filtered by category"""
        if self.is_cloud_run and self.firestore_service:
            return self.firestore_service.get_products_by_category(category_id)
        else:
            return self.odoo_service.get_products_by_category(category_id)
    
    def get_attributes(self) -> list:
        """Get attributes from appropriate cache backend"""
        if self.is_cloud_run and self.firestore_service:
            attributes = self.firestore_service.get_attributes()
            if attributes:
                return attributes
            else:
                return self.odoo_service.get_attributes()
        else:
            return self.odoo_service.get_attributes()
    
    def get_attribute_values(self) -> list:
        """Get attribute values from appropriate cache backend"""
        if self.is_cloud_run and self.firestore_service:
            values = self.firestore_service.get_attribute_values()
            if values:
                return values
            else:
                return self.odoo_service.get_attribute_values()
        else:
            return self.odoo_service.get_attribute_values()
    
    def get_product_attributes(self) -> dict:
        """Get product attributes from appropriate cache backend"""
        if self.is_cloud_run and self.firestore_service:
            attrs = self.firestore_service.get_product_attributes()
            if attrs:
                return attrs
            else:
                return self.odoo_service.get_product_attributes()
        else:
            return self.odoo_service.get_product_attributes()
    
    def get_product_attributes_by_id(self, product_id: int) -> dict:
        """Get attributes for specific product"""
        if self.is_cloud_run and self.firestore_service:
            return self.firestore_service.get_product_attributes_by_id(product_id)
        else:
            return self.odoo_service.get_product_attributes_by_id(product_id)
    
    def get_cache_status(self) -> dict:
        """Get cache status from appropriate backend"""
        if self.is_cloud_run and self.firestore_service:
            try:
                status = self.firestore_service.get_cache_status()
                status['cache_backend'] = 'firestore'
                status['environment'] = 'cloud_run'
                return status
            except Exception as e:
                print(f"❌ Error getting Firestore status: {e}")
                # Fallback to file cache status
                status = self.odoo_service.get_cache_status()
                status['cache_backend'] = 'file'
                status['firestore_error'] = str(e)
                return status
        else:
            status = self.odoo_service.get_cache_status()
            status['cache_backend'] = 'file'
            status['environment'] = 'local'
            return status
    
    def is_cache_empty(self) -> bool:
        """Check if cache is empty"""
        if self.is_cloud_run and self.firestore_service:
            return self.firestore_service.is_cache_empty()
        else:
            categories = self.odoo_service.get_categories()
            products = self.odoo_service.get_products()
            return len(categories) == 0 or len(products) == 0
    
    def test_connection(self) -> dict:
        """Test connection to Odoo and cache backends"""
        # Test Odoo connection
        odoo_result = self.odoo_service.test_connection()
        
        result = {
            'odoo': odoo_result,
            'cache_backend': 'file' if not self.is_cloud_run else 'firestore',
            'environment': 'local' if not self.is_cloud_run else 'cloud_run'
        }
        
        # Test Firestore if on Cloud Run
        if self.is_cloud_run and self.firestore_service:
            try:
                firestore_health = self.firestore_service.health_check()
                result['firestore'] = firestore_health
            except Exception as e:
                result['firestore'] = {'status': 'error', 'error': str(e)}
        
        return result


def get_cache_service(odoo_url: str, db: str, username: str = None, password: str = None, api_key: str = None) -> HybridCacheService:
    """Factory function to get the appropriate cache service"""
    return HybridCacheService(
        odoo_url=odoo_url,
        db=db,
        username=username,
        password=password,
        api_key=api_key
    )