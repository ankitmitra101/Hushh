import sys
import os
import json
import re

# Mocking the environment
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "..", "data"))

def _safe_load(filename, default=[]):
    path = os.path.join(DATA_DIR, filename)
    print(f"Loading data from: {path}")
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {filename}: {e}")
        return default

def search_products(query: str, budget_max: int = 10000, avoid_keywords: any = None, category: str = None, size: str = None):
    print(f"Running Search: Query='{query}', Category='{category}', Size='{size}'")
    products = _safe_load("catalog.json")
    
    # Standardize exclusion list
    if isinstance(avoid_keywords, str):
        avoid_list = avoid_keywords.lower().split()
    elif isinstance(avoid_keywords, list):
        avoid_list = " ".join([str(i) for i in avoid_keywords]).lower().split()
    else:
        avoid_list = []

    # Category synonym mapping
    CATEGORY_MAP = {
        "sneakers": "footwear", "sneaker": "footwear", "shoes": "footwear",
        "shoe": "footwear", "boots": "footwear", "sandals": "footwear",
        "loafers": "footwear", "footwear": "footwear",
        "shirts": "apparel", "shirt": "apparel", "t-shirts": "apparel",
        "t-shirt": "apparel", "tee": "apparel", "tees": "apparel",
        "pants": "apparel", "jeans": "apparel", "clothes": "apparel",
        "clothing": "apparel", "apparel": "apparel",
        "sunglasses": "accessories", "belts": "accessories", "bags": "accessories",
        "watches": "accessories", "accessories": "accessories"
    }
    
    normalized_category = None
    if category:
        cat_lower = category.lower().strip()
        normalized_category = CATEGORY_MAP.get(cat_lower, cat_lower)
    
    query_words = [w.lower() for w in query.split()]
    results = []

    for p in products:
        title = p.get('title', "").lower()
        keywords = [k.lower() for k in p.get('style_keywords', [])]
        price = p.get('price_inr', 0)
        
        product_category = p.get('category', "").lower()
        product_sub_category = p.get('sub_category', "").lower()
        product_size = str(p.get('size', "")).lower()
        product_material = p.get('material', "").lower()
        
        # 1. STRICT CATEGORY FILTER
        if normalized_category and product_category != normalized_category:
            continue
        
        # 2. SIZE FILTER
        if size:
            # Handle multiple sizes
            requested_sizes = [s.strip().lower() for s in re.split(r'[,|/]+|\s+and\s+|\s+or\s+', str(size)) if s.strip()]
            
            if requested_sizes:
                if product_size not in requested_sizes:
                    continue
        
        # 3. EXCLUSION CHECK
        all_text = f"{title} {product_sub_category} {product_material} {' '.join(keywords)}"
        is_excluded = any(word in avoid_list for word in all_text.split()) # IMPROVED: split text to avoid partial matches
        if is_excluded:
            continue
            
        # 4. STRICT COLOR FILTER
        COMMON_COLORS = {"white", "black", "red", "blue", "green", "yellow", "pink", "purple", "brown", "grey", "gray", "beige", "gold", "silver"}
        query_colors = [w for w in query_words if w in COMMON_COLORS]
        
        if query_colors:
            has_color = any(c in all_text for c in query_colors)
            if not has_color:
                continue

        # 5. MATCH SCORE
        match_score = 0
        if normalized_category and product_category == normalized_category:
            match_score += 10
        
        for word in query_words:
            if word in ["i", "want", "need", "looking", "for", "a", "an", "the", "some", "show", "me", "of", "size"]: # Added 'of', 'size'
                continue
            if word in title:
                match_score += 3
            if word in product_sub_category:
                match_score += 2
            for kw in keywords:
                if word in kw:
                    match_score += 1
        
        if match_score > 0 and price <= budget_max:
            results.append({**p, '_score': match_score})
    
    print(f"Found {len(results)} results")
    return results

if __name__ == "__main__":
    # Test cases representing potential failure modes
    print("--- Test 1: Query with explicit size arg ---")
    search_products(query="white sneakers", size="9", category="footwear")
    
    print("\n--- Test 2: Query with size in text, size arg is '9' ---")
    search_products(query="white sneakers of size 9", size="9", category="footwear")

    print("\n--- Test 3: Query with size in text, size arg is None (LLM failure to extract) ---")
    search_products(query="white sneakers of size 9", size=None, category="footwear")
