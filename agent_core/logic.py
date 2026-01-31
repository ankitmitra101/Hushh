import os
import json
import sys
import asyncio
import traceback
from openai import OpenAI
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from agent_core.base import BaseAgent

load_dotenv()

class ShoppingAgent(BaseAgent):
    # Class-level conversation history per user session
    _conversations = {}
    
    def __init__(self, user_id: str, session_id: str = None):
        super().__init__(user_id)
        self.session_id = session_id or user_id  # Use session_id if provided
        
        # Using Groq for high-speed, free-tier reasoning
        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url="https://api.groq.com/openai/v1"
        )
        # Initialize conversation history for this session if not exists
        if self.session_id not in ShoppingAgent._conversations:
            ShoppingAgent._conversations[self.session_id] = []

    @classmethod
    def clear_conversation(cls, session_id: str):
        """Clear conversation history for a specific session."""
        if session_id in cls._conversations:
            del cls._conversations[session_id]
            return True
        return False

    @classmethod
    def get_conversation_count(cls, session_id: str):
        """Get number of messages in a session."""
        return len(cls._conversations.get(session_id, []))

    async def process_request(self, message: str):
        print(f"[TRACE {self.trace_id}] THOUGHT: Initiating PSC end-to-end loop.")
        print(f"[DEBUG] Session: {self.session_id}, History count: {len(ShoppingAgent._conversations.get(self.session_id, []))}", file=sys.stderr)
        
        base_path = os.getcwd()
        server_script = os.path.abspath(os.path.join(base_path, "mcp_server", "server.py"))
        server_params = StdioServerParameters(
            command=sys.executable,
            args=["-u", server_script],
            env=os.environ.copy()
        )

        try:
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    
                    # 1. READ MEMORY: Fetch user preferences via MCP
                    user_mem_res = await session.call_tool("read_memory", arguments={"user_id": self.user_id})
                    user_mem = self._parse_mcp_content(user_mem_res)
                    facts = user_mem.get("facts", [])

                    # 2. PARSE REQUEST: Improved prompt for category extraction
                    system_prompt = self._build_system_prompt(facts)
                    
                    # Build messages with conversation history for THIS session
                    conversation = ShoppingAgent._conversations.get(self.session_id, [])
                    messages = [{"role": "system", "content": system_prompt}]
                    
                    # Add conversation history (last 10 messages for context)
                    for turn in conversation[-10:]:
                        messages.append(turn)
                    
                    # Add current user message
                    messages.append({"role": "user", "content": message})
                    
                    print(f"[DEBUG] Sending {len(messages)} messages to LLM", file=sys.stderr)
                    
                    response = self.client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=messages,
                        response_format={"type": "json_object"}
                    )
                    brain = json.loads(response.choices[0].message.content)
                    print(f"[DEBUG] AI Brain: {json.dumps(brain)}", file=sys.stderr)
                    
                    # Save conversation turn for this session
                    ShoppingAgent._conversations[self.session_id].append({"role": "user", "content": message})
                    ShoppingAgent._conversations[self.session_id].append({"role": "assistant", "content": response.choices[0].message.content})

                    # 3. SEARCH PRODUCTS: Call tool with filters
                    search_query = brain.get("query") or message
                    budget = brain.get("budget", 10000)  # Higher default budget
                    category = brain.get("category", None)
                    size = brain.get("size", None)  # Extract size from AI
                    
                    # Normalize category with synonyms
                    category = self._normalize_category(category, message)
                    
                    # Standardize avoid list
                    avoid = brain.get("avoid_keywords", [])
                    if isinstance(avoid, str):
                        avoid = avoid.split()
                    
                    print(f"[DEBUG] Searching - Query: {search_query}, Category: {category}, Size: {size}, Avoid: {avoid}", file=sys.stderr)

                    search_res = await session.call_tool("search_products", arguments={
                        "query": search_query, 
                        "budget_max": budget,
                        "avoid_keywords": avoid,
                        "category": category,
                        "size": size  # Pass size to search
                    })
                    
                    products = self._parse_mcp_content(search_res)
                    if isinstance(products, dict): 
                        products = products.get("products", [])

                    # 4. GET DETAILS: Hydrate results with full metadata
                    final_results = []
                    if products:
                        for p in products[:6]:
                            pid = p.get("product_id")
                            if pid:
                                detail_res = await session.call_tool("get_product_details", arguments={"product_id": pid})
                                final_results.append(self._parse_mcp_content(detail_res))

                    # 5. SAVE SHORTLIST
                    shortlist_ids = [r.get("product_id") for r in final_results[:2]]
                    await session.call_tool("save_shortlist", arguments={"user_id": self.user_id, "items": shortlist_ids})

                    # 6. WRITE MEMORY: Update persistent facts
                    new_facts = brain.get("new_facts", [])
                    if new_facts:
                        await session.call_tool("write_memory", arguments={"user_id": self.user_id, "facts": new_facts})
                    
                    # 7. RETURN STRUCTURED JSON
                    return self._format_ui_response(brain, final_results, category)

        except Exception as e:
            print(f"[TRACE {self.trace_id}] ERROR:")
            traceback.print_exc(file=sys.stderr)
            return {"agent": "personal_shopping_concierge", "trace_id": self.trace_id, "error": str(e), "results": []}

    def _build_system_prompt(self, facts):
        """Build a generalized system prompt for any product category."""
        return (
            f"You are a Personal Shopping Concierge helping users find ANY type of product. "
            f"USER HISTORY: {facts}. "
            "Your task is to understand what the user wants and extract search parameters. "
            "\n\nCATEGORY EXTRACTION (GENERALIZED):\n"
            "- Extract the CATEGORY from what the user is looking for\n"
            "- Categories can be ANYTHING: footwear, apparel, accessories, toys, electronics, food, books, etc.\n"
            "- Use the most general category name (e.g., 'footwear' not 'sneakers')\n"
            "- If user says 'shoes/sneakers/boots' → category = 'footwear'\n"
            "- If user says 'shirts/pants/clothes' → category = 'apparel'\n"
            "- If user says 'toys/games' → category = 'toys'\n"
            "- If user says 'food/snacks/groceries' → category = 'food'\n"
            "- If user says 'electronics/gadgets' → category = 'electronics'\n"
            "\nEXTRACT ALL PREFERENCES:\n"
            "- If user mentions avoid/no/don't like, put descriptors in 'avoid_keywords'\n"
            "- Extract budget if mentioned (in INR or any currency)\n"
            "- Extract size/quantity if mentioned\n"
            "\nReturn ONLY a JSON object:\n"
            "{\n"
            '  "query": "specific search terms",\n'
            '  "category": "general category name",\n'
            '  "budget": number or null,\n'
            '  "size": "size/quantity or null",\n'
            '  "avoid_keywords": ["word1", "word2"],\n'
            '  "new_facts": ["preferences to remember"],\n'
            '  "questions": ["clarifying questions if needed"]\n'
            "}"
        )

    def _normalize_category(self, category, message):
        """
        Generalized category normalization.
        Uses common synonym mappings but accepts ANY category the AI extracts.
        """
        if not category:
            return None
            
        category_lower = category.lower().strip()
        
        # Common synonym mappings to normalize similar terms
        # This is NOT restrictive - just normalizes common variations
        synonym_map = {
            # Footwear variations
            "shoes": "footwear", "shoe": "footwear", "sneakers": "footwear", 
            "sneaker": "footwear", "boots": "footwear", "sandals": "footwear",
            "runners": "footwear", "heels": "footwear", "loafers": "footwear",
            
            # Apparel variations  
            "clothes": "apparel", "clothing": "apparel", "shirts": "apparel",
            "shirt": "apparel", "t-shirts": "apparel", "t-shirt": "apparel",
            "tees": "apparel", "tee": "apparel", "pants": "apparel", 
            "jeans": "apparel", "dresses": "apparel", "jackets": "apparel",
            
            # Accessories variations
            "belts": "accessories", "bags": "accessories", "sunglasses": "accessories",
            "watches": "accessories", "jewelry": "accessories", "caps": "accessories",
            
            # Other common categories (expandable)
            "games": "toys", "gadgets": "electronics", "groceries": "food",
            "snacks": "food", "books": "books", "phones": "electronics"
        }
        
        # Return mapped synonym if exists, otherwise return as-is
        return synonym_map.get(category_lower, category_lower)

    def _parse_mcp_content(self, response):
        """Standardizes tool output parsing."""
        try:
            if hasattr(response, 'content') and response.content:
                raw_text = response.content[0].text
                return json.loads(raw_text)
            return response if isinstance(response, (dict, list)) else {}
        except Exception: 
            return {}

    def _format_ui_response(self, brain, results, normalized_category):
        """Format response for frontend UI."""
        avoided_str = ", ".join(brain.get("avoid_keywords", [])) if brain.get("avoid_keywords") else "unwanted styles"
        size_label = brain.get("size", "your size")

        return {
            "agent": "personal_shopping_concierge",
            "trace_id": self.trace_id,
            "clarifying_questions": brain.get("questions", []),
            "understood_request": {
                "category": normalized_category or brain.get("category", "unknown"),
                "constraints": {
                    "budget_inr_max": brain.get("budget", 10000),
                    "size": size_label,
                    "style_keywords": brain.get("style_filters", []),
                    "avoid_keywords": brain.get("avoid_keywords", []),
                    "category": normalized_category or brain.get("category", "unknown")
                }
            },
            "results": [
                {
                    "product_id": r.get("product_id"), 
                    "title": r.get("title"), 
                    "price_inr": r.get("price_inr"), 
                    "brand": r.get("brand", "Unknown"),
                    "category": r.get("category", "unknown"),
                    "match_score": 0.95, 
                    "pros": [f"Matches size {size_label}", f"Fits budget (₹{r.get('price_inr')})"],
                    "cons": ["Limited stock"],
                    "why_recommended": f"The {r.get('title')} is recommended because it matches your preferences."
                } for r in results
            ],
            "shortlist": [
                {"product_id": r.get("product_id"), "reason": "Best value match"} for r in results[:2]
            ],
            "message_count": len(ShoppingAgent._conversations.get(self.session_id, []))
        }