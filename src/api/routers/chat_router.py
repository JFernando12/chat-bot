from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel, Field
from typing import Any
from domain.chat import Conversation
from application.services.chat_service import chat_service

router = APIRouter(tags=["chat"])

class ChatMessage(BaseModel):
    user_input: str = Field(..., description="Mensaje del usuario")
    history: list[dict[str, str]] = Field(default_factory=list)

class ChatResponse(BaseModel):
    answer: str
    suggestions: list[dict[str, Any]] = []

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: Request, body: ChatMessage):
    """Conversación general con el agente."""
    conv = Conversation()
    for h in body.history:
        conv.add_turn(h.get("user", ""), h.get("assistant", ""))
    try:
        answer = chat_service.process_message(body.user_input, conv)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    conv.add_turn(body.user_input, answer)
    return {"answer": answer}
