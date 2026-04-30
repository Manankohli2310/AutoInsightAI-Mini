import pandas as pd

def clean_data(df):
    """Basic automated cleaning for the dataset"""
    # 1. Remove exact duplicate rows
    duplicate_count = df.duplicated().sum()
    df = df.drop_duplicates()

    # 2. Handle missing values
    # For numerical: fill with median
    # For categorical: fill with 'Unknown'
    null_report = df.isnull().sum().to_dict()
    
    for col in df.columns:
        if df[col].isnull().sum() > 0:
            if df[col].dtype in ['int64', 'float64']:
                df[col] = df[col].fillna(df[col].median())
            else:
                df[col] = df[col].fillna("Unknown")

    return df, {
        "duplicates_removed": int(duplicate_count),
        "null_values_found": null_report
    }