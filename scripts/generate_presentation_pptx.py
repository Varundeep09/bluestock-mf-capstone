"""
Day 7 Part 2: Final Presentation Generator (Bluestock_MF_Presentation.pptx)
Produces reports/Bluestock_MF_Presentation.pptx with exactly 12 structured slides,
matching the Power BI dashboard palette, embedded high-resolution charts/screenshots,
and clean, modern typography.
"""

from pathlib import Path
import os
import pptx
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.dml.color import RGBColor

PROJECT_ROOT = Path(__file__).resolve().parent.parent
REPORTS_DIR = PROJECT_ROOT / "reports"
EDA_CHARTS_DIR = REPORTS_DIR / "eda_charts"
DASH_DIR = PROJECT_ROOT / "dashboard"
OUTPUT_PPTX = REPORTS_DIR / "Bluestock_MF_Presentation.pptx"

# Color Palette Definitions (Consistent with Power BI / Report)
COLOR_NAVY_DARK  = RGBColor(29, 53, 87)     # #1D3557 - Primary Corporate
COLOR_TEAL_BLUE  = RGBColor(69, 123, 157)   # #457B9D - Secondary Blue
COLOR_ACCENT_RED = RGBColor(230, 57, 70)    # #E63946 - Accent / Highlights
COLOR_DARK_TEXT  = RGBColor(43, 45, 66)     # #2B2D42 - Dark Neutral Text
COLOR_MUTED_TEXT = RGBColor(108, 117, 125)  # #6C757D - Muted Gray
COLOR_LIGHT_BG   = RGBColor(248, 249, 250)  # #F8F9FA - Card Background
COLOR_WHITE      = RGBColor(255, 255, 255)  # #FFFFFF - White
COLOR_BORDER     = RGBColor(220, 224, 230)  # #DCE0E6 - Card Border
COLOR_GREEN_BG   = RGBColor(232, 245, 233)  # #E8F5E9 - Highlight Green
COLOR_GREEN_TEXT = RGBColor(27, 94, 32)     # #1B5E20 - Forest Green
COLOR_CARD_SHADOW= RGBColor(235, 238, 242)  # Subtle shadow tone


def create_slide(prs, bg_color=COLOR_WHITE):
    """Creates a blank slide with a custom solid background."""
    blank_layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(blank_layout)
    
    # Background shape
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    bg.fill.solid()
    bg.fill.fore_color.rgb = bg_color
    bg.line.fill.background()
    return slide


def add_header(slide, title_text, category_kicker="BLUESTOCK MUTUAL FUND ANALYTICS CAPSTONE"):
    """Adds a standard executive header to a slide."""
    # Top rule bar
    top_bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(0.35), Inches(11.733), Inches(0.04))
    top_bar.fill.solid()
    top_bar.fill.fore_color.rgb = COLOR_TEAL_BLUE
    top_bar.line.fill.background()

    # Kicker
    tb_kicker = slide.shapes.add_textbox(Inches(0.8), Inches(0.45), Inches(11.733), Inches(0.3))
    tf_kicker = tb_kicker.text_frame
    tf_kicker.word_wrap = True
    p_k = tf_kicker.paragraphs[0]
    p_k.text = category_kicker.upper()
    p_k.font.size = Pt(9)
    p_k.font.bold = True
    p_k.font.color.rgb = COLOR_ACCENT_RED

    # Title
    tb_title = slide.shapes.add_textbox(Inches(0.8), Inches(0.72), Inches(11.733), Inches(0.55))
    tf_title = tb_title.text_frame
    tf_title.word_wrap = True
    p_t = tf_title.paragraphs[0]
    p_t.text = title_text
    p_t.font.size = Pt(20)
    p_t.font.bold = True
    p_t.font.color.rgb = COLOR_NAVY_DARK


def add_card(slide, left, top, width, height, bg_color=COLOR_LIGHT_BG, border_color=COLOR_BORDER):
    """Adds a rounded rectangle card for visual content encapsulation."""
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    card.fill.solid()
    card.fill.fore_color.rgb = bg_color
    if border_color:
        card.line.color.rgb = border_color
        card.line.width = Pt(1)
    else:
        card.line.fill.background()
    return card


