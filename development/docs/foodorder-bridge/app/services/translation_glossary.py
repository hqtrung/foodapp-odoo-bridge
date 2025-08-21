"""
Vietnamese Food Translation Glossary

This module provides specialized translation handling for Vietnamese food terms
to ensure culturally appropriate and recognizable translations.
"""

from typing import Dict, List, Optional
import re


class VietnameseFoodGlossary:
    """Handles special Vietnamese food terms that need custom translation"""
    
    def __init__(self):
        # Vietnamese food terms to keep in original form (internationally recognized)
        self.preserve_terms = {
            'phở': 'pho',
            'bánh mì': 'banh mi', 
            'bánh cuốn': 'banh cuon',
            'bánh xèo': 'banh xeo',
            'bún chả': 'bun cha',
            'bún bò huế': 'bun bo hue',
            'bánh chưng': 'banh chung',
            'chả cá': 'cha ca',
            'nem nướng': 'nem nuong',
            'bánh tét': 'banh tet',
        }
        
        # Direct translations for specific Vietnamese food terms
        self.food_translations = {
            'en': {
                'cà phê sữa đá': 'Vietnamese Iced Coffee',
                'cà phê đá': 'Vietnamese Black Iced Coffee',
                'cà phê sữa': 'Vietnamese Coffee with Milk',
                'trà đá': 'Iced Tea',
                'nước mía': 'Sugarcane Juice',
                'nước dừa': 'Coconut Water',
                'sữa chua': 'Vietnamese Yogurt',
                'chè': 'Vietnamese Sweet Soup',
                'xôi': 'Sticky Rice',
                'cơm': 'Rice',
                'gỏi cuốn': 'Fresh Spring Rolls',
                'chả giò': 'Fried Spring Rolls',
                'nem rán': 'Fried Spring Rolls',
                'bánh căn': 'Vietnamese Mini Pancakes',
                'mì quảng': 'Quang Style Noodles',
                'cao lầu': 'Cao Lau Noodles',
                'hủ tiếu': 'Hu Tieu Noodles',
                'bún riêu': 'Crab Noodle Soup',
                'canh chua': 'Sour Soup',
                'thịt nướng': 'Grilled Meat',
                'gà nướng': 'Grilled Chicken',
                'heo nướng': 'Grilled Pork',
                'tôm nướng': 'Grilled Shrimp',
                'cá nướng': 'Grilled Fish',
                'lẩu': 'Hot Pot',
                'bánh tráng nướng': 'Grilled Rice Paper',
                'bánh bèo': 'Vietnamese Water Fern Cakes',
                'bánh khọt': 'Vietnamese Mini Savory Pancakes',
                'thập cẩm': 'Mixed/Combination',
                'đặc biệt': 'Special',
                'combo': 'Combo Set',
                'set': 'Set Menu',
                'đồ uống': 'Beverages',
                'nước uống': 'Drinks',
                'món chính': 'Main Dishes',
                'món phụ': 'Side Dishes',
                'khai vị': 'Appetizers',
                'tráng miệng': 'Desserts',
                'bia': 'Beer',
                'rượu': 'Wine/Alcohol',
                'nước ngọt': 'Soft Drinks',
                'nước suối': 'Bottled Water',
                'đá': 'Ice',
                'chanh': 'Lime',
                'sữa': 'Milk',
                'đường': 'Sugar',
                'muối': 'Salt',
                'tiêu': 'Pepper',
                'tỏi': 'Garlic',
                'hành': 'Onion',
                'rau': 'Vegetables',
                'salad': 'Salad',
                'trứng': 'Egg',
                'pate': 'Pate',
                'chà bông': 'Pork Floss',
                'giá': 'Bean Sprouts',
                'dưa chua': 'Pickled Vegetables',
                'nấm': 'Mushroom',
                'chay': 'Vegetarian',
                'không thịt': 'No Meat',
                'cay': 'Spicy',
                'không cay': 'Not Spicy',
                'ít cay': 'Mild Spicy',
                'rất cay': 'Very Spicy',
                'nóng': 'Hot',
                'lạnh': 'Cold',
                'tươi': 'Fresh',
                'khô': 'Dried',
                'chiên': 'Fried',
                'luộc': 'Boiled',
                'xào': 'Stir-fried',
                'nướng': 'Grilled',
                'hấp': 'Steamed',
                'rim': 'Braised',
                'kho': 'Caramelized',
                'chua ngọt': 'Sweet and Sour',
                'ngọt': 'Sweet',
                'chua': 'Sour',
                'mặn': 'Salty',
                'đắng': 'Bitter',
                'béo': 'Rich/Fatty',
                'thơm': 'Fragrant',
                'giòn': 'Crispy',
                'mềm': 'Soft',
                'dai': 'Chewy',
                'size nhỏ': 'Small Size',
                'size vừa': 'Medium Size', 
                'size lớn': 'Large Size',
                'chai': 'Bottle',
                'lon': 'Can',
                'ly': 'Glass',
                'tô': 'Bowl',
                'đĩa': 'Plate',
                'phần': 'Portion',
                'suất': 'Serving',
                'bánh mì không': 'Plain Bread',
                'không': 'Plain',
            },
            'zh': {
                'cà phê sữa đá': '越南冰奶咖啡',
                'cà phê đá': '越南冰黑咖啡', 
                'cà phê sữa': '越南奶咖啡',
                'trà đá': '冰茶',
                'nước mía': '甘蔗汁',
                'nước dừa': '椰子水',
                'sữa chua': '越南酸奶',
                'chè': '越南甜汤',
                'xôi': '糯米饭',
                'cơm': '米饭',
                'gỏi cuốn': '鲜春卷',
                'chả giò': '炸春卷',
                'nem rán': '炸春卷',
                'mì quảng': '广式面条',
                'hủ tiếu': '河粉',
                'bún riêu': '蟹肉面条汤',
                'canh chua': '酸汤',
                'thịt nướng': '烤肉',
                'gà nướng': '烤鸡',
                'heo nướng': '烤猪肉',
                'tôm nướng': '烤虾',
                'cá nướng': '烤鱼',
                'lẩu': '火锅',
                'thập cẩm': '混合/拼盘',
                'đặc biệt': '特色',
                'combo': '套餐',
                'set': '套餐',
                'đồ uống': '饮料',
                'nước uống': '饮品',
                'món chính': '主菜',
                'món phụ': '配菜',
                'khai vị': '开胃菜',
                'tráng miệng': '甜点',
                'bia': '啤酒',
                'rượu': '酒',
                'nước ngọt': '软饮',
                'nước suối': '矿泉水',
                'salad': '沙拉',
                'trứng': '鸡蛋',
                'pate': '肉酱',
                'chà bông': '肉松',
                'rau': '蔬菜',
                'nấm': '蘑菇',
                'chay': '素食',
                'cay': '辣',
                'nóng': '热',
                'lạnh': '冷',
                'tươi': '新鲜',
                'chiên': '炸',
                'luộc': '水煮',
                'xào': '炒',
                'nướng': '烤',
                'hấp': '蒸',
                'kho': '焖',
                'ngọt': '甜',
                'chua': '酸',
                'mặn': '咸',
                'size nhỏ': '小份',
                'size vừa': '中份',
                'size lớn': '大份',
                'chai': '瓶',
                'lon': '罐',
                'ly': '杯',
                'tô': '碗',
            },
            'zh-TW': {
                'cà phê sữa đá': '越南冰奶咖啡',
                'cà phê đá': '越南冰黑咖啡',
                'cà phê sữa': '越南奶咖啡',
                'trà đá': '冰茶',
                'nước mía': '甘蔗汁',
                'nước dừa': '椰子水',
                'sữa chua': '越南優格',
                'chè': '越南甜湯',
                'xôi': '糯米飯',
                'cơm': '米飯',
                'gỏi cuốn': '鮮春捲',
                'chả giò': '炸春捲',
                'nem rán': '炸春捲',
                'mì quảng': '廣式麵條',
                'hủ tiếu': '河粉',
                'bún riêu': '蟹肉麵條湯',
                'canh chua': '酸湯',
                'thịt nướng': '烤肉',
                'gà nướng': '烤雞',
                'heo nướng': '烤豬肉',
                'tôm nướng': '烤蝦',
                'cá nướng': '烤魚',
                'lẩu': '火鍋',
                'thập cẩm': '混合/拼盤',
                'đặc biệt': '特色',
                'combo': '套餐',
                'set': '套餐',
                'đồ uống': '飲料',
                'nước uống': '飲品',
                'món chính': '主菜',
                'món phụ': '配菜',
                'khai vị': '開胃菜',
                'tráng miệng': '甜點',
                'bia': '啤酒',
                'rượu': '酒',
                'nước ngọt': '軟飲',
                'nước suối': '礦泉水',
                'salad': '沙拉',
                'trứng': '雞蛋',
                'pate': '肉醬',
                'chà bông': '肉鬆',
                'rau': '蔬菜',
                'nấm': '蘑菇',
                'chay': '素食',
                'cay': '辣',
                'nóng': '熱',
                'lạnh': '冷',
                'tươi': '新鮮',
                'chiên': '炸',
                'luộc': '水煮',
                'xào': '炒',
                'nướng': '烤',
                'hấp': '蒸',
                'kho': '燜',
                'ngọt': '甜',
                'chua': '酸',
                'mặn': '鹹',
                'size nhỏ': '小份',
                'size vừa': '中份',
                'size lớn': '大份',
                'chai': '瓶',
                'lon': '罐',
                'ly': '杯',
                'tô': '碗',
            },
            'th': {
                'cà phê sữa đá': 'กาแฟเย็นเวียดนาม',
                'cà phê đá': 'กาแฟดำเย็นเวียดนาม',
                'cà phê sữa': 'กาแฟนมเวียดนาม',
                'trà đá': 'ชาเย็น',
                'nước mía': 'น้ำอ้อย',
                'nước dừa': 'น้ำมะพร้าว',
                'sữa chua': 'โยเกิร์ตเวียดนาม',
                'chè': 'ขนมหวานเวียดนาม',
                'xôi': 'ข้าวเหนียว',
                'cơm': 'ข้าว',
                'gỏi cuốn': 'ปอเปี๊ยะสด',
                'chả giò': 'ปอเปี๊ยะทอด',
                'nem rán': 'ปอเปี๊ยะทอด',
                'mì quảng': 'ก๋วยเตี๋ยวมี่กวง',
                'hủ tiếu': 'ก๋วยเตี๋ยวหู้เตี๋ยว',
                'bún riêu': 'ก๋วยเตี๋ยวปู',
                'canh chua': 'ต้มยำ',
                'thịt nướng': 'เนื้อย่าง',
                'gà nướng': 'ไก่ย่าง',
                'heo nướng': 'หมูย่าง',
                'tôm nướng': 'กุ้งย่าง',
                'cá nướng': 'ปลาย่าง',
                'lẩu': 'สุกี้',
                'thập cẩm': 'รวมมิตร',
                'đặc biệt': 'พิเศษ',
                'combo': 'คอมโบ',
                'set': 'เซต',
                'đồ uống': 'เครื่องดื่ม',
                'nước uống': 'เครื่องดื่ม',
                'món chính': 'อาหารหลัก',
                'món phụ': 'อาหารเสริม',
                'khai vị': 'อาหารเรียกน้ำย่อย',
                'tráng miệng': 'ของหวาน',
                'bia': 'เบียร์',
                'rượu': 'เหล้า',
                'nước ngọt': 'น้ำอัดลม',
                'nước suối': 'น้ำดื่ม',
                'salad': 'สลัด',
                'trứng': 'ไข่',
                'pate': 'ปาเต้',
                'chà bông': 'หมูหยอง',
                'rau': 'ผัก',
                'nấm': 'เห็ด',
                'chay': 'มังสวิรัติ',
                'cay': 'เผ็ด',
                'nóng': 'ร้อน',
                'lạnh': 'เย็น',
                'tươi': 'สด',
                'chiên': 'ทอด',
                'luộc': 'ต้ม',
                'xào': 'ผัด',
                'nướng': 'ย่าง',
                'hấp': 'นึ่ง',
                'kho': 'เคี่ยว',
                'ngọt': 'หวาน',
                'chua': 'เปรี้ยว',
                'mặn': 'เค็ม',
                'size nhỏ': 'ไซส์เล็ก',
                'size vừa': 'ไซส์กลาง',
                'size lớn': 'ไซส์ใหญ่',
                'chai': 'ขวด',
                'lon': 'กระป่อง',
                'ly': 'แก้ว',
                'tô': 'ชาม',
            },
            'fr': {
                'cà phê sữa đá': 'Café glacé vietnamien au lait',
                'cà phê đá': 'Café noir glacé vietnamien',
                'cà phê sữa': 'Café vietnamien au lait',
                'trà đá': 'Thé glacé',
                'nước mía': 'Jus de canne à sucre',
                'nước dừa': 'Eau de coco',
                'sữa chua': 'Yaourt vietnamien',
                'chè': 'Dessert sucré vietnamien',
                'xôi': 'Riz gluant',
                'cơm': 'Riz',
                'gỏi cuốn': 'Rouleaux de printemps frais',
                'chả giò': 'Rouleaux de printemps frits',
                'nem rán': 'Rouleaux de printemps frits',
                'mì quảng': 'Nouilles style Quang',
                'hủ tiếu': 'Nouilles Hu Tieu',
                'bún riêu': 'Soupe de nouilles au crabe',
                'canh chua': 'Soupe aigre',
                'thịt nướng': 'Viande grillée',
                'gà nướng': 'Poulet grillé',
                'heo nướng': 'Porc grillé',
                'tôm nướng': 'Crevettes grillées',
                'cá nướng': 'Poisson grillé',
                'lẩu': 'Fondue vietnamienne',
                'thập cẩm': 'Mixte/Assortiment',
                'đặc biệt': 'Spécial',
                'combo': 'Menu combiné',
                'set': 'Menu fixe',
                'đồ uống': 'Boissons',
                'nước uống': 'Boissons',
                'món chính': 'Plats principaux',
                'món phụ': 'Accompagnements',
                'khai vị': 'Entrées',
                'tráng miệng': 'Desserts',
                'bia': 'Bière',
                'rượu': 'Alcool',
                'nước ngọt': 'Sodas',
                'nước suối': 'Eau minérale',
                'salad': 'Salade',
                'trứng': 'Œuf',
                'pate': 'Pâté',
                'chà bông': 'Porc effiloché',
                'rau': 'Légumes',
                'nấm': 'Champignon',
                'chay': 'Végétarien',
                'cay': 'Épicé',
                'nóng': 'Chaud',
                'lạnh': 'Froid',
                'tươi': 'Frais',
                'chiên': 'Frit',
                'luộc': 'Bouilli',
                'xào': 'Sauté',
                'nướng': 'Grillé',
                'hấp': 'Vapeur',
                'kho': 'Braisé',
                'ngọt': 'Sucré',
                'chua': 'Aigre',
                'mặn': 'Salé',
                'size nhỏ': 'Petite taille',
                'size vừa': 'Taille moyenne',
                'size lớn': 'Grande taille',
                'chai': 'Bouteille',
                'lon': 'Canette',
                'ly': 'Verre',
                'tô': 'Bol',
            },
            'it': {
                'cà phê sữa đá': 'Caffè vietnamita freddo con latte',
                'cà phê đá': 'Caffè nero vietnamita freddo',
                'cà phê sữa': 'Caffè vietnamita con latte',
                'trà đá': 'Tè freddo',
                'nước mía': 'Succo di canna da zucchero',
                'nước dừa': 'Acqua di cocco',
                'sữa chua': 'Yogurt vietnamita',
                'chè': 'Dolce vietnamita',
                'xôi': 'Riso glutinoso',
                'cơm': 'Riso',
                'gỏi cuốn': 'Involtini primavera freschi',
                'chả giò': 'Involtini primavera fritti',
                'nem rán': 'Involtini primavera fritti',
                'mì quảng': 'Noodles stile Quang',
                'hủ tiếu': 'Noodles Hu Tieu',
                'bún riêu': 'Zuppa di noodles al granchio',
                'canh chua': 'Zuppa agrodolce',
                'thịt nướng': 'Carne alla griglia',
                'gà nướng': 'Pollo alla griglia',
                'heo nướng': 'Maiale alla griglia',
                'tôm nướng': 'Gamberetti alla griglia',
                'cá nướng': 'Pesce alla griglia',
                'lẩu': 'Hot pot vietnamita',
                'thập cẩm': 'Misto/Assortito',
                'đặc biệt': 'Speciale',
                'combo': 'Menu combo',
                'set': 'Menu fisso',
                'đồ uống': 'Bevande',
                'nước uống': 'Bevande',
                'món chính': 'Piatti principali',
                'món phụ': 'Contorni',
                'khai vị': 'Antipasti',
                'tráng miệng': 'Dolci',
                'bia': 'Birra',
                'rượu': 'Alcolici',
                'nước ngọt': 'Bibite',
                'nước suối': 'Acqua minerale',
                'salad': 'Insalata',
                'trứng': 'Uovo',
                'pate': 'Paté',
                'chà bông': 'Maiale sfilacciato',
                'rau': 'Verdure',
                'nấm': 'Funghi',
                'chay': 'Vegetariano',
                'cay': 'Piccante',
                'nóng': 'Caldo',
                'lạnh': 'Freddo',
                'tươi': 'Fresco',
                'chiên': 'Fritto',
                'luộc': 'Bollito',
                'xào': 'Saltato',
                'nướng': 'Grigliato',
                'hấp': 'Al vapore',
                'kho': 'Brasato',
                'ngọt': 'Dolce',
                'chua': 'Aspro',
                'mặn': 'Salato',
                'size nhỏ': 'Taglia piccola',
                'size vừa': 'Taglia media',
                'size lớn': 'Taglia grande',
                'chai': 'Bottiglia',
                'lon': 'Lattina',
                'ly': 'Bicchiere',
                'tô': 'Ciotola',
            },
            'es': {
                'cà phê sữa đá': 'Café vietnamita helado con leche',
                'cà phê đá': 'Café negro vietnamita helado',
                'cà phê sữa': 'Café vietnamita con leche',
                'trà đá': 'Té helado',
                'nước mía': 'Jugo de caña de azúcar',
                'nước dừa': 'Agua de coco',
                'sữa chua': 'Yogur vietnamita',
                'chè': 'Postre dulce vietnamita',
                'xôi': 'Arroz glutinoso',
                'cơm': 'Arroz',
                'gỏi cuốn': 'Rollitos de primavera frescos',
                'chả giò': 'Rollitos de primavera fritos',
                'nem rán': 'Rollitos de primavera fritos',
                'mì quảng': 'Fideos estilo Quang',
                'hủ tiếu': 'Fideos Hu Tieu',
                'bún riêu': 'Sopa de fideos con cangrejo',
                'canh chua': 'Sopa agria',
                'thịt nướng': 'Carne asada',
                'gà nướng': 'Pollo asado',
                'heo nướng': 'Cerdo asado',
                'tôm nướng': 'Camarones asados',
                'cá nướng': 'Pescado asado',
                'lẩu': 'Hot pot vietnamita',
                'thập cẩm': 'Mixto/Combinado',
                'đặc biệt': 'Especial',
                'combo': 'Menú combo',
                'set': 'Menú fijo',
                'đồ uống': 'Bebidas',
                'nước uống': 'Bebidas',
                'món chính': 'Platos principales',
                'món phụ': 'Acompañamientos',
                'khai vị': 'Aperitivos',
                'tráng miệng': 'Postres',
                'bia': 'Cerveza',
                'rượu': 'Alcohol',
                'nước ngọt': 'Refrescos',
                'nước suối': 'Agua mineral',
                'salad': 'Ensalada',
                'trứng': 'Huevo',
                'pate': 'Paté',
                'chà bông': 'Cerdo desmenuzado',
                'rau': 'Verduras',
                'nấm': 'Setas',
                'chay': 'Vegetariano',
                'cay': 'Picante',
                'nóng': 'Caliente',
                'lạnh': 'Frío',
                'tươi': 'Fresco',
                'chiên': 'Frito',
                'luộc': 'Hervido',
                'xào': 'Salteado',
                'nướng': 'Asado',
                'hấp': 'Al vapor',
                'kho': 'Guisado',
                'ngọt': 'Dulce',
                'chua': 'Agrio',
                'mặn': 'Salado',
                'size nhỏ': 'Tamaño pequeño',
                'size vừa': 'Tamaño mediano',
                'size lớn': 'Tamaño grande',
                'chai': 'Botella',
                'lon': 'Lata',
                'ly': 'Vaso',
                'tô': 'Tazón',
            },
            'ja': {
                'cà phê sữa đá': 'ベトナムアイスミルクコーヒー',
                'cà phê đá': 'ベトナムアイスブラックコーヒー',
                'cà phê sữa': 'ベトナムミルクコーヒー',
                'trà đá': 'アイスティー',
                'nước mía': 'サトウキビジュース',
                'nước dừa': 'ココナッツウォーター',
                'sữa chua': 'ベトナムヨーグルト',
                'chè': 'ベトナム甘味',
                'xôi': 'もち米',
                'cơm': 'ご飯',
                'gỏi cuốn': '生春巻き',
                'chả giò': '揚げ春巻き',
                'nem rán': '揚げ春巻き',
                'mì quảng': 'クアン風麺',
                'hủ tiếu': 'フーティウ麺',
                'bún riêu': 'カニ麺スープ',
                'canh chua': 'サワースープ',
                'thịt nướng': '焼肉',
                'gà nướng': '焼き鳥',
                'heo nướng': '焼き豚',
                'tôm nướng': '焼きエビ',
                'cá nướng': '焼き魚',
                'lẩu': 'ベトナム鍋',
                'thập cẩm': 'ミックス/盛り合わせ',
                'đặc biệt': '特別',
                'combo': 'コンボセット',
                'set': 'セットメニュー',
                'đồ uống': '飲み物',
                'nước uống': '飲み物',
                'món chính': 'メイン料理',
                'món phụ': 'サイドディッシュ',
                'khai vị': '前菜',
                'tráng miệng': 'デザート',
                'bia': 'ビール',
                'rượu': 'お酒',
                'nước ngọt': 'ソフトドリンク',
                'nước suối': 'ミネラルウォーター',
                'salad': 'サラダ',
                'trứng': '卵',
                'pate': 'パテ',
                'chà bông': '豚でんぶ',
                'rau': '野菜',
                'nấm': 'キノコ',
                'chay': 'ベジタリアン',
                'cay': '辛い',
                'nóng': '熱い',
                'lạnh': '冷たい',
                'tươi': '新鮮',
                'chiên': '揚げ',
                'luộc': '茹で',
                'xào': '炒め',
                'nướng': '焼き',
                'hấp': '蒸し',
                'kho': '煮込み',
                'ngọt': '甘い',
                'chua': '酸っぱい',
                'mặn': '塩辛い',
                'size nhỏ': 'Sサイズ',
                'size vừa': 'Mサイズ',
                'size lớn': 'Lサイズ',
                'chai': 'ボトル',
                'lon': '缶',
                'ly': 'グラス',
                'tô': 'ボウル',
            }
        }
        
        # Brand names that should never be translated
        self.brand_names = {
            'coca cola', 'pepsi', 'sprite', '7up', 'fanta', 'aquafina', 
            'lavie', 'dasani', 'evian', 'perrier', 'san pellegrino',
            'redbull', 'monster', 'rockstar', 'sting', 'number 1',
            'heineken', 'tiger', 'saigon', 'bia saigon', 'hanoi beer',
            'budweiser', 'corona', 'stella artois', 'carlsberg',
            'lipton', 'nestea', 'arizona', 'snapple',
            'starbucks', 'highlands', 'trung nguyen', 'g7',
        }
        
        # Product codes that should be preserved (A1, B2, C3, etc.)
        self.code_pattern = re.compile(r'\([A-Z]\d+\)|\[A-Z]\d+\]|^[A-Z]\d+[\.:]?')
        
    def preprocess_text(self, text: str, target_language: str) -> str:
        """
        Preprocess Vietnamese text before translation to handle special cases
        
        Args:
            text: Original Vietnamese text
            target_language: Target language code
            
        Returns:
            Preprocessed text ready for translation
        """
        if not text:
            return text
            
        # Convert to lowercase for matching but preserve original case
        text_lower = text.lower()
        
        # Check for brand names that should not be translated
        for brand in self.brand_names:
            if brand in text_lower:
                # Keep brand names in original form
                pass
                
        # Apply direct translations from glossary if available
        if target_language in self.food_translations:
            translations = self.food_translations[target_language]
            
            # Replace Vietnamese terms with direct translations
            for vi_term, translation in translations.items():
                if vi_term in text_lower:
                    # Use case-insensitive replacement
                    pattern = re.compile(re.escape(vi_term), re.IGNORECASE)
                    text = pattern.sub(translation, text)
                    
        return text
        
    def postprocess_text(self, original_text: str, translated_text: str, target_language: str) -> str:
        """
        Postprocess translated text to fix common issues
        
        Args:
            original_text: Original Vietnamese text
            translated_text: Translated text from API
            target_language: Target language code
            
        Returns:
            Postprocessed translated text
        """
        if not translated_text:
            return translated_text
            
        # Preserve product codes from original text
        codes = self.code_pattern.findall(original_text)
        if codes:
            # If translation lost the product code, add it back at the beginning
            if not any(code in translated_text for code in codes):
                translated_text = f"{codes[0]} {translated_text}"
                
        # Preserve internationally recognized Vietnamese terms
        original_lower = original_text.lower()
        for vi_term, preserved_form in self.preserve_terms.items():
            if vi_term in original_lower:
                # Replace any translation of these terms with the preserved form
                # This handles cases where the API might translate "phở" to "noodle soup"
                translated_text = self._preserve_vietnamese_terms(translated_text, preserved_form, target_language)
                
        # Handle brand name preservation
        for brand in self.brand_names:
            if brand in original_text.lower():
                # Ensure brand names remain in original form
                pass
                
        return translated_text.strip()
        
    def _preserve_vietnamese_terms(self, text: str, preserved_term: str, target_language: str) -> str:
        """Helper method to preserve Vietnamese food terms in translations"""
        # This is a simplified approach - in a full implementation,
        # you might want to use more sophisticated pattern matching
        common_mistranslations = {
            'en': {
                'noodle soup': preserved_term,
                'noodles': preserved_term,
                'soup': preserved_term,
                'sandwich': preserved_term if 'banh mi' in preserved_term else text,
            }
        }
        
        if target_language in common_mistranslations:
            for mistake, correction in common_mistranslations[target_language].items():
                if mistake in text.lower():
                    text = text.lower().replace(mistake, correction)
                    
        return text
        
    def get_supported_languages(self) -> List[str]:
        """Get list of languages with specialized Vietnamese food translations"""
        return list(self.food_translations.keys())
        
    def has_specialized_translation(self, text: str, target_language: str) -> bool:
        """Check if text contains terms that have specialized translations"""
        if target_language not in self.food_translations:
            return False
            
        text_lower = text.lower()
        for term in self.food_translations[target_language].keys():
            if term in text_lower:
                return True
                
        return False