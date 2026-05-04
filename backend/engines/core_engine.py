import pandas as pd
import numpy as np

class CoreAnalyzer:
    def __init__(self, df):
        self.df = df
        self.schema = self._identify_schema()
        self.stats_snapshot = self._generate_snapshot()
        self.ranked_numeric = self._rank_numeric_features()

    def _identify_schema(self):
        """Semantic detection of IDs vs actual metrics."""
        schema = {"id": [], "numeric": [], "categorical": [], "datetime": []}
        for col in self.df.columns:
            # Datetime check
            if pd.api.types.is_datetime64_any_dtype(self.df[col]) or "date" in col.lower():
                schema["datetime"].append(col)
                continue
            
            # ID check (High uniqueness ratio)
            unique_ratio = self.df[col].nunique() / len(self.df)
            if unique_ratio > 0.85 and not pd.api.types.is_float_dtype(self.df[col]):
                schema["id"].append(col)
                continue

            # Numeric vs Categorical
            if pd.api.types.is_numeric_dtype(self.df[col]):
                schema["numeric"].append(col)
            else:
                schema["categorical"].append(col)
        return schema

    def _generate_snapshot(self):
        """JSON-Safe statistical fingerprint."""
        snapshot = {}
        for col in self.schema["numeric"]:
            # CRITICAL FIX: Cast every value to float() to avoid NumPy JSON errors
            snapshot[col] = {
                "mean": float(round(self.df[col].mean(), 2)),
                "median": float(round(self.df[col].median(), 2)),
                "std": float(round(self.df[col].std(), 2)),
                "min": float(round(self.df[col].min(), 2)),
                "max": float(round(self.df[col].max(), 2)),
                "skew": float(round(self.df[col].skew(), 2))
            }
        return snapshot

    def _rank_numeric_features(self):
        """Ranks features by variation and skewness."""
        scores = {}
        for col in self.schema["numeric"]:
            mean_val = self.df[col].mean()
            cv = abs(self.df[col].std() / mean_val) if mean_val != 0 else 0
            skew = abs(self.df[col].skew())
            scores[col] = float(cv + skew)
        return sorted(scores, key=scores.get, reverse=True)

    def get_basic_info(self):
        return {
            "total_rows": int(self.df.shape[0]),
            "total_columns": int(self.df.shape[1]),
            "column_list": self.df.columns.tolist(), # Required by AI Engine
            "schema": self.schema
        }

    def generate_insights(self):
        self.insights = []
        # Insight 1: Scale
        self.insights.append(f"Analysis focused on **{len(self.schema['numeric'])}** metrics after filtering ID columns.")
        
        # Insight 2: High Volatility (Ranked)
        for col in self.ranked_numeric[:2]:
            self.insights.append(f"Detected significant fluctuations in **{col}**, indicating diverse data behavior.")

        # Insight 3: Outliers
        for col in self.ranked_numeric[:2]:
            q1, q3 = self.df[col].quantile(0.25), self.df[col].quantile(0.75)
            iqr = q3 - q1
            outliers = len(self.df[(self.df[col] < q1 - 1.5*iqr) | (self.df[col] > q3 + 1.5*iqr)])
            if outliers > 0:
                self.insights.append(f"Found **{outliers} outliers** in {col} that deviate from the statistical norm.")

        # Insight 4: Strongest Correlation
        if len(self.schema["numeric"]) >= 2:
            corr = self.df[self.schema["numeric"]].corr().stack().reset_index()
            corr = corr[corr['level_0'] != corr['level_1']]
            top = corr.sort_values(0, ascending=False).head(1)
            if not top.empty:
                self.insights.append(f"Strongest pattern: **{top.iloc[0]['level_0']}** and **{top.iloc[0]['level_1']}** move together.")

        return self.insights