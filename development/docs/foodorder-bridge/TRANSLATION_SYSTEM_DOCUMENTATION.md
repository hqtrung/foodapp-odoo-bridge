# FoodOrder Bridge Translation System Documentation

## Table of Contents
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Language Codes](#language-codes)
4. [Firestore Structure](#firestore-structure)
5. [API Endpoints](#api-endpoints)
6. [Frontend Integration](#frontend-integration)
7. [Performance](#performance)
8. [Implementation Guide](#implementation-guide)
9. [Troubleshooting](#troubleshooting)

---

## Overview

The FoodOrder Bridge Translation System provides multi-language support for Vietnamese restaurant menu data with real-time translation capabilities. The system uses a language-first Firestore architecture with 2-letter language codes for optimal performance and standards compliance.

### Key Features
- **6 Languages Supported**: Vietnamese (vi), English (en), French (fr), Italian (it), Chinese (cn), Japanese (ja)
- **Real-time Access**: Direct Firestore integration for instant language switching
- **Bulk Operations**: Single query retrieves entire menu in chosen language
- **Standards Compliant**: ISO 639-1 two-letter language codes
- **High Performance**: ~100ms to fetch 53+ products per language

### Translation Quality
- **Cultural Accuracy**: Vietnamese terms properly localized (Bánh Mì → Baguette)
- **Food Terminology**: Authentic culinary translations (Xá Xíu → Cha Siu BBQ Pork)
- **Comprehensive Content**: Full product names, short descriptions, and detailed descriptions
- **AI-Powered**: Generated using Google Vertex AI Gemini 2.5 Flash

---

## Architecture

### System Design
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │   FastAPI        │    │   Firestore     │
│   (React/Vue)   │◄──►│   Translation    │◄──►│   Collections   │
│                 │    │   API            │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
        │                        │                        │
        │                        │                        │
        ▼                        ▼                        ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ Firebase SDK    │    │ Translation      │    │ Language-First  │
│ Direct Access   │    │ Controllers      │    │ Structure       │
│ (Recommended)   │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### Data Flow
1. **Source**: Vietnamese menu data from Odoo 18 POS
2. **Translation**: AI-powered translation via Vertex AI Gemini
3. **Storage**: Language-first Firestore collections
4. **Access**: Direct Firebase SDK or FastAPI endpoints
5. **Frontend**: Real-time language switching

---

## Language Codes

### Supported Languages
| Code | Language | Native Name | Products | Status |
|------|----------|-------------|----------|---------|
| `vi` | Vietnamese | Tiếng Việt | 53 | ✅ Default |
| `en` | English | English | 53 | ✅ Complete |
| `fr` | French | Français | 53 | ✅ Complete |
| `it` | Italian | Italiano | 53 | ✅ Complete |
| `cn` | Chinese | 中文 | 53 | ✅ Complete |
| `ja` | Japanese | 日本語 | 53 | ✅ Complete |

### Language Selection Logic
```javascript
// Default language priority
const getLanguage = () => {
  return userPreference || browserLanguage || 'vi';
};

// Supported language validation
const isSupported = (lang) => {
  return ['vi', 'en', 'fr', 'it', 'cn', 'ja'].includes(lang);
};
```

---

## Firestore Structure

### Collection Architecture
```
product_translations_v2/
├── vi/
│   └── products/
│       ├── 1181
│       ├── 1186
│       └── ...
├── en/
│   └── products/
│       ├── 1181
│       ├── 1186
│       └── ...
├── fr/
│   └── products/
│       └── ...
├── it/
│   └── products/
│       └── ...
├── cn/
│   └── products/
│       └── ...
├── ja/
│   └── products/
│       └── ...
└── _metadata
```

### Document Structure
Each product document contains:
```json
{
  "product_id": 1186,
  "name": "Plain Baguette",
  "short_description": "Traditional Vietnamese Baguette",
  "long_description": "Fresh and delicious Vietnamese baguette, with a crispy golden crust...",
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
          "base_value_name": "Add Pate",
          "product_packaging_id": 4540,
          "linked_product_id": 2552,
          "linked_product_name": "(B6) Pate Mix",
          "linked_product_price": 25000
        },
        {
          "id": 31,
          "name": "Add Cha Siu BBQ Pork",
          "price_extra": 10000,
          "base_value_id": 20,
          "base_value_name": "Add Cha Siu BBQ Pork"
        }
      ]
    }
  ],
  "language_code": "en",
  "language_name": "English",
  "is_base_language": false,
  "updated_at": "2025-08-21T10:53:01Z"
}
```

### Metadata Document
```json
{
  "supported_languages": {
    "vi": {"name": "Tiếng Việt", "code": "vi", "is_default": true},
    "en": {"name": "English", "code": "en", "is_default": false},
    "fr": {"name": "Français", "code": "fr", "is_default": false},
    "it": {"name": "Italiano", "code": "it", "is_default": false},
    "cn": {"name": "中文", "code": "cn", "is_default": false},
    "ja": {"name": "日本語", "code": "ja", "is_default": false}
  },
  "default_language": "vi",
  "structure_version": "2.1",
  "language_code_format": "2-letter"
}
```

---

## Product Attributes (Toppings & Options)

### Overview
Product attributes represent customizable options like toppings, sides, and variants. Each attribute contains multiple values (options) with pricing information.

### Attribute Structure
```json
{
  "attribute_id": 1,
  "attribute_name": "Baguette Topping",
  "display_type": "check_box",
  "create_variant": "no_variant",
  "values": [...]
}
```

### Attribute Value Structure
```json
{
  "id": 30,
  "name": "Add Pate",
  "price_extra": 5000,
  "base_value_id": 19,
  "base_value_name": "Add Pate",
  "product_packaging_id": 4540,
  "linked_product_id": 2552,
  "linked_product_name": "(B6) Pate Mix",
  "linked_product_price": 25000
}
```

### Display Types
- `check_box`: Multiple selection allowed (toppings)
- `radio`: Single selection only (variants)
- `select`: Dropdown selection

### Translation Examples

#### Vietnamese → English
```json
// Vietnamese
{
  "attribute_name": "Topping Bánh mì",
  "values": [
    {"name": "Thêm Pate", "price_extra": 5000},
    {"name": "Thêm Xá Xíu", "price_extra": 10000}
  ]
}

// English
{
  "attribute_name": "Baguette Topping",
  "values": [
    {"name": "Add Pate", "price_extra": 5000},
    {"name": "Add Cha Siu BBQ Pork", "price_extra": 10000}
  ]
}
```

#### Vietnamese → French
```json
// French
{
  "attribute_name": "Garniture Baguette",
  "values": [
    {"name": "Ajouter Pâté", "price_extra": 5000},
    {"name": "Ajouter Porc BBQ Cha Siu", "price_extra": 10000}
  ]
}
```

### Frontend Usage

#### React Component Example
```jsx
const ProductCustomizer = ({ product }) => {
  const [selectedOptions, setSelectedOptions] = useState({});

  const calculateTotal = () => {
    let total = product.price;
    Object.values(selectedOptions).forEach(option => {
      if (option) total += option.price_extra;
    });
    return total;
  };

  return (
    <div>
      <h3>{product.name}</h3>
      <p>Base Price: {product.price.toLocaleString()} VND</p>
      
      {product.attributes?.map(attribute => (
        <div key={attribute.attribute_id}>
          <h4>{attribute.attribute_name}</h4>
          
          {attribute.display_type === 'check_box' && (
            <div>
              {attribute.values.map(value => (
                <label key={value.id}>
                  <input
                    type="checkbox"
                    onChange={(e) => {
                      if (e.target.checked) {
                        setSelectedOptions(prev => ({
                          ...prev,
                          [value.id]: value
                        }));
                      } else {
                        setSelectedOptions(prev => {
                          const newOptions = {...prev};
                          delete newOptions[value.id];
                          return newOptions;
                        });
                      }
                    }}
                  />
                  {value.name}
                  {value.price_extra > 0 && ` (+${value.price_extra.toLocaleString()} VND)`}
                </label>
              ))}
            </div>
          )}
          
          {attribute.display_type === 'radio' && (
            <div>
              {attribute.values.map(value => (
                <label key={value.id}>
                  <input
                    type="radio"
                    name={`attribute_${attribute.attribute_id}`}
                    onChange={() => {
                      setSelectedOptions(prev => ({
                        ...prev,
                        [`attr_${attribute.attribute_id}`]: value
                      }));
                    }}
                  />
                  {value.name}
                  {value.price_extra > 0 && ` (+${value.price_extra.toLocaleString()} VND)`}
                </label>
              ))}
            </div>
          )}
        </div>
      ))}
      
      <div>
        <strong>Total: {calculateTotal().toLocaleString()} VND</strong>
      </div>
    </div>
  );
};
```

### Statistics
- **8 products** have customizable attributes across all languages
- **Attribute types**: Toppings, sides, size options, drink choices
- **Pricing**: Extra charges from 0 to 15,000 VND per option
- **Translation quality**: Cultural food terms properly localized

---

## API Endpoints

### Base URL
```
https://your-api-domain.com/api/v1/translations-v2
```

### Core Endpoints

#### 1. Get All Products by Language
**Bulk fetch all products in a specific language (Recommended)**
```http
GET /products?language={language_code}
```

**Example:**
```bash
curl "https://api.example.com/api/v1/translations-v2/products?language=en"
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
      "price": 25000,
      "category": "Traditional Banh Mi",
      "language_code": "en"
    }
  ]
}
```

#### 2. Get Specific Product
**Get a single product in a specific language**
```http
GET /products/{product_id}?language={language_code}
```

**Example:**
```bash
curl "https://api.example.com/api/v1/translations-v2/products/1186?language=fr"
```

#### 3. Get Product in All Languages
**Get the same product across all available languages**
```http
GET /products/{product_id}/all-languages
```

#### 4. Get Categories by Language
**Get category list for a specific language**
```http
GET /categories?language={language_code}
```

#### 5. Get Products by Category and Language
**Get products filtered by category in a specific language**
```http
GET /categories/{category_id}/products?language={language_code}
```

#### 6. Get Supported Languages
**Get metadata about available languages**
```http
GET /languages
```

#### 7. Get System Status
**Get translation service status and statistics**
```http
GET /status
```

### Error Responses
```json
{
  "detail": "Language 'xx' not found. Available: ['vi', 'en', 'fr', 'it', 'cn', 'ja']"
}
```

---

## Frontend Integration

### 1. Firebase SDK Integration (Recommended)

#### Setup
```javascript
import { initializeApp } from 'firebase/app';
import { getFirestore, collection, doc, getDocs, getDoc } from 'firebase/firestore';

const firebaseConfig = {
  // Your Firebase config
};

const app = initializeApp(firebaseConfig);
const db = getFirestore(app);
```

#### Get All Products in a Language
```javascript
const getAllProductsInLanguage = async (languageCode) => {
  try {
    const productsRef = collection(db, 'product_translations_v2', languageCode, 'products');
    const snapshot = await getDocs(productsRef);
    
    const products = [];
    snapshot.forEach((doc) => {
      products.push({ id: doc.id, ...doc.data() });
    });
    
    return products;
  } catch (error) {
    console.error('Error fetching products:', error);
    return [];
  }
};

// Usage
const englishProducts = await getAllProductsInLanguage('en');
const frenchProducts = await getAllProductsInLanguage('fr');
```

#### Get Specific Product
```javascript
const getProductInLanguage = async (productId, languageCode) => {
  try {
    const productRef = doc(db, 'product_translations_v2', languageCode, 'products', productId);
    const productSnap = await getDoc(productRef);
    
    if (productSnap.exists()) {
      return { id: productSnap.id, ...productSnap.data() };
    } else {
      return null;
    }
  } catch (error) {
    console.error('Error fetching product:', error);
    return null;
  }
};

// Usage
const product = await getProductInLanguage('1186', 'fr');
```

#### Real-time Language Switching
```javascript
const LanguageSwitcher = () => {
  const [currentLanguage, setCurrentLanguage] = useState('vi');
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(false);

  const switchLanguage = async (newLanguage) => {
    setLoading(true);
    setCurrentLanguage(newLanguage);
    
    const newProducts = await getAllProductsInLanguage(newLanguage);
    setProducts(newProducts);
    
    setLoading(false);
  };

  return (
    <div>
      <select value={currentLanguage} onChange={(e) => switchLanguage(e.target.value)}>
        <option value="vi">Tiếng Việt</option>
        <option value="en">English</option>
        <option value="fr">Français</option>
        <option value="it">Italiano</option>
        <option value="cn">中文</option>
        <option value="ja">日本語</option>
      </select>
      
      {loading ? (
        <div>Loading...</div>
      ) : (
        <ProductList products={products} />
      )}
    </div>
  );
};
```

### 2. REST API Integration

#### React Hook Example
```javascript
import { useState, useEffect } from 'react';

const useTranslations = (language = 'vi') => {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchProducts = async () => {
      try {
        setLoading(true);
        const response = await fetch(
          `https://api.example.com/api/v1/translations-v2/products?language=${language}`
        );
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        setProducts(data.products || []);
        setError(null);
      } catch (err) {
        setError(err.message);
        setProducts([]);
      } finally {
        setLoading(false);
      }
    };

    fetchProducts();
  }, [language]);

  return { products, loading, error };
};

// Usage in component
const MenuComponent = () => {
  const [selectedLanguage, setSelectedLanguage] = useState('en');
  const { products, loading, error } = useTranslations(selectedLanguage);

  if (loading) return <div>Loading menu...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div>
      <LanguageSelector 
        value={selectedLanguage} 
        onChange={setSelectedLanguage} 
      />
      <ProductGrid products={products} />
    </div>
  );
};
```

### 3. Vue.js Integration
```javascript
// Vue 3 Composition API
import { ref, watch, onMounted } from 'vue';
import { db } from '@/firebase/config';
import { collection, getDocs } from 'firebase/firestore';

