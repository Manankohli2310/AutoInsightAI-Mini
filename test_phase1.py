import pandas as pd
from backend.utils.data_cleaner import clean_data
from backend.engines.core_engine import CoreAnalyzer
from backend.utils.visualizer import generate_plots

# 1. Load Data
df = pd.read_csv("data_samples/Walmart_Sales.csv") # Use any CSV you have

# 2. Test Cleaning
df_cleaned, clean_report = clean_data(df)
print("Cleaning Report:", clean_report)

# 3. Test Logic Engine
analyzer = CoreAnalyzer(df_cleaned)
print("Basic Info:", analyzer.get_basic_info())
print("Insights:", analyzer.generate_insights())

# 4. Test Visualization
plots = generate_plots(df_cleaned)
print("Plots generated:", plots.keys()) # Should show 'correlation_heatmap', etc.