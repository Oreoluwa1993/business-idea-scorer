import os
import uuid
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path

import openai
from fastapi import HTTPException

from app.core.config import settings
from app.models.schemas import (
    ScoreResponse, CategoryScore, ScoreCategory, 
    WeightConfiguration, ScoreSummary
)

def calculate_scores(file_id: str, weights: Optional[WeightConfiguration] = None) -> List[ScoreResponse]:
    """
    Calculate scores for business ideas in the uploaded file.
    
    Args:
        file_id: Unique identifier for the uploaded file
        weights: Optional custom weight configuration (defaults to settings if None)
        
    Returns:
        List of score responses for each business idea
    """
    # Find the processed file
    upload_dir = Path("./uploaded_files")
    file_pattern = f"*{file_id}*_processed*"
    processed_files = list(upload_dir.glob(file_pattern))
    
    if not processed_files:
        raise FileNotFoundError(f"Processed file for {file_id} not found")
    
    processed_file = processed_files[0]
    
    # Load the processed data
    if processed_file.suffix.lower() == '.xlsx':
        df = pd.read_excel(processed_file, engine="openpyxl")
    elif processed_file.suffix.lower() == '.csv':
        df = pd.read_csv(processed_file)
    else:
        raise ValueError(f"Unsupported file format: {processed_file.suffix}")
    
    # Use default weights if not provided
    if weights is None:
        weights = WeightConfiguration(
            market_business_model=settings.WEIGHT_MARKET_BUSINESS_MODEL,
            competitive_landscape=settings.WEIGHT_COMPETITIVE_LANDSCAPE,
            execution_team=settings.WEIGHT_EXECUTION_TEAM,
            risk_factors=settings.WEIGHT_RISK_FACTORS,
            network_platform_risks=settings.WEIGHT_NETWORK_PLATFORM_RISKS,
            social_environmental_impact=settings.WEIGHT_SOCIAL_ENVIRONMENTAL_IMPACT
        )
        
    # Calculate scores for each business idea
    scores = []
    for _, row in df.iterrows():
        score = _calculate_score_for_idea(row, weights)
        scores.append(score)
    
    return scores

