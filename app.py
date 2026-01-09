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
    """Apply premium custom CSS styling with glassmorphism and advanced effects."""
    st.markdown("""
        <style>
        /* Import premium fonts */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600&display=swap');

        /* Smooth scrolling */
        html {
            scroll-behavior: smooth;
        }

        /* Global styling with premium font stack */
        html, body, [class*="css"] {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
        }

        /* Premium animated gradient background */
        .main {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 25%, #f093fb 50%, #4facfe 75%, #00f2fe 100%);
            background-size: 400% 400%;
            animation: gradientShift 15s ease infinite;
            position: relative;
        }

        .main::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(255, 255, 255, 0.92);
            backdrop-filter: blur(100px);
            z-index: 0;
        }

        .main > div {
            position: relative;
            z-index: 1;
        }

        @keyframes gradientShift {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }

        /* Premium header styling with text gradient */
        h1 {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-weight: 900;
            letter-spacing: -1.5px;
            padding-bottom: 1rem;
            border-bottom: 4px solid transparent;
            border-image: linear-gradient(90deg, #667eea, #764ba2, #f093fb);
            border-image-slice: 1;
            margin-bottom: 1.5rem;
            animation: titleGlow 3s ease-in-out infinite;
        }

        @keyframes titleGlow {
            0%, 100% { filter: drop-shadow(0 0 8px rgba(102, 126, 234, 0.3)); }
            50% { filter: drop-shadow(0 0 16px rgba(102, 126, 234, 0.5)); }
        }

        h2 {
            color: #1e40af;
            font-weight: 700;
            margin-top: 2.5rem;
            margin-bottom: 1rem;
            letter-spacing: -0.5px;
        }

        h3 {
            color: #4f46e5;
            font-weight: 600;
            letter-spacing: -0.3px;
        }

        /* Glassmorphism cards */
        .stContainer {
            background: rgba(255, 255, 255, 0.7);
            backdrop-filter: blur(20px) saturate(180%);
            -webkit-backdrop-filter: blur(20px) saturate(180%);
            padding: 2rem;
            border-radius: 20px;
            border: 1px solid rgba(255, 255, 255, 0.5);
            box-shadow:
                0 8px 32px rgba(0, 0, 0, 0.08),
                inset 0 1px 0 rgba(255, 255, 255, 0.5);
            margin: 1rem 0;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .stContainer:hover {
            transform: translateY(-4px);
            box-shadow:
                0 16px 48px rgba(0, 0, 0, 0.12),
                inset 0 1px 0 rgba(255, 255, 255, 0.6);
        }

        /* Premium metric cards with gradient borders */
        div[data-testid="metric-container"] {
            background: linear-gradient(135deg, rgba(255,255,255,0.9) 0%, rgba(255,255,255,0.7) 100%);
            backdrop-filter: blur(10px);
            padding: 1.5rem;
            border-radius: 16px;
            border: 2px solid transparent;
            background-clip: padding-box;
            position: relative;
            transition: all 0.3s ease;
        }

        div[data-testid="metric-container"]::before {
            content: '';
            position: absolute;
            inset: 0;
            border-radius: 16px;
            padding: 2px;
            background: linear-gradient(135deg, #667eea, #764ba2, #f093fb);
            -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
            mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
            -webkit-mask-composite: xor;
            mask-composite: exclude;
            opacity: 0.6;
            transition: opacity 0.3s ease;
        }

        div[data-testid="metric-container"]:hover::before {
            opacity: 1;
        }

        div[data-testid="metric-container"]:hover {
            transform: scale(1.02);
            box-shadow: 0 8px 24px rgba(102, 126, 234, 0.2);
        }

        [data-testid="stMetricValue"] {
            font-size: 2.5rem;
            font-weight: 800;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            letter-spacing: -1px;
        }

        [data-testid="stMetricLabel"] {
            font-size: 0.8rem;
            font-weight: 600;
            color: #64748b;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        /* Premium file uploader with pulsing effect */
        [data-testid="stFileUploader"] {
            background: rgba(255, 255, 255, 0.8);
            backdrop-filter: blur(10px);
            padding: 3rem;
            border-radius: 20px;
            border: 3px dashed #667eea;
            box-shadow:
                0 8px 32px rgba(102, 126, 234, 0.15),
                inset 0 1px 0 rgba(255, 255, 255, 0.6);
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
        }

        [data-testid="stFileUploader"]::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(102, 126, 234, 0.1) 0%, transparent 70%);
            animation: pulse 3s ease-in-out infinite;
        }

        @keyframes pulse {
            0%, 100% { transform: scale(1); opacity: 0.5; }
            50% { transform: scale(1.1); opacity: 0.8; }
        }

        [data-testid="stFileUploader"]:hover {
            border-color: #764ba2;
            transform: translateY(-4px);
            box-shadow: 0 12px 48px rgba(102, 126, 234, 0.25);
        }

        /* Premium buttons with shine effect */
        .stButton > button, .stDownloadButton > button {
            position: relative;
            color: white;
            border: none;
            padding: 1rem 2.5rem;
            font-weight: 700;
            font-size: 1rem;
            border-radius: 12px;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            overflow: hidden;
            letter-spacing: 0.5px;
        }

        .stButton > button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            box-shadow:
                0 4px 15px rgba(102, 126, 234, 0.4),
                0 1px 2px rgba(0, 0, 0, 0.1);
        }

        .stDownloadButton > button {
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
            box-shadow:
                0 4px 15px rgba(17, 153, 142, 0.4),
                0 1px 2px rgba(0, 0, 0, 0.1);
        }

        .stButton > button::before,
        .stDownloadButton > button::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: linear-gradient(
                45deg,
                transparent,
                rgba(255, 255, 255, 0.3),
                transparent
            );
            transform: rotate(45deg);
            transition: all 0.5s;
        }

        .stButton > button:hover::before,
        .stDownloadButton > button:hover::before {
            left: 100%;
        }

        .stButton > button:hover {
            transform: translateY(-3px) scale(1.02);
            box-shadow:
                0 8px 25px rgba(102, 126, 234, 0.5),
                0 4px 8px rgba(0, 0, 0, 0.1);
        }

        .stDownloadButton > button:hover {
            transform: translateY(-3px) scale(1.02);
            box-shadow:
                0 8px 25px rgba(17, 153, 142, 0.5),
                0 4px 8px rgba(0, 0, 0, 0.1);
        }

        /* Premium sidebar with glassmorphism */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, rgba(30, 58, 138, 0.95) 0%, rgba(30, 64, 175, 0.95) 100%);
            backdrop-filter: blur(20px);
            border-right: 1px solid rgba(255, 255, 255, 0.1);
        }

        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3,
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] .caption {
            color: white !important;
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }

        /* Premium alert boxes */
        .stAlert {
            border-radius: 12px;
            border: none;
            backdrop-filter: blur(10px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        }

        /* Premium dataframes */
        [data-testid="stDataFrame"] {
            border-radius: 12px;
            overflow: hidden;
            box-shadow:
                0 8px 24px rgba(0, 0, 0, 0.12),
                0 2px 6px rgba(0, 0, 0, 0.08);
            border: 1px solid rgba(0, 0, 0, 0.05);
        }

        /* Premium text input */
        .stTextInput > div > div > input {
            border-radius: 12px;
            border: 2px solid #e2e8f0;
            padding: 1rem;
            font-size: 1rem;
            transition: all 0.3s ease;
            background: rgba(255, 255, 255, 0.9);
        }

        .stTextInput > div > div > input:focus {
            border-color: #667eea;
            box-shadow:
                0 0 0 4px rgba(102, 126, 234, 0.1),
                0 4px 12px rgba(102, 126, 234, 0.15);
            background: white;
            transform: translateY(-2px);
        }

        /* Premium expander */
        .streamlit-expanderHeader {
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
            backdrop-filter: blur(10px);
            border-radius: 12px;
            font-weight: 700;
            color: #4f46e5;
            border: 1px solid rgba(102, 126, 234, 0.2);
            transition: all 0.3s ease;
        }

        .streamlit-expanderHeader:hover {
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.2) 0%, rgba(118, 75, 162, 0.2) 100%);
            transform: translateX(4px);
        }

        /* Premium spinner */
        .stSpinner > div {
            border-top-color: #667eea;
            border-right-color: #764ba2;
        }

        /* Premium success message */
        .stSuccess {
            background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(5, 150, 105, 0.1) 100%);
            backdrop-filter: blur(10px);
            border-left: 4px solid #10b981;
        }

        /* Refined spacing */
        .block-container {
            padding-top: 2rem;
            padding-bottom: 4rem;
        }

        /* Subtle animations for content */
        [data-testid="stVerticalBlock"] > div {
            animation: fadeInUp 0.6s ease-out;
        }

        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        /* Premium scrollbar */
        ::-webkit-scrollbar {
            width: 12px;
        }

        ::-webkit-scrollbar-track {
            background: rgba(0, 0, 0, 0.05);
            border-radius: 10px;
        }

        ::-webkit-scrollbar-thumb {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 10px;
            border: 2px solid rgba(255, 255, 255, 0.5);
        }

        ::-webkit-scrollbar-thumb:hover {
            background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
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
    # Check if custom logo exists
    import os
    logo_path = "assets/logo.png"
    has_logo = os.path.exists(logo_path)

    st.set_page_config(
        page_title=CFG.app_name,
        layout="wide",
        page_icon=logo_path if has_logo else "🎨",
        initial_sidebar_state="expanded"
    )

    apply_custom_css()
    sidebar_controls()

    # Header with logo and styling
    if has_logo:
        col1, col2 = st.columns([1, 10])
        with col1:
            st.image(logo_path, width=80)
        with col2:
            st.markdown(f"# {CFG.app_name}", unsafe_allow_html=True)
    else:
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
