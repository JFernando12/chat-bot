from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel, Field
from application.services.chat_service import chat_service

router = APIRouter(tags=["chat"])

class ChatMessage(BaseModel):
    user_input: str = Field(..., description="Mensaje del usuario")

class ChatResponse(BaseModel):
    answer: str

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: Request, body: ChatMessage):
    """Conversación general con el agente."""
    try:
        answer = chat_service.process_message(body.user_input)
        
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
