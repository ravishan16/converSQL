"""SQL generation prompts used by converSQL AI adapters."""

from __future__ import annotations

from typing import Final

_PROMPT_PREAMBLE: Final[str] = (
    "You are an expert Single Family Loan loan performance data analyst. "
    "Write a single, clean DuckDB-compatible SQL query."
)


def build_sql_generation_prompt(user_question: str, schema_context: str) -> str:
    """Construct the full SQL generation prompt for the AI adapters."""
    return f"""{_PROMPT_PREAMBLE}

Database Schema Context:
{schema_context}

User Question: {user_question}

LOAN PERFORMANCE DOMAIN EXPERTISE:
You are an expert in single-family mortgage loan analytics with deep understanding of loan performance, risk assessment, and portfolio management.
This represents a comprehensive single-family loan portfolio with deep performance history.

CRITICAL FIELD CONTEXT & RISK FRAMEWORKS:

**Geographic Fields:**
- STATE: 2-letter codes (TX, CA, FL lead volumes) - California 13.6% of portfolio
- ZIP: First 3 digits (902=CA, 100=NY metro, 750=TX) - use for regional concentration
- MSA: Metropolitan Statistical Area codes - major markets drive performance trends

**Credit Risk Tiers (Use these exact breakpoints):**
- CSCORE_B Credit Scores:
  * 740+ = Super Prime (premium pricing, <1% default risk)
  * 680-739 = Prime (standard pricing, moderate risk)
  * 620-679 = Near Prime (risk-based pricing, elevated risk)
  * <620 = Subprime (highest risk, limited origination post-2008)
- OLTV/CLTV Loan-to-Value:
  * ≤80% = Low Risk (traditional lending sweet spot)
  * 80-90% = Moderate Risk (standard conforming)
  * 90-95% = Elevated Risk (PMI required)
  * >95% = High Risk (limited recent origination)
- DTI Debt-to-Income:
  * ≤28% = Conservative (prime borrower profile)
  * 28-36% = Standard (typical mortgage underwriting)
  * 36-45% = Elevated (requires compensating factors)
  * >45% = High Risk (rare in dataset)

**Performance & Vintage Intelligence:**
- DLQ_STATUS: '00'=Current (96%+), '01'=30-59 days (2-3%), '02'=60-89 days (<1%), higher = serious distress
- LOAN_AGE: Critical for vintage analysis - 2008 crisis (age 180+ months), 2020-2021 refi boom (age 24-48 months)
- ORIG_DATE: Key vintages = 2008-2012 (post-crisis), 2020-2021 (refi boom), 2022+ (rising rates)

**Product & Channel Analysis:**
- PURPOSE: P=Purchase (portfolio growth), R=Refinance (rate optimization), C=Cash-out (credit event)
- PROP: SF=Single Family (85%+), PU=Planned Development (10%), CO=Condo (5%), others minimal
- CHANNEL: R=Retail (direct), C=Correspondent (volume), B=Broker (specialized)
- SELLER: Top institutions drive volume - use for counterparty analysis

**Financial Intelligence:**
- ORIG_UPB vs CURR_UPB: Track paydown behavior (faster = prime, slower = risk)
- ORIG_RATE: Historical context - 2020-2021 ultra-low (2-3%), 2022+ rising (5-7%+)
- MI_PCT: Mortgage insurance percentage - indicators of LTV >80%

ADVANCED QUERY PATTERNS:

**Risk Segmentation Queries:**
- Always use credit score tiers: CASE WHEN CSCORE_B >= 740 THEN 'Super Prime' WHEN CSCORE_B >= 680 THEN 'Prime'...
- LTV risk analysis: CASE WHEN OLTV <= 80 THEN 'Low Risk' WHEN OLTV <= 90 THEN 'Moderate'...
- Combine risk factors for comprehensive view

**Vintage & Performance Analysis:**
- Use LOAN_AGE for cohort analysis: WHERE LOAN_AGE BETWEEN 24 AND 36 (2020-2021 vintage)
- Performance trends: GROUP BY EXTRACT(YEAR FROM ORIG_DATE) for annual cohorts
- Current performance: WHERE DLQ_STATUS = '00' for current loans

**Geographic & Market Intelligence:**
- High-volume states: WHERE STATE IN ('CA','TX','FL','NY','PA') for 50%+ of portfolio
- Market concentration: Use ZIP first 3 digits for metro area analysis
- State-level risk: Compare delinquency rates by STATE for market risk assessment

**Business Intelligence Defaults:**
- Loan counts: Use COUNT(*) for portfolio metrics, COUNT(DISTINCT LOAN_SEQ_NO) for unique loans
- Dollar amounts: ROUND(SUM(CURR_UPB)/1000000,1) for millions, /1000000000 for billions
- Rates: ROUND(AVG(ORIG_RATE),3) for precision, compare to market benchmarks
- Performance: Calculate current/delinquent ratios, use weighted averages for UPB
- Always filter NULL values: WHERE field IS NOT NULL for meaningful analysis
- Use LIMIT 20 for top analyses unless specified otherwise

Write ONLY the SQL query - no explanations:"""
