import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime
import pandas as pd
from pathlib import Path

from app.models.schemas import (
    BusinessIdeaCreate, BusinessIdeaUpdate, 
    BusinessIdeaResponse, Industry, BusinessModel
)
from app.services.scoring_service import _calculate_score_for_idea
from app.core.config import settings

# In-memory data store for demo purposes
# In a real application, this would be a database
_ideas_db = {}

def get_ideas(filters: Dict[str, Any], skip: int = 0, limit: int = 100) -> List[BusinessIdeaResponse]:
    """
    Get business ideas with optional filtering.
    
    Args:
        filters: Dictionary of filter criteria
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return
        
    Returns:
        List of business idea responses
    """
    # Filter ideas
    filtered_ideas = _ideas_db.values()
    
    # Apply filters
    if 'file_id' in filters:
        filtered_ideas = [idea for idea in filtered_ideas if idea.file_id == filters['file_id']]
    
    if 'min_score' in filters:
        filtered_ideas = [idea for idea in filtered_ideas if idea.score and idea.score >= filters['min_score']]
        
    if 'max_score' in filters:
        filtered_ideas = [idea for idea in filtered_ideas if idea.score and idea.score <= filters['max_score']]
        
    if 'industry' in filters:
        industry = filters['industry']
        if isinstance(industry, str):
            filtered_ideas = [idea for idea in filtered_ideas if idea.industry.value.lower() == industry.lower()]
    
    # Sort by score (descending)
    sorted_ideas = sorted(
        filtered_ideas, 
        key=lambda idea: idea.score if idea.score is not None else -1, 
        reverse=True
    )
    
    # Apply pagination
    paginated_ideas = sorted_ideas[skip:skip + limit]
    
    return paginated_ideas

def get_idea_by_id(idea_id: str) -> Optional[BusinessIdeaResponse]:
    """
    Get a specific business idea by ID.
    
    Args:
        idea_id: Unique identifier for the business idea
        
    Returns:
        Business idea response if found, None otherwise
    """
    return _ideas_db.get(idea_id)

def create_idea(idea: BusinessIdeaCreate) -> BusinessIdeaResponse:
    """
    Create a new business idea manually.
    
    Args:
        idea: Business idea creation data
        
    Returns:
        Created business idea response
    """
    # Generate a unique ID
    idea_id = str(uuid.uuid4())
    
    # Create timestamp
    now = datetime.now()
    
    # Convert to Series for scoring
    idea_series = pd.Series({
        'name': idea.name,
        'description': idea.description,
        'industry': idea.industry.value,
        'business_model': idea.business_model.value,
        'problem_statement': idea.problem_statement,
        'solution_description': idea.solution_description,
        'target_market': idea.target_market,
        'market_size_tam': idea.market_size_tam,
        'market_size_sam': idea.market_size_sam,
        'market_size_som': idea.market_size_som,
        'competition_level': idea.competition_level,
        'founding_team_experience': idea.founding_team_experience,
        'product_complexity': idea.product_complexity,
        'regulatory_risk': idea.regulatory_risk,
        'has_network_effects': idea.has_network_effects,
        'has_public_customers': idea.has_public_customers,
        'has_recurring_revenue': idea.has_recurring_revenue,
        'estimated_cac': idea.estimated_cac,
        'estimated_ltv': idea.estimated_ltv,
        'has_ip_patents': idea.has_ip_patents,
        'social_impact_score': idea.social_impact_score,
        'environmental_impact_score': idea.environmental_impact_score
    })
    
    # Calculate initial score
    score_result = _calculate_score_for_idea(idea_series, None)
    
    # Create business idea response
    business_idea = BusinessIdeaResponse(
        id=idea_id,
        name=idea.name,
        description=idea.description,
        industry=idea.industry,
        business_model=idea.business_model,
        problem_statement=idea.problem_statement,
        solution_description=idea.solution_description,
        target_market=idea.target_market,
        market_size_tam=idea.market_size_tam,
        market_size_sam=idea.market_size_sam,
        market_size_som=idea.market_size_som,
        competition_level=idea.competition_level,
        founding_team_experience=idea.founding_team_experience,
        product_complexity=idea.product_complexity,
        regulatory_risk=idea.regulatory_risk,
        has_network_effects=idea.has_network_effects,
        has_public_customers=idea.has_public_customers,
        has_recurring_revenue=idea.has_recurring_revenue,
        estimated_cac=idea.estimated_cac,
        estimated_ltv=idea.estimated_ltv,
        has_ip_patents=idea.has_ip_patents,
        social_impact_score=idea.social_impact_score,
        environmental_impact_score=idea.environmental_impact_score,
        file_id=idea.file_id,
        score=score_result.total_score,
        risk_flags=score_result.risk_flags,
        explanation=score_result.explanation,
        created_at=now,
        updated_at=now
    )
    
    # Store in "database"
    _ideas_db[idea_id] = business_idea
    
    return business_idea

