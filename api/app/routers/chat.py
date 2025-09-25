from fastapi import APIRouter
from pydantic import BaseModel

from ..core.config import settings
from ..services import retrieve_top_chunks

router = APIRouter()

class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str
    handled: bool

@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    q = request.message.strip()
    if not q:
        return ChatResponse(reply="Please ask a question about my resume.", handled=False)
    
    top_k = settings.retrieve_top_k
    threshold = settings.similarity_threshold
    result = retrieve_top_chunks(q, top_k=top_k)

    if not result.top_chunks:
        return ChatResponse(reply="I couldn't access the resume information. Please try again later.", handled=False)

    top = result.top_chunks[0]
    handled = top.score >= threshold
    
    return ChatResponse(reply=top.text, handled=handled)