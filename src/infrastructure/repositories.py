"""
Repository pattern implementation for car data access.
Following SOLID principles and dependency inversion.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
import pandas as pd
from pathlib import Path
from decimal import Decimal
import logging

from ..domain.models import Car, CustomerPreferences


logger = logging.getLogger(__name__)


class CarRepositoryInterface(ABC):
    """Abstract interface for car repository following Dependency Inversion Principle."""
    
    @abstractmethod
    def get_all_cars(self) -> List[Car]:
        """Get all cars from the repository."""
        pass
    
    @abstractmethod
    def get_car_by_stock_id(self, stock_id: str) -> Optional[Car]:
        """Get a specific car by stock ID."""
        pass
    
    @abstractmethod
    def search_cars(self, preferences: CustomerPreferences) -> List[Car]:
        """Search cars based on customer preferences."""
        pass
    
    @abstractmethod
    def get_cars_by_make(self, make: str) -> List[Car]:
        """Get cars filtered by manufacturer."""
        pass
    
    @abstractmethod
    def get_cars_in_price_range(self, min_price: Decimal, max_price: Decimal) -> List[Car]:
        """Get cars within a specific price range."""
        pass


class CSVCarRepository(CarRepositoryInterface):
    """
    Concrete implementation of car repository using CSV data source.
    Implements Single Responsibility Principle - only handles data access.
    """
    
    def __init__(self, csv_path: str):
        """Initialize repository with CSV file path."""
        self.csv_path = Path(csv_path)
        self._cars_cache: Optional[List[Car]] = None
        self._df: Optional[pd.DataFrame] = None
        
    def _load_data(self) -> pd.DataFrame:
        """Load and cache data from CSV file."""
        if self._df is None:
            try:
                self._df = pd.read_csv(self.csv_path)
                logger.info(f"Loaded {len(self._df)} cars from {self.csv_path}")
            except Exception as e:
                logger.error(f"Error loading CSV data: {e}")
                raise
        return self._df
    
    def _normalize_boolean(self, value: Any) -> Optional[bool]:
        """Normalize boolean values from CSV."""
        if pd.isna(value) or value == "":
            return None
        if isinstance(value, str):
            return value.lower() in ['sí', 'si', 'yes', 'true', '1']
        return bool(value)
    
    def _normalize_numeric(self, value: Any) -> Optional[float]:
        """Normalize numeric values from CSV."""
        if pd.isna(value) or value == "":
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
    
    def _df_row_to_car(self, row: pd.Series) -> Car:
        """Convert DataFrame row to Car model."""
        try:
            return Car(
                stock_id=str(row['stock_id']),
                make=str(row['make']),
                model=str(row['model']),
                year=int(row['year']),
                version=str(row['version']),
                price=Decimal(str(row['price'])),
                km=int(row['km']),
                bluetooth=self._normalize_boolean(row.get('bluetooth')),
                car_play=self._normalize_boolean(row.get('car_play')),
                length=self._normalize_numeric(row.get('largo')),
                width=self._normalize_numeric(row.get('ancho')),
                height=self._normalize_numeric(row.get('altura'))
            )
        except Exception as e:
            logger.warning(f"Error converting row to Car: {e}, row: {row.to_dict()}")
            raise
    
    def get_all_cars(self) -> List[Car]:
        """Get all cars from the repository."""
        if self._cars_cache is None:
            df = self._load_data()
            self._cars_cache = []
            
            for _, row in df.iterrows():
                try:
                    car = self._df_row_to_car(row)
                    self._cars_cache.append(car)
                except Exception as e:
                    logger.warning(f"Skipping invalid car row: {e}")
                    continue
                    
            logger.info(f"Loaded {len(self._cars_cache)} valid cars")
        
        return self._cars_cache.copy()
    
    def get_car_by_stock_id(self, stock_id: str) -> Optional[Car]:
        """Get a specific car by stock ID."""
        cars = self.get_all_cars()
        for car in cars:
            if car.stock_id == stock_id:
                return car
        return None
    
    def search_cars(self, preferences: CustomerPreferences) -> List[Car]:
        """Search cars based on customer preferences."""
        cars = self.get_all_cars()
        filtered_cars = cars.copy()
        
        # Filter by price range
        if preferences.min_price is not None:
            filtered_cars = [car for car in filtered_cars if car.price >= preferences.min_price]
        
        if preferences.max_price is not None:
            filtered_cars = [car for car in filtered_cars if car.price <= preferences.max_price]
        
        # Filter by preferred makes
        if preferences.preferred_makes:
            normalized_makes = [make.lower() for make in preferences.preferred_makes]
            filtered_cars = [
                car for car in filtered_cars 
                if car.make.lower() in normalized_makes
            ]
        
        # Filter by maximum kilometers
        if preferences.max_km is not None:
            filtered_cars = [car for car in filtered_cars if car.km <= preferences.max_km]
        
        # Filter by year range
        if preferences.min_year is not None:
            filtered_cars = [car for car in filtered_cars if car.year >= preferences.min_year]
        
        if preferences.max_year is not None:
            filtered_cars = [car for car in filtered_cars if car.year <= preferences.max_year]
        
        # Filter by required features
        if preferences.features_required:
            for feature in preferences.features_required:
                feature_lower = feature.lower()
                if 'bluetooth' in feature_lower:
                    filtered_cars = [car for car in filtered_cars if car.bluetooth is True]
                elif 'carplay' in feature_lower or 'car play' in feature_lower:
                    filtered_cars = [car for car in filtered_cars if car.car_play is True]
        
        # Sort by relevance (price ascending, year descending, km ascending)
        filtered_cars.sort(key=lambda car: (car.price, -car.year, car.km))
        
        logger.info(f"Found {len(filtered_cars)} cars matching preferences")
        return filtered_cars
    
    def get_cars_by_make(self, make: str) -> List[Car]:
        """Get cars filtered by manufacturer."""
        cars = self.get_all_cars()
        make_normalized = make.lower()
        return [car for car in cars if car.make.lower() == make_normalized]
    
    def get_cars_in_price_range(self, min_price: Decimal, max_price: Decimal) -> List[Car]:
        """Get cars within a specific price range."""
        cars = self.get_all_cars()
        return [
            car for car in cars 
            if min_price <= car.price <= max_price
        ]
    
    def get_unique_makes(self) -> List[str]:
        """Get list of unique car manufacturers."""
        cars = self.get_all_cars()
        makes = set(car.make for car in cars)
        return sorted(list(makes))
    
    def get_price_range(self) -> Dict[str, Decimal]:
        """Get the minimum and maximum prices in the catalog."""
        cars = self.get_all_cars()
        if not cars:
            return {"min": Decimal("0"), "max": Decimal("0")}
        
        prices = [car.price for car in cars]
        return {
            "min": min(prices),
            "max": max(prices)
        }
    
    def get_repository_stats(self) -> Dict[str, Any]:
        """Get repository statistics."""
        cars = self.get_all_cars()
        makes = self.get_unique_makes()
        price_range = self.get_price_range()
        
        return {
            "total_cars": len(cars),
            "unique_makes": len(makes),
            "makes_list": makes,
            "price_range": price_range,
            "year_range": {
                "min": min(car.year for car in cars) if cars else 0,
                "max": max(car.year for car in cars) if cars else 0
            }
        }