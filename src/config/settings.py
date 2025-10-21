import os
from dotenv import load_dotenv
load_dotenv()

class Environment:
    def __init__(self):
        self.environment = os.getenv("ENVIRONMENT", "development")
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-4o")
        self.openai_temperature = float(os.getenv("OPENAI_TEMPERATURE", 0.1))
        self.openai_max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", 1000))
        
        self.twilio_account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.twilio_auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.twilio_whatsapp_number = os.getenv("TWILIO_WHATSAPP_NUMBER")
        
        self.langsmith_api_key = os.getenv("LANGSMITH_API_KEY")
        self.langsmith_project_name = os.getenv("LANGSMITH_PROJECT_NAME", "kavak-commercial-agent")
        self.langsmith_tracing_enabled = os.getenv("LANGSMITH_TRACING_ENABLED", "true").lower() == "true"
                
env = Environment()