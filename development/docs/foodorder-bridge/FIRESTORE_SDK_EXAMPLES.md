# Firestore SDK Examples for Product Translations with Attributes

## Table of Contents
1. [Setup & Configuration](#setup--configuration)
2. [JavaScript/TypeScript SDK](#javascripttypescript-sdk)
3. [React Integration](#react-integration)
4. [Vue.js Integration](#vuejs-integration)
5. [React Native](#react-native)
6. [Python SDK](#python-sdk)
7. [Swift (iOS)](#swift-ios)
8. [Flutter/Dart](#flutterdart)

---

## Setup & Configuration

### Firebase Project Setup
```javascript
// firebase-config.js
import { initializeApp } from 'firebase/app';
import { getFirestore } from 'firebase/firestore';

const firebaseConfig = {
  apiKey: "your-api-key",
  authDomain: "your-project.firebaseapp.com",
  projectId: "finiziapp",
  storageBucket: "your-project.appspot.com",
  messagingSenderId: "123456789",
  appId: "your-app-id"
};

const app = initializeApp(firebaseConfig);
export const db = getFirestore(app);
```

---

## JavaScript/TypeScript SDK

### Basic Translation Service
```typescript
// translation-service.ts
import { 
  collection, 
  doc, 
  getDocs, 
  getDoc, 
  query, 
  where, 
  orderBy,
  limit,
  DocumentData 
} from 'firebase/firestore';
import { db } from './firebase-config';

export interface AttributeValue {
  id: number;
  name: string;
  price_extra: number;
  base_value_id?: number;
  base_value_name?: string;
  product_packaging_id?: number;
  linked_product_id?: number;
  linked_product_name?: string;
  linked_product_price?: number;
}

export interface ProductAttribute {
  attribute_id: number;
  attribute_name: string;
  display_type: 'check_box' | 'radio' | 'select';
  create_variant?: string;
  values: AttributeValue[];
}

export interface Product {
  product_id: number;
  name: string;
  short_description: string;
  long_description: string;
  price: number;
  category: string;
  category_id: number;
  attributes: ProductAttribute[];
  language_code: string;
  language_name: string;
  is_base_language?: boolean;
  updated_at: any;
}

export type LanguageCode = 'vi' | 'en' | 'fr' | 'it' | 'cn' | 'ja';

export class TranslationService {
  private readonly COLLECTION_NAME = 'product_translations_v2';

  /**
   * Get all products for a specific language
   */
  async getAllProducts(languageCode: LanguageCode): Promise<Product[]> {
    try {
      const productsRef = collection(
        db, 
        this.COLLECTION_NAME, 
        languageCode, 
        'products'
      );
      
      const snapshot = await getDocs(productsRef);
      
      return snapshot.docs.map(doc => ({
        ...doc.data() as Product,
        id: doc.id
      }));
    } catch (error) {
      console.error(`Error fetching products for ${languageCode}:`, error);
      throw error;
    }
  }

  /**
   * Get a specific product by ID in a specific language
   */
  async getProduct(
    productId: string, 
    languageCode: LanguageCode
  ): Promise<Product | null> {
    try {
      const productRef = doc(
        db, 
        this.COLLECTION_NAME, 
        languageCode, 
        'products', 
        productId
      );
      
      const productSnap = await getDoc(productRef);
      
      if (productSnap.exists()) {
        return {
          ...productSnap.data() as Product,
          id: productSnap.id
        };
      }
      
      return null;
    } catch (error) {
      console.error(`Error fetching product ${productId} in ${languageCode}:`, error);
      throw error;
    }
  }

  /**
   * Get products with attributes (toppings/options) only
   */
  async getProductsWithAttributes(
    languageCode: LanguageCode
  ): Promise<Product[]> {
    try {
      const products = await this.getAllProducts(languageCode);
      
      return products.filter(product => 
        product.attributes && 
        product.attributes.length > 0
      );
    } catch (error) {
      console.error(`Error fetching products with attributes for ${languageCode}:`, error);
      throw error;
    }
  }

  /**
   * Get products by category with attributes
   */
  async getProductsByCategory(
    categoryId: number, 
    languageCode: LanguageCode
  ): Promise<Product[]> {
    try {
      const products = await this.getAllProducts(languageCode);
      
      return products.filter(product => 
        product.category_id === categoryId
      );
    } catch (error) {
      console.error(`Error fetching products for category ${categoryId}:`, error);
      throw error;
    }
  }

  /**
   * Calculate total price including selected attributes
   */
  calculateTotalPrice(
    product: Product, 
    selectedAttributes: AttributeValue[]
  ): number {
    const basePrice = product.price;
    const attributesPrice = selectedAttributes.reduce(
      (total, attr) => total + (attr.price_extra || 0), 
      0
    );
    
    return basePrice + attributesPrice;
  }

  /**
   * Get product in multiple languages for comparison
   */
  async getProductMultiLanguage(
    productId: string, 
    languages: LanguageCode[] = ['vi', 'en', 'fr']
  ): Promise<Record<LanguageCode, Product | null>> {
    try {
      const promises = languages.map(async (lang) => ({
        [lang]: await this.getProduct(productId, lang)
      }));
      
      const results = await Promise.all(promises);
      
      return results.reduce((acc, result) => ({
        ...acc,
        ...result
      }), {} as Record<LanguageCode, Product | null>);
    } catch (error) {
      console.error(`Error fetching product ${productId} in multiple languages:`, error);
      throw error;
    }
  }

  /**
   * Search products by name (client-side filtering)
   */
  async searchProducts(
    searchTerm: string, 
    languageCode: LanguageCode
  ): Promise<Product[]> {
    try {
      const products = await this.getAllProducts(languageCode);
      
      const normalizedSearch = searchTerm.toLowerCase();
      
      return products.filter(product =>
        product.name.toLowerCase().includes(normalizedSearch) ||
        product.short_description.toLowerCase().includes(normalizedSearch) ||
        product.long_description.toLowerCase().includes(normalizedSearch)
      );
    } catch (error) {
      console.error(`Error searching products for "${searchTerm}":`, error);
      throw error;
    }
  }

  /**
   * Get available languages
   */
  async getAvailableLanguages(): Promise<LanguageCode[]> {
    try {
      // This could be enhanced to dynamically check Firestore
      // For now, return the known supported languages
      return ['vi', 'en', 'fr', 'it', 'cn', 'ja'];
    } catch (error) {
      console.error('Error getting available languages:', error);
      throw error;
    }
  }
}

// Export singleton instance
export const translationService = new TranslationService();
```

### Usage Examples
```typescript
// basic-usage.ts
import { translationService, LanguageCode } from './translation-service';

async function examples() {
  // Get all English products
  const englishProducts = await translationService.getAllProducts('en');
  console.log(`Found ${englishProducts.length} English products`);

  // Get specific product with attributes
  const product = await translationService.getProduct('2477', 'en');
  if (product) {
    console.log(`Product: ${product.name}`);
    console.log(`Base price: ${product.price.toLocaleString()} VND`);
    
    if (product.attributes && product.attributes.length > 0) {
      console.log('Available options:');
      product.attributes.forEach(attr => {
        console.log(`  ${attr.attribute_name} (${attr.display_type}):`);
        attr.values.forEach(value => {
          const priceText = value.price_extra > 0 
            ? ` (+${value.price_extra.toLocaleString()} VND)` 
            : '';
          console.log(`    - ${value.name}${priceText}`);
        });
      });
    }
  }

  // Get products with customizable options
  const productsWithToppings = await translationService.getProductsWithAttributes('en');
  console.log(`Found ${productsWithToppings.length} products with toppings/options`);

  // Calculate price with selected toppings
  if (product && product.attributes.length > 0) {
    const selectedToppings = [
      product.attributes[0].values[0], // First topping
      product.attributes[0].values[1]  // Second topping
    ];
    
    const totalPrice = translationService.calculateTotalPrice(product, selectedToppings);
    console.log(`Total with toppings: ${totalPrice.toLocaleString()} VND`);
  }

  // Get same product in multiple languages
  const multiLangProduct = await translationService.getProductMultiLanguage('2477', ['vi', 'en', 'fr']);
  Object.entries(multiLangProduct).forEach(([lang, product]) => {
    if (product) {
      console.log(`${lang}: ${product.name}`);
    }
  });

  // Search products
  const searchResults = await translationService.searchProducts('baguette', 'en');
  console.log(`Found ${searchResults.length} products matching "baguette"`);
}

examples().catch(console.error);
```

---

## React Integration

### Custom Hooks
```tsx
// hooks/useTranslations.ts
import { useState, useEffect } from 'react';
import { translationService, Product, LanguageCode } from '../services/translation-service';

export function useProducts(languageCode: LanguageCode) {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchProducts() {
      try {
        setLoading(true);
        setError(null);
        
        const data = await translationService.getAllProducts(languageCode);
        setProducts(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch products');
      } finally {
        setLoading(false);
      }
    }

    fetchProducts();
  }, [languageCode]);

  return { products, loading, error };
}

export function useProduct(productId: string, languageCode: LanguageCode) {
  const [product, setProduct] = useState<Product | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchProduct() {
      try {
        setLoading(true);
        setError(null);
        
        const data = await translationService.getProduct(productId, languageCode);
        setProduct(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch product');
      } finally {
        setLoading(false);
      }
    }

    if (productId) {
      fetchProduct();
    }
  }, [productId, languageCode]);

  return { product, loading, error };
}

export function useProductsWithAttributes(languageCode: LanguageCode) {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchProducts() {
      try {
        setLoading(true);
        setError(null);
        
        const data = await translationService.getProductsWithAttributes(languageCode);
        setProducts(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch products');
      } finally {
        setLoading(false);
      }
    }

    fetchProducts();
  }, [languageCode]);

  return { products, loading, error };
}
```

### React Components
```tsx
// components/ProductList.tsx
import React, { useState } from 'react';
import { useProducts } from '../hooks/useTranslations';
import { ProductCard } from './ProductCard';
import { LanguageCode } from '../services/translation-service';

interface ProductListProps {
  languageCode: LanguageCode;
  categoryId?: number;
}

export const ProductList: React.FC<ProductListProps> = ({ 
  languageCode, 
  categoryId 
}) => {
  const { products, loading, error } = useProducts(languageCode);
  
  const filteredProducts = categoryId 
    ? products.filter(p => p.category_id === categoryId)
    : products;

  if (loading) {
    return (
      <div className="flex justify-center items-center p-8">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
        Error: {error}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {filteredProducts.map(product => (
        <ProductCard 
          key={product.product_id} 
          product={product}
          languageCode={languageCode}
        />
      ))}
    </div>
  );
};
```

```tsx
// components/ProductCard.tsx
import React, { useState } from 'react';
import { Product, AttributeValue, LanguageCode, translationService } from '../services/translation-service';

interface ProductCardProps {
  product: Product;
  languageCode: LanguageCode;
}

export const ProductCard: React.FC<ProductCardProps> = ({ 
  product, 
  languageCode 
}) => {
  const [selectedAttributes, setSelectedAttributes] = useState<AttributeValue[]>([]);
  const [isExpanded, setIsExpanded] = useState(false);

  const totalPrice = translationService.calculateTotalPrice(product, selectedAttributes);

  const handleAttributeChange = (attribute: AttributeValue, isSelected: boolean) => {
    if (isSelected) {
      setSelectedAttributes(prev => [...prev, attribute]);
    } else {
      setSelectedAttributes(prev => 
        prev.filter(attr => attr.id !== attribute.id)
      );
    }
  };

  const handleRadioChange = (attributeId: number, value: AttributeValue) => {
    setSelectedAttributes(prev => [
      ...prev.filter(attr => 
        !product.attributes.find(prodAttr => 
          prodAttr.attribute_id === attributeId && 
          prodAttr.values.some(val => val.id === attr.id)
        )
      ),
      value
    ]);
  };

  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow">
      {/* Product Header */}
      <div className="p-4">
        <h3 className="text-lg font-semibold text-gray-900 mb-2">
          {product.name}
        </h3>
        <p className="text-gray-600 text-sm mb-3">
          {product.short_description}
        </p>
        <div className="flex justify-between items-center mb-3">
          <span className="text-xl font-bold text-green-600">
            {product.price.toLocaleString()} VND
          </span>
          <span className="text-sm text-gray-500">
            {product.category}
          </span>
        </div>
      </div>

      {/* Attributes/Toppings Section */}
      {product.attributes && product.attributes.length > 0 && (
        <div className="border-t border-gray-200">
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="w-full px-4 py-3 text-left text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none"
          >
            <div className="flex justify-between items-center">
              <span>Customize ({product.attributes.length} options)</span>
              <svg
                className={`w-5 h-5 transition-transform ${
                  isExpanded ? 'transform rotate-180' : ''
                }`}
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path
                  fillRule="evenodd"
                  d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z"
                  clipRule="evenodd"
                />
              </svg>
            </div>
          </button>

          {isExpanded && (
            <div className="px-4 pb-4">
              {product.attributes.map(attribute => (
                <div key={attribute.attribute_id} className="mb-4">
                  <h4 className="text-sm font-medium text-gray-900 mb-2">
                    {attribute.attribute_name}
                  </h4>
                  
                  {/* Checkbox attributes (multiple selection) */}
                  {attribute.display_type === 'check_box' && (
                    <div className="space-y-2">
                      {attribute.values.map(value => (
                        <label key={value.id} className="flex items-center">
                          <input
                            type="checkbox"
                            className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                            onChange={(e) => handleAttributeChange(value, e.target.checked)}
                          />
                          <span className="ml-2 text-sm text-gray-700">
                            {value.name}
                            {value.price_extra > 0 && (
                              <span className="text-green-600 font-medium">
                                {' '}(+{value.price_extra.toLocaleString()} VND)
                              </span>
                            )}
                          </span>
                        </label>
                      ))}
                    </div>
                  )}

                  {/* Radio attributes (single selection) */}
                  {attribute.display_type === 'radio' && (
                    <div className="space-y-2">
                      {attribute.values.map(value => (
                        <label key={value.id} className="flex items-center">
                          <input
                            type="radio"
                            name={`attribute_${attribute.attribute_id}`}
                            className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                            onChange={() => handleRadioChange(attribute.attribute_id, value)}
                          />
                          <span className="ml-2 text-sm text-gray-700">
                            {value.name}
                            {value.price_extra > 0 && (
                              <span className="text-green-600 font-medium">
                                {' '}(+{value.price_extra.toLocaleString()} VND)
                              </span>
                            )}
                          </span>
                        </label>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Footer with total price */}
      <div className="bg-gray-50 px-4 py-3">
        <div className="flex justify-between items-center">
          <span className="text-sm font-medium text-gray-900">
            Total: {totalPrice.toLocaleString()} VND
          </span>
          <button className="bg-blue-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2">
            Add to Cart
          </button>
        </div>
        
        {selectedAttributes.length > 0 && (
          <div className="mt-2 text-xs text-gray-600">
            Selected: {selectedAttributes.map(attr => attr.name).join(', ')}
          </div>
        )}
      </div>
    </div>
  );
};
```

```tsx
// components/LanguageSwitcher.tsx
import React from 'react';
import { LanguageCode } from '../services/translation-service';

interface LanguageSwitcherProps {
  currentLanguage: LanguageCode;
  onLanguageChange: (language: LanguageCode) => void;
}

const languages: Record<LanguageCode, string> = {
  vi: '🇻🇳 Tiếng Việt',
  en: '🇺🇸 English',
  fr: '🇫🇷 Français',
  it: '🇮🇹 Italiano',
  cn: '🇨🇳 中文',
  ja: '🇯🇵 日本語'
};

export const LanguageSwitcher: React.FC<LanguageSwitcherProps> = ({
  currentLanguage,
  onLanguageChange
}) => {
  return (
    <div className="relative">
      <select
        value={currentLanguage}
        onChange={(e) => onLanguageChange(e.target.value as LanguageCode)}
        className="appearance-none bg-white border border-gray-300 rounded-md py-2 pl-3 pr-8 text-sm leading-5 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
      >
        {Object.entries(languages).map(([code, name]) => (
          <option key={code} value={code}>
            {name}
          </option>
        ))}
      </select>
      <div className="absolute inset-y-0 right-0 flex items-center px-2 pointer-events-none">
        <svg className="w-4 h-4 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
          <path
            fillRule="evenodd"
            d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z"
            clipRule="evenodd"
          />
        </svg>
      </div>
    </div>
  );
};
```

```tsx
// App.tsx - Main Application
import React, { useState } from 'react';
import { ProductList } from './components/ProductList';
import { LanguageSwitcher } from './components/LanguageSwitcher';
import { LanguageCode } from './services/translation-service';

export const App: React.FC = () => {
  const [currentLanguage, setCurrentLanguage] = useState<LanguageCode>('vi');
  const [selectedCategory, setSelectedCategory] = useState<number | undefined>();

  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <h1 className="text-2xl font-bold text-gray-900">
              Vietnamese Restaurant Menu
            </h1>
            <LanguageSwitcher
              currentLanguage={currentLanguage}
              onLanguageChange={setCurrentLanguage}
            />
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <ProductList
          languageCode={currentLanguage}
          categoryId={selectedCategory}
        />
      </main>
    </div>
  );
};
```

---

## Vue.js Integration

### Vue 3 Composition API
```typescript
// composables/useTranslations.ts
import { ref, computed, watch } from 'vue';
import { translationService, Product, LanguageCode } from '../services/translation-service';

export function useProducts(languageCode: Ref<LanguageCode>) {
  const products = ref<Product[]>([]);
  const loading = ref(false);
  const error = ref<string | null>(null);

  const fetchProducts = async () => {
    try {
      loading.value = true;
      error.value = null;
      
      const data = await translationService.getAllProducts(languageCode.value);
      products.value = data;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch products';
    } finally {
      loading.value = false;
    }
  };

  // Watch for language changes
  watch(languageCode, fetchProducts, { immediate: true });

  return {
    products: readonly(products),
    loading: readonly(loading),
    error: readonly(error),
    refetch: fetchProducts
  };
}

export function useProduct(productId: Ref<string>, languageCode: Ref<LanguageCode>) {
  const product = ref<Product | null>(null);
  const loading = ref(false);
  const error = ref<string | null>(null);

  const fetchProduct = async () => {
    if (!productId.value) return;
    
    try {
      loading.value = true;
      error.value = null;
      
      const data = await translationService.getProduct(productId.value, languageCode.value);
      product.value = data;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch product';
    } finally {
      loading.value = false;
    }
  };

  // Watch for changes
  watch([productId, languageCode], fetchProduct, { immediate: true });

  return {
    product: readonly(product),
    loading: readonly(loading),
    error: readonly(error),
    refetch: fetchProduct
  };
}
```

```vue
<!-- components/ProductCard.vue -->
<template>
  <div class="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow">
    <!-- Product Header -->
    <div class="p-4">
      <h3 class="text-lg font-semibold text-gray-900 mb-2">
        {{ product.name }}
      </h3>
      <p class="text-gray-600 text-sm mb-3">
        {{ product.short_description }}
      </p>
      <div class="flex justify-between items-center mb-3">
        <span class="text-xl font-bold text-green-600">
          {{ formatPrice(product.price) }} VND
        </span>
        <span class="text-sm text-gray-500">
          {{ product.category }}
        </span>
      </div>
    </div>

    <!-- Attributes Section -->
    <div v-if="hasAttributes" class="border-t border-gray-200">
      <button
        @click="toggleExpanded"
        class="w-full px-4 py-3 text-left text-sm font-medium text-gray-700 hover:bg-gray-50"
      >
        <div class="flex justify-between items-center">
          <span>Customize ({{ product.attributes.length }} options)</span>
          <ChevronDownIcon 
            :class="['w-5 h-5 transition-transform', { 'rotate-180': isExpanded }]"
          />
        </div>
      </button>

      <div v-if="isExpanded" class="px-4 pb-4">
        <div v-for="attribute in product.attributes" :key="attribute.attribute_id" class="mb-4">
          <h4 class="text-sm font-medium text-gray-900 mb-2">
            {{ attribute.attribute_name }}
          </h4>
          
          <!-- Checkbox attributes -->
          <div v-if="attribute.display_type === 'check_box'" class="space-y-2">
            <label 
              v-for="value in attribute.values" 
              :key="value.id" 
              class="flex items-center"
            >
              <input
                type="checkbox"
                :value="value.id"
                v-model="selectedAttributeIds"
                class="h-4 w-4 text-blue-600 border-gray-300 rounded"
              />
              <span class="ml-2 text-sm text-gray-700">
                {{ value.name }}
                <span v-if="value.price_extra > 0" class="text-green-600 font-medium">
                  (+{{ formatPrice(value.price_extra) }} VND)
                </span>
              </span>
            </label>
          </div>

          <!-- Radio attributes -->
          <div v-if="attribute.display_type === 'radio'" class="space-y-2">
            <label 
              v-for="value in attribute.values" 
              :key="value.id" 
              class="flex items-center"
            >
              <input
                type="radio"
                :name="`attribute_${attribute.attribute_id}`"
                :value="value.id"
                @change="selectRadioValue(attribute.attribute_id, value)"
                class="h-4 w-4 text-blue-600 border-gray-300"
              />
              <span class="ml-2 text-sm text-gray-700">
                {{ value.name }}
                <span v-if="value.price_extra > 0" class="text-green-600 font-medium">
                  (+{{ formatPrice(value.price_extra) }} VND)
                </span>
              </span>
            </label>
          </div>
        </div>
      </div>
    </div>

    <!-- Footer -->
    <div class="bg-gray-50 px-4 py-3">
      <div class="flex justify-between items-center">
        <span class="text-sm font-medium text-gray-900">
          Total: {{ formatPrice(totalPrice) }} VND
        </span>
        <button 
          @click="addToCart"
          class="bg-blue-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-blue-700"
        >
          Add to Cart
        </button>
      </div>
      
      <div v-if="selectedAttributes.length > 0" class="mt-2 text-xs text-gray-600">
        Selected: {{ selectedAttributes.map(attr => attr.name).join(', ') }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { ChevronDownIcon } from '@heroicons/vue/24/outline';
import { Product, AttributeValue, translationService } from '../services/translation-service';

interface Props {
  product: Product;
}

const props = defineProps<Props>();

const isExpanded = ref(false);
const selectedAttributeIds = ref<number[]>([]);
const selectedRadioValues = ref<Record<number, AttributeValue>>({});

const hasAttributes = computed(() => 
  props.product.attributes && props.product.attributes.length > 0
);

const selectedAttributes = computed(() => {
  const checkboxAttributes: AttributeValue[] = [];
  const radioAttributes = Object.values(selectedRadioValues.value);
  
  // Get checkbox attributes
  if (props.product.attributes) {
    props.product.attributes.forEach(attr => {
      if (attr.display_type === 'check_box') {
        attr.values.forEach(value => {
          if (selectedAttributeIds.value.includes(value.id)) {
            checkboxAttributes.push(value);
          }
        });
      }
    });
  }
  
  return [...checkboxAttributes, ...radioAttributes];
});

const totalPrice = computed(() => 
  translationService.calculateTotalPrice(props.product, selectedAttributes.value)
);

const toggleExpanded = () => {
  isExpanded.value = !isExpanded.value;
};

const selectRadioValue = (attributeId: number, value: AttributeValue) => {
  selectedRadioValues.value[attributeId] = value;
};

const formatPrice = (price: number) => price.toLocaleString();

const addToCart = () => {
  // Emit event or call store action
  console.log('Adding to cart:', {
    product: props.product,
    selectedAttributes: selectedAttributes.value,
    totalPrice: totalPrice.value
  });
};
</script>
```

---

## React Native

```typescript
// services/FirestoreService.ts (React Native)
import firestore from '@react-native-firebase/firestore';
import AsyncStorage from '@react-native-async-storage/async-storage';

export class ReactNativeTranslationService {
  private readonly COLLECTION_NAME = 'product_translations_v2';
  private readonly CACHE_PREFIX = 'products_cache_';
  private readonly CACHE_DURATION = 30 * 60 * 1000; // 30 minutes

  async getAllProducts(languageCode: LanguageCode): Promise<Product[]> {
    const cacheKey = `${this.CACHE_PREFIX}${languageCode}`;
    
    try {
      // Try cache first
      const cached = await AsyncStorage.getItem(cacheKey);
      if (cached) {
        const { data, timestamp } = JSON.parse(cached);
        if (Date.now() - timestamp < this.CACHE_DURATION) {
          return data;
        }
      }

      // Fetch from Firestore
      const snapshot = await firestore()
        .collection(this.COLLECTION_NAME)
        .doc(languageCode)
        .collection('products')
        .get();

      const products = snapshot.docs.map(doc => ({
        ...doc.data(),
        id: doc.id
      })) as Product[];

      // Cache the result
      await AsyncStorage.setItem(cacheKey, JSON.stringify({
        data: products,
        timestamp: Date.now()
      }));

      return products;
    } catch (error) {
      console.error(`Error fetching products for ${languageCode}:`, error);
      
      // Try to return cached data even if expired
      try {
        const cached = await AsyncStorage.getItem(cacheKey);
        if (cached) {
          const { data } = JSON.parse(cached);
          return data;
        }
      } catch (cacheError) {
        console.error('Cache error:', cacheError);
      }
      
      throw error;
    }
  }

  async getProduct(productId: string, languageCode: LanguageCode): Promise<Product | null> {
    try {
      const doc = await firestore()
        .collection(this.COLLECTION_NAME)
        .doc(languageCode)
        .collection('products')
        .doc(productId)
        .get();

      if (doc.exists) {
        return {
          ...doc.data(),
          id: doc.id
        } as Product;
      }

      return null;
    } catch (error) {
      console.error(`Error fetching product ${productId}:`, error);
      throw error;
    }
  }

  async clearCache(): Promise<void> {
    try {
      const keys = await AsyncStorage.getAllKeys();
      const cacheKeys = keys.filter(key => key.startsWith(this.CACHE_PREFIX));
      await AsyncStorage.multiRemove(cacheKeys);
    } catch (error) {
      console.error('Error clearing cache:', error);
    }
  }
}

export const translationService = new ReactNativeTranslationService();
```

```tsx
// components/ProductList.tsx (React Native)
import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  FlatList,
  StyleSheet,
  ActivityIndicator,
  RefreshControl
} from 'react-native';
import { translationService, Product, LanguageCode } from '../services/FirestoreService';
import { ProductCard } from './ProductCard';

interface Props {
  languageCode: LanguageCode;
  categoryId?: number;
}

export const ProductList: React.FC<Props> = ({ languageCode, categoryId }) => {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchProducts = async (isRefresh = false) => {
    try {
      if (isRefresh) {
        setRefreshing(true);
        await translationService.clearCache();
      } else {
        setLoading(true);
      }
      
      setError(null);
      
      const data = await translationService.getAllProducts(languageCode);
      const filteredData = categoryId 
        ? data.filter(p => p.category_id === categoryId)
        : data;
      
      setProducts(filteredData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch products');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchProducts();
  }, [languageCode, categoryId]);

  const onRefresh = () => fetchProducts(true);

  const renderProduct = ({ item }: { item: Product }) => (
    <ProductCard product={item} languageCode={languageCode} />
  );

  if (loading) {
    return (
      <View style={styles.centerContainer}>
        <ActivityIndicator size="large" color="#3B82F6" />
        <Text style={styles.loadingText}>Loading products...</Text>
      </View>
    );
  }

  if (error) {
    return (
      <View style={styles.centerContainer}>
        <Text style={styles.errorText}>Error: {error}</Text>
      </View>
    );
  }

  return (
    <FlatList
      data={products}
      renderItem={renderProduct}
      keyExtractor={(item) => item.product_id.toString()}
      contentContainerStyle={styles.container}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
      }
      showsVerticalScrollIndicator={false}
    />
  );
};

const styles = StyleSheet.create({
  container: {
    padding: 16,
  },
  centerContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  loadingText: {
    marginTop: 10,
    fontSize: 16,
    color: '#6B7280',
  },
  errorText: {
    fontSize: 16,
    color: '#EF4444',
    textAlign: 'center',
  },
});
```

---

## Python SDK

```python
# translation_service.py
import firebase_admin
from firebase_admin import credentials, firestore
from typing import List, Dict, Optional, Union
import asyncio
from dataclasses import dataclass
from datetime import datetime

@dataclass
class AttributeValue:
    id: int
    name: str
    price_extra: float = 0
    base_value_id: Optional[int] = None
    base_value_name: Optional[str] = None
    product_packaging_id: Optional[int] = None
    linked_product_id: Optional[int] = None
    linked_product_name: Optional[str] = None
    linked_product_price: Optional[float] = None

@dataclass
class ProductAttribute:
    attribute_id: int
    attribute_name: str
    display_type: str
    create_variant: Optional[str] = None
    values: List[AttributeValue] = None

@dataclass
class Product:
    product_id: int
    name: str
    short_description: str
    long_description: str
    price: float
    category: str
    category_id: int
    attributes: List[ProductAttribute]
    language_code: str
    language_name: str
    is_base_language: bool = False
    updated_at: Optional[datetime] = None

class FirestoreTranslationService:
    def __init__(self, credentials_path: str = None):
        if not firebase_admin._apps:
            if credentials_path:
                cred = credentials.Certificate(credentials_path)
                firebase_admin.initialize_app(cred)
            else:
                # Use default credentials (for Cloud Run, etc.)
                firebase_admin.initialize_app()
        
        self.db = firestore.client()
        self.collection_name = 'product_translations_v2'
    
    def get_all_products(self, language_code: str) -> List[Product]:
        """Get all products for a specific language"""
        try:
            products_ref = (
                self.db.collection(self.collection_name)
                .document(language_code)
                .collection('products')
            )
            
            docs = products_ref.stream()
            products = []
            
            for doc in docs:
                data = doc.to_dict()
                products.append(self._dict_to_product(data))
            
            return products
        except Exception as e:
            print(f"Error fetching products for {language_code}: {e}")
            raise
    
    def get_product(self, product_id: str, language_code: str) -> Optional[Product]:
        """Get a specific product by ID in a specific language"""
        try:
            doc_ref = (
                self.db.collection(self.collection_name)
                .document(language_code)
                .collection('products')
                .document(product_id)
            )
            
            doc = doc_ref.get()
            
            if doc.exists:
                return self._dict_to_product(doc.to_dict())
            
            return None
        except Exception as e:
            print(f"Error fetching product {product_id} in {language_code}: {e}")
            raise
    
    def get_products_with_attributes(self, language_code: str) -> List[Product]:
        """Get products that have attributes (toppings/options)"""
        products = self.get_all_products(language_code)
        return [p for p in products if p.attributes and len(p.attributes) > 0]
    
    def get_products_by_category(self, category_id: int, language_code: str) -> List[Product]:
        """Get products filtered by category"""
        products = self.get_all_products(language_code)
        return [p for p in products if p.category_id == category_id]
    
    def calculate_total_price(self, product: Product, selected_attributes: List[AttributeValue]) -> float:
        """Calculate total price including selected attributes"""
        base_price = product.price
        attributes_price = sum(attr.price_extra for attr in selected_attributes)
        return base_price + attributes_price
    
    def search_products(self, search_term: str, language_code: str) -> List[Product]:
        """Search products by name or description (client-side filtering)"""
        products = self.get_all_products(language_code)
        search_lower = search_term.lower()
        
        return [
            p for p in products 
            if (search_lower in p.name.lower() or 
                search_lower in p.short_description.lower() or 
                search_lower in p.long_description.lower())
        ]
    
    def _dict_to_product(self, data: Dict) -> Product:
        """Convert Firestore document data to Product object"""
        attributes = []
        
        if data.get('attributes'):
            for attr_data in data['attributes']:
                values = []
                for val_data in attr_data.get('values', []):
                    values.append(AttributeValue(
                        id=val_data.get('id'),
                        name=val_data.get('name', ''),
                        price_extra=val_data.get('price_extra', 0),
                        base_value_id=val_data.get('base_value_id'),
                        base_value_name=val_data.get('base_value_name'),
                        product_packaging_id=val_data.get('product_packaging_id'),
                        linked_product_id=val_data.get('linked_product_id'),
                        linked_product_name=val_data.get('linked_product_name'),
                        linked_product_price=val_data.get('linked_product_price')
                    ))
                
                attributes.append(ProductAttribute(
                    attribute_id=attr_data.get('attribute_id'),
                    attribute_name=attr_data.get('attribute_name', ''),
                    display_type=attr_data.get('display_type', ''),
                    create_variant=attr_data.get('create_variant'),
                    values=values
                ))
        
        return Product(
            product_id=data.get('product_id'),
            name=data.get('name', ''),
            short_description=data.get('short_description', ''),
            long_description=data.get('long_description', ''),
            price=data.get('price', 0),
            category=data.get('category', ''),
            category_id=data.get('category_id', 0),
            attributes=attributes,
            language_code=data.get('language_code', ''),
            language_name=data.get('language_name', ''),
            is_base_language=data.get('is_base_language', False),
            updated_at=data.get('updated_at')
        )

# Usage example
if __name__ == "__main__":
    # Initialize service
    service = FirestoreTranslationService()
    
    # Get all English products
    english_products = service.get_all_products('en')
    print(f"Found {len(english_products)} English products")
    
    # Get products with toppings
    products_with_toppings = service.get_products_with_attributes('en')
    print(f"Found {len(products_with_toppings)} products with toppings")
    
    # Get specific product
    product = service.get_product('2477', 'en')
    if product:
        print(f"Product: {product.name}")
        print(f"Base price: {product.price:,.0f} VND")
        
        if product.attributes:
            print("Available options:")
            for attr in product.attributes:
                print(f"  {attr.attribute_name} ({attr.display_type}):")
                for value in attr.values:
                    price_text = f" (+{value.price_extra:,.0f} VND)" if value.price_extra > 0 else ""
                    print(f"    - {value.name}{price_text}")
        
        # Calculate price with toppings
        if product.attributes and product.attributes[0].values:
            selected_toppings = [product.attributes[0].values[0]]  # Select first topping
            total = service.calculate_total_price(product, selected_toppings)
            print(f"Total with {selected_toppings[0].name}: {total:,.0f} VND")
```

---

## Swift (iOS)

```swift
// TranslationService.swift
import Foundation
import FirebaseFirestore

struct AttributeValue: Codable {
    let id: Int
    let name: String
    let priceExtra: Double
    let baseValueId: Int?
    let baseValueName: String?
    let productPackagingId: Int?
    let linkedProductId: Int?
    let linkedProductName: String?
    let linkedProductPrice: Double?
    
    enum CodingKeys: String, CodingKey {
        case id, name
        case priceExtra = "price_extra"
        case baseValueId = "base_value_id"
        case baseValueName = "base_value_name"
        case productPackagingId = "product_packaging_id"
        case linkedProductId = "linked_product_id"
        case linkedProductName = "linked_product_name"
        case linkedProductPrice = "linked_product_price"
    }
}

struct ProductAttribute: Codable {
    let attributeId: Int
    let attributeName: String
    let displayType: String
    let createVariant: String?
    let values: [AttributeValue]
    
    enum CodingKeys: String, CodingKey {
        case attributeId = "attribute_id"
        case attributeName = "attribute_name"
        case displayType = "display_type"
        case createVariant = "create_variant"
        case values
    }
}

struct Product: Codable {
    let productId: Int
    let name: String
    let shortDescription: String
    let longDescription: String
    let price: Double
    let category: String
    let categoryId: Int
    let attributes: [ProductAttribute]
    let languageCode: String
    let languageName: String
    let isBaseLanguage: Bool?
    let updatedAt: Timestamp?
    
    enum CodingKeys: String, CodingKey {
        case productId = "product_id"
        case name
        case shortDescription = "short_description"
        case longDescription = "long_description"
        case price, category
        case categoryId = "category_id"
        case attributes
        case languageCode = "language_code"
        case languageName = "language_name"
        case isBaseLanguage = "is_base_language"
        case updatedAt = "updated_at"
    }
}

enum LanguageCode: String, CaseIterable {
    case vi = "vi"
    case en = "en"
    case fr = "fr"
    case it = "it"
    case cn = "cn"
    case ja = "ja"
    
    var displayName: String {
        switch self {
        case .vi: return "🇻🇳 Tiếng Việt"
        case .en: return "🇺🇸 English"
        case .fr: return "🇫🇷 Français"
        case .it: return "🇮🇹 Italiano"
        case .cn: return "🇨🇳 中文"
        case .ja: return "🇯🇵 日本語"
        }
    }
}

class TranslationService: ObservableObject {
    private let db = Firestore.firestore()
    private let collectionName = "product_translations_v2"
    
    func getAllProducts(languageCode: LanguageCode) async throws -> [Product] {
        let snapshot = try await db
            .collection(collectionName)
            .document(languageCode.rawValue)
            .collection("products")
            .getDocuments()
        
        return try snapshot.documents.compactMap { document in
            try document.data(as: Product.self)
        }
    }
    
    func getProduct(productId: String, languageCode: LanguageCode) async throws -> Product? {
        let document = try await db
            .collection(collectionName)
            .document(languageCode.rawValue)
            .collection("products")
            .document(productId)
            .getDocument()
        
        return try document.data(as: Product.self)
    }
    
    func getProductsWithAttributes(languageCode: LanguageCode) async throws -> [Product] {
        let products = try await getAllProducts(languageCode: languageCode)
        return products.filter { !$0.attributes.isEmpty }
    }
    
    func getProductsByCategory(categoryId: Int, languageCode: LanguageCode) async throws -> [Product] {
        let products = try await getAllProducts(languageCode: languageCode)
        return products.filter { $0.categoryId == categoryId }
    }
    
    func calculateTotalPrice(product: Product, selectedAttributes: [AttributeValue]) -> Double {
        let basePrice = product.price
        let attributesPrice = selectedAttributes.reduce(0) { $0 + $1.priceExtra }
        return basePrice + attributesPrice
    }
    
    func searchProducts(searchTerm: String, languageCode: LanguageCode) async throws -> [Product] {
        let products = try await getAllProducts(languageCode: languageCode)
        let lowercasedTerm = searchTerm.lowercased()
        
        return products.filter { product in
            product.name.lowercased().contains(lowercasedTerm) ||
            product.shortDescription.lowercased().contains(lowercasedTerm) ||
            product.longDescription.lowercased().contains(lowercasedTerm)
        }
    }
}

// SwiftUI Views
import SwiftUI

struct ProductListView: View {
    @StateObject private var translationService = TranslationService()
    @State private var products: [Product] = []
    @State private var isLoading = false
    @State private var errorMessage: String?
    @State private var selectedLanguage: LanguageCode = .vi
    
    var body: some View {
        NavigationView {
            VStack {
                // Language Picker
                Picker("Language", selection: $selectedLanguage) {
                    ForEach(LanguageCode.allCases, id: \.self) { language in
                        Text(language.displayName).tag(language)
                    }
                }
                .pickerStyle(MenuPickerStyle())
                .padding()
                
                // Products List
                if isLoading {
                    ProgressView("Loading products...")
                        .frame(maxWidth: .infinity, maxHeight: .infinity)
                } else if let errorMessage = errorMessage {
                    Text("Error: \(errorMessage)")
                        .foregroundColor(.red)
                        .padding()
                } else {
                    List(products, id: \.productId) { product in
                        ProductCardView(product: product)
                    }
                }
            }
            .navigationTitle("Menu")
            .task {
                await loadProducts()
            }
            .onChange(of: selectedLanguage) { _ in
                Task {
                    await loadProducts()
                }
            }
        }
    }
    
    private func loadProducts() async {
        isLoading = true
        errorMessage = nil
        
        do {
            products = try await translationService.getAllProducts(languageCode: selectedLanguage)
        } catch {
            errorMessage = error.localizedDescription
        }
        
        isLoading = false
    }
}

struct ProductCardView: View {
    let product: Product
    @State private var selectedAttributes: [AttributeValue] = []
    @State private var isExpanded = false
    
    private var totalPrice: Double {
        TranslationService().calculateTotalPrice(product: product, selectedAttributes: selectedAttributes)
    }
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            // Header
            VStack(alignment: .leading, spacing: 8) {
                Text(product.name)
                    .font(.headline)
                    .fontWeight(.semibold)
                
                Text(product.shortDescription)
                    .font(.subheadline)
                    .foregroundColor(.secondary)
                
                HStack {
                    Text("\(Int(product.price).formatted()) VND")
                        .font(.title2)
                        .fontWeight(.bold)
                        .foregroundColor(.green)
                    
                    Spacer()
                    
                    Text(product.category)
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
            }
            
            // Attributes
            if !product.attributes.isEmpty {
                DisclosureGroup(
                    "Customize (\(product.attributes.count) options)",
                    isExpanded: $isExpanded
                ) {
                    ForEach(product.attributes, id: \.attributeId) { attribute in
                        VStack(alignment: .leading, spacing: 8) {
                            Text(attribute.attributeName)
                                .font(.subheadline)
                                .fontWeight(.medium)
                            
                            ForEach(attribute.values, id: \.id) { value in
                                HStack {
                                    Button(action: {
                                        toggleSelection(value: value)
                                    }) {
                                        HStack {
                                            Image(systemName: selectedAttributes.contains(where: { $0.id == value.id }) ? 
                                                  "checkmark.square.fill" : "square")
                                                .foregroundColor(.blue)
                                            
                                            Text(value.name)
                                                .font(.caption)
                                            
                                            if value.priceExtra > 0 {
                                                Text("(+\(Int(value.priceExtra).formatted()) VND)")
                                                    .font(.caption)
                                                    .foregroundColor(.green)
                                            }
                                        }
                                    }
                                    .buttonStyle(PlainButtonStyle())
                                    
                                    Spacer()
                                }
                            }
                        }
                        .padding(.vertical, 4)
                    }
                }
                .padding(.vertical, 8)
            }
            
            // Footer
            HStack {
                Text("Total: \(Int(totalPrice).formatted()) VND")
                    .font(.subheadline)
                    .fontWeight(.medium)
                
                Spacer()
                
                Button("Add to Cart") {
                    // Handle add to cart
                    print("Adding to cart: \(product.name)")
                    print("Selected attributes: \(selectedAttributes.map(\.name))")
                    print("Total price: \(totalPrice)")
                }
                .buttonStyle(.borderedProminent)
                .controlSize(.small)
            }
            .padding(.top, 8)
            
            if !selectedAttributes.isEmpty {
                Text("Selected: \(selectedAttributes.map(\.name).joined(separator: ", "))")
                    .font(.caption2)
                    .foregroundColor(.secondary)
            }
        }
        .padding()
        .background(Color(.systemBackground))
        .cornerRadius(12)
        .shadow(radius: 2)
    }
    
    private func toggleSelection(value: AttributeValue) {
        if let index = selectedAttributes.firstIndex(where: { $0.id == value.id }) {
            selectedAttributes.remove(at: index)
        } else {
            selectedAttributes.append(value)
        }
    }
}

// App.swift
import SwiftUI
import FirebaseCore

@main
struct MenuApp: App {
    init() {
        FirebaseApp.configure()
    }
    
    var body: some Scene {
        WindowGroup {
            ProductListView()
        }
    }
}
```

---

## Flutter/Dart

```dart
// models/product.dart
class AttributeValue {
  final int id;
  final String name;
  final double priceExtra;
  final int? baseValueId;
  final String? baseValueName;
  final int? productPackagingId;
  final int? linkedProductId;
  final String? linkedProductName;
  final double? linkedProductPrice;

  AttributeValue({
    required this.id,
    required this.name,
    required this.priceExtra,
    this.baseValueId,
    this.baseValueName,
    this.productPackagingId,
    this.linkedProductId,
    this.linkedProductName,
    this.linkedProductPrice,
  });

  factory AttributeValue.fromMap(Map<String, dynamic> map) {
    return AttributeValue(
      id: map['id']?.toInt() ?? 0,
      name: map['name'] ?? '',
      priceExtra: map['price_extra']?.toDouble() ?? 0.0,
      baseValueId: map['base_value_id']?.toInt(),
      baseValueName: map['base_value_name'],
      productPackagingId: map['product_packaging_id']?.toInt(),
      linkedProductId: map['linked_product_id']?.toInt(),
      linkedProductName: map['linked_product_name'],
      linkedProductPrice: map['linked_product_price']?.toDouble(),
    );
  }
}

class ProductAttribute {
  final int attributeId;
  final String attributeName;
  final String displayType;
  final String? createVariant;
  final List<AttributeValue> values;

  ProductAttribute({
    required this.attributeId,
    required this.attributeName,
    required this.displayType,
    this.createVariant,
    required this.values,
  });

  factory ProductAttribute.fromMap(Map<String, dynamic> map) {
    return ProductAttribute(
      attributeId: map['attribute_id']?.toInt() ?? 0,
      attributeName: map['attribute_name'] ?? '',
      displayType: map['display_type'] ?? '',
      createVariant: map['create_variant'],
      values: List<AttributeValue>.from(
        map['values']?.map((x) => AttributeValue.fromMap(x)) ?? [],
      ),
    );
  }
}

class Product {
  final int productId;
  final String name;
  final String shortDescription;
  final String longDescription;
  final double price;
  final String category;
  final int categoryId;
  final List<ProductAttribute> attributes;
  final String languageCode;
  final String languageName;
  final bool? isBaseLanguage;
  final DateTime? updatedAt;

  Product({
    required this.productId,
    required this.name,
    required this.shortDescription,
    required this.longDescription,
    required this.price,
    required this.category,
    required this.categoryId,
    required this.attributes,
    required this.languageCode,
    required this.languageName,
    this.isBaseLanguage,
    this.updatedAt,
  });

  factory Product.fromMap(Map<String, dynamic> map) {
    return Product(
      productId: map['product_id']?.toInt() ?? 0,
      name: map['name'] ?? '',
      shortDescription: map['short_description'] ?? '',
      longDescription: map['long_description'] ?? '',
      price: map['price']?.toDouble() ?? 0.0,
      category: map['category'] ?? '',
      categoryId: map['category_id']?.toInt() ?? 0,
      attributes: List<ProductAttribute>.from(
        map['attributes']?.map((x) => ProductAttribute.fromMap(x)) ?? [],
      ),
      languageCode: map['language_code'] ?? '',
      languageName: map['language_name'] ?? '',
      isBaseLanguage: map['is_base_language'],
      updatedAt: map['updated_at']?.toDate(),
    );
  }
}

enum LanguageCode {
  vi,
  en,
  fr,
  it,
  cn,
  ja;

  String get code {
    switch (this) {
      case LanguageCode.vi:
        return 'vi';
      case LanguageCode.en:
        return 'en';
      case LanguageCode.fr:
        return 'fr';
      case LanguageCode.it:
        return 'it';
      case LanguageCode.cn:
        return 'cn';
      case LanguageCode.ja:
        return 'ja';
    }
  }

  String get displayName {
    switch (this) {
      case LanguageCode.vi:
        return '🇻🇳 Tiếng Việt';
      case LanguageCode.en:
        return '🇺🇸 English';
      case LanguageCode.fr:
        return '🇫🇷 Français';
      case LanguageCode.it:
        return '🇮🇹 Italiano';
      case LanguageCode.cn:
        return '🇨🇳 中文';
      case LanguageCode.ja:
        return '🇯🇵 日本語';
    }
  }
}
```

```dart
// services/translation_service.dart
import 'package:cloud_firestore/cloud_firestore.dart';
import '../models/product.dart';

class TranslationService {
  final FirebaseFirestore _firestore = FirebaseFirestore.instance;
  static const String _collectionName = 'product_translations_v2';

  Future<List<Product>> getAllProducts(LanguageCode languageCode) async {
    try {
      final snapshot = await _firestore
          .collection(_collectionName)
          .doc(languageCode.code)
          .collection('products')
          .get();

      return snapshot.docs
          .map((doc) => Product.fromMap(doc.data()))
          .toList();
    } catch (e) {
      print('Error fetching products for ${languageCode.code}: $e');
      rethrow;
    }
  }

  Future<Product?> getProduct(String productId, LanguageCode languageCode) async {
    try {
      final doc = await _firestore
          .collection(_collectionName)
          .doc(languageCode.code)
          .collection('products')
          .doc(productId)
          .get();

      if (doc.exists && doc.data() != null) {
        return Product.fromMap(doc.data()!);
      }
      return null;
    } catch (e) {
      print('Error fetching product $productId in ${languageCode.code}: $e');
      rethrow;
    }
  }

  Future<List<Product>> getProductsWithAttributes(LanguageCode languageCode) async {
    final products = await getAllProducts(languageCode);
    return products.where((product) => product.attributes.isNotEmpty).toList();
  }

  Future<List<Product>> getProductsByCategory(
    int categoryId,
    LanguageCode languageCode,
  ) async {
    final products = await getAllProducts(languageCode);
    return products.where((product) => product.categoryId == categoryId).toList();
  }

  double calculateTotalPrice(Product product, List<AttributeValue> selectedAttributes) {
    final basePrice = product.price;
    final attributesPrice = selectedAttributes.fold<double>(
      0,
      (sum, attr) => sum + attr.priceExtra,
    );
    return basePrice + attributesPrice;
  }

  Future<List<Product>> searchProducts(
    String searchTerm,
    LanguageCode languageCode,
  ) async {
    final products = await getAllProducts(languageCode);
    final lowercaseTerm = searchTerm.toLowerCase();

    return products.where((product) {
      return product.name.toLowerCase().contains(lowercaseTerm) ||
          product.shortDescription.toLowerCase().contains(lowercaseTerm) ||
          product.longDescription.toLowerCase().contains(lowercaseTerm);
    }).toList();
  }

  Stream<List<Product>> getProductsStream(LanguageCode languageCode) {
    return _firestore
        .collection(_collectionName)
        .doc(languageCode.code)
        .collection('products')
        .snapshots()
        .map((snapshot) => snapshot.docs
            .map((doc) => Product.fromMap(doc.data()))
            .toList());
  }
}
```

```dart
// widgets/product_list.dart
import 'package:flutter/material.dart';
import '../models/product.dart';
import '../services/translation_service.dart';
import 'product_card.dart';

class ProductList extends StatefulWidget {
  final LanguageCode languageCode;
  final int? categoryId;

  const ProductList({
    Key? key,
    required this.languageCode,
    this.categoryId,
  }) : super(key: key);

  @override
  State<ProductList> createState() => _ProductListState();
}

class _ProductListState extends State<ProductList> {
  final TranslationService _translationService = TranslationService();
  List<Product> _products = [];
  bool _isLoading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadProducts();
  }

  @override
  void didUpdateWidget(ProductList oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.languageCode != widget.languageCode ||
        oldWidget.categoryId != widget.categoryId) {
      _loadProducts();
    }
  }

  Future<void> _loadProducts() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      List<Product> products;
      
      if (widget.categoryId != null) {
        products = await _translationService.getProductsByCategory(
          widget.categoryId!,
          widget.languageCode,
        );
      } else {
        products = await _translationService.getAllProducts(widget.languageCode);
      }

      setState(() {
        _products = products;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _error = e.toString();
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            CircularProgressIndicator(),
            SizedBox(height: 16),
            Text('Loading products...'),
          ],
        ),
      );
    }

    if (_error != null) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.error_outline,
              size: 64,
              color: Colors.red[300],
            ),
            const SizedBox(height: 16),
            Text(
              'Error: $_error',
              style: TextStyle(color: Colors.red[700]),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: _loadProducts,
              child: const Text('Retry'),
            ),
          ],
        ),
      );
    }

    if (_products.isEmpty) {
      return const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.restaurant_menu,
              size: 64,
              color: Colors.grey,
            ),
            SizedBox(height: 16),
            Text(
              'No products found',
              style: TextStyle(
                fontSize: 18,
                color: Colors.grey,
              ),
            ),
          ],
        ),
      );
    }

    return RefreshIndicator(
      onRefresh: _loadProducts,
      child: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: _products.length,
        itemBuilder: (context, index) {
          return Padding(
            padding: const EdgeInsets.only(bottom: 16),
            child: ProductCard(
              product: _products[index],
              translationService: _translationService,
            ),
          );
        },
      ),
    );
  }
}
```

```dart
// widgets/product_card.dart
import 'package:flutter/material.dart';
import '../models/product.dart';
import '../services/translation_service.dart';

class ProductCard extends StatefulWidget {
  final Product product;
  final TranslationService translationService;

  const ProductCard({
    Key? key,
    required this.product,
    required this.translationService,
  }) : super(key: key);

  @override
  State<ProductCard> createState() => _ProductCardState();
}

class _ProductCardState extends State<ProductCard> {
  List<AttributeValue> _selectedAttributes = [];
  bool _isExpanded = false;

  double get _totalPrice {
    return widget.translationService.calculateTotalPrice(
      widget.product,
      _selectedAttributes,
    );
  }

  void _toggleAttribute(AttributeValue attribute) {
    setState(() {
      final index = _selectedAttributes.indexWhere((attr) => attr.id == attribute.id);
      if (index != -1) {
        _selectedAttributes.removeAt(index);
      } else {
        _selectedAttributes.add(attribute);
      }
    });
  }

  void _selectRadioAttribute(int attributeId, AttributeValue value) {
    setState(() {
      // Remove any existing selection for this attribute
      _selectedAttributes.removeWhere((attr) {
        return widget.product.attributes
            .where((prodAttr) => prodAttr.attributeId == attributeId)
            .any((prodAttr) => prodAttr.values.any((val) => val.id == attr.id));
      });
      
      // Add the new selection
      _selectedAttributes.add(value);
    });
  }

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 4,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Product Header
          Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  widget.product.name,
                  style: Theme.of(context).textTheme.titleLarge?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  widget.product.shortDescription,
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: Colors.grey[600],
                  ),
                ),
                const SizedBox(height: 12),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      '${widget.product.price.toInt().toString().replaceAllMapped(RegExp(r'(\d{1,3})(?=(\d{3})+(?!\d))'), (Match m) => '${m[1]},')} VND',
                      style: Theme.of(context).textTheme.titleLarge?.copyWith(
                        color: Colors.green[700],
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 8,
                        vertical: 4,
                      ),
                      decoration: BoxDecoration(
                        color: Colors.grey[200],
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Text(
                        widget.product.category,
                        style: Theme.of(context).textTheme.bodySmall,
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),

          // Attributes Section
          if (widget.product.attributes.isNotEmpty) ...[
            const Divider(height: 1),
            Theme(
              data: Theme.of(context).copyWith(dividerColor: Colors.transparent),
              child: ExpansionTile(
                title: Text(
                  'Customize (${widget.product.attributes.length} options)',
                  style: const TextStyle(fontWeight: FontWeight.w500),
                ),
                initiallyExpanded: _isExpanded,
                onExpansionChanged: (expanded) {
                  setState(() {
                    _isExpanded = expanded;
                  });
                },
                children: [
                  Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 16),
                    child: Column(
                      children: widget.product.attributes.map((attribute) {
                        return Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Padding(
                              padding: const EdgeInsets.symmetric(vertical: 8),
                              child: Text(
                                attribute.attributeName,
                                style: Theme.of(context).textTheme.titleSmall?.copyWith(
                                  fontWeight: FontWeight.w600,
                                ),
                              ),
                            ),
                            
                            // Checkbox attributes
                            if (attribute.displayType == 'check_box')
                              ...attribute.values.map((value) {
                                final isSelected = _selectedAttributes.any((attr) => attr.id == value.id);
                                return CheckboxListTile(
                                  contentPadding: EdgeInsets.zero,
                                  dense: true,
                                  title: Row(
                                    children: [
                                      Expanded(
                                        child: Text(
                                          value.name,
                                          style: Theme.of(context).textTheme.bodyMedium,
                                        ),
                                      ),
                                      if (value.priceExtra > 0)
                                        Text(
                                          '(+${value.priceExtra.toInt().toString().replaceAllMapped(RegExp(r'(\d{1,3})(?=(\d{3})+(?!\d))'), (Match m) => '${m[1]},')} VND)',
                                          style: Theme.of(context).textTheme.bodySmall?.copyWith(
                                            color: Colors.green[600],
                                            fontWeight: FontWeight.w500,
                                          ),
                                        ),
                                    ],
                                  ),
                                  value: isSelected,
                                  onChanged: (_) => _toggleAttribute(value),
                                );
                              }).toList(),

                            // Radio attributes
                            if (attribute.displayType == 'radio')
                              ...attribute.values.map((value) {
                                final isSelected = _selectedAttributes.any((attr) => attr.id == value.id);
                                return RadioListTile<int>(
                                  contentPadding: EdgeInsets.zero,
                                  dense: true,
                                  title: Row(
                                    children: [
                                      Expanded(
                                        child: Text(
                                          value.name,
                                          style: Theme.of(context).textTheme.bodyMedium,
                                        ),
                                      ),
                                      if (value.priceExtra > 0)
                                        Text(
                                          '(+${value.priceExtra.toInt().toString().replaceAllMapped(RegExp(r'(\d{1,3})(?=(\d{3})+(?!\d))'), (Match m) => '${m[1]},')} VND)',
                                          style: Theme.of(context).textTheme.bodySmall?.copyWith(
                                            color: Colors.green[600],
                                            fontWeight: FontWeight.w500,
                                          ),
                                        ),
                                    ],
                                  ),
                                  value: value.id,
                                  groupValue: isSelected ? value.id : null,
                                  onChanged: (_) => _selectRadioAttribute(attribute.attributeId, value),
                                );
                              }).toList(),
                            
                            const SizedBox(height: 8),
                          ],
                        );
                      }).toList(),
                    ),
                  ),
                ],
              ),
            ),
          ],

          // Footer
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.grey[50],
              borderRadius: const BorderRadius.only(
                bottomLeft: Radius.circular(12),
                bottomRight: Radius.circular(12),
              ),
            ),
            child: Column(
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      'Total: ${_totalPrice.toInt().toString().replaceAllMapped(RegExp(r'(\d{1,3})(?=(\d{3})+(?!\d))'), (Match m) => '${m[1]},')} VND',
                      style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    ElevatedButton(
                      onPressed: () {
                        // Handle add to cart
                        print('Adding to cart: ${widget.product.name}');
                        print('Selected attributes: ${_selectedAttributes.map((attr) => attr.name).join(', ')}');
                        print('Total price: $_totalPrice');
                      },
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.blue[600],
                        foregroundColor: Colors.white,
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(8),
                        ),
                      ),
                      child: const Text('Add to Cart'),
                    ),
                  ],
                ),
                
                if (_selectedAttributes.isNotEmpty) ...[
                  const SizedBox(height: 8),
                  Align(
                    alignment: Alignment.centerLeft,
                    child: Text(
                      'Selected: ${_selectedAttributes.map((attr) => attr.name).join(', ')}',
                      style: Theme.of(context).textTheme.bodySmall?.copyWith(
                        color: Colors.grey[600],
                      ),
                    ),
                  ),
                ],
              ],
            ),
          ),
        ],
      ),
    );
  }
}
```

This comprehensive SDK documentation provides working examples for all major platforms showing how to retrieve product translations with attributes from Firestore. Each example includes proper error handling, caching strategies, and UI components for displaying products with customizable options and pricing calculations.