import asyncio
import os
from dotenv import load_dotenv
load_dotenv()

# Add parent dir to path for imports
import sys
sys.path.append(os.getcwd())

from agent_core.fashion_logic import FashionStylistAgent

async def test_stylist():
    print("Testing FashionStylistAgent...")
    agent = FashionStylistAgent(user_id="test_user")
    
    # Mock some closet data for the test_user
    os.makedirs("data", exist_ok=True)
    closet_path = os.path.join("data", "closet.json")
    
    test_closet = {
        "test_user": [
            {"product_id": "snkr-001", "title": "White Sneakers", "color": "white", "type": "footwear"},
            {"product_id": "jean-001", "title": "Blue Jeans", "color": "blue", "type": "apparel"}
        ]
    }
    
    with open(closet_path, "w") as f:
        import json
        json.dump(test_closet, f)

    response = await agent.process_request("What should I wear with my blue jeans?")
    print("\n--- AGENT RESPONSE ---")
    import json
    print(json.dumps(response, indent=2))
    
    if "results" in response and len(response["results"]) > 0:
        advice = response["results"][0].get("advice")
        if advice and len(advice) > 20: 
            print("\nSUCCESS: Received detailed styling advice from LLM!")
        else:
            print("\nFAILURE: Advice was empty or too short.")
    else:
        print("\nFAILURE: No results in response.")

if __name__ == "__main__":
    asyncio.run(test_stylist())
