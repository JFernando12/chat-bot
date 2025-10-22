from typing import Any
import logging
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
from domain.agent_state import AgentState
from config.prompt_loader import prompt_loader

logger = logging.getLogger(__name__)

class ClassifyIntentAgent:
    """Clasifica la intención del usuario para dirigir al agente apropiado."""
    
    def __init__(self, classifier_llm: ChatOpenAI):
        self.classifier_llm = classifier_llm
        self.system_prompt = prompt_loader.load("classify_intent_system")
        self.user_prompt_template = prompt_loader.load("classify_intent_user")
    
    def execute(self, state: AgentState) -> dict[str, Any]:
        """
        Clasifica la intención del usuario.
        
        Args:
            state: Estado con la query del usuario
            
        Returns:
            Dict con el intent clasificado
        """
        query = state["query"]
        
        try:
            result = self.classifier_llm.invoke([
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=self.user_prompt_template.format(query=query))
            ])
            
            intent_text = result.content if isinstance(result.content, str) else str(result.content)
            intent = intent_text.strip().upper()
            
            valid_intents = ["GENERAL", "CATALOG_SEARCH", "FINANCE_CALCULATION"]
            if intent not in valid_intents:
                intent = "GENERAL"  # Default
            
            logger.info(f"Intent clasificado: {intent} para query: {query[:50]}")
            return {"intent": intent}
            
        except Exception as e:
            logger.error(f"Error en clasificación: {e}")
            return {"intent": "GENERAL"}  # Fallback seguro
