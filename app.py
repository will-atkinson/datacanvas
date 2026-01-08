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


def apply_custom_css() -> None:
    """Apply custom CSS styling for a professional look."""
    st.markdown("""
        <style>
        /* Import professional font */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

        /* Global styling */
        html, body, [class*="css"] {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }

        /* Main content area */
        .main {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        }

        /* Header styling */
        h1 {
            color: #1e3a8a;
            font-weight: 700;
            letter-spacing: -0.5px;
            padding-bottom: 0.5rem;
            border-bottom: 3px solid #3b82f6;
            margin-bottom: 1rem;
        }

        h2, h3 {
            color: #1e40af;
            font-weight: 600;
            margin-top: 2rem;
        }

        /* Card-like containers */
        .stContainer {
            background: white;
            padding: 2rem;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
            margin: 1rem 0;
        }

        /* Metric cards */
        [data-testid="stMetricValue"] {
            font-size: 2rem;
            font-weight: 700;
            color: #1e40af;
        }

        [data-testid="stMetricLabel"] {
            font-size: 0.875rem;
            font-weight: 500;
            color: #64748b;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        /* File uploader */
        [data-testid="stFileUploader"] {
            background: white;
            padding: 2rem;
            border-radius: 12px;
            border: 2px dashed #3b82f6;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        }

        [data-testid="stFileUploader"]:hover {
            border-color: #2563eb;
            box-shadow: 0 6px 12px rgba(59, 130, 246, 0.15);
        }

        /* Buttons */
        .stButton > button {
            background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
            color: white;
            border: none;
            padding: 0.75rem 2rem;
            font-weight: 600;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(59, 130, 246, 0.25);
            transition: all 0.3s ease;
        }

        .stButton > button:hover {
            background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
            box-shadow: 0 6px 12px rgba(59, 130, 246, 0.35);
            transform: translateY(-2px);
        }

        .stDownloadButton > button {
            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
            color: white;
            border: none;
            padding: 0.75rem 2rem;
            font-weight: 600;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(16, 185, 129, 0.25);
        }

        .stDownloadButton > button:hover {
            background: linear-gradient(135deg, #059669 0%, #047857 100%);
            box-shadow: 0 6px 12px rgba(16, 185, 129, 0.35);
            transform: translateY(-2px);
        }

        /* Sidebar styling */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #1e3a8a 0%, #1e40af 100%);
        }

        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3,
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] label {
            color: white !important;
        }

        /* Info/Warning boxes */
        .stAlert {
            border-radius: 8px;
            border: none;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        }

        /* DataFrames */
        [data-testid="stDataFrame"] {
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        }

        /* Text input */
        .stTextInput > div > div > input {
            border-radius: 8px;
            border: 2px solid #e2e8f0;
            padding: 0.75rem;
            font-size: 1rem;
        }

        .stTextInput > div > div > input:focus {
            border-color: #3b82f6;
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
        }

        /* Expander */
        .streamlit-expanderHeader {
            background-color: #f8fafc;
            border-radius: 8px;
            font-weight: 600;
            color: #1e40af;
        }

        /* Spinner */
        .stSpinner > div {
            border-top-color: #3b82f6;
        }

        /* Remove padding from top */
        .block-container {
            padding-top: 2rem;
        }
        </style>
    """, unsafe_allow_html=True)


def sidebar_controls() -> None:
    """Render sidebar settings."""
    st.sidebar.markdown("### ⚙️ Settings")
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"**📁 Max Upload:** {CFG.max_upload_mb}MB")
    st.sidebar.markdown(f"**👁️ Preview Rows:** {CFG.max_preview_rows}")
    st.sidebar.markdown(f"**📊 Top Categories:** {CFG.top_n_categories}")
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📖 About")
    st.sidebar.markdown(
        "DataCanvas helps you analyze CSV files instantly with "
        "automatic insights, visualizations, and professional reports."
    )
    st.sidebar.markdown("---")
    st.sidebar.caption("Built with Streamlit & Python")


