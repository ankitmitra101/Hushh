import streamlit as st
import requests
import json
import os
import time
import re
import uuid
from datetime import datetime

# Configuration & Theming
st.set_page_config(
    page_title="Hushh | AI Concierge",
    page_icon="◼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# [Keep all your CSS exactly as is...]
DARK_CSS = """
<style>
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
    html, body, .stApp, [data-testid="stAppViewContainer"] {
        background-color: var(--bg-primary) !important;
        color: var(--text-primary) !important;
    }
    [data-testid="stSidebar"] {
        background-color: var(--bg-secondary) !important;
        border-right: 1px solid var(--border) !important;
    }
    [data-testid="stSidebarContent"] {
        background-color: var(--bg-secondary) !important;
    }
    .main .block-container {
        background-color: var(--bg-primary) !important;
        padding-top: 2rem;
        max-width: 1400px;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        -webkit-font-smoothing: antialiased;
    }
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
    .profile-avatar {
        width: 72px; height: 72px; border-radius: 50%;
        background: linear-gradient(135deg, var(--accent-cyan) 0%, var(--accent-purple) 100%);
        display: flex; align-items: center; justify-content: center;
        color: #000; font-size: 28px; font-weight: 700;
        margin: 0 auto 16px;
        box-shadow: 0 0 20px rgba(0,212,255,0.3);
    }
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
    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-track { background: var(--bg-primary); }
    ::-webkit-scrollbar-thumb { background: #333; border-radius: 4px; }
    .stTextInput > div > div > input {
        background: var(--bg-card) !important;
        color: white !important;
        border: 1px solid var(--border) !important;
        border-radius: 12px !important;
    }
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
    .empty-state {
        color: var(--text-muted);
        font-style: italic;
        font-size: 0.9rem;
    }
</style>
"""

st.markdown(DARK_CSS, unsafe_allow_html=True)

# FIXED API CONFIGURATION - Removed trailing space and added rstrip
API_BASE_URL = os.getenv("BACKEND_URL", "https://hushh-backend-uc5w.onrender.com").strip().rstrip('/')
API_URL = f"{API_BASE_URL}/agents/run"

# --- DATA MANAGEMENT ---
def load_user_memory():
    """Load user memory from data/memory.json"""
    default_memory = {
        "user_id": "ankit_01",
        "name": "Ankit",
        "preferences": [],
        "avoid_keywords": [],
        "brand_affinity": [],
        "closet": []
    }
    
    try:
        if os.path.exists('data/memory.json'):
            with open('data/memory.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
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
        
        if os.path.exists('data/memory.json'):
            with open('data/memory.json', 'r', encoding='utf-8') as f:
                try:
                    existing_data = json.load(f)
                    if not isinstance(existing_data, list):
                        existing_data = [existing_data]
                except:
                    existing_data = []
        
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

def call_ai_agent(user_message: str):
    """
    Call the FastAPI backend with the ORIGINAL user message.
    Let the AI handle extraction, not local regex.
    """
    try:
        payload = {
            "user_id": "ankit_01",
            "message": user_message  # Send original text, not a dictionary!
        }
        
        # DEBUG: Show what we're sending
        st.session_state.debug_info = f"Connecting to: {API_URL}"
        
        # INCREASED TIMEOUT for Render free tier cold start (60s)
        response = requests.post(
            API_URL,
            json=payload,
            timeout=60,  # Changed from 30 to 60
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        return response.json()
        
    except requests.exceptions.Timeout:
        return {"error": "Backend is waking up (Render free tier). Please wait 30s and retry.", "agent": "error"}
    except requests.exceptions.ConnectionError as e:
        return {"error": f"Cannot reach backend. Is it running?", "agent": "error", "details": str(e)}
    except Exception as e:
        return {"error": f"Request failed: {str(e)}", "agent": "error"}

# --- SESSION STATE ---
defaults = {
    "messages": [],
    "collected": {},  # Will be populated from backend response
    "current_question": None,
    "show_results": False,
    "products": [],
    "thinking": False,
    "avoid_keywords": [],  # Will sync with backend
    "last_request": None,
    "last_response": None,
    "debug_info": None
}
for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

# Load memory on every rerun to get updates
USER_MEMORY = load_user_memory()
# Sync session state with saved memory
if "avoid_keywords" not in st.session_state or not st.session_state.avoid_keywords:
    st.session_state.avoid_keywords = USER_MEMORY.get("avoid_keywords", [])

# --- SIDEBAR ---
with st.sidebar:
    st.markdown(f"""
    <div style="text-align: center; padding: 20px 0;">
        <div class="profile-avatar">{USER_MEMORY['name'][0]}</div>
        <h2 style="margin: 0; font-size: 1.3rem; font-weight: 600; color: white;">{USER_MEMORY['name']}</h2>
        <p style="color: var(--text-muted); margin: 4px 0 0; font-size: 0.9rem;">@{USER_MEMORY['user_id']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # CONNECTION TEST PANEL - ADDED FOR DEBUGGING
    st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
    st.markdown("<h4 style='margin-top:0; color: var(--accent-orange); font-size: 0.9rem;'>🔌 CONNECTION TEST</h4>", unsafe_allow_html=True)
    
    # Show current URL being used
    st.markdown(f"<div style='font-size: 0.7rem; color: var(--text-muted); word-break: break-all;'>{API_URL}</div>", unsafe_allow_html=True)
    
    if st.button("Test Backend", use_container_width=True):
        with st.spinner("Checking..."):
            try:
                # Try to hit the health endpoint
                health_url = API_BASE_URL + "/health"
                r = requests.get(health_url, timeout=10)
                if r.status_code == 200:
                    st.success("✅ Backend is awake!")
                else:
                    st.error(f"⚠️ Status: {r.status_code}")
            except Exception as e:
                st.error(f"❌ {str(e)[:30]}...")
    
    # Show last debug info
    if st.session_state.get("debug_info"):
        st.markdown(f"<div style='font-size: 0.7rem; color: #666; margin-top: 8px;'>{st.session_state.debug_info}</div>", unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # RECENTLY AVOIDED SECTION - NOW DYNAMIC FROM BACKEND/STATE
    st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
    st.markdown("""
    <h4 style="margin-top:0; color: var(--accent-red); font-size: 0.9rem; text-transform: uppercase; letter-spacing: 0.05em;">
        ⛔ Recently Avoided
    </h4>
    """, unsafe_allow_html=True)
    
    # Use session state which gets updated from backend
    current_avoids = st.session_state.get("avoid_keywords", [])
    
    if current_avoids:
        st.markdown(f"<p style='color: var(--text-muted); font-size: 0.8rem; margin-bottom: 12px;'>{len(current_avoids)} active filters</p>", unsafe_allow_html=True)
        for avoid in current_avoids:
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"<div class='avoid-badge' style='margin: 2px 0;'>{avoid}</div>", unsafe_allow_html=True)
            with col2:
                if st.button("✕", key=f"remove_{avoid}"):
                    st.session_state.avoid_keywords.remove(avoid)
                    USER_MEMORY["avoid_keywords"] = st.session_state.avoid_keywords
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
    
    # Session Status - DYNAMIC FROM BACKEND
    st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
    st.markdown("<h4 style='margin-top:0; color: var(--accent-cyan); font-size: 0.9rem;'>SESSION STATUS</h4>", unsafe_allow_html=True)
    
    # Show what backend has collected
    constraints = st.session_state.collected.get("constraints", {})
    
    # Category
    if constraints.get("category") or st.session_state.collected.get("category"):
        cat = constraints.get("category") or st.session_state.collected.get("category")
        st.markdown(f'<div class="status-pill status-filled">✓ <b>Category:</b> {cat}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="status-pill status-pending">○ <b>Category</b> needed</div>', unsafe_allow_html=True)
    
    # Budget
    if constraints.get("budget_inr_max"):
        st.markdown(f'<div class="status-pill status-filled">✓ <b>Budget:</b> ₹{constraints["budget_inr_max"]}</div>', unsafe_allow_html=True)
    elif st.session_state.collected.get("budget"):
        st.markdown(f'<div class="status-pill status-filled">✓ <b>Budget:</b> ₹{st.session_state.collected["budget"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="status-pill status-pending">○ <b>Budget</b> needed</div>', unsafe_allow_html=True)
    
    # Size
    if constraints.get("size"):
        st.markdown(f'<div class="status-pill status-filled">✓ <b>Size:</b> {constraints["size"]}</div>', unsafe_allow_html=True)
    elif st.session_state.collected.get("size"):
        st.markdown(f'<div class="status-pill status-filled">✓ <b>Size:</b> {st.session_state.collected["size"]}</div>', unsafe_allow_html=True)
    
    # Style keywords
    if constraints.get("style_keywords"):
        styles = constraints["style_keywords"]
        if isinstance(styles, list):
            for style in styles:
                st.markdown(f'<div class="status-pill status-filled">✓ <b>Style:</b> {style}</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# --- MAIN INTERFACE ---
st.markdown("""
<div style="text-align: center; margin-bottom: 40px;">
    <h1 style="font-weight: 700; font-size: 2.2rem; margin-bottom: 8px; background: linear-gradient(90deg, var(--accent-cyan), var(--accent-purple)); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
        AI Shopping Concierge
    </h1>
    <p style="color: var(--text-muted); font-size: 1rem; margin: 0;">
        Powered by Groq AI • Smart filtering • Context aware
    </p>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([3, 1])

with col1:
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    
    # Messages
    for idx, msg in enumerate(st.session_state.messages):
        bubble_class = "msg-user" if msg["role"] == "user" else "msg-agent"
        st.markdown(f'<div class="message-bubble {bubble_class}">{msg["content"]}</div>', unsafe_allow_html=True)
        
        # Show clarifying questions if present
        if msg.get("questions"):
            st.markdown("<div style='margin: 0.5rem 0 1rem 2rem; padding: 1rem; background: rgba(0,212,255,0.05); border-radius: 12px; border-left: 3px solid var(--accent-cyan);'>", unsafe_allow_html=True)
            st.markdown("<div style='color: var(--accent-cyan); font-size: 0.8rem; margin-bottom: 0.5rem;'>FOLLOW-UP QUESTIONS</div>", unsafe_allow_html=True)
            for q in msg["questions"]:
                if st.button(f"💬 {q}", key=f"q_{idx}_{q[:20]}"):
                    st.session_state.messages.append({"role": "user", "content": q})
                    st.session_state.thinking = True
                    st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Show products
        if msg.get("products"):
            st.markdown('<div class="results-header"><h3 style="margin:0; color: var(--accent-green);">✓ Found these matches</h3></div>', unsafe_allow_html=True)
            st.markdown('<div class="product-grid">', unsafe_allow_html=True)
            for prod in msg["products"]:
                price = prod.get('price_inr', prod.get('price', 'N/A'))
                tags = prod.get("style_keywords", [])
                tags_html = "".join([f'<span class="tag">{kw}</span>' for kw in tags[:3]])
                match_score = prod.get('match_score', 0.95)
                
                st.markdown(f"""
                <div class="product-card">
                    <div class="product-image">👟<div class="match-badge">{int(match_score*100)}% MATCH</div></div>
                    <div class="product-info">
                        <div class="product-brand">{prod.get('brand', 'Unknown')}</div>
                        <div class="product-title">{prod.get('title', 'Product')}</div>
                        <div class="product-tags">{tags_html}</div>
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-top:12px;">
                            <span class="product-price">₹{price}</span>
                            <span style="color: var(--text-muted); font-size:0.8rem;">{prod.get('material', '')}</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Show why recommended
            if msg.get("avoided"):
                st.markdown(f"""
                <div style="margin-top: 1rem; padding: 1rem; background: rgba(255,71,87,0.1); border-radius: 8px; border: 1px solid rgba(255,71,87,0.2);">
                    <span style="color: var(--accent-red); font-size: 0.9rem;">
                        🚫 Filtered out items with: {', '.join(msg['avoided'])}
                    </span>
                </div>
                """, unsafe_allow_html=True)
    
    # Thinking indicator
    if st.session_state.thinking:
        st.markdown("""
        <div class="thinking">
            <span class="thinking-text">AI Agent analyzing...</span>
            <div class="dot"></div><div class="dot"></div><div class="dot"></div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Input area
    if not st.session_state.thinking:
        if prompt := st.chat_input("Tell me what you want (e.g., 'white sneakers under 2500, size 9, no chunky style')...")::
            st.session_state.messages.append({"role": "user", "content": prompt})
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
        ("API Connected", True, API_BASE_URL[:20] + "..."),
        ("AI Agent Active", True, "Groq LLM"),
        ("Memory Sync", len(st.session_state.avoid_keywords) > 0, f"{len(st.session_state.avoid_keywords)} avoided"),
        ("Last Query", st.session_state.last_request is not None, "Sent" if st.session_state.last_request else "Waiting"),
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
    
    # Show raw constraints from backend for debugging
    if st.session_state.collected:
        st.markdown("<div style='margin-top: 1rem; padding-top: 1rem; border-top: 1px solid var(--border);'>", unsafe_allow_html=True)
        st.markdown("<div style='color: var(--text-muted); font-size: 0.7rem; margin-bottom: 0.5rem;'>RAW CONSTRAINTS</div>", unsafe_allow_html=True)
        st.code(json.dumps(st.session_state.collected, indent=2), language="json")
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# --- BACKEND PROCESSING ---
if st.session_state.thinking:
    try:
        # Get the last user message
        last_user_msg = None
        for msg in reversed(st.session_state.messages):
            if msg["role"] == "user":
                last_user_msg = msg["content"]
                break
        
        if last_user_msg:
            # Call the AI backend with ORIGINAL user message
            result = call_ai_agent(last_user_msg)
            st.session_state.last_response = result
            
            if result:
                agent_type = result.get("agent", "")
                
                if "error" in result:
                    # IMPROVED ERROR MESSAGE for Render backend
                    error_msg = result['error']
                    if "waking up" in error_msg.lower() or "connection" in error_msg.lower():
                        error_msg += " Click 'Test Backend' in sidebar to wake it up."
                    
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": f"❌ {error_msg}"
                    })
                elif "fashion" in agent_type:
                    # Fashion Stylist Agent response
                    advice = result.get("results", [{}])[0].get("advice", "Here's my styling advice.")
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": advice,
                        "agent_type": "fashion"
                    })
                else:
                    # Shopping Agent response
                    understood = result.get("understood_request", {})
                    constraints = understood.get("constraints", {})
                    
                    # UPDATE SESSION STATE FROM BACKEND RESPONSE
                    st.session_state.collected = understood
                    
                    # Sync avoid keywords from backend response!
                    backend_avoids = constraints.get("avoid_keywords", [])
                    if backend_avoids:
                        st.session_state.avoid_keywords = list(set(st.session_state.avoid_keywords + backend_avoids))
                        USER_MEMORY["avoid_keywords"] = st.session_state.avoid_keywords
                        save_user_memory(USER_MEMORY)
                        st.toast(f"Avoiding: {', '.join(backend_avoids)}", icon="🚫")
                    
                    questions = result.get("clarifying_questions", [])
                    products = result.get("results", [])
                    
                    if questions and not products:
                        # Need more info
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": "I need a bit more information to find the perfect match:",
                            "questions": questions
                        })
                    else:
                        # Show results
                        avoid_display = backend_avoids if backend_avoids else st.session_state.avoid_keywords
                        msg_content = f"Found {len(products)} curated matches for you."
                        
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": msg_content,
                            "products": products,
                            "avoided": avoid_display,
                            "trace_id": result.get("trace_id", "")
                        })
                        
                        st.session_state.show_results = True
            else:
                # More descriptive error
                error_msg = "❌ Backend connection failed. "
                if "render.com" in API_URL:
                    error_msg += "Render backend may be sleeping. Click 'Test Backend' in sidebar to wake it up, then try again."
                else:
                    error_msg += "Check if backend is running on port 8000."
                
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": error_msg
                })
        else:
            st.session_state.messages.append({
                "role": "assistant",
                "content": "No message to process."
            })
            
    except Exception as e:
        st.error(f"Processing error: {e}")
        import traceback
        st.code(traceback.format_exc())
    
    finally:
        st.session_state.thinking = False
        st.rerun()

st.markdown("""
<div style="text-align: center; margin-top: 40px; color: var(--text-muted); font-size: 0.8rem;">
    <p>AI Agent • Smart Memory • Dynamic Filtering</p>
</div>
""", unsafe_allow_html=True)