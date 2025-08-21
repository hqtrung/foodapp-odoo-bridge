# Translation System Quick Reference

## 🚀 Quick Start

### Language Codes
```
vi = Vietnamese (Default)
en = English
fr = French  
it = Italian
cn = Chinese
ja = Japanese
```

### Firebase SDK (Recommended)
```javascript
// Get all products in English
const productsRef = collection(db, 'product_translations_v2/en/products');
const snapshot = await getDocs(productsRef);

// Get specific product in French
const productRef = doc(db, 'product_translations_v2/fr/products/1186');
const product = await getDoc(productRef);
```

### REST API
```bash
# All English products
GET /api/v1/translations-v2/products?language=en

# Specific French product  
GET /api/v1/translations-v2/products/1186?language=fr

# Italian categories  
GET /api/v1/translations-v2/categories?language=it

# Product with attributes/toppings
GET /api/v1/translations-v2/products/2477?language=en
```

## 📊 Performance Tips

### ✅ Do This
```javascript
// Bulk fetch (Fast: ~100ms for 53 products)
const menu = await getAllProductsInLanguage('en');

// Cache frequently used languages
const cache = new Map();
cache.set('en', await getAllProductsInLanguage('en'));
```

### ❌ Don't Do This
```javascript
// Individual calls (Slow: ~4s for 53 products)
const products = await Promise.all(
  ids.map(id => getProduct(id, 'en'))
);
```

## 🔧 Common Patterns

### Product with Attributes
```javascript
const product = await getProduct('2477', 'en');
console.log({
  name: product.name,
  price: product.price,
  attributes: product.attributes?.map(attr => ({
    name: attr.attribute_name,
    options: attr.values.length
  }))
});

// Calculate total with toppings
const calculateTotal = (product, selectedOptions) => {
  let total = product.price;
  selectedOptions.forEach(option => {
    total += option.price_extra;
  });
  return total;
};
```

## 🔧 More Patterns

### Language Switcher
```javascript
const [lang, setLang] = useState('vi');
const [menu, setMenu] = useState([]);

const switchLanguage = async (newLang) => {
  setLang(newLang);
  const newMenu = await fetchMenu(newLang);
  setMenu(newMenu);
};
```

### Error Handling
```javascript
try {
  const products = await fetchMenu(language);
} catch (error) {
  if (error.code === 'not-found') {
    // Language not available, fallback to default
    return await fetchMenu('vi');
  }
  throw error;
}
```

## 🔍 Debugging

### Check Available Languages
```javascript
const languages = ['vi', 'en', 'fr', 'it', 'cn', 'ja'];
for (const lang of languages) {
  const products = await fetchMenu(lang);
  console.log(`${lang}: ${products.length} products`);
}
```

### Validate Structure
```javascript
const product = await getProduct('1186', 'en');
console.log({
  id: product.product_id,
  name: product.name,
  language: product.language_code,
  hasDescription: !!product.short_description
});
```

## 📱 Frontend Examples

### React Hook
```javascript
const useMenu = (language) => {
  const [menu, setMenu] = useState([]);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    fetchMenu(language).then(setMenu).finally(() => setLoading(false));
  }, [language]);
  
  return { menu, loading };
};
```

### Vue Composable
```javascript
export const useTranslations = (language) => {
  const products = ref([]);
  const loading = ref(false);
  
  watch(language, async (newLang) => {
    loading.value = true;
    products.value = await fetchMenu(newLang);
    loading.value = false;
  }, { immediate: true });
  
  return { products, loading };
};
```

## 🚨 Common Errors

| Error | Fix |
|-------|-----|
| `Language 'english' not found` | Use `'en'` not `'english'` |
| `Permission denied` | Update Firestore rules |
| `Empty results` | Check language exists in Firestore |
| `Slow performance` | Use bulk fetch, not individual calls |

---

**🔗 Full Documentation:** [TRANSLATION_SYSTEM_DOCUMENTATION.md](./TRANSLATION_SYSTEM_DOCUMENTATION.md)