#!/usr/bin/env python3
"""
AI Service Module
Handles Bedrock and Claude API connections, prompt caching, and SQL generation.
"""

import json
import hashlib
import streamlit as st
from typing import Optional, Tuple, Dict, Any
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# AI Configuration
AI_PROVIDER = os.getenv('AI_PROVIDER', 'bedrock').lower()
CLAUDE_API_KEY = os.getenv('CLAUDE_API_KEY')
CLAUDE_MODEL = os.getenv('CLAUDE_MODEL', 'claude-3-5-sonnet-20241022')
BEDROCK_MODEL_ID = os.getenv('BEDROCK_MODEL_ID', 'anthropic.claude-3-5-haiku-20241022-v1:0')
ENABLE_BEDROCK = os.getenv('ENABLE_BEDROCK', 'true').lower() == 'true'
ENABLE_PROMPT_CACHE = os.getenv('ENABLE_PROMPT_CACHE', 'true').lower() == 'true'
PROMPT_CACHE_TTL = int(os.getenv('PROMPT_CACHE_TTL', '3600'))


class AIServiceError(Exception):
    """Custom exception for AI service errors."""
    pass


class BedrockClient:
    """Bedrock AI client wrapper."""
    
    def __init__(self):
        self.client = None
        self._initialize()
    
    def _initialize(self):
        """Initialize Bedrock client."""
        if not ENABLE_BEDROCK:
            return
        
        try:
            import boto3
            self.client = boto3.client(
                'bedrock-runtime',
                region_name=os.getenv('AWS_DEFAULT_REGION', 'us-west-2')
            )
            
            # Test connection
            try:
                self.client.list_foundation_models()
            except Exception:
                # Keep client - might work for invoke_model
                pass
                
        except Exception as e:
            print(f"⚠️ Bedrock initialization failed: {e}")
            self.client = None
    
    def is_available(self) -> bool:
        """Check if Bedrock is available."""
        return self.client is not None
    
    def generate_sql(self, prompt: str) -> Tuple[str, str]:
        """Generate SQL using Bedrock."""
        if not self.client:
            return "", "Bedrock client not available"
        
        try:
            request_body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 4000,
                "messages": [{"role": "user", "content": prompt}]
            }
            
            response = self.client.invoke_model(
                modelId=BEDROCK_MODEL_ID,
                body=json.dumps(request_body),
                contentType="application/json",
                accept="application/json"
            )
            
            response_body = json.loads(response['body'].read())
            sql_query = response_body['content'][0]['text'].strip()
            
            return sql_query, ""
            
        except Exception as e:
            error_msg = f"Bedrock error: {str(e)}"
            return "", error_msg


