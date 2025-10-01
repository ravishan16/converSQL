# Data Pipeline Documentation

## Overview

The **converSQL Single Family Loan Analytics** showcase implementation demonstrates a complete, production-grade data engineering pipeline. This document details how we transform Fannie Mae's public loan performance data from raw pipe-separated files into a high-performance analytical data store.

---

## Data Source: Fannie Mae Single Family Loan Performance Data

### What is This Data?

Fannie Mae's [Single Family Loan Performance Data](https://capitalmarkets.fanniemae.com/tools-applications/data-dynamics) represents one of the most comprehensive public datasets on U.S. residential mortgage markets. Released under Fannie Mae's open data initiative, it provides loan-level detail on millions of mortgages, enabling researchers, analysts, and developers to study mortgage credit risk, housing finance, and loan performance trends.

### Data Characteristics

- **Scale**: 9+ million loan records in our sample dataset
- **Columns**: 110 fields covering identification, origination, property, borrower, and performance data
- **Time Span**: Vintages from 2000s through recent years, with monthly performance updates
- **Format**: Pipe-separated text files (`.txt` with `|` delimiter)
- **Updates**: Quarterly releases with new originations and updated performance data

### Key Data Domains

The dataset is organized into rich ontological domains:

1. **Identification** (7 fields): Loan IDs, pool identifiers, servicer information
2. **Temporal** (15 fields): Origination dates, maturity dates, reporting periods
3. **Loan Terms** (13 fields): Interest rates, loan terms, product types
4. **Financial** (8 fields): Unpaid principal balances (UPB), accrued interest
5. **Borrower Profile** (8 fields): Credit scores (FICO), debt-to-income ratios
6. **Property** (8 fields): Property types, occupancy, geographic location
7. **Credit Risk** (3 fields): Loan-to-value ratios (LTV), combined LTV, mortgage insurance
8. **Performance** (6 fields): Delinquency status, default indicators
9. **Modifications** (7 fields): Loan modification history and terms
10. **Loss Events** (14 fields): Foreclosure, REO, and disposition tracking
11. **Geographic** (multiple): State, MSA, ZIP codes
12. **Pricing** (6 fields): Interest rate components and adjustments
13. **Servicing** (8 fields): Servicer transfers, fees, escrow balances
14. **Special Features** (multiple): High balance loans, first-time buyers, special programs
15. **Calculations** (derived): Loan age, remaining terms, vintage cohorts

---

## Pipeline Architecture

### High-Level Flow

```
┌─────────────────────┐
│  Raw Data Source    │
│  (Fannie Mae .txt)  │
│  Pipe-separated     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Ingestion Layer    │
│  - Download/Sync    │
│  - Validate Format  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Transformation      │
│  - Schema Mapping   │
│  - Type Casting     │
│  - Data Validation  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   Parquet Output    │
│  - SNAPPY Compress  │
│  - Columnar Format  │
│  - Metadata Rich    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Analytical Layer   │
│  - DuckDB Engine    │
│  - Fast Queries     │
│  - Ontology-Aware   │
└─────────────────────┘
```

---

## Stage 1: Data Ingestion

### Source Data Format

Fannie Mae distributes loan performance data as pipe-separated text files:

```
POOL_ID|LOAN_ID|ACT_PERIOD|CHANNEL|SELLER|SERVICER|...
ABC123|100000000001|012023|R|SELLER_A|SERVICER_X|...
ABC123|100000000002|012023|R|SELLER_B|SERVICER_Y|...
```

**Challenges:**
- **No explicit schema**: Field types are implicit
- **Large file sizes**: 1GB+ raw text files
- **Quarterly updates**: Need to merge/update existing data
- **Data quality**: Missing values, inconsistent formats

### Ingestion Process

Our ingestion layer (`scripts/sync_data.py`) handles:

