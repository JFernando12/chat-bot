import logging
from typing import Optional, Dict, Any
from twilio.rest import Client
from twilio.base.exceptions import TwilioException

from config.settings import env

logger = logging.getLogger(__name__)

class WhatsAppService:
    """
    Service for handling WhatsApp integration through Twilio.
    Follows Single Responsibility Principle - only handles WhatsApp communication.
    """
    
    def __init__(
        self,
        account_sid: Optional[str] = None,
        auth_token: Optional[str] = None,
        whatsapp_number: Optional[str] = None
    ):
        """Initialize WhatsApp service with Twilio credentials."""
        self.account_sid = account_sid or env.twilio_account_sid
        self.auth_token = auth_token or env.twilio_auth_token
        self.whatsapp_number = whatsapp_number or env.twilio_whatsapp_number
        
        self.client = Client(self.account_sid, self.auth_token)

    
    def is_available(self) -> bool:
        """Check if WhatsApp service is available."""
        return self.client is not None
    
    def send_message(
        self,
        to_number: str,
        message: str,
        media_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send a WhatsApp message to a phone number.
        
        Args:
            to_number: Recipient phone number in format +1234567890
            message: Message text to send
            media_url: Optional URL for media attachment
            
        Returns:
            Dictionary with send result and message SID
        """
        if not self.is_available():
            logger.error("WhatsApp service not available")
            return {
                "success": False,
                "error": "WhatsApp service not configured",
                "message_sid": None
            }
        
        try:
            # Ensure phone number has whatsapp: prefix
            if not to_number.startswith("whatsapp:"):
                to_number = f"whatsapp:{to_number}"
            
            # Prepare message parameters
            message_params = {
                "from_": self.whatsapp_number,
                "to": to_number,
                "body": message
            }
            
            # Add media if provided
            if media_url:
                message_params["media_url"] = media_url
            
            # Send message through Twilio
            twilio_message = self.client.messages.create(**message_params)
            
            logger.info(f"WhatsApp message sent successfully. SID: {twilio_message.sid}")
            
            return {
                "success": True,
                "message_sid": twilio_message.sid,
                "status": twilio_message.status,
                "error": None
            }
            
        except TwilioException as e:
            logger.error(f"Twilio error sending WhatsApp message: {e}")
            return {
                "success": False,
                "error": f"Twilio error: {str(e)}",
                "message_sid": None
            }
        except Exception as e:
            logger.error(f"Unexpected error sending WhatsApp message: {e}")
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "message_sid": None
            }
    
    def send_template_message(
        self,
        to_number: str,
        template_sid: str,
        template_variables: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Send a WhatsApp template message.
        
        Args:
            to_number: Recipient phone number
            template_sid: Twilio template SID
            template_variables: Variables for template substitution
            
        Returns:
            Dictionary with send result
        """
        if not self.is_available():
            return {
                "success": False,
                "error": "WhatsApp service not configured"
            }
        
        try:
            # Ensure phone number has whatsapp: prefix
            if not to_number.startswith("whatsapp:"):
                to_number = f"whatsapp:{to_number}"
            
            # Send template message
            message = self.client.messages.create(
                from_=self.whatsapp_number,
                to=to_number,
                content_sid=template_sid,
                content_variables=template_variables or {}
            )
            
            logger.info(f"WhatsApp template message sent. SID: {message.sid}")
            
            return {
                "success": True,
                "message_sid": message.sid,
                "status": message.status
            }
            
        except TwilioException as e:
            logger.error(f"Error sending WhatsApp template: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def validate_webhook_signature(
        self,
        request_url: str,
        post_data: Dict[str, Any],
        signature: str
    ) -> bool:
        """
        Validate Twilio webhook signature for security.
        
        Args:
            request_url: The full URL of the webhook request
            post_data: POST data from the webhook
            signature: X-Twilio-Signature header value
            
        Returns:
            True if signature is valid, False otherwise
        """
        if not self.auth_token:
            logger.warning("Cannot validate webhook signature - no auth token")
            return False
        
        try:
            from twilio.request_validator import RequestValidator
            
            validator = RequestValidator(self.auth_token)
            return validator.validate(request_url, post_data, signature)
            
        except Exception as e:
            logger.error(f"Error validating webhook signature: {e}")
            return False
    
    def get_message_status(self, message_sid: str) -> Dict[str, Any]:
        """
        Get the status of a sent message.
        
        Args:
            message_sid: Twilio message SID
            
        Returns:
            Dictionary with message status information
        """
        if not self.is_available():
            return {
                "success": False,
                "error": "WhatsApp service not configured"
            }
        
        try:
            message = self.client.messages(message_sid).fetch()
            
            return {
                "success": True,
                "sid": message.sid,
                "status": message.status,
                "error_code": message.error_code,
                "error_message": message.error_message,
                "date_sent": message.date_sent,
                "date_updated": message.date_updated
            }
            
        except TwilioException as e:
            logger.error(f"Error fetching message status: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def format_phone_number(self, phone_number: str) -> str:
        """
        Format phone number for WhatsApp use.
        
        Args:
            phone_number: Phone number in various formats
            
        Returns:
            Formatted phone number with whatsapp: prefix
        """
        # Remove any existing prefixes
        cleaned = phone_number.replace("whatsapp:", "").replace("+", "")
        
        # Add + prefix if not present
        if not cleaned.startswith("+"):
            cleaned = f"+{cleaned}"
        
        # Add whatsapp: prefix
        return f"whatsapp:{cleaned}"


# Global WhatsApp service instance
whatsapp_service = WhatsAppService()