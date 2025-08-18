from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Dict, Optional
from app.services.cache_factory import get_cache_service as get_hybrid_cache_service, HybridCacheService
from app.config import get_settings


router = APIRouter(prefix="/api/v1", tags=["menu"])


def get_cache_service() -> HybridCacheService:
    """Dependency to get hybrid cache service instance"""
    settings = get_settings()
    
    # Use API key if provided, otherwise fall back to username/password
    if settings.ODOO_API_KEY:
        return get_hybrid_cache_service(
            odoo_url=settings.ODOO_URL,
            db=settings.ODOO_DB,
            username=settings.ODOO_USERNAME,
            api_key=settings.ODOO_API_KEY
        )
    else:
        return get_hybrid_cache_service(
            odoo_url=settings.ODOO_URL,
            db=settings.ODOO_DB,
            username=settings.ODOO_USERNAME,
            password=settings.ODOO_PASSWORD
        )


@router.get("/categories", response_model=Dict[str, List[Dict]])
async def get_categories(
    lang: Optional[str] = Query(None, description="Language code for translations (vi, en, zh, zh-TW, th)"),
    cache_service: HybridCacheService = Depends(get_cache_service)
):
    """Get all POS categories from cache with optional translation"""
    try:
        categories = cache_service.get_categories()
        if not categories:
            raise HTTPException(
                status_code=503, 
                detail="Cache is empty. Please reload cache first using POST /api/v1/cache/reload"
            )
        
        # Apply language translation if requested
        if lang and lang != 'vi':
            settings = get_settings()
            if lang in settings.SUPPORTED_LANGUAGES:
                categories = _apply_category_translations(categories, lang)
            
        return {"categories": categories}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving categories: {str(e)}")


@router.get("/products", response_model=Dict[str, List[Dict]])
async def get_products(
    category_id: Optional[int] = Query(None, description="Filter products by category ID"),
    lang: Optional[str] = Query(None, description="Language code for translations (vi, en, zh, zh-TW, th)"),
    cache_service: HybridCacheService = Depends(get_cache_service)
):
    """Get all POS products from cache, optionally filtered by category with optional translation"""
    try:
        if category_id:
            products = cache_service.get_products_by_category(category_id)
        else:
            products = cache_service.get_products()
        
        if not products and category_id is None:
            raise HTTPException(
                status_code=503, 
                detail="Cache is empty. Please reload cache first using POST /api/v1/cache/reload"
            )
        
        # Apply language translation if requested
        if lang and lang != 'vi':
            settings = get_settings()
            if lang in settings.SUPPORTED_LANGUAGES:
                products = _apply_product_translations(products, lang)
        
        return {"products": products}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving products: {str(e)}")


@router.get("/products/{product_id}", response_model=Dict)
async def get_product(
    product_id: int,
    lang: Optional[str] = Query(None, description="Language code for translations (vi, en, zh, zh-TW, th)"),
    cache_service: HybridCacheService = Depends(get_cache_service)
):
    """Get a specific product by ID with optional translation"""
    try:
        products = cache_service.get_products()
        product = next((p for p in products if p['id'] == product_id), None)
        
        if not product:
            raise HTTPException(status_code=404, detail=f"Product with ID {product_id} not found")
        
        # Apply language translation if requested
        if lang and lang != 'vi':
            settings = get_settings()
            if lang in settings.SUPPORTED_LANGUAGES:
                product = _apply_product_translations([product], lang)[0]
        
        return {"product": product}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving product: {str(e)}")


@router.post("/cache/reload", response_model=Dict)
async def reload_cache(cache_service: HybridCacheService = Depends(get_cache_service)):
    """Manually reload cache from Odoo"""
    try:
        print("Starting cache reload...")
        metadata = cache_service.reload_cache()
        return {
            "status": "success",
            "message": "Cache reloaded successfully",
            "metadata": metadata
        }
    except ValueError as e:
        raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to reload cache: {str(e)}")


