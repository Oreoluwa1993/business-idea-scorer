import os
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Any, Optional

from app.utils.helpers import ensure_directory_exists, generate_unique_id
from app.utils.data_processing import (
    normalize_column_names,
    standardize_industry_terms,
    standardize_business_model_terms,
    detect_market_size,
    convert_to_boolean,
    extract_numeric_rating
)

def process_excel_file(file_path: Path) -> Dict[str, Any]:
    """
    Process an uploaded Excel file containing business ideas.
    Handles data cleaning, standardization, and validation.
    
    Args:
        file_path: Path to the uploaded Excel file
        
    Returns:
        Dict with summary information about the processed data
    """
    try:
        # Read Excel file
        df = pd.read_excel(file_path, engine="openpyxl")
        
        # Process the dataframe
        df_processed = _process_dataframe(df)
        
        # Save processed data
        processed_path = _save_processed_file(file_path, df_processed, "xlsx")
        
        # Return summary information
        return {
            "record_count": len(df_processed),
            "columns": df_processed.columns.tolist(),
            "processed_file": str(processed_path)
        }
    
    except Exception as e:
        raise Exception(f"Error processing Excel file: {str(e)}")

def process_csv_file(file_path: Path) -> Dict[str, Any]:
    """
    Process an uploaded CSV file containing business ideas.
    Handles data cleaning, standardization, and validation.
    
    Args:
        file_path: Path to the uploaded CSV file
        
    Returns:
        Dict with summary information about the processed data
    """
    try:
        # Read CSV file
        df = pd.read_csv(file_path)
        
        # Process the dataframe
        df_processed = _process_dataframe(df)
        
        # Save processed data
        processed_path = _save_processed_file(file_path, df_processed, "csv")
        
        # Return summary information
        return {
            "record_count": len(df_processed),
            "columns": df_processed.columns.tolist(),
            "processed_file": str(processed_path)
        }
    
    except Exception as e:
        raise Exception(f"Error processing CSV file: {str(e)}")

def _process_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Common processing logic for both Excel and CSV data.
    
    Args:
        df: Original pandas DataFrame
        
    Returns:
        Processed DataFrame
    """
    # Create a copy to avoid modifying the original
    df_processed = df.copy()
    
    # 1. Standardize column names
    df_processed = normalize_column_names(df_processed)
    
    # 2. Handle missing values
    df_processed = _handle_missing_values(df_processed)
    
    # 3. Standardize text fields
    df_processed = _standardize_text_fields(df_processed)
    
    # 4. Extract and standardize specific fields
    df_processed = _extract_specific_fields(df_processed)
    
    # 5. Add derived columns
    df_processed = _add_derived_columns(df_processed)
    
    # 6. Identify data quality issues
    df_processed = _identify_data_quality_issues(df_processed)
    
    return df_processed

def _handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Handle missing values in the DataFrame.
    
    Args:
        df: Input DataFrame
        
    Returns:
        DataFrame with handled missing values
    """
    # Create a copy to avoid modifying the original
    df_processed = df.copy()
    
    # For numerical columns, fill with median
    numerical_cols = df_processed.select_dtypes(include=['number']).columns
    for col in numerical_cols:
        df_processed[col] = df_processed[col].fillna(df_processed[col].median())
    
    # For text columns, fill with empty string
    text_cols = df_processed.select_dtypes(include=['object']).columns
    for col in text_cols:
        df_processed[col] = df_processed[col].fillna('')
    
    # For boolean columns, leave as NaN (will be handled during scoring)
    bool_cols = df_processed.select_dtypes(include=['bool']).columns
    
    return df_processed

def _standardize_text_fields(df: pd.DataFrame) -> pd.DataFrame:
    """
    Standardize text fields in the DataFrame.
    
    Args:
        df: Input DataFrame
        
    Returns:
        DataFrame with standardized text fields
    """
    # Create a copy to avoid modifying the original
    df_processed = df.copy()
    
    # Get text columns
    text_cols = df_processed.select_dtypes(include=['object']).columns
    
    # Standardize industry and business model terms in all text columns
    for col in text_cols:
        # Convert all text to lowercase
        df_processed[col] = df_processed[col].astype(str).str.lower()
        
        # Apply specific standardization to relevant columns
        if 'industry' in col:
            df_processed[col] = df_processed[col].apply(standardize_industry_terms)
        
        if 'business_model' in col or 'model' in col:
            df_processed[col] = df_processed[col].apply(standardize_business_model_terms)
    
    return df_processed