export default {
  setup() {
    const currentLanguage = ref('vi');
    const products = ref([]);
    const loading = ref(false);

    const fetchProducts = async (language) => {
      loading.value = true;
      try {
        const productsRef = collection(db, 'product_translations_v2', language, 'products');
        const snapshot = await getDocs(productsRef);
        
        products.value = snapshot.docs.map(doc => ({
          id: doc.id,
          ...doc.data()
        }));
      } catch (error) {
        console.error('Error fetching products:', error);
      } finally {
        loading.value = false;
      }
    };

    // Watch for language changes
    watch(currentLanguage, (newLanguage) => {
      fetchProducts(newLanguage);
    });

    // Initial load
    onMounted(() => {
      fetchProducts(currentLanguage.value);
    });

    return {
      currentLanguage,
      products,
      loading,
      fetchProducts
    };
  }
};
```

---

## Performance

### Benchmarks
| Operation | Time | Details |
|-----------|------|---------|
| Bulk fetch 53 products | ~100ms | Single language, all products |
| Individual product fetch | ~50ms | Specific product in specific language |
| Language switching | ~150ms | Complete menu reload |
| Category filtering | ~10ms | Client-side filtering of bulk data |

### Performance Comparison
```
Bulk Fetch vs Individual Calls (53 products):
┌─────────────────┬──────────┬─────────────┐
│ Method          │ Time     │ API Calls   │
├─────────────────┼──────────┼─────────────┤
│ Bulk fetch      │ 0.123s   │ 1 call      │
│ Individual calls│ 4.159s   │ 53 calls    │
│ Speedup         │ 33.8x    │ 53x fewer   │
└─────────────────┴──────────┴─────────────┘
```

### Optimization Strategies

#### 1. Bulk Loading (Recommended)
```javascript
// ✅ Efficient: Single query for entire menu
const menu = await getAllProductsInLanguage('en');

