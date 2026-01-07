"""Report generation utilities."""
from datetime import datetime
from typing import List, Tuple

import pandas as pd


def render_report_stub(title: str, kpis: List[Tuple[str, str]], df: pd.DataFrame) -> bytes:
    """Render a basic text report with KPIs and data preview.

    Args:
        title: Report title
        kpis: List of (label, value) KPI tuples
        df: DataFrame to include in preview

    Returns:
        Report content as bytes (UTF-8 encoded)
    """
    lines = [
        title,
        f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}",
        "",
        "KPIs:",
        *[f"- {k}: {v}" for k, v in kpis],
        "",
        "Preview (first 10 rows):",
        df.head(10).to_csv(index=False),
    ]
    return "\n".join(lines).encode("utf-8")
