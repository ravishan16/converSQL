import streamlit as st


def load_css():
    st.markdown(
        """
<style>
:root {
    --color-background: #FAF6F0;
    --color-background-alt: #FDFDFD;
    --color-text-primary: #3A3A3A;
    --color-text-secondary: #7C6F64;
    --color-accent-primary: #DDBEA9;
    --color-accent-primary-darker: #B45F4D;
    --color-border-light: #E4C590;
    --color-tag-bg: #E4C590;
    --color-tag-text: #3A3A3A;
    --color-footer-bg: #FAF6F0;
    --color-footer-text: #7C6F64;
    --color-footer-link-hover: #DDBEA9;
    --color-success-bg: #F4E8DC;
    --color-success-border: #E4C590;
    --color-success-text: #3A3A3A;
    --color-warning-bg: #F9E7CE;
    --color-warning-border: #E4C590;
    --color-warning-text: #7C6F64;
}

body {
    background: var(--color-background);
    color: var(--color-text-secondary);
}

.main .block-container {
    padding: 1.25rem 0;
    background: var(--color-background);
    max-width: 100%;
    margin: 0 auto;
}

/* Standard content width container */
.main .block-container > div:not(.results-card) {
    max-width: 1360px;
    margin: 0 auto;
    padding: 0 1.75rem;
}

.stTabs [data-baseweb="tab-list"] {
    gap: 0.5rem;
    background: none;
    border-bottom: 1px solid var(--color-border-light);
    margin-bottom: 1.5rem;
}

/* Full-width chart container */
div[data-testid="stVegaLiteChart"] {
    width: 100% !important;
    padding: 0.5rem 0 !important;
}

/* Action button containers */
.button-container {
    display: flex;
    gap: 1rem;
    margin: 1rem 0;
}

.button-container > div {
    flex: 1;
}

/* Query action buttons */
.query-actions {
    display: flex;
    gap: 0.75rem;
    margin: 1rem 0;
}

.query-actions .stButton {
    flex: 1;
}

/* Small action buttons */
.action-button-small button {
    height: 36px;
    min-width: 100px;
    padding: 0 1rem;
    font-size: 0.9rem;
}

/* Control layout improvements */
.stSelectbox label {
    color: var(--color-text-primary);
    font-weight: 500;
    font-size: 0.95rem;
}

/* Consistent spacing for control groups */
.control-group {
    margin: 0.75rem 0;
    padding: 0.5rem 0;
}

.stTabs [data-baseweb="tab"] {
    background: linear-gradient(160deg, var(--color-background-alt) 0%, var(--color-background) 100%);
    border: 1px solid var(--color-border-light);
    border-radius: 8px 8px 0 0;
    color: var(--color-text-secondary);
    font-weight: 500;
    padding: 0.5rem 1rem;
    margin: 0 0.25rem;
    border-bottom: none;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(150deg, var(--color-accent-primary) 0%, var(--color-accent-primary-darker) 100%);
    color: var(--color-background-alt);
    border-color: var(--color-accent-primary-darker);
    box-shadow: 0 4px 12px rgba(180, 95, 77, 0.25);
}

.metric-card {
    background-color: var(--color-background-alt);
    border: 1px solid var(--color-border-light);
    border-radius: 0.5rem;
    padding: 0.75rem;
}

.stSelectbox > div > div,
.stTextArea > div > div {
    border-radius: 0.5rem;
    border-color: var(--color-border-light) !important;
    box-shadow: none !important;
}

.stButton > button {
    border-radius: 0.5rem;
    font-weight: 500;
    background: var(--color-accent-primary);
    color: var(--color-text-primary);
    border: 1px solid var(--color-accent-primary-darker);
    padding: 0.75rem 1rem;
    height: 42px;
    min-width: 120px;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
}

/* Full-width buttons in flex containers */
div.row-widget.stButton {
    flex: 1;
    width: 100%;
}

/* Action buttons */
div[kind="primary"] button {
    background: var(--color-accent-primary-darker);
    color: var(--color-background-alt);
}

/* Fixed-size buttons for common actions */
div[kind="primary"] button {
    background: var(--color-accent-primary-darker);
    color: var(--color-background-alt);
}

/* Control spacing between buttons */
.stButton {
    margin: 0.25rem 0;
}

.stButton > button:hover {
    background: var(--color-accent-primary-darker);
    color: var(--color-background-alt);
}

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

.footer-links {
    margin-top: 1rem;
    display: flex;
    justify-content: center;
    gap: 1.5rem;
    flex-wrap: wrap;
}

.footer-links a {
    color: var(--color-accent-primary-darker);
    text-decoration: none;
    font-weight: 500;
    font-size: 0.85rem;
}

.footer-links a:hover {
    color: var(--color-footer-link-hover);
}

.brand-logo {
    display: flex;
    justify-content: center;
    margin: 0 auto 2.5rem auto;
    max-width: 640px;
    padding: 0.5rem 1rem 0 1rem;
}

.brand-logo img {
    width: 100%;
    height: auto;
    filter: drop-shadow(0 18px 36px rgba(180, 95, 77, 0.22));
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


.sidebar {
    padding: 1rem 0.75rem;
}

section[data-testid="stSidebar"] {
    background: var(--color-background);
}

section[data-testid="stSidebar"] .block-container {
    padding-top: 2rem;
}

/* Consistent sidebar cards */
.sidebar-card {
    background: var(--color-background-alt);
    border: 1px solid var(--color-border-light);
    border-radius: 12px;
    padding: 1.25rem;
    margin: 0 0 1rem 0;
}

/* Status indicators */
.status-card {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 1rem;
    background: var(--color-background-alt);
    border: 1px solid var(--color-border-light);
    border-radius: 8px;
    margin: 0.5rem 0;
}

.status-card__icon {
    width: 24px;
    height: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--color-accent-primary);
    border-radius: 6px;
    color: var(--color-text-primary);
}

.status-card__content {
    flex: 1;
}

.status-card__label {
    font-weight: 500;
    color: var(--color-text-primary);
    margin-bottom: 0.25rem;
    font-size: 0.9rem;
}

.status-card__value {
    color: var(--color-text-secondary);
    font-size: 0.85rem;
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

.section-card {
    background: var(--color-background-alt);
    border: 1px solid var(--color-border-light);
    border-radius: 12px;
    padding: 1.5rem;
    box-shadow: 0 8px 24px rgba(180, 95, 77, 0.08);
    margin-bottom: 1.5rem;
}

/* Card headers */
.section-card__header {
    margin-bottom: 1.25rem;
}

.section-card__header h3 {
    color: var(--color-text-primary);
    font-weight: 500;
    font-size: 1.1rem;
    margin: 0 0 0.5rem 0;
}

.section-card__header p {
    color: var(--color-text-secondary);
    font-size: 0.9rem;
    margin: 0;
    line-height: 1.4;
}

/* Input labels */
.text-label {
    display: block;
    margin: 1.25rem 0 0.5rem 0;
    font-weight: 500;
    font-size: 0.9rem;
    color: var(--color-text-primary);
}

/* Query input area */
.stTextArea > div > textarea {
    border-radius: 8px !important;
    border-color: var(--color-border-light) !important;
    padding: 0.75rem !important;
    font-size: 0.95rem !important;
    background: var(--color-background) !important;
    min-height: 100px !important;
}

/* Consistent button layout */
.button-container {
    display: flex !important;
    gap: 0.75rem !important;
    margin: 1rem 0 !important;
}

.button-container .stButton {
    flex: 1 !important;
}

.stButton > button {
    width: 100% !important;
    border-radius: 8px !important;
    padding: 0.75rem 1.25rem !important;
    height: 42px !important;
    font-weight: 500 !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    gap: 0.5rem !important;
}

/* Primary action button */
div[kind="primary"] button {
    background: var(--color-accent-primary-darker) !important;
    color: var(--color-background-alt) !important;
    border-color: var(--color-accent-primary-darker) !important;
}

/* Secondary action button */
button:not([kind="primary"]) {
    background: var(--color-background-alt) !important;
    color: var(--color-accent-primary-darker) !important;
    border-color: var(--color-border-light) !important;
}

.section-spacer {
    height: 2rem;
}

.results-card {
    background: var(--color-background-alt);
    border: 1px solid var(--color-border-light);
    border-radius: 18px;
    padding: 1.25rem 1.5rem;
    box-shadow: 0 12px 28px rgba(180, 95, 77, 0.10);
    margin: 1rem 0 1.5rem 0;
}
/* Results container */
.results-card {
    background: var(--color-background-alt);
    border: 1px solid var(--color-border-light);
    border-radius: 12px;
    padding: 1.5rem;
    margin: 1.5rem 0;
    box-shadow: 0 8px 24px rgba(180, 95, 77, 0.08);
    position: relative;
    left: 0;
    width: 100vw;
    margin-left: calc(-50vw + 50%);
    margin-right: calc(-50vw + 50%);
    max-width: 100vw;
}

/* Container for results content */
.results-card > div {
    max-width: 1360px;
    margin: 0 auto;
    padding: 0 1.75rem;
}

/* Results header and metrics */
.results-header {
    margin-bottom: 1.25rem;
    border-bottom: 1px solid var(--color-border-light);
    padding-bottom: 1.25rem;
}

.results-content {
    max-width: 1360px;
    margin: 0 auto;
    padding: 0 1.75rem;
}

.results-metrics {
    display: grid !important;
    grid-template-columns: repeat(4, 1fr) !important;
    gap: 1rem !important;
    margin: 1.25rem 0 1.5rem 0 !important;
}

/* Individual metric styling */
[data-testid="metric-container"] {
    background: var(--color-background) !important;
    border: 1px solid var(--color-border-light) !important;
    border-radius: 8px !important;
    padding: 0.75rem !important;
    text-align: center !important;
    height: 100% !important;
    transition: all 0.2s ease-in-out !important;
}

[data-testid="metric-container"]:hover {
    border-color: var(--color-accent-primary) !important;
    box-shadow: 0 4px 12px rgba(180, 95, 77, 0.1) !important;
}

[data-testid="metric-container"] label {
    font-size: 0.7rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
    color: var(--color-text-secondary) !important;
    margin-bottom: 0.25rem !important;
}

[data-testid="metric-container"] [data-testid="metric-value"] {
    font-size: 1.2rem !important;
    font-weight: 600 !important;
    color: var(--color-text-primary) !important;
}

[data-testid="metric-container"] [data-testid="stMetricDelta"] {
    color: var(--color-success-text) !important;
    font-size: 0.8rem !important;
    opacity: 0.9 !important;
}

/* Results table styling */
.results-card div[data-testid="stDataFrame"] {
    margin-top: 1rem !important;
    border: 1px solid var(--color-border-light) !important;
    border-radius: 8px !important;
    background: var(--color-background) !important;
}

/* Download button in metrics */
.results-card .stDownloadButton button {
    width: 100% !important;
    text-transform: uppercase !important;
    font-size: 0.7rem !important;
    letter-spacing: 0.05em !important;
    font-weight: 600 !important;
    background: var(--color-background) !important;
    color: var(--color-text-secondary) !important;
    border: 1px solid var(--color-border-light) !important;
    height: 100% !important;
    min-height: 42px !important;
}

.results-card [data-testid="metric-container"] label {
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: var(--color-text-secondary);
    font-weight: 500;
    margin-bottom: 0.25rem;
}

.results-card [data-testid="metric-container"] [data-testid="metric-value"] {
    font-size: 1.25rem;
    font-weight: 600;
    color: var(--color-text-primary);
    margin-top: 0.25rem;
}

.results-card [data-testid="metric-container"] div[data-testid="metric-value"] {
    font-size: 1.1rem;
    font-weight: 600;
    color: var(--color-text-primary);
    margin: 0.25rem 0;
}

/* Chart section styling */
.chart-section {
    background: var(--color-background);
    border: 1px solid var(--color-border-light);
    border-radius: 12px;
    padding: 1.5rem;
    margin: 1.5rem 0;
}

/* Chart controls styling */
.chart-controls {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    margin: 1rem 0;
}

.control-group {
    background: var(--color-background-alt);
    border: 1px solid var(--color-border-light);
    border-radius: 8px;
    padding: 1rem;
}

.control-group label {
    color: var(--color-text-primary);
    font-weight: 500;
    font-size: 0.9rem;
    margin-bottom: 0.25rem;
}

.disabled-control {
    opacity: 0.75;
    padding: 0.5rem;
    background: var(--color-background);
    border-radius: 6px;
}

.disabled-control label {
    display: block;
    color: var(--color-text-secondary);
    font-size: 0.875rem;
    font-weight: 500;
    margin-bottom: 0.25rem;
}

.disabled-control .info-text {
    color: var(--color-text-secondary);
    font-size: 0.8rem;
    font-style: italic;
    opacity: 0.9;
}

.disabled-control .info-text {
    color: var(--color-text-secondary);
    font-size: 0.8rem;
    font-style: italic;
}

/* Query control buttons */
.query-controls {
    display: flex;
    gap: 0.75rem;
    margin: 1rem 0;
}

.query-controls .stButton {
    flex: 1;
}

/* Consistent spacing for sections */
.section-spacer {
    height: 1.5rem;
}
</style>
""",
        unsafe_allow_html=True,
    )
