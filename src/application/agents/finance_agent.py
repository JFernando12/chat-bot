from typing import Any
import logging
import json
import re
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
from domain.finance import FinanceCalculator
from domain.agent_state import AgentState

logger = logging.getLogger(__name__)


class FinanceAgent:
    """Extrae parámetros y calcula planes de financiamiento automotriz."""
    
    def __init__(self, classifier_llm: ChatOpenAI):
        self.classifier_llm = classifier_llm
    
    def execute(self, state: AgentState) -> dict[str, Any]:
        """
        Extrae parámetros y calcula financiamiento.
        
        Args:
            state: Estado con la query del usuario
            
        Returns:
            Dict con respuesta y plan de financiamiento (si aplica)
        """
        query = state["query"]
        
        extraction_prompt = """Extrae los valores para calcular financiamiento automotriz:

Consulta: "{query}"

Extrae:
- precio: precio del auto en pesos (ej: 250000)
- enganche: monto del enganche en pesos (ej: 50000)
- years: años del financiamiento (debe ser entre 3 y 6)

Si falta algún dato, responde con "MISSING" para ese campo.

Formato de respuesta (JSON):
{{"precio": 250000, "enganche": 50000, "years": 5}}

Si falta algo:
{{"precio": "MISSING", "enganche": "MISSING", "years": "MISSING"}}"""
        
        try:
            # Extraer parámetros con LLM
            result = self.classifier_llm.invoke([
                SystemMessage(content="Extrae parámetros numéricos. Responde solo con JSON válido."),
                HumanMessage(content=extraction_prompt.format(query=query))
            ])
            
            # Parsear respuesta
            content = result.content if isinstance(result.content, str) else str(result.content)
            content = content.strip()
            # Limpiar markdown si existe
            content = re.sub(r'```json\s*|\s*```', '', content)
            
            params = json.loads(content)
            
            # Verificar si tenemos todos los parámetros
            if (params.get("precio") != "MISSING" and 
                params.get("enganche") != "MISSING" and 
                params.get("years") != "MISSING"):
                
                # Calcular financiamiento
                plan = FinanceCalculator.calculate(
                    price=float(params["precio"]),
                    enganche=float(params["enganche"]),
                    annual_rate=0.10,
                    years=int(params["years"])
                )
                
                plan_dict = FinanceCalculator.to_dict(plan)
                
                response = f"""💰 **Plan de Financiamiento Kavak**

🚗 Precio del auto: ${float(params['precio']):,.0f} MXN
💵 Enganche: ${float(params['enganche']):,.0f} MXN
📊 Monto financiado: ${plan.financed_amount:,.2f} MXN
📅 Plazo: {params['years']} años ({plan.months} meses)
💳 Mensualidad: ${plan.monthly_payment:,.2f} MXN
💸 Total a pagar: ${plan.total_paid:,.2f} MXN
📈 Intereses totales: ${plan.total_interest:,.2f} MXN

✅ Tasa fija anual: 10%
✅ Sin comisión por apertura
✅ Aprobación en 24 horas"""
                
                logger.info(f"Financiamiento calculado: ${plan.monthly_payment:,.2f}/mes")
                return {"response": response, "financing_plan": plan_dict}
            
            else:
                # Faltan parámetros
                response = """Para calcular tu plan de financiamiento necesito:

📋 **Datos requeridos:**
1. Precio del auto (ej: $250,000)
2. Monto del enganche (ej: $50,000)
3. Plazo en años (3, 4, 5 o 6 años)

Ejemplo: "Quiero financiar un auto de $300,000 con $60,000 de enganche a 5 años"

¿Me puedes proporcionar estos datos?"""
                
                logger.info("Parámetros faltantes para financiamiento")
                return {"response": response, "financing_plan": None}
                
        except Exception as e:
            logger.error(f"Error en finance_agent: {e}")
            response = """Para calcular financiamiento, especifica:
- Precio del auto
- Enganche
- Plazo (3-6 años)

Ejemplo: "Auto de $250,000, enganche $50,000, 4 años" """
            return {"response": response, "financing_plan": None}
