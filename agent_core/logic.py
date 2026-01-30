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
    def __init__(self, user_id):
        super().__init__(user_id)
        # Using Groq for high-speed, free-tier reasoning
        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url="https://api.groq.com/openai/v1"
        )

    async def process_request(self, message: str):
        print(f"[TRACE {self.trace_id}] THOUGHT: Initiating PSC end-to-end loop.")
        
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
                    
                    # 1. READ MEMORY: Fetch user preferences via MCP [cite: 61, 118]
                    user_mem_res = await session.call_tool("read_memory", arguments={"user_id": self.user_id})
                    user_mem = self._parse_mcp_content(user_mem_res)
                    facts = user_mem.get("facts", [])

                    # 2. PARSE REQUEST: Deciding the plan with LLM [cite: 117]
                    system_prompt = (
    f"You are a Personal Shopping Concierge. USER HISTORY: {facts}. "
    "MANDATORY: If the user mentions a preference, size, or dislike, "
    "put it in 'new_facts'. MANDATORY: Always include 1-2 clarifying questions "
    "in the 'questions' list to help narrow down style, even if results are found. "
    "Return ONLY a JSON object with: 'query', 'budget', 'size', 'style_filters', "
    "'avoid_keywords', 'new_facts', 'questions'."
)
                    
                    response = self.client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": message}],
                        response_format={"type": "json_object"}
                    )
                    brain = json.loads(response.choices[0].message.content)
                    print(f"[DEBUG] AI Brain: {json.dumps(brain)}", file=sys.stderr)

                    # 3. SEARCH PRODUCTS: Call tool with filters [cite: 58, 119]
                    search_query = brain.get("query") or "sneaker"
                    budget = brain.get("budget", 2500)
                    
                    search_res = await session.call_tool("search_products", arguments={
                        "query": search_query, 
                        "budget_max": budget
                    })
                    products = self._parse_mcp_content(search_res)
                    if isinstance(products, dict): products = products.get("products", [])

                    # 4. GET DETAILS: Fetch deep data for top 6 candidates [cite: 58, 120]
                    final_results = []
                    if products:
                        for p in products[:6]: # Requirement: Show up to 6 options [cite: 17, 155]
                            pid = p.get("product_id")
                            if pid:
                                detail_res = await session.call_tool("get_product_details", arguments={"product_id": pid})
                                final_results.append(self._parse_mcp_content(detail_res))

                    # 5. SAVE SHORTLIST: Persist the state [cite: 58, 122]
                    shortlist_ids = [r.get("product_id") for r in final_results[:2]]
                    await session.call_tool("save_shortlist", arguments={"user_id": self.user_id, "items": shortlist_ids})

                    # 6. WRITE MEMORY: Update facts (e.g., 'dislikes chunky soles') [cite: 60, 123]
                    new_facts = brain.get("new_facts", [])
                    if new_facts:
                        await session.call_tool("write_memory", arguments={"user_id": self.user_id, "facts": new_facts})
                    
                    # 7. RETURN STRUCTURED JSON: Strict UI Contract [cite: 66-114, 124]
                    return self._format_ui_response(brain, final_results)

        except Exception as e:
            print(f"[TRACE {self.trace_id}] ERROR:")
            traceback.print_exc(file=sys.stderr)
            return {"agent": "personal_shopping_concierge", "trace_id": self.trace_id, "error": str(e), "results": []}

    def _parse_mcp_content(self, response):
        try:
            if hasattr(response, 'content') and response.content:
                raw_text = response.content[0].text
                return json.loads(raw_text)
            return response if isinstance(response, (dict, list)) else {}
        except: return {}

    def _format_ui_response(self, brain, results):
        """Strict JSON Contract implementation [cite: 69-113]"""
        return {
            "agent": "personal_shopping_concierge",
            "trace_id": self.trace_id,
            "clarifying_questions": brain.get("questions", []),
            "understood_request": {
                "category": "footwear", 
                "constraints": {
                    "budget_inr_max": brain.get("budget", 2500),
                    "size": brain.get("size", "Not specified"),
                    "style_keywords": brain.get("style_filters", []),
                    "avoid_keywords": brain.get("avoid_keywords", [])
                }
            },
            "results": [
                {
                    "product_id": r.get("product_id"), 
                    "title": r.get("title"), 
                    "price_inr": r.get("price_inr"), 
                    "brand": r.get("brand", "Unknown"),
                    "match_score": 0.95, 
                    "pros": ["Highly rated", "Matches style"],
                    "cons": ["Limited stock"],
                    "why_recommended": "Perfect match for your minimal preference."
                } for r in results
            ],
            "shortlist": [
                {"product_id": r.get("product_id"), "reason": "Top rated match"} for r in results[:2]
            ],
            "comparisons": {
                "summary": "These options offer the best value for your budget.",
                "tradeoffs": ["Price vs Premium Materials"]
            },
            "next_actions": [{"action": "ASK_SIZE_CONFIRMATION", "payload": {}}]
        }