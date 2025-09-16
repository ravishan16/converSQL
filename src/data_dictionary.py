#!/usr/bin/env python3
"""
Clean, ontological data dictionary for Single Family Loan performance data.
Provides structured loan performance ontology optimized for UI and AI model context.
Comprehensive coverage of all 110 columns with ACTUAL field names from data.
"""

import pandas as pd
import duckdb
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


# =============================================================================
# FIELD METADATA STRUCTURE
# =============================================================================

@dataclass
class FieldMetadata:
    """Standard field metadata structure for ontological organization."""
    description: str
    domain: str
    data_type: str
    business_context: str
    risk_impact: str = ""
    values: Optional[Dict[str, str]] = None
    relationships: Optional[List[str]] = None
    calculation: str = ""


# =============================================================================
# COMPREHENSIVE LOAN ONTOLOGY - ACTUAL 110 COLUMNS FROM DATA
# =============================================================================

LOAN_ONTOLOGY = {
    "IDENTIFICATION": {
        "domain_description": "Unique identifiers and pool information for loan tracking",
        "primary_key": "LOAN_ID",
        "fields": {
            "POOL_ID": FieldMetadata(
                description="Pool identifier grouping loans",
                domain="Identification",
                data_type="VARCHAR",
                business_context="Groups loans for portfolio management and risk analysis",
                relationships=["groups_loans_by_characteristics"]
            ),
            "LOAN_ID": FieldMetadata(
                description="Unique loan sequence number",
                domain="Identification",
                data_type="VARCHAR",
                business_context="Primary key for loan-level analysis and cross-file linkage",
                relationships=["primary_key", "links_acquisition_to_performance"]
            ),
            "CHANNEL": FieldMetadata(
                description="Current channel designation",
                domain="Identification",
                data_type="VARCHAR",
                business_context="Current portfolio channel classification"
            ),
            "SELLER": FieldMetadata(
                description="Original seller/lender identifier",
                domain="Identification",
                data_type="VARCHAR",
                business_context="Originator identification for quality assessment"
            ),
            "SERVICER": FieldMetadata(
                description="Current servicer identifier",
                domain="Identification",
                data_type="VARCHAR",
                business_context="Current servicer for performance attribution"
            ),
            "MASTER_SERVICER": FieldMetadata(
                description="Master servicer identifier",
                domain="Identification",
                data_type="VARCHAR",
                business_context="Master servicer overseeing loan administration"
            ),
            "DEAL_NAME": FieldMetadata(
                description="Securitization deal name",
                domain="Identification",
                data_type="VARCHAR",
                business_context="MBS pool or deal identification"
            )
        }
    },

    "TEMPORAL": {
        "domain_description": "Time dimensions covering loan lifecycle and performance periods",
        "fields": {
            "ACT_PERIOD": FieldMetadata(
                description="Activity period for performance data (MMYYYY)",
                domain="Temporal",
                data_type="VARCHAR",
                business_context="Reporting period for loan performance tracking",
                relationships=["time_series_key"]
            ),
            "ORIG_DATE": FieldMetadata(
                description="Original loan date (MMYYYY)",
                domain="Temporal",
                data_type="VARCHAR",
                business_context="Loan origination date for vintage analysis",
                relationships=["determines_vintage", "key_for_cohort_analysis"]
            ),
            "FIRST_PAY": FieldMetadata(
                description="First payment date (MMYYYY)",
                domain="Temporal",
                data_type="VARCHAR",
                business_context="First scheduled payment for age calculations"
            ),
            "MATR_DT": FieldMetadata(
                description="Loan maturity date (MMYYYY)",
                domain="Temporal",
                data_type="VARCHAR",
                business_context="Final scheduled payment date"
            ),
            "LAST_PAID_INSTALLMENT_DATE": FieldMetadata(
                description="Last paid installment date (MMYYYY)",
                domain="Temporal",
                data_type="VARCHAR",
                business_context="Most recent payment received date"
            ),
            "FORECLOSURE_DATE": FieldMetadata(
                description="Foreclosure date (MMYYYY)",
                domain="Temporal",
                data_type="VARCHAR",
                business_context="Date foreclosure proceedings started"
            ),
            "DISPOSITION_DATE": FieldMetadata(
                description="Property disposition date (MMYYYY)",
                domain="Temporal",
                data_type="VARCHAR",
                business_context="REO property sale completion date"
            ),
            "ZB_DTE": FieldMetadata(
                description="Zero balance date (MMYYYY)",
                domain="Temporal",
                data_type="VARCHAR",
                business_context="Date loan balance reached zero"
            ),
            "RPRCH_DTE": FieldMetadata(
                description="Repurchase date (MMYYYY)",
                domain="Temporal",
                data_type="VARCHAR",
                business_context="Date loan was repurchased from pool"
            ),
            "ORIGINAL_LIST_START_DATE": FieldMetadata(
                description="Original REO listing start date (MMYYYY)",
                domain="Temporal",
                data_type="VARCHAR",
                business_context="Initial REO property listing date"
            ),
            "CURRENT_LIST_START_DATE": FieldMetadata(
                description="Current REO listing start date (MMYYYY)",
                domain="Temporal",
                data_type="VARCHAR",
                business_context="Current REO listing period start date"
            ),
            "INTEREST_RATE_CHANGE_DATE": FieldMetadata(
                description="Interest rate change date (MMYYYY)",
                domain="Temporal",
                data_type="VARCHAR",
                business_context="Date of ARM rate adjustment"
            ),
            "PAYMENT_CHANGE_DATE": FieldMetadata(
                description="Payment change date (MMYYYY)",
                domain="Temporal",
                data_type="VARCHAR",
                business_context="Date of ARM payment adjustment"
            ),
            "ZERO_BALANCE_CODE_CHANGE_DATE": FieldMetadata(
                description="Zero balance code change date (MMYYYY)",
                domain="Temporal",
                data_type="VARCHAR",
                business_context="Date zero balance code was updated"
            ),
            "LOAN_HOLDBACK_EFFECTIVE_DATE": FieldMetadata(
                description="Loan holdback effective date (MMYYYY)",
                domain="Temporal",
                data_type="VARCHAR",
                business_context="Effective date of loan holdback"
            )
        }
    },

    "LOAN_TERMS": {
        "domain_description": "Core loan structure, terms, and product characteristics",
        "fields": {
            "ORIG_RATE": FieldMetadata(
                description="Original interest rate (%)",
                domain="Loan Terms",
                data_type="FLOAT",
                business_context="Origination rate affecting refinance propensity",
                risk_impact="Low rates create refinance risk when rates rise"
            ),
            "CURR_RATE": FieldMetadata(
                description="Current interest rate (%)",
                domain="Loan Terms",
                data_type="FLOAT",
                business_context="Current rate for ARM products"
            ),
            "ORIG_TERM": FieldMetadata(
                description="Original loan term (months)",
                domain="Loan Terms",
                data_type="SMALLINT",
                business_context="Original amortization period",
                values={"360": "30-year", "180": "15-year", "240": "20-year"}
            ),
            "REM_MONTHS": FieldMetadata(
                description="Remaining months to maturity",
                domain="Loan Terms",
                data_type="SMALLINT",
                business_context="Remaining term affects prepayment behavior"
            ),
            "ADJ_REM_MONTHS": FieldMetadata(
                description="Adjusted remaining months",
                domain="Loan Terms",
                data_type="SMALLINT",
                business_context="Adjusted remaining term calculation"
            ),
            "LOAN_AGE": FieldMetadata(
                description="Loan age in months since origination",
                domain="Loan Terms",
                data_type="SMALLINT",
                business_context="Seasoning indicator - defaults peak at 12-60 months",
                risk_impact="Early payment default risk highest in first 12 months"
            ),
            "PURPOSE": FieldMetadata(
                description="Loan purpose code",
                domain="Loan Terms",
                data_type="VARCHAR",
                business_context="Transaction type affecting risk",
                risk_impact="Purchase < Rate/Term Refi < Cash-Out Refi",
                values={
                    "P": "Purchase - Home acquisition",
                    "R": "Rate/Term Refinance",
                    "C": "Cash-Out Refinance"
                }
            ),
            "PRODUCT": FieldMetadata(
                description="Loan product type",
                domain="Loan Terms",
                data_type="VARCHAR",
                business_context="Product classification (FRM/ARM)"
            ),
            "IO": FieldMetadata(
                description="Interest-only indicator",
                domain="Loan Terms",
                data_type="VARCHAR",
                business_context="Interest-only payment feature"
            ),
            "FIRST_PAY_IO": FieldMetadata(
                description="First payment IO date",
                domain="Loan Terms",
                data_type="VARCHAR",
                business_context="First interest-only payment date"
            ),
            "MNTHS_TO_AMTZ_IO": FieldMetadata(
                description="Months to amortize IO",
                domain="Loan Terms",
                data_type="VARCHAR",
                business_context="Months until IO converts to amortizing"
            ),
            "PPMT_FLG": FieldMetadata(
                description="Prepayment penalty flag",
                domain="Loan Terms",
                data_type="VARCHAR",
                business_context="Indicates presence of prepayment penalty"
            ),
            "BALLOON_INDICATOR": FieldMetadata(
                description="Balloon payment indicator",
                domain="Loan Terms",
                data_type="VARCHAR",
                business_context="Indicates balloon payment feature"
            ),
            "PLAN_NUMBER": FieldMetadata(
                description="Plan number identifier",
                domain="Loan Terms",
                data_type="VARCHAR",
                business_context="Internal plan classification"
            )
        }
    },

    "UNPAID_BALANCES": {
        "domain_description": "All unpaid principal balance measurements and calculations",
        "fields": {
            "ORIG_UPB": FieldMetadata(
                description="Original unpaid principal balance ($)",
                domain="Unpaid Balances",
                data_type="DOUBLE",
                business_context="Original loan amount determining jumbo status",
                relationships=["baseline_for_balance_tracking"]
            ),
            "CURRENT_UPB": FieldMetadata(
                description="Current unpaid principal balance ($)",
                domain="Unpaid Balances",
                data_type="DOUBLE",
                business_context="Current outstanding balance for exposure calculation"
            ),
            "ISSUANCE_UPB": FieldMetadata(
                description="UPB at MBS issuance ($)",
                domain="Unpaid Balances",
                data_type="DOUBLE",
                business_context="Balance when securitized into MBS"
            ),
            "LAST_UPB": FieldMetadata(
                description="Last unpaid principal balance ($)",
                domain="Unpaid Balances",
                data_type="DOUBLE",
                business_context="Final UPB before zero balance"
            ),
            "NON_INTEREST_BEARING_UPB": FieldMetadata(
                description="Non-interest bearing UPB ($)",
                domain="Unpaid Balances",
                data_type="DOUBLE",
                business_context="Principal not accruing interest"
            ),
            "INTEREST_BEARING_UPB": FieldMetadata(
                description="Interest bearing UPB ($)",
                domain="Unpaid Balances",
                data_type="DOUBLE",
                business_context="Principal accruing interest"
            )
        }
    },

    "BORROWER_PROFILE": {
        "domain_description": "Borrower characteristics and creditworthiness indicators",
        "fields": {
            "CSCORE_B": FieldMetadata(
                description="Primary borrower credit score",
                domain="Borrower Profile",
                data_type="SMALLINT",
                business_context="Primary credit quality indicator",
                risk_impact="740+ Super Prime vs <620 Subprime - 10x default difference",
                values={
                    "740+": "Super Prime",
                    "680-739": "Prime",
                    "620-679": "Near Prime",
                    "<620": "Subprime"
                }
            ),
            "CSCORE_C": FieldMetadata(
                description="Co-borrower credit score",
                domain="Borrower Profile",
                data_type="SMALLINT",
                business_context="Secondary borrower credit quality"
            ),
            "CURR_SCOREB": FieldMetadata(
                description="Current primary borrower credit score",
                domain="Borrower Profile",
                data_type="SMALLINT",
                business_context="Updated primary borrower credit score"
            ),
            "CURR_SCOREC": FieldMetadata(
                description="Current co-borrower credit score",
                domain="Borrower Profile",
                data_type="SMALLINT",
                business_context="Updated co-borrower credit score"
            ),
            "ISSUE_SCOREB": FieldMetadata(
                description="Issue date primary borrower credit score",
                domain="Borrower Profile",
                data_type="SMALLINT",
                business_context="Primary borrower score at MBS issuance"
            ),
            "ISSUE_SCOREC": FieldMetadata(
                description="Issue date co-borrower credit score",
                domain="Borrower Profile",
                data_type="SMALLINT",
                business_context="Co-borrower score at MBS issuance"
            ),
            "DTI": FieldMetadata(
                description="Debt-to-income ratio (%)",
                domain="Borrower Profile",
                data_type="FLOAT",
                business_context="Payment capacity measure",
                risk_impact="≤36% standard vs >43% stressed capacity",
                values={
                    "≤28%": "Conservative capacity",
                    "29-36%": "Standard capacity",
                    "37-43%": "Stretched capacity",
                    ">43%": "Aggressive capacity"
                }
            ),
            "NUM_BO": FieldMetadata(
                description="Number of borrowers",
                domain="Borrower Profile",
                data_type="VARCHAR",
                business_context="Count of borrowers on loan (1 or 2)"
            ),
            "FIRST_FLAG": FieldMetadata(
                description="First-time homebuyer flag",
                domain="Borrower Profile",
                data_type="VARCHAR",
                business_context="Indicates first-time homebuyer status"
            )
        }
    },

    "PROPERTY_INFO": {
        "domain_description": "Property characteristics, location, and collateral information",
        "fields": {
            "PROP": FieldMetadata(
                description="Property type code",
                domain="Property Info",
                data_type="VARCHAR",
                business_context="Physical property classification",
                values={
                    "SF": "Single Family - Lowest risk",
                    "PU": "Planned Unit Development",
                    "CO": "Condominium",
                    "MH": "Manufactured Housing - Highest risk"
                }
            ),
            "NO_UNITS": FieldMetadata(
                description="Number of units in property",
                domain="Property Info",
                data_type="TINYINT",
                business_context="Property unit count affects classification"
            ),
            "OCC_STAT": FieldMetadata(
                description="Occupancy status code",
                domain="Property Info",
                data_type="VARCHAR",
                business_context="Property usage affecting payment priority",
                values={
                    "P": "Primary residence - Lowest risk",
                    "S": "Second home",
                    "I": "Investment property - Highest risk"
                }
            ),
            "STATE": FieldMetadata(
                description="State code",
                domain="Property Info",
                data_type="VARCHAR",
                business_context="State location for geographic risk assessment"
            ),
            "MSA": FieldMetadata(
                description="Metropolitan Statistical Area code",
                domain="Property Info",
                data_type="VARCHAR",
                business_context="MSA classification for market analysis"
            ),
            "ZIP": FieldMetadata(
                description="Property ZIP code (3 digits)",
                domain="Property Info",
                data_type="VARCHAR",
                business_context="Geographic location (privacy protected to 3 digits)"
            )
        }
    },

    "LTV_RATIOS": {
        "domain_description": "Loan-to-value ratios and equity position metrics",
        "fields": {
            "OLTV": FieldMetadata(
                description="Original loan-to-value ratio (%)",
                domain="LTV Ratios",
                data_type="FLOAT",
                business_context="Original equity position - key loss predictor",
                risk_impact="≤80% Conservative vs >95% High Risk",
                values={
                    "≤80%": "Conservative equity",
                    "81-90%": "Standard equity",
                    "91-95%": "Minimal equity",
                    ">95%": "High risk - very limited equity"
                }
            ),
            "OCLTV": FieldMetadata(
                description="Original combined LTV (%)",
                domain="LTV Ratios",
                data_type="FLOAT",
                business_context="Combined LTV including subordinate liens"
            ),
            "MI_PCT": FieldMetadata(
                description="Mortgage insurance percentage (%)",
                domain="LTV Ratios",
                data_type="FLOAT",
                business_context="MI coverage percentage for high LTV loans"
            )
        }
    },

    "PAYMENT_STATUS": {
        "domain_description": "Payment performance and delinquency status tracking",
        "fields": {
            "DLQ_STATUS": FieldMetadata(
                description="Current delinquency status code",
                domain="Payment Status",
                data_type="VARCHAR",
                business_context="Payment performance indicator - 98%+ current in portfolio",
                values={
                    "00": "Current - No missed payments",
                    "01": "30-59 Days - First delinquency",
                    "02": "60-89 Days - Serious delinquency",
                    "03": "90+ Days - Severe delinquency"
                }
            ),
            "PMT_HISTORY": FieldMetadata(
                description="Payment history string",
                domain="Payment Status",
                data_type="VARCHAR",
                business_context="Coded payment performance history"
            ),
            "MOD_FLAG": FieldMetadata(
                description="Modification flag",
                domain="Payment Status",
                data_type="VARCHAR",
                business_context="Loan modification indicator"
            ),
            "DELINQUENT_ACCRUED_INTEREST": FieldMetadata(
                description="Delinquent accrued interest amount ($)",
                domain="Payment Status",
                data_type="DOUBLE",
                business_context="Unpaid interest accumulation"
            ),
            "FORBEARANCE_INDICATOR": FieldMetadata(
                description="Forbearance indicator",
                domain="Payment Status",
                data_type="VARCHAR",
                business_context="Temporary payment relief status"
            ),
            "PAYMENT_DEFERRAL_MOD_EVENT_FLAG": FieldMetadata(
                description="Payment deferral modification event flag",
                domain="Payment Status",
                data_type="VARCHAR",
                business_context="Payment deferral modification indicator"
            )
        }
    },

    "PRINCIPAL_PAYMENTS": {
        "domain_description": "Scheduled and unscheduled principal payment tracking",
        "fields": {
            "CURR_SCHD_PRNCPL": FieldMetadata(
                description="Current scheduled principal ($)",
                domain="Principal Payments",
                data_type="DOUBLE",
                business_context="Current month scheduled principal payment"
            ),
            "TOT_SCHD_PRNCPL": FieldMetadata(
                description="Total scheduled principal ($)",
                domain="Principal Payments",
                data_type="DOUBLE",
                business_context="Cumulative scheduled principal payments"
            ),
            "UNSCHD_PRNCPL_CURR": FieldMetadata(
                description="Current unscheduled principal ($)",
                domain="Principal Payments",
                data_type="DOUBLE",
                business_context="Extra principal payments this period"
            ),
            "PRINCIPAL_FORGIVENESS_AMOUNT": FieldMetadata(
                description="Principal forgiveness amount ($)",
                domain="Principal Payments",
                data_type="DOUBLE",
                business_context="Principal amount forgiven in modification"
            )
        }
    },

    "FORECLOSURE_COSTS": {
        "domain_description": "All foreclosure-related costs and expenses",
        "fields": {
            "FORECLOSURE_COSTS": FieldMetadata(
                description="Total foreclosure costs ($)",
                domain="Foreclosure Costs",
                data_type="DOUBLE",
                business_context="Direct foreclosure legal and processing costs"
            ),
            "PROPERTY_PRESERVATION_AND_REPAIR_COSTS": FieldMetadata(
                description="Property preservation and repair costs ($)",
                domain="Foreclosure Costs",
                data_type="DOUBLE",
                business_context="Maintenance and repair costs for REO properties"
            ),
            "ASSET_RECOVERY_COSTS": FieldMetadata(
                description="Asset recovery costs ($)",
                domain="Foreclosure Costs",
                data_type="DOUBLE",
                business_context="Costs to recover and sell REO property"
            ),
            "MISCELLANEOUS_HOLDING_EXPENSES_AND_CREDITS": FieldMetadata(
                description="Miscellaneous holding expenses and credits ($)",
                domain="Foreclosure Costs",
                data_type="DOUBLE",
                business_context="Other holding costs and credits"
            ),
            "ASSOCIATED_TAXES_FOR_HOLDING_PROPERTY": FieldMetadata(
                description="Associated taxes for holding property ($)",
                domain="Foreclosure Costs",
                data_type="DOUBLE",
                business_context="Property taxes while REO"
            ),
            "FORECLOSURE_PRINCIPAL_WRITE_OFF_AMOUNT": FieldMetadata(
                description="Foreclosure principal write-off amount ($)",
                domain="Foreclosure Costs",
                data_type="DOUBLE",
                business_context="Principal amount written off in foreclosure"
            )
        }
    },

    "PROPERTY_DISPOSITION": {
        "domain_description": "REO property listing, sale, and disposition information",
        "fields": {
            "ORIGINAL_LIST_PRICE": FieldMetadata(
                description="Original REO listing price ($)",
                domain="Property Disposition",
                data_type="DOUBLE",
                business_context="Initial REO property listing price"
            ),
            "CURRENT_LIST_PRICE": FieldMetadata(
                description="Current REO listing price ($)",
                domain="Property Disposition",
                data_type="DOUBLE",
                business_context="Current REO property listing price"
            ),
            "NET_SALES_PROCEEDS": FieldMetadata(
                description="Net sales proceeds ($)",
                domain="Property Disposition",
                data_type="DOUBLE",
                business_context="Net proceeds after costs from REO sale"
            ),
            "CREDIT_ENHANCEMENT_PROCEEDS": FieldMetadata(
                description="Credit enhancement proceeds ($)",
                domain="Property Disposition",
                data_type="DOUBLE",
                business_context="Proceeds from credit enhancement"
            ),
            "REPURCHASES_MAKE_WHOLE_PROCEEDS": FieldMetadata(
                description="Repurchase make-whole proceeds ($)",
                domain="Property Disposition",
                data_type="DOUBLE",
                business_context="Make-whole payments from repurchases"
            ),
            "OTHER_FORECLOSURE_PROCEEDS": FieldMetadata(
                description="Other foreclosure proceeds ($)",
                domain="Property Disposition",
                data_type="DOUBLE",
                business_context="Other recovery proceeds from foreclosure"
            ),
            "RE_PROCS_FLAG": FieldMetadata(
                description="REO proceeds flag",
                domain="Property Disposition",
                data_type="VARCHAR",
                business_context="REO proceeds processing indicator"
            )
        }
    },

    "MORTGAGE_INSURANCE": {
        "domain_description": "Mortgage insurance coverage and cancellation tracking",
        "fields": {
            "MI_TYPE": FieldMetadata(
                description="Mortgage insurance type",
                domain="Mortgage Insurance",
                data_type="VARCHAR",
                business_context="Type of mortgage insurance coverage",
                values={
                    "1": "Borrower-paid monthly MI",
                    "2": "Lender-paid MI",
                    "3": "Split premium MI"
                }
            ),
            "MI_CANCEL_FLAG": FieldMetadata(
                description="MI cancellation flag",
                domain="Mortgage Insurance",
                data_type="VARCHAR",
                business_context="Mortgage insurance cancellation status"
            )
        }
    },

    "MODIFICATIONS_LOSSES": {
        "domain_description": "Loan modifications and realized loss amounts",
        "fields": {
            "CURRENT_PERIOD_MODIFICATION_LOSS_AMOUNT": FieldMetadata(
                description="Current period modification loss amount ($)",
                domain="Modifications & Losses",
                data_type="DOUBLE",
                business_context="Modification loss recognized this period"
            ),
            "CUMULATIVE_MODIFICATION_LOSS_AMOUNT": FieldMetadata(
                description="Cumulative modification loss amount ($)",
                domain="Modifications & Losses",
                data_type="DOUBLE",
                business_context="Total modification losses to date"
            ),
            "CURRENT_PERIOD_CREDIT_EVENT_NET_GAIN_OR_LOSS": FieldMetadata(
                description="Current period credit event net gain/loss ($)",
                domain="Modifications & Losses",
                data_type="DOUBLE",
                business_context="Net credit event impact this period"
            ),
            "CUMULATIVE_CREDIT_EVENT_NET_GAIN_OR_LOSS": FieldMetadata(
                description="Cumulative credit event net gain/loss ($)",
                domain="Modifications & Losses",
                data_type="DOUBLE",
                business_context="Cumulative credit event net impact"
            )
        }
    },

    "ARM_FEATURES": {
        "domain_description": "Adjustable Rate Mortgage specific characteristics",
        "fields": {
            "ARM_5_YR_INDICATOR": FieldMetadata(
                description="ARM 5-year indicator",
                domain="ARM Features",
                data_type="VARCHAR",
                business_context="Indicates 5-year ARM product"
            ),
            "ARM_PRODUCT_TYPE": FieldMetadata(
                description="ARM product type",
                domain="ARM Features",
                data_type="VARCHAR",
                business_context="Specific ARM product classification"
            ),
            "MONTHS_UNTIL_FIRST_PAYMENT_RESET": FieldMetadata(
                description="Months until first payment reset",
                domain="ARM Features",
                data_type="SMALLINT",
                business_context="Months until first ARM payment adjustment"
            ),
            "MONTHS_BETWEEN_SUBSEQUENT_PAYMENT_RESET": FieldMetadata(
                description="Months between subsequent payment resets",
                domain="ARM Features",
                data_type="SMALLINT",
                business_context="Months between subsequent ARM adjustments"
            ),
            "ARM_INDEX": FieldMetadata(
                description="ARM index type",
                domain="ARM Features",
                data_type="VARCHAR",
                business_context="Reference rate index for ARM adjustments"
            ),
            "ARM_CAP_STRUCTURE": FieldMetadata(
                description="ARM cap structure",
                domain="ARM Features",
                data_type="VARCHAR",
                business_context="ARM rate cap structure definition"
            ),
            "INITIAL_INTEREST_RATE_CAP": FieldMetadata(
                description="Initial interest rate cap (%)",
                domain="ARM Features",
                data_type="FLOAT",
                business_context="Initial rate adjustment cap limit"
            ),
            "PERIODIC_INTEREST_RATE_CAP": FieldMetadata(
                description="Periodic interest rate cap (%)",
                domain="ARM Features",
                data_type="FLOAT",
                business_context="Periodic rate adjustment cap limit"
            ),
            "LIFETIME_INTEREST_RATE_CAP": FieldMetadata(
                description="Lifetime interest rate cap (%)",
                domain="ARM Features",
                data_type="FLOAT",
                business_context="Maximum rate increase over loan life"
            ),
            "MARGIN": FieldMetadata(
                description="ARM margin (%)",
                domain="ARM Features",
                data_type="FLOAT",
                business_context="Fixed margin added to ARM index rate"
            )
        }
    },

    "SPECIAL_INDICATORS": {
        "domain_description": "Special programs and servicing indicators",
        "fields": {
            "SERV_IND": FieldMetadata(
                description="Servicing indicator",
                domain="Special Indicators",
                data_type="VARCHAR",
                business_context="Special servicing status or programs"
            ),
            "HOMEREADY_PROGRAM_INDICATOR": FieldMetadata(
                description="HomeReady program indicator",
                domain="Special Indicators",
                data_type="VARCHAR",
                business_context="Affordable housing program participation"
            ),
            "RELOCATION_MORTGAGE_INDICATOR": FieldMetadata(
                description="Relocation mortgage indicator",
                domain="Special Indicators",
                data_type="VARCHAR",
                business_context="Employee relocation benefit program"
            ),
            "LOAN_HOLDBACK_INDICATOR": FieldMetadata(
                description="Loan holdback indicator",
                domain="Special Indicators",
                data_type="VARCHAR",
                business_context="Loan holdback status indicator"
            ),
            "PROPERTY_INSPECTION_WAIVER_INDICATOR": FieldMetadata(
                description="Property inspection waiver indicator",
                domain="Special Indicators",
                data_type="VARCHAR",
                business_context="Property inspection waiver status"
            ),
            "HIGH_BALANCE_LOAN_INDICATOR": FieldMetadata(
                description="High balance loan indicator",
                domain="Special Indicators",
                data_type="VARCHAR",
                business_context="High-cost area conforming loan designation"
            ),
            "HIGH_LOAN_TO_VALUE_HLTV_REFINANCE_OPTION_INDICATOR": FieldMetadata(
                description="High LTV refinance option indicator",
                domain="Special Indicators",
                data_type="VARCHAR",
                business_context="HLTV refinance program indicator"
            ),
            "Zero_Bal_Code": FieldMetadata(
                description="Zero balance code",
                domain="Special Indicators",
                data_type="VARCHAR",
                business_context="Loan termination reason code",
                values={
                    "01": "Prepayment - Normal payoff",
                    "02": "Third party sale - Foreclosure auction",
                    "03": "Short sale - Negotiated sale",
                    "09": "REO disposition - Bank-owned sale"
                }
            ),
            "ADR_TYPE": FieldMetadata(
                description="Alternative disposition type",
                domain="Special Indicators",
                data_type="VARCHAR",
                business_context="Alternative disposition method"
            ),
            "ADR_COUNT": FieldMetadata(
                description="Alternative disposition count",
                domain="Special Indicators",
                data_type="SMALLINT",
                business_context="Count of alternative dispositions"
            ),
            "ADR_UPB": FieldMetadata(
                description="Alternative disposition UPB ($)",
                domain="Special Indicators",
                data_type="DOUBLE",
                business_context="UPB for alternative disposition"
            )
        }
    }
}


