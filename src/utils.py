from typing import Dict


def get_analyst_questions() -> Dict[str, str]:
    """Return sophisticated analyst questions leveraging loan performance domain expertise."""
    return {
        "🎯 Portfolio Health Check": "Show me our current portfolio composition by credit risk tiers (Super Prime 740+, Prime 680-739, Near Prime 620-679, Subprime <620) with current UPB and delinquency rates",
        "🌎 Geographic Risk Assessment": "Which top 10 states have the highest loan concentrations and how do their current delinquency rates compare to the national average?",
        "📈 Vintage Performance Analysis": "Compare loan performance between 2020-2021 refi boom vintages vs 2022+ rising rate vintages - show loan counts, average rates, and current performance",
        "⚠️ High-Risk Concentration": "Identify loans with combined high-risk factors: OLTV >90%, DTI >36%, and credit scores <680 - show geographic distribution and current status",
        "💰 Jumbo Loan Intelligence": "Analyze loans above $500K - show credit profile distribution, geographic concentration, and performance compared to conforming loans",
        "🏠 Product Mix Evolution": "Compare purchase vs refinance vs cash-out refinance loans originated in the last 24 months - show volume trends and borrower risk profiles",
        "📊 Market Share by Channel": "Show origination volume and average loan characteristics by channel (Retail, Correspondent, Broker) for top 5 volume states",
        "🔍 Credit Migration Analysis": "For loans aged 24-48 months (2020-2021 vintage), show how many have migrated from current to 30+ day delinquent status by original credit score",
        "🌟 Super Prime Performance": "Analyze our Super Prime segment (740+ credit scores) - show portfolio share, average UPB, geographic distribution, and performance metrics",
        "🎲 Rate Sensitivity Analysis": "Compare current portfolio performance between ultra-low rate loans (2-4%) vs higher rate loans (5%+) - show delinquency rates and paydown behavior",
    }
