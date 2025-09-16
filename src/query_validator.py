#!/usr/bin/env python3
"""
Query Validator for Single Family Loan Data Analysis
Provides validation and suggestions for SQL queries.
"""

from typing import List, Dict, Optional
from .data_dictionary import LOAN_ONTOLOGY, get_field_context

class QueryValidator:
    """Validates and suggests improvements for SQL queries."""

    def __init__(self):
        # Extract all fields from ontology
        self.known_fields = set()
        for domain_info in LOAN_ONTOLOGY.values():
            self.known_fields.update(domain_info['fields'].keys())

        self.risk_fields = ['CSCORE_B', 'OLTV', 'OCLTV', 'DTI']
        self.geographic_fields = ['STATE', 'MSA', 'ZIP']
        self.financial_fields = ['ORIG_UPB', 'CURRENT_UPB', 'ORIG_RATE', 'CURR_RATE']
    
    def validate_query(self, sql_query: str) -> Dict:
        """Validate SQL query and return suggestions."""
        results = {
            'is_valid': True,
            'warnings': [],
            'suggestions': [],
            'enhancements': []
        }
        
        # Check for common field usage patterns
        self._check_geographic_analysis(sql_query, results)
        self._check_risk_analysis(sql_query, results)
        self._check_financial_analysis(sql_query, results)
        self._check_performance_analysis(sql_query, results)
        self._check_null_handling(sql_query, results)
        self._check_aggregation_best_practices(sql_query, results)
        
        return results
    
    def _check_geographic_analysis(self, query: str, results: Dict):
        """Check geographic analysis patterns."""
        query_upper = query.upper()

        if 'STATE' in query_upper:
            if 'GROUP BY STATE' not in query_upper:
                results['suggestions'].append(
                    "Consider adding 'GROUP BY STATE' for state-level analysis"
                )

            if 'WHERE STATE IS NOT NULL' not in query_upper:
                results['warnings'].append(
                    "STATE field may contain NULL values - consider adding 'WHERE STATE IS NOT NULL'"
                )

        if 'ZIP' in query_upper:
            results['enhancements'].append(
                "ZIP field contains only first 3 digits for privacy (e.g., '902', '100')"
            )
    
    def _check_risk_analysis(self, query: str, results: Dict):
        """Check risk analysis patterns."""
        query_upper = query.upper()
        
        if 'CSCORE_B' in query_upper:
            if 'CASE WHEN' not in query_upper:
                results['suggestions'].append(
                    "Consider creating credit score tiers: "
                    "CASE WHEN CSCORE_B >= 740 THEN 'Super Prime' "
                    "WHEN CSCORE_B >= 680 THEN 'Prime' "
                    "WHEN CSCORE_B >= 620 THEN 'Near Prime' "
                    "ELSE 'Subprime' END"
                )
        
        if any(field in query_upper for field in ['OLTV', 'CLTV']):
            if 'WHERE' not in query_upper or 'IS NOT NULL' not in query_upper:
                results['warnings'].append(
                    "LTV fields may be NULL for loans >97% LTV - consider filtering NULL values"
                )
        
        if 'DTI' in query_upper:
            results['enhancements'].append(
                "DTI interpretation: <=28% = Low Risk, 29-36% = Moderate, 37-45% = High, >45% = Very High"
            )
    
    def _check_financial_analysis(self, query: str, results: Dict):
        """Check financial analysis patterns."""
        query_upper = query.upper()
        
        if 'ORIG_UPB' in query_upper and 'AVG' in query_upper:
            if '/1000' not in query:
                results['suggestions'].append(
                    "Consider dividing ORIG_UPB by 1000 for readability: ROUND(AVG(ORIG_UPB)/1000, 0)"
                )
        
        if 'ORIG_RATE' in query_upper and 'AVG' in query_upper:
            if 'ROUND' not in query_upper:
                results['suggestions'].append(
                    "Consider rounding rates for readability: ROUND(AVG(ORIG_RATE), 2)"
                )
        
        if 'ORIG_UPB' in query_upper and 'CURR_UPB' in query_upper:
            results['enhancements'].append(
                "Comparing ORIG_UPB vs CURR_UPB shows paydown patterns - useful for prepayment analysis"
            )
    
    def _check_performance_analysis(self, query: str, results: Dict):
        """Check performance analysis patterns."""
        query_upper = query.upper()
        
        if 'DLQ_STATUS' in query_upper:
            results['enhancements'].append(
                "DLQ_STATUS values: '00'=Current, '01'=30-59 days, '02'=60-89 days, etc."
            )
            
            if "'00'" not in query and "= '00'" not in query:
                results['suggestions'].append(
                    "For current loans analysis, use WHERE DLQ_STATUS = '00'"
                )
        
        if 'LOAN_AGE' in query_upper:
            results['enhancements'].append(
                "LOAN_AGE is in months since origination - useful for vintage/seasoning analysis"
            )
    
    def _check_null_handling(self, query: str, results: Dict):
        """Check NULL value handling."""
        query_upper = query.upper()
        
        # Fields commonly with NULL values
        nullable_fields = ['DTI', 'CSCORE_C', 'OLTV', 'CLTV']
        
        for field in nullable_fields:
            if field in query_upper and 'IS NOT NULL' not in query_upper:
                results['warnings'].append(
                    f"{field} field commonly contains NULL values - consider filtering with 'WHERE {field} IS NOT NULL'"
                )
    
    def _check_aggregation_best_practices(self, query: str, results: Dict):
        """Check aggregation best practices."""
        query_upper = query.upper()
        
        if 'GROUP BY' in query_upper and 'ORDER BY' not in query_upper:
            results['suggestions'].append(
                "Consider adding ORDER BY clause to sort results meaningfully"
            )
        
        if 'COUNT(*)' in query_upper and 'LIMIT' not in query_upper:
            results['suggestions'].append(
                "For top N analysis, consider adding LIMIT clause (e.g., LIMIT 10)"
            )
        
        # Check for common Single Family Loan analysis patterns
        if 'STATE' in query_upper and 'COUNT(*)' in query_upper:
            if 'ORDER BY' not in query_upper:
                results['suggestions'].append(
                    "For state analysis, consider ORDER BY loan count: ORDER BY COUNT(*) DESC"
                )
    
    def suggest_query_improvements(self, user_question: str) -> List[str]:
        """Suggest query approaches based on user question."""
        suggestions = []
        question_lower = user_question.lower()
        
        # Geographic analysis suggestions
        if any(word in question_lower for word in ['state', 'geographic', 'region', 'location']):
            suggestions.append(
                "Geographic Analysis: Use GROUP BY STATE, consider MSA for metro areas, ZIP for regional analysis"
            )
        
        # Risk analysis suggestions
        if any(word in question_lower for word in ['risk', 'credit', 'score', 'ltv', 'dti']):
            suggestions.append(
                "Risk Analysis: Create tiers for CSCORE_B (740+=Super Prime), OLTV (80%=Low Risk), DTI (28%=Low Risk)"
            )
        
        # Performance suggestions
        if any(word in question_lower for word in ['performance', 'delinquent', 'current', 'default']):
            suggestions.append(
                "Performance Analysis: Use DLQ_STATUS for delinquency, LOAN_AGE for seasoning effects"
            )
        
        # Top N analysis
        if any(word in question_lower for word in ['top', 'best', 'worst', 'highest', 'lowest']):
            suggestions.append(
                "Top N Analysis: Use ORDER BY [metric] DESC LIMIT N pattern"
            )
        
        return suggestions

