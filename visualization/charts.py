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

    fig = plt.figure()
    plt.plot(series.index, series.values)
    plt.title(f"{metric_col} over time")
    plt.xlabel("Date")
    plt.ylabel(metric_col)
    plt.xticks(rotation=30, ha="right")
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

    fig = plt.figure()
    plt.barh(agg.index.astype(str), agg.values)
    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel(category_col)
    plt.tight_layout()
    return fig
