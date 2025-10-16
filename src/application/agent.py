import logging
from typing import Dict, Any, List, Optional, Annotated, TypedDict
from decimal import Decimal

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import tool, BaseTool
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from pydantic import BaseModel, Field, SecretStr

from ..domain.models import Car, CustomerPreferences, ConversationState
from ..application.services.recommendation_service import RecommendationService
from ..application.services.financing_service import FinancingService
from ..application.services.car_search_service import CarSearchService
from ..infrastructure.repositories import CarRepositoryInterface

logger = logging.getLogger(__name__)

class AgentState(TypedDict):
    """Defines the state used by the LangGraph workflow."""
    messages: Annotated[List, add_messages]
    user_id: str
    conversation_state: ConversationState
    last_recommendations: Optional[List[Car]]
    last_search_query: Optional[str]

class CarRecommendationInput(BaseModel):
    min_price: Optional[float] = Field(None, description="Minimum price in MXN")
    max_price: Optional[float] = Field(None, description="Maximum price in MXN")
    preferred_makes: Optional[List[str]] = Field(None, description="Preferred car brands")
    max_km: Optional[int] = Field(None, description="Maximum kilometers")
    min_year: Optional[int] = Field(None, description="Minimum year")
    features: Optional[List[str]] = Field(None, description="Required features like bluetooth, carplay")
    limit: int = Field(5, description="Number of recommendations to return")


class FinancingCalculationInput(BaseModel):
    car_price: float = Field(..., description="Car price in MXN")
    down_payment: float = Field(..., description="Down payment amount in MXN")
    term_years: int = Field(..., description="Financing term in years (3-6)")


class CarSearchInput(BaseModel):
    query: str = Field(..., description="Search query for cars")

