from fastapi import APIRouter, Form, Request
from fastapi.responses import Response
from twilio.twiml.messaging_response import MessagingResponse
from domain.chat import Conversation
from application.services.chat_service import chat_service

router = APIRouter(tags=["whatsapp"], prefix="/whatsapp")

# Memoria de conversaciones (demo)
_conversations = {}

@router.post("/webhook")
async def whatsapp_webhook(
    request: Request,
    From: str = Form(...),
    Body: str = Form(...)
):
    """
    Webhook que recibe mensajes desde Twilio WhatsApp Sandbox.
    """
    user_id = From
    user_msg = Body.strip()

    conv = _conversations.get(user_id, Conversation())
    answer = chat_service.process_message(user_msg, conv)
    conv.add_turn(user_msg, answer)
    _conversations[user_id] = conv

    response = MessagingResponse()
    response.message(answer)
    return Response(content=str(response), media_type="application/xml")
