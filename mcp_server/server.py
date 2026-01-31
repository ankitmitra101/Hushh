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
        return default
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception:
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
    products = _safe_load("catalog.json")
    
    # 1. STANDARDIZE EXCLUSION LIST
    if isinstance(avoid_keywords, str):
        avoid_list = avoid_keywords.lower().split()
    elif isinstance(avoid_keywords, list):
        avoid_list = " ".join([str(i) for i in avoid_keywords]).lower().split()
    else:
        avoid_list = []

    # Filter out overly generic words
    generic_words = ["soles", "shoes", "style", "designs", "design", "product", "products"]
    avoid_list = [w for w in avoid_list if w not in generic_words]
    
    # Debug logging
    print(f"[SEARCH] Query: {query}, Category: {category}, Size: {size}, Avoid: {avoid_list}, Budget: {budget_max}", file=sys.stderr)
    
    query_words = query.lower().split()
    results = []

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
        
        # 2. CATEGORY FILTER
        if category:
            category_lower = category.lower().strip()
            normalized_category = category_synonyms.get(category_lower, category_lower)
            if product_category != normalized_category:
                continue
        
        # 3. SIZE FILTER (if specified)
        if size:
            size_lower = size.lower().strip()
            if product_size != size_lower:
                # Also check if size appears in title or keywords
                if size_lower not in title and size_lower not in all_searchable_text:
                    continue
        
        # 4. EXCLUSION CHECK - Check ALL fields
        is_excluded = False
        for word in avoid_list:
            if word in all_searchable_text:
                is_excluded = True
                print(f"[SEARCH] Excluded: {p.get('title')} (matched avoid word: {word})", file=sys.stderr)
                break
                
        if is_excluded:
            continue

        # 5. POSITIVE MATCHING - Search across ALL fields
        match_score = 0
        for word in query_words:
            # Skip common words
            if word in ["i", "want", "need", "looking", "for", "a", "an", "the", "some", "please", "show", "me"]:
                continue
            
            # Check title (highest weight)
            if word in title:
                match_score += 3
            # Check style keywords
            for kw in keywords:
                if word in kw or kw in word:
                    match_score += 2
            # Check sub_category
            if word in product_sub_category:
                match_score += 2
            # Check material
            if word in product_material:
                match_score += 1
            # Check brand
            if word in product_brand:
                match_score += 1
        
        # 6. BUDGET FILTER
        if match_score > 0 and price <= int(budget_max):
            p['_match_score'] = match_score  # Add score for sorting
            results.append(p)
    
    # Sort by match score (descending), then by price (ascending)
    sorted_results = sorted(results, key=lambda x: (-x.get('_match_score', 0), x.get('price_inr', 0)))
    
    # Remove internal score before returning
    for r in sorted_results:
        r.pop('_match_score', None)
    
    print(f"[SEARCH] Found {len(sorted_results)} products", file=sys.stderr)
    
    if not sorted_results:
        return {"message": "No products found matching your preferences.", "products": []}
    
    return {"products": sorted_results}

@mcp.tool()
def get_product_details(product_id: str):
    """Fetches full metadata for a specific product ID."""
    products = _safe_load("catalog.json")
    product = next((p for p in products if str(p.get("product_id")) == str(product_id)), None)
    return product if product else {"error": "Product not found"}

@mcp.tool()
def save_shortlist(user_id: str, items: list):
    """Saves a user's shortlisted items to disk."""
    shortlists = _safe_load("shortlists.json", default={})
    shortlists[user_id] = items
    _safe_save("shortlists.json", shortlists)
    return {"status": "success", "message": f"Saved {len(items)} items to shortlist"}

@mcp.tool()
def get_shortlist(user_id: str):
    """Retrieves a user's previously saved shortlist."""
    shortlists = _safe_load("shortlists.json", default={})
    return shortlists.get(user_id, [])

@mcp.tool()
def write_memory(user_id: str, facts: list):
    """Updates user preferences (facts) in long-term memory."""
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
    memories = _safe_load("memory.json", default=[])
    return next((m for m in memories if m.get("user_id") == user_id), {"user_id": user_id, "facts": []})

if __name__ == "__main__":
    # Start the FastMCP server with stdio transport
    mcp.run(transport="stdio")