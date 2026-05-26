import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.memory import InMemoryMemoryService
from google.genai import types
from agent import github_card_agent

app = FastAPI(title="GitHub Dev Card Generator")

# 1. Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Setup ADK Services (Local InMemory)
session_service = InMemorySessionService()
memory_service = InMemoryMemoryService()

# 3. Initialize Runner
runner = Runner(
    app_name="github_dev_card",
    agent=github_card_agent,
    session_service=session_service,
    memory_service=memory_service
)

# Ensure static directory exists
os.makedirs("static/cards", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

class CardRequest(BaseModel):
    username: str

@app.post("/generate")
async def generate_dev_card(request: CardRequest):
    """
    Triggers the agentic workflow to generate and save a dev card.
    """
    username = request.username
    user_id = f"user_{username}" # Simple user mapping
    
    # Create or reuse a session for the user
    session = await session_service.create_session(
        app_name="github_dev_card",
        user_id=user_id
    )

    try:
        # Run the agent
        events = runner.run_async(
            session_id=session.id,
            user_id=user_id,
            new_message=types.Content(role="user", parts=[types.Part(text=f"Generate a dev card for {username}")])
        )

        final_text = ""
        async for event in events:
            if hasattr(event, 'text') and event.text:
                final_text += event.text

        # Extract facts/memories from this session for future use
        await memory_service.add_session_to_memory(session)

        # The agent is instructed to save the card.
        card_url = f"/static/cards/{username}.html"
        
        # Check if file actually exists
        if not os.path.exists(f"static/cards/{username}.html"):
            raise HTTPException(status_code=500, detail="Agent failed to save the card.")

        return {
            "username": username,
            "card_url": card_url,
            "agent_response": final_text
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/card/{username}")
async def get_card(username: str):
    """
    Serves a saved card directly.
    """
    path = f"static/cards/{username}.html"
    if os.path.exists(path):
        return FileResponse(path)
    raise HTTPException(status_code=404, detail="Card not found")

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
