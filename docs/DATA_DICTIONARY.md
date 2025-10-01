# Comprehensive Data Dictionary - Mortgage Loan Performance Dataset

**Dataset Overview:**
- Total Columns: 110
- Total Rows: 9,091,836
- File: `/Users/ravi/projects/git/converSQL/data/processed/data.parquet`
- Date Generated: September 15, 2025

## Column Categories and Complete Listing

### 1. LOAN IDENTIFIERS & POOL INFORMATION (7 columns)
| Column Name | Data Type | Description |
|-------------|-----------|-------------|
| POOL_ID | String | Pool identifier |
| LOAN_ID | String | Unique loan identifier |
| CHANNEL | String | Channel through which loan was originated |
| SELLER | String | Loan seller identifier |
| SERVICER | String | Current loan servicer |
| MASTER_SERVICER | String | Master servicer identifier |
| DEAL_NAME | String | Deal or transaction name |

### 2. DATES & TIME PERIODS (15 columns)
| Column Name | Data Type | Description |
|-------------|-----------|-------------|
| ACT_PERIOD | String | Activity period (MMYYYY format) |
| ORIG_DATE | String | Loan origination date |
| FIRST_PAY | String | First payment date |
| MATR_DT | String | Maturity date |
| ZB_DTE | String | Zero balance date |
| RPRCH_DTE | String | Repurchase date |
| LAST_PAID_INSTALLMENT_DATE | String | Last paid installment date |
| FORECLOSURE_DATE | String | Foreclosure date |
| DISPOSITION_DATE | String | Property disposition date |
| ORIGINAL_LIST_START_DATE | String | Original listing start date |
| CURRENT_LIST_START_DATE | String | Current listing start date |
| ZERO_BALANCE_CODE_CHANGE_DATE | String | Zero balance code change date |
| LOAN_HOLDBACK_EFFECTIVE_DATE | String | Loan holdback effective date |
| INTEREST_RATE_CHANGE_DATE | String | Interest rate change date |
| PAYMENT_CHANGE_DATE | String | Payment change date |

### 3. LOAN TERMS & STRUCTURE (13 columns)
| Column Name | Data Type | Description |
|-------------|-----------|-------------|
| ORIG_RATE | Float | Original interest rate |
| CURR_RATE | Float | Current interest rate |
| ORIG_TERM | Int16 | Original loan term in months |
| LOAN_AGE | Int16 | Current age of loan in months |
| REM_MONTHS | Int16 | Remaining months to maturity |
| ADJ_REM_MONTHS | Int16 | Adjusted remaining months |
| PURPOSE | String | Loan purpose (Purchase/Refinance) |
| PRODUCT | String | Product type |
| IO | String | Interest-only indicator |
| FIRST_PAY_IO | String | First payment interest-only |
| MNTHS_TO_AMTZ_IO | String | Months to amortize interest-only |
| BALLOON_INDICATOR | String | Balloon payment indicator |
| PLAN_NUMBER | String | Plan number |

### 4. UNPAID PRINCIPAL BALANCES (UPB) (8 columns)
| Column Name | Data Type | Description |
|-------------|-----------|-------------|
| ORIG_UPB | Double | Original unpaid principal balance |
| ISSUANCE_UPB | Double | Issuance unpaid principal balance |
| CURRENT_UPB | Double | Current unpaid principal balance |
| LAST_UPB | Double | Last unpaid principal balance |
| NON_INTEREST_BEARING_UPB | Double | Non-interest bearing UPB |
| INTEREST_BEARING_UPB | Double | Interest bearing UPB |
| ADR_UPB | Double | Alternative dispute resolution UPB |
| DELINQUENT_ACCRUED_INTEREST | Double | Delinquent accrued interest |

### 5. BORROWER CHARACTERISTICS (8 columns)
| Column Name | Data Type | Description |
|-------------|-----------|-------------|
| NUM_BO | String | Number of borrowers |
| DTI | Float | Debt-to-income ratio |
| CSCORE_B | Int16 | Credit score of borrower |
| CSCORE_C | Int16 | Credit score of co-borrower |
| ISSUE_SCOREB | Int16 | Issue credit score borrower |
| ISSUE_SCOREC | Int16 | Issue credit score co-borrower |
| CURR_SCOREB | Int16 | Current credit score borrower |
| CURR_SCOREC | Int16 | Current credit score co-borrower |

### 6. PROPERTY INFORMATION (8 columns)
| Column Name | Data Type | Description |
|-------------|-----------|-------------|
| PROP | String | Property type |
| NO_UNITS | Int8 | Number of units |
| OCC_STAT | String | Occupancy status |
| STATE | String | Property state |
| MSA | String | Metropolitan Statistical Area |
| ZIP | String | Property ZIP code |
| FIRST_FLAG | String | First-time homebuyer flag |
| HIGH_BALANCE_LOAN_INDICATOR | String | High balance loan indicator |

### 7. LOAN-TO-VALUE RATIOS (3 columns)
| Column Name | Data Type | Description |
|-------------|-----------|-------------|
| OLTV | Float | Original loan-to-value ratio |
| OCLTV | Float | Original combined loan-to-value ratio |
| MI_PCT | Float | Mortgage insurance percentage |

### 8. PAYMENT STATUS & DELINQUENCY (6 columns)
| Column Name | Data Type | Description |
|-------------|-----------|-------------|
| DLQ_STATUS | String | Delinquency status |
| PMT_HISTORY | String | Payment history |
| PPMT_FLG | String | Prepayment flag |
| Zero_Bal_Code | String | Zero balance code |
| FORBEARANCE_INDICATOR | String | Forbearance indicator |
| PAYMENT_DEFERRAL_MOD_EVENT_FLAG | String | Payment deferral modification event flag |