# =============================================================================
# PORTFOLIO INTELLIGENCE & BUSINESS CONTEXT
# =============================================================================

PORTFOLIO_CONTEXT = {
    "overview": {
        "description": "Single Family Loan Single-Family Loan Performance Dataset",
        "coverage": "56.8+ million loans worth $12.4+ trillion original UPB",
        "vintage_range": "1999-2025 loan originations",
        "geographic_scope": "All 50 states plus District of Columbia",
        "update_frequency": "Monthly performance data through March 2025"
    },

    "performance_summary": {
        "lifetime_loss_rate": "0.3% of original UPB",
        "current_performance": "~98% of active loans current on payments",
        "credit_quality": "Average FICO 762 (borrower), 758 (co-borrower)",
        "leverage_metrics": "Average LTV 71.8%, Average DTI 34.5%",
        "seasoning_impact": "Default risk peaks at 12-60 months loan age"
    },

    "risk_framework": {
        "credit_triangle": "CSCORE_B (Credit) + OLTV (Collateral) + DTI (Capacity)",
        "risk_tiers": {
            "super_prime": "FICO 740+ AND LTV ≤80% AND DTI ≤36%",
            "prime": "FICO 680-739 with compensating factors",
            "alt_a": "One degraded factor with compensating strengths",
            "high_risk": "Multiple degraded factors (rare post-2008)"
        }
    },

    "analytical_dimensions": [
        "Vintage cohort analysis by ORIG_DATE",
        "Geographic concentration by STATE (state-level risk)",
        "Credit migration tracking via PMT_HISTORY",
        "Loss severity prediction by Zero_Bal_Code",
        "Prepayment modeling using rate differential",
        "ARM performance during rate cycles"
    ],

    "key_relationships": {
        "credit_collateral": "CSCORE_B inversely correlated with OLTV",
        "capacity_leverage": "DTI directly impacts delinquency probability",
        "geography_performance": "STATE concentration affects portfolio risk",
        "vintage_cycles": "ORIG_DATE correlates with economic cycle",
        "seasoning_curves": "Default probability varies by LOAN_AGE",
        "rate_sensitivity": "ARM products sensitive to index movements"
    }
}


