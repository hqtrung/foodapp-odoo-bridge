# Translation API Reference

**Base URL:** `/api/v1/translations-v2`

## Authentication
No authentication required for read operations.

## Language Codes
- `vi` - Vietnamese (Default)
- `en` - English  
- `fr` - French
- `it` - Italian
- `cn` - Chinese
- `ja` - Japanese

---

## Endpoints

### 1. Get All Products by Language
Get all products for a specific language in one request.

**Endpoint:** `GET /products`

**Parameters:**
- `language` (required): 2-letter language code

**Example:**
```http
GET /api/v1/translations-v2/products?language=en
```

**Response:**
```json
{
  "status": "success",
  "language": "en",
  "products_count": 53,
  "products": [
    {
      "product_id": 1186,
      "name": "Plain Baguette",
      "short_description": "Traditional Vietnamese Baguette",
      "long_description": "Fresh and delicious Vietnamese baguette...",
      "price": 25000,
      "category": "Traditional Banh Mi",
      "category_id": 5,
      "attributes": [
        {
          "attribute_id": 1,
          "attribute_name": "Baguette Topping",
          "display_type": "check_box",
          "create_variant": "no_variant",
          "values": [
            {
              "id": 30,
              "name": "Add Pate",
              "price_extra": 5000,
              "base_value_id": 19,
              "base_value_name": "Add Pate"
            },
            {
              "id": 31,
              "name": "Add Cha Siu BBQ Pork", 
              "price_extra": 10000
            }
          ]
        }
      ],
      "language_code": "en",
      "language_name": "English"
    }
  ]
}
```

---

### 2. Get Specific Product
Get a single product in a specific language.

**Endpoint:** `GET /products/{product_id}`

**Parameters:**
- `product_id` (path): Product ID (1-999999)
- `language` (query): 2-letter language code

**Example:**
```http
GET /api/v1/translations-v2/products/1186?language=fr
```

**Response:**
```json
{
  "status": "success",
  "product_id": 1186,
  "language": "fr",
  "product": {
    "product_id": 1186,
    "name": "Baguette Nature",
    "short_description": "Baguette vietnamienne traditionnelle",
    "long_description": "Baguette vietnamienne fraîche et délicieuse...",
    "price": 25000,
    "category": "Banh Mi Traditionnel",
    "category_id": 5,
    "language_code": "fr",
    "language_name": "Français"
  }
}
```

---

### 3. Get Product in All Languages
Get the same product across all available languages.

**Endpoint:** `GET /products/{product_id}/all-languages`

**Parameters:**
- `product_id` (path): Product ID

**Example:**
```http
GET /api/v1/translations-v2/products/1186/all-languages
```

**Response:**
```json
{
  "status": "success",
  "product_id": 1186,
  "available_languages": ["vi", "en", "fr", "it", "cn", "ja"],
  "translations": {
    "vi": {
      "name": "Bánh Mì Không",
      "language_name": "Tiếng Việt"
    },
    "en": {
      "name": "Plain Baguette", 
      "language_name": "English"
    },
    "fr": {
      "name": "Baguette Nature",
      "language_name": "Français"
    }
  }
}
```

---

### 4. Get Categories by Language
Get category list for a specific language.

**Endpoint:** `GET /categories`

**Parameters:**
- `language` (required): 2-letter language code

**Example:**
```http
GET /api/v1/translations-v2/categories?language=it
```

**Response:**
```json
{
  "status": "success",
  "language": "it",
  "categories_count": 8,
  "categories": [
    {
      "category_id": 5,
      "category_name": "Banh Mi Tradizionale",
      "product_count": 12
    },
    {
      "category_id": 15,
      "category_name": "Noodles Misti e Riso Appiccicoso",
      "product_count": 8
    }
  ]
}
```

---

### 5. Get Products by Category and Language
Get products filtered by category in a specific language.

**Endpoint:** `GET /categories/{category_id}/products`

**Parameters:**
- `category_id` (path): Category ID (1-999999)
- `language` (query): 2-letter language code

**Example:**
```http
GET /api/v1/translations-v2/categories/5/products?language=cn
```

**Response:**
```json
{
  "status": "success",
  "category_id": 5,
  "language": "cn",
  "products_count": 12,
  "products": [
    {
      "product_id": 1186,
      "name": "原味法棍",
      "category": "传统越式法棍",
      "language_code": "cn",
      "language_name": "中文"
    }
  ]
}
```