def update_idea(idea_id: str, idea_update: BusinessIdeaUpdate) -> Optional[BusinessIdeaResponse]:
    """
    Update an existing business idea.
    
    Args:
        idea_id: Unique identifier for the business idea
        idea_update: Business idea update data
        
    Returns:
        Updated business idea response if found, None otherwise
    """
    # Check if the idea exists
    existing_idea = _ideas_db.get(idea_id)
    if not existing_idea:
        return None
    
    # Update fields if provided in the update
    updated_data = existing_idea.dict()
    update_dict = {k: v for k, v in idea_update.dict().items() if v is not None}
    updated_data.update(update_dict)
    
    # Update timestamp
    updated_data['updated_at'] = datetime.now()
    
    # Convert to Series for scoring
    idea_series = pd.Series(updated_data)
    
    # Recalculate score if relevant fields were updated
    score_fields = [
        'industry', 'business_model', 'market_size_tam', 'competition_level',
        'founding_team_experience', 'product_complexity', 'regulatory_risk',
        'has_network_effects', 'has_public_customers', 'has_recurring_revenue',
        'estimated_cac', 'estimated_ltv', 'has_ip_patents',
        'social_impact_score', 'environmental_impact_score'
    ]
    
    if any(field in update_dict for field in score_fields):
        score_result = _calculate_score_for_idea(idea_series, None)
        updated_data['score'] = score_result.total_score
        updated_data['risk_flags'] = score_result.risk_flags
        updated_data['explanation'] = score_result.explanation
    
    # Create updated business idea
    updated_idea = BusinessIdeaResponse(**updated_data)
    
    # Update in "database"
    _ideas_db[idea_id] = updated_idea
    
    return updated_idea

def delete_idea(idea_id: str) -> bool:
    """
    Delete a business idea.
    
    Args:
        idea_id: Unique identifier for the business idea
        
    Returns:
        True if deleted, False if not found
    """
    if idea_id in _ideas_db:
        del _ideas_db[idea_id]
        return True
    
    return False

def import_ideas_from_file(file_id: str, file_path: Path) -> List[BusinessIdeaResponse]:
    """
    Import business ideas from a processed Excel or CSV file.
    
    Args:
        file_id: Unique identifier for the uploaded file
        file_path: Path to the processed file
        
    Returns:
        List of imported business idea responses
    """
    # Load the processed data
    if file_path.suffix.lower() == '.xlsx':
        df = pd.read_excel(file_path, engine="openpyxl")
    elif file_path.suffix.lower() == '.csv':
        df = pd.read_csv(file_path)
    else:
        raise ValueError(f"Unsupported file format: {file_path.suffix}")
    
    # Create timestamp
    now = datetime.now()
    
    # Import each row as a business idea
    imported_ideas = []
    for _, row in df.iterrows():
        # Generate a unique ID
        idea_id = str(uuid.uuid4())
        
        # Extract and normalize fields
        name = row.get('name', row.get('idea_name', f"Idea-{idea_id[:8]}"))
        description = row.get('description', '')
        
        # Convert industry to enum
        industry_str = str(row.get('industry', '')).lower()
        industry = _map_to_industry(industry_str)
        
        # Convert business model to enum
        business_model_str = str(row.get('business_model', '')).lower()
        business_model = _map_to_business_model(business_model_str)
        
        # Calculate score
        score_result = _calculate_score_for_idea(row, None)
        
        # Create business idea
        business_idea = BusinessIdeaResponse(
            id=idea_id,
            name=name,
            description=description,
            industry=industry,
            business_model=business_model,
            problem_statement=row.get('problem_statement', ''),
            solution_description=row.get('solution_description', ''),
            target_market=row.get('target_market', ''),
            market_size_tam=row.get('market_size_tam', row.get('tam', None)),
            market_size_sam=row.get('market_size_sam', row.get('sam', None)),
            market_size_som=row.get('market_size_som', row.get('som', None)),
            competition_level=row.get('competition_level', None),
            founding_team_experience=row.get('founding_team_experience', None),
            product_complexity=row.get('product_complexity', None),
            regulatory_risk=row.get('regulatory_risk', None),
            has_network_effects=row.get('has_network_effects', None),
            has_public_customers=row.get('has_public_customers', None),
            has_recurring_revenue=row.get('has_recurring_revenue', None),
            estimated_cac=row.get('estimated_cac', None),
            estimated_ltv=row.get('estimated_ltv', None),
            has_ip_patents=row.get('has_ip_patents', None),
            social_impact_score=row.get('social_impact_score', None),
            environmental_impact_score=row.get('environmental_impact_score', None),
            file_id=file_id,
            score=score_result.total_score,
            risk_flags=score_result.risk_flags,
            explanation=score_result.explanation,
            created_at=now,
            updated_at=now
        )
        
        # Store in "database"
        _ideas_db[idea_id] = business_idea
        imported_ideas.append(business_idea)
    
    return imported_ideas

