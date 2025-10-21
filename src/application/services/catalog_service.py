from dataclasses import dataclass
from typing import Optional, Protocol, List
import pandas as pd
from openai import OpenAI
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from config.settings import env

@dataclass(frozen=True)
class Car:
    id: str
    marca: str
    modelo: str
    year: int
    price: float
    kms: Optional[int] = None
    version: Optional[str] = None
    bluetooth: Optional[str] = None
    largo: Optional[float] = None
    ancho: Optional[float] = None
    altura: Optional[float] = None
    car_play: Optional[str] = None

class CatalogRepository(Protocol):
    """Abstracción del origen de datos del catálogo."""
    def get_all(self) -> List[Car]:
        ...

class PandasCatalogRepository:
    """Implementación del repositorio usando pandas y CSV."""
    def __init__(self, csv_path: str):
        self.csv_path = csv_path

    def get_all(self) -> List[Car]:
        df = pd.read_csv(self.csv_path)
        df = df.fillna("")
        cars = [
            Car(
                id=str(row["stock_id"]),
                marca=row["make"],
                modelo=row["model"],
                year=int(row["year"]),
                price=float(row["price"]),
                kms=int(row["km"]) if row["km"] else None,
                version=row["version"] if row["version"] else None,
                bluetooth=row["bluetooth"] if row["bluetooth"] else None,
                largo=float(row["largo"]) if row["largo"] else None,
                ancho=float(row["ancho"]) if row["ancho"] else None,
                altura=float(row["altura"]) if row["altura"] else None,
                car_play=row["car_play"] if row["car_play"] else None
            )
            for _, row in df.iterrows()
        ]
        return cars

class SemanticCatalogSearchService:
    """Búsqueda semántica usando embeddings de OpenAI."""
    def __init__(self, repository: CatalogRepository):
        self.repository = repository
        print("Inicializando cliente de OpenAI para embeddings...")
        self.client = OpenAI(api_key=env.openai_api_key)
        self.embedding_model = "text-embedding-3-small"
        print("Preparando embeddings del catálogo...")
        self._prepare_embeddings()
        print("Embeddings listos.")

    def _get_embedding(self, text: str) -> List[float]:
        """Obtiene el embedding de un texto usando OpenAI."""
        response = self.client.embeddings.create(
            input=text,
            model=self.embedding_model
        )
        return response.data[0].embedding

    def _prepare_embeddings(self):
        self.cars = self.repository.get_all()
        texts = [
            f"{car.marca} {car.modelo} año {car.year} version {car.version or ''} "
            f"precio {car.price} kilometros {car.kms or ''} "
            f"bluetooth {car.bluetooth or ''} carplay {car.car_play or ''} "
            f"largo {car.largo or ''} ancho {car.ancho or ''} altura {car.altura or ''}"
            for car in self.cars
        ]
        # Obtener embeddings de todos los textos
        print(f"Generando embeddings para {len(texts)} vehículos...")
        self.embeddings = np.array([self._get_embedding(text) for text in texts])

    def search_by_text(self, query: str, top_k: int = 5) -> List[Car]:
        query_emb = np.array([self._get_embedding(query)])
        sims = cosine_similarity(query_emb, self.embeddings)[0]
        ranked_idx = np.argsort(sims)[::-1]
        top_cars = [self.cars[i] for i in ranked_idx[:top_k]]

        print(f"\nConsulta: {query}")
        print("Resultados:")
        for car, sim in zip(top_cars, sims[ranked_idx[:top_k]]):
            print(f"- {car.marca} {car.modelo} {car.year} - {car.price} - ({car.version}) -> similitud: {sim:.2f}")
        return top_cars
    
pandasCatalogRepository = PandasCatalogRepository("data/sample_caso_ai_engineer.csv")
semanticCatalogSearchService = SemanticCatalogSearchService(pandasCatalogRepository)