def _calculate_score_for_idea(idea_data: pd.Series, weights: WeightConfiguration) -> ScoreResponse:
    """
    Calculate score for a single business idea based on the provided data.
    
    Args:
        idea_data: Series containing the business idea data
        weights: Weight configuration for the scoring algorithm
        
    Returns:
        Score response for the business idea
    """
    # Extract the idea name
    idea_name = idea_data.get('name', idea_data.get('idea_name', f"Idea-{uuid.uuid4().hex[:8]}"))
    
    # Calculate category scores
    category_scores = []
    risk_flags = []
    
    # 1. Market & Business Model Score (35%)
    market_score = _calculate_market_business_model_score(idea_data)
    category_scores.append(
        CategoryScore(
            category=ScoreCategory.MARKET_BUSINESS_MODEL,
            score=market_score,
            weight=weights.market_business_model,
            weighted_score=market_score * weights.market_business_model / 100,
            factors={
                "market_size": _get_market_size_score(idea_data),
                "recurring_revenue": _get_recurring_revenue_score(idea_data),
                "scalability": _get_scalability_score(idea_data)
            }
        )
    )
    
    # 2. Competitive Landscape Score (15%)
    competitive_score = _calculate_competitive_landscape_score(idea_data)
    category_scores.append(
        CategoryScore(
            category=ScoreCategory.COMPETITIVE_LANDSCAPE,
            score=competitive_score,
            weight=weights.competitive_landscape,
            weighted_score=competitive_score * weights.competitive_landscape / 100,
            factors={
                "competition_level": _get_competition_level_score(idea_data),
                "first_mover_advantage": _get_first_mover_advantage_score(idea_data)
            }
        )
    )
    
    # 3. Execution & Team Score (20%)
    execution_score = _calculate_execution_team_score(idea_data)
    category_scores.append(
        CategoryScore(
            category=ScoreCategory.EXECUTION_TEAM,
            score=execution_score,
            weight=weights.execution_team,
            weighted_score=execution_score * weights.execution_team / 100,
            factors={
                "founder_experience": _get_founder_experience_score(idea_data),
                "product_complexity": _get_product_complexity_score(idea_data),
                "unit_economics": _get_unit_economics_score(idea_data)
            }
        )
    )
    
    # 4. Risk Factors Score (10%)
    risk_score, new_risk_flags = _calculate_risk_factors_score(idea_data)
    risk_flags.extend(new_risk_flags)
    category_scores.append(
        CategoryScore(
            category=ScoreCategory.RISK_FACTORS,
            score=risk_score,
            weight=weights.risk_factors,
            weighted_score=risk_score * weights.risk_factors / 100,
            factors={
                "regulatory_risk": _get_regulatory_risk_score(idea_data),
                "public_sector_complexity": _get_public_sector_complexity_score(idea_data)
            }
        )
    )
    
    # 5. Network & Platform Risks Score (10%)
    network_score, new_risk_flags = _calculate_network_platform_risks_score(idea_data)
    risk_flags.extend(new_risk_flags)
    category_scores.append(
        CategoryScore(
            category=ScoreCategory.NETWORK_PLATFORM_RISKS,
            score=network_score,
            weight=weights.network_platform_risks,
            weighted_score=network_score * weights.network_platform_risks / 100,
            factors={
                "network_effects": _get_network_effects_score(idea_data),
                "marketplace_complexity": _get_marketplace_complexity_score(idea_data)
            }
        )
    )
    
    # 6. Social & Environmental Impact Score (10%)
    impact_score = _calculate_social_environmental_impact_score(idea_data)
    category_scores.append(
        CategoryScore(
            category=ScoreCategory.SOCIAL_ENVIRONMENTAL_IMPACT,
            score=impact_score,
            weight=weights.social_environmental_impact,
            weighted_score=impact_score * weights.social_environmental_impact / 100,
            factors={
                "social_impact": _get_social_impact_score(idea_data),
                "environmental_impact": _get_environmental_impact_score(idea_data)
            }
        )
    )
    
    # Calculate total score (weighted sum of category scores)
    total_score = sum(cs.weighted_score for cs in category_scores)
    
    # Create and return the score response
    return ScoreResponse(
        id=str(uuid.uuid4()),
        idea_name=idea_name,
        file_id=str(uuid.uuid4()),  # In a real implementation, this would be the actual file ID
        total_score=round(total_score, 2),
        category_scores=category_scores,
        risk_flags=risk_flags,
        explanation=None,  # This will be filled in by the GPT API
        created_at=datetime.now(),
        updated_at=datetime.now()
    )

