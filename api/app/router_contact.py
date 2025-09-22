from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class ContactRequest(BaseModel):
    name: str
    email: str
    message: str


class ContactResponse(BaseModel):
    success: bool

@router.post("/contact", response_model=ContactResponse)
def contact(request: ContactRequest):
    return ContactResponse(success=True)