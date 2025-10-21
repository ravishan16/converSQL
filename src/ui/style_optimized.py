"""
Optimized CSS styling for converSQL application.
Consolidated and cleaned up to fix spacing, alignment, and container issues.
"""

import streamlit as st


def load_css():
    """Load optimized CSS with fixed spacing, alignment, and container widths."""
    st.markdown(
        """
<style>
/* ============================================================================
   CSS VARIABLES - Single source of truth for colors and spacing
   ============================================================================ */
:root {
    /* Color Palette */
    --color-background: #FAF6F0;
    --color-background-alt: #FDFDFD;
    --color-text-primary: #3A3A3A;
    --color-text-secondary: #7C6F64;
    --color-accent-primary: #DDBEA9;
    --color-accent-primary-darker: #B45F4D;
    --color-border-light: #E4C590;
    --color-success-bg: #F4E8DC;
    --color-success-border: #E4C590;
    --color-success-text: #3A3A3A;
    --color-warning-bg: #F9E7CE;
    --color-warning-border: #E4C590;
    --color-warning-text: #7C6F64;

    /* Spacing */
    --spacing-xs: 0.25rem;
    --spacing-sm: 0.5rem;
    --spacing-md: 1rem;
    --spacing-lg: 1.5rem;
    --spacing-xl: 2rem;

    /* Container */
    --container-max-width: 1360px;
    --container-padding: 1.75rem;
}

/* ============================================================================
   BASE LAYOUT - Main container and body
   ============================================================================ */
body {
    background: var(--color-background);
    color: var(--color-text-secondary);
}

/* Main content container - consistent width and padding */
.main .block-container {
    padding: var(--spacing-lg) var(--container-padding);
    background: var(--color-background);
    max-width: var(--container-max-width);
    margin: 0 auto;
}

/* Remove conflicting nested container rules */
.main .block-container > div {
    width: 100%;
}

/* ============================================================================
   TABS - Consistent tab styling
   ============================================================================ */
.stTabs [data-baseweb="tab-list"] {
    gap: var(--spacing-sm);
    background: none;
    border-bottom: 1px solid var(--color-border-light);
    margin-bottom: var(--spacing-lg);
}

.stTabs [data-baseweb="tab"] {
    background: linear-gradient(160deg, var(--color-background-alt) 0%, var(--color-background) 100%);
    border: 1px solid var(--color-border-light);
    border-radius: 8px 8px 0 0;
    color: var(--color-text-secondary);
    font-weight: 500;
    padding: var(--spacing-sm) var(--spacing-md);
    margin: 0 var(--spacing-xs);
    border-bottom: none;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(150deg, var(--color-accent-primary) 0%, var(--color-accent-primary-darker) 100%);
    color: var(--color-background-alt);
    border-color: var(--color-accent-primary-darker);
    box-shadow: 0 4px 12px rgba(180, 95, 77, 0.25);
}

/* ============================================================================
   FORM CONTROLS - Consistent input and select styling
   ============================================================================ */
.stSelectbox > div > div,
.stTextArea > div > div {
    border-radius: 8px;
    border-color: var(--color-border-light) !important;
    box-shadow: none !important;
}

.stTextArea > div > textarea {
    border-radius: 8px !important;
    border-color: var(--color-border-light) !important;
    padding: 0.75rem !important;
    font-size: 0.95rem !important;
    background: var(--color-background) !important;
    min-height: 100px !important;
}

.stSelectbox label,
.stTextArea label {
    color: var(--color-text-primary);
    font-weight: 500;
    font-size: 0.95rem;
}

/* ============================================================================
   BUTTONS - Unified button styling
   ============================================================================ */
.stButton > button {
    border-radius: 8px;
    font-weight: 500;
    background: var(--color-accent-primary);
    color: var(--color-text-primary);
    border: 1px solid var(--color-accent-primary-darker);
    padding: 0.75rem 1.25rem;
    height: 42px;
    min-width: 120px;
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: var(--spacing-sm);
    transition: all 0.2s ease;
}

.stButton > button:hover {
    background: var(--color-accent-primary-darker);
    color: var(--color-background-alt);
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(180, 95, 77, 0.2);
}

/* Primary action buttons */
div[kind="primary"] button {
    background: var(--color-accent-primary-darker) !important;
    color: var(--color-background-alt) !important;
    border-color: var(--color-accent-primary-darker) !important;
}

div[kind="primary"] button:hover {
    background: #9d4f3e !important;
}

/* Secondary buttons */
button:not([kind="primary"]) {
    background: var(--color-background-alt) !important;
    color: var(--color-accent-primary-darker) !important;
    border-color: var(--color-border-light) !important;
}

/* Button spacing */
.stButton {
    margin: var(--spacing-xs) 0;
}

/* ============================================================================
   BUTTON CONTAINERS - Consistent flex layout
   ============================================================================ */
.button-container,
.query-actions,
.query-controls {
    display: flex;
    gap: 0.75rem;
    margin: var(--spacing-md) 0;
    width: 100%;
}

.button-container .stButton,
.query-actions .stButton,
.query-controls .stButton {
    flex: 1;
    min-width: 0; /* Prevent flex items from overflowing */
}

/* ============================================================================
   CARDS - Section and metric cards
   ============================================================================ */
.section-card {
    background: var(--color-background-alt);
    border: 1px solid var(--color-border-light);
    border-radius: 12px;
    padding: var(--spacing-lg);
    box-shadow: 0 8px 24px rgba(180, 95, 77, 0.08);
    margin-bottom: var(--spacing-lg);
}

.section-card__header h3 {
    color: var(--color-text-primary);
    font-weight: 500;
    font-size: 1.1rem;
    margin: 0 0 var(--spacing-sm) 0;
}

.section-card__header p {
    color: var(--color-text-secondary);
    font-size: 0.9rem;
    margin: 0;
    line-height: 1.4;
}

.metric-card {
    background-color: var(--color-background-alt);
    border: 1px solid var(--color-border-light);
    border-radius: 8px;
    padding: 0.75rem;
}

/* ============================================================================
   RESULTS CARD - FIXED: Single definition, proper width
   ============================================================================ */
.results-card {
    background: var(--color-background-alt);
    border: 1px solid var(--color-border-light);
    border-radius: 12px;
    padding: var(--spacing-lg);
    margin: var(--spacing-lg) 0;
    box-shadow: 0 8px 24px rgba(180, 95, 77, 0.08);
    /* FIXED: Use max-width instead of viewport hacks */
    width: 100%;
    max-width: 100%;
}

/* Hide empty results-card divs */
.results-card:empty {
    display: none !important;
    margin: 0 !important;
    padding: 0 !important;
    border: none !important;
}

.results-card div[data-testid="stDataFrame"] {
    margin-top: var(--spacing-md);
    border: 1px solid var(--color-border-light);
    border-radius: 8px;
    background: var(--color-background);
}

/* ============================================================================
   DATAFRAMES - Full width table display
   ============================================================================ */
div[data-testid="stDataFrame"],
div[data-testid="stDataFrame"] > div,
div[data-testid="stDataFrame"] [data-testid="stVerticalBlock"],
div[data-testid="stDataFrame"] [data-testid="stHorizontalBlock"],
div[data-testid="stDataFrame"] [data-testid="stDataFrameResizable"] {
    width: 100% !important;
    max-width: 100% !important;
    margin-left: 0 !important;
    margin-right: 0 !important;
}

div[data-testid="stDataFrame"] table {
    width: 100% !important;
}

div[data-testid="stDataFrame"] [data-testid="StyledDataFrame"] {
    width: 100% !important;
    max-width: 100% !important;
}

/* ============================================================================
   METRICS - Consistent metric display
   ============================================================================ */
.results-metrics {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: var(--spacing-md);
    margin: var(--spacing-lg) 0;
}

[data-testid="metric-container"] {
    background: var(--color-background);
    border: 1px solid var(--color-border-light);
    border-radius: 8px;
    padding: 0.75rem;
    text-align: center;
    transition: all 0.2s ease;
}

[data-testid="metric-container"]:hover {
    border-color: var(--color-accent-primary);
    box-shadow: 0 4px 12px rgba(180, 95, 77, 0.1);
}

[data-testid="metric-container"] label {
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--color-text-secondary);
    margin-bottom: var(--spacing-xs);
}

[data-testid="metric-container"] [data-testid="metric-value"] {
    font-size: 1.2rem;
    font-weight: 600;
    color: var(--color-text-primary);
}

/* ============================================================================
   CHARTS - Full width chart containers
   ============================================================================ */
div[data-testid="stVegaLiteChart"] {
    width: 100% !important;
    padding: var(--spacing-sm) 0 !important;
}

.chart-section {
    background: var(--color-background);
    border: 1px solid var(--color-border-light);
    border-radius: 12px;
    padding: var(--spacing-lg);
    margin: var(--spacing-lg) 0;
}

/* ============================================================================
   ALERTS - Success, warning, error messages
   ============================================================================ */
.stSuccess {
    background-color: var(--color-success-bg);
    border-color: var(--color-success-border);
    color: var(--color-success-text);
}

.stWarning {
    background-color: var(--color-warning-bg);
    border-color: var(--color-warning-border);
    color: var(--color-warning-text);
}

/* ============================================================================
   SIDEBAR - Consistent sidebar styling
   ============================================================================ */
section[data-testid="stSidebar"] {
    background: var(--color-background);
}

section[data-testid="stSidebar"] .block-container {
    padding-top: var(--spacing-xl);
}

.sidebar-card {
    background: var(--color-background-alt);
    border: 1px solid var(--color-border-light);
    border-radius: 12px;
    padding: 1.25rem;
    margin: 0 0 var(--spacing-md) 0;
}

.sidebar-logo {
    display: flex;
    justify-content: center;
    margin: 0 0 1.25rem 0;
    padding: 0.35rem 0.75rem 0 0.75rem;
}

.sidebar-logo img {
    width: 100%;
    height: auto;
    filter: drop-shadow(0 12px 24px rgba(180, 95, 77, 0.18));
}

.sidebar-hero {
    margin: 0 0 var(--spacing-lg) 0;
    padding: 1.35rem 1.2rem 1.4rem 1.2rem;
    background: var(--color-background-alt);
    border: 1px solid var(--color-border-light);
    border-radius: 16px;
    box-shadow: 0 10px 24px rgba(180, 95, 77, 0.12);
}

.sidebar-hero__pill-label {
    color: var(--color-text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-size: 0.65rem;
}

.sidebar-hero__pill-value {
    color: var(--color-accent-primary-darker);
    font-weight: 600;
}

/* ============================================================================
   BRANDING - Logo and brand elements
   ============================================================================ */
.brand-logo {
    display: flex;
    justify-content: center;
    margin: 0 auto var(--spacing-xl) auto;
    max-width: 640px;
    padding: var(--spacing-sm) var(--spacing-md) 0 var(--spacing-md);
}

.brand-logo img {
    width: 100%;
    height: auto;
    filter: drop-shadow(0 18px 36px rgba(180, 95, 77, 0.22));
}

/* ============================================================================
   FOOTER - Application footer
   ============================================================================ */
.footer-links {
    margin-top: var(--spacing-md);
    display: flex;
    justify-content: center;
    gap: var(--spacing-lg);
    flex-wrap: wrap;
}

.footer-links a {
    color: var(--color-accent-primary-darker);
    text-decoration: none;
    font-weight: 500;
    font-size: 0.85rem;
    transition: color 0.2s ease;
}

.footer-links a:hover {
    color: var(--color-accent-primary);
}

/* ============================================================================
   UTILITY CLASSES
   ============================================================================ */
.text-label {
    display: block;
    margin: 1.25rem 0 var(--spacing-sm) 0;
    font-weight: 500;
    font-size: 0.9rem;
    color: var(--color-text-primary);
}

.section-spacer {
    height: var(--spacing-lg);
}

/* Download button styling */
.stDownloadButton button {
    width: 100%;
    text-transform: uppercase;
    font-size: 0.7rem;
    letter-spacing: 0.05em;
    font-weight: 600;
    background: var(--color-background);
    color: var(--color-text-secondary);
    border: 1px solid var(--color-border-light);
    height: 100%;
    min-height: 42px;
}

/* ============================================================================
   RESPONSIVE DESIGN
   ============================================================================ */
@media (max-width: 768px) {
    :root {
        --container-padding: 1rem;
    }

    .main .block-container {
        padding: var(--spacing-md) var(--container-padding);
    }

    .results-metrics {
        grid-template-columns: repeat(2, 1fr);
    }

    .button-container,
    .query-actions,
    .query-controls {
        flex-direction: column;
    }
}
</style>
""",
        unsafe_allow_html=True,
    )
