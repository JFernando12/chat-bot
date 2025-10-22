from typing import Dict

class FinanceResponseLoader:
    """Carga y formatea las respuestas del agente de financiamiento."""
    
    def __init__(self, file_path: str = "prompts/finance_agent_responses.txt"):
        self.responses = self._load_responses(file_path)
    
    def _load_responses(self, file_path: str) -> Dict[str, str]:
        """Carga las respuestas desde el archivo."""
        responses = {}
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        sections = content.split('## ')
        for section in sections:
            if section.strip():
                lines = section.strip().split('\n', 1)
                if len(lines) == 2:
                    key = lines[0].strip()
                    value = lines[1].strip()
                    responses[key] = value
        
        return responses
    
    def get(self, key: str, **kwargs) -> str:
        """
        Obtiene una respuesta y formatea con los parámetros dados.
        
        Args:
            key: Clave de la respuesta
            **kwargs: Parámetros para formatear
            
        Returns:
            Respuesta formateada
        """
        template = self.responses.get(key, "")
        return template.format(**kwargs)

finance_responses = FinanceResponseLoader()
