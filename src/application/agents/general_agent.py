from typing import Any
import logging
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
from domain.agent_state import AgentState

logger = logging.getLogger(__name__)


class GeneralAgent:
    """Responde preguntas generales sobre Kavak sin necesitar catálogo."""
    
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
    
    def execute(self, state: AgentState) -> dict[str, Any]:
        """
        Genera respuesta para preguntas generales.
        
        Args:
            state: Estado con la query y contexto del usuario
            
        Returns:
            Dict con la respuesta generada
        """
        query = state["query"]
        conversation_history = state.get("conversation_history", "")
        
        system_prompt = """Eres un agente de atención al cliente de Kavak. Responde preguntas sobre:

INFORMACIÓN DE KAVAK:
✅ Garantía: 3 meses o 3,000 km
✅ Periodo de prueba: 7 días (devuelve el auto si no te convence)
✅ Certificación: Más de 200 puntos de inspección
✅ Proceso: 100% digital y transparente
✅ Entrega: A domicilio sin costo
✅ Financiamiento: Disponible con tasas competitivas (10% anual, 3-6 años)

Sé amable, conciso y profesional. Si preguntan por autos específicos, invítalos a especificar marca o modelo."""
        
        try:
            human_content = query
            if conversation_history:
                human_content = f"Historial:\n{conversation_history}\n\nConsulta: {query}"
            
            result = self.llm.invoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=human_content)
            ])
            
            response = result.content if isinstance(result.content, str) else str(result.content)
            logger.info("Respuesta generada por general_agent")
            return {"response": response}
            
        except Exception as e:
            logger.error(f"Error en general_agent: {e}")
            return {"response": "Disculpa, ¿podrías reformular tu pregunta?"}
