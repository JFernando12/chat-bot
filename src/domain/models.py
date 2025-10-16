"""
Domain models for the Kavak commercial agent.
Following Domain-Driven Design principles and SOLID patterns.
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from enum import Enum
from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel, Field, field_validator
import re


class CarCondition(str, Enum):
    """Car condition enumeration."""
    EXCELLENT = "excelente"
    GOOD = "bueno"
    FAIR = "regular"


class TransmissionType(str, Enum):
    """Transmission type enumeration."""
    MANUAL = "manual"
    AUTOMATIC = "automatico"
    CVT = "cvt"
    DCT = "dct"


class FuelType(str, Enum):
    """Fuel type enumeration."""
    GASOLINE = "gasolina"
    DIESEL = "diesel"
    HYBRID = "hibrido"
    ELECTRIC = "electrico"


class Car(BaseModel):
    """Car entity following Domain-Driven Design."""
    
    stock_id: str = Field(..., description="Unique stock identifier")
    make: str = Field(..., description="Car manufacturer")
    model: str = Field(..., description="Car model")
    year: int = Field(..., ge=2000, le=2030, description="Manufacturing year")
    version: str = Field(..., description="Car version/trim")
    price: Decimal = Field(..., ge=0, description="Car price in MXN")
    km: int = Field(..., ge=0, description="Kilometers driven")
    
    # Optional features
    bluetooth: Optional[bool] = Field(None, description="Bluetooth connectivity")
    car_play: Optional[bool] = Field(None, description="Apple CarPlay support")
    
    # Dimensions in mm
    length: Optional[float] = Field(None, ge=0, description="Car length in mm")
    width: Optional[float] = Field(None, ge=0, description="Car width in mm")
    height: Optional[float] = Field(None, ge=0, description="Car height in mm")
    
    # Derived properties
    condition: Optional[CarCondition] = None
    fuel_type: Optional[FuelType] = None
    transmission: Optional[TransmissionType] = None
    
    @field_validator('make', 'model')
    def normalize_text(cls, v):
        """Normalize make and model text for consistent search."""
        if v:
            return v.strip().title()
        return v
    
    @property
    def formatted_price(self) -> str:
        """Format price in Mexican pesos."""
        return f"${self.price:,.0f} MXN"
    
    @property
    def age_in_years(self) -> int:
        """Calculate car age in years."""
        current_year = datetime.now().year
        return current_year - self.year
    
    @property
    def is_recent_model(self) -> bool:
        """Check if car is from recent years (last 3 years)."""
        return self.age_in_years <= 3
    
    def __str__(self) -> str:
        return f"{self.year} {self.make} {self.model} - {self.formatted_price}"


class CustomerPreferences(BaseModel):
    """Customer preferences for car recommendations."""
    
    min_price: Optional[Decimal] = Field(None, ge=0, description="Minimum price range")
    max_price: Optional[Decimal] = Field(None, ge=0, description="Maximum price range")
    preferred_makes: Optional[List[str]] = Field(default_factory=list, description="Preferred car brands")
    max_km: Optional[int] = Field(None, ge=0, description="Maximum kilometers acceptable")
    min_year: Optional[int] = Field(None, ge=2000, description="Minimum manufacturing year")
    max_year: Optional[int] = Field(None, le=2030, description="Maximum manufacturing year")
    features_required: Optional[List[str]] = Field(default_factory=list, description="Required features")
    car_type: Optional[str] = Field(None, description="Type of car (sedan, SUV, etc.)")
    
    @field_validator('max_price')
    def validate_price_range(cls, v, values):
        """Ensure max_price is greater than min_price."""
        if v and 'min_price' in values and values['min_price']:
            if v <= values['min_price']:
                raise ValueError('max_price must be greater than min_price')
        return v


class FinancingPlan(BaseModel):
    """Financing plan calculation model."""
    
    car_price: Decimal = Field(..., ge=0, description="Car price")
    down_payment: Decimal = Field(..., ge=0, description="Down payment amount")
    interest_rate: Decimal = Field(default=Decimal('0.10'), description="Annual interest rate")
    term_years: int = Field(..., ge=3, le=6, description="Financing term in years")
    
    @field_validator('down_payment')
    def validate_down_payment(cls, v, values):
        """Ensure down payment doesn't exceed car price."""
        if v and 'car_price' in values and values['car_price']:
            if v > values['car_price']:
                raise ValueError('down_payment cannot exceed car_price')
        return v
    
    @property
    def financed_amount(self) -> Decimal:
        """Calculate the amount to be financed."""
        return self.car_price - self.down_payment
    
    @property
    def monthly_payment(self) -> Decimal:
        """Calculate monthly payment using compound interest formula."""
        if self.financed_amount <= 0:
            return Decimal('0')
        
        monthly_rate = self.interest_rate / 12
        num_payments = self.term_years * 12
        
        if monthly_rate == 0:
            return self.financed_amount / num_payments
        
        factor = (1 + monthly_rate) ** num_payments
        monthly_payment = self.financed_amount * (monthly_rate * factor) / (factor - 1)
        
        return monthly_payment.quantize(Decimal('0.01'))
    
    @property
    def total_amount(self) -> Decimal:
        """Calculate total amount to be paid."""
        return self.down_payment + (self.monthly_payment * self.term_years * 12)
    
    @property
    def total_interest(self) -> Decimal:
        """Calculate total interest paid."""
        return self.total_amount - self.car_price
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert financing plan to dictionary for API response."""
        return {
            "car_price": f"${self.car_price:,.0f} MXN",
            "down_payment": f"${self.down_payment:,.0f} MXN",
            "financed_amount": f"${self.financed_amount:,.0f} MXN",
            "interest_rate": f"{self.interest_rate * 100:.1f}%",
            "term_years": self.term_years,
            "monthly_payment": f"${self.monthly_payment:,.0f} MXN",
            "total_amount": f"${self.total_amount:,.0f} MXN",
            "total_interest": f"${self.total_interest:,.0f} MXN"
        }


class ChatMessage(BaseModel):
    """Chat message model for conversation handling."""
    
    user_id: str = Field(..., description="User identifier")
    message_id: str = Field(..., description="Message identifier")
    content: str = Field(..., min_length=1, description="Message content")
    timestamp: datetime = Field(default_factory=datetime.now, description="Message timestamp")
    message_type: str = Field(default="user", description="Message type (user/agent)")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional context")


class ConversationState(BaseModel):
    """Conversation state for maintaining context."""
    
    user_id: str = Field(..., description="User identifier")
    current_preferences: Optional[CustomerPreferences] = None
    interested_cars: List[str] = Field(default_factory=list, description="List of car stock_ids user showed interest in")
    conversation_stage: str = Field(default="greeting", description="Current conversation stage")
    last_updated: datetime = Field(default_factory=datetime.now)
    
    class Config:
        arbitrary_types_allowed = True