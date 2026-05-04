import pandas as pd
import numpy as np

def clean_data(df):
    """
    Scientific Cleaning Pipeline:
    1. Duplicate Removal
    2. Constant Column Drop (Zero information)
    3. High-Null Column Drop (>60% missing)
    4. Smart Imputation (Median/Mode)
    """
    report = {
        "initial_rows": int(df.shape[0]),
        "initial_cols": int(df.shape[1]),
        "dropped_columns": []
    }

    # 1. Remove duplicates
    dupe_count = int(df.duplicated().sum())
    df = df.drop_duplicates()
    report["duplicates_removed"] = dupe_count

    # 2. Drop Constant Columns
    constant_cols = [col for col in df.columns if df[col].nunique() <= 1]
    if constant_cols:
        df = df.drop(columns=constant_cols)
        report["dropped_columns"].extend(constant_cols)

    # 3. Drop High-Null Columns
    high_null_cols = [col for col in df.columns if df[col].isnull().mean() > 0.6]
    if high_null_cols:
        df = df.drop(columns=high_null_cols)
        report["dropped_columns"].extend(high_null_cols)

    # 4. Smart Imputation & Type Correction
    for col in df.columns:
        # If numeric, use Median
        if pd.api.types.is_numeric_dtype(df[col]):
            if df[col].isnull().sum() > 0:
                df[col] = df[col].fillna(df[col].median())
        # If categorical/object
        else:
            # Try to fix dates
            if "date" in col.lower() or "time" in col.lower():
                converted = pd.to_datetime(df[col], errors='coerce')
                if not converted.isna().all():
                    df[col] = converted
            
            # Impute with Mode
            if df[col].isnull().sum() > 0:
                mode_val = df[col].mode()
                df[col] = df[col].fillna(mode_val[0] if not mode_val.empty else "Unknown")

    report["final_rows"] = int(df.shape[0])
    report["final_cols"] = int(df.shape[1])
    
    return df, report