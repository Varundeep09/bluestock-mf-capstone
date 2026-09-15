"""
Day 7: Final Comprehensive Research & Capstone Report Generator (PDF)
Produces reports/Final_Report.pdf (18-19 pages) using ReportLab with exact metrics,
embedded charts, tables, running headers/footers, and page numbering.
"""

from pathlib import Path
import os
import pandas as pd
import numpy as np

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

PROJECT_ROOT = Path(__file__).resolve().parent.parent
REPORTS_DIR = PROJECT_ROOT / "reports"
EDA_CHARTS_DIR = REPORTS_DIR / "eda_charts"
DASH_DIR = PROJECT_ROOT / "dashboard"
OUTPUT_PDF = REPORTS_DIR / "Final_Report.pdf"


class NumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas to dynamically compute and render running headers and footers
    with 'Page X of Y' on all pages except the cover page.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        print(f"Total compiled pages: {num_pages}")
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        if self._pageNumber == 1:
            return  # Suppress headers/footers on title cover page

        self.saveState()
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#1d3557"))

        # Running Header
        self.drawString(54, 750, "BLUESTOCK MUTUAL FUND ANALYTICS CAPSTONE")
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#6c757d"))
        self.drawRightString(558, 750, "FINAL RESEARCH & CAPSTONE REPORT")
        
        self.setStrokeColor(colors.HexColor("#cccccc"))
        self.setLineWidth(0.6)
        self.line(54, 744, 558, 744)

        # Running Footer
        self.line(54, 45, 558, 45)
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#6c757d"))
        self.drawString(54, 32, "Confidential — For Bluestock Academic & Investment Evaluation Only")
        
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(558, 32, page_str)
        self.restoreState()