def validate_and_enhance_query(sql_query: str, user_question: str = "") -> Dict:
    """Main validation function."""
    validator = QueryValidator()
    
    # Basic validation
    results = validator.validate_query(sql_query)
    
    # Add question-specific suggestions
    if user_question:
        question_suggestions = validator.suggest_query_improvements(user_question)
        results['question_suggestions'] = question_suggestions
    
    return results

# Example usage and test cases
if __name__ == "__main__":
    # Test queries
    test_queries = [
        ("SELECT STATE, COUNT(*) FROM data GROUP BY STATE", "Show loan counts by state"),
        ("SELECT AVG(CSCORE_B) FROM data", "What's the average credit score?"),
        ("SELECT * FROM data WHERE OLTV > 90", "Show high LTV loans"),
    ]
    
    for query, question in test_queries:
        print(f"\nTesting: {question}")
        print(f"Query: {query}")
        results = validate_and_enhance_query(query, question)
        
        if results['warnings']:
            print("Warnings:")
            for warning in results['warnings']:
                print(f"  - {warning}")
        
        if results['suggestions']:
            print("Suggestions:")
            for suggestion in results['suggestions']:
                print(f"  - {suggestion}")
        
        if results['enhancements']:
            print("Enhancements:")
            for enhancement in results['enhancements']:
                print(f"  - {enhancement}")