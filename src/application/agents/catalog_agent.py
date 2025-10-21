"""Agente para búsqueda y recomendación de autos del catálogo."""
from typing import Any
import logging
from dataclasses import asdict
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
from domain.agent_state import AgentState
from application.services.catalog_service import semanticCatalogSearchService

logger = logging.getLogger(__name__)


class CatalogAgent:
    """Busca autos en el catálogo y genera recomendaciones personalizadas."""
    
    def __init__(self, llm: ChatOpenAI, top_k: int = 3):
        self.llm = llm
        self.top_k = top_k
    
    def execute(self, state: AgentState) -> dict[str, Any]:
        """
        Busca en catálogo y genera recomendaciones.
        
        Args:
            state: Estado con la query y contexto del usuario
            
        Returns:
            Dict con respuesta, autos encontrados y contexto del catálogo
        """
        query = state["query"]
        conversation_history = state.get("conversation_history", "")
        
        try:
            cars = semanticCatalogSearchService.search_by_text(query, self.top_k)
            cars_dict = [asdict(c) for c in cars]
            
            if cars_dict:
                catalog_context = "Autos disponibles:\n" + "\n".join(
                    f"- {c['marca']} {c['modelo']} {c['year']} — ${c['price']:,.0f} MXN, {c['kms']:,} km"
                    if c.get('kms') else f"- {c['marca']} {c['modelo']} {c['year']} — ${c['price']:,.0f} MXN"
                    for c in cars_dict
                )
            else:
                catalog_context = "No se encontraron autos que coincidan. Sugiere alternativas similares."
            
            system_prompt = """Eres un vendedor experto de Kavak. Tu misión es recomendar autos del catálogo.

CATÁLOGO:
{catalog_context}

REGLAS:
- Recomienda SOLO autos del catálogo mostrado
- Destaca precio, kilometraje, año y ventajas
- Si no hay coincidencias exactas, ofrece alternativas
- Sé persuasivo pero honesto
- Menciona que todos incluyen garantía y 7 días de prueba"""
            
            human_content = query
            if conversation_history:
                human_content = f"Historial:\n{conversation_history}\n\nConsulta: {query}"
            
            result = self.llm.invoke([
                SystemMessage(content=system_prompt.format(catalog_context=catalog_context)),
                HumanMessage(content=human_content)
            ])
            
            response = result.content if isinstance(result.content, str) else str(result.content)
            logger.info(f"Respuesta generada por catalog_agent con {len(cars_dict)} autos")
            
            return {
                "response": response,
                "cars": cars_dict,
                "catalog_context": catalog_context
            }
            
        except Exception as e:
            logger.error(f"Error en catalog_agent: {e}")
            return {
                "response": "Disculpa, tuve un problema al buscar en el catálogo.",
                "cars": [],
                "catalog_context": ""
            }
