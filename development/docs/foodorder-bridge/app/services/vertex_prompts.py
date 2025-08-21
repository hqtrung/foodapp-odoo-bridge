"""
Specialized prompts for Vietnamese food translation using Vertex AI
"""

def get_product_translation_prompt(target_language: str, target_country: str = None) -> str:
    """
    Get specialized prompt for product translation
    
    Args:
        target_language: Target language name (e.g., "English", "French")
        target_country: Target country for localization (optional)
    
    Returns:
        Formatted prompt template
    """
    country_context = f" in {target_country}" if target_country else ""
    
    return f"""You are a specialized translator for a Vietnamese Banh Mi restaurant chain.

Restaurant Context:
- Fast-food Vietnamese sandwich (Banh Mi) restaurant
- Menu includes traditional Vietnamese items and modern fusion
- Target audience: International customers{country_context}
- Brand voice: Friendly, authentic, appetizing

Translation Requirements:
1. Product codes (A1, B2, C3) must be preserved exactly
2. Keep "Banh Mi" unchanged as it's internationally recognized
3. For ingredients:
   - Pate → Pâté (French markets) or Pate (others)
   - Xá xíu → Char siu/BBQ pork
   - Chả lụa → Vietnamese ham
   - Đồ chua → Pickled vegetables
4. Maintain appetizing descriptions
5. Use culinary terms familiar to {target_language} speakers

Products to translate:
{{products_json}}

Return a JSON object with translated names and descriptions.
"""


def get_topping_translation_prompt(target_language: str) -> str:
    """
    Get specialized prompt for topping/attribute translation
    
    Args:
        target_language: Target language name
        
    Returns:
        Formatted prompt template
    """
    return f"""Translate these Vietnamese food toppings/options for a Banh Mi menu.

Context: These are customization options customers can add to their sandwiches.

Guidelines:
- Use common culinary terms in {target_language}
- Keep it concise (toppings are displayed as checkboxes/radio buttons)
- Preserve pricing indicators
- Make it appetizing and clear

Toppings to translate:
{{toppings_json}}

Return JSON with translated topping names.
"""


def get_category_translation_prompt(target_language: str) -> str:
    """
    Get specialized prompt for category translation
    
    Args:
        target_language: Target language name
        
    Returns:
        Formatted prompt template
    """
    return f"""Translate these Vietnamese food menu categories for a Banh Mi restaurant.

Context: These are main menu sections that help customers navigate the menu.

Guidelines:
- Use clear, appetizing category names in {target_language}
- Keep the essence of Vietnamese cuisine identity
- Make it easy for international customers to understand
- Use restaurant industry standard terminology

Categories to translate:
{{categories_json}}

Return JSON with translated category names and descriptions.
"""


# Vietnamese food term mappings for better context
VIETNAMESE_FOOD_TERMS = {
    "banh_mi": {
        "keep_original": True,
        "description": "Vietnamese sandwich with baguette bread"
    },
    "pho": {
        "keep_original": True,
        "description": "Vietnamese noodle soup"
    },
    "nem": {
        "keep_original": True,
        "description": "Vietnamese spring rolls"
    },
    "cha_lua": {
        "translations": {
            "en": "Vietnamese ham",
            "fr": "Jambon vietnamien",
            "es": "Jamón vietnamita",
            "it": "Prosciutto vietnamita",
            "zh": "越南火腿",
            "zh-TW": "越南火腿",
            "th": "แฮมเวียดนาม",
            "ja": "ベトナムハム"
        }
    },
    "xa_xiu": {
        "translations": {
            "en": "BBQ pork",
            "fr": "Porc BBQ",
            "es": "Cerdo a la barbacoa",
            "it": "Maiale BBQ",
            "zh": "叉烧",
            "zh-TW": "叉燒",
            "th": "หมูแดง",
            "ja": "チャーシュー"
        }
    },
    "do_chua": {
        "translations": {
            "en": "Pickled vegetables",
            "fr": "Légumes marinés",
            "es": "Verduras encurtidas",
            "it": "Verdure sottaceto",
            "zh": "腌菜",
            "zh-TW": "醃菜",
            "th": "ผักดอง",
            "ja": "ピクルス"
        }
    },
    "pate": {
        "translations": {
            "en": "Pâté",
            "fr": "Pâté",
            "es": "Paté",
            "it": "Paté",
            "zh": "肝酱",
            "zh-TW": "肝醬",
            "th": "ปาเต้",
            "ja": "パテ"
        }
    }
}