def _extract_specific_fields(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extract and standardize specific fields in the DataFrame.
    
    Args:
        df: Input DataFrame
        
    Returns:
        DataFrame with extracted and standardized fields
    """
    # Create a copy to avoid modifying the original
    df_processed = df.copy()
    
    # Convert market size columns to float
    market_size_columns = [col for col in df_processed.columns if 'market' in col or 'tam' in col or 'sam' in col or 'som' in col]
    
    for col in market_size_columns:
        if df_processed[col].dtype == object:  # If it's a string column
            df_processed[col] = df_processed[col].apply(lambda x: detect_market_size(str(x)) if pd.notna(x) else np.nan)
    
    # Convert boolean indicators
    boolean_columns = [
        col for col in df_processed.columns 
        if 'has_' in col or 'is_' in col or 'network_effects' in col or 'recurring' in col
    ]
    
    for col in boolean_columns:
        df_processed[col] = df_processed[col].apply(convert_to_boolean)
    
    # Extract numeric ratings
    rating_columns = [
        col for col in df_processed.columns 
        if 'rating' in col or 'score' in col or 'level' in col or 'experience' in col or 'complexity' in col or 'risk' in col
    ]
    
    for col in rating_columns:
        if df_processed[col].dtype == object:  # If it's a string column
            df_processed[col] = df_processed[col].apply(lambda x: extract_numeric_rating(str(x)) if pd.notna(x) else np.nan)
    
    return df_processed

def _add_derived_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add derived columns to the DataFrame.
    
    Args:
        df: Input DataFrame
        
    Returns:
        DataFrame with added derived columns
    """
    # Create a copy to avoid modifying the original
    df_processed = df.copy()
    
    # Calculate LTV/CAC ratio if both values exist
    if 'estimated_ltv' in df_processed.columns and 'estimated_cac' in df_processed.columns:
        df_processed['ltv_cac_ratio'] = df_processed['estimated_ltv'] / df_processed['estimated_cac'].replace(0, np.nan)
    
    # Ensure we have a name column
    if 'name' not in df_processed.columns and 'idea_name' in df_processed.columns:
        df_processed['name'] = df_processed['idea_name']
    elif 'name' not in df_processed.columns and 'idea' in df_processed.columns:
        df_processed['name'] = df_processed['idea']
    elif 'name' not in df_processed.columns and 'title' in df_processed.columns:
        df_processed['name'] = df_processed['title']
    elif 'name' not in df_processed.columns:
        # Generate a name if none exists
        df_processed['name'] = ['Business Idea ' + str(i+1) for i in range(len(df_processed))]
    
    return df_processed

def _identify_data_quality_issues(df: pd.DataFrame) -> pd.DataFrame:
    """
    Identify and flag data quality issues in the DataFrame.
    
    Args:
        df: Input DataFrame
        
    Returns:
        DataFrame with data quality flags
    """
    # Create a copy to avoid modifying the original
    df_processed = df.copy()
    
    # Add data quality flag
    df_processed['data_quality_issues'] = False
    
    # Flag missing critical fields
    critical_fields = ['name', 'description', 'problem_statement', 'solution_description']
    for field in critical_fields:
        if field in df_processed.columns:
            df_processed.loc[df_processed[field].astype(str).str.len() < 5, 'data_quality_issues'] = True
    
    # Flag potential data inconsistencies
    if 'market_size_tam' in df_processed.columns and 'market_size_sam' in df_processed.columns:
        # SAM should be smaller than TAM
        df_processed.loc[(df_processed['market_size_sam'] > df_processed['market_size_tam']) & 
                         (pd.notna(df_processed['market_size_sam'])) & 
                         (pd.notna(df_processed['market_size_tam'])), 'data_quality_issues'] = True
    
    if 'market_size_sam' in df_processed.columns and 'market_size_som' in df_processed.columns:
        # SOM should be smaller than SAM
        df_processed.loc[(df_processed['market_size_som'] > df_processed['market_size_sam']) & 
                         (pd.notna(df_processed['market_size_som'])) & 
                         (pd.notna(df_processed['market_size_sam'])), 'data_quality_issues'] = True
    
    return df_processed

def _save_processed_file(original_path: Path, df: pd.DataFrame, format_type: str) -> Path:
    """
    Save the processed DataFrame to a file.
    
    Args:
        original_path: Original file path
        df: Processed DataFrame
        format_type: File format (xlsx or csv)
        
    Returns:
        Path to the saved file
    """
    # Create a unique filename
    processed_dir = ensure_directory_exists(original_path.parent / "processed")
    unique_id = generate_unique_id()[:8]
    processed_path = processed_dir / f"{original_path.stem}_{unique_id}_processed.{format_type}"
    
    # Save the file
    if format_type.lower() == 'xlsx':
        df.to_excel(processed_path, index=False)
    else:  # csv
        df.to_csv(processed_path, index=False)
    
    return processed_path
