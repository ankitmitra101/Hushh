import streamlit as st
import requests
import json
import os
import streamlit as st

# It will look for a RENDER_URL first; if not found, it uses the local one
API_BASE_URL = os.getenv("BACKEND_URL", "https://hushh-backend-uc5w.onrender.com")
API_URL = f"{API_BASE_URL}/agents/run"


st.set_page_config(page_title="PSC Agent Console", layout="wide")

# Custom CSS for a "Shopping App" look
st.markdown("""
    <style>
    .product-card { border: 1px solid #ddd; padding: 15px; border-radius: 10px; margin-bottom: 10px; background: #f9f9f9; }
    .shortlist-badge { background-color: #ff4b4b; color: white; padding: 2px 8px; border-radius: 5px; font-size: 0.8em; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛍️ Personal Shopping Concierge")

# --- SIDEBAR: AGENT TRACE ---
with st.sidebar:
    st.header("🧠 Agent Reasoning")
    if "last_trace" in st.session_state:
        st.json(st.session_state.last_trace)
    else:
        st.write("No active trace.")

# --- MAIN CHAT INTERFACE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display conversation
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User Input
if prompt := st.chat_input("What are you looking for today?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # API Call
    try:
        response = requests.post(API_URL, json={"user_id": "ankit_01", "message": prompt})
        data = response.json()
        st.session_state.last_trace = data # Update sidebar for demo
        
        with st.chat_message("assistant"):
            # 1. Handle Clarifying Questions
            if data.get("clarifying_questions"):
                for q in data["clarifying_questions"]:
                    st.warning(f"🤔 **Question:** {q}")
            
            # 2. Display Ranking and Explanation
            if data.get("comparisons"):
                st.info(f"💡 **Analysis:** {data['comparisons']['summary']}")
            
            # 3. Render Product Gallery (6 options)
            if data.get("results"):
                st.subheader("Top Matches")
                cols = st.columns(2)
                for i, item in enumerate(data["results"]):
                    with cols[i % 2]:
                        st.markdown(f"""
                        <div class="product-card">
                            <h4>{item['title']}</h4>
                            <p><b>Price:</b> ₹{item['price_inr']} | <b>Match:</b> {int(item['match_score']*100)}%</p>
                            <p style="color: green;">✅ {item['pros'][0]}</p>
                            <p style="color: gray; font-size: 0.9em;">{item['why_recommended']}</p>
                        </div>
                        """, unsafe_allow_html=True)

            # 4. Show Shortlist
            if data.get("shortlist"):
                st.success("📝 **Shortlist Saved:** These items were added to your profile for price tracking.")

    except Exception as e:
        st.error(f"Connection Error: {e}")