def main() -> None:
    """Main application entry point."""
    st.set_page_config(
        page_title=CFG.app_name,
        layout="wide",
        page_icon="📊",
        initial_sidebar_state="expanded"
    )

    apply_custom_css()
    sidebar_controls()

    # Header with better styling
    st.markdown(f"# 📊 {CFG.app_name}")
    st.markdown(
        """
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    padding: 1.5rem; border-radius: 12px; color: white; margin-bottom: 2rem;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);'>
            <h3 style='margin: 0; color: white; border: none; padding: 0;'>
                🚀 Transform Your Data Into Insights
            </h3>
            <p style='margin: 0.5rem 0 0 0; opacity: 0.95;'>
                Upload a CSV file to get instant KPIs, beautiful visualizations, and professional reports
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    uploaded = st.file_uploader(
        "📁 Upload Your CSV File",
        type=["csv"],
        accept_multiple_files=False,
        help="Upload a CSV file to begin analysis (max 10MB)"
    )

    if not uploaded:
        st.info("👆 Upload a CSV file to get started with your data analysis")

        # Add helpful example
        st.markdown("---")
        st.markdown("### 💡 What You'll Get")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("""
                **📈 Automatic Analysis**
                - Auto-detect date columns
                - Find key metrics
                - Identify categories
            """)
        with col2:
            st.markdown("""
                **📊 Visualizations**
                - Trend charts over time
                - Category breakdowns
                - Data previews
            """)
        with col3:
            st.markdown("""
                **📄 Professional Reports**
                - Downloadable PDF
                - KPI summaries
                - Data insights
            """)
        return

    if getattr(uploaded, "size", 0) > CFG.max_upload_mb * 1024 * 1024:
        st.error(f"⚠️ File too large. Please upload a CSV under {CFG.max_upload_mb}MB.")
        return

    with st.spinner("🔄 Reading your CSV file..."):
        df_raw = read_csv(uploaded)

    st.success(f"✅ Loaded {len(df_raw):,} rows and {len(df_raw.columns)} columns")

    # Section 1: Preview
    st.markdown("---")
    st.markdown("## 👁️ Data Preview")
    with st.expander("📋 View raw data (first 25 rows)", expanded=False):
        st.dataframe(df_raw.head(CFG.max_preview_rows), use_container_width=True)

    with st.spinner("🧹 Cleaning data and detecting column types..."):
        df = clean_dataframe(df_raw)
        date_col = infer_date_column(df)
        metric_col = infer_metric_column(df)
        category_col = infer_category_column(df)

    # Section 2: Inferred columns
    st.markdown("---")
    st.markdown("## 🔍 Detected Columns")
    c1, c2, c3 = st.columns(3)

    with c1:
        if date_col:
            c1.metric("📅 Date Column", date_col, help="Automatically detected date/time column")
        else:
            c1.metric("📅 Date Column", "Not found", delta="", delta_color="off")

    with c2:
        if metric_col:
            c2.metric("📊 Metric Column", metric_col, help="Primary numeric column for analysis")
        else:
            c2.metric("📊 Metric Column", "Not found", delta="", delta_color="off")

    with c3:
        if category_col:
            c3.metric("🏷️ Category Column", category_col, help="Categorical grouping column")
        else:
            c3.metric("🏷️ Category Column", "Not found", delta="", delta_color="off")

    # Section 3: KPIs
    st.markdown("---")
    st.markdown("## 📈 Key Performance Indicators")
    kpis = compute_kpis(df, date_col, metric_col)

    if kpis:
        cols = st.columns(min(4, max(1, len(kpis))))
        for i, (label, value) in enumerate(kpis):
            with cols[i % len(cols)]:
                st.metric(label, value)
    else:
        st.info("No KPIs available for this dataset")

    # Section 4: Charts
    st.markdown("---")
    st.markdown("## 📊 Visualizations")
    left, right = st.columns(2)

    with left:
        st.markdown("### 📈 Trend Over Time")
        if date_col and metric_col:
            with st.spinner("Creating trend chart..."):
                fig_trend = build_trend_chart(df, date_col, metric_col)
                st.pyplot(fig_trend, clear_figure=True)
        else:
            st.warning("⚠️ Trend chart requires a date column and numeric metric column")

    with right:
        st.markdown("### 🏷️ Category Breakdown")
        if category_col:
            with st.spinner("Creating category chart..."):
                fig_cat = build_category_chart(df, category_col, metric_col, CFG.top_n_categories)
                st.pyplot(fig_cat, clear_figure=True)
        else:
            st.warning("⚠️ Category chart requires a categorical column")

    # Section 5: Export
    st.markdown("---")
    st.markdown("## 📄 Export Report")

    report_title = st.text_input(
        "Report Title",
        value="Management Report",
        help="Enter a custom title for your PDF report"
    )

    with st.spinner("📝 Generating PDF report..."):
        report_bytes = render_report_stub(report_title, kpis, df)

    st.download_button(
        label="📥 Download PDF Report",
        data=report_bytes,
        file_name="management_report.pdf",
        mime="application/pdf",
        help="Download a professional PDF report with KPIs and data preview"
    )

    # Debug section
    with st.expander("🔧 Advanced: View cleaned data"):
        st.dataframe(df.head(CFG.max_preview_rows), use_container_width=True)


if __name__ == "__main__":
    main()
