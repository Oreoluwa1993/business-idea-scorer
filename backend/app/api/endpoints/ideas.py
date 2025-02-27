from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, Path, status

from app.models.schemas import BusinessIdeaResponse, BusinessIdeaCreate, BusinessIdeaUpdate
from app.services.idea_service import get_ideas, get_idea_by_id, create_idea, update_idea, delete_idea

router = APIRouter()

@router.get("/", response_model=List[BusinessIdeaResponse])
async def list_business_ideas(
    file_id: Optional[str] = None,
    min_score: Optional[float] = None,
    max_score: Optional[float] = None,
    industry: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
):
    """
    List business ideas with optional filtering.
    
    - file_id: Filter by uploaded file ID
    - min_score: Filter by minimum score
    - max_score: Filter by maximum score
    - industry: Filter by industry
    - skip: Number of records to skip (for pagination)
    - limit: Maximum number of records to return
    """
    try:
        filters = {
            "file_id": file_id,
            "min_score": min_score,
            "max_score": max_score,
            "industry": industry
        }
        
        # Remove None values
        filters = {k: v for k, v in filters.items() if v is not None}
        
        ideas = get_ideas(filters, skip, limit)
        return ideas
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving business ideas: {str(e)}"
        )

@router.get("/{idea_id}", response_model=BusinessIdeaResponse)
async def get_business_idea(idea_id: str):
    """
    Get a specific business idea by ID.
    """
    idea = get_idea_by_id(idea_id)
    
    if idea is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Business idea with ID {idea_id} not found"
        )
        
    return idea

@router.post("/", response_model=BusinessIdeaResponse, status_code=status.HTTP_201_CREATED)
async def create_business_idea(idea: BusinessIdeaCreate):
    """
    Create a new business idea manually.
    """
    try:
        created_idea = create_idea(idea)
        return created_idea
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating business idea: {str(e)}"
        )

@router.put("/{idea_id}", response_model=BusinessIdeaResponse)
async def update_business_idea(idea_id: str, idea_update: BusinessIdeaUpdate):
    """
    Update an existing business idea.
    """
    try:
        updated_idea = update_idea(idea_id, idea_update)
        
        if updated_idea is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Business idea with ID {idea_id} not found"
            )
            
        return updated_idea
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating business idea: {str(e)}"
        )

@router.delete("/{idea_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_business_idea(idea_id: str):
    """
    Delete a business idea.
    """
    try:
        success = delete_idea(idea_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Business idea with ID {idea_id} not found"
            )
            
        return None
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting business idea: {str(e)}"
        )

@router.get("/export/{file_id}", response_model=List[BusinessIdeaResponse])
async def export_ideas(
    file_id: str,
    min_score: Optional[float] = None,
    include_explanations: bool = True
):
    """
    Export business ideas for a specific file, with optional filtering.
    
    - file_id: Filter by uploaded file ID
    - min_score: Filter by minimum score
    - include_explanations: Whether to include GPT-generated explanations
    """
    try:
        filters = {
            "file_id": file_id,
            "min_score": min_score
        }
        
        # Remove None values
        filters = {k: v for k, v in filters.items() if v is not None}
        
        ideas = get_ideas(filters)
        
        # Optionally remove explanations to reduce payload size
        if not include_explanations:
            for idea in ideas:
                idea.explanation = None
                
        return ideas
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error exporting business ideas: {str(e)}"
        )
