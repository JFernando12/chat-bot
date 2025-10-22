from typing import Any, Optional
import logging
import json
import re
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
from domain.finance import FinanceCalculator
from domain.agent_state import AgentState
from config.prompt_loader import prompt_loader
from config.finance_responses import finance_responses
from application.services.catalog_service import SemanticCatalogSearchService, pandasCatalogRepository

logger = logging.getLogger(__name__)

class FinanceAgent:
    """Extrae parámetros y calcula planes de financiamiento automotriz."""
    
    def __init__(self, classifier_llm: ChatOpenAI):
        self.classifier_llm = classifier_llm
        self.response_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
        self.system_prompt = prompt_loader.load("finance_agent_system")
        self.extraction_prompt_template = prompt_loader.load("finance_agent_extraction")
        self.response_prompt_template = prompt_loader.load("finance_agent_response")
        self.response_system_prompt = prompt_loader.load("finance_agent_response_system")
        # Inicializar el servicio de búsqueda de catálogo
        self.catalog_service = SemanticCatalogSearchService(pandasCatalogRepository)
    
    def _search_car_price(self, car_name: str) -> Optional[float]:
        """
        Busca el precio de un auto en el catálogo por su nombre.
        
        Args:
            car_name: Nombre del auto (marca, modelo, año)
            
        Returns:
            Precio del auto si se encuentra, None si no
        """
        try:
            results = self.catalog_service.search_by_text(car_name, top_k=1)
            if results:
                car = results[0]
                logger.info(f"Auto encontrado: {car.marca} {car.modelo} {car.year} - ${car.price:,.0f}")
                return car.price
            return None
        except Exception as e:
            logger.error(f"Error buscando auto en catálogo: {e}")
            return None
    
    def _generate_natural_response(
        self,
        query: str,
        precio: float,
        enganche: float,
        plan: Any,
        years: int,
        conversation_history: str
    ) -> str:
        """
        Genera una respuesta natural usando IA para presentar el plan de financiamiento.
        
        Args:
            query: Pregunta original del usuario
            precio: Precio del auto
            enganche: Monto del enganche
            plan: Objeto FinancePlan con los cálculos
            years: Años del financiamiento
            conversation_history: Historial de la conversación
            
        Returns:
            Respuesta natural generada por IA
        """
        prompt = self.response_prompt_template.format(
            query=query,
            precio=f"{precio:,.0f}",
            enganche=f"{enganche:,.0f}",
            financed_amount=f"{plan.financed_amount:,.2f}",
            years=years,
            months=plan.months,
            monthly_payment=f"{plan.monthly_payment:,.2f}",
            total_paid=f"{plan.total_paid:,.2f}",
            total_interest=f"{plan.total_interest:,.2f}"
        )
        
        if conversation_history:
            prompt = f"Historial:\n{conversation_history}\n\n{prompt}"

        result = self.response_llm.invoke([
            SystemMessage(content=self.response_system_prompt),
            HumanMessage(content=prompt)
        ])
        content = result.content if isinstance(result.content, str) else str(result.content)
        return content

    def execute(self, state: AgentState) -> dict[str, Any]:
        """
        Extrae parámetros y calcula financiamiento.
        
        Args:
            state: Estado con la query del usuario
            
        Returns:
            Dict con respuesta y plan de financiamiento (si aplica)
        """
        query = state["query"]
        conversation_history = state.get("conversation_history", "")
        
        try:
            extraction_content = self.extraction_prompt_template.format(query=query)
            if conversation_history:
                extraction_content = f"Historial:\n{conversation_history}\n\n{extraction_content}"
            
            result = self.classifier_llm.invoke([
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=extraction_content)
            ])
            
            content = result.content if isinstance(result.content, str) else str(result.content)
            content = content.strip()
            content = re.sub(r'```json\s*|\s*```', '', content)
            
            params = json.loads(content)
            
            if params.get("enganche") == "MISSING":
                response = finance_responses.get("MISSING_ENGANCHE")
                logger.info("Falta el enganche")
                return {"response": response, "financing_plan": None}
            
            precio = None
            
            if params.get("precio") != "MISSING":
                precio = float(params["precio"])
            elif params.get("nombre_auto") != "MISSING":
                logger.info(f"Buscando precio para: {params['nombre_auto']}")
                precio = self._search_car_price(params["nombre_auto"])
                if precio:
                    logger.info(f"Auto encontrado en catálogo: {params['nombre_auto']} - ${precio:,.0f}")
                else:
                    response = finance_responses.get(
                        "CAR_NOT_FOUND",
                        car_name=params['nombre_auto'],
                        enganche=params['enganche']
                    )
                    logger.info(f"Auto no encontrado: {params['nombre_auto']}")
                    return {"response": response, "financing_plan": None}
            
            if precio is None:
                response = finance_responses.get("MISSING_PRICE")
                logger.info("Falta el precio del auto")
                return {"response": response, "financing_plan": None}
            
            years = 5  # Valor por defecto
            if params.get("years") != "MISSING" and params.get("years"):
                try:
                    years = int(params["years"])
                    if years < 3 or years > 6:
                        years = 5
                except:
                    years = 5
            
            enganche = float(params["enganche"])
            
            plan = FinanceCalculator.calculate(
                price=precio,
                enganche=enganche,
                annual_rate=0.10,
                years=years
            )
            
            plan_dict = FinanceCalculator.to_dict(plan)
            
            response = self._generate_natural_response(
                query=query,
                precio=precio,
                enganche=enganche,
                plan=plan,
                years=years,
                conversation_history=conversation_history or ""
            )
            
            logger.info(f"Financiamiento calculado: ${plan.monthly_payment:,.2f}/mes en {years} años")
            return {"response": response, "financing_plan": plan_dict}
                
        except Exception as e:
            logger.error(f"Error en finance_agent: {e}")
            response = finance_responses.get("ERROR_GENERIC")
            return {"response": response, "financing_plan": None}