def _map_to_industry(industry_str: str) -> Industry:
    """
    Map a string to an Industry enum value.
    
    Args:
        industry_str: String representation of industry
        
    Returns:
        Industry enum value
    """
    mapping = {
        'fintech': Industry.FINTECH,
        'healthtech': Industry.HEALTHTECH,
        'edtech': Industry.EDTECH,
        'ecommerce': Industry.ECOMMERCE,
        'enterprise_saas': Industry.ENTERPRISE_SaaS,
        'saas': Industry.ENTERPRISE_SaaS,
        'enterprise': Industry.ENTERPRISE_SaaS,
        'consumer_apps': Industry.CONSUMER_APPS,
        'consumer': Industry.CONSUMER_APPS,
        'mobile': Industry.CONSUMER_APPS,
        'ai_ml': Industry.AI_ML,
        'ai': Industry.AI_ML,
        'ml': Industry.AI_ML,
        'artificial intelligence': Industry.AI_ML,
        'machine learning': Industry.AI_ML,
        'biotech': Industry.BIOTECH,
        'cleantech': Industry.CLEANTECH,
        'iot': Industry.IOT,
        'internet of things': Industry.IOT,
        'blockchain': Industry.BLOCKCHAIN,
        'crypto': Industry.BLOCKCHAIN
    }
    
    # Try to match against mapping
    for key, value in mapping.items():
        if key in industry_str:
            return value
    
    # Default to OTHER
    return Industry.OTHER

def _map_to_business_model(business_model_str: str) -> BusinessModel:
    """
    Map a string to a BusinessModel enum value.
    
    Args:
        business_model_str: String representation of business model
        
    Returns:
        BusinessModel enum value
    """
    mapping = {
        'saas': BusinessModel.SAAS,
        'software as a service': BusinessModel.SAAS,
        'marketplace': BusinessModel.MARKETPLACE,
        'consumer_app': BusinessModel.CONSUMER_APP,
        'consumer app': BusinessModel.CONSUMER_APP,
        'app': BusinessModel.CONSUMER_APP,
        'ecommerce': BusinessModel.ECOMMERCE,
        'e-commerce': BusinessModel.ECOMMERCE,
        'subscription': BusinessModel.SUBSCRIPTION,
        'freemium': BusinessModel.FREEMIUM,
        'hardware': BusinessModel.HARDWARE,
        'advertising': BusinessModel.ADVERTISING,
        'data_monetization': BusinessModel.DATA_MONETIZATION,
        'data monetization': BusinessModel.DATA_MONETIZATION,
        'licensing': BusinessModel.LICENSING
    }
    
    # Try to match against mapping
    for key, value in mapping.items():
        if key in business_model_str:
            return value
    
    # Default to OTHER
    return BusinessModel.OTHER
