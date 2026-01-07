"""Report generation utilities."""
from datetime import datetime
from io import BytesIO
from typing import List, Tuple

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle


def render_report_stub(title: str, kpis: List[Tuple[str, str]], df: pd.DataFrame) -> bytes:
    """Render a professional PDF report with KPIs and data preview.

    Args:
        title: Report title
        kpis: List of (label, value) KPI tuples
        df: DataFrame to include in preview

    Returns:
        PDF report as bytes
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.75*inch, bottomMargin=0.75*inch)

    # Container for the PDF elements
    elements = []

    # Get styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1f77b4'),
        spaceAfter=12,
    )
    heading_style = styles['Heading2']
    normal_style = styles['Normal']

    # Add title
    elements.append(Paragraph(title, title_style))
    elements.append(Spacer(1, 0.2*inch))

    # Add timestamp
    timestamp = f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}"
    elements.append(Paragraph(timestamp, normal_style))
    elements.append(Spacer(1, 0.3*inch))

    # Add KPIs section
    elements.append(Paragraph("Key Performance Indicators", heading_style))
    elements.append(Spacer(1, 0.1*inch))

    if kpis:
        # Create KPI table
        kpi_data = [[label, value] for label, value in kpis]
        kpi_table = Table(kpi_data, colWidths=[3.5*inch, 2.5*inch])
        kpi_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f0f0f0')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        elements.append(kpi_table)
    else:
        elements.append(Paragraph("No KPIs available", normal_style))

    elements.append(Spacer(1, 0.4*inch))

    # Add data preview section
    elements.append(Paragraph("Data Preview (First 10 Rows)", heading_style))
    elements.append(Spacer(1, 0.1*inch))

    if not df.empty:
        # Prepare data for table (limit to first 10 rows)
        preview_df = df.head(10)

        # Convert DataFrame to list of lists for ReportLab table
        table_data = [preview_df.columns.tolist()] + preview_df.values.tolist()

        # Limit columns if too many (to fit on page)
        max_cols = 6
        if len(table_data[0]) > max_cols:
            table_data = [row[:max_cols] + ['...'] for row in table_data]

        # Calculate column widths dynamically
        available_width = 6.5 * inch
        col_width = available_width / len(table_data[0])

        # Create table
        data_table = Table(table_data, colWidths=[col_width] * len(table_data[0]))
        data_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')]),
        ]))
        elements.append(data_table)
    else:
        elements.append(Paragraph("No data available", normal_style))

    # Build PDF
    doc.build(elements)

    # Get PDF bytes
    pdf_bytes = buffer.getvalue()
    buffer.close()

    return pdf_bytes