1. **Download/Sync from Cloudflare R2** (or local storage)
2. **File validation**: Check format, delimiter, basic structure
3. **Header parsing**: Extract column names from first row
4. **Chunked reading**: Process large files in manageable batches

```python
# Example: Reading pipe-separated file
import pandas as pd

df = pd.read_csv(
    'raw_data.txt',
    sep='|',
    dtype='str',  # Read all as strings initially
    na_values=['', 'NULL', 'NA'],
    keep_default_na=False,
    low_memory=False
)
```

---

## Stage 2: Schema Transformation

### The Schema Challenge

Fannie Mae provides data dictionaries, but the raw files have no enforced types. Columns like `ORIG_UPB` (unpaid principal balance) are stored as strings, and credit scores may mix integers with nulls or special codes.

### Our Schema Solution

We define an **explicit, typed schema** for all 110 columns:

```python
SCHEMA = {
    # Identifiers - VARCHAR for flexibility
    'LOAN_ID': 'VARCHAR',
    'POOL_ID': 'VARCHAR',
    
    # Financial - appropriate numeric types
    'ORIG_UPB': 'DOUBLE',       # Large dollar amounts
    'CURRENT_UPB': 'DOUBLE',
    
    # Credit scores - INT16 (range: 300-850)
    'CSCORE_B': 'INT16',
    'CSCORE_C': 'INT16',
    
    # Ratios and percentages - FLOAT
    'OLTV': 'FLOAT',
    'DTI': 'FLOAT',
    'ORIG_RATE': 'FLOAT',
    
    # Dates - VARCHAR (MMYYYY format)
    'ORIG_DATE': 'VARCHAR',
    'ACT_PERIOD': 'VARCHAR',
    
    # Categorical - VARCHAR
    'STATE': 'VARCHAR',
    'PURPOSE': 'VARCHAR',
    'PROP': 'VARCHAR',
    
    # ... and 100+ more fields
}
```

### Type Casting Logic

The transformation layer (`notebooks/pipeline_csv_to_parquet.ipynb`) applies sophisticated type casting:

```python
def cast_columns(df, schema):
    for col, dtype in schema.items():
        if col not in df.columns:
            continue
            
        if dtype == 'DOUBLE' or dtype == 'FLOAT':
            # Handle currency and percentages
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        elif dtype.startswith('INT'):
            # Handle integers with nulls
            df[col] = pd.to_numeric(df[col], errors='coerce')
            if dtype == 'INT16':
                df[col] = df[col].astype('Int16')  # Nullable integer
            elif dtype == 'INT8':
                df[col] = df[col].astype('Int8')
        
        elif dtype == 'VARCHAR':
            # Keep as string, handle nulls
            df[col] = df[col].astype('str')
            df[col] = df[col].replace(['nan', 'None'], pd.NA)
    
    return df
```

### Data Validation

Post-transformation, we validate:
- **Range checks**: Credit scores 300-850, LTV 0-200%
- **Referential integrity**: Valid state codes, property types
- **Business rules**: Origination date <= current period
- **Null handling**: Expected nulls (co-borrower fields) vs. data quality issues

---

## Stage 3: Parquet Storage

### Why Parquet?

