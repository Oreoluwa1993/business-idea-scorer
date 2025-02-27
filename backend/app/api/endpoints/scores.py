from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, Path, status
from pydantic import UUID4

from app.models.schemas import ScoringInput, ScoreResponse, ScoreSummary, WeightConfiguration
from app.services.scoring_service import calculate_scores, get_gpt_explanation
from app.core.config import settings

router = APIRouter()

@router.post("/calculate", response_model=List[ScoreResponse], status_code=status.HTTP_200_OK)
async def score_business_ideas(
    file_id: str,
    weights: Optional[WeightConfiguration] = None
):
    """
    Calculate scores for all business ideas in the uploaded file.
    
    Optional custom weight configuration can be provided to adjust the scoring algorithm.
    If no weights are provided, the default weights from settings will be used.
    """
    try:
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
            
        # Validate weights sum to 100
        total_weights = (
            weights.market_business_model +
            weights.competitive_landscape +
            weights.execution_team +
            weights.risk_factors +
            weights.network_platform_risks +
            weights.social_environmental_impact
        )
        
        if not (99.5 <= total_weights <= 100.5):  # Allow for small floating point differences
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Weight configuration must sum to 100. Current sum: {total_weights}"
            )
            
        # Calculate scores
        scores = calculate_scores(file_id, weights)
        
        # Generate GPT explanations for each score
        for score in scores:
            score.explanation = get_gpt_explanation(score)
            
        return scores
    
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File {file_id} not found"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating scores: {str(e)}"
        )

@router.get("/summary", response_model=ScoreSummary)
async def get_score_summary(file_id: str):
    """
    Get a summary of scores for a specific file.
    Includes average score, highest and lowest scores, and distribution statistics.
    """
    try:
        # Calculate scores with default weights
        scores = calculate_scores(file_id)
        
        # Calculate summary statistics
        if not scores:
            return ScoreSummary(
                file_id=file_id,
                average_score=0,
                highest_score=0,
                lowest_score=0,
                count=0,
                distribution={
                    "0-20": 0,
                    "21-40": 0,
                    "41-60": 0,
                    "61-80": 0,
                    "81-100": 0
                }
            )
            
        score_values = [score.total_score for score in scores]
        
        # Calculate distribution
        distribution = {
            "0-20": len([s for s in score_values if 0 <= s <= 20]),
            "21-40": len([s for s in score_values if 21 <= s <= 40]),
            "41-60": len([s for s in score_values if 41 <= s <= 60]),
            "61-80": len([s for s in score_values if 61 <= s <= 80]),
            "81-100": len([s for s in score_values if 81 <= s <= 100])
        }
        
        return ScoreSummary(
            file_id=file_id,
            average_score=sum(score_values) / len(score_values) if score_values else 0,
            highest_score=max(score_values) if score_values else 0,
            lowest_score=min(score_values) if score_values else 0,
            count=len(scores),
            distribution=distribution
        )
        
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File {file_id} not found"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating score summary: {str(e)}"
        )

@router.put("/weights", response_model=WeightConfiguration)
async def update_weights(weights: WeightConfiguration):
    """
    Update the default weight configuration for the scoring algorithm.
    """
    try:
        # Validate weights sum to 100
        total_weights = (
            weights.market_business_model +
            weights.competitive_landscape +
            weights.execution_team +
            weights.risk_factors +
            weights.network_platform_risks +
            weights.social_environmental_impact
        )
        
        if not (99.5 <= total_weights <= 100.5):  # Allow for small floating point differences
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Weight configuration must sum to 100. Current sum: {total_weights}"
            )
            
        # Would typically update database or settings here
        # For MVP, we'll just return the validated weights
        return weights
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating weights: {str(e)}"
        )