def get_enhanced_translation_prompt(items, target_language: str, source_language: str = 'vi', context_type: str = 'general') -> str:
    """
    Create enhanced translation prompt with Vietnamese food context
    
    Args:
        items: List of items to translate
        target_language: Target language name
        source_language: Source language name
        context_type: Type of content (product, category, topping, etc.)
        
    Returns:
        Enhanced prompt with food context
    """
    
    # Context-specific instructions
    context_instructions = {
        'product': """
- Focus on making items sound appetizing and authentic
- Emphasize fresh ingredients and traditional preparation methods
- Use descriptive language that makes customers want to try the item
        """,
        'category': """
- Use clear, navigational language
- Help customers understand what type of food is in each section
- Make it easy to browse the menu
        """,
        'topping': """
- Use short, clear names (space is limited in UI)
- Focus on the key characteristic of each topping
- Make add-on options sound appealing
        """,
        'attribute': """
- Clear option descriptions
- Help customers make informed choices
- Maintain consistency in terminology
        """
    }
    
    specific_instructions = context_instructions.get(context_type, context_instructions['product'])
    
    # Enhanced Vietnamese food context with specific instructions
    food_context = """
CRITICAL VIETNAMESE BÁNH MÌ RESTAURANT TRANSLATION RULES:
- This is a Vietnamese Bánh Mì (Baguette) Restaurant
- Do NOT translate "Bánh Mì" as "Sandwich" - prefer "Baguette" and translate from "Baguette" concept
- "Bánh Mì Pate Trứng Double" = "Baguette with Pâté and Eggs"
- "Thập cẩm" = "Mixed Meat" (not "assorted" or "combination")

SPECIFIC FOOD TERM TRANSLATIONS:
- Bánh Mì → Keep as "Bánh Mì" or use "Baguette" concept if translation needed
- Pate → "Pâté" (with accent)
- Trứng → "Eggs"
- Thập cẩm → "Mixed Meat"
- Chả lụa → "Vietnamese ham" or "Pork roll"
- Xá xíu → "Char siu" or "BBQ pork"
- Đồ chua → "Pickled vegetables"
- Rau thơm → "Fresh herbs"
- Thịt nướng → "Grilled pork"
- Gà nướng → "Grilled chicken"
"""
    
    prompt = f"""You are a professional translator specializing in Vietnamese cuisine and restaurant menus.

Context: This is the translation for Vietnamese Bánh Mì (Baguette) Restaurant menu from {source_language} to {target_language}.

{food_context}

Content Type: {context_type.title()}
{specific_instructions}

Translation Guidelines:
1. Preserve product codes exactly: (A1), (B2), (C3), etc.
2. Keep brand names unchanged: Coca Cola, Pepsi, etc.
3. Maintain Vietnamese baguette restaurant authenticity and cultural identity
4. Use appetizing, professional restaurant language
5. Be consistent with Vietnamese culinary terminology
6. Focus on baguette concept rather than sandwich concept

Please translate the following Vietnamese baguette restaurant items to {target_language}.

Return ONLY a valid JSON object with this structure:
{{
  "translations": [
    {{
      "id": "item_id",
      "translated_text": "translated text here"
    }}
  ]
}}

Items to translate:
"""
    
    # Add items to the prompt
    for item in items:
        item_type = item.get('type', context_type)
        prompt += f'\n- ID: {item["id"]}, Type: {item_type}, Text: "{item["text"]}"'
    
    return prompt


# Language-specific customizations
LANGUAGE_CUSTOMIZATIONS = {
    'en': {
        'currency_symbol': '$',
        'decimal_separator': '.',
        'date_format': 'MM/DD/YYYY',
        'food_style': 'American casual dining terminology'
    },
    'fr': {
        'currency_symbol': '€',
        'decimal_separator': ',',
        'date_format': 'DD/MM/YYYY',
        'food_style': 'French culinary terminology, maintain food authenticity'
    },
    'es': {
        'currency_symbol': '€',
        'decimal_separator': ',',
        'date_format': 'DD/MM/YYYY',
        'food_style': 'Spanish casual dining terminology'
    },
    'it': {
        'currency_symbol': '€',
        'decimal_separator': ',',
        'date_format': 'DD/MM/YYYY',
        'food_style': 'Italian culinary terminology, emphasize fresh ingredients'
    },
    'zh': {
        'currency_symbol': '¥',
        'decimal_separator': '.',
        'date_format': 'YYYY/MM/DD',
        'food_style': 'Chinese culinary terminology, familiar Asian food terms'
    },
    'zh-TW': {
        'currency_symbol': 'NT$',
        'decimal_separator': '.',
        'date_format': 'YYYY/MM/DD',
        'food_style': 'Traditional Chinese culinary terminology'
    },
    'th': {
        'currency_symbol': '฿',
        'decimal_separator': '.',
        'date_format': 'DD/MM/YYYY',
        'food_style': 'Thai culinary terminology, Southeast Asian context'
    },
    'ja': {
        'currency_symbol': '¥',
        'decimal_separator': '.',
        'date_format': 'YYYY/MM/DD',
        'food_style': 'Japanese culinary terminology, familiar Asian concepts'
    }
}