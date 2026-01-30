import streamlit as st
import requests
import json
import os
import time
import re
from datetime import datetime

# Configuration & Theming
st.set_page_config(
    page_title="Hushh | Personal Concierge",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apple Design System CSS
APPLE_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');
    
    :root {
        --ios-blue: #007AFF;
        --ios-indigo: #5856D6;
        --ios-purple: #AF52DE;
        --ios-red: #FF3B30;
        --ios-orange: #FF9500;
        --ios-green: #34C759;
        --ios-gray: #8E8E93;
        --glass-bg: rgba(255, 255, 255, 0.75);
        --glass-border: rgba(255, 255, 255, 0.4);
    }
    
    * { font-family: 'Inter', -apple-system, sans-serif; -webkit-font-smoothing: antialiased; }
    
    .main .block-container { padding-top: 2rem; max-width: 1200px; }
    
    /* Glassmorphism */
    .glass-panel {
        background: var(--glass-bg);
        backdrop-filter: saturate(180%) blur(20px);
        border: 1px solid var(--glass-border);
        border-radius: 24px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.04);
        padding: 24px;
        margin-bottom: 20px;
        transition: all 0.3s ease;
    }
    
    .glass-panel:hover { box-shadow: 0 12px 40px rgba(0,0,0,0.08); }
    
    /* Profile */
    .profile-avatar {
        width: 80px; height: 80px; border-radius: 50%;
        background: linear-gradient(135deg, var(--ios-blue) 0%, var(--ios-purple) 100%);
        display: flex; align-items: center; justify-content: center;
        color: white; font-size: 32px; font-weight: 600;
        margin: 0 auto 16px;
        box-shadow: 0 4px 20px rgba(0,122,255,0.3);
    }
    
    /* Memory Chips */
    .chip-container { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 12px; }
    .memory-chip {
        display: inline-flex; align-items: center; padding: 6px 14px;
        border-radius: 100px; font-size: 0.8rem; font-weight: 500;
        transition: transform 0.2s ease; cursor: default;
    }
    .memory-chip:hover { transform: scale(1.05); }
    .chip-pref { background: rgba(0,122,255,0.1); color: var(--ios-blue); border: 1px solid rgba(0,122,255,0.2); }
    .chip-avoid { background: rgba(255,59,48,0.08); color: var(--ios-red); border: 1px solid rgba(255,59,48,0.15); }
    .chip-brand { background: rgba(175,82,222,0.08); color: var(--ios-purple); border: 1px solid rgba(175,82,222,0.15); }
    .chip-status { background: rgba(52,199,89,0.1); color: var(--ios-green); border: 1px solid rgba(52,199,89,0.2); }
    
    /* Chat */
    .chat-container {
        background: white; border-radius: 24px; padding: 24px;
        box-shadow: 0 4px 24px rgba(0,0,0,0.03); border: 1px solid rgba(0,0,0,0.04);
        min-height: 500px;
    }
    
    .message-bubble {
        max-width: 75%; padding: 14px 20px; margin: 8px 0;
        font-size: 0.95rem; line-height: 1.4;
        animation: messageSlide 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
    }
    .msg-user {
        background: var(--ios-blue); color: white;
        border-radius: 20px 20px 4px 20px; margin-left: auto;
        box-shadow: 0 4px 12px rgba(0,122,255,0.25);
    }
    .msg-agent {
        background: #F2F2F7; color: #1C1C1E;
        border-radius: 20px 20px 20px 4px; margin-right: auto;
    }
    
    @keyframes messageSlide {
        from { opacity: 0; transform: translateY(20px) scale(0.95); }
        to { opacity: 1; transform: translateY(0) scale(1); }
    }
    
    /* Single Question Card */
    .question-card {
        background: linear-gradient(135deg, rgba(0,122,255,0.05) 0%, rgba(88,86,214,0.05) 100%);
        border: 2px solid var(--ios-blue);
        border-radius: 20px; padding: 24px;
        margin: 16px 0;
        text-align: center;
        animation: pulseBorder 2s infinite;
    }
    
    @keyframes pulseBorder {
        0%, 100% { border-color: rgba(0,122,255,0.3); }
        50% { border-color: rgba(0,122,255,0.8); }
    }
    
    .question-text {
        font-size: 1.1rem; font-weight: 600; color: #1C1C1E;
        margin-bottom: 16px;
    }
    
    .answer-btn {
        background: white; border: 1px solid var(--ios-blue); color: var(--ios-blue);
        padding: 10px 20px; border-radius: 20px; margin: 6px;
        cursor: pointer; transition: all 0.2s; font-weight: 500;
    }
    .answer-btn:hover { background: var(--ios-blue); color: white; transform: scale(1.05); }
    
    /* Product Cards */
    .product-grid {
        display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
        gap: 20px; margin-top: 20px;
    }
    .product-card {
        background: white; border-radius: 20px; overflow: hidden;
        border: 1px solid rgba(0,0,0,0.06);
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        transition: all 0.3s ease; position: relative;
    }
    .product-card:hover { transform: translateY(-4px); box-shadow: 0 12px 32px rgba(0,0,0,0.12); }
    .product-image-placeholder {
        width: 100%; height: 160px; background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        display: flex; align-items: center; justify-content: center; font-size: 48px;
    }
    .match-score {
        position: absolute; top: 12px; right: 12px;
        background: rgba(0,0,0,0.75); color: white;
        padding: 6px 12px; border-radius: 20px;
        font-size: 0.75rem; font-weight: 600; backdrop-filter: blur(10px);
    }
    .product-info { padding: 20px; }
    
    /* Status Indicators */
    .status-bar {
        display: flex; gap: 12px; margin-bottom: 20px; flex-wrap: wrap;
    }
    .status-pill {
        padding: 8px 16px; border-radius: 100px; font-size: 0.85rem;
        background: rgba(120,120,128,0.08); border: 1px solid rgba(120,120,128,0.15);
        display: flex; align-items: center; gap: 8px;
    }
    .status-pill.filled { background: rgba(52,199,89,0.1); border-color: rgba(52,199,89,0.3); color: var(--ios-green); }
    .status-pill.pending { background: rgba(255,149,0,0.1); border-color: rgba(255,149,0,0.3); color: var(--ios-orange); }
    
    /* Trace */
    .trace-node {
        padding: 12px 16px; margin: 8px 0; background: rgba(120,120,128,0.08);
        border-radius: 12px; border-left: 3px solid var(--ios-blue);
        font-family: 'SF Mono', monospace; font-size: 0.85rem;
    }
    .trace-ok { border-left-color: var(--ios-green); }
    .trace-wait { border-left-color: var(--ios-orange); }
    
    .bento-grid {
        display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; margin-top: 16px;
    }
    .stat-box {
        background: rgba(120,120,128,0.06); border-radius: 16px;
        padding: 16px; text-align: center; border: 1px solid rgba(120,120,128,0.1);
    }
    .stat-number { font-size: 1.8rem; font-weight: 700; color: var(--ios-blue); }
    .stat-label { font-size: 0.75rem; color: var(--ios-gray); margin-top: 4px; text-transform: uppercase; }
