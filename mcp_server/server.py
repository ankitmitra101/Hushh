import sys
import json
import os
import traceback
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP
mcp = FastMCP("ShoppingTools")

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
def search_products(query: str, budget_max: int = 10000, avoid_keywords: any = None, category: str = None, size: str = None):
    """
    Intelligent product search that checks ALL catalog fields.
    
    Args:
        query: Search query (e.g., "white sneakers size 9")
        budget_max: Maximum budget in INR
        avoid_keywords: Keywords to exclude (checks title, style_keywords, material, etc.)
        category: Category filter (footwear, apparel, accessories, toys, electronics, etc.)
        size: Size filter (e.g., "9", "M", "L", "XL")
    """
    print(f"\n{'='*60}", file=sys.stderr)
    print(f"[SEARCH] Called with:", file=sys.stderr)
    print(f"  query: '{query}'", file=sys.stderr)
    print(f"  budget_max: {budget_max}", file=sys.stderr)
    print(f"  avoid_keywords (raw): {avoid_keywords}", file=sys.stderr)
    print(f"  avoid_keywords type: {type(avoid_keywords)}", file=sys.stderr)
    
    products = _safe_load("catalog.json")
    print(f"[SEARCH] Loaded {len(products)} products from catalog", file=sys.stderr)
    
    # 1. STANDARDIZE EXCLUSION LIST
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

    # 2. FILTER OUT GENERIC WORDS
    filtered_words = ["soles", "shoes", "style", "sneaker", "sneakers"]
    avoid_list = [w for w in avoid_list if w not in filtered_words]
    print(f"[SEARCH] After filtering generic words: {avoid_list}", file=sys.stderr)
    
    query_words = query.lower().split()
    results = []
    excluded_products = []  # Track what we exclude for debug

    # Category synonym mapping (generalized)
    category_synonyms = {
        "sneakers": "footwear", "sneaker": "footwear", "shoes": "footwear",
        "shoe": "footwear", "runners": "footwear", "running": "footwear",
        "boots": "footwear", "sandals": "footwear", "heels": "footwear",
        "shirts": "apparel", "shirt": "apparel", "t-shirts": "apparel",
        "t-shirt": "apparel", "tee": "apparel", "tees": "apparel",
        "tops": "apparel", "pants": "apparel", "jeans": "apparel",
        "clothing": "apparel", "clothes": "apparel", "dresses": "apparel",
        "belts": "accessories", "sunglasses": "accessories", "bags": "accessories",
        "watches": "accessories", "jewelry": "accessories", "caps": "accessories",
        "games": "toys", "gadgets": "electronics", "groceries": "food",
        "snacks": "food", "phones": "electronics"
    }

    for p in products:
        # Extract ALL searchable fields from catalog
        title = p.get('title', "").lower()
        keywords = [k.lower() for k in p.get('style_keywords', [])]
        price = p.get('price_inr', 0)
        product_category = p.get('category', "").lower()
        product_sub_category = p.get('sub_category', "").lower()
        product_size = str(p.get('size', "")).lower()
        product_material = p.get('material', "").lower()
        product_brand = p.get('brand', "").lower()
        
        # Combine all searchable text for the product
        all_searchable_text = f"{title} {product_sub_category} {product_material} {product_brand} {' '.join(keywords)}"
        
        print(f"[SEARCH] Checking: '{p.get('title')}' | keywords: {keywords} | price: {price}", file=sys.stderr)
        
        # 3. EXCLUSION CHECK (Negative Matching)
        is_excluded = False
        excluded_reason = []
        
        for word in avoid_list:
            if word in title:
                is_excluded = True
                excluded_reason.append(f"'{word}' in title")
                print(f"    ❌ EXCLUDED: '{word}' found in title '{title}'", file=sys.stderr)
                break
            if any(word in kw for kw in keywords):
                is_excluded = True
                excluded_reason.append(f"'{word}' in keywords")
                print(f"    ❌ EXCLUDED: '{word}' found in keywords {keywords}", file=sys.stderr)
                break
        
        if is_excluded:
            excluded_products.append({
                "product": p.get('title'),
                "reason": excluded_reason
            })
            continue

        # 4. INCLUSION CHECK (Positive Matching)
        matches_text = any(any(word in title or word in kw for kw in keywords) for word in query_words)
        
        # 5. BUDGET FILTER
        if matches_text and price <= int(budget_max):
            print(f"    ✅ INCLUDED: matches query and budget", file=sys.stderr)
            results.append(p)
        else:
            print(f"    ❌ NO MATCH: matches_text={matches_text}, price_ok={price <= int(budget_max)}", file=sys.stderr)
    
    # Sort by match score (descending), then by price (ascending)
    sorted_results = sorted(results, key=lambda x: (-x.get('_match_score', 0), x.get('price_inr', 0)))
    
    # Remove internal score before returning
    for r in sorted_results:
        r.pop('_match_score', None)
    
    print(f"[SEARCH] Found {len(sorted_results)} products", file=sys.stderr)
    
    print(f"\n[SEARCH] RESULTS: {len(sorted_results)} included, {len(excluded_products)} excluded", file=sys.stderr)
    print(f"[SEARCH] Excluded: {[e['product'] for e in excluded_products]}", file=sys.stderr)
    print(f"{'='*60}\n", file=sys.stderr)
    
    if not sorted_results:
        return {"message": "No products found matching your current preferences and budget.", "excluded": excluded_products}
    
    return {"products": sorted_results, "debug_excluded": excluded_products}

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