def generate_enhanced_schema_context(parquet_files):
    """Generate clean, ontological schema context optimized for AI and UI consumption."""

    if not parquet_files:
        return "-- No data files available"

    try:
        conn = duckdb.connect()

        # Build comprehensive schema with ontological organization
        schema_context = f"""
-- ===================================================================
-- SINGLE FAMILY LOAN PERFORMANCE DATA - ONTOLOGICAL SCHEMA
-- ===================================================================
-- Portfolio: {PORTFOLIO_CONTEXT['overview']['coverage']}
-- Vintage: {PORTFOLIO_CONTEXT['overview']['vintage_range']}
-- Geography: {PORTFOLIO_CONTEXT['overview']['geographic_scope']}
-- Performance: {PORTFOLIO_CONTEXT['performance_summary']['lifetime_loss_rate']} lifetime loss rate
-- Credit Quality: {PORTFOLIO_CONTEXT['performance_summary']['credit_quality']}

-- RISK ASSESSMENT FRAMEWORK:
-- {PORTFOLIO_CONTEXT['risk_framework']['credit_triangle']}
-- Super Prime: {PORTFOLIO_CONTEXT['risk_framework']['risk_tiers']['super_prime']}
-- Prime: {PORTFOLIO_CONTEXT['risk_framework']['risk_tiers']['prime']}

"""

        # Generate table schema with ontological grouping
        for file_path in parquet_files:
            table_name = os.path.splitext(os.path.basename(file_path))[0]

            # Get actual schema from file
            query = f"DESCRIBE SELECT * FROM '{file_path}' LIMIT 1"
            schema_df = conn.execute(query).fetchdf()

            schema_context += f"""
-- ===================================================================
-- TABLE: {table_name.upper()} - ONTOLOGICALLY ORGANIZED
-- ===================================================================

CREATE TABLE {table_name} (
"""

            # Organize columns by ontological domains
            organized_columns = []
            unmapped_columns = []

            for domain_name, domain_info in LOAN_ONTOLOGY.items():
                domain_columns = []
                for _, row in schema_df.iterrows():
                    column_name = row['column_name']
                    column_type = row['column_type']

                    if column_name in domain_info['fields']:
                        field_meta = domain_info['fields'][column_name]
                        comment = f"-- {field_meta.description} | {field_meta.domain}"
                        if field_meta.risk_impact:
                            comment += f" | Risk: {field_meta.risk_impact}"
                        domain_columns.append(f"    {column_name} {column_type} {comment}")

                if domain_columns:
                    organized_columns.append(f"    -- {domain_name}: {domain_info['domain_description']}")
                    organized_columns.extend(domain_columns)
                    organized_columns.append("")

            # Add any unmapped columns
            for _, row in schema_df.iterrows():
                column_name = row['column_name']
                column_type = row['column_type']

                # Check if column exists in any domain
                found = False
                for domain_info in LOAN_ONTOLOGY.values():
                    if column_name in domain_info['fields']:
                        found = True
                        break

                if not found:
                    unmapped_columns.append(f"    {column_name} {column_type} -- {column_name.replace('_', ' ').title()}")

            if unmapped_columns:
                organized_columns.append("    -- OTHER FIELDS:")
                organized_columns.extend(unmapped_columns)

            # Join columns and complete table definition
            schema_context += "\n".join([col for col in organized_columns if col.strip()])
            schema_context += "\n);\n"

        conn.close()

        # Add business intelligence context
        schema_context += f"""

-- ===================================================================
-- BUSINESS INTELLIGENCE & ANALYTICAL GUIDANCE
-- ===================================================================

-- KEY PERFORMANCE INDICATORS:
-- • Portfolio Health: COUNT(*) WHERE DLQ_STATUS = '00' / COUNT(*)
-- • Credit Quality Distribution: COUNT(*) GROUP BY CSCORE_B ranges
-- • Geographic Concentration: SUM(CURRENT_UPB) GROUP BY STATE
-- • Vintage Performance: Default rates GROUP BY SUBSTR(ORIG_DATE,3,4)
-- • Loss Severity: Analysis using foreclosure costs and proceeds

-- ANALYTICAL QUERY PATTERNS:
-- Credit Risk: SELECT CASE WHEN CSCORE_B >= 740 THEN 'Super Prime' WHEN CSCORE_B >= 680 THEN 'Prime' ELSE 'Subprime' END, COUNT(*)
-- Geographic: SELECT STATE, COUNT(*), SUM(CURRENT_UPB)/1000000 as UPB_MM FROM data GROUP BY STATE ORDER BY UPB_MM DESC
-- Vintage: SELECT ORIG_DATE, COUNT(*), AVG(CSCORE_B), AVG(OLTV) FROM data GROUP BY ORIG_DATE ORDER BY ORIG_DATE
-- Performance: SELECT DLQ_STATUS, COUNT(*) FROM data GROUP BY DLQ_STATUS

-- DOMAIN RELATIONSHIPS:
{chr(10).join([f"-- • {rel}" for rel in PORTFOLIO_CONTEXT['analytical_dimensions']])}

"""

        return schema_context

    except Exception as e:
        return f"-- Error generating schema: {str(e)}"


# Legacy compatibility functions
def get_field_context(field_name):
    """Get context for a specific field (legacy compatibility)."""
    for domain in LOAN_ONTOLOGY.values():
        if field_name in domain['fields']:
            return domain['fields'][field_name].__dict__
    return {}

def get_analysis_suggestions(field_names):
    """Get analysis suggestions based on field names (legacy compatibility)."""
    suggestions = []
    for field in field_names:
        field_info = get_field_context(field)
        if field_info and 'business_context' in field_info:
            suggestions.append(f"{field}: {field_info['business_context']}")
    return suggestions[:10]  # Limit to 10 suggestions