// ❌ Inefficient: Multiple queries
const products = await Promise.all(
  productIds.map(id => getProductInLanguage(id, 'en'))
);
```

#### 2. Caching Strategy
```javascript
const MenuCache = {
  cache: new Map(),
  
  async getProducts(language) {
    if (this.cache.has(language)) {
      return this.cache.get(language);
    }
    
    const products = await getAllProductsInLanguage(language);
    this.cache.set(language, products);
    return products;
  },
  
  clearCache() {
    this.cache.clear();
  }
};
```

#### 3. Preloading
```javascript
// Preload common languages on app start
const preloadLanguages = async () => {
  const commonLangs = ['vi', 'en', 'fr'];
  
  await Promise.all(
    commonLangs.map(lang => MenuCache.getProducts(lang))
  );
};
```

---

## Implementation Guide

### 1. Quick Start

#### Step 1: Choose Integration Method
- **Firebase SDK**: For real-time apps, better performance
- **REST API**: For traditional web apps, easier debugging

#### Step 2: Basic Implementation
```javascript
// Firebase SDK approach
import { getFirestore, collection, getDocs } from 'firebase/firestore';

const fetchMenu = async (language = 'vi') => {
  const db = getFirestore();
  const productsRef = collection(db, 'product_translations_v2', language, 'products');
  const snapshot = await getDocs(productsRef);
  
  return snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
};
```

#### Step 3: Add Language Switching
```javascript
const [currentLang, setCurrentLang] = useState('vi');
const [menu, setMenu] = useState([]);