---

### 6. Get Supported Languages
Get metadata about available languages.

**Endpoint:** `GET /languages`

**Example:**
```http
GET /api/v1/translations-v2/languages
```

**Response:**
```json
{
  "status": "success",
  "available_languages": ["vi", "en", "fr", "it", "cn", "ja"],
  "metadata": {
    "supported_languages": {
      "vi": {"name": "Tiếng Việt", "code": "vi", "is_default": true},
      "en": {"name": "English", "code": "en", "is_default": false},
      "fr": {"name": "Français", "code": "fr", "is_default": false},
      "it": {"name": "Italiano", "code": "it", "is_default": false},
      "cn": {"name": "中文", "code": "cn", "is_default": false},
      "ja": {"name": "日本語", "code": "ja", "is_default": false}
    },
    "default_language": "vi",
    "structure_version": "2.1"
  },
  "total_languages": 6
}
```

---

### 7. Get System Status
Get translation service status and statistics.

**Endpoint:** `GET /status`

**Example:**
```http
GET /api/v1/translations-v2/status
```

**Response:**
```json
{
  "status": "operational",
  "collection_name": "product_translations_v2",
  "structure_version": "2.0 - Language First",
  "available_languages": ["vi", "en", "fr", "it", "cn", "ja"],
  "language_statistics": {
    "vi": 53,
    "en": 53,
    "fr": 53,
    "it": 53,
    "cn": 53,
    "ja": 53
  },
  "total_languages": 6,
  "endpoints": {
    "bulk_language_products": "/api/v1/translations-v2/products?language={2-letter-code}",
    "specific_product": "/api/v1/translations-v2/products/{product_id}?language={2-letter-code}",
    "category_products": "/api/v1/translations-v2/categories/{category_id}/products?language={2-letter-code}",
    "all_product_languages": "/api/v1/translations-v2/products/{product_id}/all-languages"
  }
}
```

---

## Error Responses

### 400 Bad Request
Invalid parameters or malformed request.
```json
{
  "detail": "Language parameter is required"
}
```

### 404 Not Found
Resource not found.
```json
{
  "detail": "Product 99999 not found in fr"
}
```

### 422 Unprocessable Entity
Invalid language code.
```json
{
  "detail": "Language 'english' not found. Available: ['vi', 'en', 'fr', 'it', 'cn', 'ja']"
}
```

### 503 Service Unavailable
Translation service not available.
```json
{
  "detail": "Translation service not available"
}
```

---

## Rate Limits
- **100 requests per minute** per IP address
- **1000 requests per hour** per IP address

## Response Headers
All responses include:
```
Content-Type: application/json
X-API-Version: 2.1
X-Language-Codes: vi,en,fr,it,cn,ja
```

## Caching
- API responses are cached for **5 minutes**
- Use `Cache-Control: no-cache` header to bypass cache
- ETags are supported for conditional requests

## Performance Notes
- **Bulk fetch** (`/products?language=en`) is ~33x faster than individual calls
- **Response time**: ~100ms for bulk operations, ~50ms for individual products
- **Payload size**: ~50KB for full menu in one language

---

## SDKs and Libraries

### JavaScript/TypeScript
```javascript
class TranslationAPI {
  constructor(baseURL = '/api/v1/translations-v2') {
    this.baseURL = baseURL;
  }

  async getAllProducts(language) {
    const response = await fetch(`${this.baseURL}/products?language=${language}`);
    return response.json();
  }

  async getProduct(productId, language) {
    const response = await fetch(`${this.baseURL}/products/${productId}?language=${language}`);
    return response.json();
  }
}

// Usage
const api = new TranslationAPI();
const englishMenu = await api.getAllProducts('en');
```

### Python
```python
import requests

class TranslationAPI:
    def __init__(self, base_url='/api/v1/translations-v2'):
        self.base_url = base_url
    
    def get_all_products(self, language):
        response = requests.get(f'{self.base_url}/products', params={'language': language})
        return response.json()
    
    def get_product(self, product_id, language):
        response = requests.get(f'{self.base_url}/products/{product_id}', params={'language': language})
        return response.json()

# Usage
api = TranslationAPI()
french_menu = api.get_all_products('fr')
```

---

**Last Updated:** August 21, 2025  
**API Version:** 2.1  
**Documentation Version:** 1.0