"""
modules/eda.py — MODULE 5
Generates data visualizations using Matplotlib and Seaborn.
Plots are converted to Base64 strings to be embedded directly in HTML.
"""

import matplotlib
matplotlib.use('Agg')  # Non-interactive backend (essential for Flask)
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
import pandas as pd


def get_base64_plot():
    """Converts the current matplotlib figure to a base64 string."""
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close()
    buf.seek(0)
    return base64.b64encode(buf.getvalue()).decode('utf-8')


def generate_visualizations(df: pd.DataFrame) -> dict:
    """
    Generates a set of plots for the dataset:
      1. Histograms for all numeric columns.
      2. Bar charts for top categorical columns.
      3. Correlation heatmap for numeric columns.

    Returns a dictionary of {plot_name: base64_string}.
    """
    plots = {}

    # Set dark theme for plots to match UI
    plt.style.use('dark_background')
    sns.set_palette("husl")

    # 1. ── Histograms (Numeric Distributions) ──────────
    numeric_cols = df.select_dtypes(include=['number']).columns
    if not numeric_cols.empty:
        # We'll plot up to top 6 numeric columns to keep it clean
        cols_to_plot = numeric_cols[:6]
        n = len(cols_to_plot)
        rows = (n + 1) // 2
        
        plt.figure(figsize=(12, 4 * rows))
        for i, col in enumerate(cols_to_plot):
            plt.subplot(rows, 2, i + 1)
            sns.histplot(df[col].dropna(), kde=True, color='#6c63ff')
            plt.title(f'Distribution of {col}', color='#00d2ff', fontweight='bold')
            plt.grid(alpha=0.2)
        
        plt.tight_layout()
        plots['histograms'] = get_base64_plot()

    # 2. ── Bar Charts (Categorical Counts) ──────────────
    cat_cols = df.select_dtypes(include=['object', 'category']).columns
    if not cat_cols.empty:
        # Plot up to top 4 categorical columns
        cols_to_plot = cat_cols[:4]
        n = len(cols_to_plot)
        rows = (n + 1) // 2

        plt.figure(figsize=(12, 4 * rows))
        for i, col in enumerate(cols_to_plot):
            plt.subplot(rows, 2, i + 1)
            # Show top 10 categories only
            counts = df[col].value_counts().head(10)
            sns.barplot(x=counts.index, y=counts.values, palette="mako")
            plt.title(f'Counts of {col} (Top 10)', color='#00d2ff', fontweight='bold')
            plt.xticks(rotation=45)
            plt.grid(alpha=0.2, axis='y')
        
        plt.tight_layout()
        plots['bar_charts'] = get_base64_plot()

    # 3. ── Correlation Heatmap ──────────────────────────
    if len(numeric_cols) > 1:
        plt.figure(figsize=(10, 8))
        corr = df[numeric_cols].corr()
        sns.heatmap(corr, annot=True, cmap='coolwarm', fmt=".2f", linewidths=0.5)
        plt.title('Feature Correlation Heatmap', color='#00d2ff', fontweight='bold', fontsize=16)
        
        plt.tight_layout()
        plots['heatmap'] = get_base64_plot()

    return plots