class KavakCommercialAgent:
    def __init__(
        self,
        car_repository: CarRepositoryInterface,
        openai_api_key: str,
        model_name: str = "gpt-4o",
        temperature: float = 0.2,
    ):
        self.car_repository = car_repository
        self.recommendation_service = RecommendationService(car_repository)
        self.financing_service = FinancingService()
        self.search_service = CarSearchService(car_repository)

        # Initialize LLM
        self.llm = ChatOpenAI(
            api_key=SecretStr(openai_api_key),
            model=model_name,
            temperature=temperature
        )

        # Initialize Tools
        self.tools = self._create_tools()

        # Create the LangGraph workflow
        self.graph = self._create_graph()

    def _create_tools(self) -> List[BaseTool]:
        """Define tools for the agent."""

        @tool("get_car_recommendations", args_schema=CarRecommendationInput)
        def get_car_recommendations(**kwargs) -> str:
            """Get car recommendations based on preferences."""
            try:
                prefs = CustomerPreferences(
                    min_price=Decimal(str(kwargs.get("min_price"))) if kwargs.get("min_price") else None,
                    max_price=Decimal(str(kwargs.get("max_price"))) if kwargs.get("max_price") else None,
                    preferred_makes=kwargs.get("preferred_makes") or [],
                    max_km=kwargs.get("max_km"),
                    min_year=kwargs.get("min_year"),
                    max_year=None,
                    car_type=None,
                    features_required=kwargs.get("features") or [],
                )

                result = self.recommendation_service.recommend_cars(prefs, kwargs.get("limit", 5))

                if not result['cars']:
                    return "No se encontraron autos que coincidan con tus preferencias."

                lines = ["🚗 Autos recomendados:\n"]
                for i, car in enumerate(result['cars'], 1):
                    lines.append(f"{i}. {car.year} {car.make} {car.model} — {car.formatted_price} — ID: {car.stock_id}")
                if result['recommendation_reason']:
                    lines.append(f"\n📊 Motivo: {result['recommendation_reason']}")
                return "\n".join(lines)

            except Exception as e:
                logger.error(f"Error en get_car_recommendations: {e}")
                return f"Error buscando recomendaciones: {e}"

        @tool("calculate_financing", args_schema=FinancingCalculationInput)
        def calculate_financing(car_price: float, down_payment: float, term_years: int) -> str:
            """Calculate financing plan."""
            try:
                if not (3 <= term_years <= 6):
                    return "El plazo debe ser entre 3 y 6 años."
                if down_payment > car_price:
                    return "El enganche no puede ser mayor al precio del auto."

                plan = self.financing_service.calculate_financing(
                    Decimal(str(car_price)),
                    Decimal(str(down_payment)),
                    term_years
                )
                data = plan.to_dict()
                return (
                    f"💰 Plan de Financiamiento Kavak\n\n"
                    f"🚗 Precio: {data['car_price']}\n"
                    f"💵 Enganche: {data['down_payment']}\n"
                    f"💳 A financiar: {data['financed_amount']}\n"
                    f"📈 Interés: {data['interest_rate']}\n"
                    f"📅 Plazo: {data['term_years']} años\n"
                    f"💰 Mensualidad: {data['monthly_payment']}\n"
                    f"💸 Total: {data['total_amount']}\n"
                )

            except Exception as e:
                logger.error(f"Error en calculate_financing: {e}")
                return f"Error calculando financiamiento: {e}"

        @tool("search_cars", args_schema=CarSearchInput)
        def search_cars(query: str) -> str:
            """Search for cars by text query."""
            try:
                cars = self.search_service.search_by_text(query)
                if not cars:
                    cars = self.search_service.fuzzy_search_make_model(query)
                if not cars:
                    return f"No encontré autos que coincidan con '{query}'."
                cars = cars[:5]
                lines = [f"🔍 Resultados para '{query}':\n"]
                for i, car in enumerate(cars, 1):
                    lines.append(f"{i}. {car.year} {car.make} {car.model} — {car.formatted_price} — ID: {car.stock_id}")
                return "\n".join(lines)
            except Exception as e:
                logger.error(f"Error en search_cars: {e}")
                return f"Error en la búsqueda: {e}"

        @tool("get_kavak_info")
        def get_kavak_info() -> str:
            """Provide Kavak's value proposition."""
            return (
                "🚗 **Kavak: Revolucionando la compra de autos usados en México**\n\n"
                "✅ Calidad garantizada: inspección de 240 puntos.\n"
                "✅ Precio fijo, sin regateos.\n"
                "✅ Garantía de 3 meses o 3,000 km.\n"
                "✅ Financiamiento desde 10% de enganche.\n"
                "✅ Compra 100% digital.\n"
                "✅ Red nacional en más de 25 ciudades.\n"
            )

        return [get_car_recommendations, calculate_financing, search_cars, get_kavak_info]


    def _create_system_prompt(self) -> str:
        return """
Eres un agente comercial experto de Kavak, la plataforma líder de autos usados en México.
Tu objetivo es ayudar al cliente a encontrar el auto ideal y ofrecer financiamiento.

**Instrucciones:**
- Usa herramientas si lo necesitas.
- Sé amigable, preciso y proactivo.
- Evita alucinaciones: solo usa datos reales de herramientas.
- Usa emojis moderadamente.
        """.strip()

    def _create_graph(self):
        """Build the LangGraph workflow with tools."""
        workflow = StateGraph(AgentState)

        # Define LLM node
        def call_model(state: AgentState):
            messages = state["messages"]

            # Add system message if missing
            if not messages or not isinstance(messages[0], SystemMessage):
                system_prompt = self._create_system_prompt()
                messages = [SystemMessage(content=system_prompt)] + messages

            # Bind tools to model
            model_with_tools = self.llm.bind_tools(self.tools)
            response = model_with_tools.invoke(messages)
            return {"messages": [response]}

        # Create LangGraph nodes
        workflow.add_node("agent", call_model)
        workflow.add_node("tools", ToolNode(self.tools))

        # Define flow: agent → tools (if needed) → agent → END
        workflow.set_entry_point("agent")

        def route(state: AgentState) -> str:
            """Route based on tool usage."""
            last_message = state["messages"][-1]
            if hasattr(last_message, "tool_calls") and last_message.tool_calls:
                return "tools"
            return END

        workflow.add_conditional_edges(
            "agent",
            route,
            {
                "tools": "tools",
                END: END,
            },
        )

        workflow.add_edge("tools", "agent")

        return workflow.compile()

    def process_message(
        self,
        user_id: str,
        message: str,
        conversation_state: Optional[ConversationState] = None,
    ) -> Dict[str, Any]:
        """Process a user message using the compiled LangGraph."""
        try:
            if conversation_state is None:
                conversation_state = ConversationState(user_id=user_id, conversation_stage="greeting")

            state = AgentState(
                messages=[HumanMessage(content=message)],
                user_id=user_id,
                conversation_state=conversation_state,
                last_recommendations=None,
                last_search_query=None,
            )

            result = self.graph.invoke(state)

            # Extract final AI response
            ai_messages = [m for m in result["messages"] if isinstance(m, AIMessage)]
            response_text = ai_messages[-1].content if ai_messages else "Lo siento, no pude procesar tu solicitud."

            return {
                "response": response_text,
                "conversation_state": conversation_state,
                "success": True,
            }

        except Exception as e:
            logger.exception("Error procesando mensaje")
            return {
                "response": f"Error interno del agente: {e}",
                "conversation_state": conversation_state,
                "success": False,
            }
