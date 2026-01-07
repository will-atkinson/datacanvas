"""Column inference utilities."""
from typing import Optional, Tuple

import numpy as np
import pandas as pd


def infer_date_column(df: pd.DataFrame) -> Optional[str]:
    """Infer the most suitable date column from a DataFrame.

    Selects the datetime column with the most non-null values.

    Args:
        df: Input DataFrame

    Returns:
        Name of the inferred date column, or None if no datetime columns exist
    """
    date_cols = [c for c in df.columns if np.issubdtype(df[c].dtype, np.datetime64)]
    if not date_cols:
        return None
    date_cols = sorted(date_cols, key=lambda c: df[c].notna().sum(), reverse=True)
    return date_cols[0]


def infer_metric_column(df: pd.DataFrame) -> Optional[str]:
    """Infer the most suitable numeric metric column from a DataFrame.

    Prioritizes numeric columns with:
    - High non-null count
    - High variance (avoiding ID-like columns)
    - Names that don't suggest IDs, postcodes, or zip codes

    Args:
        df: Input DataFrame

    Returns:
        Name of the inferred metric column, or None if no numeric columns exist
    """
    num_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
    if not num_cols:
        return None

    def score(col: str) -> Tuple[int, float]:
        name = col.lower()
        penalty = 0
        if "id" in name or "postcode" in name or "zip" in name:
            penalty -= 2
        non_null = int(df[col].notna().sum())
        var = float(df[col].var(skipna=True) or 0.0)
        return (penalty + non_null, var)

    num_cols = sorted(num_cols, key=score, reverse=True)
    return num_cols[0]


def infer_category_column(df: pd.DataFrame) -> Optional[str]:
    """Infer the most suitable categorical column from a DataFrame.

    Prioritizes object columns with:
    - Around 10 unique values (goldilocks zone)
    - High non-null count
    - Not too high cardinality (avoids free-text fields)

    Args:
        df: Input DataFrame

    Returns:
        Name of the inferred category column, or None if no object columns exist
    """
    obj_cols = [c for c in df.columns if df[c].dtype == "object"]
    if not obj_cols:
        return None

    def score(col: str) -> Tuple[int, int]:
        nunique = int(df[col].nunique(dropna=True))
        non_null = int(df[col].notna().sum())
        penalty = -abs(nunique - 10)
        if nunique > max(50, len(df) * 0.3):
            penalty -= 50
        return (penalty, non_null)

    obj_cols = sorted(obj_cols, key=score, reverse=True)
    return obj_cols[0]