### 9. PRINCIPAL PAYMENTS & SCHEDULES (4 columns)
| Column Name | Data Type | Description |
|-------------|-----------|-------------|
| CURR_SCHD_PRNCPL | Double | Current scheduled principal |
| TOT_SCHD_PRNCPL | Double | Total scheduled principal |
| UNSCHD_PRNCPL_CURR | Double | Unscheduled principal current |
| PRINCIPAL_FORGIVENESS_AMOUNT | Double | Principal forgiveness amount |

### 10. FORECLOSURE & RECOVERY COSTS (9 columns)
| Column Name | Data Type | Description |
|-------------|-----------|-------------|
| FORECLOSURE_COSTS | Double | Foreclosure costs |
| PROPERTY_PRESERVATION_AND_REPAIR_COSTS | Double | Property preservation and repair costs |
| ASSET_RECOVERY_COSTS | Double | Asset recovery costs |
| MISCELLANEOUS_HOLDING_EXPENSES_AND_CREDITS | Double | Miscellaneous holding expenses and credits |
| ASSOCIATED_TAXES_FOR_HOLDING_PROPERTY | Double | Associated taxes for holding property |
| NET_SALES_PROCEEDS | Double | Net sales proceeds |
| CREDIT_ENHANCEMENT_PROCEEDS | Double | Credit enhancement proceeds |
| REPURCHASES_MAKE_WHOLE_PROCEEDS | Double | Repurchase make-whole proceeds |
| OTHER_FORECLOSURE_PROCEEDS | Double | Other foreclosure proceeds |

### 11. PROPERTY LISTING & SALES (4 columns)
| Column Name | Data Type | Description |
|-------------|-----------|-------------|
| ORIGINAL_LIST_PRICE | Double | Original listing price |
| CURRENT_LIST_PRICE | Double | Current listing price |
| FORECLOSURE_PRINCIPAL_WRITE_OFF_AMOUNT | Double | Foreclosure principal write-off amount |
| RE_PROCS_FLAG | String | Real estate proceeds flag |

### 12. MORTGAGE INSURANCE (3 columns)
| Column Name | Data Type | Description |
|-------------|-----------|-------------|
| MI_TYPE | String | Mortgage insurance type |
| MI_CANCEL_FLAG | String | Mortgage insurance cancellation flag |
| PROPERTY_INSPECTION_WAIVER_INDICATOR | String | Property inspection waiver indicator |

### 13. LOAN MODIFICATIONS & LOSSES (6 columns)
| Column Name | Data Type | Description |
|-------------|-----------|-------------|
| MOD_FLAG | String | Modification flag |
| CURRENT_PERIOD_MODIFICATION_LOSS_AMOUNT | Double | Current period modification loss amount |
| CUMULATIVE_MODIFICATION_LOSS_AMOUNT | Double | Cumulative modification loss amount |
| CURRENT_PERIOD_CREDIT_EVENT_NET_GAIN_OR_LOSS | Double | Current period credit event net gain/loss |
| CUMULATIVE_CREDIT_EVENT_NET_GAIN_OR_LOSS | Double | Cumulative credit event net gain/loss |
| LOAN_HOLDBACK_INDICATOR | String | Loan holdback indicator |

### 14. ARM (ADJUSTABLE RATE MORTGAGE) FEATURES (11 columns)
| Column Name | Data Type | Description |
|-------------|-----------|-------------|
| ARM_5_YR_INDICATOR | String | ARM 5-year indicator |
| ARM_PRODUCT_TYPE | String | ARM product type |
| MONTHS_UNTIL_FIRST_PAYMENT_RESET | Int16 | Months until first payment reset |
| MONTHS_BETWEEN_SUBSEQUENT_PAYMENT_RESET | Int16 | Months between subsequent payment reset |
| ARM_INDEX | String | ARM index type |
| ARM_CAP_STRUCTURE | String | ARM cap structure |
| INITIAL_INTEREST_RATE_CAP | Float | Initial interest rate cap |
| PERIODIC_INTEREST_RATE_CAP | Float | Periodic interest rate cap |
| LIFETIME_INTEREST_RATE_CAP | Float | Lifetime interest rate cap |
| MARGIN | Float | ARM margin |
| HIGH_LOAN_TO_VALUE_HLTV_REFINANCE_OPTION_INDICATOR | String | High LTV refinance option indicator |

### 15. SPECIAL PROGRAMS & INDICATORS (5 columns)
| Column Name | Data Type | Description |
|-------------|-----------|-------------|
| HOMEREADY_PROGRAM_INDICATOR | String | HomeReady program indicator |
| RELOCATION_MORTGAGE_INDICATOR | String | Relocation mortgage indicator |
| SERV_IND | String | Servicing indicator |
| ADR_TYPE | String | Alternative dispute resolution type |
| ADR_COUNT | Int16 | Alternative dispute resolution count |

## Data Type Summary
- **String/Text Columns:** 72 columns
- **Float Columns:** 25 columns
- **Integer Columns:** 13 columns
- **Total:** 110 columns

## Key Insights
1. This is a comprehensive mortgage loan performance dataset covering the full lifecycle of loans
2. Contains both origination data and performance/servicing data over time
3. Includes detailed foreclosure and loss mitigation information
4. Covers various loan products including ARM and special programs
5. Time series data with activity periods showing loan performance over time
6. Extensive coverage of financial metrics, costs, and recoveries

## Notes
- Date fields are in MMYYYY format (e.g., "012024" = January 2024)
- Many fields can be null/empty depending on loan status and applicability
- UPB = Unpaid Principal Balance
- ARM = Adjustable Rate Mortgage
- MI = Mortgage Insurance
- LTV = Loan-to-Value
- DTI = Debt-to-Income