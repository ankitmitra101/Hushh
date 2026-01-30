import streamlit as st
import requests
import json
import os
import time
import re
from datetime import datetime

# Configuration & Theming
st.set_page_config(
    page_title="Hushh | AI Concierge",
    page_icon="◼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Force dark theme CSS - Applied to ENTIRE page
DARK_CSS = """
<style>
    /* Root variables for dark theme */
    :root {
        --bg-primary: #0a0a0f;
        --bg-secondary: #151520;
        --bg-card: #1a1a2e;
        --bg-hover: #222236;
        --accent-cyan: #00d4ff;
        --accent-purple: #bb86fc;
        --accent-pink: #ff006e;
        --accent-green: #00f5d4;
        --accent-orange: #fb5607;
        --accent-red: #ff4757;
        --text-primary: #ffffff;
        --text-secondary: #a0a0b0;
        --text-muted: #6c6c7d;
        --border: #2a2a3e;
        --border-hover: #3a3a50;
    }
    
    /* Force dark background on ALL containers */
    html, body, .stApp, [data-testid="stAppViewContainer"] {
        background-color: var(--bg-primary) !important;
        color: var(--text-primary) !important;
    }
    
    /* Sidebar dark */
    [data-testid="stSidebar"] {
        background-color: var(--bg-secondary) !important;
        border-right: 1px solid var(--border) !important;
    }
    
    [data-testid="stSidebarContent"] {
        background-color: var(--bg-secondary) !important;
    }
    
    /* Main content area */
    .main .block-container {
        background-color: var(--bg-primary) !important;
        padding-top: 2rem;
        max-width: 1400px;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Typography */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        -webkit-font-smoothing: antialiased;
    }
    
    /* Glass Cards - Dark theme */
    .glass-panel {
        background: linear-gradient(145deg, rgba(26,26,46,0.9) 0%, rgba(21,21,32,0.9) 100%);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 16px;
        transition: all 0.3s ease;
    }
    
    .glass-panel:hover {
        border-color: var(--border-hover);
        box-shadow: 0 4px 20px rgba(0,0,0,0.5);
    }
    
    /* Profile Section */
    .profile-avatar {
        width: 72px; height: 72px; border-radius: 50%;
        background: linear-gradient(135deg, var(--accent-cyan) 0%, var(--accent-purple) 100%);
        display: flex; align-items: center; justify-content: center;
        color: #000; font-size: 28px; font-weight: 700;
        margin: 0 auto 16px;
        box-shadow: 0 0 20px rgba(0,212,255,0.3);
    }
    
    /* Avoided/Dislikes Section - Red badges */
    .avoid-badge {
        display: inline-flex; align-items: center; padding: 6px 12px;
        background: rgba(255,71,87,0.15); 
        color: var(--accent-red);
        border: 1px solid rgba(255,71,87,0.3);
        border-radius: 8px; font-size: 0.85rem; font-weight: 500;
        margin: 4px; cursor: pointer;
        transition: all 0.2s;
    }
    
    .avoid-badge:hover {
        background: rgba(255,71,87,0.25);
        transform: translateY(-1px);
    }
    
    .avoid-badge .remove-icon {
        margin-left: 6px;
        opacity: 0.7;
        font-weight: bold;
    }
    
    /* Memory/Preference Chips */
    .memory-chip {
        display: inline-flex; align-items: center; padding: 6px 14px;
        background: rgba(0,212,255,0.1); 
        color: var(--accent-cyan);
        border: 1px solid rgba(0,212,255,0.2);
        border-radius: 100px; font-size: 0.8rem; font-weight: 500;
        margin: 4px;
    }
    
    .chip-brand {
        background: rgba(187,134,252,0.1);
        color: var(--accent-purple);
        border-color: rgba(187,134,252,0.2);
    }
    
    /* Chat Interface - Dark */
    .chat-container {
        background: var(--bg-secondary);
        border-radius: 20px;
        border: 1px solid var(--border);
        min-height: 500px;
        padding: 24px;
    }
    
    .message-bubble {
        max-width: 80%; padding: 14px 20px; margin: 12px 0;
        font-size: 0.95rem; line-height: 1.5;
        animation: slideIn 0.3s ease;
        position: relative;
    }
    
    .msg-user {
        background: linear-gradient(135deg, var(--accent-cyan) 0%, #0099cc 100%);
        color: #000;
        border-radius: 20px 20px 4px 20px;
        margin-left: auto;
        font-weight: 500;
        box-shadow: 0 4px 15px rgba(0,212,255,0.3);
    }
    
    .msg-agent {
        background: var(--bg-card);
        color: var(--text-primary);
        border: 1px solid var(--border);
        border-radius: 20px 20px 20px 4px;
        margin-right: auto;
    }
    
    @keyframes slideIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* FIXED Question Card - Dark Blue/High Contrast */
    .question-card {
        background: linear-gradient(145deg, #1e3a5f 0%, #2d4a6f 100%);
        border: 2px solid var(--accent-cyan);
        border-radius: 16px;
        padding: 28px;
        margin: 20px 0;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0,212,255,0.15);
    }
    
    .question-text {
        font-size: 1.2rem; font-weight: 600;
        margin-bottom: 20px;
        color: var(--text-primary);
        text-shadow: 0 1px 2px rgba(0,0,0,0.3);
    }
    
    .progress-indicator {
        color: var(--accent-cyan);
        font-size: 0.85rem;
        margin-bottom: 16px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.1em;
    }
    
    /* Answer Buttons - Dark theme */
    .answer-btn {
        background: var(--bg-card);
        border: 1px solid var(--border);
        color: var(--text-primary);
        padding: 12px 24px;
        border-radius: 12px;
        margin: 6px;
        cursor: pointer;
        transition: all 0.2s;
        font-weight: 500;
    }
    
    .answer-btn:hover {
        background: rgba(0,212,255,0.1);
        border-color: var(--accent-cyan);
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,212,255,0.2);
    }
    
    /* Product Results */
    .results-header {
        background: linear-gradient(90deg, rgba(0,245,212,0.1) 0%, transparent 100%);
        border-left: 4px solid var(--accent-green);
        padding: 16px 20px;
        border-radius: 12px;
        margin-bottom: 20px;
    }
    
    .product-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
        gap: 20px;
        margin-top: 20px;
    }
    
    .product-card {
        background: var(--bg-card);
        border-radius: 16px;
        overflow: hidden;
        border: 1px solid var(--border);
        transition: all 0.3s ease;
    }
    
    .product-card:hover {
        transform: translateY(-4px);
        border-color: var(--accent-cyan);
        box-shadow: 0 10px 30px rgba(0,0,0,0.4);
    }
    
    .product-image {
        width: 100%; height: 180px;
        background: linear-gradient(135deg, #252538 0%, #1e1e2d 100%);
        display: flex; align-items: center; justify-content: center;
        font-size: 64px;
        position: relative;
        border-bottom: 1px solid var(--border);
    }
    
    .match-badge {
        position: absolute; top: 12px; right: 12px;
        background: rgba(0,0,0,0.8);
        color: var(--accent-green);
        padding: 6px 12px;
        border-radius: 20px;
        font-size: 0.8rem; font-weight: 700;
        border: 1px solid var(--accent-green);
    }
    
    .product-info { padding: 20px; }
    
    .product-title {
        font-size: 1.1rem; font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 8px;
    }
    
    .product-brand {
        color: var(--accent-purple);
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 8px;
    }
    
    .product-price {
        color: var(--accent-cyan);
        font-size: 1.4rem; font-weight: 700;
    }
    
    .product-tags {
        display: flex; flex-wrap: wrap; gap: 6px;
        margin-top: 12px;
    }
    
    .tag {
        padding: 4px 10px;
        background: rgba(0,212,255,0.1);
        color: var(--accent-cyan);
        border-radius: 6px;
        font-size: 0.75rem;
    }
    
    /* Status Pills */
    .status-pill {
        padding: 8px 16px;
        border-radius: 100px;
        font-size: 0.85rem;
        font-weight: 500;
        display: flex; align-items: center; gap: 8px;
        background: var(--bg-card);
        border: 1px solid var(--border);
        margin-bottom: 8px;
    }
    
    .status-filled {
        border-color: var(--accent-green);
        color: var(--accent-green);
        background: rgba(0,245,212,0.1);
    }
    
    .status-pending {
        border-color: var(--accent-orange);
        color: var(--accent-orange);
        background: rgba(251,86,7,0.1);
    }
    
    /* Thinking Animation */
    .thinking {
        display: flex; align-items: center; gap: 12px;
        padding: 16px 20px;
        background: var(--bg-card);
        border-radius: 16px;
        border: 1px solid var(--border);
        width: fit-content;
        margin: 12px 0;
    }
    
    .thinking-text {
        color: var(--accent-cyan);
        font-weight: 500;
    }
    
    .dot {
        width: 8px; height: 8px;
        background: var(--accent-cyan);
        border-radius: 50%;
        animation: bounce 1.4s infinite ease-in-out both;
    }
    
    @keyframes bounce {
        0%, 80%, 100% { transform: scale(0); }
        40% { transform: scale(1); }
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-track { background: var(--bg-primary); }
    ::-webkit-scrollbar-thumb { background: #333; border-radius: 4px; }
    ::-webkit-scrollbar-thumb:hover { background: #444; }
    
    /* Input styling */
    .stTextInput > div > div > input {
        background: var(--bg-card) !important;
        color: white !important;
        border: 1px solid var(--border) !important;
        border-radius: 12px !important;
    }
    
    /* Fix Streamlit buttons */
    .stButton > button {
        background: var(--bg-card) !important;
        color: white !important;
        border: 1px solid var(--border) !important;
        border-radius: 8px !important;
    }
    
    .stButton > button:hover {
        border-color: var(--accent-cyan) !important;
        box-shadow: 0 0 10px rgba(0,212,255,0.2) !important;
    }
    
    /* Empty state text */
    .empty-state {
        color: var(--text-muted);
        font-style: italic;
        font-size: 0.9rem;
    }
</style>
"""

st.markdown(DARK_CSS, unsafe_allow_html=True)

API_BASE_URL = os.getenv("BACKEND_URL", "https://hushh-backend-uc5w.onrender.com")
API_URL = f"{API_BASE_URL}/agents/run"

REQUIRED_FIELDS = ["category", "budget"]

# --- DYNAMIC DATA LOADING ---
def load_catalog():
    """Load catalog from data/catalog.json"""
    try:
        with open('data/catalog.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Error loading catalog: {e}")
        return []

def load_user_memory():
    """Load user memory from data/memory.json"""
    default_memory = {
        "user_id": "ankit_01",
        "name": "Ankit",
        "preferences": [],
        "avoid_keywords": [],  # Starts empty!
        "brand_affinity": [],
        "closet": []
    }
    
    try:
        if os.path.exists('data/memory.json'):
            with open('data/memory.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Find user or return default
                if isinstance(data, list):
                    for user in data:
                        if user.get("user_id") == "ankit_01":
                            return user
                    return default_memory
                elif isinstance(data, dict):
                    return data
        return default_memory
    except Exception as e:
        st.error(f"Error loading memory: {e}")
        return default_memory

def save_user_memory(memory_data):
    """Save user memory to data/memory.json"""
    try:
        os.makedirs('data', exist_ok=True)
        existing_data = []
        
        # Load existing if present
        if os.path.exists('data/memory.json'):
            with open('data/memory.json', 'r', encoding='utf-8') as f:
                try:
                    existing_data = json.load(f)
                    if not isinstance(existing_data, list):
                        existing_data = [existing_data]
                except:
                    existing_data = []
        
        # Update or append
        user_found = False
        for i, user in enumerate(existing_data):
            if user.get("user_id") == memory_data["user_id"]:
                existing_data[i] = memory_data
                user_found = True
                break
        
        if not user_found:
            existing_data.append(memory_data)
        
        with open('data/memory.json', 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, indent=2)
            
    except Exception as e:
        st.error(f"Error saving memory: {e}")

def extract_avoided_keywords(text):
    """Extract what user wants to avoid"""
    avoided = []
    text_lower = text.lower()
    
    # Patterns for avoidance
    patterns = [
        r'(?:no|avoid|hate|skip|without|not|don\'t\s+(?:like|want))\s+(?:any\s+)?(\w+)',
        r'(?:no|avoid|hate|skip)\s+(?:any\s+)?(\w+\s+\w+)',  # Two words like "chunky shoes"
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text_lower)
        avoided.extend(matches)
    
    # Clean up and remove duplicates
    avoided = [a.strip() for a in avoided if len(a.strip()) > 2]
    return list(set(avoided))

def extract_entities(text):
    """Smart entity extraction"""
    entities = {}
    text_lower = text.lower()
    
    # Category detection
    categories = {
        "footwear": ["shoes", "sneakers", "footwear", "kicks", "runners", "boots", "slip-on"],
        "apparel": ["shirt", "t-shirt", "pants", "jeans", "clothes", "top", "bottom", "crewneck"],
        "accessories": ["belt", "sunglasses", "watch", "accessories", "bag", "wallet", "eyewear"]
    }
    for cat, keywords in categories.items():
        if any(kw in text_lower for kw in keywords):
            entities["category"] = cat
            break
    
    # Budget extraction
    budget_patterns = [
        r'(?:under|below|max|up to|less than)\s*(?:₹|rs\.?|inr)?\s*(\d{3,5})',
        r'(?:₹|rs\.?|inr)\s*(\d{3,5})',
        r'(\d{3,5})\s*(?:₹|rs\.?|inr)',
    ]
    for pattern in budget_patterns:
        match = re.search(pattern, text_lower)
        if match:
            entities["budget"] = int(match.group(1))
            break
    
    # Size extraction
    size_match = re.search(r'\b(?:size\s*)?(\d+|s|m|l|xl)\b', text_lower)
    if size_match:
        entities["size"] = size_match.group(1).upper() if size_match.group(1) in ['s','m','l','xl'] else size_match.group(1)
    
    # Color extraction
    colors = ["white", "black", "blue", "navy", "red", "brown", "beige", "olive", "indigo", "gold"]
    for color in colors:
        if color in text_lower:
            entities["color"] = color
            break
    
    return entities

def get_missing_fields(collected):
    return [field for field in REQUIRED_FIELDS if field not in collected]

def generate_question(field):
    questions = {
        "category": "What are you looking for?",
        "budget": "What's your budget?",
        "size": "What size?",
        "color": "Preferred color?"
    }
    return questions.get(field, f"Please specify {field}")

def get_quick_options(field):
    options = {
        "category": ["Sneakers/Shoes", "Shirts/Tops", "Pants/Jeans", "Accessories"],
        "budget": ["Under ₹1500", "₹1500-₹2500", "₹2500-₹3500", "No limit"],
        "size": ["7", "8", "9", "10", "M", "L"],
        "color": ["White", "Black", "Blue", "Any"]
    }
    return options.get(field, [])

def parse_quick_option(field, option):
    if field == "budget":
        if "Under" in option:
            return 1500
        elif "No limit" in option:
            return 100000
        else:
            nums = re.findall(r'\d+', option)
            return int(nums[-1]) if nums else 5000
    elif field == "category":
        mapping = {
            "Sneakers/Shoes": "footwear",
            "Shirts/Tops": "apparel",
            "Pants/Jeans": "apparel",
            "Accessories": "accessories"
        }
        return mapping.get(option, "footwear")
    return option.lower()

def filter_products(catalog, collected, avoid_keywords):
    """Smart filtering with avoid logic"""
    results = []
    
    for product in catalog:
        # Check if product has avoided keywords
        has_avoided = False
        product_keywords = [k.lower() for k in product.get("style_keywords", [])]
        product_title = product.get("title", "").lower()
        
        for avoid in avoid_keywords:
            avoid_lower = avoid.lower()
            if avoid_lower in product_keywords or avoid_lower in product_title:
                has_avoided = True
                break
        
        if has_avoided:
            continue  # Skip this product
        
        # Calculate match score
        score = 0
        
        if collected.get("category") and product.get("category") == collected["category"]:
            score += 40
        
        if "budget" in collected and product.get("price_inr", 99999) <= collected["budget"]:
            score += 30
        
        if collected.get("size"):
            if str(product.get("size")) == str(collected["size"]):
                score += 15
        
        if collected.get("color"):
            if any(collected["color"] in kw for kw in product.get("style_keywords", [])):
                score += 10
        
        if score > 0:
            product["match_score"] = min(score / 100, 0.99)
            results.append(product)
    
    results.sort(key=lambda x: x["match_score"], reverse=True)
    return results[:6]

# --- SESSION STATE ---
defaults = {
    "messages": [],
    "collected": {},
    "current_question": None,
    "show_results": False,
    "products": [],
    "thinking": False
}
for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

# Load data
CATALOG = load_catalog()
USER_MEMORY = load_user_memory()

# --- SIDEBAR ---
with st.sidebar:
    st.markdown(f"""
    <div style="text-align: center; padding: 20px 0;">
        <div class="profile-avatar">{USER_MEMORY['name'][0]}</div>
        <h2 style="margin: 0; font-size: 1.3rem; font-weight: 600; color: white;">{USER_MEMORY['name']}</h2>
        <p style="color: var(--text-muted); margin: 4px 0 0; font-size: 0.9rem;">@{USER_MEMORY['user_id']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # RECENTLY AVOIDED SECTION
    st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
    st.markdown("""
    <h4 style="margin-top:0; color: var(--accent-red); font-size: 0.9rem; text-transform: uppercase; letter-spacing: 0.05em;">
        ⛔ Recently Avoided
    </h4>
    """, unsafe_allow_html=True)
    
    if USER_MEMORY.get("avoid_keywords"):
        st.markdown("<p style='color: var(--text-muted); font-size: 0.8rem; margin-bottom: 12px;'>Click ✕ to remove filter</p>", unsafe_allow_html=True)
        for avoid in USER_MEMORY["avoid_keywords"]:
            if st.button(f"✕ {avoid}", key=f"remove_{avoid}"):
                USER_MEMORY["avoid_keywords"].remove(avoid)
                save_user_memory(USER_MEMORY)
                st.rerun()
    else:
        st.markdown("""
        <p class="empty-state">
            No filters yet. Tell me things like<br/>
            <span style="color: var(--accent-cyan);">"no chunky shoes"</span> or 
            <span style="color: var(--accent-cyan);">"avoid neon"</span>
        </p>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Session Status
    st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
    st.markdown("<h4 style='margin-top:0; color: var(--accent-cyan); font-size: 0.9rem;'>SESSION STATUS</h4>", unsafe_allow_html=True)
    
    for field in REQUIRED_FIELDS:
        if field in st.session_state.collected:
            val = st.session_state.collected[field]
            display = f"₹{val}" if field == "budget" else val
            st.markdown(f'<div class="status-pill status-filled">✓ <b>{field.title()}:</b> {display}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="status-pill status-pending">○ <b>{field.title()}</b> needed</div>', unsafe_allow_html=True)
    
    if st.session_state.collected.get("size"):
        st.markdown(f'<div class="status-pill status-filled">✓ <b>Size:</b> {st.session_state.collected["size"]}</div>', unsafe_allow_html=True)
    if st.session_state.collected.get("color"):
        st.markdown(f'<div class="status-pill status-filled">✓ <b>Color:</b> {st.session_state.collected["color"]}</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# --- MAIN INTERFACE ---
st.markdown("""
<div style="text-align: center; margin-bottom: 40px;">
    <h1 style="font-weight: 700; font-size: 2.2rem; margin-bottom: 8px; background: linear-gradient(90deg, var(--accent-cyan), var(--accent-purple)); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
        AI Shopping Concierge
    </h1>
    <p style="color: var(--text-muted); font-size: 1rem; margin: 0;">
        I learn what you dislike. I ask only what's necessary.
    </p>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([3, 1])

with col1:
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    
    # Messages
    for msg in st.session_state.messages:
        bubble_class = "msg-user" if msg["role"] == "user" else "msg-agent"
        st.markdown(f'<div class="message-bubble {bubble_class}">{msg["content"]}</div>', unsafe_allow_html=True)
        
        if msg.get("products"):
            st.markdown('<div class="results-header"><h3 style="margin:0; color: var(--accent-green);">✓ Found these matches</h3></div>', unsafe_allow_html=True)
            st.markdown('<div class="product-grid">', unsafe_allow_html=True)
            for prod in msg["products"]:
                tags_html = "".join([f'<span class="tag">{kw}</span>' for kw in prod.get("style_keywords", [])[:3]])
                st.markdown(f"""
                <div class="product-card">
                    <div class="product-image">👟<div class="match-badge">{int(prod['match_score']*100)}% MATCH</div></div>
                    <div class="product-info">
                        <div class="product-brand">{prod['brand']}</div>
                        <div class="product-title">{prod['title']}</div>
                        <div class="product-tags">{tags_html}</div>
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-top:12px;">
                            <span class="product-price">₹{prod['price_inr']}</span>
                            <span style="color: var(--text-muted); font-size:0.8rem;">{prod.get('material', '')}</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Thinking
    if st.session_state.thinking:
        st.markdown("""
        <div class="thinking">
            <span class="thinking-text">Finding best matches...</span>
            <div class="dot"></div><div class="dot"></div><div class="dot"></div>
        </div>
        """, unsafe_allow_html=True)
    
    # Question Card (FIXED - Dark blue, white text)
    if st.session_state.current_question and not st.session_state.show_results:
        field = st.session_state.current_question
        q_text = generate_question(field)
        options = get_quick_options(field)
        progress = len([f for f in REQUIRED_FIELDS if f in st.session_state.collected])
        
        st.markdown(f"""
        <div class="question-card">
            <div class="progress-indicator">Step {progress + 1} of {len(REQUIRED_FIELDS) + 1}</div>
            <div class="question-text">{q_text}</div>
        </div>
        """, unsafe_allow_html=True)
        
        cols = st.columns(min(len(options), 2))
        for i, opt in enumerate(options):
            with cols[i % 2]:
                if st.button(opt, key=f"btn_{field}_{i}", use_container_width=True):
                    val = parse_quick_option(field, opt)
                    st.session_state.collected[field] = val
                    st.session_state.messages.append({"role": "user", "content": opt})
                    
                    missing = get_missing_fields(st.session_state.collected)
                    if missing:
                        st.session_state.current_question = missing[0]
                    else:
                        st.session_state.current_question = None
                        st.session_state.thinking = True
                    st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Input
    if not st.session_state.show_results and not st.session_state.current_question:
        if prompt := st.chat_input("Tell me what you want (e.g., 'white sneakers no chunky style')..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Extract what to avoid and add to memory
            avoided = extract_avoided_keywords(prompt)
            if avoided:
                USER_MEMORY["avoid_keywords"].extend(avoided)
                USER_MEMORY["avoid_keywords"] = list(set(USER_MEMORY["avoid_keywords"]))  # Deduplicate
                save_user_memory(USER_MEMORY)
                st.toast(f"Added to avoid list: {', '.join(avoided)}", icon="🚫")
            
            # Extract entities
            extracted = extract_entities(prompt)
            st.session_state.collected.update(extracted)
            
            missing = get_missing_fields(st.session_state.collected)
            if missing:
                st.session_state.current_question = missing[0]
            else:
                st.session_state.thinking = True
            st.rerun()
    
    if st.session_state.show_results:
        if st.button("🔄 Start New Search", use_container_width=True):
            for key in defaults:
                st.session_state[key] = defaults[key]
            st.rerun()

with col2:
    st.markdown('<div class="glass-panel" style="height: 600px; overflow-y: auto;">', unsafe_allow_html=True)
    st.markdown("<h4 style='margin-top:0; color: var(--accent-cyan);'>SYSTEM TRACE</h4>", unsafe_allow_html=True)
    
    steps = [
        ("Catalog Loaded", len(CATALOG) > 0, f"{len(CATALOG)} items"),
        ("Memory Active", True, f"{len(USER_MEMORY.get('avoid_keywords', []))} avoided"),
        ("Intent Parsed", "category" in st.session_state.collected, "Category detected"),
        ("Budget Set", "budget" in st.session_state.collected, "Price filter active"),
        ("Results Ready", st.session_state.show_results, f"{len(st.session_state.products)} matches")
    ]
    
    for label, status, detail in steps:
        color = "var(--accent-green)" if status else "var(--text-muted)"
        icon = "✓" if status else "○"
        st.markdown(f"""
        <div style="padding: 10px; margin: 6px 0; background: var(--bg-card); border-radius: 8px; border-left: 3px solid {color};">
            <div style="color: {color}; font-weight: 600;">{icon} {label}</div>
            <div style="color: var(--text-muted); font-size: 0.8rem;">{detail}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# --- BACKEND CALL ---
if st.session_state.thinking:
    try:
        time.sleep(0.5)
        
        # Local filter first (always works)
        filtered = filter_products(CATALOG, st.session_state.collected, USER_MEMORY.get("avoid_keywords", []))
        
        # Try API if available
        try:
            resp = requests.post(API_URL, json={
                "user_id": "ankit_01",
                "message": str(st.session_state.collected),
                "context": st.session_state.collected
            }, timeout=5)
            if resp.status_code == 200:
                api_results = resp.json().get("results", [])
                if api_results:
                    filtered = api_results
        except:
            pass
        
        st.session_state.messages.append({
            "role": "assistant",
            "content": f"Found {len(filtered)} items. Filtered out items with: {', '.join(USER_MEMORY.get('avoid_keywords', ['none']))}",
            "products": filtered
        })
        
        st.session_state.products = filtered
        st.session_state.thinking = False
        st.session_state.show_results = True
        
    except Exception as e:
        st.session_state.thinking = False
        st.error(f"Error: {e}")
    
    st.rerun()

st.markdown("""
<div style="text-align: center; margin-top: 40px; color: var(--text-muted); font-size: 0.8rem;">
    <p>Dynamic memory • Smart filtering • Minimal questioning</p>
</div>
""", unsafe_allow_html=True)