import os
import json
from openai import OpenAI
from agent_core.base import BaseAgent

class FashionStylistAgent(BaseAgent):
    def __init__(self, user_id: str):
        super().__init__(user_id)
        # Using Groq for high-speed style advice
        self.client = OpenAI(
            api_key=os.getenv("GROQ_API_KEY") or os.getenv("OPENAI_API_KEY"),
            base_url="https://api.groq.com/openai/v1"
        )

    def _load_closet(self):
        """Helper to load the user's current wardrobe."""
        path = os.path.join("data", "closet.json")
        if not os.path.exists(path):
            return []
        try:
            with open(path, "r") as f:
                data = json.load(f)
                # If data is a list (fallback), we might need to handle it
                if isinstance(data, list):
                    return data # Basic fallback
                return data.get(self.user_id, [])
        except (json.JSONDecodeError, AttributeError):
            return []

    async def process_request(self, message: str):
        """
        Async implementation to match the ShoppingAgent signature.
        """
        # 1. Fetch user's existing clothes
        closet = self._load_closet()
        closet_summary = json.dumps(closet) if closet else "Empty Wardrobe"
        
        print(f"[TRACE {self.trace_id}] Analyzing style with closet items: {len(closet)}")

        # 2. Reasoning: Match the request with owned items using LLM
        try:
            system_prompt = (
                "You are an expert Fashion Stylist. You help users style their existing clothes "
                "or suggest how new items might match what they already own. "
                f"USER CLOSET: {closet_summary}. "
                "\n\n=== RULES ==="
                "\n1. Be helpful, concise, and trendy."
                "\n2. Refer to specific items in the user's closet if relevant."
                "\n3. If the closet is empty, give general advice."
                "\n4. ALWAYS return a JSON response."
                "\n\n=== OUTPUT FORMAT (JSON ONLY) ==="
                "\n{"
                '\n  "advice": "your fashion advice string",\n'
                '  "referenced_items": ["item1_id", "item2_id"]\n'
                "}"
            )

            response = self.client.chat.completions.create(
                model="llama-3.1-8b-instant", # Faster model for quick advice
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                response_format={"type": "json_object"}
            )
            
            brain = json.loads(response.choices[0].message.content)
            advice = brain.get("advice", "I'm having trouble finding the perfect match right now, but a classic look always works!")
            referenced_ids = brain.get("referenced_items", [])
            
            # Map referenced IDs back to full items for the UI
            referenced_items = [i for i in closet if i.get("product_id") in referenced_ids]

            return {
                "agent": "fashion_stylist_agent",
                "trace_id": self.trace_id,
                "understood_request": {"intent": "styling_advice"},
                "results": [{"advice": advice, "owned_items_referenced": referenced_items}],
                "next_actions": [{"action": "VIEW_STYLING_GUIDE"}]
            }

        except Exception as e:
            print(f"[ERROR] FashionStylistAgent LLM failure: {e}")
            return {
                "agent": "fashion_stylist_agent",
                "trace_id": self.trace_id,
                "error": str(e),
                "results": [{"advice": "Styling service temporarily unavailable.", "owned_items_referenced": []}]
            }
