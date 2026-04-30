import pandas as pd
import numpy as np

class CoreAnalyzer:
    def __init__(self, df):
        self.df = df
        self.insights = []

    def get_basic_info(self):
        return {
            "total_rows": int(self.df.shape[0]),
            "total_columns": int(self.df.shape[1]),
            "column_list": self.df.columns.tolist(),
            "numerical_columns": self.df.select_dtypes(include=[np.number]).columns.tolist(),
            "categorical_columns": self.df.select_dtypes(include=['object']).columns.tolist()
        }

    def generate_insights(self):
        self.insights = []
        df = self.df
        num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        cat_cols = df.select_dtypes(include=['object']).columns.tolist()

        # 1. Dataset Scale
        self.insights.append(f"Analysis complete for **{df.shape[0]}** records across **{df.shape[1]}** variables.")

        # 2. Automated Date Detection
        date_col = next((col for col in df.columns if 'date' in col.lower() or 'year' in col.lower()), None)
        if date_col:
            try:
                temp_date = pd.to_datetime(df[date_col], errors='coerce')
                self.insights.append(f"Data timeline spans from **{temp_date.min().year}** to **{temp_date.max().year}**.")
            except: pass

        # 3. Variability & Outliers (Numeric)
        for col in num_cols[:3]: # Limit to top 3 numeric columns
            cv = df[col].std() / df[col].mean() if df[col].mean() != 0 else 0
            if cv > 0.5:
                self.insights.append(f"Column **{col}** shows high variability (CV: {round(cv,2)}), suggesting diverse data points.")
            
            # Outlier detection
            q1, q3 = df[col].quantile(0.25), df[col].quantile(0.75)
            outliers = len(df[(df[col] < q1 - 1.5*(q3-q1)) | (df[col] > q3 + 1.5*(q3-q1))])
            if outliers > 0:
                self.insights.append(f"Detected **{outliers}** unusual outliers in **{col}** that deviate from the normal average.")

        # 4. Categorical Dominance
        for col in cat_cols[:2]:
            top_val = df[col].mode()[0]
            perc = (df[col].value_counts().max() / len(df)) * 100
            self.insights.append(f"In **{col}**, the category '**{top_val}**' is most frequent ({round(perc,1)}% of data).")

        # 5. Correlations
        if len(num_cols) >= 2:
            corr = df[num_cols].corr()
            for i in range(len(num_cols)):
                for j in range(i+1, len(num_cols)):
                    val = corr.iloc[i, j]
                    if abs(val) > 0.4:
                        rel = "positive" if val > 0 else "negative"
                        self.insights.append(f"Found a **{rel} relationship** ({round(val,2)}) between **{num_cols[i]}** and **{num_cols[j]}**.")

        return self.insights