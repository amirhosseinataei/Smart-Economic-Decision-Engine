"""
Schema definitions for chatbot queries and responses
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from enum import Enum


class SearchGoalType(str, Enum):
    """Types of search goals"""
    RESIDENTIAL_RENT = "residential_rent"
    RESIDENTIAL_PURCHASE = "residential_purchase"
    VEHICLE_PURCHASE = "vehicle_purchase"
    VEHICLE_LEASE = "vehicle_lease"
    ELECTRONICS = "electronics"
    GENERAL = "general"


class BudgetSource(str, Enum):
    """Sources of budget"""
    LIQUIDITY = "liquidity"
    LOAN = "loan"
    LIQUIDITY_LOAN = "liquidity + loan"
    MONTHLY_PAYMENT = "monthly_payment"


class Priority(str, Enum):
    """Priority levels"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class UserProfile(BaseModel):
    """User financial profile"""
    liquidity: float = Field(default=0.0, ge=0, description="Available cash in Tomans")
    loan_amount: float = Field(default=0.0, ge=0, description="Loan amount in Tomans")
    loan_availability_months: int = Field(default=0, ge=0, description="Months until loan is available")
    max_monthly_payment: float = Field(default=0.0, ge=0, description="Maximum monthly payment in Tomans")
    existing_obligations: float = Field(default=0.0, ge=0, description="Existing monthly obligations")
    
    @property
    def total_budget(self) -> float:
        """Calculate total available budget"""
        return self.liquidity + self.loan_amount
    
    @property
    def effective_monthly_budget(self) -> float:
        """Calculate effective monthly budget after obligations"""
        return self.max_monthly_payment - self.existing_obligations


class SearchGoal(BaseModel):
    """Individual search goal"""
    goal_id: int = Field(description="Unique goal identifier")
    type: SearchGoalType = Field(description="Type of search goal")
    target_location: str = Field(default="", description="Target location or area")
    budget_source: BudgetSource = Field(description="Source of budget for this goal")
    priority: Priority = Field(default=Priority.MEDIUM, description="Priority level")
    search_type: str = Field(description="Search type (e.g., رهن کامل, خرید نقدی)")
    min_price: Optional[float] = Field(default=None, ge=0, description="Minimum price")
    max_price: Optional[float] = Field(default=None, ge=0, description="Maximum price")
    max_monthly_lease_payment: Optional[float] = Field(default=None, ge=0)
    additional_filters: Dict[str, Any] = Field(default_factory=dict, description="Additional search filters")
    
    @validator('max_price')
    def validate_price_range(cls, v, values):
        """Validate price range"""
        if 'min_price' in values and v and values['min_price']:
            if v < values['min_price']:
                raise ValueError('max_price must be greater than min_price')
        return v


class StructuredQuery(BaseModel):
    """Structured query schema for search execution"""
    user_profile: UserProfile = Field(description="User financial profile")
    search_goals: List[SearchGoal] = Field(description="List of search goals")
    is_multi_goal: bool = Field(default=False, description="Whether multiple goals exist")
    context: Dict[str, Any] = Field(default_factory=dict, description="Additional context")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="Confidence score")
    timestamp: Optional[str] = Field(default=None, description="Query timestamp")
    
    @validator('search_goals')
    def validate_goals(cls, v):
        """Validate search goals"""
        if not v:
            raise ValueError('At least one search goal is required')
        return v


class ChatbotResponse(BaseModel):
    """Response from chatbot engine"""
    success: bool = Field(description="Whether processing was successful")
    query: Optional[StructuredQuery] = Field(default=None, description="Structured query")
    message: str = Field(default="", description="Response message to user")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="Confidence score")
    requires_clarification: bool = Field(default=False, description="Whether clarification is needed")
    clarification_questions: List[str] = Field(default_factory=list, description="Questions for clarification")
    errors: List[str] = Field(default_factory=list, description="List of errors if any")

