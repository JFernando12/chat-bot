"""Estado compartido entre agentes del chatbot."""
from typing import Any, Optional, TypedDict


class AgentState(TypedDict):
    """Estado que fluye por el grafo del agente comercial."""
    query: str
    conversation_history: Optional[str]
    intent: str  # Tipo de intención detectada
    catalog_context: str
    cars: list[dict[str, Any]]
    response: str
    final_message: str
    financing_plan: Optional[dict[str, Any]]  # Plan de financiamiento si aplica
