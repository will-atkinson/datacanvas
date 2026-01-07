"""DataCanvas - CSV analysis and visualization web application."""
import streamlit as st

from config import CFG
from data import (
    read_csv,
    clean_dataframe,
    infer_date_column,
    infer_metric_column,
    infer_category_column,
)
from analytics import compute_kpis
from visualization import build_trend_chart, build_category_chart
from export import render_report_stub


def sidebar_controls() -> None:
    """Render sidebar settings."""
    st.sidebar.title("Settings")
    st.sidebar.caption("MVP: keep it minimal.")
    st.sidebar.write(f"Max upload: {CFG.max_upload_mb}MB")
    st.sidebar.write(f"Preview rows: {CFG.max_preview_rows}")


def main() -> None:
    """Main application entry point."""
    st.set_page_config(page_title=CFG.app_name, layout="wide")
    st.title(CFG.app_name)
    st.caption("Upload a CSV → instant KPIs + charts → export a management report (MVP).")

    sidebar_controls()

    uploaded = st.file_uploader("Upload a CSV", type=["csv"], accept_multiple_files=False)

    if not uploaded:
        st.info("Upload a CSV to begin.")
        return

    if getattr(uploaded, "size", 0) > CFG.max_upload_mb * 1024 * 1024:
        st.error(f"File too large. Please upload a CSV under {CFG.max_upload_mb}MB.")
        return

    with st.spinner("Reading CSV..."):
        df_raw = read_csv(uploaded)

    st.subheader("1) Preview")
    st.write("Raw preview:")
    st.dataframe(df_raw.head(CFG.max_preview_rows), use_container_width=True)

    with st.spinner("Cleaning & inferring columns..."):
        df = clean_dataframe(df_raw)
        date_col = infer_date_column(df)
        metric_col = infer_metric_column(df)
        category_col = infer_category_column(df)

    st.subheader("2) Inferred columns")
    c1, c2, c3 = st.columns(3)
    c1.metric("Date column", date_col or "—")
    c2.metric("Metric column", metric_col or "—")
    c3.metric("Category column", category_col or "—")

    st.subheader("3) KPIs")
    kpis = compute_kpis(df, date_col, metric_col)
    cols = st.columns(min(4, max(1, len(kpis))))
    for i, (label, value) in enumerate(kpis):
        cols[i % len(cols)].metric(label, value)

    st.subheader("4) Charts")
    left, right = st.columns(2)

    with left:
        if date_col and metric_col:
            fig_trend = build_trend_chart(df, date_col, metric_col)
            st.pyplot(fig_trend, clear_figure=True)
        else:
            st.warning("Trend chart requires an inferred date column and numeric metric column.")

    with right:
        if category_col:
            fig_cat = build_category_chart(df, category_col, metric_col, CFG.top_n_categories)
            st.pyplot(fig_cat, clear_figure=True)
        else:
            st.warning("Category chart requires an inferred category column.")

    st.subheader("5) Export")
    report_title = st.text_input("Report title", value="Management Report")
    report_bytes = render_report_stub(report_title, kpis, df)

    st.download_button(
        label="Download PDF Report",
        data=report_bytes,
        file_name="management_report.pdf",
        mime="application/pdf",
    )

    with st.expander("Debug: cleaned dataframe preview"):
        st.dataframe(df.head(CFG.max_preview_rows), use_container_width=True)


if __name__ == "__main__":
    main()
