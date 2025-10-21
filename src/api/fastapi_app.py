import logging
from fastapi import FastAPI

from api.routers.chat_router import router as chat_router
from api.routers.whatsapp_router import router as whatsapp_router

logger = logging.getLogger(__name__)

def create_app() -> FastAPI:
    app = FastAPI(
        title="Kavak AI Sales Agent",
        version="1.0",
        description="Agente comercial inteligente integrado con WhatsApp y LangGraph"
    )
    
    app.include_router(chat_router, prefix="/api")
    app.include_router(whatsapp_router, prefix="/api")

    return app

app = create_app()
