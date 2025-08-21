"""
Translation API Controller for Language-First Firestore Structure
================================================================

New endpoints optimized for the restructured Firestore collection:
- product_translations_v2/{language}/products/{product_id}

This allows:
1. Bulk fetch all products in a language with single query
2. Efficient language switching
3. Reduced API calls for frontend
"""

from fastapi import APIRouter, HTTPException, Query, Path
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
import logging
from datetime import datetime

# Firebase imports
try:
    from google.cloud import firestore
    from google.cloud.firestore import Client
except ImportError:
    firestore = None

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/translations-v2", tags=["translations-v2"])


class LanguageQuery(BaseModel):
    """Validation for language query parameter"""
    lang: str = Field(..., pattern="^(vi|en|fr|it|cn|ja)$")


class ProductResponse(BaseModel):
    """Product translation response model"""
    product_id: int
    name: str
    short_description: str
    long_description: str
    price: float
    category: str
    category_id: int
    language: str


class LanguageMetadata(BaseModel):
    """Language metadata response"""
    supported_languages: Dict[str, Dict[str, Any]]
    default_language: str
    structure_version: str


class FirestoreTranslationService:
    """Service for the new language-first Firestore structure"""
    
    def __init__(self, project_id: str = "finiziapp"):
        if not firestore:
            raise ImportError("google-cloud-firestore is not installed")
            
        self.db = firestore.Client(project=project_id)
        self.collection_name = "product_translations_v2"
    
    def get_all_products_in_language(self, language: str) -> List[Dict[str, Any]]:
        """Get ALL products for a specific language in one query"""
        try:
            products_ref = (self.db.collection(self.collection_name)
                           .document(language)
                           .collection('products'))
            
            docs = products_ref.stream()
            products = []
            
            for doc in docs:
                data = doc.to_dict()
                if data:
                    products.append(data)
            
            return products
            
        except Exception as e:
            logger.error(f"Error getting all products for {language}: {e}")
            return []
    
    def get_product_in_language(self, language: str, product_id: str) -> Optional[Dict[str, Any]]:
        """Get specific product in a specific language"""
        try:
            doc_ref = (self.db.collection(self.collection_name)
                      .document(language)
                      .collection('products')
                      .document(product_id))
            
            doc = doc_ref.get()
            if doc.exists:
                return doc.to_dict()
            return None
            
        except Exception as e:
            logger.error(f"Error getting product {product_id} in {language}: {e}")
            return None
    
    def get_language_metadata(self) -> Optional[Dict[str, Any]]:
        """Get language metadata and supported languages"""
        try:
            doc_ref = self.db.collection(self.collection_name).document('_metadata')
            doc = doc_ref.get()
            
            if doc.exists:
                return doc.to_dict()
            return None
            
        except Exception as e:
            logger.error(f"Error getting language metadata: {e}")
            return None
    
    def get_available_languages(self) -> List[str]:
        """Get list of available languages"""
        try:
            collection_ref = self.db.collection(self.collection_name)
            docs = collection_ref.stream()
            
            languages = []
            for doc in docs:
                if doc.id != '_metadata':
                    languages.append(doc.id)
            
            return sorted(languages)
            
        except Exception as e:
            logger.error(f"Error getting available languages: {e}")
            return []


# Initialize service
try:
    translation_service = FirestoreTranslationService()
except Exception as e:
    logger.error(f"Failed to initialize translation service: {e}")
    translation_service = None


@router.get("/languages", response_model=Dict[str, Any])
async def get_supported_languages():
    """Get all supported languages with metadata"""
    if not translation_service:
        raise HTTPException(status_code=503, detail="Translation service not available")
    
    try:
        metadata = translation_service.get_language_metadata()
        available_languages = translation_service.get_available_languages()
        
        if not metadata:
            # Fallback metadata
            metadata = {
                'supported_languages': {
                    'vi': {'name': 'Tiếng Việt', 'code': 'vi', 'is_default': True},
                    'en': {'name': 'English', 'code': 'en', 'is_default': False},
                    'fr': {'name': 'Français', 'code': 'fr', 'is_default': False},
                    'it': {'name': 'Italiano', 'code': 'it', 'is_default': False},
                    'cn': {'name': '中文', 'code': 'cn', 'is_default': False},
                    'ja': {'name': '日本語', 'code': 'ja', 'is_default': False}
                },
                'default_language': 'vi'
            }
        
        return {
            'status': 'success',
            'available_languages': available_languages,
            'metadata': metadata,
            'total_languages': len(available_languages)
        }
        
    except Exception as e:
        logger.error(f"Error getting supported languages: {e}")
        raise HTTPException(status_code=500, detail="Failed to get supported languages")