const changeLanguage = async (newLang) => {
  setCurrentLang(newLang);
  const newMenu = await fetchMenu(newLang);
  setMenu(newMenu);
};
```

### 2. Advanced Integration

#### Error Handling
```javascript
const fetchMenuWithRetry = async (language, retries = 3) => {
  for (let i = 0; i < retries; i++) {
    try {
      return await fetchMenu(language);
    } catch (error) {
      if (i === retries - 1) throw error;
      await new Promise(resolve => setTimeout(resolve, 1000 * (i + 1)));
    }
  }
};
```

#### Offline Support
```javascript
// Cache menu data in localStorage
const CachedMenuService = {
  CACHE_KEY: 'menu_cache',
  CACHE_DURATION: 24 * 60 * 60 * 1000, // 24 hours

  async getMenu(language) {
    // Try cache first
    const cached = this.getCachedMenu(language);
    if (cached) return cached;

    // Fetch fresh data
    try {
      const menu = await fetchMenu(language);
      this.setCachedMenu(language, menu);
      return menu;
    } catch (error) {
      // Return cached data if available, even if expired
      return this.getCachedMenu(language, true) || [];
    }
  },

  getCachedMenu(language, ignoreExpiry = false) {
    const cache = JSON.parse(localStorage.getItem(this.CACHE_KEY) || '{}');
    const data = cache[language];
    
    if (!data) return null;
    if (!ignoreExpiry && Date.now() - data.timestamp > this.CACHE_DURATION) {
      return null;
    }
    
    return data.menu;
  },

  setCachedMenu(language, menu) {
    const cache = JSON.parse(localStorage.getItem(this.CACHE_KEY) || '{}');
    cache[language] = {
      menu,
      timestamp: Date.now()
    };
    localStorage.setItem(this.CACHE_KEY, JSON.stringify(cache));
  }
};
```

### 3. React Native Integration
```javascript
import AsyncStorage from '@react-native-async-storage/async-storage';