def get_gpt_explanation(score: ScoreResponse) -> str:
    """
    Generate a detailed explanation for the score using the GPT API.
    
    Args:
        score: Score response for the business idea
        
    Returns:
        Generated explanation
    """
    # Skip if API key is not configured
    if not settings.OPENAI_API_KEY:
        return "GPT explanation not available (API key not configured)"
    
    try:
        # Configure OpenAI client
        openai.api_key = settings.OPENAI_API_KEY
        
        # Prepare category scores for the prompt
        category_scores_str = "\n".join([
            f"- {cs.category.value}: {cs.score}/100 (weight: {cs.weight}%)"
            for cs in score.category_scores
        ])
        
        # Prepare risk flags for the prompt
        risk_flags_str = "\n".join([f"- {flag}" for flag in score.risk_flags]) if score.risk_flags else "None identified"
        
        # Create the prompt
        prompt = f"""
        Generate a detailed explanation for a business idea score.
        
        Business Idea: {score.idea_name}
        Total Score: {score.total_score}/100
        
        Category Scores:
        {category_scores_str}
        
        Risk Flags:
        {risk_flags_str}
        
        Please provide:
        1. A detailed explanation of why this business idea received its score
        2. Analysis of strengths and weaknesses based on the category scores
        3. Recommendations for improvement
        4. Potential investment considerations
        
        The response should be professional, balanced, and insightful, suitable for investors reviewing this business idea.
        """
        
        # Call GPT API
        response = openai.ChatCompletion.create(
            model=settings.GPT_MODEL,
            messages=[
                {"role": "system", "content": "You are an expert business analyst providing detailed assessments of business ideas for investors."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=750,
            temperature=0.7
        )
        
        # Extract and return the explanation
        explanation = response.choices[0].message.content.strip()
        return explanation
    
    except Exception as e:
        # Log the error and return a generic explanation
        print(f"Error generating GPT explanation: {str(e)}")
        return f"Automated analysis: This business idea scored {score.total_score}/100, ranking it as {'high potential' if score.total_score >= 75 else 'medium potential' if score.total_score >= 50 else 'low potential'}. Key strengths include {', '.join([cs.category.value for cs in score.category_scores if cs.score >= 75])}. Areas for improvement include {', '.join([cs.category.value for cs in score.category_scores if cs.score < 50])}."

# Category scoring functions
def _calculate_market_business_model_score(idea_data: pd.Series) -> float:
    """Calculate the market and business model score (0-100)"""
    # Combine sub-scores with equal weights
    market_size_score = _get_market_size_score(idea_data)
    recurring_revenue_score = _get_recurring_revenue_score(idea_data)
    scalability_score = _get_scalability_score(idea_data)
    
    # Weight the sub-scores
    return (market_size_score * 0.5) + (recurring_revenue_score * 0.3) + (scalability_score * 0.2)

def _calculate_competitive_landscape_score(idea_data: pd.Series) -> float:
    """Calculate the competitive landscape score (0-100)"""
    competition_score = _get_competition_level_score(idea_data)
    first_mover_score = _get_first_mover_advantage_score(idea_data)
    
    return (competition_score * 0.7) + (first_mover_score * 0.3)

def _calculate_execution_team_score(idea_data: pd.Series) -> float:
    """Calculate the execution and team score (0-100)"""
    founder_score = _get_founder_experience_score(idea_data)
    complexity_score = _get_product_complexity_score(idea_data)
    economics_score = _get_unit_economics_score(idea_data)
    
    return (founder_score * 0.4) + (complexity_score * 0.3) + (economics_score * 0.3)

def _calculate_risk_factors_score(idea_data: pd.Series) -> tuple:
    """
    Calculate the risk factors score (0-100) and identify risk flags
    Returns: (score, risk_flags)
    """
    regulatory_score = _get_regulatory_risk_score(idea_data)
    public_sector_score = _get_public_sector_complexity_score(idea_data)
    
    risk_flags = []
    
    # Identify significant risk flags
    if regulatory_score < 50:
        risk_flags.append("High Regulatory Risk")
    if public_sector_score < 50:
        risk_flags.append("Public Sector Complexity")
    
    # Calculate the overall risk score (higher is better - less risky)
    risk_score = (regulatory_score * 0.6) + (public_sector_score * 0.4)
    
    return risk_score, risk_flags

def _calculate_network_platform_risks_score(idea_data: pd.Series) -> tuple:
    """
    Calculate the network and platform risks score (0-100) and identify risk flags
    Returns: (score, risk_flags)
    """
    network_score = _get_network_effects_score(idea_data)
    marketplace_score = _get_marketplace_complexity_score(idea_data)
    
    risk_flags = []
    
    # Identify significant risk flags
    if network_score < 50:
        risk_flags.append("Network Effect Dependency")
    if marketplace_score < 50:
        risk_flags.append("Marketplace/Chicken-and-Egg Challenge")
    
    # Calculate the overall network/platform score (higher is better - less risky)
    network_platform_score = (network_score * 0.5) + (marketplace_score * 0.5)
    
    return network_platform_score, risk_flags

def _calculate_social_environmental_impact_score(idea_data: pd.Series) -> float:
    """Calculate the social and environmental impact score (0-100)"""
    social_score = _get_social_impact_score(idea_data)
    environmental_score = _get_environmental_impact_score(idea_data)
    
    return (social_score * 0.5) + (environmental_score * 0.5)

# Sub-scoring functions
def _get_market_size_score(idea_data: pd.Series) -> float:
    """Calculate the market size score (0-100)"""
    # Get TAM (Total Addressable Market) in millions
    tam = idea_data.get('market_size_tam', idea_data.get('tam', idea_data.get('market_size', 0)))
    
    if pd.isna(tam) or tam <= 0:
        return 50  # Default score if no market size data
    
    # Logarithmic scale for market size:
    # < $10M: 0-30
    # $10M-$100M: 30-60
    # $100M-$1B: 60-80
    # $1B-$10B: 80-95
    # > $10B: 95-100
    if tam < 10:
        return 30 * (tam / 10)
    elif tam < 100:
        return 30 + (30 * (tam - 10) / 90)
    elif tam < 1000:
        return 60 + (20 * (tam - 100) / 900)
    elif tam < 10000:
        return 80 + (15 * (tam - 1000) / 9000)
    else:
        return 95 + (5 * min(1, (tam - 10000) / 10000))

def _get_recurring_revenue_score(idea_data: pd.Series) -> float:
    """Calculate the recurring revenue model score (0-100)"""
    # Check if the business model is recurring
    recurring_model = idea_data.get('has_recurring_revenue', idea_data.get('recurring_revenue', None))
    business_model = str(idea_data.get('business_model', '')).lower()
    
    # Default score if no data
    if pd.isna(recurring_model) and not business_model:
        return 50
    
    # If explicit recurring revenue flag is available
    if isinstance(recurring_model, bool):
        return 80 if recurring_model else 60
    
    # Infer from business model
    high_recurring_models = ['saas', 'subscription', 'sass', 'recurring']
    medium_recurring_models = ['marketplace', 'freemium']
    low_recurring_models = ['one-time', 'onetime', 'hardware', 'consulting']
    
    if any(model in business_model for model in high_recurring_models):
        return 90
    elif any(model in business_model for model in medium_recurring_models):
        return 70
    elif any(model in business_model for model in low_recurring_models):
        return 40
    
    return 50

def _get_scalability_score(idea_data: pd.Series) -> float:
    """Calculate the scalability score (0-100)"""
    # Infer scalability from industry, business model, and geographic expansion potential
    industry = str(idea_data.get('industry', '')).lower()
    business_model = str(idea_data.get('business_model', '')).lower()
    
    # High scalability industries
    high_scalability_industries = ['saas', 'software', 'ai', 'digital', 'online', 'mobile', 'app', 'platform']
    medium_scalability_industries = ['marketplace', 'ecommerce', 'consumer']
    low_scalability_industries = ['hardware', 'manufacturing', 'physical', 'local', 'service']
    
    # Check industry scalability
    if any(ind in industry for ind in high_scalability_industries):
        industry_score = 90
    elif any(ind in industry for ind in medium_scalability_industries):
        industry_score = 70
    elif any(ind in industry for ind in low_scalability_industries):
        industry_score = 50
    else:
        industry_score = 60
    
    # Check business model scalability
    if any(model in business_model for model in ['saas', 'software', 'platform', 'digital']):
        model_score = 90
    elif any(model in business_model for model in ['marketplace', 'freemium', 'subscription']):
        model_score = 80
    elif any(model in business_model for model in ['ecommerce', 'consumer']):
        model_score = 70
    elif any(model in business_model for model in ['hardware', 'physical', 'service']):
        model_score = 50
    else:
        model_score = 60
    
    # Combine scores, weighting industry slightly less than business model
    return (industry_score * 0.4) + (model_score * 0.6)

def _get_competition_level_score(idea_data: pd.Series) -> float:
    """Calculate the competition level score (0-100). Lower competition = higher score."""
    competition_level = idea_data.get('competition_level', None)
    
    if pd.isna(competition_level):
        return 50  # Default if no data
    
    # Normalize to 1-10 if it's already a number
    if isinstance(competition_level, (int, float)):
        if 1 <= competition_level <= 10:
            # Invert the scale since lower competition is better
            return 100 - (competition_level - 1) * 10
        else:
            # Attempt to normalize unknown scales
            return 50
    
    # If it's a string description, interpret it
    competition_str = str(competition_level).lower()
    
    if any(term in competition_str for term in ['low', 'minimal', 'none', 'limited']):
        return 90
    elif any(term in competition_str for term in ['moderate', 'medium', 'some']):
        return 70
    elif any(term in competition_str for term in ['high', 'intense', 'significant', 'strong']):
        return 40
    elif any(term in competition_str for term in ['saturated', 'crowded', 'very high']):
        return 20
    
    return 50  # Default for unclear descriptions

def _get_first_mover_advantage_score(idea_data: pd.Series) -> float:
    """Calculate the first-mover advantage score (0-100)"""
    # This is speculative without explicit first-mover data
    # Could be derived from competition level and idea novelty
    competition_score = _get_competition_level_score(idea_data)
    
    # A high competition score suggests low competition, which may indicate first-mover potential
    if competition_score >= 80:
        return 90  # High potential first-mover advantage
    elif competition_score >= 60:
        return 70  # Moderate first-mover advantage
    elif competition_score >= 40:
        return 50  # Limited first-mover advantage
    else:
        return 30  # Little first-mover advantage
        
def _get_founder_experience_score(idea_data: pd.Series) -> float:
    """Calculate the founder experience score (0-100)"""
    experience = idea_data.get('founding_team_experience', idea_data.get('founder_experience', None))
    
    if pd.isna(experience):
        return 50  # Default if no data
    
    # If it's a numeric rating (1-10)
    if isinstance(experience, (int, float)):
        if 1 <= experience <= 10:
            return experience * 10
        else:
            return 50  # Default for unexpected numeric range
    
    # If it's a string description
    experience_str = str(experience).lower()
    
    if any(term in experience_str for term in ['extensive', 'expert', 'serial', 'previous exit', 'successful']):
        return 90
    elif any(term in experience_str for term in ['experienced', 'strong', 'prior startups']):
        return 75
    elif any(term in experience_str for term in ['moderate', 'some', 'industry']):
        return 60
    elif any(term in experience_str for term in ['limited', 'first time', 'new']):
        return 40
    elif any(term in experience_str for term in ['none', 'no experience']):
        return 20
    
    return 50  # Default for unclear descriptions

def _get_product_complexity_score(idea_data: pd.Series) -> float:
    """Calculate the product complexity score (0-100). Lower complexity = higher score."""
    complexity = idea_data.get('product_complexity', None)
    
    if pd.isna(complexity):
        return 50  # Default if no data
    
    # If it's a numeric rating (1-10, where 10 is most complex)
    if isinstance(complexity, (int, float)):
        if 1 <= complexity <= 10:
            # Invert the scale since lower complexity is better
            return 100 - (complexity - 1) * 10
        else:
            return 50  # Default for unexpected numeric range
    
    # If it's a string description
    complexity_str = str(complexity).lower()
    
    if any(term in complexity_str for term in ['simple', 'straightforward', 'easy', 'low']):
        return 80
    elif any(term in complexity_str for term in ['moderate', 'medium']):
        return 60
    elif any(term in complexity_str for term in ['complex', 'difficult', 'high', 'challenging']):
        return 40
    elif any(term in complexity_str for term in ['very complex', 'highly complex', 'extremely']):
        return 20
    
    return 50  # Default for unclear descriptions

def _get_unit_economics_score(idea_data: pd.Series) -> float:
    """Calculate the unit economics score (0-100)"""
    ltv = idea_data.get('estimated_ltv', None)
    cac = idea_data.get('estimated_cac', None)
    ltv_cac_ratio = idea_data.get('ltv_cac_ratio', None)
    
    # If we have both LTV and CAC
    if not pd.isna(ltv) and not pd.isna(cac) and cac > 0:
        ratio = ltv / cac
    elif not pd.isna(ltv_cac_ratio):
        ratio = ltv_cac_ratio
    else:
        return 50  # Default if no data
    
    # Score based on LTV/CAC ratio
    # < 1: 0-20 (unprofitable)
    # 1-2: 20-50 (marginal)
    # 2-3: 50-70 (good)
    # 3-5: 70-90 (excellent)
    # > 5: 90-100 (exceptional)
    if ratio < 1:
        return max(0, ratio * 20)
    elif ratio < 2:
        return 20 + ((ratio - 1) * 30)
    elif ratio < 3:
        return 50 + ((ratio - 2) * 20)
    elif ratio < 5:
        return 70 + ((ratio - 3) * 10)
    else:
        return min(100, 90 + ((ratio - 5) * 2))

def _get_regulatory_risk_score(idea_data: pd.Series) -> float:
    """Calculate the regulatory risk score (0-100). Lower risk = higher score."""
    risk = idea_data.get('regulatory_risk', None)
    industry = str(idea_data.get('industry', '')).lower()
    
    # Default based on industry if no explicit risk rating
    if pd.isna(risk):
        # High-regulation industries
        high_regulation = ['healthcare', 'healthtech', 'fintech', 'finance', 'banking', 'insurance', 
                          'pharma', 'biotech', 'energy', 'education', 'legal']
        
        # Medium-regulation industries
        medium_regulation = ['transportation', 'food', 'retail', 'consumer', 'real estate', 
                            'telecom', 'media']
        
        # Low-regulation industries
        low_regulation = ['software', 'technology', 'digital', 'entertainment', 'games', 
                         'media', 'consumer apps']
        
        if any(ind in industry for ind in high_regulation):
            return 30  # High regulatory risk
        elif any(ind in industry for ind in medium_regulation):
            return 60  # Medium regulatory risk
        elif any(ind in industry for ind in low_regulation):
            return 85  # Low regulatory risk
        else:
            return 50  # Default for unknown industries
    
    # If it's a numeric rating (1-10, where 10 is highest risk)
    if isinstance(risk, (int, float)):
        if 1 <= risk <= 10:
            # Invert the scale since lower risk is better
            return 100 - (risk - 1) * 10
        else:
            return 50  # Default for unexpected numeric range
    
    # If it's a string description
    risk_str = str(risk).lower()
    
    if any(term in risk_str for term in ['low', 'minimal', 'none', 'limited']):
        return 85
    elif any(term in risk_str for term in ['moderate', 'medium', 'some']):
        return 60
    elif any(term in risk_str for term in ['high', 'significant', 'heavy', 'strict']):
        return 30
    elif any(term in risk_str for term in ['extreme', 'very high', 'severe']):
        return 10
    
    return 50  # Default for unclear descriptions

def _get_public_sector_complexity_score(idea_data: pd.Series) -> float:
    """Calculate the public sector customer complexity score (0-100). Lower complexity = higher score."""
    public_customers = idea_data.get('has_public_customers', idea_data.get('public_customers', None))
    target_market = str(idea_data.get('target_market', '')).lower()
    
    # If we have explicit flag
    if isinstance(public_customers, bool):
        return 40 if public_customers else 80
    
    # If we can infer from target market
    public_sector_terms = ['government', 'public sector', 'federal', 'state', 'local government', 
                         'municipality', 'public agency', 'public institution']
    
    if any(term in target_market for term in public_sector_terms):
        return 40  # Public sector complexity
    
    return 70  # Default assumes limited public sector complexity

def _get_network_effects_score(idea_data: pd.Series) -> float:
    """Calculate the network effects score (0-100). Strong positive network effects = higher score."""
    network_effects = idea_data.get('has_network_effects', idea_data.get('network_effects', None))
    business_model = str(idea_data.get('business_model', '')).lower()
    
    # If we have explicit flag
    if isinstance(network_effects, bool):
        # Network effects can be good (if well executed) or challenging
        # We'll give a moderate score for now
        return 60 if network_effects else 75
    
    # Infer from business model
    strong_network_models = ['marketplace', 'platform', 'social', 'network', 'community']
    moderate_network_models = ['saas platform', 'multi-sided', 'two-sided']
    
    if any(model in business_model for model in strong_network_models):
        return 60  # Network effects present - moderate score due to chicken-egg challenge
    elif any(model in business_model for model in moderate_network_models):
        return 70  # Some network effects
    
    return 80  # Default assumes limited network effect dependency

def _get_marketplace_complexity_score(idea_data: pd.Series) -> float:
    """Calculate the marketplace complexity score (0-100). Lower complexity = higher score."""
    business_model = str(idea_data.get('business_model', '')).lower()
    
    # Check if it's a marketplace model
    marketplace_terms = ['marketplace', 'two-sided', 'multi-sided', 'platform', 'peer-to-peer']
    
    if any(term in business_model for term in marketplace_terms):
        return 50  # Marketplace models have chicken-and-egg challenges
    
    return 80  # Not a marketplace model, so no complexity from this perspective

def _get_social_impact_score(idea_data: pd.Series) -> float:
    """Calculate the social impact score (0-100)"""
    impact = idea_data.get('social_impact_score', None)
    description = str(idea_data.get('description', '')).lower() + ' ' + str(idea_data.get('problem_statement', '')).lower()
    
    # If we have explicit score
    if not pd.isna(impact) and isinstance(impact, (int, float)):
        if 1 <= impact <= 10:
            return impact * 10
        else:
            return 50  # Default for unexpected numeric range
    
    # Try to infer from description
    high_impact_terms = ['social impact', 'underserved', 'accessibility', 'education', 'healthcare', 
                       'equality', 'diversity', 'inclusion', 'community', 'welfare', 'poverty', 
                       'developing', 'sustainable']
    
    moderate_impact_terms = ['quality of life', 'well-being', 'employment', 'jobs', 'skill development']
    
    if any(term in description for term in high_impact_terms):
        return 85  # High social impact
    elif any(term in description for term in moderate_impact_terms):
        return 65  # Moderate social impact
    
    return 50  # Default assumes neutral social impact

def _get_environmental_impact_score(idea_data: pd.Series) -> float:
    """Calculate the environmental impact score (0-100)"""
    impact = idea_data.get('environmental_impact_score', None)
    description = str(idea_data.get('description', '')).lower() + ' ' + str(idea_data.get('problem_statement', '')).lower()
    
    # If we have explicit score
    if not pd.isna(impact) and isinstance(impact, (int, float)):
        if 1 <= impact <= 10:
            return impact * 10
        else:
            return 50  # Default for unexpected numeric range
    
    # Try to infer from description
    high_impact_terms = ['environmental', 'sustainability', 'carbon neutral', 'carbon negative', 'green', 
                       'renewable', 'clean energy', 'eco-friendly', 'biodegradable', 'recycling', 
                       'circular economy', 'waste reduction', 'climate']
    
    moderate_impact_terms = ['efficiency', 'optimization', 'reduction', 'paperless', 'digital transformation']
    
    if any(term in description for term in high_impact_terms):
        return 85  # High environmental impact
    elif any(term in description for term in moderate_impact_terms):
        return 65  # Moderate environmental impact
    
    return 50  # Default assumes neutral environmental impact
