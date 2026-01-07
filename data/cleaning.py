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

    # Try to parse datelike columns (improved heuristic)
    for col in out.columns:  # Check ALL columns, not just first 20
        if out[col].dtype == "object":
            sample = out[col].dropna().astype(str).head(100)  # Increased sample size
            if sample.empty:
                continue

            # Try multiple date parsing strategies
            best_parsed = None
            best_success_rate = 0.0

            # Strategy 1: ISO format (2024-01-15) - don't use dayfirst
            parsed = pd.to_datetime(sample, errors="coerce", format="mixed")
            success_rate = parsed.notna().mean()
            if success_rate > best_success_rate:
                best_parsed = parsed
                best_success_rate = success_rate

            # Strategy 2: Day-first format (15/01/2024 or 15-01-2024)
            if best_success_rate < 0.8:  # Only try if first strategy wasn't great
                parsed = pd.to_datetime(sample, errors="coerce", dayfirst=True)
                success_rate = parsed.notna().mean()
                if success_rate > best_success_rate:
                    best_parsed = parsed
                    best_success_rate = success_rate

            # Apply if we got at least 50% success rate (lowered threshold)
            if best_success_rate >= 0.5:
                # Apply the best strategy to the full column
                if best_parsed is not None:
                    # Determine which strategy worked best and apply to full column
                    parsed_full = pd.to_datetime(out[col], errors="coerce", format="mixed")
                    if parsed_full.notna().mean() < best_success_rate - 0.1:
                        # Try dayfirst if mixed format didn't work well
                        parsed_full = pd.to_datetime(out[col], errors="coerce", dayfirst=True)
                    out[col] = parsed_full

    return out
