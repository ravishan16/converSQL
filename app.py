"""
NLP to SQL - Professional Streamlit Application
A minimal and professional interface for natural language to SQL conversion.
"""

import streamlit as st
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="NLP to SQL",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def main():
    """Main application function."""
    
    # Header
    st.title("🔍 NLP to SQL")
    st.markdown("---")
    
    # AI Provider information
    ai_provider = os.getenv("AI_PROVIDER", "Not configured")
    
    # Welcome section
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### Welcome to NLP to SQL")
        st.markdown(
            """
            Transform natural language queries into SQL statements with ease.
            This application leverages advanced AI to bridge the gap between 
            human language and database queries.
            """
        )
        
        # Feature highlights
        st.markdown("#### ✨ Features")
        features = [
            "🤖 AI-powered natural language processing",
            "💬 Intuitive query interface",
            "⚡ Fast and accurate SQL generation",
            "🔒 Secure and reliable processing"
        ]
        
        for feature in features:
            st.markdown(f"- {feature}")
    
    with col2:
        # System status card
        st.markdown("#### 🔧 System Status")
        
        with st.container():
            st.markdown(
                f"""
                <div style="
                    padding: 1rem;
                    background-color: #f8f9fa;
                    border-radius: 0.5rem;
                    border-left: 4px solid #28a745;
                    margin-bottom: 1rem;
                ">
                    <strong>AI Provider:</strong><br>
                    <code>{ai_provider}</code>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            st.success("✅ System Ready")
    
    # Interactive section
    st.markdown("---")
    st.markdown("### 🚀 Get Started")
    
    # Demo query input
    with st.container():
        st.markdown("**Try a sample query:**")
        sample_query = st.text_area(
            "Enter your natural language query:",
            placeholder="e.g., Show me all customers who made purchases in the last 30 days",
            height=100,
            key="query_input"
        )
        
        col1, col2, col3 = st.columns([1, 1, 4])
        
        with col1:
            if st.button("🔄 Convert", type="primary"):
                if sample_query.strip():
                    with st.spinner("Processing your query..."):
                        # Placeholder for actual NLP to SQL conversion
                        st.success("Query processed successfully!")
                        st.code(
                            "-- Generated SQL (Demo)\nSELECT * FROM customers \nWHERE purchase_date >= CURRENT_DATE - INTERVAL '30 days';",
                            language="sql"
                        )
                else:
                    st.warning("Please enter a query to convert.")
        
        with col2:
            if st.button("🧹 Clear"):
                st.rerun()
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style="text-align: center; color: #666; font-size: 0.9em;">
            Built with ❤️ using Streamlit | Powered by {ai_provider}
        </div>
        """.format(ai_provider=ai_provider),
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()