from decimal import Decimal
from typing import Any
from ...domain.models import Car, CustomerPreferences
from ...infrastructure.repositories import CarRepositoryInterface

class RecommendationService():
    """
    Concrete implementation of recommendation service.
    Follows Single Responsibility Principle - only handles car recommendations.
    """
    
    def __init__(self, car_repository: CarRepositoryInterface):
        """Initialize with car repository dependency."""
        self.car_repository = car_repository
    
    def recommend_cars(
        self, 
        preferences: CustomerPreferences, 
        limit: int = 5
    ):
        """Recommend cars based on customer preferences with scoring."""
        
        # Get cars matching basic criteria
        matching_cars = self.car_repository.search_cars(preferences)
        
        # Score and rank cars
        scored_cars = []
        for car in matching_cars:
            score = self._calculate_recommendation_score(car, preferences)
            scored_cars.append((car, score))
        
        # Sort by score descending
        scored_cars.sort(key=lambda x: x[1], reverse=True)
        
        # Take top recommendations
        top_cars = [car for car, score in scored_cars[:limit]]
        
        # Generate recommendation reason
        reason = self._generate_recommendation_reason(preferences, len(matching_cars))
        
        return {
            'cars': top_cars,
            'total_matches': len(matching_cars),
            'search_criteria': self._extract_search_criteria(preferences),
            'recommendation_reason': reason
        }
    
    def find_similar_cars(self, car: Car, limit: int = 3) -> list[Car]:
        """Find cars similar to the given car."""
        all_cars = self.car_repository.get_all_cars()
        
        similar_cars = []
        for other_car in all_cars:
            if other_car.stock_id == car.stock_id:
                continue
            
            similarity_score = self._calculate_similarity_score(car, other_car)
            similar_cars.append((other_car, similarity_score))
        
        # Sort by similarity score descending
        similar_cars.sort(key=lambda x: x[1], reverse=True)
        
        return [car for car, score in similar_cars[:limit]]
    
    def _calculate_recommendation_score(
        self, 
        car: Car, 
        preferences: CustomerPreferences
    ) -> float:
        """Calculate recommendation score for a car based on preferences."""
        score = 0.0
        
        # Price preference scoring
        if preferences.min_price and preferences.max_price:
            price_range = preferences.max_price - preferences.min_price
            if price_range > 0:
                # Prefer cars in the middle of the price range
                ideal_price = preferences.min_price + (price_range * Decimal('0.6'))
                price_diff = abs(car.price - ideal_price)
                price_score = max(0, 1 - float(price_diff / price_range))
                score += price_score * 0.3
        
        # Year preference (newer is generally better)
        age_score = max(0, 1 - (car.age_in_years / 15))  # Normalize by 15 years
        score += age_score * 0.2
        
        # Kilometer preference (lower is better)
        km_score = max(0, 1 - (car.km / 200000))  # Normalize by 200,000 km
        score += km_score * 0.2
        
        # Features bonus
        if car.bluetooth:
            score += 0.1
        if car.car_play:
            score += 0.1
        
        # Recent model bonus
        if car.is_recent_model:
            score += 0.1
        
        return score
    
    def _calculate_similarity_score(self, car1: Car, car2: Car) -> float:
        """Calculate similarity score between two cars."""
        score = 0.0
        
        # Same make bonus
        if car1.make.lower() == car2.make.lower():
            score += 0.4
        
        # Similar price range (within 20%)
        price_diff = abs(car1.price - car2.price) / max(car1.price, car2.price)
        if float(price_diff) <= 0.2:
            score += 0.3
        
        # Similar year (within 2 years)
        year_diff = abs(car1.year - car2.year)
        if year_diff <= 2:
            score += 0.2
        
        # Similar features
        if car1.bluetooth == car2.bluetooth:
            score += 0.05
        if car1.car_play == car2.car_play:
            score += 0.05
        
        return score
    
    def _extract_search_criteria(self, preferences: CustomerPreferences) -> dict[str, Any]:
        """Extract search criteria from preferences."""
        criteria = {}
        
        if preferences.min_price or preferences.max_price:
            criteria["price_range"] = {
                "min": preferences.min_price,
                "max": preferences.max_price
            }
        
        if preferences.preferred_makes:
            criteria["makes"] = preferences.preferred_makes
        
        if preferences.max_km:
            criteria["max_km"] = preferences.max_km
        
        if preferences.min_year or preferences.max_year:
            criteria["year_range"] = {
                "min": preferences.min_year,
                "max": preferences.max_year
            }
        
        return criteria
    
    def _generate_recommendation_reason(
        self, 
        preferences: CustomerPreferences, 
        total_matches: int
    ) -> str:
        """Generate human-readable recommendation reason."""
        reasons = []
        
        if preferences.max_price:
            reasons.append(f"within your budget of ${preferences.max_price:,.0f}")
        
        if preferences.preferred_makes:
            makes_str = ", ".join(preferences.preferred_makes)
            reasons.append(f"from preferred brands: {makes_str}")
        
        if preferences.max_km:
            reasons.append(f"with less than {preferences.max_km:,} km")
        
        if preferences.min_year:
            reasons.append(f"manufactured after {preferences.min_year}")
        
        base_reason = f"Found {total_matches} cars"
        if reasons:
            base_reason += " " + " and ".join(reasons)
        
        return base_reason