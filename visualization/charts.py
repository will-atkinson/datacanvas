"""Chart generation utilities."""
from typing import Optional

import matplotlib.pyplot as plt
import pandas as pd


def build_trend_chart(df: pd.DataFrame, date_col: str, metric_col: str) -> plt.Figure:
    """Build a time series trend chart.

    Shows the metric aggregated over time (weekly or monthly depending on span).

    Args:
        df: Input DataFrame
        date_col: Name of the date column
        metric_col: Name of the metric column

    Returns:
        Matplotlib Figure object
    """
    tmp = df[[date_col, metric_col]].dropna().sort_values(date_col)
    span_days = (tmp[date_col].max() - tmp[date_col].min()).days
    freq = "MS" if span_days >= 60 else "W-MON"
    series = tmp.set_index(date_col)[metric_col].resample(freq).sum()

    # Enhanced styling
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(series.index, series.values, linewidth=2.5, color='#3b82f6', marker='o',
            markersize=6, markerfacecolor='#2563eb', markeredgecolor='white', markeredgewidth=1.5)

    # Fill area under curve
    ax.fill_between(series.index, series.values, alpha=0.15, color='#3b82f6')

    # Styling
    ax.set_title(f"{metric_col} over time", fontsize=14, fontweight='bold', color='#1e40af', pad=20)
    ax.set_xlabel("Date", fontsize=11, fontweight='500', color='#64748b')
    ax.set_ylabel(metric_col, fontsize=11, fontweight='500', color='#64748b')
    ax.tick_params(axis='x', rotation=30, labelsize=9, colors='#475569')
    ax.tick_params(axis='y', labelsize=9, colors='#475569')

    # Grid
    ax.grid(True, alpha=0.2, linestyle='--', linewidth=0.5)
    ax.set_axisbelow(True)

    # Clean up spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#e2e8f0')
    ax.spines['bottom'].set_color('#e2e8f0')

    plt.tight_layout()
    return fig


def build_category_chart(
    df: pd.DataFrame,
    category_col: str,
    metric_col: Optional[str],
    top_n: int,
) -> plt.Figure:
    """Build a horizontal bar chart for top categories.

    If a metric column is provided, aggregates by sum.
    Otherwise, shows counts.

    Args:
        df: Input DataFrame
        category_col: Name of the category column
        metric_col: Name of the metric column (can be None)
        top_n: Number of top categories to display

    Returns:
        Matplotlib Figure object
    """
    if metric_col and pd.api.types.is_numeric_dtype(df[metric_col]):
        agg = (
            df[[category_col, metric_col]]
            .dropna()
            .groupby(category_col)[metric_col]
            .sum()
            .sort_values(ascending=False)
            .head(top_n)
        )
        title = f"Top {top_n} {category_col} by {metric_col}"
        x_label = metric_col
    else:
        agg = (
            df[category_col]
            .dropna()
            .value_counts()
            .head(top_n)
            .sort_values(ascending=True)
        )
        title = f"Top {top_n} {category_col} by count"
        x_label = "Count"

    # Enhanced styling
    fig, ax = plt.subplots(figsize=(10, 6))

    # Create gradient colors from light to dark blue
    colors = plt.cm.Blues(range(50, 255, 205 // len(agg)))[::-1]

    bars = ax.barh(agg.index.astype(str), agg.values, color=colors, edgecolor='white', linewidth=1.5)

    # Add value labels on bars
    for i, (bar, value) in enumerate(zip(bars, agg.values)):
        width = bar.get_width()
        ax.text(width, bar.get_y() + bar.get_height()/2, f' {value:,.0f}',
                ha='left', va='center', fontsize=9, fontweight='600', color='#475569')

    # Styling
    ax.set_title(title, fontsize=14, fontweight='bold', color='#1e40af', pad=20)
    ax.set_xlabel(x_label, fontsize=11, fontweight='500', color='#64748b')
    ax.set_ylabel(category_col, fontsize=11, fontweight='500', color='#64748b')
    ax.tick_params(axis='both', labelsize=9, colors='#475569')

    # Grid
    ax.grid(True, alpha=0.2, linestyle='--', linewidth=0.5, axis='x')
    ax.set_axisbelow(True)

    # Clean up spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#e2e8f0')
    ax.spines['bottom'].set_color('#e2e8f0')

    plt.tight_layout()
    return fig