const MenuService = {
  async getMenuForLanguage(language) {
    try {
      // Try cache first
      const cachedMenu = await AsyncStorage.getItem(`menu_${language}`);
      if (cachedMenu) {
        const parsed = JSON.parse(cachedMenu);
        if (Date.now() - parsed.timestamp < 3600000) { // 1 hour
          return parsed.data;
        }
      }

      // Fetch fresh data
      const response = await fetch(
        `https://api.example.com/api/v1/translations-v2/products?language=${language}`
      );
      const result = await response.json();
      
      // Cache the result
      await AsyncStorage.setItem(`menu_${language}`, JSON.stringify({
        data: result.products,
        timestamp: Date.now()
      }));
      
      return result.products;
    } catch (error) {
      console.error('Error fetching menu:', error);
      return [];
    }
  }
};
```

---

## Troubleshooting

### Common Issues

#### 1. Firebase Permission Errors
**Error:** `Permission denied`
**Solution:** Check Firestore security rules
```javascript
// Firestore rules for public read access
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /product_translations_v2/{language}/products/{product} {
      allow read: if true; // Public read access
    }
    match /product_translations_v2/_metadata {
      allow read: if true;
    }
  }
}
```

#### 2. Language Code Validation Errors
**Error:** `Language 'english' not found`
**Solution:** Use 2-letter codes only
```javascript
// ❌ Wrong
const products = await fetchMenu('english');

