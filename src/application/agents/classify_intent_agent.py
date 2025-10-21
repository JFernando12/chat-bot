"""Agente clasificador de intenciones para routing inteligente."""
from typing import Any
import logging
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
from domain.agent_state import AgentState

logger = logging.getLogger(__name__)


class ClassifyIntentAgent:
    """Clasifica la intención del usuario para dirigir al agente apropiado."""
    
    def __init__(self, classifier_llm: ChatOpenAI):
        self.classifier_llm = classifier_llm
    
    def execute(self, state: AgentState) -> dict[str, Any]:
        """
        Clasifica la intención del usuario.
        
        Args:
            state: Estado con la query del usuario
            
        Returns:
            Dict con el intent clasificado
        """
        query = state["query"]
        
        classification_prompt = """Clasifica la siguiente consulta en UNA de estas categorías:

CATEGORÍAS:
1. GENERAL - Preguntas sobre Kavak, políticas, garantía, devoluciones, proceso de compra, servicios
2. CATALOG_SEARCH - Búsqueda de autos específicos (marca, modelo, año, precio, características)
3. FINANCE_CALCULATION - Cálculo de financiamiento, mensualidades, planes de pago

Ejemplos:
- "¿Qué garantía ofrecen?" → GENERAL
- "Quiero un Honda Civic" → CATALOG_SEARCH
- "¿Cuánto pagaría mensualmente por un auto de $250k?" → FINANCE_CALCULATION

Consulta: "{query}"

Responde SOLO con UNA palabra: GENERAL, CATALOG_SEARCH o FINANCE_CALCULATION"""
        
        try:
            result = self.classifier_llm.invoke([
                SystemMessage(content="Eres un clasificador de intenciones. Responde con UNA palabra."),
                HumanMessage(content=classification_prompt.format(query=query))
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
