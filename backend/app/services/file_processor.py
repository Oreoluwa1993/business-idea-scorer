import os
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Any, Optional

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
        
        # Save processed data (in a real application, this would go to a database)
        processed_path = file_path.parent / f"{file_path.stem}_processed{file_path.suffix}"
        df_processed.to_excel(processed_path, index=False)
        
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
        
        # Save processed data (in a real application, this would go to a database)
        processed_path = file_path.parent / f"{file_path.stem}_processed{file_path.suffix}"
        df_processed.to_csv(processed_path, index=False)
        
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
    df_processed.columns = [col.lower().strip().replace(' ', '_') for col in df_processed.columns]
    
    # 2. Handle missing values
    # For numerical columns, fill with median
    numerical_cols = df_processed.select_dtypes(include=['number']).columns
    for col in numerical_cols:
        df_processed[col] = df_processed[col].fillna(df_processed[col].median())
    
    # For text columns, fill with empty string
    text_cols = df_processed.select_dtypes(include=['object']).columns
    for col in text_cols:
        df_processed[col] = df_processed[col].fillna('')
    
    # 3. Standardize text fields
    for col in text_cols:
        # Convert all text to lowercase
        df_processed[col] = df_processed[col].astype(str).str.lower()
        
        # Standardize common terms
        standardize_map = {
            'b2b': 'b2b',
            'b2c': 'b2c',
            'b2b2c': 'b2b2c',
            'market place': 'marketplace',
            'market-place': 'marketplace',
            'saas': 'saas',
            'software as a service': 'saas',
            'subscription': 'subscription',
            'freemium': 'freemium',
            'ecommerce': 'ecommerce',
            'e-commerce': 'ecommerce',
            'healthcare': 'healthtech',
            'health tech': 'healthtech',
            'fintech': 'fintech',
            'financial technology': 'fintech',
            'edtech': 'edtech',
            'educational technology': 'edtech',
            'ai': 'ai_ml',
            'machine learning': 'ai_ml',
            'artificial intelligence': 'ai_ml',
            'ml': 'ai_ml'
        }
        
        for original, standardized in standardize_map.items():
            df_processed[col] = df_processed[col].str.replace(r'\b' + original + r'\b', standardized, regex=True)
    
    # 4. Convert fields to appropriate types
    # Convert market size to float if available
    market_size_columns = ['market_size', 'tam', 'sam', 'som', 'market_size_tam', 'market_size_sam', 'market_size_som']
    for col in market_size_columns:
        if col in df_processed.columns:
            df_processed[col] = _convert_market_size_to_float(df_processed[col])
    
    # Convert boolean indicators
    boolean_columns = [
        'has_network_effects', 'has_public_customers', 'has_recurring_revenue', 
        'has_ip_patents', 'network_effects', 'public_customers', 'recurring_revenue', 
        'ip_patents'
    ]
    
    for col in boolean_columns:
        if col in df_processed.columns:
            df_processed[col] = _convert_to_boolean(df_processed[col])
    
    # 5. Add derived columns that may be useful for scoring
    # Calculate LTV/CAC ratio if both values exist
    if 'estimated_ltv' in df_processed.columns and 'estimated_cac' in df_processed.columns:
        df_processed['ltv_cac_ratio'] = df_processed['estimated_ltv'] / df_processed['estimated_cac'].replace(0, np.nan)
    
    # 6. Identify and flag potential data quality issues
    # Flag rows with potential data quality issues
    df_processed['data_quality_issues'] = False
    
    # Flag missing critical fields
    critical_fields = ['name', 'description', 'problem_statement', 'solution_description']
    for field in critical_fields:
        if field in df_processed.columns:
            df_processed.loc[df_processed[field].astype(str).str.len() < 5, 'data_quality_issues'] = True
    
    return df_processed

def _convert_market_size_to_float(series: pd.Series) -> pd.Series:
    """
    Convert market size values to float. Handles different formats like:
    - $5M, $5.2M, $5MM, $5B, 5 million, 5M, 5.2B, etc.
    
    Args:
        series: Pandas Series containing market size values
        
    Returns:
        Series with standardized float values (in millions)
    """
    def convert_value(value):
        if pd.isna(value) or value == '':
            return np.nan
        
        value = str(value).lower().strip()
        
        # Remove currency symbols and spaces
        value = value.replace('$', '').replace(',', '').strip()
        
        # Convert to float with multiplier
        try:
            if 'billion' in value or 'b' in value:
                # Extract the number part
                number_part = ''.join(c for c in value if c.isdigit() or c == '.')
                return float(number_part) * 1000  # Convert billions to millions
            elif 'million' in value or 'm' in value or 'mm' in value:
                # Extract the number part
                number_part = ''.join(c for c in value if c.isdigit() or c == '.')
                return float(number_part)
            elif 'thousand' in value or 'k' in value:
                # Extract the number part
                number_part = ''.join(c for c in value if c.isdigit() or c == '.')
                return float(number_part) / 1000  # Convert thousands to millions
            else:
                # Assume raw number is in millions
                return float(value)
        except ValueError:
            return np.nan
    
    return series.apply(convert_value)

def _convert_to_boolean(series: pd.Series) -> pd.Series:
    """
    Convert various string representations to boolean values.
    
    Args:
        series: Pandas Series containing boolean-like values
        
    Returns:
        Series with standardized boolean values
    """
    true_values = ['yes', 'y', 'true', 't', '1', 'high', 'strong', 'positive']
    false_values = ['no', 'n', 'false', 'f', '0', 'low', 'weak', 'negative']
    
    def convert_value(value):
        if pd.isna(value):
            return np.nan
        
        value_str = str(value).lower().strip()
        
        if value_str in true_values:
            return True
        elif value_str in false_values:
            return False
        else:
            return np.nan
    
    return series.apply(convert_value)
