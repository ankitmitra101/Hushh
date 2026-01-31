import asyncio
import os
import json
from dotenv import load_dotenv

# Ensure we are in the right directory and load .env
load_dotenv()

# Add project root to sys.path
import sys
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.append(project_root)

from agent_core.logic import ShoppingAgent

async def live_test():
    print("--- STARTING LIVE GROQ API TEST ---")
    print(f"Checking environment: GROQ_API_KEY present? {bool(os.getenv('GROQ_API_KEY'))}")
    
    agent = ShoppingAgent(user_id="verification_user", session_id="test_session")
    
    test_message = "I want a blue cotton shirt under 2000"
    print(f"Sending test message: '{test_message}'")
    
    try:
        # We manually call the LLM part of process_request to verify the key
        # using the _build_system_prompt and self.client
        system_prompt = agent._build_system_prompt([])
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": test_message}
        ]
        
        print("Waiting for Groq response...")
        response = agent.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            response_format={"type": "json_object"}
        )
        
        content = response.choices[0].message.content
        print("\n--- LIVE RESPONSE RECEIVED ---")
        print(content)
        
        data = json.loads(content)
        if data.get("query") and "blue" in data.get("query").lower():
            print("\n✅ SUCCESS: Groq API key is WORKING perfectly.")
            print(f"Extracted Query: {data.get('query')}")
            print(f"Extracted Budget: {data.get('budget')}")
        else:
            print("\n⚠️ WARNING: Response received but data seems unexpected.")
            
    except Exception as e:
        print(f"\n❌ FAILURE: API Call failed!")
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(live_test())
