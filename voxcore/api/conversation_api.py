"""
VoxCore Conversation API
Exposes the conversation layer as a REST API for chat UI integration.
"""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from voxcore.engine.conversation_manager import ConversationManager

app = FastAPI()
conversation_manager = ConversationManager()

@app.post("/api/conversation/message")
async def conversation_message(request: Request):
    data = await request.json()
    message = data.get("message")
    session_id = data.get("session_id")
    if not message or not session_id:
        return JSONResponse({"error": "Missing message or session_id"}, status_code=400)
    response = conversation_manager.handle_message(message, session_id)
    return response

# Example: To run with uvicorn
# uvicorn voxcore.api.conversation_api:app --reload