// ✅ Correct
const products = await fetchMenu('en');
```

#### 3. Empty Results
**Error:** No products returned
**Debugging:**
```javascript
const debugFetch = async (language) => {
  console.log(`Fetching products for language: ${language}`);
  
  // Check if language exists
  const db = getFirestore();
  const langDoc = doc(db, 'product_translations_v2', language);
  const langSnap = await getDoc(langDoc);
  
  if (!langSnap.exists()) {
    console.error(`Language ${language} does not exist`);
    return [];
  }
  
  // Check products subcollection
  const productsRef = collection(db, 'product_translations_v2', language, 'products');
  const snapshot = await getDocs(productsRef);
  
  console.log(`Found ${snapshot.size} products`);
  return snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
};
```

#### 4. Performance Issues
**Issue:** Slow loading times
**Solutions:**
- Use bulk fetching instead of individual calls
- Implement caching strategy
- Preload common languages
- Use Firebase SDK over REST API

### Debugging Tools

#### 1. Language Availability Checker
```javascript
const checkLanguageAvailability = async () => {
  const db = getFirestore();
  const collection = 'product_translations_v2';
  
  const languages = ['vi', 'en', 'fr', 'it', 'cn', 'ja'];
  const results = {};
  
  for (const lang of languages) {
    try {
      const productsRef = collection(db, collection, lang, 'products');
      const snapshot = await getDocs(productsRef);
      results[lang] = {
        available: true,
        productCount: snapshot.size
      };
    } catch (error) {
      results[lang] = {
        available: false,
        error: error.message
      };
    }
  }
  
  console.table(results);
  return results;
};
```

#### 2. Data Structure Validator
```javascript
const validateProductStructure = (product) => {
  const requiredFields = [
    'product_id', 'name', 'language_code', 'language_name'
  ];
  
  const missing = requiredFields.filter(field => !product[field]);
  
  if (missing.length > 0) {
    console.warn(`Product ${product.product_id} missing fields:`, missing);
    return false;
  }
  
  return true;
};
```

### Error Codes and Messages

| Code | Message | Solution |
|------|---------|----------|
| `404` | Language not found | Use valid 2-letter code (vi, en, fr, it, cn, ja) |
| `404` | Product not found | Check product ID exists in that language |
| `503` | Translation service not available | Check Firestore connection |
| `403` | Permission denied | Update Firestore security rules |
| `500` | Internal server error | Check server logs for details |

---

## Migration and Maintenance

### Data Updates
```python
# Update single product across all languages
def update_product_translations(product_id, updates):
    languages = ['vi', 'en', 'fr', 'it', 'cn', 'ja']
    
    for lang in languages:
        doc_ref = db.collection('product_translations_v2').document(lang).collection('products').document(str(product_id))
        doc_ref.update(updates)
```

### Backup Strategy
```python
# Backup all translations
def backup_translations():
    backup_data = {}
    languages = ['vi', 'en', 'fr', 'it', 'cn', 'ja']
    
    for lang in languages:
        products_ref = db.collection('product_translations_v2').document(lang).collection('products')
        products = products_ref.stream()
        
        backup_data[lang] = {}
        for product in products:
            backup_data[lang][product.id] = product.to_dict()
    
    # Save to file
    with open(f'translation_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json', 'w') as f:
        json.dump(backup_data, f, indent=2, ensure_ascii=False)
```

---

## Conclusion

The FoodOrder Bridge Translation System provides a robust, scalable solution for multi-language menu support with:

- **Performance**: 33x faster than individual API calls
- **Standards**: ISO 639-1 compliant language codes
- **Flexibility**: Multiple integration options (Firebase SDK, REST API)
- **Scalability**: Language-first architecture for easy expansion
- **Quality**: AI-powered translations with cultural accuracy

For additional support or questions, please refer to the API documentation or contact the development team.

---

**Last Updated:** August 21, 2025  
**Version:** 2.1  
**Authors:** Development Team  
**Status:** Production Ready