</style>
"""

st.markdown(APPLE_CSS, unsafe_allow_html=True)

API_BASE_URL = os.getenv("BACKEND_URL", "https://hushh-backend-uc5w.onrender.com")
API_URL = f"{API_BASE_URL}/agents/run"

# CRITICAL FIELDS - Only these trigger cross-questioning
REQUIRED_FIELDS = ["size", "budget", "color", "occasion"]

def load_user_profile():
    return {
        "user_id": "ankit_01", "name": "Ankit",
        "memory": {
            "preferences": ["organic cotton", "minimalist", "size 9", "earth tones"],
            "avoid_keywords": ["neon", "polyester", "slim-fit", "chunky"],
            "brand_affinity": ["StepClean", "Heritage", "SummerBreeze"]
        },
        "closet": [
            {"name": "Dark Indigo Jeans", "category": "bottom"},
            {"name": "White Oxford Shirt", "category": "top"},
            {"name": "Beige Chinos", "category": "bottom"}
        ],
        "stats": {"items_owned": 12, "searches_made": 48, "saved_items": 5}
    }

def extract_entities(text):
    """Extract critical attributes from user message"""
    entities = {}
    text_lower = text.lower()
    
    # Size extraction (numeric or S/M/L/XL)
    size_patterns = [
        r'\bsize\s*(\d+|s|m|l|xl|xxl)\b',
        r'\b(us|uk|eu)\s*(\d+)\b',
        r'\b(\d+)(?:\s|$)(?!\s*(?:inr|rs|₹|dollars|usd))\b'  # Number not followed by currency
    ]
    for pattern in size_patterns:
        match = re.search(pattern, text_lower)
        if match:
            entities["size"] = match.group(1) if match.group(1) else match.group(2)
            break
    
    # Budget extraction
    budget_patterns = [
        r'(?:under|below|max|maximum|up to|budget of|around|about)\s*(?:₹|rs\.?|inr)?\s*(\d+)',
        r'(\d+)\s*(?:₹|rs\.?|inr)',
        r'(\d+)\s*budget',
        r'budget\s*(\d+)'
    ]
    for pattern in budget_patterns:
        match = re.search(pattern, text_lower)
        if match:
            entities["budget"] = int(match.group(1))
            break
    
    # Color extraction
    colors = ["white", "black", "blue", "red", "green", "brown", "beige", "navy", "grey", "gray", "pink", "yellow", "purple", "orange"]
    for color in colors:
        if color in text_lower:
            entities["color"] = color
            break
    
    # Occasion extraction
    occasions = ["casual", "formal", "party", "wedding", "office", "sports", "running", "gym", "daily", "work", "interview", "date"]
    for occasion in occasions:
        if occasion in text_lower:
            entities["occasion"] = occasion
            break
            
    return entities

def get_missing_fields(collected):
    """Return list of missing critical fields"""
    return [field for field in REQUIRED_FIELDS if field not in collected or not collected[field]]

def generate_question(field):
    """Generate specific question for missing field"""
    questions = {
        "size": "What size do you wear?",
        "budget": "What's your budget range? (e.g., under 2000, around 3000)",
        "color": "Any specific color preference?",
        "occasion": "What's the occasion? (casual, formal, office, etc.)"
    }
    return questions.get(field, f"Could you specify your {field}?")

def get_quick_options(field):
    """Get quick answer buttons for common fields"""
    options = {
        "size": ["7", "8", "9", "10", "11", "S", "M", "L", "XL"],
        "budget": ["Under ₹1000", "₹1000-₹2000", "₹2000-₹3000", "₹3000-₹5000", "No limit"],
        "color": ["White", "Black", "Blue", "Beige", "Navy", "Don't care"],
        "occasion": ["Casual daily", "Office/Formal", "Party/Event", "Sports", "Wedding"]
    }
    return options.get(field, [])

# --- SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "collected_attrs" not in st.session_state:
    st.session_state.collected_attrs = {}
if "current_question_field" not in st.session_state:
    st.session_state.current_question_field = None
if "show_results" not in st.session_state:
    st.session_state.show_results = False
if "last_products" not in st.session_state:
    st.session_state.last_products = []
if "is_thinking" not in st.session_state:
    st.session_state.is_thinking = False

# --- SIDEBAR ---
with st.sidebar:
    user = load_user_profile()
    
    st.markdown(f"""
    <div style="text-align: center; margin-bottom: 24px;">
        <div class="profile-avatar">{user['name'][0]}</div>
        <h2 style="margin: 8px 0 4px; font-weight: 600; color: #1C1C1E;">{user['name']}</h2>
        <p style="color: #8E8E93; font-size: 0.9rem;">@{user['user_id']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Status Panel
    st.markdown('<div class="glass-panel" style="padding: 16px;">', unsafe_allow_html=True)
    st.markdown("<h4 style='margin-top:0; font-size:0.9rem; color:#8E8E93;'>SESSION STATUS</h4>", unsafe_allow_html=True)
    
    missing = get_missing_fields(st.session_state.collected_attrs)
    for field in REQUIRED_FIELDS:
        status = "filled" if field in st.session_state.collected_attrs else "pending"
        icon = "✓" if status == "filled" else "○"
        value = st.session_state.collected_attrs.get(field, "Needed")
        if status == "filled":
            st.markdown(f'<div class="status-pill filled">{icon} <b>{field.title()}:</b> {value}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="status-pill pending">{icon} <b>{field.title()}</b></div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Memory Section
    with st.expander("🧠 Permanent Memory", expanded=True):
        st.markdown('<div class="chip-container">', unsafe_allow_html=True)
        for pref in user['memory']['preferences']:
            st.markdown(f'<span class="memory-chip chip-pref">✓ {pref}</span>', unsafe_allow_html=True)
        for brand in user['memory']['brand_affinity']:
            st.markdown(f'<span class="memory-chip chip-brand">★ {brand}</span>', unsafe_allow_html=True)
        for avoid in user['memory']['avoid_keywords']:
            st.markdown(f'<span class="memory-chip chip-avoid">✕ {avoid}</span>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Current Session Attributes
    with st.expander("⚡ Current Context"):
        if st.session_state.collected_attrs:
            for k, v in st.session_state.collected_attrs.items():
                st.markdown(f'<span class="memory-chip chip-status">{k}: {v}</span>', unsafe_allow_html=True)
        else:
            st.caption("No attributes collected yet")

# --- MAIN INTERFACE ---
st.markdown("""
<div style="text-align: center; margin-bottom: 32px;">
    <h1 style="font-weight: 700; letter-spacing: -0.02em; color: #1C1C1E; margin-bottom: 8px;">
        Personal Shopping Concierge
    </h1>
    <p style="color: #8E8E93; font-size: 1.1rem; margin: 0;">
        Minimal questions. Maximum relevance.
    </p>
</div>
""", unsafe_allow_html=True)

chat_col, trace_col = st.columns([2, 1])

with chat_col:
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    
    # Display conversation
    for i, msg in enumerate(st.session_state.messages):
        bubble_class = "msg-user" if msg["role"] == "user" else "msg-agent"
        st.markdown(f'<div class="message-bubble {bubble_class}">{msg["content"]}</div>', unsafe_allow_html=True)
    
    # Show collected attributes summary if we have them
    if st.session_state.collected_attrs and not st.session_state.show_results:
        attrs_text = " | ".join([f"{k}: {v}" for k, v in st.session_state.collected_attrs.items()])
        st.markdown(f"""
        <div style="background: rgba(0,122,255,0.05); border-radius: 12px; padding: 12px 16px; 
                    margin: 12px 0; border-left: 3px solid var(--ios-blue); font-size: 0.9rem; color: #555;">
            <b>Understood:</b> {attrs_text}
        </div>
        """, unsafe_allow_html=True)
    
    # Show SINGLE question if we have one pending
    if st.session_state.current_question_field and not st.session_state.show_results:
        field = st.session_state.current_question_field
        question = generate_question(field)
        quick_opts = get_quick_options(field)
        
        st.markdown(f"""
        <div class="question-card">
            <div class="question-text">🤔 {question}</div>
            <div style="color: #8E8E93; font-size: 0.85rem; margin-bottom: 12px;">
                (Question {list(REQUIRED_FIELDS).index(field) + 1} of {len(REQUIRED_FIELDS)})
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Quick option buttons
        cols = st.columns(min(len(quick_opts), 3))
        for idx, opt in enumerate(quick_opts):
            with cols[idx % 3]:
                if st.button(opt, key=f"opt_{field}_{opt}", use_container_width=True):
                    # Parse the option
                    if field == "budget":
                        if "Under" in opt:
                            val = 1000
                        elif "No limit" in opt:
                            val = 10000
                        else:
                            val = int(opt.replace("₹", "").split("-")[0])
                        st.session_state.collected_attrs[field] = val
                    else:
                        st.session_state.collected_attrs[field] = opt.lower().replace(" daily", "").replace("/formal", "")
                    
                    st.session_state.messages.append({"role": "user", "content": opt})
                    st.session_state.current_question_field = None
                    st.rerun()
    
    # Show products if ready
    if st.session_state.show_results and st.session_state.last_products:
        st.markdown("""
        <div style="background: linear-gradient(135deg, rgba(52,199,89,0.1) 0%, rgba(52,199,89,0.05) 100%); 
                    border: 2px solid rgba(52,199,89,0.3); border-radius: 16px; padding: 16px; margin: 20px 0;">
            <h3 style="margin: 0; color: var(--ios-green); font-weight: 600;">✓ Perfect! Here are your matches</h3>
            <p style="margin: 4px 0 0 0; color: #666; font-size: 0.9rem;">
                Based on: {attrs}
            </p>
        </div>
        """.format(attrs=" | ".join([f"{k}: {v}" for k, v in st.session_state.collected_attrs.items()])), unsafe_allow_html=True)
        
        st.markdown('<div class="product-grid">', unsafe_allow_html=True)
        for item in st.session_state.last_products[:6]:  # Max 6 as per your logic.py
            st.markdown(f"""
            <div class="product-card">
                <div class="product-image-placeholder">👟</div>
                <div class="match-score">{int(item.get('match_score', 0.9)*100)}% Match</div>
                <div class="product-info">
                    <h4 style="margin: 0 0 4px; font-weight: 600; color: #1C1C1E;">{item.get('title', 'Product')}</h4>
                    <p style="margin: 0; color: var(--ios-blue); font-weight: 600; font-size: 1.1rem;">
                        ₹{item.get('price_inr', 'N/A')}
                    </p>
                    <p style="margin: 8px 0 0; color: #8E8E93; font-size: 0.85rem;">
                        {item.get('why_recommended', 'Matches your style profile')}
                    </p>
                </div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        if st.button("🔄 Start New Search", use_container_width=True):
            st.session_state.collected_attrs = {}
            st.session_state.current_question_field = None
            st.session_state.show_results = False
            st.session_state.last_products = []
            st.session_state.messages = []
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Input handling
    if prompt := st.chat_input("Tell me what you're looking for..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Extract what we can from the message
        extracted = extract_entities(prompt)
        st.session_state.collected_attrs.update(extracted)
        
        # Check what's missing
        missing = get_missing_fields(st.session_state.collected_attrs)
        
        if missing:
            # Ask only the first missing one
            st.session_state.current_question_field = missing[0]
            st.session_state.show_results = False
        else:
            # All fields collected - fetch results immediately
            st.session_state.is_thinking = True
            st.session_state.show_results = True
        
        st.rerun()

with trace_col:
    st.markdown('<div class="glass-panel" style="height: 600px; overflow-y: auto;">', unsafe_allow_html=True)
    st.markdown("<h3 style='margin-top:0; font-weight: 600;'>🕵️ Agent Trace</h3>", unsafe_allow_html=True)
    
    # Show reasoning steps based on current state
    steps = [
        ("Intent Analysis", "Extracting entities from message", "trace-ok" if st.session_state.collected_attrs else "trace-wait"),
        ("Critical Fields", f"Missing: {get_missing_fields(st.session_state.collected_attrs)}", "trace-wait" if get_missing_fields(st.session_state.collected_attrs) else "trace-ok"),
        ("Cross-Questioning", f"Asking: {st.session_state.current_question_field or 'None'}", "trace-wait" if st.session_state.current_question_field else "trace-ok"),
        ("Search", "Querying catalog" if st.session_state.is_thinking else "Waiting", "trace-wait" if st.session_state.is_thinking else ""),
        ("Results", f"Found {len(st.session_state.last_products)} items" if st.session_state.last_products else "Pending", "trace-ok" if st.session_state.last_products else "")
    ]
    
    for title, detail, css_class in steps:
        if css_class:
            st.markdown(f"""
            <div class="trace-node {css_class}">
                <strong>{title}</strong><br/>
                <span style="color: #8E8E93; font-size: 0.8rem;">{detail}</span>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# --- BACKEND CALL ---
if st.session_state.is_thinking and st.session_state.show_results:
    try:
        time.sleep(0.5)  # Visual feedback
        
        # Construct rich query from collected attributes
        search_context = " ".join([
            st.session_state.collected_attrs.get("color", ""),
            st.session_state.collected_attrs.get("occasion", ""),
            "sneakers"  # default or extract from original message
        ]).strip()
        
        response = requests.post(API_URL, json={
            "user_id": "ankit_01",
            "message": search_context,
            "context": st.session_state.collected_attrs  # Send full context if backend supports it
        })
        data = response.json()
        
        st.session_state.last_products = data.get("results", [])
        st.session_state.is_thinking = False
        
        # If backend returned clarifying questions but we already have all fields, ignore them
        if data.get("clarifying_questions") and not get_missing_fields(st.session_state.collected_attrs):
            pass
            
        st.rerun()
        
    except Exception as e:
        st.session_state.is_thinking = False
        st.error(f"Connection error: {e}")

st.markdown("""
<div style="text-align: center; margin-top: 40px; color: #8E8E93; font-size: 0.8rem;">
    <p>Smart questioning • Memory aware • Minimal friction</p>
</div>
""", unsafe_allow_html=True)