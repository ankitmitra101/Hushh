import sys
import json
import os
import asyncio
from typing import Optional
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP
mcp = FastMCP("Shopping Assistant")

# Absolute path calculation to ensure data files are always found regardless of execution context
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "..", "data"))

def _safe_load(filename, default=[]):
    """Safely loads JSON data from the data directory."""
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        print(f"[DEBUG] File not found: {path}", file=sys.stderr)
        return default
    try:
        with open(path, "r") as f:
            data = json.load(f)
            print(f"[DEBUG] Loaded {len(data)} items from {filename}", file=sys.stderr)
            return data
    except Exception as e:
        print(f"[DEBUG] Error loading {filename}: {e}", file=sys.stderr)
        return default

def _safe_save(filename, data):
    """Safely persists JSON data with proper formatting."""
    os.makedirs(DATA_DIR, exist_ok=True)
    path = os.path.join(DATA_DIR, filename)
    with open(path, "w") as f:
        json.dump(data, f, indent=4)

@mcp.tool()
def search_products(query: str, budget_max: int = 10000, avoid_keywords: any = None, category: Optional[str] = None, size: Optional[str] = None):
    """
    Searches the product catalog with strict filters.
    Args:
        query: Search keywords
        budget_max: Maximum price (INR). If not provided, defaults to 10000.
        avoid_keywords: Keywords to exclude
        category: Category filter (footwear, apparel, accessories)
        size: Size filter (e.g., "9", "M", "L")
    """
    print(f"\n{'='*60}", file=sys.stderr)
    print(f"[SEARCH] Called with:", file=sys.stderr)
    print(f"  query: '{query}'", file=sys.stderr)
    print(f"  budget_max: {budget_max}", file=sys.stderr)
    print(f"  avoid_keywords (raw): {avoid_keywords}", file=sys.stderr)
    print(f"  avoid_keywords type: {type(avoid_keywords)}", file=sys.stderr)
    
    products = _safe_load("catalog.json")
    print(f"[SEARCH] Loaded {len(products)} products from catalog", file=sys.stderr)
    
    # Standardize exclusion list
    if isinstance(avoid_keywords, str):
        avoid_list = avoid_keywords.lower().split()
        print(f"[SEARCH] Parsed string to list: {avoid_list}", file=sys.stderr)
    elif isinstance(avoid_keywords, list):
        # FLATTEN NESTED LISTS - THIS IS THE BUG FIX
        flat_list = []
        for item in avoid_keywords:
            if isinstance(item, str):
                flat_list.extend(item.lower().split())
            else:
                flat_list.append(str(item).lower())
        avoid_list = flat_list
        print(f"[SEARCH] Flattened list: {avoid_list}", file=sys.stderr)
    else:
        avoid_list = []
        print(f"[SEARCH] No avoid keywords provided", file=sys.stderr)

    # Category synonym mapping - maps query terms to standard categories
    CATEGORY_MAP = {
        # Footwear
        "sneakers": "footwear", "sneaker": "footwear", "shoes": "footwear",
        "shoe": "footwear", "boots": "footwear", "sandals": "footwear",
        "loafers": "footwear", "footwear": "footwear",
        # Apparel
        "shirts": "apparel", "shirt": "apparel", "t-shirts": "apparel",
        "t-shirt": "apparel", "tee": "apparel", "tees": "apparel",
        "pants": "apparel", "jeans": "apparel", "clothes": "apparel",
        "clothing": "apparel", "apparel": "apparel",
        # Accessories
        "sunglasses": "accessories", "belts": "accessories", "bags": "accessories",
        "watches": "accessories", "accessories": "accessories"
    }
    
    # Normalize category to standard form
    normalized_category = None
    if category:
        cat_lower = category.lower().strip()
        normalized_category = CATEGORY_MAP.get(cat_lower, cat_lower)
    
    # Debug
    print(f"[SEARCH] Query: {query}, Category: {category} -> {normalized_category}, Size: {size}, Budget: {budget_max}, Avoid: {avoid_list}", file=sys.stderr)
    
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
        product_brand = p.get('brand', "").lower()
        
        # 1. STRICT CATEGORY FILTER - If category specified, product MUST match
        if normalized_category and product_category != normalized_category:
            continue  # Skip products not in the requested category
        
        # 2. SIZE FILTER
        if size:
            # Handle multiple sizes (e.g. "8 and 9", "8, 9", "8 or 9")
            import re
            requested_sizes = [s.strip().lower() for s in re.split(r'[,|/]+|\s+and\s+|\s+or\s+', str(size)) if s.strip()]
            
            if requested_sizes:
                # If product size matches ANY of the requested sizes
                if product_size not in requested_sizes:
                    continue
        
        # 3. EXCLUSION CHECK
        all_text = f"{title} {product_sub_category} {product_material} {' '.join(keywords)}"
        is_excluded = any(word in all_text for word in avoid_list)
        if is_excluded:
            continue
            
        # 4. STRICT COLOR FILTER (Heuristic)
        # If query contains a common color, that color MUST appear in product text
        COMMON_COLORS = {"white", "black", "red", "blue", "green", "yellow", "pink", "purple", "brown", "grey", "gray", "beige", "gold", "silver"}
        query_colors = [w for w in query_words if w in COMMON_COLORS]
        
        if query_colors:
            # Check if ANY of the asked colors are in the product
            # (Relaxed: matches "white sneakers" to "white" but not "red")
            has_color = any(c in all_text for c in query_colors)
            if not has_color:
                continue

        # 4. CALCULATE MATCH SCORE
        match_score = 0
        
        # Base score if category matches (so all products in category show up)
        if normalized_category and product_category == normalized_category:
            match_score += 10
        
        # Bonus for query word matches
        for word in query_words:
            if word in ["i", "want", "need", "looking", "for", "a", "an", "the", "some", "show", "me", "of", "size", "with"]:
                continue
            if word in title:
                match_score += 3
            if word in product_sub_category:
                match_score += 2
            for kw in keywords:
                if word in kw:
                    match_score += 1
        
        # 5. BUDGET FILTER & ADD TO RESULTS
        if match_score > 0 and price <= budget_max:
            results.append({**p, '_score': match_score})
    
    # Sort by score (desc), then price (asc)
    results.sort(key=lambda x: (-x.get('_score', 0), x.get('price_inr', 0)))
    
    # Remove internal score
    for r in results:
        r.pop('_score', None)
    
    print(f"[SEARCH] Found {len(results)} products", file=sys.stderr)
    
    if not results:
        return {"message": "No products found.", "products": []}
    
    return {"products": results}

