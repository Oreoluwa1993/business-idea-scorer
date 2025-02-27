import re
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Union, Tuple

def normalize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize column names in a DataFrame.
    
    Args:
        df: Input DataFrame
        
    Returns:
        DataFrame with normalized column names
    """
    # Create a copy to avoid modifying the original
    df_copy = df.copy()
    
    # Normalize column names
    df_copy.columns = [
        re.sub(r'[^a-zA-Z0-9_]', '', col.lower().strip().replace(' ', '_'))
        for col in df_copy.columns
    ]
    
    return df_copy

def standardize_industry_terms(text: str) -> str:
    """
    Standardize industry terms in text.
    
    Args:
        text: Text containing industry terms
        
    Returns:
        Text with standardized industry terms
    """
    # Dictionary of term mappings
    industry_mappings = {
        'fintech': 'fintech',
        'financial tech': 'fintech',
        'financial technology': 'fintech',
        'financial services': 'fintech',
        'finance': 'fintech',
        
        'healthtech': 'healthtech',
        'health tech': 'healthtech',
        'healthcare': 'healthtech',
        'health care': 'healthtech',
        'medical': 'healthtech',
        
        'edtech': 'edtech',
        'education tech': 'edtech',
        'educational technology': 'edtech',
        'education technology': 'edtech',
        
        'e-commerce': 'ecommerce',
        'ecommerce': 'ecommerce',
        'e commerce': 'ecommerce',
        'retail': 'ecommerce',
        'online retail': 'ecommerce',
        
        'saas': 'enterprise_saas',
        'enterprise saas': 'enterprise_saas',
        'enterprise software': 'enterprise_saas',
        'b2b saas': 'enterprise_saas',
        'b2b software': 'enterprise_saas',
        
        'consumer app': 'consumer_apps',
        'consumer apps': 'consumer_apps',
        'mobile app': 'consumer_apps',
        'mobile apps': 'consumer_apps',
        'b2c app': 'consumer_apps',
        
        'ai': 'ai_ml',
        'ml': 'ai_ml',
        'artificial intelligence': 'ai_ml',
        'machine learning': 'ai_ml',
        'deep learning': 'ai_ml',
        
        'biotech': 'biotech',
        'biotechnology': 'biotech',
        'bio tech': 'biotech',
        
        'cleantech': 'cleantech',
        'clean technology': 'cleantech',
        'green tech': 'cleantech',
        'renewable': 'cleantech',
        'sustainability': 'cleantech',
        
        'iot': 'iot',
        'internet of things': 'iot',
        'connected devices': 'iot',
        
        'blockchain': 'blockchain',
        'crypto': 'blockchain',
        'cryptocurrency': 'blockchain',
        'web3': 'blockchain',
    }
    
    # Convert text to lowercase for consistent matching
    text_lower = text.lower()
    
    # Replace terms
    for original, replacement in industry_mappings.items():
        # Use word boundaries to avoid partial matches
        pattern = r'\\b' + re.escape(original) + r'\\b'
        text_lower = re.sub(pattern, replacement, text_lower)
    
    return text_lower

def standardize_business_model_terms(text: str) -> str:
    """
    Standardize business model terms in text.
    
    Args:
        text: Text containing business model terms
        
    Returns:
        Text with standardized business model terms
    """
    # Dictionary of term mappings
    model_mappings = {
        'saas': 'saas',
        'software as a service': 'saas',
        'software-as-a-service': 'saas',
        
        'marketplace': 'marketplace',
        'market place': 'marketplace',
        'two sided marketplace': 'marketplace',
        'two-sided marketplace': 'marketplace',
        
        'consumer app': 'consumer_app',
        'app': 'consumer_app',
        'mobile app': 'consumer_app',
        
        'ecommerce': 'ecommerce',
        'e-commerce': 'ecommerce',
        'e commerce': 'ecommerce',
        'online store': 'ecommerce',
        
        'subscription': 'subscription',
        'subscription model': 'subscription',
        'recurring revenue': 'subscription',
        
        'freemium': 'freemium',
        'free to paid': 'freemium',
        'free tier': 'freemium',
        
        'hardware': 'hardware',
        'device': 'hardware',
        'physical product': 'hardware',
        
        'advertising': 'advertising',
        'ad-supported': 'advertising',
        'ad supported': 'advertising',
        'ads': 'advertising',
        
        'data monetization': 'data_monetization',
        'data-monetization': 'data_monetization',
        'data licensing': 'data_monetization',
        
        'licensing': 'licensing',
        'license': 'licensing',
        'ip licensing': 'licensing',
    }
    
    # Convert text to lowercase for consistent matching
    text_lower = text.lower()
    
    # Replace terms
    for original, replacement in model_mappings.items():
        # Use word boundaries to avoid partial matches
        pattern = r'\\b' + re.escape(original) + r'\\b'
        text_lower = re.sub(pattern, replacement, text_lower)
    
    return text_lower

def detect_market_size(text: str) -> Optional[float]:
    """
    Detect market size in millions from text.
    
    Args:
        text: Text containing market size information
        
    Returns:
        Market size in millions, or None if not found
    """
    # Patterns to match market size
    # Example patterns: $5M, $5.2B, 5 million, 5.2 billion, etc.
    billion_pattern = r'\\$?(\d+(?:\.\d+)?)\s*(?:B|billion|B\s*$)'
    million_pattern = r'\\$?(\d+(?:\.\d+)?)\s*(?:M|million|M\s*$)'
    thousand_pattern = r'\\$?(\d+(?:\.\d+)?)\s*(?:K|thousand|K\s*$)'
    
    # Check for billions
    billion_match = re.search(billion_pattern, text, re.IGNORECASE)
    if billion_match:
        return float(billion_match.group(1)) * 1000  # Convert billions to millions
    
    # Check for millions
    million_match = re.search(million_pattern, text, re.IGNORECASE)
    if million_match:
        return float(million_match.group(1))
    
    # Check for thousands
    thousand_match = re.search(thousand_pattern, text, re.IGNORECASE)
    if thousand_match:
        return float(thousand_match.group(1)) / 1000  # Convert thousands to millions
    
    return None

def convert_to_boolean(value: Any) -> Optional[bool]:
    """
    Convert various input formats to boolean.
    
    Args:
        value: Input value to convert
        
    Returns:
        Boolean value, or None if conversion not possible
    """
    if pd.isna(value):
        return None
    
    # If already boolean, return as is
    if isinstance(value, bool):
        return value
    
    # Convert to string for consistent processing
    str_value = str(value).lower().strip()
    
    # True values
    if str_value in ['yes', 'y', 'true', 't', '1', 'high', 'strong']:
        return True
    
    # False values
    if str_value in ['no', 'n', 'false', 'f', '0', 'low', 'weak']:
        return False
    
    # Cannot determine
    return None

def extract_numeric_rating(text: str, default: Optional[float] = None) -> Optional[float]:
    """
    Extract numeric rating from text.
    
    Args:
        text: Text containing rating information
        default: Default value if no rating found
        
    Returns:
        Numeric rating, or default if not found
    """
    # Pattern to match numeric ratings
    # Example patterns: 8/10, 8 out of 10, rating: 8, etc.
    rating_pattern = r'(\d+(?:\.\d+)?)\s*(?:\/|\s*out\s*of\s*)\s*10'
    simple_pattern = r'(\d+(?:\.\d+)?)'
    
    # Check for explicit ratings
    rating_match = re.search(rating_pattern, text, re.IGNORECASE)
    if rating_match:
        return float(rating_match.group(1))
    
    # If it's just a number, check if it's in the range 1-10
    simple_match = re.search(simple_pattern, text)
    if simple_match:
        value = float(simple_match.group(1))
        if 1 <= value <= 10:
            return value
    
    return default