@router.get("/cache/status", response_model=Dict)
async def get_cache_status(cache_service: HybridCacheService = Depends(get_cache_service)):
    """Get cache status and metadata"""
    try:
        status = cache_service.get_cache_status()
        return {
            "status": "success",
            "cache": status
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving cache status: {str(e)}")


@router.get("/cache/test-connection", response_model=Dict)
async def test_odoo_connection(cache_service: HybridCacheService = Depends(get_cache_service)):
    """Test connection to Odoo server without modifying cache"""
    try:
        result = cache_service.test_connection()
        if result['status'] == 'error':
            raise HTTPException(status_code=500, detail=result['error'])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error testing connection: {str(e)}")


@router.delete("/cache/clear")
async def clear_cache(cache_service: HybridCacheService = Depends(get_cache_service)):
    """Clear all cache files (for development/testing)"""
    try:
        # Remove JSON cache files
        import os
        cache_files = ['categories.json', 'products.json', 'attributes.json', 'attribute_values.json', 'product_attributes.json', 'metadata.json']
        removed_files = []
        
        for filename in cache_files:
            filepath = cache_service.cache_dir / filename
            if filepath.exists():
                os.remove(filepath)
                removed_files.append(filename)
        
        return {
            "status": "success",
            "message": f"Cache cleared successfully",
            "removed_files": removed_files
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing cache: {str(e)}")


@router.get("/menu/summary", response_model=Dict)
async def get_menu_summary(cache_service: HybridCacheService = Depends(get_cache_service)):
    """Get a summary of categories with product counts"""
    try:
        categories = cache_service.get_categories()
        products = cache_service.get_products()
        
        if not categories:
            raise HTTPException(
                status_code=503, 
                detail="Cache is empty. Please reload cache first."
            )
        
        # Count products per category
        category_counts = {}
        for product in products:
            if product.get('pos_categ_id'):
                cat_id = product['pos_categ_id'][0]
                category_counts[cat_id] = category_counts.get(cat_id, 0) + 1
        
        # Add product counts to categories
        categories_with_counts = []
        for category in categories:
            cat_with_count = category.copy()
            cat_with_count['product_count'] = category_counts.get(category['id'], 0)
            categories_with_counts.append(cat_with_count)
        
        return {
            "status": "success",
            "categories": categories_with_counts,
            "total_categories": len(categories),
            "total_products": len(products)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving menu summary: {str(e)}")


@router.get("/attributes", response_model=Dict[str, List[Dict]])
async def get_attributes(cache_service: HybridCacheService = Depends(get_cache_service)):
    """Get all product attributes from cache"""
    try:
        attributes = cache_service.get_attributes()
        if not attributes:
            raise HTTPException(
                status_code=503,
                detail="Attributes cache is empty. Please reload cache first using POST /api/v1/cache/reload"
            )
        return {"attributes": attributes}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving attributes: {str(e)}")


@router.get("/attribute-values", response_model=Dict[str, List[Dict]])
async def get_attribute_values(cache_service: HybridCacheService = Depends(get_cache_service)):
    """Get all attribute values from cache"""
    try:
        attribute_values = cache_service.get_attribute_values()
        if not attribute_values:
            raise HTTPException(
                status_code=503,
                detail="Attribute values cache is empty. Please reload cache first using POST /api/v1/cache/reload"
            )
        return {"attribute_values": attribute_values}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving attribute values: {str(e)}")


@router.get("/products/{product_id}/attributes", response_model=Dict)
async def get_product_attributes(
    product_id: int,
    cache_service: HybridCacheService = Depends(get_cache_service)
):
    """Get attributes for a specific product (toppings, options, etc.)"""
    try:
        product_attrs = cache_service.get_product_attributes_by_id(product_id)
        
        if not product_attrs:
            # Check if product exists first
            products = cache_service.get_products()
            product_exists = any(p['id'] == product_id for p in products)
            
            if not product_exists:
                raise HTTPException(status_code=404, detail=f"Product with ID {product_id} not found")
            else:
                # Product exists but has no attributes
                return {
                    "product_id": product_id,
                    "attribute_lines": [],
                    "message": "This product has no configurable attributes"
                }
        
        return product_attrs
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving product attributes: {str(e)}")


@router.get("/products/{product_id}/toppings", response_model=Dict)
async def get_product_toppings(
    product_id: int,
    cache_service: HybridCacheService = Depends(get_cache_service)
):
    """Get topping options for a specific product (convenience endpoint)"""
    try:
        product_attrs = cache_service.get_product_attributes_by_id(product_id)
        
        if not product_attrs:
            # Check if product exists first
            products = cache_service.get_products()
            product_exists = any(p['id'] == product_id for p in products)
            
            if not product_exists:
                raise HTTPException(status_code=404, detail=f"Product with ID {product_id} not found")
            else:
                return {
                    "product_id": product_id,
                    "toppings": [],
                    "message": "This product has no toppings available"
                }
        
        # Filter for topping-like attributes
        toppings = []
        for attr_line in product_attrs.get('attribute_lines', []):
            # Look for attributes that are likely toppings (checkboxes or contain "topping" in name)
            if (attr_line['display_type'] == 'check_box' or 
                'topping' in attr_line['attribute_name'].lower() or
                attr_line['create_variant'] == 'no_variant'):
                
                toppings.append({
                    'attribute_id': attr_line['attribute_id'],
                    'name': attr_line['attribute_name'],
                    'display_type': attr_line['display_type'],
                    'options': attr_line['values']
                })
        
        return {
            "product_id": product_id,
            "product_name": product_attrs.get('product_name', ''),
            "toppings": toppings
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving product toppings: {str(e)}")


@router.get("/categories/{category_id}/image", response_model=Dict)
async def get_category_image(
    category_id: int,
    size: str = Query("image_256", description="Image size: image_128, image_256, image_512, image_1024"),
    cache_service: HybridCacheService = Depends(get_cache_service)
):
    """Get direct Odoo image URL for a category"""
    try:
        categories = cache_service.get_categories()
        category = next((c for c in categories if c['id'] == category_id), None)
        
        if not category:
            raise HTTPException(status_code=404, detail=f"Category with ID {category_id} not found")
        
        # Generate direct Odoo image URL
        from app.config import get_settings
        settings = get_settings()
        image_url = f"{settings.ODOO_URL}/web/image/pos.category/{category_id}/{size}"
        
        return {
            "category_id": category_id,
            "category_name": category.get('name', ''),
            "image_url": image_url,
            "size": size
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving category image: {str(e)}")


@router.get("/products/{product_id}/image", response_model=Dict)
async def get_product_image(
    product_id: int,
    size: str = Query("image_512", description="Image size: image_128, image_256, image_512, image_1024"),
    cache_service: HybridCacheService = Depends(get_cache_service)
):
    """Get direct Odoo image URL for a product"""
    try:
        products = cache_service.get_products()
        product = next((p for p in products if p['id'] == product_id), None)
        
        if not product:
            raise HTTPException(status_code=404, detail=f"Product with ID {product_id} not found")
        
        # Generate direct Odoo image URL
        from app.config import get_settings
        settings = get_settings()
        image_url = f"{settings.ODOO_URL}/web/image/product.product/{product_id}/{size}"
        
        return {
            "product_id": product_id,
            "product_name": product.get('name', ''),
            "image_url": image_url,
            "size": size
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving product image: {str(e)}")


@router.get("/images/test", response_model=Dict)
async def test_image_urls(cache_service: HybridCacheService = Depends(get_cache_service)):
    """Test endpoint to get sample image URLs for categories and products"""
    try:
        categories = cache_service.get_categories()
        products = cache_service.get_products()
        
        from app.config import get_settings
        settings = get_settings()
        
        sample_data = {
            "odoo_base_url": settings.ODOO_URL,
            "categories": [],
            "products": []
        }
        
        # Get first 3 categories with images
        for category in categories[:3]:
            if category.get('has_image') and category.get('image_urls'):
                sample_data["categories"].append({
                    "id": category['id'],
                    "name": category['name'],
                    "image_urls": category['image_urls']
                })
        
        # Get first 3 products with images  
        products_with_images = [p for p in products if p.get('has_image') and p.get('image_urls')]
        for product in products_with_images[:3]:
            sample_data["products"].append({
                "id": product['id'],
                "name": product['name'],
                "image_urls": product['image_urls']
            })
        
        return sample_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating test image URLs: {str(e)}")


# Translation Management Endpoints
@router.get("/translations/languages", response_model=Dict)
async def get_supported_languages():
    """Get list of supported languages for translation"""
    try:
        settings = get_settings()
        return {
            "supported_languages": {
                "vi": "Vietnamese (Default)",
                "en": "English",
                "zh": "Chinese (Simplified)",
                "zh-TW": "Chinese (Traditional)",
                "th": "Thai"
            },
            "default_language": settings.DEFAULT_LANGUAGE,
            "translation_enabled": settings.ENABLE_TRANSLATION
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving languages: {str(e)}")


@router.get("/translations/status", response_model=Dict)
async def get_translation_status(cache_service: HybridCacheService = Depends(get_cache_service)):
    """Get translation service status and cache statistics"""
    try:
        status = cache_service.get_translation_status()
        return {
            "status": "success",
            "translation_service": status
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving translation status: {str(e)}")


@router.post("/translations/refresh", response_model=Dict)
async def refresh_translations(cache_service: HybridCacheService = Depends(get_cache_service)):
    """Refresh translation cache by clearing old translations and reloading cache"""
    try:
        # Clear old translation cache
        cache_service.clear_translation_cache(older_than_days=7)
        
        # Reload cache with fresh translations
        metadata = cache_service.reload_cache()
        
        return {
            "status": "success",
            "message": "Translation cache refreshed successfully",
            "metadata": metadata
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error refreshing translations: {str(e)}")


# Helper functions for applying translations
def _apply_product_translations(products: List[Dict], target_language: str) -> List[Dict]:
    """Apply translations to product list"""
    translated_products = []
    
    for product in products:
        translated_product = product.copy()
        
        # Apply name translation if available
        if 'name_translations' in product and target_language in product['name_translations']:
            translated_product['name'] = product['name_translations'][target_language]
        
        # Apply description translation if available
        if 'description_translations' in product and target_language in product['description_translations']:
            translated_product['description_sale'] = product['description_translations'][target_language]
        
        translated_products.append(translated_product)
    
    return translated_products


def _apply_category_translations(categories: List[Dict], target_language: str) -> List[Dict]:
    """Apply translations to category list"""
    translated_categories = []
    
    for category in categories:
        translated_category = category.copy()
        
        # Apply name translation if available
        if 'name_translations' in category and target_language in category['name_translations']:
            translated_category['name'] = category['name_translations'][target_language]
        
        # Apply description translation if available  
        if 'description_translations' in category and target_language in category['description_translations']:
            translated_category['description'] = category['description_translations'][target_language]
        
        translated_categories.append(translated_category)
    
    return translated_categories