@mcp.tool()
def get_product_details(product_id: str):
    """Fetches full metadata for a specific product ID."""
    print(f"[DEBUG] get_product_details called for: {product_id}", file=sys.stderr)
    products = _safe_load("catalog.json")
    product = next((p for p in products if str(p.get("product_id")) == str(product_id)), None)
    return product if product else {"error": "Product not found"}

@mcp.tool()
def save_shortlist(user_id: str, items: list):
    """Saves a user's shortlisted items to disk."""
    print(f"[DEBUG] save_shortlist for user {user_id}: {items}", file=sys.stderr)
    shortlists = _safe_load("shortlists.json", default={})
    shortlists[user_id] = items
    _safe_save("shortlists.json", shortlists)
    return {"status": "success", "message": f"Saved {len(items)} items to shortlist"}

@mcp.tool()
def get_shortlist(user_id: str):
    """Retrieves a user's previously saved shortlist."""
    print(f"[DEBUG] get_shortlist for user {user_id}", file=sys.stderr)
    shortlists = _safe_load("shortlists.json", default={})
    return shortlists.get(user_id, [])

@mcp.tool()
def write_memory(user_id: str, facts: list):
    """Updates user preferences (facts) in long-term memory."""
    print(f"[DEBUG] write_memory for {user_id}: {facts}", file=sys.stderr)
    memories = _safe_load("memory.json", default=[])
    user_mem = next((m for m in memories if m.get("user_id") == user_id), {"user_id": user_id, "facts": []})
    
    # Merge new facts into the set of unique existing facts
    user_mem["facts"] = list(set(user_mem["facts"] + facts))
    
    memories = [m for m in memories if m.get("user_id") != user_id]
    memories.append(user_mem)
    _safe_save("memory.json", memories)
    return {"status": "success", "facts_count": len(user_mem["facts"])}

@mcp.tool()
def read_memory(user_id: str):
    """Fetches stored preferences/facts for a specific user."""
    print(f"[DEBUG] read_memory for {user_id}", file=sys.stderr)
    memories = _safe_load("memory.json", default=[])
    return next((m for m in memories if m.get("user_id") == user_id), {"user_id": user_id, "facts": []})

if __name__ == "__main__":
    print("[DEBUG] Starting MCP server...", file=sys.stderr)
    # Start the FastMCP server with stdio transport
    mcp.run(transport="stdio")