def build_presentation():
    prs = Presentation()
    # 16:9 Widescreen dimensions
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    # =========================================================================
    # SLIDE 1: TITLE SLIDE (Dark Hero Theme)
    # =========================================================================
    s1 = create_slide(prs, bg_color=COLOR_NAVY_DARK)

    # Decorative Accent Bar
    accent_bar = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(1.0), Inches(1.2), Inches(0.12), Inches(5.0))
    accent_bar.fill.solid()
    accent_bar.fill.fore_color.rgb = COLOR_ACCENT_RED
    accent_bar.line.fill.background()

    # Kicker
    tb1_kicker = s1.shapes.add_textbox(Inches(1.3), Inches(1.2), Inches(10.5), Inches(0.4))
    tf1_k = tb1_kicker.text_frame
    p1_k = tf1_k.paragraphs[0]
    p1_k.text = "BLUESTOCK FINTECH CAPSTONE PROJECT — EXECUTIVE SUBMISSION"
    p1_k.font.size = Pt(11)
    p1_k.font.bold = True
    p1_k.font.color.rgb = COLOR_ACCENT_RED

    # Title
    tb1_title = s1.shapes.add_textbox(Inches(1.3), Inches(1.6), Inches(10.5), Inches(1.4))
    tf1_t = tb1_title.text_frame
    tf1_t.word_wrap = True
    p1_t = tf1_t.paragraphs[0]
    p1_t.text = "Indian Mutual Fund Quantitative Analytics & Risk Intelligence Platform"
    p1_t.font.size = Pt(28)
    p1_t.font.bold = True
    p1_t.font.color.rgb = COLOR_WHITE

    # Subtitle
    tb1_sub = s1.shapes.add_textbox(Inches(1.3), Inches(3.1), Inches(10.5), Inches(1.0))
    tf1_s = tb1_sub.text_frame
    tf1_s.word_wrap = True
    p1_s = tf1_s.paragraphs[0]
    p1_s.text = "End-to-End ETL Engineering, Relational Star Schema, Multi-Factor Scoring, Advanced Tail-Risk Models (VaR/CVaR, Monte Carlo, Markowitz Frontier), and Executive Power BI Intelligence"
    p1_s.font.size = Pt(13)
    p1_s.font.color.rgb = RGBColor(200, 215, 235)

    # Metadata Box
    add_card(s1, Inches(1.3), Inches(4.3), Inches(10.8), Inches(1.9), bg_color=RGBColor(38, 70, 110), border_color=COLOR_TEAL_BLUE)
    
    tb1_meta = s1.shapes.add_textbox(Inches(1.5), Inches(4.45), Inches(10.4), Inches(1.6))
    tf1_m = tb1_meta.text_frame
    tf1_m.word_wrap = True
    
    p_m1 = tf1_m.paragraphs[0]
    p_m1.text = "Candidate / Lead Quant Engineer: Varundeep  |  Institutional Partner: Bluestock Fintech"
    p_m1.font.size = Pt(12)
    p_m1.font.bold = True
    p_m1.font.color.rgb = COLOR_WHITE
    
    p_m2 = tf1_m.add_paragraph()
    p_m2.text = "Repository: github.com/Varundeep09/bluestock-mf-capstone  |  Date: September 2026 (Version 1.0)"
    p_m2.font.size = Pt(11)
    p_m2.font.color.rgb = RGBColor(220, 230, 245)
    
    p_m3 = tf1_m.add_paragraph()
    p_m3.text = "Core Tech Stack: Python 3.13, SQLite 3, SQLAlchemy, Pandas, SciPy, Power BI Desktop, ReportLab"
    p_m3.font.size = Pt(11)
    p_m3.font.color.rgb = RGBColor(180, 205, 235)

    # =========================================================================
    # SLIDE 2: PROBLEM STATEMENT & PROJECT OBJECTIVES
    # =========================================================================
    s2 = create_slide(prs)
    add_header(s2, "Business Problem Context & Core Project Objectives")

    # Left Card: 5 Business Problems (P1-P5)
    add_card(s2, Inches(0.8), Inches(1.4), Inches(5.6), Inches(5.5), bg_color=COLOR_LIGHT_BG)
    tb_p = s2.shapes.add_textbox(Inches(1.0), Inches(1.55), Inches(5.2), Inches(5.2))
    tf_p = tb_p.text_frame
    tf_p.word_wrap = True
    
    p_ph = tf_p.paragraphs[0]
    p_ph.text = "5 Core Business Challenges (P1 – P5)"
    p_ph.font.size = Pt(14)
    p_ph.font.bold = True
    p_ph.font.color.rgb = COLOR_NAVY_DARK
    
    probs = [
        ("P1. Opaque Fund Selection", "Evaluating funds on trailing returns alone ignores risk-adjusted efficiency, drawdowns, and expense leakage."),
        ("P2. Fragmented Market Ingestion", "Manual, error-prone data pipelines struggle with missing trading days and unstandardized AMFI feeds."),
        ("P3. Blindness to Tail Risk", "Traditional metrics overlook severe tail-risk losses (VaR/CVaR) during systemic market shocks."),
        ("P4. Silent Retail SIP Churn", "Distributor platforms lack early-warning detection for irregular deposit gaps and mandate drop-offs."),
        ("P5. Hidden Sector Concentration", "Thematic bias and single-sector overweights (HHI > 2500) go unnoticed in retail portfolios.")
    ]
    for code_title, desc in probs:
        p_item = tf_p.add_paragraph()
        p_item.text = f"• {code_title}: {desc}"
        p_item.font.size = Pt(10)
        p_item.font.color.rgb = COLOR_DARK_TEXT
        p_item.space_before = Pt(6)

    # Right Card: 8 Project Objectives (O1-O8)
    add_card(s2, Inches(6.8), Inches(1.4), Inches(5.7), Inches(5.5), bg_color=COLOR_LIGHT_BG)
    tb_o = s2.shapes.add_textbox(Inches(7.0), Inches(1.55), Inches(5.3), Inches(5.2))
    tf_o = tb_o.text_frame
    tf_o.word_wrap = True
    
    p_oh = tf_o.paragraphs[0]
    p_oh.text = "8 Key Engineering & Analytical Objectives (O1 – O8)"
    p_oh.font.size = Pt(14)
    p_oh.font.bold = True
    p_oh.font.color.rgb = COLOR_TEAL_BLUE
    
    objs = [
        ("O1. Automated Pipeline", "Build an automated 5-layer ETL engine ingesting 10 raw CSVs and live AMFI API feeds."),
        ("O2. Relational Warehouse", "Design an 11-table star schema in SQLite with strict foreign keys and index optimization."),
        ("O3. Exploratory Analysis", "Synthesize 10 macro insights across AUM growth, SIP inflows, and demographics with 15+ charts."),
        ("O4. Fund Scorecard", "Engineer a 5-factor quantitative scoring model (0–100) weighting returns, Sharpe, alpha, TER, and drawdown."),
        ("O5. Tail-Risk Modeling", "Calculate 95% Historical VaR and CVaR (Expected Shortfall) across all 40 schemes."),
        ("O6. Retention Analytics", "Conduct investor cohort tracking and diagnose empirical inter-transaction SIP churn gaps."),
        ("O7. Portfolio Frontiers", "Simulate 5Y Monte Carlo GBM cones and solve Markowitz Efficient Frontier optimal weights."),
        ("O8. Executive BI", "Deliver an interactive 4-page Power BI dashboard with KPI cards and dynamic filters.")
    ]
    for code_title, desc in objs:
        p_item = tf_o.add_paragraph()
        p_item.text = f"• {code_title}: {desc}"
        p_item.font.size = Pt(9.5)
        p_item.font.color.rgb = COLOR_DARK_TEXT
        p_item.space_before = Pt(4)

    # =========================================================================
    # SLIDE 3: DATA SOURCES & AUTHENTICITY BREAKDOWN
    # =========================================================================
    s3 = create_slide(prs)
    add_header(s3, "Data Sources, Ingestion Architecture & Data Authenticity")

    # Left Column: Ingested Datasets
    add_card(s3, Inches(0.8), Inches(1.4), Inches(5.6), Inches(5.5))
    tb_ds = s3.shapes.add_textbox(Inches(1.0), Inches(1.55), Inches(5.2), Inches(5.2))
    tf_ds = tb_ds.text_frame
    tf_ds.word_wrap = True
    
    p_dsh = tf_ds.paragraphs[0]
    p_dsh.text = "Ingested Datasets & Live Feeds (46,000+ Records)"
    p_dsh.font.size = Pt(13)
    p_dsh.font.bold = True
    p_dsh.font.color.rgb = COLOR_NAVY_DARK
    
    ds_items = [
        ("Fund Master & NAVs", "40 Schemes across 1,150 trading sessions (46,000 daily NAV rows, Jan 2022 – May 2026)."),
        ("Live AMFI API Feeds", "Automated REST pulls from mfapi.in for 6 core funds (20,208 records staging cache)."),
        ("Investor Transactions", "32,778 transaction records capturing SIP, Lumpsum, Redemption, Demographics, and KYC."),
        ("Market Benchmarks", "8,050 daily records across NIFTY 50, NIFTY 100, NIFTY 500, and NIFTY MIDCAP 150."),
        ("Industry Macro Disclosures", "90 quarterly AUM points, 48 monthly SIP inflows (₹ Cr), 144 category net flow points, 21 folio disclosures."),
        ("Portfolio Holdings", "322 equity holdings with sectoral allocations and company weights.")
    ]
    for title, desc in ds_items:
        p_item = tf_ds.add_paragraph()
        p_item.text = f"• {title}: {desc}"
        p_item.font.size = Pt(9.5)
        p_item.font.color.rgb = COLOR_DARK_TEXT
        p_item.space_before = Pt(5)

    # Right Column: Authenticity & Governance Disclosures
    add_card(s3, Inches(6.8), Inches(1.4), Inches(5.7), Inches(5.5), bg_color=COLOR_GREEN_BG, border_color=RGBColor(165, 214, 167))
    tb_auth = s3.shapes.add_textbox(Inches(7.0), Inches(1.55), Inches(5.3), Inches(5.2))
    tf_auth = tb_auth.text_frame
    tf_auth.word_wrap = True
    
    p_ah = tf_auth.paragraphs[0]
    p_ah.text = "Data Authenticity & Governance Disclosures"
    p_ah.font.size = Pt(13)
    p_ah.font.bold = True
    p_ah.font.color.rgb = COLOR_GREEN_TEXT
    
    auth_items = [
        ("Real AMFI Metadata", "Scheme identifiers, AMFI codes, official names, Total Expense Ratios (TER), AMC brands, and fund managers reflect authentic regulatory filings."),
        ("Anchored Market NAVs", "Daily historical NAV series and NSE benchmark index values reflect real market volatility and return trajectories across the 4.4-year window."),
        ("Synthetic Demographic Layer", "Investor demographics, KYC states, and transaction histories (fact_transactions) are synthetically generated to model realistic Indian investor distributions while preserving privacy."),
        ("Strict ETL Normalization", "Heterogeneous date formats converted to ISO-8601; trading gaps forward-filled; TER clamped to [0.1%, 2.5%]; outlier returns bounded within +/-20%.")
    ]
    for title, desc in auth_items:
        p_item = tf_auth.add_paragraph()
        p_item.text = f"• {title}: {desc}"
        p_item.font.size = Pt(10)
        p_item.font.color.rgb = COLOR_DARK_TEXT
        p_item.space_before = Pt(7)

    # =========================================================================
    # SLIDE 4: SYSTEM ARCHITECTURE & STAR SCHEMA
    # =========================================================================
    s4 = create_slide(prs)
    add_header(s4, "5-Layer Pipeline Architecture & Relational Star Schema")

    # Top Banner: 5 Architecture Layers
    layers = [
        ("1. INGESTION", "Raw CSVs & AMFI API feeds\nAutomated schema profiling"),
        ("2. PROCESSING", "Date normalization & ffill\nTER & Return boundary checks"),
        ("3. WAREHOUSE", "SQLite Star Schema (11 tables)\nForeign keys & B-Tree indexes"),
        ("4. QUANT ENGINE", "CAGR, Sharpe, VaR/CVaR\nMonte Carlo & Markowitz"),
        ("5. BI LAYER", "Power BI Desktop (4 pages)\nInteractive slicers & KPIs")
    ]
    box_w = Inches(2.2)
    box_h = Inches(1.4)
    start_x = Inches(0.8)
    for i, (l_title, l_desc) in enumerate(layers):
        bx = start_x + i * Inches(2.38)
        c = add_card(s4, bx, Inches(1.4), box_w, box_h, bg_color=COLOR_NAVY_DARK if i==2 else COLOR_LIGHT_BG, border_color=COLOR_TEAL_BLUE)
        tb_l = s4.shapes.add_textbox(bx + Inches(0.1), Inches(1.45), box_w - Inches(0.2), box_h - Inches(0.1))
        tf_l = tb_l.text_frame
        tf_l.word_wrap = True
        p_lt = tf_l.paragraphs[0]
        p_lt.text = l_title
        p_lt.font.size = Pt(11)
        p_lt.font.bold = True
        p_lt.font.color.rgb = COLOR_WHITE if i==2 else COLOR_NAVY_DARK
        
        p_ld = tf_l.add_paragraph()
        p_ld.text = l_desc
        p_ld.font.size = Pt(8.5)
        p_ld.font.color.rgb = RGBColor(220, 230, 245) if i==2 else COLOR_DARK_TEXT

    # Bottom Area: Star Schema Breakdown
    add_card(s4, Inches(0.8), Inches(3.0), Inches(11.733), Inches(3.9), bg_color=COLOR_LIGHT_BG)
    tb_sch = s4.shapes.add_textbox(Inches(1.0), Inches(3.1), Inches(11.333), Inches(3.7))
    tf_sch = tb_sch.text_frame
    tf_sch.word_wrap = True
    
    p_sch_h = tf_sch.paragraphs[0]
    p_sch_h.text = "Relational Star Schema Summary (data/db/bluestock_mf.db — 11 Tables)"
    p_sch_h.font.size = Pt(13)
    p_sch_h.font.bold = True
    p_sch_h.font.color.rgb = COLOR_NAVY_DARK
    
    sch_points = [
        ("Dimension Tables", "• dim_fund (PK: amfi_code, 40 schemes) — Scheme metadata, category, launch date, TER, risk rating.\n• dim_date (PK: date_id, 1,608 calendar dates) — Year, quarter, month, day-of-week attributes."),
        ("Time-Series Fact Tables", "• fact_nav (PK: amfi_code, date, 46,000 rows) — Daily NAVs, daily return pct, 1,150 trading sessions.\n• fact_benchmark (PK: index_name, date, 8,050 rows) — Daily closing values for NIFTY 50, 100, 500, MidCap 150."),
        ("Transactional & Operational Facts", "• fact_transactions (PK: tx_id, 32,778 rows) — Granular transaction events, investor demographics, payment channels.\n• fact_portfolio (322 rows), fact_performance (40 rows), fact_aum (90 rows), fact_sip_industry (48 rows), fact_category_inflows (144 rows), fact_folio_count (21 rows)."),
        ("Performance SLA", "• Sub-second analytical queries via composite B-Tree indexes (idx_fact_nav_date, idx_fact_tx_date, idx_fact_tx_state). Master ETL pipeline builds entire DB in 25.4 seconds.")
    ]
    for cat, desc in sch_points:
        p_item = tf_sch.add_paragraph()
        p_item.text = f"{cat}: {desc}"
        p_item.font.size = Pt(9.5)
        p_item.font.color.rgb = COLOR_DARK_TEXT
        p_item.space_before = Pt(4)

    # =========================================================================
    # SLIDE 5: EDA HIGHLIGHTS (PART 1) - MACRO INFLOWS & AUM
    # =========================================================================
    s5 = create_slide(prs)
    add_header(s5, "Exploratory Data Analysis: Macro Trends & Industry Inflows")

    # Left Bullets
    add_card(s5, Inches(0.8), Inches(1.4), Inches(5.4), Inches(5.5))
    tb_e1 = s5.shapes.add_textbox(Inches(1.0), Inches(1.55), Inches(5.0), Inches(5.2))
    tf_e1 = tb_e1.text_frame
    tf_e1.word_wrap = True
    
    p_e1h = tf_e1.paragraphs[0]
    p_e1h.text = "Key Macroeconomic Findings"
    p_e1h.font.size = Pt(13)
    p_e1h.font.bold = True
    p_e1h.font.color.rgb = COLOR_NAVY_DARK
    
    e1_points = [
        ("Retail SIP Surge (+169.2%)", "Monthly SIP inflows grew from ₹11,517 Cr (Jan 2022) to a record ₹31,002 Cr (Dec 2025), creating a massive domestic liquidity cushion against global volatility."),
        ("Equity Folio Doubling (+97.0%)", "Total folios expanded from 13.26 Cr to 26.12 Cr, with Equity folios reaching 69.98% (18.28 Cr) of the total industry."),
        ("Top 3 AMC Dominance (>55%)", "SBI MF (₹12.50 Lakh Cr), ICICI Prudential (₹10.74 Lakh Cr), and HDFC MF (₹9.30 Lakh Cr) command over 55% of industry AUM."),
        ("Correction Resilience", "Retail investors consistently bought market dips (June 2022, March 2023) through sustained SIP contributions.")
    ]
    for title, desc in e1_points:
        p_item = tf_e1.add_paragraph()
        p_item.text = f"• {title}:\n  {desc}"
        p_item.font.size = Pt(9.5)
        p_item.font.color.rgb = COLOR_DARK_TEXT
        p_item.space_before = Pt(6)

    # Right Embedded Chart: Monthly SIP Inflows
    c3_path = str(EDA_CHARTS_DIR / "chart_03_monthly_sip_inflows.png")
    if os.path.exists(c3_path):
        add_card(s5, Inches(6.5), Inches(1.4), Inches(6.0), Inches(5.5), bg_color=COLOR_WHITE)
        s5.shapes.add_picture(c3_path, Inches(6.6), Inches(1.6), width=Inches(5.8), height=Inches(4.9))

    # =========================================================================
    # SLIDE 6: EDA HIGHLIGHTS (PART 2) - DEMOGRAPHICS & SECTORS
    # =========================================================================
    s6 = create_slide(prs)
    add_header(s6, "Exploratory Data Analysis: Demographics, Channels & Sectors")

    # Left Bullets
    add_card(s6, Inches(0.8), Inches(1.4), Inches(5.4), Inches(5.5))
    tb_e2 = s6.shapes.add_textbox(Inches(1.0), Inches(1.55), Inches(5.0), Inches(5.2))
    tf_e2 = tb_e2.text_frame
    tf_e2.word_wrap = True
    
    p_e2h = tf_e2.paragraphs[0]
    p_e2h.text = "Demographic & Allocation Findings"
    p_e2h.font.size = Pt(13)
    p_e2h.font.bold = True
    p_e2h.font.color.rgb = COLOR_NAVY_DARK
    
    e2_points = [
        ("Millennial Leadership (55%)", "Investors aged 26–45 represent 55% of all transaction accounts; Gen-Z (18–25) drives rapid digital micro-SIP adoption."),
        ("Beyond-Metro (B30) Growth", "B30 semi-urban/rural towns contribute 39.8% of transaction capital volume, proving deep geographic penetration."),
        ("Digital Payment Rails (68.2%)", "UPI and eNACH mandates capture 68.2% of mutual fund transactions, reducing cheques to under 12%."),
        ("Direct Plan Alpha (60–110 bps)", "Direct plans offer 0.6%–1.1% lower expense ratios than Regular plans, adding ~0.8% compounding net return."),
        ("Structural Sector Tilts", "Portfolios carry heavy systemic weightings in Financials (32.1%) and Information Technology (19.4%).")
    ]
    for title, desc in e2_points:
        p_item = tf_e2.add_paragraph()
        p_item.text = f"• {title}:\n  {desc}"
        p_item.font.size = Pt(9.5)
        p_item.font.color.rgb = COLOR_DARK_TEXT
        p_item.space_before = Pt(5)

    # Right Embedded Chart: Demographics & Sector Donut
    c5_path = str(EDA_CHARTS_DIR / "chart_05_investor_demographics_sip.png")
    c9_path = str(EDA_CHARTS_DIR / "chart_09_sector_allocation_donut.png")
    if os.path.exists(c5_path) and os.path.exists(c9_path):
        add_card(s6, Inches(6.5), Inches(1.4), Inches(6.0), Inches(2.65), bg_color=COLOR_WHITE)
        s6.shapes.add_picture(c5_path, Inches(6.6), Inches(1.45), width=Inches(5.8), height=Inches(2.55))
        
        add_card(s6, Inches(6.5), Inches(4.25), Inches(6.0), Inches(2.65), bg_color=COLOR_WHITE)
        s6.shapes.add_picture(c9_path, Inches(6.6), Inches(4.3), width=Inches(5.8), height=Inches(2.55))

    # =========================================================================
    # SLIDE 7: PERFORMANCE METRICS (PART 1) - SCORECARD & TOP 5 FUNDS
    # =========================================================================
    s7 = create_slide(prs)
    add_header(s7, "Performance Analytics: Multi-Factor Scorecard & Top Funds")

    # Left: Scorecard Methodology
    add_card(s7, Inches(0.8), Inches(1.4), Inches(4.8), Inches(5.5))
    tb_sc = s7.shapes.add_textbox(Inches(1.0), Inches(1.55), Inches(4.4), Inches(5.2))
    tf_sc = tb_sc.text_frame
    tf_sc.word_wrap = True
    
    p_sch = tf_sc.paragraphs[0]
    p_sch.text = "Multi-Factor Scoring Methodology (0–100)"
    p_sch.font.size = Pt(13)
    p_sch.font.bold = True
    p_sch.font.color.rgb = COLOR_NAVY_DARK
    
    sc_weights = [
        ("30% Trailing 3Y CAGR", "Measures medium-term annualized compound capital appreciation."),
        ("25% Sharpe Ratio (Rf=6.5%)", "Measures excess return per unit of total annualized volatility."),
        ("20% Jensen's Alpha", "Measures active fund manager outperformance over CAPM benchmark."),
        ("15% Inverted Expense Ratio", "Rewards low-cost schemes (higher score for lower TER)."),
        ("10% Inverted Max Drawdown", "Rewards capital preservation during market downturns.")
    ]
    for w_title, w_desc in sc_weights:
        p_item = tf_sc.add_paragraph()
        p_item.text = f"• {w_title}: {w_desc}"
        p_item.font.size = Pt(9.5)
        p_item.font.color.rgb = COLOR_DARK_TEXT
        p_item.space_before = Pt(5)

    # Right: Top 5 Funds Table
    add_card(s7, Inches(5.8), Inches(1.4), Inches(6.733), Inches(5.5), bg_color=COLOR_WHITE)
    tb_top = s7.shapes.add_textbox(Inches(6.0), Inches(1.55), Inches(6.333), Inches(5.2))
    tf_top = tb_top.text_frame
    tf_top.word_wrap = True
    
    p_th = tf_top.paragraphs[0]
    p_th.text = "Top 5 Mutual Fund Schemes Across Categories"
    p_th.font.size = Pt(13)
    p_th.font.bold = True
    p_th.font.color.rgb = COLOR_TEAL_BLUE

    top5_funds = [
        ("1. Kotak Flexicap Fund (Score: 71.38)", "Equity | 3Y Return: 15.65% | Sharpe: 0.98 | Alpha: 1.85 | TER: 1.45% | Max DD: -19.50%"),
        ("2. SBI Small Cap Fund - Reg (Score: 70.25)", "Equity | 3Y Return: 23.39% | Sharpe: 0.94 | Alpha: 1.23 | TER: 1.43% | Max DD: -13.35%"),
        ("3. ICICI Pru Liquid Fund - Reg (Score: 70.12)", "Debt/Liquid | 3Y Return: 7.68% | Sharpe: 7.68 | Alpha: 1.85 | TER: 0.74% | Max DD: -2.62%"),
        ("4. HDFC Short Term Debt - Reg (Score: 69.88)", "Debt | 3Y Return: 7.37% | Sharpe: 1.84 | Alpha: 1.98 | TER: 0.56% | Max DD: -6.01%"),
        ("5. Kotak Emerging Equity - Reg (Score: 67.88)", "Equity/Mid | 3Y Return: 18.23% | Sharpe: 0.96 | Alpha: 1.91 | TER: 1.56% | Max DD: -21.92%")
    ]
    for fund_name, metrics in top5_funds:
        p_item = tf_top.add_paragraph()
        p_item.text = f"★ {fund_name}\n   {metrics}"
        p_item.font.size = Pt(9.5)
        p_item.font.color.rgb = COLOR_DARK_TEXT
        p_item.space_before = Pt(6)

    # =========================================================================
    # SLIDE 8: PERFORMANCE METRICS (PART 2) - RISK & TAIL METRICS
    # =========================================================================
    s8 = create_slide(prs)
    add_header(s8, "Performance Analytics: Tail Risk (VaR/CVaR) & Tracking Error")

    # Left: Risk Metrics & HHI Flags
    add_card(s8, Inches(0.8), Inches(1.4), Inches(5.4), Inches(5.5))
    tb_r2 = s8.shapes.add_textbox(Inches(1.0), Inches(1.55), Inches(5.0), Inches(5.2))
    tf_r2 = tb_r2.text_frame
    tf_r2.word_wrap = True
    
    p_r2h = tf_r2.paragraphs[0]
    p_r2h.text = "Quantitative Risk & Concentration Findings"
    p_r2h.font.size = Pt(13)
    p_r2h.font.bold = True
    p_r2h.font.color.rgb = COLOR_NAVY_DARK
    
    risk_points = [
        ("95% 1-Day VaR & CVaR Tail Risk", "SBI Small Cap Direct (119599) carries the highest 1-day tail risk with VaR of -2.69%, CVaR of -3.24%, and worst 1-day drop of -5.12%."),
        ("Tracking Error Divergence", "Small Cap schemes exhibit high tracking error (28.45%) vs Large Cap (3.45%) against NIFTY indices due to active off-benchmark stock picking."),
        ("HHI Concentration Flags (>2500)", "4 schemes exceed high concentration thresholds: Axis Bluechip (2967.69) due to 48.7% IT weighting; Mirae Tax Saver (2549.92) with 39.8% Banking."),
        ("Multi-Asset Downside Protection", "Debt and Liquid funds maintain near-zero correlation (-0.05 to +0.12) to equities, providing robust drawdown mitigation.")
    ]
    for title, desc in risk_points:
        p_item = tf_r2.add_paragraph()
        p_item.text = f"• {title}:\n  {desc}"
        p_item.font.size = Pt(9.5)
        p_item.font.color.rgb = COLOR_DARK_TEXT
        p_item.space_before = Pt(5)

    # Right: Embedded Benchmark Chart
    b_path = str(REPORTS_DIR / "top5_funds_vs_benchmarks.png")
    if os.path.exists(b_path):
        add_card(s8, Inches(6.5), Inches(1.4), Inches(6.0), Inches(5.5), bg_color=COLOR_WHITE)
        s8.shapes.add_picture(b_path, Inches(6.6), Inches(1.7), width=Inches(5.8), height=Inches(4.7))

    # =========================================================================
    # SLIDE 9: DASHBOARD (PART 1) - POWER BI PAGES 1 & 2
    # =========================================================================
    s9 = create_slide(prs)
    add_header(s9, "Executive Power BI Dashboard: Macro Trends & Fund Scorecard")

    # Left: Page 1 Screenshot & Description
    p1_img = str(DASH_DIR / "page1_industry_overview.png")
    add_card(s9, Inches(0.8), Inches(1.4), Inches(5.7), Inches(5.5), bg_color=COLOR_WHITE)
    tb_d1 = s9.shapes.add_textbox(Inches(1.0), Inches(1.45), Inches(5.3), Inches(1.0))
    tf_d1 = tb_d1.text_frame
    tf_d1.word_wrap = True
    p_d1h = tf_d1.paragraphs[0]
    p_d1h.text = "Page 1: Industry & Macro Overview"
    p_d1h.font.size = Pt(12)
    p_d1h.font.bold = True
    p_d1h.font.color.rgb = COLOR_NAVY_DARK
    p_d1s = tf_d1.add_paragraph()
    p_d1s.text = "Tracks total industry AUM, AMC market share, monthly category net flows, and macroeconomic growth trends."
    p_d1s.font.size = Pt(8.5)
    p_d1s.font.color.rgb = COLOR_DARK_TEXT
    if os.path.exists(p1_img):
        s9.shapes.add_picture(p1_img, Inches(0.9), Inches(2.3), width=Inches(5.5), height=Inches(4.4))

    # Right: Page 2 Screenshot & Description
    p2_img = str(DASH_DIR / "page2_fund_performance.png")
    add_card(s9, Inches(6.8), Inches(1.4), Inches(5.7), Inches(5.5), bg_color=COLOR_WHITE)
    tb_d2 = s9.shapes.add_textbox(Inches(7.0), Inches(1.45), Inches(5.3), Inches(1.0))
    tf_d2 = tb_d2.text_frame
    tf_d2.word_wrap = True
    p_d2h = tf_d2.paragraphs[0]
    p_d2h.text = "Page 2: Fund Performance & Risk Scorecard"
    p_d2h.font.size = Pt(12)
    p_d2h.font.bold = True
    p_d2h.font.color.rgb = COLOR_NAVY_DARK
    p_d2s = tf_d2.add_paragraph()
    p_d2s.text = "Interactive 40-fund scorecard table, 1Y/3Y/5Y returns, Sharpe/Sortino ratios, Alpha, Beta, and TER slider filters."
    p_d2s.font.size = Pt(8.5)
    p_d2s.font.color.rgb = COLOR_DARK_TEXT
    if os.path.exists(p2_img):
        s9.shapes.add_picture(p2_img, Inches(6.9), Inches(2.3), width=Inches(5.5), height=Inches(4.4))

    # =========================================================================
    # SLIDE 10: DASHBOARD (PART 2) - POWER BI PAGES 3 & 4
    # =========================================================================
    s10 = create_slide(prs)
    add_header(s10, "Executive Power BI Dashboard: Demographics & SIP Trajectory")

    # Left: Page 3 Screenshot & Description
    p3_img = str(DASH_DIR / "page3_investor_analytics.png")
    add_card(s10, Inches(0.8), Inches(1.4), Inches(5.7), Inches(5.5), bg_color=COLOR_WHITE)
    tb_d3 = s10.shapes.add_textbox(Inches(1.0), Inches(1.45), Inches(5.3), Inches(1.0))
    tf_d3 = tb_d3.text_frame
    tf_d3.word_wrap = True
    p_d3h = tf_d3.paragraphs[0]
    p_d3h.text = "Page 3: Investor Demographics & Churn Analytics"
    p_d3h.font.size = Pt(12)
    p_d3h.font.bold = True
    p_d3h.font.color.rgb = COLOR_NAVY_DARK
    p_d3s = tf_d3.add_paragraph()
    p_d3s.text = "Geographic T30/B30 volume split, payment mode shares (UPI/eNACH), age brackets, and KYC compliance."
    p_d3s.font.size = Pt(8.5)
    p_d3s.font.color.rgb = COLOR_DARK_TEXT
    if os.path.exists(p3_img):
        s10.shapes.add_picture(p3_img, Inches(0.9), Inches(2.3), width=Inches(5.5), height=Inches(4.4))

    # Right: Page 4 Screenshot & Description
    p4_img = str(DASH_DIR / "page4_sip_market_trends.png")
    add_card(s10, Inches(6.8), Inches(1.4), Inches(5.7), Inches(5.5), bg_color=COLOR_WHITE)
    tb_d4 = s10.shapes.add_textbox(Inches(7.0), Inches(1.45), Inches(5.3), Inches(1.0))
    tf_d4 = tb_d4.text_frame
    tf_d4.word_wrap = True
    p_d4h = tf_d4.paragraphs[0]
    p_d4h.text = "Page 4: SIP Growth & Market Penetration"
    p_d4h.font.size = Pt(12)
    p_d4h.font.bold = True
    p_d4h.font.color.rgb = COLOR_NAVY_DARK
    p_d4s = tf_d4.add_paragraph()
    p_d4s.text = "Industry monthly SIP contribution trajectories, active account expansion, ticket size distributions, and YoY trends."
    p_d4s.font.size = Pt(8.5)
    p_d4s.font.color.rgb = COLOR_DARK_TEXT
    if os.path.exists(p4_img):
        s10.shapes.add_picture(p4_img, Inches(6.9), Inches(2.3), width=Inches(5.5), height=Inches(4.4))

    # =========================================================================
    # SLIDE 11: KEY FINDINGS & STRATEGIC TAKEAWAYS (Non-Technical Audience)
    # =========================================================================
    s11 = create_slide(prs)
    add_header(s11, "Strategic Business Takeaways & Key Findings for Leadership")

    # 6 High-Impact Executive Cards Grid (2 rows x 3 cols)
    findings_grid = [
        ("1. Domestic Retail Liquidity Moat", "Monthly SIP inflows grew +169.2% to ₹31,002 Cr, creating an institutional-grade domestic buffer against global market shocks.", COLOR_NAVY_DARK),
        ("2. Compounding Direct Plan Alpha", "Direct mutual fund plans deliver a 60–110 bps expense saving over Regular plans, generating ~0.8% higher annualized net return.", COLOR_TEAL_BLUE),
        ("3. Beyond-Metro (B30) Momentum", "Tier-2 and Tier-3 towns drive ~40% of total transaction capital, proving strong digital financial inclusion across India.", COLOR_NAVY_DARK),
        ("4. Re-Thinking SIP Churn Dynamics", "97.8% of investors deposit every ~65 days (manual habit, not churn); platforms must deploy smart WhatsApp nudges and auto-pay.", COLOR_ACCENT_RED),
        ("5. Automated Concentration Shields", "Top equity funds show high sector concentration (e.g. Axis Bluechip @ 48.7% IT), warranting automated 30% sector alert caps.", COLOR_NAVY_DARK),
        ("6. Multi-Asset Core-Satellite Edge", "Blending 80% low-cost debt anchors with 20% high-alpha equities maximizes portfolio Sharpe (2.12) while limiting equity drawdowns.", COLOR_TEAL_BLUE),
    ]

    card_w = Inches(3.7)
    card_h = Inches(2.55)
    for idx, (f_title, f_desc, bar_col) in enumerate(findings_grid):
        row = idx // 3
        col = idx % 3
        cx = Inches(0.8) + col * Inches(3.95)
        cy = Inches(1.4) + row * Inches(2.8)
        
        add_card(s11, cx, cy, card_w, card_h, bg_color=COLOR_LIGHT_BG)
        
        # Color bar on card left
        c_bar = s11.shapes.add_shape(MSO_SHAPE.RECTANGLE, cx, cy, Inches(0.1), card_h)
        c_bar.fill.solid()
        c_bar.fill.fore_color.rgb = bar_col
        c_bar.line.fill.background()
        
        tb_f = s11.shapes.add_textbox(cx + Inches(0.2), cy + Inches(0.15), card_w - Inches(0.35), card_h - Inches(0.3))
        tf_f = tb_f.text_frame
        tf_f.word_wrap = True
        
        p_ft = tf_f.paragraphs[0]
        p_ft.text = f_title
        p_ft.font.size = Pt(11)
        p_ft.font.bold = True
        p_ft.font.color.rgb = COLOR_NAVY_DARK
        
        p_fd = tf_f.add_paragraph()
        p_fd.text = f_desc
        p_fd.font.size = Pt(9.5)
        p_fd.font.color.rgb = COLOR_DARK_TEXT
        p_fd.space_before = Pt(6)

    # =========================================================================
    # SLIDE 12: CLOSING / THANK YOU SLIDE
    # =========================================================================
    s12 = create_slide(prs, bg_color=COLOR_NAVY_DARK)

    # Decorative Accent
    accent_bar12 = s12.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(1.0), Inches(1.2), Inches(0.12), Inches(5.0))
    accent_bar12.fill.solid()
    accent_bar12.fill.fore_color.rgb = COLOR_ACCENT_RED
    accent_bar12.line.fill.background()

    tb12 = s12.shapes.add_textbox(Inches(1.4), Inches(1.2), Inches(10.5), Inches(5.0))
    tf12 = tb12.text_frame
    tf12.word_wrap = True
    
    p12_k = tf12.paragraphs[0]
    p12_k.text = "CAPSTONE DELIVERABLES COMPLETE & VERIFIED"
    p12_k.font.size = Pt(11)
    p12_k.font.bold = True
    p12_k.font.color.rgb = COLOR_ACCENT_RED
    
    p12_t = tf12.add_paragraph()
    p12_t.text = "Thank You — Questions & Discussion"
    p12_t.font.size = Pt(28)
    p12_t.font.bold = True
    p12_t.font.color.rgb = COLOR_WHITE
    p12_t.space_before = Pt(8)
    
    p12_m = tf12.add_paragraph()
    p12_m.text = "Indian Mutual Fund Quantitative Analytics & Risk Intelligence Platform\nBluestock Fintech Capstone Submission | Lead Quant Engineer: Varundeep"
    p12_m.font.size = Pt(13)
    p12_m.font.color.rgb = RGBColor(200, 215, 235)
    p12_m.space_before = Pt(10)
    
    p12_del = tf12.add_paragraph()
    p12_del.text = "Comprehensive Project Deliverables Inventory:\n" \
                   "• 19-Page Final Research Report (reports/Final_Report.pdf)\n" \
                   "• 12-Slide Companion Executive Presentation (reports/Bluestock_MF_Presentation.pptx)\n" \
                   "• Interactive Power BI Dashboard (dashboard/bluestock_mf.pbix + Dashboard.pdf)\n" \
                   "• 5 Executed Jupyter Notebooks (01_data_ingestion to 05_advanced_analytics)\n" \
                   "• Automated Master ETL Pipeline & Relational SQLite Database (data/db/bluestock_mf.db)"
    p12_del.font.size = Pt(10.5)
    p12_del.font.color.rgb = RGBColor(220, 235, 255)
    p12_del.space_before = Pt(14)
    
    p12_repo = tf12.add_paragraph()
    p12_repo.text = "GitHub Repository: https://github.com/Varundeep09/bluestock-mf-capstone"
    p12_repo.font.size = Pt(12)
    p12_repo.font.bold = True
    p12_repo.font.color.rgb = COLOR_WHITE
    p12_repo.space_before = Pt(14)

    # Save presentation
    prs.save(str(OUTPUT_PPTX))
    print(f"Final Presentation successfully created -> {OUTPUT_PPTX} ({len(prs.slides)} slides)")


if __name__ == "__main__":
    build_presentation()
