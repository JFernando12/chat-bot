"""
Basic test for the Kavak Commercial Agent.
Run with: pytest tests/test_basic.py -v
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.domain.models import Car, CustomerPreferences, FinancingPlan
from decimal import Decimal


class TestDomainModels:
    """Test domain models."""
    
    def test_car_model_creation(self):
        """Test Car model creation and properties."""
        car = Car(
            stock_id="123456",
            make="Toyota",
            model="Corolla",
            year=2020,
            version="LE",
            price=Decimal("300000"),
            km=50000,
            bluetooth=True,
            car_play=True
        )
        
        assert car.stock_id == "123456"
        assert car.make == "Toyota"
        assert car.model == "Corolla"
        assert car.formatted_price == "$300,000 MXN"
        assert car.age_in_years >= 4  # Current year - 2020
        assert car.is_recent_model is False  # Older than 3 years
    
    def test_customer_preferences(self):
        """Test CustomerPreferences model."""
        preferences = CustomerPreferences(
            min_price=Decimal("200000"),
            max_price=Decimal("500000"),
            preferred_makes=["Toyota", "Honda"],
            max_km=80000,
            min_year=2018
        )
        
        assert preferences.min_price == Decimal("200000")
        assert preferences.max_price == Decimal("500000")
        assert "Toyota" in preferences.preferred_makes
    
    def test_financing_plan(self):
        """Test FinancingPlan calculations."""
        plan = FinancingPlan(
            car_price=Decimal("300000"),
            down_payment=Decimal("60000"),
            interest_rate=Decimal("0.10"),
            term_years=4
        )
        
        assert plan.financed_amount == Decimal("240000")
        assert plan.monthly_payment > 0
        assert plan.total_amount > plan.car_price
        assert plan.total_interest > 0
    
    def test_financing_plan_validation(self):
        """Test FinancingPlan validation."""
        with pytest.raises(ValueError):
            # Down payment > car price should fail
            FinancingPlan(
                car_price=Decimal("300000"),
                down_payment=Decimal("400000"),  # Too high
                term_years=4
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])