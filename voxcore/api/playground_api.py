import uuid
from fastapi import APIRouter, Request
from pydantic import BaseModel
from voxcore.engine.conversation_manager import ConversationManager

# In-memory session store for demo (no login)
session_store = {}

# Safety limits
MAX_ROWS = 500
QUERY_TIMEOUT = 5  # seconds
SESSION_TIMEOUT = 1800  # 30 minutes

router = APIRouter()
conversation_manager = ConversationManager(demo_mode=True)

class PlaygroundRequest(BaseModel):
    session_id: str = None
    text: str

@router.post("/api/playground/query")
async def playground_query(request: PlaygroundRequest):
    # Session handling
    session_id = request.session_id or str(uuid.uuid4())
    session_store[session_id] = {
        'last_active': uuid.uuid1().time  # For timeout logic
    }
    # Route to conversation manager (demo mode)
    response = conversation_manager.handle_message(
        session_id=session_id,
        message=request.text,
        max_rows=MAX_ROWS,
        timeout=QUERY_TIMEOUT,
        demo_db=True
    )
    return {"session_id": session_id, **response}
