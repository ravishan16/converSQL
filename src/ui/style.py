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
    padding: 1.25rem 1.75rem 1.75rem 1.75rem;
    background: var(--color-background);
    max-width: 1360px;
    margin: 0 auto;
}

.stTabs [data-baseweb="tab-list"] {
    gap: 0.5rem;
    background: none;
    border-bottom: 1px solid var(--color-border-light);
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
    padding: 0.6rem 1rem;
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


.sidebar-hero {
    margin: 0 0 1.5rem 0;
    padding: 1.35rem 1.2rem 1.4rem 1.2rem;
    background: var(--color-background-alt);
    border: 1px solid var(--color-border-light);
    border-radius: 16px;
    box-shadow: 0 10px 24px rgba(180, 95, 77, 0.12);
}

.sidebar-hero__eyebrow {
    display: block;
    color: var(--color-text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.18em;
    font-size: 0.7rem;
    margin-bottom: 0.55rem;
}

.sidebar-hero__title {
    color: var(--color-text-primary);
    font-weight: 500;
    font-size: 1.35rem;
    margin: 0 0 0.5rem 0;
}

.sidebar-hero__subhead {
    color: var(--color-text-secondary);
    font-size: 0.92rem;
    line-height: 1.4;
    margin: 0 0 0.75rem 0;
}

.sidebar-hero__pill {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.6rem 0.95rem;
    border-radius: 999px;
    background: rgba(221, 190, 169, 0.18);
    border: 1px solid rgba(221, 190, 169, 0.45);
    font-weight: 500;
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
    border-radius: 18px;
    padding: 1.25rem 1.25rem;
    box-shadow: 0 12px 28px rgba(180, 95, 77, 0.10);
    margin-bottom: 1.25rem;
}

.section-card__header h3 {
    color: var(--color-text-primary);
    font-weight: 400;
    margin-bottom: 0.5rem;
}

.section-card__header p {
    color: var(--color-text-secondary);
    font-size: 0.97rem;
    margin: 0;
}

.text-label {
    display: block;
    margin: 1.5rem 0 0.4rem 0;
    font-weight: 500;
    color: var(--color-text-primary);
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
.results-card div[data-testid="stDataFrame"] {
    padding-top: 0.5rem;
}
</style>
""",
        unsafe_allow_html=True,
    )