[Apache Parquet](https://parquet.apache.org/) is a columnar storage format ideal for analytical workloads:

- **Columnar layout**: Read only the columns you need
- **Compression**: SNAPPY, GZIP, or ZSTD reduce file size 5-15x
- **Type preservation**: Native support for integers, floats, decimals
- **Metadata**: Embedded schema and statistics for query optimization
- **Ecosystem support**: Works with DuckDB, Pandas, Spark, etc.

### Our Parquet Configuration

```python
import pyarrow as pa
import pyarrow.parquet as pq

# Define schema with explicit types
schema = pa.schema([
    ('LOAN_ID', pa.string()),
    ('ORIG_UPB', pa.float64()),
    ('CSCORE_B', pa.int16()),
    ('STATE', pa.string()),
    # ... all 110 fields
])

# Write with SNAPPY compression
table = pa.Table.from_pandas(df, schema=schema)
pq.write_table(
    table,
    'data.parquet',
    compression='SNAPPY',
    use_dictionary=True,  # Compress repetitive values
    write_statistics=True  # Enable query optimization
)
```

### Performance Gains

| Metric | Raw .txt | Parquet (SNAPPY) | Improvement |
|--------|----------|------------------|-------------|
| File Size | 1.2 GB | 120 MB | **10x reduction** |
| Full Scan | 45 seconds | 2 seconds | **22x faster** |
| Column Select | 45 seconds | 0.3 seconds | **150x faster** |
| Memory Usage | 3.5 GB | 450 MB | **7.8x reduction** |

---

## Stage 4: DuckDB Integration

### Why DuckDB?

[DuckDB](https://duckdb.org/) is an embedded analytical database designed for fast OLAP queries:

- **Zero-copy reads**: Queries Parquet files directly without loading into memory
- **Vectorized execution**: SIMD optimizations for blazing-fast aggregations
- **SQL support**: Full SQL-92 compliance with analytical extensions
- **Embedded**: No server setup, runs in-process with Python

### Query Examples

**Simple aggregation:**
```sql
SELECT STATE, COUNT(*) as loan_count, AVG(ORIG_UPB) as avg_balance
FROM 'data/processed/data.parquet'
GROUP BY STATE
ORDER BY loan_count DESC
LIMIT 10;
```
*Execution time: 0.15 seconds for 9M rows*

**Complex analytical query:**
```sql
SELECT 
    CASE 
        WHEN CSCORE_B >= 740 THEN 'Super Prime'
        WHEN CSCORE_B >= 680 THEN 'Prime'
        WHEN CSCORE_B >= 620 THEN 'Near Prime'
        ELSE 'Subprime'
    END as credit_tier,
    COUNT(*) as loans,
    ROUND(AVG(OLTV), 1) as avg_ltv,
    ROUND(AVG(DTI), 1) as avg_dti,
    SUM(CASE WHEN DLQ_STATUS > '00' THEN 1 ELSE 0 END) as delinquent,
    ROUND(SUM(CURRENT_UPB)/1000000000, 2) as total_upb_billions
FROM 'data/processed/data.parquet'
WHERE CSCORE_B IS NOT NULL
GROUP BY credit_tier
ORDER BY MIN(CSCORE_B);
```
*Execution time: 0.8 seconds with aggregations and conditional logic*

### Integration with converSQL

Our `src/core.py` module wraps DuckDB for seamless querying:

```python
import duckdb

def execute_sql_query(sql_query: str, parquet_files: List[str]):
    """Execute SQL on Parquet files using DuckDB."""
    conn = duckdb.connect()
    
    # Register Parquet files as tables
    for file_path in parquet_files:
        table_name = os.path.splitext(os.path.basename(file_path))[0]
        conn.execute(f"CREATE TABLE {table_name} AS SELECT * FROM '{file_path}'")
    
    # Execute query
    result_df = conn.execute(sql_query).fetchdf()
    conn.close()
    
    return result_df
```

---

## Data Ontology Integration

### From Raw Data to Business Intelligence

The pipeline doesn't just transform file formats—it infuses **business intelligence** through our ontological data dictionary.

### Ontology Structure

Located in `src/data_dictionary.py`, the ontology defines:

1. **Domain organization**: 15 business domains (Credit Risk, Geographic, Temporal, etc.)
2. **Field metadata**: Description, business context, risk implications
3. **Relationships**: Cross-field dependencies and calculations
4. **Value codes**: Enumerated types (e.g., DLQ_STATUS codes, PURPOSE types)
5. **Business rules**: Credit score tiers, LTV risk bands, vintage cohorts

### Example: Credit Risk Domain

```python
LOAN_ONTOLOGY = {
    "CREDIT_RISK": {
        "domain_description": "Borrower credit quality and equity position indicators",
        "fields": {
            "CSCORE_B": FieldMetadata(
                description="Primary borrower credit score (FICO)",
                domain="Credit_Risk",
                data_type="INT16",
                business_context="Primary indicator of credit quality. Scores 740+ are super prime, 680-739 prime, 620-679 near prime, <620 subprime.",
                risk_impact="Primary driver of default risk. Each 20-point decrease in score doubles default probability.",
                relationships=["credit_tier", "default_risk", "pricing"]
            ),
            "OLTV": FieldMetadata(
                description="Original loan-to-value ratio (%)",
                domain="Credit_Risk",
                data_type="FLOAT",
                business_context="Measures borrower equity at origination. LTV >80% typically requires mortgage insurance. LTV >95% indicates minimal down payment.",
                risk_impact="Higher LTV = lower equity cushion = higher default and loss severity risk. 80% is key threshold.",
                relationships=["equity_position", "mi_requirement", "loss_severity"]
            )
        }
    }
}
```

### How AI Uses Ontology

When converSQL generates SQL, it leverages ontology to:

1. **Map concepts to fields**: "high-risk loans" → `CSCORE_B < 620 AND OLTV > 90`
2. **Apply business rules**: "super prime borrowers" → `CSCORE_B >= 740`
3. **Generate context-aware calculations**: "portfolio concentration" includes grouping and ratio logic
4. **Provide semantic relationships**: Understanding that `OLTV` relates to `MI_PCT` and loss severity

---

## Pipeline Execution

### Running the Pipeline

**Notebooks (Development):**
```bash
# For single file conversion
jupyter notebook notebooks/pipeline_csv_to_parquet.ipynb

# For multi-file processing
jupyter notebook notebooks/pipeline_csv_to_parquet_multifile.ipynb
```

**Scripts (Production):**
```bash
# Sync data from R2 storage
python scripts/sync_data.py

# Force re-download and re-process
python scripts/sync_data.py --force
```

### Configuration

Set environment variables in `.env`:

```bash
# Data directories
PROCESSED_DATA_DIR=data/processed/
RAW_DATA_DIR=data/raw/

# Cloudflare R2 (optional)
R2_ACCOUNT_ID=your_account_id
R2_ACCESS_KEY_ID=your_access_key
R2_SECRET_ACCESS_KEY=your_secret_key
R2_BUCKET_NAME=your_bucket_name
```

---

## Data Quality & Monitoring

### Quality Checks

Our pipeline includes automated quality checks:

```python
def validate_data(df):
    """Validate transformed data quality."""
    issues = []
    
    # Check for required fields
    required_fields = ['LOAN_ID', 'ORIG_UPB', 'STATE']
    missing = [f for f in required_fields if f not in df.columns]
    if missing:
        issues.append(f"Missing required fields: {missing}")
    
    # Check credit score ranges
    if 'CSCORE_B' in df.columns:
        invalid_scores = df[(df['CSCORE_B'] < 300) | (df['CSCORE_B'] > 850)].shape[0]
        if invalid_scores > 0:
            issues.append(f"{invalid_scores} invalid credit scores (out of 300-850 range)")
    
    # Check LTV ranges
    if 'OLTV' in df.columns:
        invalid_ltv = df[(df['OLTV'] < 0) | (df['OLTV'] > 200)].shape[0]
        if invalid_ltv > 0:
            issues.append(f"{invalid_ltv} invalid LTV values (out of 0-200% range)")
    
    # Check for duplicates
    dupes = df.duplicated(subset=['LOAN_ID', 'ACT_PERIOD']).sum()
    if dupes > 0:
        issues.append(f"{dupes} duplicate loan-period combinations")
    
    return issues
```

### Monitoring Metrics

Track pipeline health with:
- **Processing time**: Target <5 minutes per 1M rows
- **Data volume**: Row counts match expected quarterly releases
- **Quality scores**: % of records passing validation
- **File sizes**: Compression ratios within expected range (8-12x)
- **Query performance**: Sample queries execute within SLA

---

## Performance Optimization

### Optimization Techniques

1. **Chunked processing**: Read/write large files in 500K row chunks
2. **Column selection**: Only cast columns actually used in queries
3. **Compression tuning**: SNAPPY for speed, GZIP for size
4. **Partitioning**: Consider partitioning by year/quarter for very large datasets
5. **Indexing**: Parquet row groups serve as implicit indexes
6. **Caching**: Reuse Parquet files across application sessions

### Scaling Considerations

For datasets beyond 50M rows:

- **Partitioning by time**: `data_2020Q1.parquet`, `data_2020Q2.parquet`, etc.
- **Delta updates**: Only process new/changed records
- **Distributed processing**: Use Spark or Dask for multi-machine transformation
- **Data warehousing**: Consider BigQuery, Snowflake, or Redshift for very large scale

---

## Extending the Pipeline

### Adapting to Your Data

To use this pipeline for other datasets:

1. **Update schema definition**: Define column types for your data
2. **Modify transformation logic**: Adjust type casting and validation
3. **Create custom ontology**: Define your domain-specific ontology
4. **Configure data source**: Point to your raw data location
5. **Test thoroughly**: Validate with sample data before production

### Example: E-commerce Order Data

```python
# Define schema
ECOMMERCE_SCHEMA = {
    'order_id': 'VARCHAR',
    'customer_id': 'VARCHAR',
    'order_date': 'DATE',
    'order_amount': 'DOUBLE',
    'product_category': 'VARCHAR',
    'quantity': 'INT16',
    'discount_pct': 'FLOAT'
}

# Define ontology
ECOMMERCE_ONTOLOGY = {
    "CUSTOMER": {
        "domain_description": "Customer identification and segmentation",
        "fields": {
            "customer_id": FieldMetadata(
                description="Unique customer identifier",
                domain="Customer",
                data_type="VARCHAR",
                business_context="Primary key for customer analytics"
            )
        }
    },
    "TRANSACTION": {
        "domain_description": "Order and revenue tracking",
        "fields": {
            "order_amount": FieldMetadata(
                description="Total order value in USD",
                domain="Transaction",
                data_type="DOUBLE",
                business_context="Revenue metric for analytics and reporting"
            )
        }
    }
}
```

---

## Troubleshooting

### Common Issues

**Issue: Out of memory during transformation**
- Solution: Reduce chunk size, process in batches

**Issue: Parquet write fails with schema errors**
- Solution: Check for incompatible types (e.g., mixed int/float in same column)

**Issue: Query performance degradation**
- Solution: Check file size, consider partitioning, verify compression

**Issue: Data quality failures**
- Solution: Review raw data, adjust null handling, update validation rules

---

## Resources

### Documentation
- [Fannie Mae Data Portal](https://capitalmarkets.fanniemae.com/tools-applications/data-dynamics)
- [Apache Parquet Format](https://parquet.apache.org/docs/)
- [DuckDB Documentation](https://duckdb.org/docs/)
- [Pandas API Reference](https://pandas.pydata.org/docs/)

### Related Files
- `notebooks/pipeline_csv_to_parquet.ipynb` — Single-file transformation notebook
- `notebooks/pipeline_csv_to_parquet_multifile.ipynb` — Multi-file batch processing
- `scripts/sync_data.py` — Production data sync script
- `src/data_dictionary.py` — Ontological data dictionary
- `docs/comprehensive_data_dictionary.md` — Complete field reference

---

## Questions?

For pipeline questions or issues:
- Open an issue on GitHub
- Check existing documentation in `docs/`
- Review notebook examples in `notebooks/`

**Making data pipelines conversational, one transformation at a time.** 🚀
