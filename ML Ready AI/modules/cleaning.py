"""
modules/cleaning.py — MODULE 6, 7, 8
Handles data cleaning tasks:
- Missing Value Imputation (Module 6)
- Outlier Detection & Handling (Module 7)
- Duplicate Removal & Consistency (Module 8)
"""

import pandas as pd
import numpy as np

def handle_missing_values(df: pd.DataFrame, strategy: str = 'auto') -> pd.DataFrame:
    """
    Imputes missing values in the dataframe.
    
    Strategies:
    - 'auto': 
        - Numeric cols: Mean
        - Categorical cols: Mode
    - 'median':
        - Numeric cols: Median
        - Categorical cols: Mode
    """
    df_cleaned = df.copy()
    
    # Identify numeric and categorical columns
    numeric_cols = df_cleaned.select_dtypes(include=[np.number]).columns
    categorical_cols = df_cleaned.select_dtypes(exclude=[np.number]).columns
    
    for col in numeric_cols:
        if df_cleaned[col].isnull().any():
            if strategy == 'median':
                fill_value = df_cleaned[col].median()
            else:
                fill_value = df_cleaned[col].mean()
            df_cleaned[col] = df_cleaned[col].fillna(fill_value)
            
    for col in categorical_cols:
        if df_cleaned[col].isnull().any():
            # Mode returns a Series, take the first element if not empty
            mode_series = df_cleaned[col].mode()
            if not mode_series.empty:
                df_cleaned[col] = df_cleaned[col].fillna(mode_series[0])
            else:
                # If no mode found, fill with 'Missing'
                df_cleaned[col] = df_cleaned[col].fillna('Unknown')
                
    return df_cleaned

def get_missing_stats(df: pd.DataFrame) -> dict:
    """Returns total missing values per column."""
    missing = df.isnull().sum()
    return missing[missing > 0].to_dict()


def detect_outliers(df: pd.DataFrame) -> dict:
    """
    Detects outliers using the IQR (Interquartile Range) method.
    Returns a dict with column names and the number of outliers found.
    """
    outlier_stats = {}
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    
    for col in numeric_cols:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]
        if not outliers.empty:
            outlier_stats[col] = len(outliers)
            
    return outlier_stats


def handle_outliers(df: pd.DataFrame, strategy: str = 'remove') -> pd.DataFrame:
    """
    Handles outliers using the specified strategy.
    
    Strategies:
    - 'remove': Drops rows containing outliers.
    - 'cap': Caps outliers to the IQR bounds (Capping/Winsorization).
    """
    df_cleaned = df.copy()
    numeric_cols = df_cleaned.select_dtypes(include=[np.number]).columns
    
    for col in numeric_cols:
        Q1 = df_cleaned[col].quantile(0.25)
        Q3 = df_cleaned[col].quantile(0.75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        if strategy == 'remove':
            df_cleaned = df_cleaned[(df_cleaned[col] >= lower_bound) & (df_cleaned[col] <= upper_bound)]
        elif strategy == 'cap':
            df_cleaned[col] = np.where(df_cleaned[col] < lower_bound, lower_bound, df_cleaned[col])
            df_cleaned[col] = np.where(df_cleaned[col] > upper_bound, upper_bound, df_cleaned[col])
            
    return df_cleaned


def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """Removes duplicate rows from the dataframe."""
    return df.drop_duplicates()


def fix_inconsistencies(df: pd.DataFrame) -> pd.DataFrame:
    """
    Fixes basic inconsistencies:
    - Strips whitespace from strings.
    - Converts object columns to lowercase (optional, but good for consistency).
    """
    df_cleaned = df.copy()
    for col in df_cleaned.select_dtypes(include=['object']).columns:
        df_cleaned[col] = df_cleaned[col].str.strip()
    return df_cleaned
