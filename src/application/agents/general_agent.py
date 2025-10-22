from typing import Any
import logging
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
from domain.agent_state import AgentState
from config.prompt_loader import prompt_loader
from application.services.kavak_info_service import semanticKavakInfoService

logger = logging.getLogger(__name__)

class GeneralAgent:
    """Responde preguntas generales sobre Kavak sin necesitar catálogo."""
    
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
        self.system_prompt_template = prompt_loader.load("general_agent_system")
        self.info_service = semanticKavakInfoService
    
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
        
        try:
            relevant_context = self.info_service.get_context_for_query(query, top_k=3)
            
            system_prompt = self.system_prompt_template.format(relevant_context=relevant_context)
            
            if conversation_history:
                query = f"Historial:\n{conversation_history}\n\nConsulta: {query}"
            
            result = self.llm.invoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=query)
            ])
            
            response = result.content if isinstance(result.content, str) else str(result.content)
            logger.info("Respuesta generada por general_agent con contexto de embeddings")
            return {"response": response}
            
        except Exception as e:
            logger.error(f"Error en general_agent: {e}")
            return {"response": "Disculpa, ¿podrías reformular tu pregunta?"}
