from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str
    handled: bool

@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    return ChatResponse(reply=f"Hello {request.message}", handled=True)