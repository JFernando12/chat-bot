from typing import List
from openai import OpenAI
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from config.settings import env

class SemanticKavakInfoService:
    """Búsqueda semántica de información de Kavak usando embeddings."""
    def __init__(self, txt_path: str):
        self.client = OpenAI(api_key=env.openai_api_key)
        self.embedding_model = "text-embedding-3-small"
        
        with open(txt_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        self.sections = []
        for section in content.split('## ')[1:]:  # Saltar el título principal
            if section.strip():
                lines = section.strip().split('\n')
                title = lines[0]
                text = '\n'.join(lines[1:])
                self.sections.append(f"{title}\n{text}")
        
        self.embeddings = np.array([self._get_embedding(text) for text in self.sections])
    
    def _get_embedding(self, text: str) -> List[float]:
        """Obtiene el embedding de un texto."""
        response = self.client.embeddings.create(
            input=text,
            model=self.embedding_model
        )
        return response.data[0].embedding
    
    def get_context_for_query(self, query: str, top_k: int = 3) -> str:
        """Obtiene el contexto relevante para una consulta."""
        query_emb = np.array([self._get_embedding(query)])
        sims = cosine_similarity(query_emb, self.embeddings)[0]
        ranked_idx = np.argsort(sims)[::-1][:top_k]
        
        return "\n\n".join([self.sections[i] for i in ranked_idx])

semanticKavakInfoService = SemanticKavakInfoService("data/kavak_info.txt")