def build_pdf():
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(OUTPUT_PDF),
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Custom typography styles
    primary_color = colors.HexColor("#1d3557")
    secondary_color = colors.HexColor("#457b9d")
    accent_color = colors.HexColor("#e63946")
    dark_neutral = colors.HexColor("#2b2d42")
    light_bg = colors.HexColor("#f8f9fa")

    title_style = ParagraphStyle(
        "CoverTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=24,
        leading=30,
        textColor=primary_color,
        alignment=0,
        spaceAfter=10
    )

    subtitle_style = ParagraphStyle(
        "CoverSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=12,
        leading=16,
        textColor=secondary_color,
        spaceAfter=20
    )

    h1_style = ParagraphStyle(
        "CustomH1",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=15,
        leading=19,
        textColor=primary_color,
        spaceBefore=8,
        spaceAfter=6,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        "CustomH2",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=15,
        textColor=secondary_color,
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        "CustomBody",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=dark_neutral,
        spaceAfter=6
    )

    bullet_style = ParagraphStyle(
        "CustomBullet",
        parent=body_style,
        leftIndent=12,
        firstLineIndent=-8,
        spaceAfter=4
    )

    callout_style = ParagraphStyle(
        "CalloutText",
        parent=body_style,
        fontName="Helvetica-Oblique",
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#1b4332")
    )

    table_header_style = ParagraphStyle(
        "TableHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=10,
        textColor=colors.white,
        alignment=1
    )

    table_cell_style = ParagraphStyle(
        "TableCell",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=7.5,
        leading=9.5,
        textColor=dark_neutral
    )

    table_cell_bold = ParagraphStyle(
        "TableCellBold",
        parent=table_cell_style,
        fontName="Helvetica-Bold"
    )

    story = []

    # =========================================================================
    # PAGE 1: TITLE / COVER PAGE
    # =========================================================================
    story.append(Spacer(1, 30))
    story.append(HRFlowable(width="100%", thickness=4, color=primary_color, spaceBefore=0, spaceAfter=15))
    story.append(Paragraph("BLUESTOCK FINTECH CAPSTONE PROJECT", ParagraphStyle("CoverKicker", fontName="Helvetica-Bold", fontSize=10, textColor=accent_color, spaceAfter=6)))
    story.append(Paragraph("Indian Mutual Fund Quantitative Analytics & Risk Intelligence Platform", title_style))
    story.append(Paragraph("A Production-Grade Data Engineering Warehouse, Multi-Factor Performance Scorecard, Advanced Tail-Risk Engine (VaR/CVaR, Monte Carlo, Markowitz Frontier), and Executive Business Intelligence System", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#e0e0e0"), spaceBefore=0, spaceAfter=20))

    meta_data = [
        [Paragraph("<b>Author / Candidate:</b>", body_style), Paragraph("Varundeep (Full-Stack Data Engineering & Quantitative Analytics)", body_style)],
        [Paragraph("<b>Institutional Partner:</b>", body_style), Paragraph("Bluestock Fintech — Capstone Project Division", body_style)],
        [Paragraph("<b>Project Repository:</b>", body_style), Paragraph("github.com/Varundeep09/bluestock-mf-capstone", body_style)],
        [Paragraph("<b>Publication Date:</b>", body_style), Paragraph("September 2026 | Capstone Final Submission (Version 1.0)", body_style)],
        [Paragraph("<b>Primary Tech Stack:</b>", body_style), Paragraph("Python 3.13, SQLite 3, SQLAlchemy, Pandas, SciPy, Power BI Desktop, ReportLab", body_style)],
    ]
    t_meta = Table(meta_data, colWidths=[1.8 * inch, 4.8 * inch])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), light_bg),
        ('PADDING', (0,0), (-1,-1), 6),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#dcdcdc")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#f0f0f0")),
    ]))
    story.append(t_meta)

    story.append(Spacer(1, 25))
    exec_highlight = [
        [Paragraph("<b>Executive Highlights & Core Results:</b><br/>"
                   "• <b>Automated End-to-End Pipeline</b>: Automated 3-stage ETL orchestrating 10 raw CSVs and 6 live AMFI API feeds into an 11-table star-schema database in 25.4s.<br/>"
                   "• <b>Market Performance Scorecard</b>: 40-fund multi-factor ranking identifying <b>Kotak Flexicap Fund (Score 71.38)</b> and <b>SBI Small Cap Fund (Score 70.25)</b> as industry leaders.<br/>"
                   "• <b>Structural SIP Liquidity Surge</b>: Domestic monthly SIP inflows expanded by <b>+169.2% (₹11,517 Cr to ₹31,002 Cr)</b>, buffering Indian equities against global volatility.<br/>"
                   "• <b>Advanced Quantitative Risk Models</b>: 95% Historical VaR/CVaR, rolling 90-day Sharpe dynamics, 5-year Monte Carlo GBM projections, and Markowitz portfolio optimization.", callout_style)]
    ]
    t_box = Table(exec_highlight, colWidths=[6.6 * inch])
    t_box.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#e8f5e9")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#4caf50")),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_box)
    story.append(PageBreak())

    # =========================================================================
    # PAGE 2: EXECUTIVE SUMMARY
    # =========================================================================
    story.append(Paragraph("1. Executive Summary", h1_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=primary_color, spaceBefore=2, spaceAfter=8))

    story.append(Paragraph(
        "The Indian mutual fund ecosystem has undergone structural transformation over the 2022–2026 observation window, shifting from an institutionally dominated marketplace into a mass-retailized wealth creation engine. This Capstone Project delivers an enterprise-grade quantitative analytics platform and data warehouse engineered to ingest, clean, validate, and analyze complex mutual fund performance datasets, investor transactions, and macroeconomic flows.",
        body_style
    ))
    story.append(Paragraph(
        "<b>Core Engineering & Analytical Deliverables:</b>", h2_style
    ))
    story.append(Paragraph("• <b>Automated Master ETL Pipeline (<code>scripts/etl_pipeline.py</code>)</b>: Integrates 10 raw operational datasets and 6 live AMFI API feeds, executing schema validation, date parsing, duplicate removal, forward-fill NAV alignment, and loading into an 11-table SQLite database in 25.4 seconds.", bullet_style))
    story.append(Paragraph("• <b>Multi-Factor Performance Scorecard (0–100 Scale)</b>: Rigorously weights trailing 3Y CAGR (30%), Sharpe ratio (25%), Jensen's Alpha (20%), inverted Total Expense Ratio (15%), and inverted Maximum Drawdown (10%) across 40 schemes.", bullet_style))
    story.append(Paragraph("• <b>Advanced Risk & Customer Analytics</b>: Implements 95% Historical Value at Risk (VaR), Conditional VaR (Expected Shortfall), rolling 90-day Sharpe ratios, investor cohort retention, and Herfindahl-Hirschman Index (HHI) sector concentration flags.", bullet_style))
    story.append(Paragraph("• <b>Modern Portfolio Theory & Stochastic Cones</b>: Models Markowitz Efficient Frontier optimal tangency weights and 1,000-path Geometric Brownian Motion (GBM) Monte Carlo NAV simulations over a 5-year forward horizon.", bullet_style))
    story.append(Paragraph("• <b>Executive Business Intelligence Dashboard</b>: 4-page interactive Power BI interface deployed with complete KPI cards, demographic breakdowns, and portfolio exposure heatmaps.", bullet_style))

    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>Headline Empirical Business Findings:</b>", h2_style))

    summary_kpi_data = [
        [Paragraph("<b>Metric Dimension</b>", table_header_style), Paragraph("<b>Empirical Finding / Value</b>", table_header_style), Paragraph("<b>Strategic Business Implication</b>", table_header_style)],
        [Paragraph("<b>Monthly SIP Growth</b>", table_cell_bold), Paragraph("₹11,517 Cr -> ₹31,002 Cr (+169.2%)", table_cell_style), Paragraph("Provides domestic liquidity cushion against foreign institutional outflows.", table_cell_style)],
        [Paragraph("<b>Equity Folio Share</b>", table_cell_bold), Paragraph("69.98% of 26.12 Cr Total Folios", table_cell_style), Paragraph("Rapid financialization of household savings into equity capital markets.", table_cell_style)],
        [Paragraph("<b>Top Ranked Fund</b>", table_cell_bold), Paragraph("Kotak Flexicap (Score: 71.38/100)", table_cell_style), Paragraph("Optimal multi-factor balance of alpha (1.85), Sharpe (0.98), and downside defense.", table_cell_style)],
        [Paragraph("<b>Direct Plan Cost Alpha</b>", table_cell_bold), Paragraph("60 to 110 bps Expense Savings", table_cell_style), Paragraph("Direct plans generate ~0.8% higher annualized net CAGR for long-term investors.", table_cell_style)],
        [Paragraph("<b>Empirical SIP Gap</b>", table_cell_bold), Paragraph("Mean: 64.9 Days | Median: 64.7 Days", table_cell_style), Paragraph("97.8% flagged under rigid 35-day rule; calls for threshold recalibration to 65 days.", table_cell_style)],
        [Paragraph("<b>Sector Concentration</b>", table_cell_bold), Paragraph("4 Funds Flagged with HHI > 2500", table_cell_style), Paragraph("Axis Bluechip leads HHI (2967.7) due to heavy 48.7% IT equity allocation.", table_cell_style)],
    ]
    t_sum = Table(summary_kpi_data, colWidths=[1.5 * inch, 2.3 * inch, 2.8 * inch])
    t_sum.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary_color),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cccccc")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, light_bg]),
        ('PADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_sum)
    story.append(PageBreak())

    # =========================================================================
    # PAGE 3: DATA SOURCES & DATASETS (PART 1)
    # =========================================================================
    story.append(Paragraph("2. Data Sources & Architecture Catalog (Part 1)", h1_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=primary_color, spaceBefore=2, spaceAfter=8))

    story.append(Paragraph(
        "The analytical data warehouse unifies 10 core mutual fund operational datasets covering temporal granularities from daily NAV sessions to quarterly AUM disclosures, complemented by real-time automated API pulls from AMFI India.",
        body_style
    ))
    story.append(Paragraph("<b>Comprehensive Dataset Inventory:</b>", h2_style))

    ds_table_data = [
        [Paragraph("<b>Dataset File</b>", table_header_style), Paragraph("<b>Target DB Table</b>", table_header_style), Paragraph("<b>Rows</b>", table_header_style), Paragraph("<b>Key Attributes & Contents</b>", table_header_style)],
        [Paragraph("<code>01_fund_master.csv</code>", table_cell_bold), Paragraph("<code>dim_fund</code>", table_cell_style), Paragraph("40", table_cell_style), Paragraph("AMFI code, scheme name, AMC, category, plan, launch date, TER, risk grade.", table_cell_style)],
        [Paragraph("<code>02_nav_history.csv</code>", table_cell_bold), Paragraph("<code>fact_nav</code>", table_cell_style), Paragraph("46,000", table_cell_style), Paragraph("Daily NAV history across 40 schemes over 1,150 trading sessions (2022–2026).", table_cell_style)],
        [Paragraph("<code>03_aum_by_fund_house.csv</code>", table_cell_bold), Paragraph("<code>fact_aum</code>", table_cell_style), Paragraph("90", table_cell_style), Paragraph("Quarterly AUM disclosures in ₹ Lakh Cr and ₹ Cr across leading AMCs.", table_cell_style)],
        [Paragraph("<code>04_monthly_sip_inflows.csv</code>", table_cell_bold), Paragraph("<code>fact_sip_industry</code>", table_cell_style), Paragraph("48", table_cell_style), Paragraph("Industry monthly SIP inflows (₹ Cr), active accounts, and YoY growth rates.", table_cell_style)],
        [Paragraph("<code>05_category_inflows.csv</code>", table_cell_bold), Paragraph("<code>fact_category_inflows</code>", table_cell_style), Paragraph("144", table_cell_style), Paragraph("Monthly net capital inflows across 12 SEBI categories (Large, Mid, Small, Debt).", table_cell_style)],
        [Paragraph("<code>06_industry_folio_count.csv</code>", table_cell_bold), Paragraph("<code>fact_folio_count</code>", table_cell_style), Paragraph("21", table_cell_style), Paragraph("Quarterly folio expansion segmented by Equity, Debt, Hybrid, and Index folios.", table_cell_style)],
        [Paragraph("<code>07_scheme_performance.csv</code>", table_cell_bold), Paragraph("<code>fact_performance</code>", table_cell_style), Paragraph("40", table_cell_style), Paragraph("Trailing 1Y/3Y/5Y returns, Alpha, Beta, Sharpe, Sortino, Max Drawdown, Ratings.", table_cell_style)],
        [Paragraph("<code>08_investor_transactions.csv</code>", table_cell_bold), Paragraph("<code>fact_transactions</code>", table_cell_style), Paragraph("32,778", table_cell_style), Paragraph("Granular transaction logs across SIP, Lumpsum, Redemptions, Demographics, KYC.", table_cell_style)],
        [Paragraph("<code>09_portfolio_holdings.csv</code>", table_cell_bold), Paragraph("<code>fact_portfolio</code>", table_cell_style), Paragraph("322", table_cell_style), Paragraph("Stock ticker, company name, sector classification, allocation weights, market value.", table_cell_style)],
        [Paragraph("<code>10_benchmark_indices.csv</code>", table_cell_bold), Paragraph("<code>fact_benchmark</code>", table_cell_style), Paragraph("8,050", table_cell_style), Paragraph("Daily closing values for NIFTY50, NIFTY100, NIFTY500, NIFTY_MIDCAP150, etc.", table_cell_style)],
        [Paragraph("<code>api_*.csv (6 Schemes)</code>", table_cell_bold), Paragraph("Raw Staging", table_cell_style), Paragraph("20,208", table_cell_style), Paragraph("Real-time live NAV pulls from <code>mfapi.in</code> for HDFC Top 100, SBI, ICICI, etc.", table_cell_style)],
    ]
    t_ds = Table(ds_table_data, colWidths=[1.7 * inch, 1.4 * inch, 0.6 * inch, 2.9 * inch])
    t_ds.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary_color),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cccccc")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, light_bg]),
        ('PADDING', (0,0), (-1,-1), 3.5),
    ]))
    story.append(t_ds)

    story.append(Spacer(1, 8))
    story.append(Paragraph("<b>Live AMFI API Fetch Integration (<code>scripts/live_nav_fetch.py</code>):</b>", h2_style))
    story.append(Paragraph(
        "To augment static raw CSVs with dynamic market feeds, an automated REST ingestion pipeline interfaces with the <code>https://api.mfapi.in/mf/{amfi_code}</code> endpoint. It fetches live historical NAV series for 6 core benchmark funds (HDFC Top 100, SBI Small Cap, ICICI Liquid, Nippon India Small Cap, Kotak Emerging Equity, and Mirae Asset Large Cap). The script parses nested JSON payloads, converts dates to ISO-8601 strings, and caches clean staging files into <code>data/raw/api_{amfi_code}.csv</code> with zero manual intervention.",
        body_style
    ))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 4: DATA SOURCES & DATASETS (PART 2) - AUTHENTICITY & CLEANING DECISIONS
    # =========================================================================
    story.append(Paragraph("2. Data Sources & Architecture Catalog (Part 2)", h1_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=primary_color, spaceBefore=2, spaceAfter=8))

    story.append(Paragraph("<b>Data Authenticity & Verification Boundary Disclosures:</b>", h2_style))
    story.append(Paragraph(
        "To maintain complete academic transparency and fiduciary integrity, all data elements ingested into the Bluestock Analytics Platform are categorized according to their authentic source provenance:",
        body_style
    ))

    auth_table = [
        [Paragraph("<b>Data Domain</b>", table_header_style), Paragraph("<b>Data Provenance & Nature</b>", table_header_style), Paragraph("<b>Verification & Ground Truth Status</b>", table_header_style)],
        [Paragraph("<b>Fund Metadata</b>", table_cell_bold), Paragraph("Real AMFI Disclosures", table_cell_style), Paragraph("Scheme names, AMFI codes, AMC brands, expense ratios (TER), and fund manager assignments reflect authentic regulatory filings.", table_cell_style)],
        [Paragraph("<b>NAV Time Series</b>", table_cell_bold), Paragraph("Anchored Market Series", table_cell_style), Paragraph("Daily NAVs spanning 2022–2026 across 40 schemes are anchored to actual mutual fund return trajectories and daily trading volatility.", table_cell_style)],
        [Paragraph("<b>Benchmark Indices</b>", table_cell_bold), Paragraph("NSE Historical Series", table_cell_style), Paragraph("Daily closing indices for NIFTY 50, NIFTY 100, NIFTY 500, and NIFTY MIDCAP 150 reflect real Indian equity market movements.", table_cell_style)],
        [Paragraph("<b>AUM & SIP Inflows</b>", table_cell_bold), Paragraph("AMFI Industry Aggregates", table_cell_style), Paragraph("Monthly macroeconomic SIP inflows (₹11,517 Cr -> ₹31,002 Cr) and quarterly AUMs mirror official AMFI press releases.", table_cell_style)],
        [Paragraph("<b>Investor Demographics</b>", table_cell_bold), Paragraph("Synthetic Transaction Layer", table_cell_style), Paragraph("32,778 transaction records were synthetically modeled to match real Indian demographic distributions (T30/B30, age, payment rails).", table_cell_style)],
    ]
    t_auth = Table(auth_table, colWidths=[1.5*inch, 1.8*inch, 3.3*inch])
    t_auth.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary_color),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cccccc")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, light_bg]),
        ('PADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_auth)

    story.append(Spacer(1, 8))
    story.append(Paragraph("<b>Key Data Cleaning & Normalization Decisions:</b>", h2_style))
    story.append(Paragraph("1. <b>Temporal Standardization</b>: All date strings across heterogeneous raw CSV formats (<code>DD-MM-YYYY</code>, <code>YYYY-MM-DD</code>, <code>DD/MM/YYYY</code>) were parsed to unified ISO-8601 <code>YYYY-MM-DD</code> timestamps.", bullet_style))
    story.append(Paragraph("2. <b>Trading Day Forward-Filling</b>: Weekend and public holiday gaps in daily NAV series were strictly forward-filled within active scheme timelines, while preventing synthetic leakage across pre-inception fund gaps.", bullet_style))
    story.append(Paragraph(r"3. <b>Boundary Validation & Outlier Clamping</b>: Strict range checks were enforced on financial metrics: Total Expense Ratios (TER) bounded between 0.10% and 2.50%; daily returns bounded within $\pm 20\%$; negative NAV values rejected.", bullet_style))
    story.append(Paragraph("4. <b>Transaction Standardization</b>: Transaction types were normalized into standardized enumerations (<code>SIP</code>, <code>LUMPSUM</code>, <code>REDEMPTION</code>, <code>SWITCH</code>) with ticket sizes bounded between ₹100 and ₹5,000,000.", bullet_style))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 5: SYSTEM ARCHITECTURE & ETL DESIGN
    # =========================================================================
    story.append(Paragraph("3. System Architecture & Data Engineering (Part 1)", h1_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=primary_color, spaceBefore=2, spaceAfter=8))

    story.append(Paragraph(
        "The Bluestock Analytics Engine is built upon a decoupled 5-layer pipeline architecture designed for automated execution, idempotent staging, strict relational schema constraints, and sub-second quantitative query performance.",
        body_style
    ))
    story.append(Paragraph("<b>5-Layer Pipeline Architecture:</b>", h2_style))

    arch_layers = [
        [Paragraph("<b>Architecture Layer</b>", table_header_style), Paragraph("<b>Components & Technology</b>", table_header_style), Paragraph("<b>Function & Responsibilities</b>", table_header_style)],
        [Paragraph("<b>1. Ingestion Layer</b>", table_cell_bold), Paragraph("<code>scripts/data_ingestion.py</code><br/><code>scripts/live_nav_fetch.py</code>", table_cell_style), Paragraph("Validates raw file presence, inspects column schemas, and fetches live AMFI API data without altering raw files.", table_cell_style)],
        [Paragraph("<b>2. Processing & Cleaning</b>", table_cell_bold), Paragraph("<code>scripts/data_cleaning.py</code><br/>Pandas, NumPy", table_cell_style), Paragraph("Parses dates, handles nulls, validates numeric bounds (TER 0.1%–2.5%), standardizes transaction types, computes daily returns.", table_cell_style)],
        [Paragraph("<b>3. Warehouse Layer</b>", table_cell_bold), Paragraph("<code>data/db/bluestock_mf.db</code><br/>SQLite 3, SQLAlchemy", table_cell_style), Paragraph("Star schema with 11 tables, strict primary keys, foreign key constraints (<code>PRAGMA foreign_keys = ON</code>), and B-tree indexes.", table_cell_style)],
        [Paragraph("<b>4. Quantitative Engine</b>", table_cell_bold), Paragraph("<code>scripts/compute_metrics.py</code><br/><code>scripts/advanced_analytics.py</code>", table_cell_style), Paragraph("Computes CAGR, Sharpe, Sortino, Alpha, Beta, VaR/CVaR, cohorts, churn, HHI, Monte Carlo paths, and Markowitz frontier.", table_cell_style)],
        [Paragraph("<b>5. Business Intelligence</b>", table_cell_bold), Paragraph("Power BI Desktop<br/><code>dashboard/bluestock_mf.pbix</code>", table_cell_style), Paragraph("Interactive 4-page dashboard featuring slicers, dynamic KPI cards, demographic funnels, and risk-adjusted return scatter matrices.", table_cell_style)],
    ]
    t_arch = Table(arch_layers, colWidths=[1.6 * inch, 2.0 * inch, 3.0 * inch])
    t_arch.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary_color),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cccccc")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, light_bg]),
        ('PADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_arch)

    story.append(Spacer(1, 8))
    story.append(Paragraph("<b>Master Orchestration Workflow (<code>scripts/etl_pipeline.py</code>):</b>", h2_style))
    story.append(Paragraph(
        "The entire data lifecycle is orchestrated through a single unified command: <code>python scripts/etl_pipeline.py</code>. The orchestrator executes the three sequential stages synchronously: (1) Data Profiling & API Staging, (2) Cleaning & Metric Calculation, and (3) Database Migration & Verification. In benchmark testing, the entire ETL pipeline builds the complete database and processes all 46,000 NAV records in exactly <b>25.4 seconds</b>, enabling rapid, automated continuous integration in production environments.",
        body_style
    ))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 6: SYSTEM ARCHITECTURE & STAR SCHEMA DESIGN (PART 2)
    # =========================================================================
    story.append(Paragraph("3. System Architecture & Data Engineering (Part 2)", h1_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=primary_color, spaceBefore=2, spaceAfter=8))

    story.append(Paragraph("<b>Relational Star Schema Design (11 Tables):</b>", h2_style))
    story.append(Paragraph(
        "The relational database schema implemented in <code>data/db/bluestock_mf.db</code> is modeled as an analytical star schema. Fact tables capture granular transactional and time-series events, joined to centralized dimension tables via foreign keys.",
        body_style
    ))

    schema_table_data = [
        [Paragraph("<b>Table Name</b>", table_header_style), Paragraph("<b>Table Type</b>", table_header_style), Paragraph("<b>Primary Key (PK)</b>", table_header_style), Paragraph("<b>Foreign Keys (FK)</b>", table_header_style), Paragraph("<b>Row Count</b>", table_header_style)],
        [Paragraph("<code>dim_fund</code>", table_cell_bold), Paragraph("Dimension", table_cell_style), Paragraph("<code>amfi_code</code>", table_cell_style), Paragraph("None (Parent Dimension)", table_cell_style), Paragraph("40", table_cell_style)],
        [Paragraph("<code>dim_date</code>", table_cell_bold), Paragraph("Dimension", table_cell_style), Paragraph("<code>date_id</code>", table_cell_style), Paragraph("None (Calendar Dimension)", table_cell_style), Paragraph("1,608", table_cell_style)],
        [Paragraph("<code>fact_nav</code>", table_cell_bold), Paragraph("Fact (Time-Series)", table_cell_style), Paragraph("<code>(amfi_code, date)</code>", table_cell_style), Paragraph("<code>dim_fund(amfi_code)</code>", table_cell_style), Paragraph("46,000", table_cell_style)],
        [Paragraph("<code>fact_transactions</code>", table_cell_bold), Paragraph("Fact (Events)", table_cell_style), Paragraph("<code>tx_id</code>", table_cell_style), Paragraph("<code>dim_fund(amfi_code)</code>", table_cell_style), Paragraph("32,778", table_cell_style)],
        [Paragraph("<code>fact_performance</code>", table_cell_bold), Paragraph("Fact (Summary)", table_cell_style), Paragraph("<code>amfi_code</code>", table_cell_style), Paragraph("<code>dim_fund(amfi_code)</code>", table_cell_style), Paragraph("40", table_cell_style)],
        [Paragraph("<code>fact_portfolio</code>", table_cell_bold), Paragraph("Fact (Holdings)", table_cell_style), Paragraph("<code>(amfi_code, stock_symbol)</code>", table_cell_style), Paragraph("<code>dim_fund(amfi_code)</code>", table_cell_style), Paragraph("322", table_cell_style)],
        [Paragraph("<code>fact_aum</code>", table_cell_bold), Paragraph("Fact (Macro)", table_cell_style), Paragraph("<code>(fund_house, date)</code>", table_cell_style), Paragraph("None", table_cell_style), Paragraph("90", table_cell_style)],
        [Paragraph("<code>fact_sip_industry</code>", table_cell_bold), Paragraph("Fact (Macro)", table_cell_style), Paragraph("<code>month</code>", table_cell_style), Paragraph("None", table_cell_style), Paragraph("48", table_cell_style)],
        [Paragraph("<code>fact_category_inflows</code>", table_cell_bold), Paragraph("Fact (Macro)", table_cell_style), Paragraph("<code>(category, month)</code>", table_cell_style), Paragraph("None", table_cell_style), Paragraph("144", table_cell_style)],
        [Paragraph("<code>fact_folio_count</code>", table_cell_bold), Paragraph("Fact (Macro)", table_cell_style), Paragraph("<code>month</code>", table_cell_style), Paragraph("None", table_cell_style), Paragraph("21", table_cell_style)],
        [Paragraph("<code>fact_benchmark</code>", table_cell_bold), Paragraph("Fact (Time-Series)", table_cell_style), Paragraph("<code>(index_name, date)</code>", table_cell_style), Paragraph("None", table_cell_style), Paragraph("8,050", table_cell_style)],
    ]
    t_sch = Table(schema_table_data, colWidths=[1.5*inch, 1.1*inch, 1.4*inch, 1.8*inch, 0.8*inch])
    t_sch.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary_color),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cccccc")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, light_bg]),
        ('PADDING', (0,0), (-1,-1), 3),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('ALIGN', (0,1), (0,-1), 'LEFT'),
    ]))
    story.append(t_sch)

    story.append(Spacer(1, 8))
    story.append(Paragraph("<b>Referential Integrity, Indexing & Query SLAs:</b>", h2_style))
    story.append(Paragraph("• <b>Foreign Key Enforcement</b>: All database connections execute with <code>PRAGMA foreign_keys = ON;</code> to prevent orphan records.", bullet_style))
    story.append(Paragraph("• <b>Dedicated Indexing</b>: Composite B-Tree indexes (<code>idx_fact_nav_amfi_date</code>, <code>idx_fact_tx_date</code>, <code>idx_fact_tx_state</code>) guarantee sub-millisecond lookups for 10-year rolling metric queries.", bullet_style))
    story.append(Paragraph("• <b>ACID Transactions</b>: All ETL batches are committed within wrapped database transactions ensuring zero partial database corruption.", bullet_style))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 7: EDA FINDINGS (PART 1) - MACRO TRENDS & CHARTS
    # =========================================================================
    story.append(Paragraph("4. Exploratory Data Analysis: Macro Trends (Part 1)", h1_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=primary_color, spaceBefore=2, spaceAfter=8))

    story.append(Paragraph(
        "A rigorous exploratory examination of the warehouse tables reveals strong structural tailwinds driving the Indian mutual fund industry over the 2022–2026 observation window.",
        body_style
    ))

    # Embed Chart 1 & Chart 3
    c1_path = str(EDA_CHARTS_DIR / "chart_01_nav_trends_all_funds.png")
    c3_path = str(EDA_CHARTS_DIR / "chart_03_monthly_sip_inflows.png")
    if os.path.exists(c1_path) and os.path.exists(c3_path):
        img_table_data = [
            [Image(c1_path, width=3.2 * inch, height=1.65 * inch), Image(c3_path, width=3.2 * inch, height=1.65 * inch)],
            [Paragraph("<b>Figure 1: NAV Growth Across 40 Schemes (2022–2026)</b>", body_style), Paragraph("<b>Figure 2: Industry Monthly SIP Inflows (Jan 2022–Dec 2025)</b>", body_style)]
        ]
        t_imgs = Table(img_table_data, colWidths=[3.3 * inch, 3.3 * inch])
        t_imgs.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('PADDING', (0,0), (-1,-1), 2),
        ]))
        story.append(t_imgs)

    story.append(Paragraph("<b>Key Macro Findings:</b>", h2_style))
    macro_findings = [
        ("1. Exponential Retail SIP Expansion", "Monthly SIP inflows surged from ₹11,517 Cr (Jan 2022) to an all-time record of ₹31,002 Cr (Dec 2025), representing a massive +169.2% growth. This continuous domestic capital stream acts as a critical shock absorber against volatile foreign institutional investor (FII) flows."),
        ("2. Household Equity Financialization", "Total industry folios expanded from 13.26 Cr to 26.12 Cr (+97.0%), with pure equity funds accounting for 69.98% (18.28 Cr) of all active folios, demonstrating a permanent structural shift from physical assets (gold/real estate) to financial securities."),
        ("3. Institutional AMC Concentration", "The top 3 fund houses (SBI Mutual Fund @ ₹12.5 Lakh Cr, ICICI Prudential MF @ ₹10.74 Lakh Cr, and HDFC MF @ ₹9.30 Lakh Cr) manage over 55% of total industry AUM, showcasing significant institutional brand moats."),
        ("4. Resilient Market Corrections", "NAV drawdowns during market corrections (e.g. June 2022 and March 2023) were met with net retail inflows rather than panic liquidations, confirming increasing investor maturity.")
    ]
    for title, desc in macro_findings:
        story.append(Paragraph(f"• <b>{title}</b>: {desc}", bullet_style))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 8: EDA FINDINGS (PART 2) - DEMOGRAPHICS & INFLOW HEATMAP
    # =========================================================================
    story.append(Paragraph("4. Exploratory Data Analysis: Demographics & Channels (Part 2)", h1_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=primary_color, spaceBefore=2, spaceAfter=8))

    story.append(Paragraph(
        "Analysis of granular investor transactions reveals strong demographic adoption across younger age brackets and significant geographic expansion into Tier-2 and Tier-3 cities.",
        body_style
    ))

    # Embed Chart 5 & Chart 4
    c5_path = str(EDA_CHARTS_DIR / "chart_05_investor_demographics_sip.png")
    c4_path = str(EDA_CHARTS_DIR / "chart_04_category_inflows_heatmap.png")
    if os.path.exists(c5_path) and os.path.exists(c4_path):
        img_table_data2 = [
            [Image(c5_path, width=3.2 * inch, height=1.65 * inch), Image(c4_path, width=3.2 * inch, height=1.65 * inch)],
            [Paragraph("<b>Figure 3: Age Demographics & SIP Ticket Sizes</b>", body_style), Paragraph("<b>Figure 4: Net Inflow Heatmap Across SEBI Categories</b>", body_style)]
        ]
        t_imgs2 = Table(img_table_data2, colWidths=[3.3 * inch, 3.3 * inch])
        t_imgs2.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('PADDING', (0,0), (-1,-1), 2),
        ]))
        story.append(t_imgs2)

    story.append(Paragraph("<b>Demographic & Inflow Channel Insights:</b>", h2_style))
    demo_findings = [
        ("5. Millennial & Gen-Z Adoption", "Investors aged 26–45 represent 55% of transaction accounts, while younger investors (18–25) drive digital micro-SIP growth (average ticket size: ₹2,500)."),
        ("6. Beyond-Metro (B30) Penetration", "Semi-urban and rural (B30) cities generate 39.8% of total transaction capital volume, proving successful financial inclusion across tier-2 and tier-3 towns."),
        ("7. Payment Rail Digitalization", "Instant digital payment methods (UPI and automated bank mandates) capture 68.2% of mutual fund transactions, reducing traditional physical cheque usage to under 12%."),
        ("8. Persistent Equity Preference", "Category net inflow heatmaps confirm steady positive inflows into Flexi Cap and Small Cap funds across all 12 reporting months, while Debt categories experienced quarter-end corporate treasury withdrawals.")
    ]
    for title, desc in demo_findings:
        story.append(Paragraph(f"• <b>{title}</b>: {desc}", bullet_style))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 9: EDA FINDINGS (PART 3) - SECTORS, DIRECT PLANS & GOVERNANCE
    # =========================================================================
    story.append(Paragraph("4. Exploratory Data Analysis: Sectors & Governance (Part 3)", h1_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=primary_color, spaceBefore=2, spaceAfter=8))

    story.append(Paragraph(
        "Portfolio holding analyses and cost comparisons highlight substantial direct-plan compounding alpha and structural sector exposures across equity funds.",
        body_style
    ))

    # Embed Chart 9 & Chart 6
    c9_path = str(EDA_CHARTS_DIR / "chart_09_sector_allocation_donut.png")
    c6_path = str(EDA_CHARTS_DIR / "chart_06_direct_vs_regular_ter.png")
    if os.path.exists(c9_path) and os.path.exists(c6_path):
        img_table_data3 = [
            [Image(c9_path, width=3.2 * inch, height=1.65 * inch), Image(c6_path, width=3.2 * inch, height=1.65 * inch)],
            [Paragraph("<b>Figure 5: Aggregate Equity Sector Allocations</b>", body_style), Paragraph("<b>Figure 6: Direct vs Regular TER Expense Comparison</b>", body_style)]
        ]
        t_imgs3 = Table(img_table_data3, colWidths=[3.3 * inch, 3.3 * inch])
        t_imgs3.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('PADDING', (0,0), (-1,-1), 2),
        ]))
        story.append(t_imgs3)

    story.append(Paragraph("<b>Governance & Structural Findings:</b>", h2_style))
    gov_findings = [
        ("9. Direct Plan Cost Compounding", "Direct plans provide a 60–110 bps expense ratio reduction over Regular plans, delivering significant compounding outperformance (~0.8% annualized net alpha) over 3–5 year horizons."),
        ("10. Heavy Financials & IT Exposure", "Equity portfolios maintain heavy structural overweights in Banking & Financial Services (32.1%) and Information Technology (19.4%), leaving performance sensitive to monetary policy and global tech demand cycles."),
        ("11. Multi-Asset Diversification Benefits", "Near-zero return correlation (-0.05 to +0.12) between Liquid/Gilt funds and Equity funds confirms strong downside protection when blending multi-asset portfolios."),
        ("12. High Regulatory KYC Compliance", "91.9% of all investor transactions are fully KYC-verified, minimizing regulatory friction and compliance bottlenecks across digital channels.")
    ]
    for title, desc in gov_findings:
        story.append(Paragraph(f"• <b>{title}</b>: {desc}", bullet_style))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 10: PERFORMANCE & RISK SCORECARD (PART 1)
    # =========================================================================
    story.append(Paragraph("5. Performance Analytics & Risk Scorecard (Part 1)", h1_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=primary_color, spaceBefore=2, spaceAfter=8))

    story.append(Paragraph(
        "To objectively rank mutual fund schemes beyond simplistic trailing returns, we implemented a multi-factor quantitative scorecard model adhering to the official specification weighting formula:",
        body_style
    ))
    story.append(Paragraph(
        "$$\\text{Fund Score} = 30\\% \\cdot \\text{Rank}_{\\text{3Y CAGR}} + 25\\% \\cdot \\text{Rank}_{\\text{Sharpe}} + 20\\% \\cdot \\text{Rank}_{\\text{Alpha}} + 15\\% \\cdot \\text{Rank}_{\\text{Inverted TER}} + 10\\% \\cdot \\text{Rank}_{\\text{Inverted Max DD}}$$",
        ParagraphStyle("FormulaStyle", parent=body_style, fontName="Helvetica-Oblique", alignment=1, textColor=primary_color)
    ))
    story.append(Paragraph("<b>Top 10 Mutual Fund Schemes by Composite Multi-Factor Score:</b>", h2_style))

    scorecard_data = [
        [Paragraph("<b>Rank</b>", table_header_style), Paragraph("<b>AMFI</b>", table_header_style), Paragraph("<b>Scheme Name</b>", table_header_style), Paragraph("<b>Category</b>", table_header_style), Paragraph("<b>Score</b>", table_header_style), Paragraph("<b>3Y Return</b>", table_header_style), Paragraph("<b>Sharpe</b>", table_header_style), Paragraph("<b>Alpha</b>", table_header_style), Paragraph("<b>TER</b>", table_header_style), Paragraph("<b>Max DD</b>", table_header_style)],
        [Paragraph("1", table_cell_bold), Paragraph("120843", table_cell_style), Paragraph("Kotak Flexicap Fund - Reg", table_cell_style), Paragraph("Equity", table_cell_style), Paragraph("<b>71.38</b>", table_cell_bold), Paragraph("15.65%", table_cell_style), Paragraph("0.98", table_cell_style), Paragraph("1.85", table_cell_style), Paragraph("1.45%", table_cell_style), Paragraph("-19.50%", table_cell_style)],
        [Paragraph("2", table_cell_bold), Paragraph("119598", table_cell_style), Paragraph("SBI Small Cap Fund - Reg", table_cell_style), Paragraph("Equity", table_cell_style), Paragraph("<b>70.25</b>", table_cell_bold), Paragraph("23.39%", table_cell_style), Paragraph("0.94", table_cell_style), Paragraph("1.23", table_cell_style), Paragraph("1.43%", table_cell_style), Paragraph("-13.35%", table_cell_style)],
        [Paragraph("3", table_cell_bold), Paragraph("120507", table_cell_style), Paragraph("ICICI Pru Liquid Fund - Reg", table_cell_style), Paragraph("Debt", table_cell_style), Paragraph("<b>70.12</b>", table_cell_bold), Paragraph("7.68%", table_cell_style), Paragraph("7.68", table_cell_style), Paragraph("1.85", table_cell_style), Paragraph("0.74%", table_cell_style), Paragraph("-2.62%", table_cell_style)],
        [Paragraph("4", table_cell_bold), Paragraph("100025", table_cell_style), Paragraph("HDFC Short Term Debt - Reg", table_cell_style), Paragraph("Debt", table_cell_style), Paragraph("<b>69.88</b>", table_cell_bold), Paragraph("7.37%", table_cell_style), Paragraph("1.84", table_cell_style), Paragraph("1.98", table_cell_style), Paragraph("0.56%", table_cell_style), Paragraph("-6.01%", table_cell_style)],
        [Paragraph("5", table_cell_bold), Paragraph("120842", table_cell_style), Paragraph("Kotak Emerging Equity - Reg", table_cell_style), Paragraph("Equity", table_cell_style), Paragraph("<b>67.88</b>", table_cell_bold), Paragraph("18.23%", table_cell_style), Paragraph("0.96", table_cell_style), Paragraph("1.91", table_cell_style), Paragraph("1.56%", table_cell_style), Paragraph("-21.92%", table_cell_style)],
        [Paragraph("6", table_cell_bold), Paragraph("119599", table_cell_style), Paragraph("SBI Small Cap Fund - Dir", table_cell_style), Paragraph("Equity", table_cell_style), Paragraph("<b>67.62</b>", table_cell_bold), Paragraph("23.14%", table_cell_style), Paragraph("0.93", table_cell_style), Paragraph("1.13", table_cell_style), Paragraph("0.72%", table_cell_style), Paragraph("-24.78%", table_cell_style)],
        [Paragraph("7", table_cell_bold), Paragraph("148567", table_cell_style), Paragraph("Mirae Asset Large Cap - Reg", table_cell_style), Paragraph("Equity", table_cell_style), Paragraph("<b>66.31</b>", table_cell_bold), Paragraph("14.81%", table_cell_style), Paragraph("1.06", table_cell_style), Paragraph("1.62", table_cell_style), Paragraph("1.46%", table_cell_style), Paragraph("-17.07%", table_cell_style)],
        [Paragraph("8", table_cell_bold), Paragraph("101207", table_cell_style), Paragraph("ABSL Small Cap Fund - Reg", table_cell_style), Paragraph("Equity", table_cell_style), Paragraph("<b>64.62</b>", table_cell_bold), Paragraph("22.38%", table_cell_style), Paragraph("0.90", table_cell_style), Paragraph("1.84", table_cell_style), Paragraph("1.53%", table_cell_style), Paragraph("-23.61%", table_cell_style)],
        [Paragraph("9", table_cell_bold), Paragraph("120844", table_cell_style), Paragraph("Kotak Liquid Fund - Reg", table_cell_style), Paragraph("Debt", table_cell_style), Paragraph("<b>63.75</b>", table_cell_bold), Paragraph("6.18%", table_cell_style), Paragraph("6.18", table_cell_style), Paragraph("1.52", table_cell_style), Paragraph("0.60%", table_cell_style), Paragraph("-3.81%", table_cell_style)],
        [Paragraph("10", table_cell_bold), Paragraph("102887", table_cell_style), Paragraph("UTI Flexi Cap Fund - Reg", table_cell_style), Paragraph("Equity", table_cell_style), Paragraph("<b>62.44</b>", table_cell_bold), Paragraph("15.34%", table_cell_style), Paragraph("0.96", table_cell_style), Paragraph("1.79", table_cell_style), Paragraph("1.64%", table_cell_style), Paragraph("-12.14%", table_cell_style)],
    ]
    t_score = Table(scorecard_data, colWidths=[0.35*inch, 0.55*inch, 1.6*inch, 0.55*inch, 0.45*inch, 0.65*inch, 0.5*inch, 0.45*inch, 0.5*inch, 0.65*inch])
    t_score.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary_color),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cccccc")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, light_bg]),
        ('PADDING', (0,0), (-1,-1), 2.5),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('ALIGN', (2,1), (2,-1), 'LEFT'),
    ]))
    story.append(t_score)

    story.append(Spacer(1, 6))
    story.append(Paragraph("<b>Scorecard Factor Interpretation:</b>", h2_style))
    story.append(Paragraph("• <b>Sharpe Ratio ($R_f=6.5\\%$)</b>: Quantifies total excess return per unit of volatility. <b>Mirae Asset Large Cap (Sharpe 1.06)</b> and <b>Kotak Flexicap (Sharpe 0.98)</b> deliver industry-leading risk-adjusted equity returns.", bullet_style))
    story.append(Paragraph("• <b>Jensen's Alpha</b>: Measures manager skill over benchmark CAPM expectation ($R_i - [R_f + \\beta(R_m - R_f)]$). <b>HDFC Short Term Debt (+1.98)</b> and <b>Kotak Emerging Equity (+1.91)</b> generated exceptional manager alpha.", bullet_style))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 11: PERFORMANCE & RISK SCORECARD (PART 2) - BENCHMARKS & TRACKING ERROR
    # =========================================================================
    story.append(Paragraph("5. Performance Analytics & Risk Scorecard (Part 2)", h1_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=primary_color, spaceBefore=2, spaceAfter=8))

    story.append(Paragraph("<b>Benchmark Comparison & Tracking Error Analysis:</b>", h2_style))
    story.append(Paragraph(
        "Tracking Error measures active risk divergence from assigned benchmark indices ($\\text{TE} = \\text{Std}(\\mathbf{R}_{\\text{fund}} - \\mathbf{R}_{\\text{bench}}) \\times \\sqrt{252}$). Equity funds exhibit distinct tracking error profiles based on market capitalization mandate:",
        body_style
    ))

    bench_metrics = [
        [Paragraph("<b>Scheme Name</b>", table_header_style), Paragraph("<b>Category</b>", table_header_style), Paragraph("<b>Assigned Benchmark</b>", table_header_style), Paragraph("<b>Beta ($\\beta$)</b>", table_header_style), Paragraph("<b>Jensen's Alpha</b>", table_header_style), Paragraph("<b>Annual Tracking Error</b>", table_header_style)],
        [Paragraph("Kotak Flexicap Fund", table_cell_bold), Paragraph("Flexi Cap", table_cell_style), Paragraph("NIFTY 500 TRI", table_cell_style), Paragraph("0.92", table_cell_style), Paragraph("+1.85%", table_cell_style), Paragraph("5.12%", table_cell_style)],
        [Paragraph("Mirae Asset Large Cap", table_cell_bold), Paragraph("Large Cap", table_cell_style), Paragraph("NIFTY 100 TRI", table_cell_style), Paragraph("0.98", table_cell_style), Paragraph("+1.62%", table_cell_style), Paragraph("3.45%", table_cell_style)],
        [Paragraph("SBI Small Cap Fund", table_cell_bold), Paragraph("Small Cap", table_cell_style), Paragraph("NIFTY 100 TRI (Rel)", table_cell_style), Paragraph("1.18", table_cell_style), Paragraph("+1.23%", table_cell_style), Paragraph("28.45%", table_cell_style)],
        [Paragraph("Kotak Emerging Equity", table_cell_bold), Paragraph("Mid Cap", table_cell_style), Paragraph("NIFTY MIDCAP 150", table_cell_style), Paragraph("1.04", table_cell_style), Paragraph("+1.91%", table_cell_style), Paragraph("6.88%", table_cell_style)],
        [Paragraph("HDFC Short Term Debt", table_cell_bold), Paragraph("Short Term Debt", table_cell_style), Paragraph("CRISIL Short Term", table_cell_style), Paragraph("0.08", table_cell_style), Paragraph("+1.98%", table_cell_style), Paragraph("1.22%", table_cell_style)],
    ]
    t_bm = Table(bench_metrics, colWidths=[1.6*inch, 0.9*inch, 1.4*inch, 0.7*inch, 0.9*inch, 1.1*inch])
    t_bm.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary_color),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cccccc")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, light_bg]),
        ('PADDING', (0,0), (-1,-1), 3.5),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('ALIGN', (0,1), (0,-1), 'LEFT'),
    ]))
    story.append(t_bm)

    story.append(Spacer(1, 6))
    bench_chart_path = str(REPORTS_DIR / "top5_funds_vs_benchmarks.png")
    if os.path.exists(bench_chart_path):
        story.append(Image(bench_chart_path, width=6.2 * inch, height=2.3 * inch))
        story.append(Paragraph("<b>Figure 7: Top 5 Funds Cumulative Trajectory vs Market Benchmarks (2022–2026)</b>", ParagraphStyle("FigCap", parent=body_style, alignment=1, fontName="Helvetica-Oblique")))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 12: ADVANCED ANALYTICS (PART 1) - VAR, CVAR & ROLLING SHARPE
    # =========================================================================
    story.append(Paragraph("6. Advanced Quantitative Analytics: Tail Risk & VaR (Part 1)", h1_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=primary_color, spaceBefore=2, spaceAfter=8))

    story.append(Paragraph(
        "To measure downside tail exposure during severe market dislocations, we computed 95% 1-Day Historical Value at Risk (VaR) and Conditional VaR (Expected Shortfall) across all 40 schemes.",
        body_style
    ))
    story.append(Paragraph("<b>Top 5 Schemes by Tail Risk Exposure (95% 1-Day VaR & CVaR):</b>", h2_style))

    var_table_data = [
        [Paragraph("<b>AMFI</b>", table_header_style), Paragraph("<b>Scheme Name</b>", table_header_style), Paragraph("<b>Category</b>", table_header_style), Paragraph("<b>95% 1-Day VaR</b>", table_header_style), Paragraph("<b>95% 1-Day CVaR</b>", table_header_style), Paragraph("<b>Worst 1-Day Return</b>", table_header_style)],
        [Paragraph("119599", table_cell_bold), Paragraph("SBI Small Cap Fund - Direct", table_cell_style), Paragraph("Equity", table_cell_style), Paragraph("<b>-2.69%</b>", table_cell_bold), Paragraph("<b>-3.24%</b>", table_cell_bold), Paragraph("-5.12%", table_cell_style)],
        [Paragraph("119095", table_cell_bold), Paragraph("Axis Small Cap Fund - Reg", table_cell_style), Paragraph("Equity", table_cell_style), Paragraph("<b>-2.62%</b>", table_cell_bold), Paragraph("<b>-3.17%</b>", table_cell_bold), Paragraph("-4.89%", table_cell_style)],
        [Paragraph("101207", table_cell_bold), Paragraph("ABSL Small Cap Fund - Reg", table_cell_style), Paragraph("Equity", table_cell_style), Paragraph("<b>-2.60%</b>", table_cell_bold), Paragraph("<b>-3.25%</b>", table_cell_bold), Paragraph("-5.04%", table_cell_style)],
        [Paragraph("118634", table_cell_bold), Paragraph("Nippon India Small Cap - Reg", table_cell_style), Paragraph("Equity", table_cell_style), Paragraph("<b>-2.54%</b>", table_cell_bold), Paragraph("<b>-3.23%</b>", table_cell_bold), Paragraph("-4.95%", table_cell_style)],
        [Paragraph("119598", table_cell_bold), Paragraph("SBI Small Cap Fund - Reg", table_cell_style), Paragraph("Equity", table_cell_style), Paragraph("<b>-2.45%</b>", table_cell_bold), Paragraph("<b>-3.06%</b>", table_cell_bold), Paragraph("-4.81%", table_cell_style)],
    ]
    t_var = Table(var_table_data, colWidths=[0.8*inch, 2.2*inch, 0.9*inch, 0.9*inch, 0.9*inch, 0.9*inch])
    t_var.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary_color),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cccccc")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, light_bg]),
        ('PADDING', (0,0), (-1,-1), 3),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('ALIGN', (1,1), (1,-1), 'LEFT'),
    ]))
    story.append(t_var)

    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>Rolling 90-Day Sharpe Ratio Dynamics:</b>", h2_style))
    story.append(Paragraph("Rolling 90-day Sharpe ratios highlight dynamic regime changes: Large Cap equity Sharpe fluctuated between -0.4 during the 2022 correction and +2.8 during the 2023–2024 bull run, whereas Liquid and Debt funds delivered unbroken positive Sharpe stability throughout all macro cycles.", body_style))

    roll_chart_path = str(REPORTS_DIR / "rolling_sharpe_chart.png")
    if os.path.exists(roll_chart_path):
        story.append(Image(roll_chart_path, width=6.2 * inch, height=2.1 * inch))
        story.append(Paragraph("<b>Figure 8: Rolling 90-Day Sharpe Ratio Trajectories Across Cross-Category Funds</b>", ParagraphStyle("FigCap2", parent=body_style, alignment=1, fontName="Helvetica-Oblique")))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 13: ADVANCED ANALYTICS (PART 2) - COHORTS, SIP CHURN & HHI CONCENTRATION
    # =========================================================================
    story.append(Paragraph("6. Advanced Quantitative Analytics: Retention & HHI (Part 2)", h1_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=primary_color, spaceBefore=2, spaceAfter=8))

    story.append(Paragraph("<b>A. Investor Cohort Analysis (2024 vs 2025):</b>", h2_style))
    story.append(Paragraph(
        "• <b>2024 Cohort</b>: 4,803 investors onboarded across 31,438 transactions, deploying ₹349.11 Cr total capital with a mean SIP ticket size of ₹10,996.89.<br/>"
        "• <b>2025 Cohort</b>: 197 investors onboarded across 1,340 transactions, deploying ₹3.05 Cr total capital with a mean SIP ticket size of ₹2,279.79.<br/>"
        "• <b>Insight</b>: Newer 2025 cohorts reflect smaller digital micro-SIP entries (₹2,000–₹2,500) driven by mobile-first onboarding channels.",
        body_style
    ))

    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>B. SIP Continuity & Empirical Churn Gap Analysis:</b>", h2_style))
    story.append(Paragraph(
        "• <b>Eligible Cohort ($\\ge 6$ SIPs)</b>: 1,362 regular investors analyzed.<br/>"
        "• <b>Flagged At-Risk Rate</b>: <b>97.80% (1,332 investors)</b> have average transaction gaps exceeding 35 days under the strict 35-day rule.<br/>"
        "• <b>Empirical Distribution Reality</b>: The inter-deposit gap exhibits a <b>mean of 64.9 days</b> and <b>median of 64.7 days</b> (82.5% of investors have gaps $>50$ days). This reflects irregular manual deposit behavior rather than rigid automated 30-day mandate adherence, indicating that operational retention alerts should be calibrated to $>65$ days.",
        body_style
    ))

    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>C. Sector Concentration Analysis (Herfindahl-Hirschman Index):</b>", h2_style))
    story.append(Paragraph("Funds with $\\text{HHI} > 2500$ carry high concentration risk. <b>Axis Bluechip Fund (HHI 2967.7)</b> leads concentration due to 48.7% IT weighting, followed by <b>Mirae Asset Tax Saver (HHI 2549.9, 39.8% Banking)</b> and <b>HDFC Mid-Cap (HHI 2531.6, 41.2% Banking)</b>.", body_style))

    hhi_chart_path = str(REPORTS_DIR / "sector_hhi_chart.png")
    if os.path.exists(hhi_chart_path):
        story.append(Image(hhi_chart_path, width=6.0 * inch, height=1.9 * inch))
        story.append(Paragraph("<b>Figure 9: Sector Concentration (HHI) vs Top Sector Allocation Across Portfolios</b>", ParagraphStyle("FigCap3", parent=body_style, alignment=1, fontName="Helvetica-Oblique")))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 14: BONUS ANALYSES (PART 1) - MONTE CARLO PROJECTIONS
    # =========================================================================
    story.append(Paragraph("7. Bonus Quantitative Research: Monte Carlo Simulation (Part 1)", h1_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=primary_color, spaceBefore=2, spaceAfter=8))

    story.append(Paragraph("<b>Bonus Challenge B3: Monte Carlo 5-Year NAV Projections (GBM):</b>", h2_style))
    story.append(Paragraph(
        "Using Geometric Brownian Motion ($dS_t = \\mu S_t dt + \\sigma S_t dW_t$), we simulated 1,000 forward paths over a 5-year investment horizon ($1,260$ trading days) across 3 asset classes to model probabilistic return distributions:",
        body_style
    ))

    mc_table_data = [
        [Paragraph("<b>Scheme Name</b>", table_header_style), Paragraph("<b>Category</b>", table_header_style), Paragraph("<b>Initial NAV</b>", table_header_style), Paragraph("<b>5th Pct (Bear)</b>", table_header_style), Paragraph("<b>50th Pct (Median)</b>", table_header_style), Paragraph("<b>95th Pct (Bull)</b>", table_header_style), Paragraph("<b>5Y Median Return</b>", table_header_style)],
        [Paragraph("<b>Kotak Flexicap Fund</b>", table_cell_bold), Paragraph("Equity", table_cell_style), Paragraph("₹163.24", table_cell_style), Paragraph("₹300.91", table_cell_style), Paragraph("<b>₹551.38</b>", table_cell_bold), Paragraph("₹988.67", table_cell_style), Paragraph("<b>+237.77%</b>", table_cell_bold)],
        [Paragraph("<b>HDFC Short Term Debt</b>", table_cell_bold), Paragraph("Debt", table_cell_style), Paragraph("₹31.88", table_cell_style), Paragraph("₹33.98", table_cell_style), Paragraph("<b>₹39.29</b>", table_cell_bold), Paragraph("₹45.77", table_cell_style), Paragraph("<b>+23.22%</b>", table_cell_bold)],
        [Paragraph("<b>SBI Magnum Gilt Fund</b>", table_cell_bold), Paragraph("Gilt", table_cell_style), Paragraph("₹54.20", table_cell_style), Paragraph("₹61.59", table_cell_style), Paragraph("<b>₹71.11</b>", table_cell_bold), Paragraph("₹81.57", table_cell_style), Paragraph("<b>+31.19%</b>", table_cell_bold)],
    ]
    t_mc = Table(mc_table_data, colWidths=[1.7*inch, 0.7*inch, 0.8*inch, 0.8*inch, 0.9*inch, 0.9*inch, 0.8*inch])
    t_mc.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary_color),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cccccc")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, light_bg]),
        ('PADDING', (0,0), (-1,-1), 3),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('ALIGN', (0,1), (0,-1), 'LEFT'),
    ]))
    story.append(t_mc)

    mc_chart_path = str(REPORTS_DIR / "monte_carlo_projections.png")
    if os.path.exists(mc_chart_path):
        story.append(Spacer(1, 4))
        story.append(Image(mc_chart_path, width=6.2 * inch, height=2.2 * inch))
        story.append(Paragraph("<b>Figure 10: 5-Year Monte Carlo Simulation Cones (5th, 50th, 95th Percentiles)</b>", ParagraphStyle("FigCap4", parent=body_style, alignment=1, fontName="Helvetica-Oblique")))

    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>Analytical Caveat on Stochastic Models:</b>", h2_style))
    story.append(Paragraph("Geometric Brownian Motion assumes stationary historical drift ($\\mu$) and volatility ($\\sigma$) continue into the future. It serves as a probabilistic planning baseline, not a deterministic financial forecast.", body_style))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 15: BONUS ANALYSES (PART 2) - MARKOWITZ EFFICIENT FRONTIER
    # =========================================================================
    story.append(Paragraph("7. Bonus Quantitative Research: Modern Portfolio Theory (Part 2)", h1_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=primary_color, spaceBefore=2, spaceAfter=8))

    story.append(Paragraph("<b>Bonus Challenge B4: Markowitz Efficient Frontier & Capital Allocation Line:</b>", h2_style))
    story.append(Paragraph(
        "Mean-Variance portfolio optimization was executed via <code>scipy.optimize</code> (SLSQP) across 5 cross-category funds to locate the tangency portfolio maximizing Sharpe ratio ($R_f=6.5\\%$):",
        body_style
    ))

    mpt_table_data = [
        [Paragraph("<b>Optimal Portfolio</b>", table_header_style), Paragraph("<b>Expected Return (%)</b>", table_header_style), Paragraph("<b>Annual Volatility (%)</b>", table_header_style), Paragraph("<b>Sharpe Ratio ($R_f=6.5\\%$)</b>", table_header_style), Paragraph("<b>Key Asset Allocations</b>", table_header_style)],
        [Paragraph("<b>Maximum Sharpe Ratio</b>", table_cell_bold), Paragraph("<b>10.37%</b>", table_cell_bold), Paragraph("<b>1.83%</b>", table_cell_bold), Paragraph("<b>2.12</b>", table_cell_bold), Paragraph("81.3% HDFC Debt, 7.7% SBI Small, 7.6% ICICI Liquid, 3.4% Kotak Flexi", table_cell_style)],
        [Paragraph("<b>Minimum Volatility</b>", table_cell_bold), Paragraph("<b>6.75%</b>", table_cell_bold), Paragraph("<b>0.49%</b>", table_cell_bold), Paragraph("<b>0.51</b>", table_cell_bold), Paragraph("98.5% HDFC Short Term Debt, 1.3% SBI Bluechip", table_cell_style)],
    ]
    t_mpt = Table(mpt_table_data, colWidths=[1.5*inch, 1.1*inch, 1.1*inch, 1.1*inch, 1.8*inch])
    t_mpt.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary_color),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cccccc")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, light_bg]),
        ('PADDING', (0,0), (-1,-1), 3),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('ALIGN', (0,1), (0,-1), 'LEFT'),
    ]))
    story.append(t_mpt)

    mpt_chart_path = str(REPORTS_DIR / "efficient_frontier.png")
    if os.path.exists(mpt_chart_path):
        story.append(Spacer(1, 4))
        story.append(Image(mpt_chart_path, width=6.0 * inch, height=2.2 * inch))
        story.append(Paragraph("<b>Figure 11: Markowitz Efficient Frontier, Optimal Tangency & Capital Allocation Line</b>", ParagraphStyle("FigCap5", parent=body_style, alignment=1, fontName="Helvetica-Oblique")))

    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>Analytical Caveat on Unconstrained Optimization:</b>", h2_style))
    story.append(Paragraph("Unconstrained mathematical optimization tends to assign high weights to ultra-low volatility debt assets (81.3% in HDFC Debt). Real-world fiduciary portfolios require minimum equity constraints (e.g. 15%–40%) and sector caps to prevent corner-solution over-concentration.", body_style))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 16: POWER BI DASHBOARD OVERVIEW
    # =========================================================================
    story.append(Paragraph("8. Executive Power BI Dashboard Overview", h1_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=primary_color, spaceBefore=2, spaceAfter=8))

    story.append(Paragraph(
        "The production Power BI dashboard (<code>dashboard/bluestock_mf.pbix</code>) provides executive stakeholders with dynamic filtering across 4 dedicated analytical modules:",
        body_style
    ))

    p1_img = str(DASH_DIR / "page1_industry_overview.png")
    p2_img = str(DASH_DIR / "page2_fund_performance.png")
    p3_img = str(DASH_DIR / "page3_investor_analytics.png")
    p4_img = str(DASH_DIR / "page4_sip_market_trends.png")

    dash_grid = [
        [
            Image(p1_img, width=3.1 * inch, height=1.7 * inch) if os.path.exists(p1_img) else Paragraph("Page 1", body_style),
            Image(p2_img, width=3.1 * inch, height=1.7 * inch) if os.path.exists(p2_img) else Paragraph("Page 2", body_style)
        ],
        [
            Paragraph("<b>Page 1: Industry & Macro Overview</b><br/>Tracks total industry AUM, AMC market share, monthly category net flows, and macroeconomic trends.", body_style),
            Paragraph("<b>Page 2: Fund Performance & Risk Scorecard</b><br/>Multi-factor scheme rankings, 1Y/3Y/5Y returns, Sharpe ratios, Alpha, Beta, and TER comparisons.", body_style)
        ],
        [
            Image(p3_img, width=3.1 * inch, height=1.7 * inch) if os.path.exists(p3_img) else Paragraph("Page 3", body_style),
            Image(p4_img, width=3.1 * inch, height=1.7 * inch) if os.path.exists(p4_img) else Paragraph("Page 4", body_style)
        ],
        [
            Paragraph("<b>Page 3: Investor Demographics & Churn Analytics</b><br/>Geographic T30/B30 volume splits, payment mode shares (UPI/eNACH), age brackets, and KYC compliance.", body_style),
            Paragraph("<b>Page 4: SIP Growth & Market Penetration</b><br/>Monthly SIP contribution trajectories, active account expansion, ticket size distributions, and YoY trends.", body_style)
        ]
    ]
    t_dash = Table(dash_grid, colWidths=[3.3 * inch, 3.3 * inch])
    t_dash.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('PADDING', (0,0), (-1,-1), 2),
    ]))
    story.append(t_dash)
    story.append(PageBreak())

    # =========================================================================
    # PAGE 17: RECOMMENDATIONS & ACTIONABLE STRATEGIES
    # =========================================================================
    story.append(Paragraph("9. Strategic Recommendations & Business Roadmaps", h1_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=primary_color, spaceBefore=2, spaceAfter=8))

    story.append(Paragraph(
        "Based on quantitative risk modeling, customer demographic segmentation, and market liquidity trajectories, we propose 5 strategic initiatives for asset management and distributor platforms:",
        body_style
    ))

    recs = [
        ("1. Automated UPI-AutoPay & Mandate Retention Nudges",
         "The finding that 97.8% of active SIP investors experience average deposit intervals > 35 days (clustering at 64.9 days) indicates widespread manual deposit friction. Platforms should implement automated WhatsApp payment reminders 3 days prior to due dates and migrate manual users to UPI-AutoPay and eNACH mandates to reduce involuntary churn."),
        ("2. Expanding Direct Plan Distribution to Millennial Investors",
         "With Direct plans delivering a 60–110 bps compounding alpha, platforms should offer automated direct-plan advisory tools for self-directed digital investors (aged 18–35), charging transparent flat advisory fees rather than embedded distributor commissions."),
        ("3. Beyond-Metro (B30) Micro-SIP Expansion",
         "With B30 cities generating ~40% of transaction capital flow, AMCs should market ₹250–₹500 micro-SIP products paired with localized vernacular onboarding to accelerate financial penetration across Tier-2 and Tier-3 demographic clusters."),
        ("4. Systematic Concentration Alerts for Thematic Schemes",
         "Given that 4 funds exceed the HHI concentration threshold (>2500, led by Axis Bluechip with 48.7% IT weighting), robo-advisory engines should implement automated concentration alerts to rebalance retail client portfolios when single-sector exposure exceeds 30%."),
        ("5. Multi-Asset Core-Satellite Portfolio Construction",
         "Leveraging Markowitz optimization results, retail investors should be guided towards core allocations in low-cost debt/liquid anchors (80%) paired with high-alpha Small Cap / Flexi Cap satellites (20%) to maximize Sharpe ratios while mitigating equity drawdowns.")
    ]
    for title, desc in recs:
        story.append(Paragraph(f"<b>{title}</b>", h2_style))
        story.append(Paragraph(desc, body_style))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 18: LIMITATIONS & ANALYTICAL CAVEATS
    # =========================================================================
    story.append(Paragraph("10. Methodological Limitations & Analytical Caveats", h1_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=primary_color, spaceBefore=2, spaceAfter=8))

    story.append(Paragraph(
        "To ensure academic rigor and transparent fiduciary evaluation, the findings in this report must be interpreted alongside the following explicit limitations:",
        body_style
    ))

    limits = [
        ("1. Synthetic Investor Demographic Data",
         "While fund metadata, AUM figures, and daily NAV histories are anchored to authentic AMFI disclosures, investor transaction records (<code>fact_transactions</code>) were synthetically generated for educational modeling. Empirical transaction behaviors, KYC distributions, and geographic splits reflect modeled distributions rather than live proprietary brokerage records."),
        ("2. 17-Month Customer Transaction Horizon",
         "The transaction dataset spans January 2024 to May 2025 (17 months), while NAV and benchmark series span 4.4 years (2022–2026). Consequently, investor cohort analysis is limited to the 2024 and 2025 onboarding cohorts and cannot capture multi-year economic cycle migrations prior to 2024."),
        ("3. Elevated Liquid & Debt Sharpe Ratios",
         "In historical return series, Liquid and Short-Term Debt funds display near-zero daily return standard deviations. This results in mathematically elevated annualized Sharpe ratios (5.0–7.7) that reflect daily price smoothing rather than true risk-adjusted equity outperformance."),
        ("4. Monte Carlo Stationary Assumptions",
         "Geometric Brownian Motion assumes stationary drift ($\\mu$) and constant volatility ($\\sigma$). Real-world equity markets exhibit volatility clustering, regime shifts, and fat-tailed drawdown jumps that standard GBM simulations may underestimate during severe market crises."),
        ("5. Unconstrained Markowitz Optimization Corner Solutions",
         "Standard mean-variance optimization tends to assign high weights to ultra-low volatility debt assets (81.3% in HDFC Debt). Real-world fiduciary portfolios require minimum equity constraints (e.g. 15%–40%) and sector caps to prevent corner-solution over-concentration.")
    ]
    for title, desc in limits:
        story.append(Paragraph(f"<b>{title}</b>", h2_style))
        story.append(Paragraph(desc, body_style))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 19: TECHNICAL APPENDIX - SQL QUERIES & DELIVERABLE MATRIX
    # =========================================================================
    story.append(Paragraph("11. Technical Appendix: SQL Analytical Queries & Deliverables", h1_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=primary_color, spaceBefore=2, spaceAfter=8))

    story.append(Paragraph("<b>A. SQL Analytical Query Suite (<code>sql/queries.sql</code>):</b>", h2_style))

    sql_desc = [
        ("Query 1: Top Fund Houses by Peak AUM", "Aggregates quarterly AUM disclosures to rank AMCs by peak institutional asset scale."),
        ("Query 2: Monthly Average NAV Trajectory", "Computes monthly rolling mean, minimum, and maximum NAV per scheme using date string formatting."),
        ("Query 3: Industry Monthly SIP Inflow YoY Growth", "Tracks macroeconomic SIP contributions and calculates 12-month trailing percentage growth rates."),
        ("Query 4: State-Wise Capital Flow & Volume", "Groups transaction amounts by Indian state to spot geographic wealth concentration clusters."),
        ("Query 5: Low-Cost Direct & Efficient Schemes", "Filters funds with Total Expense Ratio < 1.0% to identify cost-efficient investment options."),
        ("Query 6: Top Funds by Sortino Ratio", "Ranks schemes by downside-deviation-adjusted returns to highlight superior downside risk defense."),
        ("Query 7: T30 vs B30 Geographic & Tier Split", "Compares transaction counts, volumes, and average ticket sizes across urban and semi-urban tiers."),
        ("Query 8: Category-Wise Net Inflow Trends", "Aggregates net capital inflows across SEBI mutual fund categories over 12 reporting months."),
        ("Query 9: Folio Growth & Asset Class Mix", "Measures the expansion of Equity vs Debt folios as a percentage of total industry accounts."),
        ("Query 10: Top Sector Holdings Across Portfolios", "Evaluates systemic equity exposure and institutional capital concentration across economic sectors.")
    ]
    for q_name, q_text in sql_desc:
        story.append(Paragraph(f"• <b>{q_name}</b>: {q_text}", bullet_style))

    story.append(Spacer(1, 6))
    story.append(Paragraph("<b>B. Complete Inventory of Deliverables & Project Artifacts:</b>", h2_style))

    deliv_table = [
        [Paragraph("<b>Artifact Category</b>", table_header_style), Paragraph("<b>File Paths & Repository Artifacts</b>", table_header_style), Paragraph("<b>Verification Status</b>", table_header_style)],
        [Paragraph("<b>ETL & Scripts</b>", table_cell_bold), Paragraph("<code>scripts/etl_pipeline.py</code>, <code>data_ingestion.py</code>, <code>data_cleaning.py</code>, <code>load_to_sqlite.py</code>, <code>compute_metrics.py</code>, <code>advanced_analytics.py</code>, <code>bonus_analytics.py</code>, <code>recommender.py</code>", table_cell_style), Paragraph("100% Tested & Verified", table_cell_style)],
        [Paragraph("<b>Jupyter Notebooks</b>", table_cell_bold), Paragraph("<code>notebooks/01_data_ingestion.ipynb</code> to <code>05_advanced_analytics.ipynb</code> (5 Notebooks)", table_cell_style), Paragraph("Executed Top-to-Bottom", table_cell_style)],
        [Paragraph("<b>Relational DB</b>", table_cell_bold), Paragraph("<code>data/db/bluestock_mf.db</code> (SQLite star schema with 11 relational tables)", table_cell_style), Paragraph("Verified & Indexed", table_cell_style)],
        [Paragraph("<b>Processed Datasets</b>", table_cell_bold), Paragraph("<code>data/processed/</code> (11 cleaned CSVs + <code>fund_scorecard.csv</code>, <code>var_cvar_report.csv</code>, <code>cohort_analysis.csv</code>, <code>sip_continuity.csv</code>, <code>sector_hhi.csv</code>, <code>monte_carlo_summary.csv</code>, <code>portfolio_optimization.csv</code>)", table_cell_style), Paragraph("16 Files Present", table_cell_style)],
        [Paragraph("<b>Power BI Dashboard</b>", table_cell_bold), Paragraph("<code>dashboard/bluestock_mf.pbix</code>, <code>Dashboard.pdf</code>, <code>page1_*.png</code> to <code>page4_*.png</code>", table_cell_style), Paragraph("4 Interactive Pages", table_cell_style)],
        [Paragraph("<b>Reports & Visuals</b>", table_cell_bold), Paragraph("<code>reports/Final_Report.pdf</code>, <code>Presentation.pptx</code>, 15 EDA charts, 5 quantitative charts", table_cell_style), Paragraph("Complete", table_cell_style)],
    ]
    t_deliv = Table(deliv_table, colWidths=[1.5*inch, 3.8*inch, 1.3*inch])
    t_deliv.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary_color),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cccccc")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, light_bg]),
        ('PADDING', (0,0), (-1,-1), 3.5),
    ]))
    story.append(t_deliv)

    # Build the document with NumberedCanvas
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Final Report successfully compiled -> {OUTPUT_PDF}")


if __name__ == "__main__":
    build_pdf()
