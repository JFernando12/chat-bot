from pathlib import Path

class PromptLoader:
    """Carga prompts desde archivos de texto."""
    
    def __init__(self, prompts_dir: str = "prompts"):
        """
        Inicializa el cargador de prompts.
        
        Args:
            prompts_dir: Directorio donde se encuentran los archivos de prompts
        """
        self.prompts_dir = Path(prompts_dir)
        if not self.prompts_dir.is_absolute():
            # Si es relativo, hacerlo relativo al directorio del proyecto
            project_root = Path(__file__).parent.parent.parent
            self.prompts_dir = project_root / prompts_dir
    
    def load(self, prompt_name: str) -> str:
        """
        Carga un prompt desde un archivo.
        
        Args:
            prompt_name: Nombre del archivo de prompt (sin extensión .txt)
            
        Returns:
            Contenido del prompt
            
        Raises:
            FileNotFoundError: Si el archivo no existe
        """
        prompt_path = self.prompts_dir / f"{prompt_name}.txt"
        
        if not prompt_path.exists():
            raise FileNotFoundError(f"Prompt no encontrado: {prompt_path}")
        
        with open(prompt_path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    
    def load_template(self, prompt_name: str, **kwargs) -> str:
        """
        Carga un prompt y reemplaza variables de plantilla.
        
        Args:
            prompt_name: Nombre del archivo de prompt
            **kwargs: Variables para reemplazar en el prompt
            
        Returns:
            Prompt con variables reemplazadas
        """
        prompt = self.load(prompt_name)
        return prompt.format(**kwargs)

prompt_loader = PromptLoader()
