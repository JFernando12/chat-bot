from typing import Any, Optional
import logging

from config.settings import env

from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.graph.state import CompiledStateGraph
from pydantic import SecretStr

from domain.chat import Conversation
from domain.finance import FinanceCalculator
from domain.agent_state import AgentState

from ..agents import (
    ClassifyIntentAgent,
    GeneralAgent,
    CatalogAgent,
    FinanceAgent
)

logger = logging.getLogger(__name__)


class ChatService:
    """
    Agente comercial de Kavak usando LangGraph con Router + Agentes Especializados.
    
    Flujo del grafo:
    START -> classify_intent -> [router] -> agente específico -> format_output -> END
    
    Agentes disponibles:
    - general_agent: Preguntas generales sobre Kavak
    - catalog_agent: Búsqueda de autos en catálogo
    - finance_agent: Cálculo de financiamiento
    """

    def __init__(self, top_k: int = 3):
        self.top_k = top_k
        
        # Inicializar LLM
        api_key = env.openai_api_key
        if not api_key:
            raise ValueError("OPENAI_API_KEY no configurada en el entorno.")
        
        # LLM principal para respuestas
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.2,
            api_key=SecretStr(api_key)
        )
        
        # LLM para clasificación (más rápido)
        self.classifier_llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,  # Sin creatividad, solo clasificación
            api_key=SecretStr(api_key)
        )
        
        self.classify_intent_agent = ClassifyIntentAgent(self.classifier_llm)
        self.general_agent = GeneralAgent(self.llm)
        self.catalog_agent = CatalogAgent(self.llm, top_k)
        self.finance_agent = FinanceAgent(self.classifier_llm)
        
        self.graph = self._build_graph()
        logger.info("ChatService inicializado con arquitectura de Router + Agentes")

    def _build_graph(self) -> CompiledStateGraph:
        """Construye el grafo de estado con Router + Agentes Especializados."""
        
        graph_builder = StateGraph(AgentState)
        
        def classify_intent(state: AgentState) -> dict[str, Any]:
            """Nodo que clasifica la intención usando ClassifyIntentAgent."""
            return self.classify_intent_agent.execute(state)
        
        def general_agent(state: AgentState) -> dict[str, Any]:
            """Nodo que maneja preguntas generales usando GeneralAgent."""
            return self.general_agent.execute(state)
        
        def catalog_agent(state: AgentState) -> dict[str, Any]:
            """Nodo que busca en catálogo usando CatalogAgent."""
            return self.catalog_agent.execute(state)
        
        def finance_agent(state: AgentState) -> dict[str, Any]:
            """Nodo que calcula financiamiento usando FinanceAgent."""
            return self.finance_agent.execute(state)
        
        def format_output(state: AgentState) -> dict[str, Any]:
            """Formatea la respuesta final."""
            response = state.get("response", "")
            
            logger.info("Respuesta final lista")
            return {"final_message": response}
        
        def route_by_intent(state: AgentState) -> str:
            """Ruta hacia el agente apropiado según la intención."""
            intent = state.get("intent", "GENERAL")
            
            routing = {
                "GENERAL": "general_agent",
                "CATALOG_SEARCH": "catalog_agent",
                "FINANCE_CALCULATION": "finance_agent"
            }
            
            next_node = routing.get(intent, "general_agent")
            logger.info(f"Routing: {intent} → {next_node}")
            return next_node
        
        graph_builder.add_node("classify_intent", classify_intent)
        graph_builder.add_node("general_agent", general_agent)
        graph_builder.add_node("catalog_agent", catalog_agent)
        graph_builder.add_node("finance_agent", finance_agent)
        graph_builder.add_node("format_output", format_output)
        
        graph_builder.add_edge(START, "classify_intent")
        
        graph_builder.add_conditional_edges(
            "classify_intent",
            route_by_intent,
            {
                "general_agent": "general_agent",
                "catalog_agent": "catalog_agent",
                "finance_agent": "finance_agent"
            }
        )
        
        graph_builder.add_edge("general_agent", "format_output")
        graph_builder.add_edge("catalog_agent", "format_output")
        graph_builder.add_edge("finance_agent", "format_output")
        graph_builder.add_edge("format_output", END)
        
        compiled_graph = graph_builder.compile()
        
        logger.info("Grafo compilado: START → classify_intent → [router] → agente → format_output → END")
        return compiled_graph

    def process_message(
        self, user_input: str, conversation: Optional[Conversation] = None
    ) -> str:
        """
        Procesa un mensaje del usuario a través del grafo completo.
        
        Args:
            user_input: Mensaje del usuario
            conversation: Historial de conversación (opcional)
            
        Returns:
            Tuple de (respuesta_final, lista_de_autos_sugeridos)
        """
        try:
            conversation_history = ""
            if conversation and conversation.turns:
                conversation_history = conversation.get_history_text(last_n=3)
            
            initial_state = {
                "query": user_input,
                "conversation_history": conversation_history,
                "intent": "",
                "catalog_context": "",
                "cars": [],
                "response": "",
                "final_message": "",
                "financing_plan": None
            }
            
            logger.info(f"Procesando mensaje: {user_input[:50]}...")
            result = self.graph.invoke(initial_state)
            
            final_message = result.get("final_message", "")
            
            return final_message
        
        except Exception as e:
            logger.exception(f"Error ejecutando el grafo LangGraph: {e}")
            return "Lo siento, tuve un problema procesando tu solicitud. "        
    
    def calculate_financing(
        self, price: float, enganche: float, years: int
    ) -> dict[str, Any]:
        """
        Calcula un plan de financiamiento.
        
        Args:
            price: Precio del auto
            enganche: Monto del enganche
            years: Años del financiamiento (3-6)
            
        Returns:
            Diccionario con el plan de financiamiento
        """
        try:
            plan = FinanceCalculator.calculate(
                price=price,
                enganche=enganche,
                annual_rate=0.10,
                years=years
            )
            return FinanceCalculator.to_dict(plan)
        except ValueError as e:
            logger.warning(f"Error en cálculo de financiamiento: {e}")
            raise
        except Exception as e:
            logger.error(f"Error inesperado calculando financiamiento: {e}")
            raise ValueError("No se pudo calcular el plan de financiamiento.")

chat_service = ChatService(top_k=3)