from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import logging

from ..domain.models import ConversationState
from ..application.agent import KavakCommercialAgent
from ..infrastructure.repositories import CSVCarRepository
from ..infrastructure.whatsapp import whatsapp_service
from config.settings import env

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API Models
class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    user_id: str = Field(..., description="Unique user identifier")
    message: str = Field(..., min_length=1, max_length=1000, description="User message")

class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    response: str = Field(..., description="Agent response")
    user_id: str = Field(..., description="User identifier")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")
    conversation_stage: str = Field(..., description="Current conversation stage")
    success: bool = Field(..., description="Whether the request was successful")
    error: Optional[str] = Field(None, description="Error message if any")

class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str = Field(..., description="Service status")
    timestamp: datetime = Field(default_factory=datetime.now, description="Health check timestamp")
    version: str = Field(default="1.0.0", description="API version")
    services: dict[str, str] = Field(..., description="Status of dependent services")

class WhatsAppWebhook(BaseModel):
    """Model for WhatsApp webhook requests."""
    From: str = Field(..., description="Sender phone number")
    Body: str = Field(..., description="Message body")
    MessageSid: str = Field(..., description="Message ID")
    To: str = Field(..., description="Recipient phone number")

# Dependency injection
def get_agent() -> KavakCommercialAgent:
    """Get the commercial agent instance."""
    car_repository = CSVCarRepository(env.database_csv_path)
    
    agent = KavakCommercialAgent(
        car_repository=car_repository,
        openai_api_key=env.openai_api_key,
        model_name=env.openai_model,
        temperature=env.openai_temperature
    )
    
    return agent

# Create FastAPI app
app = FastAPI(
    title="Kavak Commercial Agent API",
    description="AI-powered commercial agent for Kavak car dealership",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory conversation storage (use Redis or database in production)
conversation_storage: dict[str, ConversationState] = {}

@app.post("/chat", response_model=ChatResponse, tags=["Chat"])
def chat(
    request: ChatRequest,
    agent: KavakCommercialAgent = Depends(get_agent)
):
    """
    Main chat endpoint for interacting with the commercial agent.
    """
    try:
        logger.info(f"Processing chat request from user {request.user_id}")
        
        # Get or create conversation state
        conversation_state = conversation_storage.get(request.user_id)
        print(f"Current conversation state: {conversation_state}")
        
        # Process the message
        result = agent.process_message(
            user_id=request.user_id,
            message=request.message,
            conversation_state=conversation_state
        )
        
        # Update conversation storage
        conversation_storage[request.user_id] = result["conversation_state"]
        
        return ChatResponse(
            response=result["response"],
            user_id=request.user_id,
            conversation_stage=result["conversation_state"].conversation_stage,
            success=result["success"],
            error=result.get("error")
        )
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

# WhatsApp webhook endpoints (for Twilio integration)
@app.post("/webhook/whatsapp", tags=["WhatsApp"])
def whatsapp_webhook(
    webhook_data: WhatsAppWebhook,
    background_tasks: BackgroundTasks,
    agent: KavakCommercialAgent = Depends(get_agent)
):
    """
    Webhook endpoint for receiving WhatsApp messages from Twilio.
    """
    try:
        logger.info(f"Received WhatsApp message from {webhook_data.From}")
        
        # Extract user ID from phone number
        user_id = webhook_data.From.replace("whatsapp:", "").replace("+", "")
        
        # Process message in background
        background_tasks.add_task(
            process_whatsapp_message,
            user_id,
            webhook_data.Body,
            webhook_data.From,
            agent
        )
        
        return {"status": "received"}
        
    except Exception as e:
        logger.error(f"Error in WhatsApp webhook: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Webhook processing failed: {str(e)}"
        )


def process_whatsapp_message(
    user_id: str,
    message: str,
    phone_number: str,
    agent: KavakCommercialAgent
):
    """
    Process WhatsApp message in background.
    """
    try:
        # Get conversation state
        conversation_state = conversation_storage.get(user_id)
        
        # Process message
        result = agent.process_message(
            user_id=user_id,
            message=message,
            conversation_state=conversation_state
        )
        
        # Update conversation storage
        conversation_storage[user_id] = result["conversation_state"]
        
        # Send response back to WhatsApp (implement Twilio client here)
        send_whatsapp_response(phone_number, result["response"])
        
        logger.info(f"Processed WhatsApp message for user {user_id}")
        
    except Exception as e:
        logger.error(f"Error processing WhatsApp message: {e}")


def send_whatsapp_response(phone_number: str, message: str):
    """
    Send response back to WhatsApp via Twilio.
    """
    try:
        if whatsapp_service.is_available():
            result = whatsapp_service.send_message(phone_number, message)
            if result["success"]:
                logger.info(f"WhatsApp message sent successfully to {phone_number}")
            else:
                logger.error(f"Failed to send WhatsApp message: {result['error']}")
        else:
            logger.warning(f"WhatsApp service not available. Would send to {phone_number}: {message}")
    except Exception as e:
        logger.error(f"Error sending WhatsApp response: {e}")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        app,
        host="localhost",
        port=8000,
        log_level="info",
        reload=True,
    )