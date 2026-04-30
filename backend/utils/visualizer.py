import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64

def generate_plots(df):
    plot_data = {}
    plt.style.use('dark_background')
    plt.rcParams.update({
        'figure.facecolor': '#111111', 'axes.facecolor': '#111111',
        'axes.edgecolor': '#222222', 'grid.color': '#222222',
        'axes.labelcolor': '#ff6600', 'xtick.color': '#888888', 'ytick.color': '#888888'
    })

    num_df = df.select_dtypes(include=['number'])
    cat_cols = df.select_dtypes(include=['object']).columns.tolist()

    # 1. RELATIONSHIP MAP (If enough numeric columns)
    if len(num_df.columns) >= 2:
        try:
            plt.figure(figsize=(10, 8))
            sns.heatmap(num_df.corr(), annot=True, cmap='YlOrBr', fmt=".2f", linewidths=1, linecolor='#111111')
            plt.title("Relationship Map", color='#ffc400', fontsize=16, pad=20)
            
            buf = io.BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight', facecolor='#111111')
            buf.seek(0)
            plot_data['relationship_map'] = {
                "image": base64.b64encode(buf.read()).decode('utf-8'),
                "explanation": "Brighter yellow cells show strong connections between numeric variables."
            }
            plt.close()
        except: pass

    # 2. DISTRIBUTION PLOT (If at least one numeric column)
    if not num_df.empty:
        try:
            target = num_df.columns[-1]
            plt.figure(figsize=(10, 6))
            sns.histplot(df[target], kde=True, color='#ff6600', edgecolor='#ffc400')
            plt.title(f"Data Distribution: {target}", color='#ffc400', fontsize=16)
            
            buf = io.BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight', facecolor='#111111')
            buf.seek(0)
            plot_data['data_distribution'] = {
                "image": base64.b64encode(buf.read()).decode('utf-8'),
                "explanation": f"Shows the frequency spread of {target}."
            }
            plt.close()
        except: pass

    # 3. CATEGORY ANALYSIS (If text data exists)
    if cat_cols:
        try:
            target = cat_cols[0]
            plt.figure(figsize=(10, 6))
            df[target].value_counts().head(10).plot(kind='barh', color='#ff6600', edgecolor='#ffc400')
            plt.title(f"Top Categories: {target}", color='#ffc400', fontsize=16)
            
            buf = io.BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight', facecolor='#111111')
            buf.seek(0)
            plot_data['category_analysis'] = {
                "image": base64.b64encode(buf.read()).decode('utf-8'),
                "explanation": "Frequency analysis for the most common labels in your dataset."
            }
            plt.close()
        except: pass

    return plot_data