import pandas as pd 
from sklearn.preprocessing import LabelEncoder, StandardScaler 
 
def apply_label_encoding(df: pd.DataFrame, columns: list) -> pd.DataFrame:
    df_transformed = df.copy() 
    le = LabelEncoder() 
     
    for col in columns: 
        if col in df_transformed.columns: 
            # Drop NaN just in case, though they should be handled in Module 6 
            df_transformed[col] = le.fit_transform(df_transformed[col].astype(str)) 
             
    return df_transformed 
 
def apply_standard_scaling(df: pd.DataFrame, columns: list) -> pd.DataFrame: 
    df_transformed = df.copy() 
    scaler = StandardScaler() 
     
    if not columns: 
        return df_transformed 
         
    # Only scale columns that actually exist and are numeric 
    valid_cols = [c for c in columns if c in df_transformed.columns] 
     
    if valid_cols: 
        df_transformed[valid_cols] = scaler.fit_transform(df_transformed[valid_cols]) 
         
    return df_transformed 
 
def get_feature_info(df: pd.DataFrame) -> dict:
    return { 
        'categorical': list(df.select_dtypes(include=['object', 'category']).columns), 
        'numeric': list(df.select_dtypes(include=['number']).columns) 
    }  