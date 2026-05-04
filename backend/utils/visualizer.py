import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64

def generate_plots(df, schema, ranked_numeric):
    """
    Intelligent Visualizer:
    - Generates plots based on Ranked Mathematical Significance.
    - Matches Black/Neon Orange/Yellow theme.
    - Pairs specific charts to discovered insights.
    """
    plot_data = {}
    
    # Theme Configuration
    plt.style.use('dark_background')
    plt.rcParams.update({
        'figure.facecolor': '#111111', 
        'axes.facecolor': '#111111',
        'axes.edgecolor': '#222222', 
        'grid.color': '#222222',
        'axes.labelcolor': '#ff6600', 
        'xtick.color': '#888888', 
        'ytick.color': '#888888',
        'font.family': 'sans-serif'
    })

    # 1. OUTLIER ANALYSIS (Box Plot)
    # We pick the MOST volatile numeric column based on our ranking
    if ranked_numeric:
        try:
            target = ranked_numeric[0]
            plt.figure(figsize=(10, 5))
            sns.boxplot(x=df[target], color='#ff6600', fliersize=7, 
                        boxprops=dict(edgecolor='#ffc400', linewidth=2),
                        whiskerprops=dict(color='#ffc400'),
                        capprops=dict(color='#ffc400'))
            
            plt.title(f"Outlier & Spread Analysis: {target}", color='#ffc400', fontsize=14, pad=15)
            plot_data['outlier_boxplot'] = _save_plot_to_base64(plt, 
                f"This Box-plot visualizes the statistical 'reach' of {target}. The dots outside the whiskers represent unusual anomalies (outliers).")
        except: pass

    # 2. KEY RELATIONSHIPS (Heatmap)
    # Exclude IDs and non-numeric columns automatically
    useful_nums = schema["numeric"]
    if len(useful_nums) >= 2:
        try:
            plt.figure(figsize=(10, 8))
            # Use YlOrBr for Neon Orange/Yellow vibe
            sns.heatmap(df[useful_nums].corr(), annot=True, cmap='YlOrBr', fmt=".2f", 
                        linewidths=1, linecolor='#111111')
            plt.title("Variable Dependency Map", color='#ffc400', fontsize=14, pad=20)
            plot_data['correlation_heatmap'] = _save_plot_to_base64(plt, 
                "This map identifies how different metrics influence each other. Brighter yellow indicates a high mathematical dependency.")
        except: pass

    # 3. RELATIONSHIP PROOF (Scatter Plot)
    # If we have a top ranked pair, show their specific relationship
    if len(ranked_numeric) >= 2:
        try:
            col1, col2 = ranked_numeric[0], ranked_numeric[1]
            plt.figure(figsize=(10, 6))
            sns.regplot(data=df, x=col1, y=col2, 
                        scatter_kws={'color': '#ff6600', 'alpha': 0.5},
                        line_kws={'color': '#ffc400', 'linewidth': 3})
            plt.title(f"Relationship Proof: {col1} vs {col2}", color='#ffc400', fontsize=14)
            plot_data['relationship_proof'] = _save_plot_to_base64(plt, 
                f"Visual proof of how {col1} impacts {col2}. The yellow line represents the overall mathematical trend.")
        except: pass

    # 4. CATEGORICAL DOMINANCE (Bar Chart)
    if schema["categorical"]:
        try:
            # Pick a category with reasonable diversity
            target_cat = schema["categorical"][0]
            for cat in schema["categorical"]:
                if 1 < df[cat].nunique() < 15:
                    target_cat = cat
                    break
            
            plt.figure(figsize=(10, 6))
            df[target_cat].value_counts().head(10).plot(kind='bar', color='#ff6600', edgecolor='#ffc400', linewidth=1)
            plt.title(f"Categorical Focus: {target_cat}", color='#ffc400', fontsize=14)
            plt.xticks(rotation=45)
            plot_data['category_focus'] = _save_plot_to_base64(plt, 
                f"Breakdown of the top 10 most frequent labels within the '{target_cat}' segment.")
        except: pass

    return plot_data

def _save_plot_to_base64(plt, explanation):
    """Helper to convert plot to base64 and clear memory"""
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', facecolor='#111111')
    plt.close()
    return {
        "image": base64.b64encode(buf.getvalue()).decode('utf-8'),
        "explanation": explanation
    }