from typing import Dict, List, Optional, Union
from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field, validator

# File Upload Schemas
class UploadResponse(BaseModel):
    filename: str
    saved_as: str
    size_bytes: int
    record_count: int
    columns: List[str]
    status: str
    message: str

# Scoring Schemas
class ScoreCategory(str, Enum):
    MARKET_BUSINESS_MODEL = "market_business_model"
    COMPETITIVE_LANDSCAPE = "competitive_landscape"
    EXECUTION_TEAM = "execution_team"
    RISK_FACTORS = "risk_factors"
    NETWORK_PLATFORM_RISKS = "network_platform_risks"
    SOCIAL_ENVIRONMENTAL_IMPACT = "social_environmental_impact"

class WeightConfiguration(BaseModel):
    market_business_model: float = Field(35.0, ge=0, le=100)
    competitive_landscape: float = Field(15.0, ge=0, le=100)
    execution_team: float = Field(20.0, ge=0, le=100)
    risk_factors: float = Field(10.0, ge=0, le=100)
    network_platform_risks: float = Field(10.0, ge=0, le=100)
    social_environmental_impact: float = Field(10.0, ge=0, le=100)
    
    @validator('market_business_model', 'competitive_landscape', 'execution_team', 
               'risk_factors', 'network_platform_risks', 'social_environmental_impact')
    def round_to_one_decimal(cls, v):
        return round(v, 1)

class CategoryScore(BaseModel):
    category: ScoreCategory
    score: float
    weight: float
    weighted_score: float
    factors: Dict[str, float] = {}

class ScoringInput(BaseModel):
    file_id: str
    weights: Optional[WeightConfiguration] = None

class ScoreResponse(BaseModel):
    id: str
    idea_name: str
    file_id: str
    total_score: float
    category_scores: List[CategoryScore]
    risk_flags: List[str] = []
    explanation: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class ScoreSummary(BaseModel):
    file_id: str
    average_score: float
    highest_score: float
    lowest_score: float
    count: int
    distribution: Dict[str, int]

# Business Idea Schemas
class Industry(str, Enum):
    FINTECH = "fintech"
    HEALTHTECH = "healthtech"
    EDTECH = "edtech"
    ECOMMERCE = "ecommerce"
    ENTERPRISE_SaaS = "enterprise_saas"
    CONSUMER_APPS = "consumer_apps"
    AI_ML = "ai_ml"
    BIOTECH = "biotech"
    CLEANTECH = "cleantech"
    IOT = "iot"
    BLOCKCHAIN = "blockchain"
    OTHER = "other"

class BusinessModel(str, Enum):
    SAAS = "saas"
    MARKETPLACE = "marketplace"
    CONSUMER_APP = "consumer_app"
    ECOMMERCE = "ecommerce"
    SUBSCRIPTION = "subscription"
    FREEMIUM = "freemium"
    HARDWARE = "hardware"
    ADVERTISING = "advertising"
    DATA_MONETIZATION = "data_monetization"
    LICENSING = "licensing"
    OTHER = "other"

class BusinessIdeaBase(BaseModel):
    name: str
    description: str
    industry: Industry
    business_model: BusinessModel
    problem_statement: str
    solution_description: str
    target_market: str
    market_size_tam: Optional[float] = None
    market_size_sam: Optional[float] = None
    market_size_som: Optional[float] = None
    competition_level: Optional[int] = Field(None, ge=1, le=10)
    founding_team_experience: Optional[int] = Field(None, ge=1, le=10)
    product_complexity: Optional[int] = Field(None, ge=1, le=10)
    regulatory_risk: Optional[int] = Field(None, ge=1, le=10)
    has_network_effects: Optional[bool] = None
    has_public_customers: Optional[bool] = None
    has_recurring_revenue: Optional[bool] = None
    estimated_cac: Optional[float] = None
    estimated_ltv: Optional[float] = None
    has_ip_patents: Optional[bool] = None
    social_impact_score: Optional[int] = Field(None, ge=1, le=10)
    environmental_impact_score: Optional[int] = Field(None, ge=1, le=10)

class BusinessIdeaCreate(BusinessIdeaBase):
    file_id: Optional[str] = None
    raw_data: Optional[Dict[str, Union[str, int, float, bool]]] = None

class BusinessIdeaUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    industry: Optional[Industry] = None
    business_model: Optional[BusinessModel] = None
    problem_statement: Optional[str] = None
    solution_description: Optional[str] = None
    target_market: Optional[str] = None
    market_size_tam: Optional[float] = None
    market_size_sam: Optional[float] = None
    market_size_som: Optional[float] = None
    competition_level: Optional[int] = Field(None, ge=1, le=10)
    founding_team_experience: Optional[int] = Field(None, ge=1, le=10)
    product_complexity: Optional[int] = Field(None, ge=1, le=10)
    regulatory_risk: Optional[int] = Field(None, ge=1, le=10)
    has_network_effects: Optional[bool] = None
    has_public_customers: Optional[bool] = None
    has_recurring_revenue: Optional[bool] = None
    estimated_cac: Optional[float] = None
    estimated_ltv: Optional[float] = None
    has_ip_patents: Optional[bool] = None
    social_impact_score: Optional[int] = Field(None, ge=1, le=10)
    environmental_impact_score: Optional[int] = Field(None, ge=1, le=10)

class BusinessIdeaResponse(BusinessIdeaBase):
    id: str
    file_id: Optional[str] = None
    score: Optional[float] = None
    risk_flags: List[str] = []
    explanation: Optional[str] = None
    created_at: datetime
    updated_at: datetime