@router.get("/products", response_model=Dict[str, Any])
async def get_all_products_by_language(
    language: str = Query(..., pattern="^(vi|en|fr|it|cn|ja)$", 
                         description="Language code to retrieve products in (vi, en, fr, it, cn, ja)")
):
    """Get ALL products for a specific language - optimized for bulk fetching"""
    if not translation_service:
        raise HTTPException(status_code=503, detail="Translation service not available")
    
    try:
        products = translation_service.get_all_products_in_language(language)
        
        if not products:
            # Check if language exists
            available_languages = translation_service.get_available_languages()
            if language not in available_languages:
                raise HTTPException(
                    status_code=404, 
                    detail=f"Language '{language}' not found. Available: {available_languages}"
                )
        
        return {
            'status': 'success',
            'language': language,
            'products_count': len(products),
            'products': products,
            'usage_note': 'This endpoint returns ALL products in the specified language for efficient bulk loading'
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting products for language {language}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get products for {language}")


@router.get("/products/{product_id}", response_model=Dict[str, Any])
async def get_product_translation(
    product_id: int = Path(..., ge=1, le=999999, description="Product ID"),
    language: str = Query(..., pattern="^(vi|en|fr|it|cn|ja)$",
                         description="Language code to retrieve product in (vi, en, fr, it, cn, ja)")
):
    """Get a specific product in a specific language"""
    if not translation_service:
        raise HTTPException(status_code=503, detail="Translation service not available")
    
    try:
        product = translation_service.get_product_in_language(language, str(product_id))
        
        if not product:
            raise HTTPException(
                status_code=404,
                detail=f"Product {product_id} not found in {language}"
            )
        
        return {
            'status': 'success',
            'product_id': product_id,
            'language': language,
            'product': product
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting product {product_id} in {language}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get product translation")


@router.get("/products/{product_id}/all-languages", response_model=Dict[str, Any])
async def get_product_all_languages(
    product_id: int = Path(..., ge=1, le=999999, description="Product ID")
):
    """Get a specific product in ALL available languages"""
    if not translation_service:
        raise HTTPException(status_code=503, detail="Translation service not available")
    
    try:
        available_languages = translation_service.get_available_languages()
        all_translations = {}
        
        for language in available_languages:
            product = translation_service.get_product_in_language(language, str(product_id))
            if product:
                all_translations[language] = product
        
        if not all_translations:
            raise HTTPException(
                status_code=404,
                detail=f"Product {product_id} not found in any language"
            )
        
        return {
            'status': 'success',
            'product_id': product_id,
            'available_languages': list(all_translations.keys()),
            'translations': all_translations
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting all translations for product {product_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get product translations")


@router.get("/categories", response_model=Dict[str, Any])
async def get_category_list_by_language(
    language: str = Query(..., pattern="^(vi|en|fr|it|cn|ja)$",
                         description="Language code to retrieve categories in (vi, en, fr, it, cn, ja)")
):
    """Get unique category list for a specific language"""
    if not translation_service:
        raise HTTPException(status_code=503, detail="Translation service not available")
    
    try:
        products = translation_service.get_all_products_in_language(language)
        
        # Extract unique categories
        categories = {}
        for product in products:
            category_id = product.get('category_id')
            category_name = product.get('category', '')
            
            if category_id and category_name:
                if category_id not in categories:
                    categories[category_id] = {
                        'category_id': category_id,
                        'category_name': category_name,
                        'product_count': 0
                    }
                categories[category_id]['product_count'] += 1
        
        category_list = list(categories.values())
        category_list.sort(key=lambda x: x['category_id'])
        
        return {
            'status': 'success',
            'language': language,
            'categories_count': len(category_list),
            'categories': category_list
        }
        
    except Exception as e:
        logger.error(f"Error getting categories for {language}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get categories for {language}")


@router.get("/categories/{category_id}/products", response_model=Dict[str, Any])
async def get_products_by_category_and_language(
    category_id: int = Path(..., ge=1, le=999999, description="Category ID"),
    language: str = Query(..., pattern="^(vi|en|fr|it|cn|ja)$",
                         description="Language code to retrieve products in (vi, en, fr, it, cn, ja)")
):
    """Get all products in a specific category and language"""
    if not translation_service:
        raise HTTPException(status_code=503, detail="Translation service not available")
    
    try:
        all_products = translation_service.get_all_products_in_language(language)
        
        # Filter by category
        category_products = [
            product for product in all_products 
            if product.get('category_id') == category_id
        ]
        
        if not category_products:
            raise HTTPException(
                status_code=404,
                detail=f"No products found for category {category_id} in {language}"
            )
        
        return {
            'status': 'success',
            'category_id': category_id,
            'language': language,
            'products_count': len(category_products),
            'products': category_products
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting products for category {category_id} in {language}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get category products")


@router.get("/status", response_model=Dict[str, Any])
async def get_translation_service_status():
    """Get translation service status and statistics"""
    if not translation_service:
        raise HTTPException(status_code=503, detail="Translation service not available")
    
    try:
        available_languages = translation_service.get_available_languages()
        metadata = translation_service.get_language_metadata()
        
        # Get product counts per language
        language_stats = {}
        for language in available_languages:
            products = translation_service.get_all_products_in_language(language)
            language_stats[language] = len(products)
        
        return {
            'status': 'operational',
            'collection_name': 'product_translations_v2',
            'structure_version': '2.0 - Language First',
            'available_languages': available_languages,
            'language_statistics': language_stats,
            'total_languages': len(available_languages),
            'metadata': metadata,
            'endpoints': {
                'bulk_language_products': '/api/v1/translations-v2/products?language={2-letter-code}',
                'specific_product': '/api/v1/translations-v2/products/{product_id}?language={2-letter-code}',
                'category_products': '/api/v1/translations-v2/categories/{category_id}/products?language={2-letter-code}',
                'all_product_languages': '/api/v1/translations-v2/products/{product_id}/all-languages'
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting translation service status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get service status")