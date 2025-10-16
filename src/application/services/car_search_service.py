import logging
import re

from ...domain.models import Car
from ...infrastructure.repositories import CarRepositoryInterface

logger = logging.getLogger(__name__)

class CarSearchService():
    """
    Concrete implementation of car search service.
    Handles natural language processing and fuzzy search.
    """
    
    def __init__(self, car_repository: CarRepositoryInterface):
        self.car_repository = car_repository
    
    def search_by_text(self, query: str) -> list[Car]:
        query_lower = query.lower()
        all_cars = self.car_repository.get_all_cars()
        
        matching_cars = []
        
        for car in all_cars:
            score = self._calculate_text_match_score(car, query_lower)
            if score > 0:
                matching_cars.append((car, score))
        
        # Sort by relevance score descending
        matching_cars.sort(key=lambda x: x[1], reverse=True)
        
        return [car for car, score in matching_cars]
    
    def fuzzy_search_make_model(self, make_model: str) -> list[Car]:
        make_model_lower = make_model.lower()
        all_cars = self.car_repository.get_all_cars()
        
        # Normalize common misspellings and variations
        normalized_query = self._normalize_make_model(make_model_lower)
        
        matching_cars = []
        
        for car in all_cars:
            car_make_model = f"{car.make} {car.model}".lower()
            normalized_car = self._normalize_make_model(car_make_model)
            
            # Calculate fuzzy match score
            score = self._calculate_fuzzy_score(normalized_query, normalized_car)
            if score > 0.5:  # Threshold for relevance
                matching_cars.append((car, score))
        
        # Sort by relevance score descending
        matching_cars.sort(key=lambda x: x[1], reverse=True)
        
        return [car for car, score in matching_cars]
    
    def _calculate_text_match_score(self, car: Car, query: str) -> float:
        score = 0.0
        
        # Create searchable text from car
        searchable_text = f"{car.make} {car.model} {car.version} {car.year}".lower()
        
        # Split query into words
        query_words = query.split()
        
        for word in query_words:
            if word in searchable_text:
                score += 1.0
        
        # Normalize by number of query words
        if query_words:
            score = score / len(query_words)
        
        return score
    
    def _normalize_make_model(self, text: str) -> str:
        # Common normalizations for Spanish/Mexican market
        normalizations = {
            'volkswagen': 'vw',
            'chevrolet': 'chevy',
            'mercedes benz': 'mercedes',
            'land rover': 'landrover',
            'bmw': 'bmw',
        }
        
        normalized = text
        for original, replacement in normalizations.items():
            normalized = normalized.replace(original, replacement)
        
        # Remove special characters and extra spaces
        normalized = re.sub(r'[^\w\s]', '', normalized)
        normalized = ' '.join(normalized.split())
        
        return normalized
    
    def _calculate_fuzzy_score(self, query: str, target: str) -> float:
        # Simple Levenshtein-like scoring
        query_words = set(query.split())
        target_words = set(target.split())
        
        if not query_words or not target_words:
            return 0.0
        
        # Calculate Jaccard similarity
        intersection = query_words.intersection(target_words)
        union = query_words.union(target_words)
        
        return len(intersection) / len(union) if union else 0.0