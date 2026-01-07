"""CSV reading and data cleaning utilities."""
import pandas as pd


def read_csv(file) -> pd.DataFrame:
    """Read a CSV upload safely with encoding fallback.

    Args:
        file: Uploaded file object

    Returns:
        DataFrame containing the CSV data
    """
    try:
        df = pd.read_csv(file)
    except UnicodeDecodeError:
        file.seek(0)
        df = pd.read_csv(file, encoding="latin-1")
    return df


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Basic, opinionated cleaning for v1.

    - Normalizes column names (strip whitespace, collapse multiple spaces)
    - Removes completely empty columns
    - Attempts to parse date-like columns using heuristics

    Args:
        df: Raw DataFrame

    Returns:
        Cleaned DataFrame
    """
    out = df.copy()

    # Normalize column names
    out.columns = (
        out.columns.astype(str)
        .str.strip()
        .str.replace(r"\s+", " ", regex=True)
    )

    # Remove empty columns
    out = out.dropna(axis=1, how="all")

    # Try to parse datelike columns (lightweight heuristic)
    for col in out.columns[: min(len(out.columns), 20)]:
        if out[col].dtype == "object":
            sample = out[col].dropna().astype(str).head(50)
            if sample.empty:
                continue
            parsed = pd.to_datetime(sample, errors="coerce", dayfirst=True)
            if parsed.notna().mean() >= 0.6:
                out[col] = pd.to_datetime(out[col], errors="coerce", dayfirst=True)

    return out
