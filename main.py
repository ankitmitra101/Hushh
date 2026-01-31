import os
import json
import time
import traceback
import sys
from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from contextlib import asynccontextmanager
from dotenv import load_dotenv
load_dotenv()
groq_key = os.getenv("GROQ_API_KEY")
openai_key = os.getenv("OPENAI_API_KEY")
print(f"DEBUG: GROQ_API_KEY loaded: {bool(groq_key)}")
if groq_key:
    print(f"DEBUG: Groq Key starts with: {groq_key[:10]}...")
print(f"DEBUG: OPENAI_API_KEY loaded: {bool(openai_key)}")

from agent_core.logic import ShoppingAgent
from agent_core.fashion_logic import FashionStylistAgent
from fastapi.middleware.cors import CORSMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    os.makedirs("data", exist_ok=True)
    for filename in ["memory.json", "catalog.json", "closet.json"]:
        path = os.path.join("data", filename)
        if not os.path.exists(path):
            with open(path, "w") as f:
                json.dump([] if filename != "catalog.json" else [
                    {
                        "product_id": "snkr-001", 
                        "title": "Default Slim Sneaker", 
                        "price_inr": 2000, 
                        "size": "9", 
                        "style_keywords": ["minimal", "white"]
                    }
                ], f)
    yield

app = FastAPI(title="Hushh Power Agent Platform", lifespan=lifespan)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AgentRequest(BaseModel):
    user_id: str
    message: str
    session_id: str = None  # Optional session ID for conversation tracking

class ClearConversationRequest(BaseModel):
    session_id: str

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    print(f"Path: {request.url.path} | Duration: {process_time:.4f}s")
    return response

@app.post("/agents/run")
async def run_agent(request: AgentRequest):
    try:
        msg = request.message.lower()
        session_id = request.session_id or request.user_id  # Use session_id if provided
        
        # Intent routing
        if any(word in msg for word in ["style", "match", "wear with", "advice", "look"]):
            print(f"--- ROUTING TO: FashionStylistAgent ---")
            agent = FashionStylistAgent(user_id=request.user_id)
            response = await agent.process_request(request.message)
        else:
            print(f"--- ROUTING TO: ShoppingAgent (session: {session_id}) ---")
            agent = ShoppingAgent(user_id=request.user_id, session_id=session_id)
            response = await agent.process_request(request.message)
        
        return response

    except ExceptionGroup as eg:
        print("\n" + "!"*60)
        print("DIAGNOSTIC: UNPACKING TASKGROUP ERRORS")
        for i, error in enumerate(eg.exceptions):
            print(f"\n[SUB-ERROR {i+1}]:")
            traceback.print_exception(type(error), error, error.__traceback__)
        print("!"*60 + "\n")
        
        raise HTTPException(
            status_code=500, 
            detail={"error": "TaskGroup loop failed", "sub_errors": [str(e) for e in eg.exceptions]}
        )
    except Exception as e:
        print(f"CRITICAL ERROR: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500, 
            detail={"error": "General Agent failure", "trace": str(e)}
        )

@app.post("/agents/clear")
async def clear_conversation(request: ClearConversationRequest):
    """Clear conversation history for a session - used when starting a new chat."""
    success = ShoppingAgent.clear_conversation(request.session_id)
    return {
        "success": success,
        "message": "Conversation cleared" if success else "No conversation found for this session",
        "session_id": request.session_id
    }

@app.get("/agents/session/{session_id}")
async def get_session_info(session_id: str):
    """Get info about a conversation session."""
    count = ShoppingAgent.get_conversation_count(session_id)
    return {
        "session_id": session_id,
        "message_count": count,
        "has_history": count > 0
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "platform": "hushh-power-agent-mvp"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)