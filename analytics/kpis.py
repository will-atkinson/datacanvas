"""KPI computation utilities."""
from typing import List, Optional, Tuple

import numpy as np
import pandas as pd


def compute_kpis(
    df: pd.DataFrame,
    date_col: Optional[str],
    metric_col: Optional[str],
) -> List[Tuple[str, str]]:
    """Compute key performance indicators from a DataFrame.

    Calculates:
    - Row and column counts
    - Date range (if date column available)
    - Total and average for metric column (if available)
    - Period-over-period change (if both date and metric columns available)

    Args:
        df: Input DataFrame
        date_col: Name of the date column (can be None)
        metric_col: Name of the metric column (can be None)

    Returns:
        List of (label, value) tuples representing KPIs
    """
    kpis: List[Tuple[str, str]] = []

    kpis.append(("Rows", f"{len(df):,}"))
    kpis.append(("Columns", f"{df.shape[1]:,}"))

    if date_col:
        dmin = df[date_col].min()
        dmax = df[date_col].max()
        if pd.notna(dmin) and pd.notna(dmax):
            kpis.append(("Date range", f"{dmin.date()} → {dmax.date()}"))

    if metric_col:
        total = df[metric_col].sum(skipna=True)
        avg = df[metric_col].mean(skipna=True)
        kpis.append((f"Total {metric_col}", f"{total:,.2f}" if np.isfinite(total) else "—"))
        kpis.append((f"Average {metric_col}", f"{avg:,.2f}" if np.isfinite(avg) else "—"))

        if date_col:
            tmp = df[[date_col, metric_col]].dropna()
            if len(tmp) >= 10:
                tmp = tmp.sort_values(date_col)
                span_days = (tmp[date_col].max() - tmp[date_col].min()).days
                freq = "MS" if span_days >= 60 else "W-MON"
                series = tmp.set_index(date_col)[metric_col].resample(freq).sum()
                if len(series) >= 2:
                    last = series.iloc[-1]
                    prev = series.iloc[-2]
                    if prev != 0:
                        pct = (last - prev) / abs(prev) * 100.0
                        kpis.append(("Change vs prev period", f"{pct:+.1f}%"))
                    else:
                        kpis.append(("Change vs prev period", "—"))

    return kpis
