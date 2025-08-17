# FoodOrder PWA - Complete Project Planning Document

## Table of Contents
1. [Executive Summary](#executive-summary)
2. [Product Requirements Document](#product-requirements-document)
3. [Technical Architecture](#technical-architecture)
4. [Internationalization (i18n)](#internationalization-i18n)
5. [System Integration](#system-integration)
6. [Database Design](#database-design)
7. [User Interface Specifications](#user-interface-specifications)
8. [Development Phases](#development-phases)
9. [API Documentation](#api-documentation)
10. [PWA Features](#pwa-features)
11. [Deployment Strategy](#deployment-strategy)

---

## Executive Summary

### Project Overview
A mobile-first Progressive Web App (PWA) for Vietnamese food ordering, designed to seamlessly integrate with existing Odoo 18 POS systems. The application will serve customers placing orders for table service or home delivery, with cash payment processing through the restaurant's existing workflow.

### Key Objectives
- **Customer Experience**: Provide fast, intuitive mobile ordering with offline capabilities
- **Business Integration**: Leverage existing Odoo 18 POS infrastructure without disruption
- **Operational Efficiency**: Streamline order management through unified dashboard
- **Technical Excellence**: Modern PWA with offline-first architecture

### Success Metrics
- Order completion rate improvement
- Reduced order processing time
- Customer satisfaction with mobile experience
- Staff efficiency in order management

---

## Product Requirements Document

### Core Features

#### Customer Features
- **Menu Browsing**: Category-based navigation with search functionality
- **Product Customization**: Topping selection with dynamic pricing
- **Shopping Cart**: Item management with customer notes per item
- **Order Types**: 
  - Table service (table ID entry for dine-in delivery)
  - Home delivery (address entry with delivery notes)
- **Order Placement**: Simple checkout with cash payment confirmation
- **Order Tracking**: Real-time status updates with push notifications
- **Customer Notes**: 
  - Item-level notes (allergies, preferences, special requests)
  - Delivery-level notes (address details, delivery instructions)

#### Staff Features
- **Order Dashboard**: Real-time view of incoming orders by type and status
- **Order Management**: Status updates through workflow stages
- **Menu Display**: Current item availability and pricing

#### Administrative Features
- **Menu Synchronization**: Automatic sync with Odoo 18 POS product catalog
- **Order Integration**: Seamless order creation in existing POS system
- **Analytics**: Basic order tracking and reporting through Odoo

### Menu Categories

#### Special Categories
- **Promotion**: Featured deals and special offers
- **Combo**: Bundled meal packages
- **Flash Sale**: Time-limited promotional items

#### Food Categories
- **Banh Mi**: Vietnamese sandwich varieties
- **Drink**: Beverages (coffee, tea, juices, soft drinks)
- **Other Dishes**: Main courses and rice dishes
- **Side Dish**: Appetizers and complementary items
- **Dessert**: Sweet treats and desserts

### Product Customization System
- **Toppings**: Each product can have multiple topping options
- **Pricing**: Dynamic price calculation (base price + topping costs)
- **Examples**: 
  - Extra meat (+$2.00)
  - Extra vegetables (+$1.00)
  - Spicy sauce (+$0.50)
  - Remove ingredients (no charge)

### User Journey

#### Customer Flow
1. **Landing Page** → Select order type (table service/delivery)
2. **Menu Browsing** → Navigate categories, view product details
3. **Product Selection** → Customize with toppings, add to cart
4. **Cart Review** → Modify quantities, add item notes
5. **Checkout** → Enter table ID or delivery address, add delivery notes
6. **Order Confirmation** → Receive order number and tracking link
7. **Order Tracking** → Monitor real-time status updates

#### Staff Flow
1. **Dashboard Login** → View pending orders by type
2. **Order Review** → Check order details, items, and customizations
3. **Status Management** → Update order through workflow stages
4. **Order Completion** → Mark as ready/delivered

---

## Technical Architecture

### Technology Stack

#### Frontend
- **Framework**: Next.js 15 with App Router
- **Language**: TypeScript for type safety
- **Styling**: Tailwind CSS for responsive design
- **PWA**: @ducanh2912/next-pwa (modern alternative to next-pwa)
- **State Management**: Zustand for global state
- **Forms**: React Hook Form + Zod validation
- **UI Components**: Headless UI or Radix UI primitives
- **Internationalization**: next-intl for multi-language support
- **Fonts**: next/font for optimized font loading

#### Backend Bridge
- **API Framework**: FastAPI for high-performance REST API
- **Authentication**: JWT tokens with Odoo session management
- **Caching**: Redis for session data and menu caching
- **Real-time**: Server-Sent Events for order status updates
- **Background Tasks**: Celery for async order processing

#### Database & Integration
- **Primary Database**: Odoo 18 PostgreSQL database
- **Session Storage**: Redis for temporary data
- **File Storage**: Local storage for cached images
- **Search**: Basic text search within application

### Architecture Patterns

#### Frontend Architecture
```
app/
├── (customer)/          # Customer-facing routes
│   ├── page.tsx         # Landing page
│   ├── menu/            # Menu browsing
│   ├── product/[id]/    # Product details
│   ├── cart/           # Shopping cart
│   └── order/[id]/     # Order tracking
├── (staff)/            # Staff dashboard routes
│   └── dashboard/      # Order management
├── api/                # API route handlers
└── globals.css         # Global styles
```

#### Component Structure
```
components/
├── ui/                 # Reusable UI components
├── menu/              # Menu-specific components
├── cart/              # Shopping cart components
├── order/             # Order management components
└── layout/            # Layout components
```

#### State Management
```typescript
// Zustand stores
interface CartStore {
  items: CartItem[]
  addItem: (item: Product, toppings: Topping[]) => void
  removeItem: (id: string) => void
  updateQuantity: (id: string, quantity: number) => void
  clear: () => void
}

interface OrderStore {
  currentOrder: Order | null
  orderHistory: Order[]
  trackOrder: (orderId: string) => void
}
```

---

## Internationalization (i18n)

### Multi-Language Support

The FoodOrder PWA will support **6 languages** with Vietnamese as the primary language:

1. **Vietnamese (vi)** - Primary language
2. **English (en)** - International customers
3. **French (fr)** - French-speaking customers
4. **Italian (it)** - Italian-speaking customers
5. **Chinese (zh)** - Chinese-speaking customers
6. **Japanese (ja)** - Japanese-speaking customers

### Technical Implementation

#### Next.js Internationalization with next-intl

```typescript
// middleware.ts - Route handling for different locales
import createMiddleware from 'next-intl/middleware';

export default createMiddleware({
  locales: ['vi', 'en', 'fr', 'it', 'zh', 'ja'],
  defaultLocale: 'vi',
  localePrefix: 'as-needed'
});

export const config = {
  matcher: ['/((?!api|_next|_vercel|.*\\..*).*)']
};
```

#### Language File Structure

```
locales/
├── vi/           # Vietnamese (Primary)
│   ├── common.json
│   ├── menu.json
│   ├── cart.json
│   ├── order.json
│   └── staff.json
├── en/           # English
│   ├── common.json
│   ├── menu.json
│   ├── cart.json
│   ├── order.json
│   └── staff.json
├── fr/           # French
├── it/           # Italian
├── zh/           # Chinese
└── ja/           # Japanese
```

#### Translation File Examples

```json
// locales/vi/common.json
{
  "navigation": {
    "home": "Trang chủ",
    "menu": "Thực đơn",
    "cart": "Giỏ hàng",
    "orders": "Đơn hàng"
  },
  "orderTypes": {
    "table": "Phục vụ tại bàn",
    "delivery": "Giao hàng tận nơi"
  },
  "actions": {
    "addToCart": "Thêm vào giỏ",
    "checkout": "Thanh toán",
    "placeOrder": "Đặt hàng"
  }
}

// locales/en/common.json
{
  "navigation": {
    "home": "Home",
    "menu": "Menu",
    "cart": "Cart",
    "orders": "Orders"
  },
  "orderTypes": {
    "table": "Table Service",
    "delivery": "Home Delivery"
  },
  "actions": {
    "addToCart": "Add to Cart",
    "checkout": "Checkout",
    "placeOrder": "Place Order"
  }
}
```

#### Menu Category Translations

```json
// locales/vi/menu.json
{
  "categories": {
    "promotion": "Khuyến mãi",
    "combo": "Combo",
    "flashSale": "Flash Sale",
    "banhMi": "Bánh mì",
    "drink": "Đồ uống",
    "otherDishes": "Món khác",
    "sideDish": "Món phụ",
    "dessert": "Tráng miệng"
  },
  "toppings": {
    "extraMeat": "Thêm thịt",
    "extraVegetables": "Thêm rau",
    "spicySauce": "Tương ớt",
    "remove": "Bỏ"
  }
}

// locales/en/menu.json
{
  "categories": {
    "promotion": "Promotion",
    "combo": "Combo",
    "flashSale": "Flash Sale",
    "banhMi": "Banh Mi",
    "drink": "Drinks",
    "otherDishes": "Other Dishes",
    "sideDish": "Side Dish",
    "dessert": "Dessert"
  },
  "toppings": {
    "extraMeat": "Extra Meat",
    "extraVegetables": "Extra Vegetables",
    "spicySauce": "Spicy Sauce",
    "remove": "Remove"
  }
}
```

### Locale-Specific Features

#### Date and Time Formatting

```typescript
// utils/dateFormatting.ts
import { useLocale } from 'next-intl';

export function useLocalizedDate() {
  const locale = useLocale();
  
  const formatOrderTime = (date: Date) => {
    return new Intl.DateTimeFormat(locale, {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    }).format(date);
  };
  
  const formatEstimatedTime = (minutes: number) => {
    const translations = {
      vi: `${minutes} phút`,
      en: `${minutes} minutes`,
      fr: `${minutes} minutes`,
      it: `${minutes} minuti`,
      zh: `${minutes} 分钟`,
      ja: `${minutes} 分`
    };
    
    return translations[locale] || `${minutes} min`;
  };
  
  return { formatOrderTime, formatEstimatedTime };
}
```

#### Currency Formatting

```typescript
// utils/currencyFormatting.ts
import { useLocale } from 'next-intl';

export function useLocalizedCurrency() {
  const locale = useLocale();
  
  const formatPrice = (amount: number) => {
    const currencyFormatters = {
      vi: new Intl.NumberFormat('vi-VN', { 
        style: 'currency', 
        currency: 'VND',
        minimumFractionDigits: 0
      }),
      en: new Intl.NumberFormat('en-US', { 
        style: 'currency', 
        currency: 'USD' 
      }),
      fr: new Intl.NumberFormat('fr-FR', { 
        style: 'currency', 
        currency: 'EUR' 
      }),
      it: new Intl.NumberFormat('it-IT', { 
        style: 'currency', 
        currency: 'EUR' 
      }),
      zh: new Intl.NumberFormat('zh-CN', { 
        style: 'currency', 
        currency: 'CNY' 
      }),
      ja: new Intl.NumberFormat('ja-JP', { 
        style: 'currency', 
        currency: 'JPY' 
      })
    };
    
    return currencyFormatters[locale]?.format(amount) || `$${amount}`;
  };
  
  return { formatPrice };
}
```

### Language Selector Component

```typescript
// components/LanguageSelector.tsx
import { useLocale, useTranslations } from 'next-intl';
import { useRouter, usePathname } from 'next/navigation';

const languages = [
  { code: 'vi', name: 'Tiếng Việt', flag: '🇻🇳' },
  { code: 'en', name: 'English', flag: '🇺🇸' },
  { code: 'fr', name: 'Français', flag: '🇫🇷' },
  { code: 'it', name: 'Italiano', flag: '🇮🇹' },
  { code: 'zh', name: '中文', flag: '🇨🇳' },
  { code: 'ja', name: '日本語', flag: '🇯🇵' }
];

export function LanguageSelector() {
  const locale = useLocale();
  const router = useRouter();
  const pathname = usePathname();
  const t = useTranslations('common');
  
  const handleLanguageChange = (newLocale: string) => {
    const newPath = pathname.replace(`/${locale}`, `/${newLocale}`);
    router.push(newPath);
  };
  
  return (
    <select 
      value={locale}
      onChange={(e) => handleLanguageChange(e.target.value)}
      className="language-selector"
    >
      {languages.map((lang) => (
        <option key={lang.code} value={lang.code}>
          {lang.flag} {lang.name}
        </option>
      ))}
    </select>
  );
}
```

### Font Optimization for Multi-Language

```typescript
// app/layout.tsx
import { Inter } from 'next/font/google';
import localFont from 'next/font/local';

// Inter for Latin scripts (English, French, Italian)
const inter = Inter({
  subsets: ['latin', 'latin-ext'],
  variable: '--font-inter'
});

// Be Vietnam Pro for Vietnamese
const beVietnamPro = localFont({
  src: [
    {
      path: './fonts/BeVietnamPro-Regular.woff2',
      weight: '400',
      style: 'normal',
    },
    {
      path: './fonts/BeVietnamPro-Medium.woff2',
      weight: '500',
      style: 'normal',
    },
    {
      path: './fonts/BeVietnamPro-SemiBold.woff2',
      weight: '600',
      style: 'normal',
    }
  ],
  variable: '--font-be-vietnam-pro'
});

// Noto Sans for Chinese and Japanese
const notoSans = localFont({
  src: [
    {
      path: './fonts/NotoSansCJK-Regular.woff2',
      weight: '400',
      style: 'normal',
    },
    {
      path: './fonts/NotoSansCJK-Medium.woff2',
      weight: '500',
      style: 'normal',
    }
  ],
  variable: '--font-noto-sans'
});
```

### CSS for Language-Specific Styling

```css
/* globals.css */
:root {
  --font-primary: var(--font-inter);
  --font-vietnamese: var(--font-be-vietnam-pro);
  --font-cjk: var(--font-noto-sans);
}

html[lang="vi"] {
  font-family: var(--font-vietnamese), var(--font-primary), sans-serif;
}

html[lang="zh"],
html[lang="ja"] {
  font-family: var(--font-cjk), var(--font-primary), sans-serif;
}

html[lang="en"],
html[lang="fr"],
html[lang="it"] {
  font-family: var(--font-primary), sans-serif;
}

/* Right-to-left support for future expansion */
html[dir="rtl"] {
  text-align: right;
}

html[dir="rtl"] .cart-panel {
  right: auto;
  left: 0;
}
```

### API Internationalization

```python
# FastAPI backend - Language-aware responses
from fastapi import FastAPI, Header
from typing import Optional

app = FastAPI()

@app.get("/api/v1/categories")
async def get_categories(
    accept_language: Optional[str] = Header(None)
):
    locale = parse_locale(accept_language) or 'vi'
    
    categories = await get_categories_from_odoo()
    
    # Return translated category names
    return {
        "categories": [
            {
                "id": cat.id,
                "name": get_translated_name(cat, locale),
                "type": cat.type,
                "products": [
                    {
                        "id": prod.id,
                        "name": get_translated_name(prod, locale),
                        "description": get_translated_description(prod, locale),
                        "base_price": prod.base_price
                    }
                    for prod in cat.products
                ]
            }
            for cat in categories
        ]
    }

def parse_locale(accept_language: str) -> str:
    if not accept_language:
        return 'vi'
    
    # Parse Accept-Language header
    # Example: "vi,en;q=0.9,fr;q=0.8"
    languages = accept_language.split(',')
    for lang in languages:
        locale = lang.split(';')[0].strip()[:2]
        if locale in ['vi', 'en', 'fr', 'it', 'zh', 'ja']:
            return locale
    
    return 'vi'
```

### Development Workflow for Translations

#### Translation Management

```json
// package.json scripts for translation management
{
  "scripts": {
    "i18n:extract": "extract-messages",
    "i18n:compile": "compile-messages",
    "i18n:validate": "validate-translations",
    "i18n:sync": "sync-translations"
  }
}
```

#### Translation Validation

```typescript
// scripts/validateTranslations.ts
import fs from 'fs';
import path from 'path';

const locales = ['vi', 'en', 'fr', 'it', 'zh', 'ja'];
const files = ['common.json', 'menu.json', 'cart.json', 'order.json', 'staff.json'];

function validateTranslations() {
  const baseLocale = 'vi';
  const issues: string[] = [];
  
  for (const file of files) {
    const basePath = path.join('locales', baseLocale, file);
    const baseContent = JSON.parse(fs.readFileSync(basePath, 'utf8'));
    const baseKeys = extractKeys(baseContent);
    
    for (const locale of locales) {
      if (locale === baseLocale) continue;
      
      const localePath = path.join('locales', locale, file);
      if (!fs.existsSync(localePath)) {
        issues.push(`Missing file: ${localePath}`);
        continue;
      }
      
      const localeContent = JSON.parse(fs.readFileSync(localePath, 'utf8'));
      const localeKeys = extractKeys(localeContent);
      
      // Check for missing keys
      const missingKeys = baseKeys.filter(key => !localeKeys.includes(key));
      if (missingKeys.length > 0) {
        issues.push(`${locale}/${file}: Missing keys: ${missingKeys.join(', ')}`);
      }
      
      // Check for extra keys
      const extraKeys = localeKeys.filter(key => !baseKeys.includes(key));
      if (extraKeys.length > 0) {
        issues.push(`${locale}/${file}: Extra keys: ${extraKeys.join(', ')}`);
      }
    }
  }
  
  if (issues.length > 0) {
    console.error('Translation issues found:');
    issues.forEach(issue => console.error(`- ${issue}`));
    process.exit(1);
  } else {
    console.log('All translations are valid ✅');
  }
}

function extractKeys(obj: any, prefix = ''): string[] {
  const keys: string[] = [];
  
  for (const [key, value] of Object.entries(obj)) {
    const fullKey = prefix ? `${prefix}.${key}` : key;
    
    if (typeof value === 'object' && value !== null) {
      keys.push(...extractKeys(value, fullKey));
    } else {
      keys.push(fullKey);
    }
  }
  
  return keys;
}

validateTranslations();
```

### PWA Manifest Localization

```typescript
// Dynamic manifest generation based on locale
export async function GET(request: Request) {
  const url = new URL(request.url);
  const locale = url.searchParams.get('locale') || 'vi';
  
  const manifests = {
    vi: {
      name: "FoodOrder - Nhà hàng Việt Nam",
      short_name: "FoodOrder",
      description: "Đặt món ăn Việt Nam phục vụ tại bàn hoặc giao hàng",
      lang: "vi",
      dir: "ltr"
    },
    en: {
      name: "FoodOrder - Vietnamese Restaurant",
      short_name: "FoodOrder", 
      description: "Order Vietnamese food for table service or delivery",
      lang: "en",
      dir: "ltr"
    },
    fr: {
      name: "FoodOrder - Restaurant Vietnamien",
      short_name: "FoodOrder",
      description: "Commandez de la nourriture vietnamienne pour service à table ou livraison",
      lang: "fr",
      dir: "ltr"
    }
    // ... other locales
  };
  
  const baseManifest = {
    start_url: `/${locale}`,
    display: "standalone",
    background_color: "#ffffff",
    theme_color: "#F97316",
    orientation: "portrait-primary",
    icons: [/* ... */],
    categories: ["food", "business"]
  };
  
  return Response.json({
    ...baseManifest,
    ...manifests[locale]
  });
}
```

---

## System Integration

### Odoo 18 Integration Strategy

#### FastAPI Bridge Architecture
The FastAPI application serves as a middleware layer between the Next.js frontend and Odoo 18 backend, providing:

- **Data Transformation**: Convert Odoo models to simplified JSON for frontend consumption
- **Authentication Management**: Handle Odoo API credentials securely
- **Caching Layer**: Reduce direct Odoo API calls through intelligent caching
- **Real-time Updates**: Manage WebSocket/SSE connections for order status
- **Error Handling**: Graceful error management and fallback strategies

#### Odoo 18 POS Integration Points

##### Product Catalog Sync
```python
# FastAPI endpoints for menu data
GET /api/v1/categories -> Odoo product.category model
GET /api/v1/products -> Odoo product.product model
GET /api/v1/products/{id}/toppings -> Custom topping management
```

##### Order Management
```python
# Order lifecycle management
POST /api/v1/orders -> Create pos.order in Odoo
PUT /api/v1/orders/{id}/status -> Update order workflow state
GET /api/v1/orders/{id} -> Fetch order details from Odoo
GET /api/v1/orders/{id}/stream -> SSE for real-time updates
```

##### Data Models Mapping
```python
# Odoo to API model transformation
OdooProduct -> {
    id: int
    name: str
    category_id: int
    base_price: float
    description: str
    image_url: str
    available: bool
    toppings: List[Topping]
}

OdooOrder -> {
    id: int
    order_number: str
    customer_notes: str
    delivery_notes: str
    order_type: "table" | "delivery"
    table_id: Optional[str]
    delivery_address: Optional[str]
    status: OrderStatus
    items: List[OrderItem]
    total: float
    created_at: datetime
}
```

### API Authentication & Security

#### Odoo API Access
- **API Keys**: Secure Odoo API key management
- **Session Management**: Handle Odoo user sessions
- **Rate Limiting**: Prevent API abuse
- **Data Validation**: Ensure data integrity

#### Frontend Security
- **HTTPS Only**: Force secure connections
- **Content Security Policy**: Prevent XSS attacks
- **Input Validation**: Sanitize all user inputs
- **Session Security**: Secure JWT token handling

---

## Database Design

### Odoo 18 Models (Source of Truth)

#### Core Product Models
```sql
-- Existing Odoo models to leverage
product.category (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    parent_id INTEGER,
    sequence INTEGER
)

product.product (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    categ_id INTEGER REFERENCES product.category,
    list_price DECIMAL(10,2),
    description TEXT,
    available_in_pos BOOLEAN,
    image_1920 BYTEA
)
```

#### POS Order Models
```sql
pos.order (
    id SERIAL PRIMARY KEY,
    name VARCHAR(64),
    date_order TIMESTAMP,
    user_id INTEGER,
    amount_total DECIMAL(10,2),
    state VARCHAR(32),
    table_id INTEGER,
    customer_notes TEXT,
    delivery_address TEXT
)

pos.order.line (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES pos.order,
    product_id INTEGER REFERENCES product.product,
    qty DECIMAL(10,3),
    price_unit DECIMAL(10,2),
    customer_note TEXT
)
```

### Extended Models for Food Ordering

#### Custom Topping System
```sql
-- Custom models for enhanced functionality
food_order.topping (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    price DECIMAL(8,2),
    category VARCHAR(64),
    available BOOLEAN DEFAULT TRUE
)

food_order.product_topping (
    id SERIAL PRIMARY KEY,
    product_id INTEGER REFERENCES product.product,
    topping_id INTEGER REFERENCES food_order.topping
)

food_order.order_line_topping (
    id SERIAL PRIMARY KEY,
    order_line_id INTEGER REFERENCES pos.order.line,
    topping_id INTEGER REFERENCES food_order.topping,
    quantity INTEGER DEFAULT 1
)
```

#### Session & Cache Models
```sql
-- FastAPI session management
food_order.cart_session (
    id UUID PRIMARY KEY,
    session_data JSONB,
    created_at TIMESTAMP,
    expires_at TIMESTAMP
)

food_order.notification_queue (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES pos.order,
    message TEXT,
    push_token VARCHAR(512),
    status VARCHAR(32),
    created_at TIMESTAMP
)
```

---

## User Interface Specifications

### Design Principles
- **Mobile-First**: Optimized for smartphone usage
- **Vietnamese Cultural Context**: Appropriate colors, fonts, and imagery
- **Accessibility**: WCAG 2.1 AA compliance
- **Performance**: <3 second load times on 3G networks

### Color Palette
```css
/* Modern Vietnamese food ordering color scheme */
:root {
  --primary: #F97316;        /* Modern Orange */
  --primary-light: #FDBA74;  /* Light Orange */
  --secondary: #EF4444;      /* Warm Coral */
  --accent: #22C55E;         /* Fresh Mint Green */
  --background: #FCFCFD;     /* Pure White */
  --surface: #F9FAFB;        /* Light Gray */
  --text-primary: #1F2937;   /* Dark Gray */
  --text-secondary: #6B7280; /* Medium Gray */
}
```

### Typography
- **Primary Font**: Inter (clean, readable)
- **Accent Font**: Be Vietnam Pro (Vietnamese-optimized)
- **Size Scale**: 14px base, 1.25 ratio

### Component Specifications

#### Navigation
- **Bottom Tab Bar**: Primary navigation for customers
- **Breadcrumbs**: Category navigation in menu
- **Back Button**: Consistent placement and behavior

#### Product Cards
- **Image**: 16:9 aspect ratio, lazy loaded
- **Price Display**: Prominent, with currency symbol
- **Availability**: Clear indicators for out-of-stock
- **Quick Add**: Fast add-to-cart functionality

#### Shopping Cart
- **Sliding Panel**: Overlay with item summary
- **Item Cards**: Image, name, customizations, quantity controls
- **Price Breakdown**: Subtotal, tax (if applicable), total
- **Notes Input**: Text areas for customer preferences

#### Order Tracking
- **Progress Bar**: Visual order status indicator
- **Timeline**: Detailed status history
- **Estimated Time**: Dynamic delivery estimates
- **Contact Options**: Easy access to restaurant contact

### Responsive Breakpoints
```css
/* Mobile-first responsive design */
@media (min-width: 640px) { /* sm */ }
@media (min-width: 768px) { /* md */ }
@media (min-width: 1024px) { /* lg */ }
@media (min-width: 1280px) { /* xl */ }
```

---

## Development Phases

### Phase 1: Foundation Setup (Week 1)
**Objective**: Establish development environment and basic architecture

#### Tasks
- [ ] Next.js 15 project initialization with TypeScript
- [ ] Tailwind CSS configuration and design system setup
- [ ] PWA configuration with @ducanh2912/next-pwa
- [ ] Basic routing structure (customer/staff route groups)
- [ ] Zustand store setup for state management
- [ ] Development environment configuration

#### Deliverables
- Working Next.js application with PWA capabilities
- Basic navigation and routing
- Design system components
- Development tooling (ESLint, Prettier, Husky)

### Phase 2: Menu System (Week 2)
**Objective**: Implement menu browsing and product selection

#### Tasks
- [ ] Category-based menu navigation
- [ ] Product listing with images and pricing
- [ ] Product detail pages with topping selection
- [ ] Search functionality within menu
- [ ] Basic shopping cart implementation
- [ ] Mock data integration for development

#### Deliverables
- Complete menu browsing experience
- Product customization interface
- Shopping cart with item management
- Responsive design implementation

### Phase 3: FastAPI Bridge Development (Week 3)
**Objective**: Create API bridge to Odoo 18 system

#### Tasks
- [ ] FastAPI application setup and configuration
- [ ] Odoo 18 API integration and authentication
- [ ] Product catalog synchronization endpoints
- [ ] Order creation and management APIs
- [ ] Caching layer implementation with Redis
- [ ] Error handling and logging setup

#### Deliverables
- Functional FastAPI bridge application
- Odoo integration for products and orders
- API documentation (OpenAPI/Swagger)
- Caching and performance optimization

### Phase 4: Order Management (Week 4)
**Objective**: Complete order lifecycle management

#### Tasks
- [ ] Order placement functionality
- [ ] Real-time order status tracking
- [ ] Staff dashboard for order management
- [ ] Push notification system implementation
- [ ] Customer notes and delivery instructions
- [ ] Order history and tracking

#### Deliverables
- End-to-end order processing
- Staff management interface
- Real-time updates and notifications
- Complete customer order experience

### Phase 5: PWA Features & Optimization (Week 5)
**Objective**: Enhance offline capabilities and performance

#### Tasks
- [ ] Offline menu browsing implementation
- [ ] Service worker for background sync
- [ ] Push notification registration and handling
- [ ] Performance optimization and caching
- [ ] Error boundary and fallback handling
- [ ] PWA manifest and installability

#### Deliverables
- Full offline functionality
- Optimized performance metrics
- Installable PWA experience
- Comprehensive error handling

### Phase 6: Testing & Deployment (Week 6)
**Objective**: Quality assurance and production deployment

#### Tasks
- [ ] Unit testing for critical components
- [ ] Integration testing for API endpoints
- [ ] End-to-end testing for user workflows
- [ ] Performance testing and optimization
- [ ] Production deployment configuration
- [ ] Monitoring and analytics setup

#### Deliverables
- Comprehensive test coverage
- Production-ready deployment
- Monitoring and error tracking
- Documentation and user guides

---

## API Documentation

### REST API Endpoints

#### Menu Management
```typescript
// Get all categories with products
GET /api/v1/categories
Response: {
  categories: Array<{
    id: number
    name: string
    type: 'special' | 'food'
    products: Array<Product>
  }>
}

// Get product details with toppings
GET /api/v1/products/{productId}
Response: {
  product: {
    id: number
    name: string
    description: string
    base_price: number
    image_url: string
    category_id: number
    available: boolean
    toppings: Array<{
      id: number
      name: string
      price: number
      category: string
    }>
  }
}
```

#### Order Operations
```typescript
// Create new order
POST /api/v1/orders
Request: {
  order_type: 'table' | 'delivery'
  table_id?: string
  delivery_address?: string
  delivery_notes?: string
  items: Array<{
    product_id: number
    quantity: number
    customer_note?: string
    toppings: Array<{
      topping_id: number
      quantity: number
    }>
  }>
}
Response: {
  order: {
    id: number
    order_number: string
    status: 'pending' | 'confirmed' | 'preparing' | 'ready' | 'completed'
    total: number
    estimated_time?: number
  }
}

// Get order status
GET /api/v1/orders/{orderId}
Response: {
  order: {
    id: number
    order_number: string
    status: OrderStatus
    items: Array<OrderItem>
    total: number
    created_at: string
    updated_at: string
    table_id?: string
    delivery_address?: string
    delivery_notes?: string
  }
}

// Update order status (staff only)
PUT /api/v1/orders/{orderId}/status
Request: {
  status: OrderStatus
}
Response: {
  success: boolean
  order: Order
}
```

#### Real-time Updates
```typescript
// Server-Sent Events for order tracking
GET /api/v1/orders/{orderId}/stream
Response: text/event-stream
Event Types:
- status_changed: { status: OrderStatus, timestamp: string }
- estimated_time_updated: { estimated_time: number }
- notification: { message: string, type: 'info' | 'warning' | 'success' }
```

### WebSocket Events (Alternative to SSE)
```typescript
// WebSocket connection for real-time updates
WS /api/v1/ws/orders/{orderId}

Client -> Server:
{
  type: 'subscribe',
  order_id: number
}

Server -> Client:
{
  type: 'status_update',
  data: {
    order_id: number,
    status: OrderStatus,
    timestamp: string
  }
}
```

### Error Handling
```typescript
// Standard error response format
{
  error: {
    code: string
    message: string
    details?: any
  }
  timestamp: string
  path: string
}

// Common error codes
- INVALID_INPUT: Request validation failed
- ORDER_NOT_FOUND: Order does not exist
- PRODUCT_UNAVAILABLE: Product is out of stock
- ODOO_CONNECTION_ERROR: Backend integration issue
- AUTHENTICATION_REQUIRED: Invalid or missing credentials
```

---

## PWA Features

### Service Worker Implementation

#### Caching Strategies
```javascript
// Cache-first for static assets
self.addEventListener('fetch', (event) => {
  if (event.request.destination === 'image') {
    event.respondWith(
      caches.open('images-v1').then(cache => {
        return cache.match(event.request).then(response => {
          return response || fetch(event.request).then(response => {
            cache.put(event.request, response.clone());
            return response;
          });
        });
      })
    );
  }
});

// Network-first for API calls
self.addEventListener('fetch', (event) => {
  if (event.request.url.includes('/api/')) {
    event.respondWith(
      fetch(event.request).catch(() => {
        return caches.match(event.request);
      })
    );
  }
});
```

#### Background Sync
```javascript
// Queue orders for background sync
self.addEventListener('sync', (event) => {
  if (event.tag === 'order-sync') {
    event.waitUntil(syncOrders());
  }
});

async function syncOrders() {
  const pendingOrders = await getStoredOrders();
  
  for (const order of pendingOrders) {
    try {
      await submitOrder(order);
      await removeStoredOrder(order.id);
    } catch (error) {
      console.error('Failed to sync order:', error);
    }
  }
}
```

### Push Notifications

#### Registration
```typescript
// Register for push notifications
async function subscribeToPushNotifications(orderId: number) {
  if ('serviceWorker' in navigator && 'PushManager' in window) {
    const registration = await navigator.serviceWorker.ready;
    
    const subscription = await registration.pushManager.subscribe({
      userVisibleOnly: true,
      applicationServerKey: VAPID_PUBLIC_KEY
    });
    
    // Send subscription to server
    await fetch('/api/v1/notifications/subscribe', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        subscription,
        order_id: orderId
      })
    });
  }
}
```

#### Push Event Handling
```javascript
// Handle push notifications
self.addEventListener('push', (event) => {
  const data = event.data.json();
  
  const options = {
    body: data.message,
    icon: '/icons/icon-192x192.png',
    badge: '/icons/badge-72x72.png',
    tag: `order-${data.order_id}`,
    data: {
      order_id: data.order_id,
      url: `/order/${data.order_id}`
    },
    actions: [
      {
        action: 'view',
        title: 'View Order',
        icon: '/icons/view-icon.png'
      }
    ]
  };
  
  event.waitUntil(
    self.registration.showNotification(data.title, options)
  );
});
```

### Offline Functionality

#### Menu Caching
```typescript
// Cache menu data for offline access
const MENU_CACHE_KEY = 'menu-data-v1';

async function cacheMenuData() {
  try {
    const response = await fetch('/api/v1/categories');
    const menuData = await response.json();
    
    localStorage.setItem(MENU_CACHE_KEY, JSON.stringify({
      data: menuData,
      timestamp: Date.now()
    }));
  } catch (error) {
    console.error('Failed to cache menu data:', error);
  }
}

async function getMenuData() {
  try {
    // Try network first
    const response = await fetch('/api/v1/categories');
    if (response.ok) {
      const data = await response.json();
      cacheMenuData();
      return data;
    }
  } catch (error) {
    // Fallback to cache
    const cached = localStorage.getItem(MENU_CACHE_KEY);
    if (cached) {
      const { data } = JSON.parse(cached);
      return data;
    }
  }
  
  throw new Error('Menu data unavailable');
}
```

#### Order Queue Management
```typescript
// Queue orders when offline
interface QueuedOrder {
  id: string;
  orderData: CreateOrderRequest;
  timestamp: number;
  retryCount: number;
}

class OrderQueue {
  private queue: QueuedOrder[] = [];
  
  async addOrder(orderData: CreateOrderRequest): Promise<string> {
    const queuedOrder: QueuedOrder = {
      id: generateUniqueId(),
      orderData,
      timestamp: Date.now(),
      retryCount: 0
    };
    
    this.queue.push(queuedOrder);
    this.saveQueue();
    
    // Try to sync immediately
    this.syncOrders();
    
    return queuedOrder.id;
  }
  
  async syncOrders(): Promise<void> {
    if (!navigator.onLine) return;
    
    const pendingOrders = [...this.queue];
    
    for (const order of pendingOrders) {
      try {
        await this.submitOrder(order);
        this.removeOrder(order.id);
      } catch (error) {
        order.retryCount++;
        if (order.retryCount >= 3) {
          this.removeOrder(order.id);
        }
      }
    }
    
    this.saveQueue();
  }
}
```

### Web App Manifest
```json
{
  "name": "FoodOrder - Vietnamese Restaurant",
  "short_name": "FoodOrder",
  "description": "Order Vietnamese food for table service or delivery",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#ffffff",
  "theme_color": "#F97316",
  "orientation": "portrait-primary",
  "icons": [
    {
      "src": "/icons/icon-72x72.png",
      "sizes": "72x72",
      "type": "image/png",
      "purpose": "maskable any"
    },
    {
      "src": "/icons/icon-96x96.png",
      "sizes": "96x96",
      "type": "image/png",
      "purpose": "maskable any"
    },
    {
      "src": "/icons/icon-128x128.png",
      "sizes": "128x128",
      "type": "image/png",
      "purpose": "maskable any"
    },
    {
      "src": "/icons/icon-144x144.png",
      "sizes": "144x144",
      "type": "image/png",
      "purpose": "maskable any"
    },
    {
      "src": "/icons/icon-152x152.png",
      "sizes": "152x152",
      "type": "image/png",
      "purpose": "maskable any"
    },
    {
      "src": "/icons/icon-192x192.png",
      "sizes": "192x192",
      "type": "image/png",
      "purpose": "maskable any"
    },
    {
      "src": "/icons/icon-384x384.png",
      "sizes": "384x384",
      "type": "image/png",
      "purpose": "maskable any"
    },
    {
      "src": "/icons/icon-512x512.png",
      "sizes": "512x512",
      "type": "image/png",
      "purpose": "maskable any"
    }
  ],
  "categories": ["food", "business"],
  "lang": "vi",
  "dir": "ltr"
}
```

---

## Deployment Strategy

### Environment Configuration

#### Development Environment
- **Local Development**: Next.js dev server + FastAPI uvicorn
- **Database**: Local PostgreSQL or Docker container
- **Caching**: Local Redis instance
- **File Storage**: Local filesystem

#### Staging Environment
- **Frontend**: Vercel or Netlify deployment
- **Backend**: Docker containers on staging server
- **Database**: Staging PostgreSQL instance
- **Caching**: Redis cluster
- **File Storage**: Cloud storage (S3/GCS)

#### Production Environment
- **Frontend**: CDN-distributed static assets
- **Backend**: Load-balanced FastAPI instances
- **Database**: Production PostgreSQL with replication
- **Caching**: Redis cluster with persistence
- **File Storage**: CDN-backed cloud storage
- **Monitoring**: Application performance monitoring

### Deployment Pipeline

#### CI/CD Workflow
```yaml
# GitHub Actions workflow
name: Deploy FoodOrder PWA

on:
  push:
    branches: [main, staging]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: npm ci
      - run: npm run test
      - run: npm run build
      - run: npm run lint

  deploy-staging:
    if: github.ref == 'refs/heads/staging'
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to staging
        run: |
          # Deploy to staging environment
          
  deploy-production:
    if: github.ref == 'refs/heads/main'
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to production
        run: |
          # Deploy to production environment
```

#### Infrastructure as Code
```dockerfile
# Frontend Dockerfile
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/out /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

```dockerfile
# Backend Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Performance Optimization

#### Frontend Optimization
- **Image Optimization**: Next.js Image component with WebP
- **Code Splitting**: Route-based and component-based splitting
- **Bundle Analysis**: Regular bundle size monitoring
- **Caching**: Aggressive caching for static assets
- **Compression**: Gzip/Brotli compression for all assets

#### Backend Optimization
- **Database Indexing**: Optimize queries with proper indexes
- **Caching**: Redis for frequently accessed data
- **Connection Pooling**: Database connection optimization
- **Load Balancing**: Multiple FastAPI instances
- **Rate Limiting**: Prevent abuse and ensure stability

### Monitoring & Analytics

#### Application Monitoring
- **Error Tracking**: Sentry for error monitoring
- **Performance**: New Relic or DataDog for APM
- **Uptime**: UptimeRobot for service availability
- **Logs**: Centralized logging with ELK stack

#### Business Analytics
- **Order Analytics**: Track conversion rates and order patterns
- **User Behavior**: Heat maps and user journey analysis
- **Performance Metrics**: Load times and user satisfaction
- **A/B Testing**: Feature flag management for experiments

### Security Considerations

#### Application Security
- **HTTPS**: Force SSL/TLS for all connections
- **Content Security Policy**: Prevent XSS attacks
- **Input Validation**: Sanitize all user inputs
- **Rate Limiting**: Prevent abuse and DDoS
- **Authentication**: Secure JWT token management

#### Infrastructure Security
- **Network Security**: VPC with proper firewall rules
- **Database Security**: Encrypted connections and data
- **Secrets Management**: Secure environment variable handling
- **Regular Updates**: Keep all dependencies updated
- **Backup Strategy**: Regular database and file backups

---

## Conclusion

This comprehensive planning document provides a complete roadmap for developing the FoodOrder PWA, from initial concept through production deployment. The modular architecture, detailed technical specifications, and phased development approach ensure a successful implementation that meets both customer needs and business requirements.

The integration with Odoo 18 POS through a FastAPI bridge provides flexibility while leveraging existing restaurant infrastructure. The PWA features ensure a modern, app-like experience that works reliably even with poor network connectivity.

Key success factors include:
- **User-Centric Design**: Focus on mobile-first, intuitive interface
- **Technical Excellence**: Modern architecture with offline capabilities
- **Business Integration**: Seamless Odoo POS workflow integration
- **Performance**: Fast, reliable operation under all conditions
- **Scalability**: Architecture that grows with business needs

This plan serves as the foundation for development, ensuring all stakeholders have a clear understanding of the project scope, technical approach, and expected outcomes.