class ClaudeClient:
    """Claude API client wrapper."""
    
    def __init__(self):
        self.client = None
        self._initialize()
    
    def _initialize(self):
        """Initialize Claude client."""
        if not CLAUDE_API_KEY:
            return
        
        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)
            
            # Test connection with minimal request
            try:
                self.client.messages.create(
                    model=CLAUDE_MODEL,
                    max_tokens=10,
                    messages=[{"role": "user", "content": "test"}]
                )
            except Exception:
                # Keep client - might work for other requests
                pass
                
        except ImportError:
            print("⚠️ Anthropic package not installed. Run: pip install anthropic")
            self.client = None
        except Exception as e:
            print(f"⚠️ Claude initialization failed: {e}")
            self.client = None
    
    def is_available(self) -> bool:
        """Check if Claude API is available."""
        return self.client is not None
    
    def generate_sql(self, prompt: str) -> Tuple[str, str]:
        """Generate SQL using Claude API."""
        if not self.client:
            return "", "Claude API client not available"
        
        try:
            response = self.client.messages.create(
                model=CLAUDE_MODEL,
                max_tokens=4000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            sql_query = response.content[0].text.strip()
            return sql_query, ""
            
        except Exception as e:
            error_msg = f"Claude API error: {str(e)}"
            return "", error_msg


class AIService:
    """Main AI service that manages multiple providers."""
    
    def __init__(self):
        self.bedrock = BedrockClient()
        self.claude = ClaudeClient()
        self.active_provider = None
        self._determine_active_provider()
    
    def _determine_active_provider(self):
        """Determine which AI provider to use."""
        if AI_PROVIDER == 'claude' and self.claude.is_available():
            self.active_provider = 'claude'
        elif AI_PROVIDER == 'bedrock' and self.bedrock.is_available():
            self.active_provider = 'bedrock'
        elif self.claude.is_available():
            self.active_provider = 'claude'
        elif self.bedrock.is_available():
            self.active_provider = 'bedrock'
        else:
            self.active_provider = None
    
    def is_available(self) -> bool:
        """Check if any AI provider is available."""
        return self.active_provider is not None
    
    def get_active_provider(self) -> Optional[str]:
        """Get the currently active provider."""
        return self.active_provider
    
    def get_provider_status(self) -> Dict[str, bool]:
        """Get status of all providers."""
        return {
            'bedrock': self.bedrock.is_available(),
            'claude': self.claude.is_available(),
            'active': self.active_provider
        }
    
    def _create_prompt_hash(self, user_question: str, schema_context: str) -> str:
        """Create hash for prompt caching."""
        combined = f"{user_question}|{schema_context}|{self.active_provider}"
        return hashlib.md5(combined.encode()).hexdigest()
    
    def _build_sql_prompt(self, user_question: str, schema_context: str) -> str:
        """Build the SQL generation prompt."""
        return f"""You are an expert Single Family Loan loan performance data analyst. Write a single, clean DuckDB-compatible SQL query.

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
    
    @st.cache_data(ttl=PROMPT_CACHE_TTL)
    def _cached_generate_sql(_self, user_question: str, schema_context: str, provider: str) -> Tuple[str, str]:
        """Cached SQL generation to reduce API calls."""
        # This is a placeholder for the cache decorator
        # Actual generation happens in generate_sql
        return "", ""
    
    def generate_sql(self, user_question: str, schema_context: str) -> Tuple[str, str, str]:
        """
        Generate SQL query using available AI provider.
        Returns: (sql_query, error_message, provider_used)
        """
        if not self.is_available():
            error_msg = """🚫 **AI SQL Generation Unavailable**

No AI providers are configured or available. This could be due to:
- Missing API keys (Claude API key or AWS credentials)
- Network connectivity issues
- Service configuration problems

**You can still use the application by:**
- Writing SQL queries manually in the Advanced tab
- Using the sample queries provided
- Referring to the database schema for guidance"""
            return "", error_msg, "none"
        
        # Check cache if enabled
        if ENABLE_PROMPT_CACHE:
            cache_key = self._create_prompt_hash(user_question, schema_context)
            try:
                cached_result = self._cached_generate_sql(user_question, schema_context, self.active_provider)
                if cached_result[0]:  # If cached result exists
                    return cached_result[0], cached_result[1], f"{self.active_provider} (cached)"
            except Exception:
                pass  # Cache miss or error, continue with API call
        
        # Build prompt
        prompt = self._build_sql_prompt(user_question, schema_context)
        
        # Generate SQL using active provider
        if self.active_provider == 'claude':
            sql_query, error_msg = self.claude.generate_sql(prompt)
        elif self.active_provider == 'bedrock':
            sql_query, error_msg = self.bedrock.generate_sql(prompt)
        else:
            return "", "No AI provider available", "none"
        
        # Cache the result if successful and caching is enabled
        if ENABLE_PROMPT_CACHE and sql_query and not error_msg:
            try:
                # Update cache by calling the cached function
                self._cached_generate_sql(user_question, schema_context, self.active_provider)
            except Exception:
                pass  # Cache update failed, but we have the result
        
        return sql_query, error_msg, self.active_provider


# Global AI service instance
_ai_service = None


def get_ai_service() -> AIService:
    """Get or create global AI service instance."""
    global _ai_service
    if _ai_service is None:
        _ai_service = AIService()
    return _ai_service


# Convenience functions for backward compatibility
def initialize_ai_client() -> Tuple[Optional[object], str]:
    """Initialize AI client - backward compatibility."""
    service = get_ai_service()
    if service.is_available():
        return service, service.get_active_provider()
    return None, "none"


def generate_sql_with_ai(user_question: str, schema_context: str) -> Tuple[str, str]:
    """Generate SQL with AI - backward compatibility."""
    service = get_ai_service()
    sql_query, error_msg, provider = service.generate_sql(user_question, schema_context)
    return sql_query, error_msg