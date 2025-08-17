from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Dict, Optional
from app.services.odoo_cache_service import OdooCacheService
from app.config import get_settings


router = APIRouter(prefix="/api/v1", tags=["menu"])


def get_cache_service() -> OdooCacheService:
    """Dependency to get cache service instance"""
    settings = get_settings()
    
    # Use API key if provided, otherwise fall back to username/password
    if settings.ODOO_API_KEY:
        return OdooCacheService(
            odoo_url=settings.ODOO_URL,
            db=settings.ODOO_DB,
            username=settings.ODOO_USERNAME,
            api_key=settings.ODOO_API_KEY
        )
    else:
        return OdooCacheService(
            odoo_url=settings.ODOO_URL,
            db=settings.ODOO_DB,
            username=settings.ODOO_USERNAME,
            password=settings.ODOO_PASSWORD
        )


@router.get("/categories", response_model=Dict[str, List[Dict]])
async def get_categories(cache_service: OdooCacheService = Depends(get_cache_service)):
    """Get all POS categories from cache"""
    try:
        categories = cache_service.get_categories()
        if not categories:
            raise HTTPException(
                status_code=503, 
                detail="Cache is empty. Please reload cache first using POST /api/v1/cache/reload"
            )
        return {"categories": categories}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving categories: {str(e)}")


@router.get("/products", response_model=Dict[str, List[Dict]])
async def get_products(
    category_id: Optional[int] = Query(None, description="Filter products by category ID"),
    cache_service: OdooCacheService = Depends(get_cache_service)
):
    """Get all POS products from cache, optionally filtered by category"""
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
        
        return {"products": products}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving products: {str(e)}")


@router.get("/products/{product_id}", response_model=Dict)
async def get_product(
    product_id: int,
    cache_service: OdooCacheService = Depends(get_cache_service)
):
    """Get a specific product by ID"""
    try:
        products = cache_service.get_products()
        product = next((p for p in products if p['id'] == product_id), None)
        
        if not product:
            raise HTTPException(status_code=404, detail=f"Product with ID {product_id} not found")
        
        return {"product": product}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving product: {str(e)}")


@router.post("/cache/reload", response_model=Dict)
async def reload_cache(cache_service: OdooCacheService = Depends(get_cache_service)):
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
async def get_cache_status(cache_service: OdooCacheService = Depends(get_cache_service)):
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
async def test_odoo_connection(cache_service: OdooCacheService = Depends(get_cache_service)):
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
async def clear_cache(cache_service: OdooCacheService = Depends(get_cache_service)):
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
async def get_menu_summary(cache_service: OdooCacheService = Depends(get_cache_service)):
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
async def get_attributes(cache_service: OdooCacheService = Depends(get_cache_service)):
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
async def get_attribute_values(cache_service: OdooCacheService = Depends(get_cache_service)):
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
    cache_service: OdooCacheService = Depends(get_cache_service)
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
    cache_service: OdooCacheService = Depends(get_cache_service)
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