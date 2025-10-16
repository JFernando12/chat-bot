from decimal import Decimal
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from ...domain.models import Car, CustomerPreferences, FinancingPlan

class FinancingService():
    """
    Concrete implementation of financing service.
    Follows Single Responsibility Principle - only handles financing calculations.
    """
    
    def __init__(self, default_interest_rate: Decimal = Decimal('0.10')):
        """Initialize with default interest rate."""
        self.default_interest_rate = default_interest_rate
    
    def calculate_financing(
        self,
        car_price: Decimal,
        down_payment: Decimal,
        term_years: int
    ):
        """Calculate financing plan for a car."""
        return FinancingPlan(
            car_price=car_price,
            down_payment=down_payment,
            interest_rate=self.default_interest_rate,
            term_years=term_years
        )
    
    def get_financing_options(
        self,
        car_price: Decimal,
        max_monthly_payment: Optional[Decimal] = None
    ) -> List[FinancingPlan]:
        """Get multiple financing options for a car."""
        options = []
        
        # Different down payment scenarios: 10%, 20%, 30%
        down_payment_percentages = [Decimal('0.10'), Decimal('0.20'), Decimal('0.30')]
        
        # Different term options: 3, 4, 5, 6 years
        term_options = [3, 4, 5, 6]
        
        for down_percent in down_payment_percentages:
            down_payment = car_price * down_percent
            
            for term_years in term_options:
                financing_plan = self.calculate_financing(
                    car_price, down_payment, term_years
                )
                
                # Filter by max monthly payment if specified
                if max_monthly_payment is None or financing_plan.monthly_payment <= max_monthly_payment:
                    options.append(financing_plan)
        
        # Sort by monthly payment ascending
        options.sort(key=lambda plan: plan.monthly_payment)
        
        return options