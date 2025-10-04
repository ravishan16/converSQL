import time

import pandas as pd
import streamlit as st

from src.core import execute_sql_query  # Assuming it's here; adjust if elsewhere
from src.services.ai_service import generate_sql_with_ai
from src.services.data_service import display_results
from src.simple_auth import get_auth_service
from src.utils import get_analyst_questions


def render_tabs():
    tab_query, tab_manual, tab_ontology, tab_schema = st.tabs(
        [
            "🔍 Query Builder",
            "🛠️ Manual SQL",
            "️ Data Ontology",
            "🗂️ Database Schema",
        ]
    )

    st.markdown("<div style='margin-bottom: 1rem;'></div>", unsafe_allow_html=True)

    with tab_query:
        st.markdown(
            """
        <div class='section-card'>
            <div class='section-card__header'>
                <h3>Ask Questions About Your Loan Data</h3>
                <p>Use natural language to query your loan portfolio data.</p>
            </div>
        """,
            unsafe_allow_html=True,
        )

        # More compact analyst question dropdown
        analyst_questions = get_analyst_questions()

        query_col1, query_col2 = st.columns([4, 1], gap="medium")
        with query_col1:
            selected_question = st.selectbox(
                "💡 **Common Questions:**",
                [""] + list(analyst_questions.keys()),
                help="Select a pre-defined question",
            )

        with query_col2:
            st.write("")
            if st.button("🎯 Use", disabled=not selected_question, use_container_width=True):
                if selected_question in analyst_questions:
                    st.session_state.user_question = analyst_questions[selected_question]
                    st.rerun()

        # Professional question input with better styling
        st.markdown("<label class='text-label'>💭 Your Question:</label>", unsafe_allow_html=True)
        user_question = st.text_area(
            "Your Question",
            value=st.session_state.get("user_question", ""),
            placeholder="e.g., What are the top 10 states by loan volume and their average interest rates?",
            help="Ask your question in natural language - be specific for better results",
            height=100,
            label_visibility="collapsed",
        )

        # AI Generation - Always show button, disable if conditions not met
        ai_service = st.session_state.get("ai_service")
        ai_provider = ai_service.get_active_provider() if ai_service else None

        # Get provider display name
        if ai_service and ai_provider:
            available_providers = ai_service.get_available_providers()
            provider_name = available_providers.get(ai_provider, ai_provider.title())
        else:
            provider_name = "AI"

        ai_available = st.session_state.get("ai_available", False)
        is_ai_ready = ai_available and user_question.strip()

        generate_button = st.button(
            f"🤖 Generate SQL with {provider_name}",
            type="primary",
            use_container_width=True,
            disabled=not is_ai_ready,
            help="Enter a question above to generate SQL" if not is_ai_ready else None,
        )

        if generate_button and is_ai_ready:
            with st.spinner(f"🧠 {provider_name} is analyzing your question..."):
                start_time = time.time()
                sql_query, error_msg = generate_sql_with_ai(user_question, st.session_state.get("schema_context", ""))
                ai_generation_time = time.time() - start_time
                st.session_state.generated_sql = sql_query
                st.session_state.ai_error = error_msg
                # Hide Edit panel on fresh generation to avoid empty editor gaps
                st.session_state.show_edit_sql = False

                # Log query for authenticated users
                auth = get_auth_service()
                if auth.is_authenticated() and sql_query and not error_msg:
                    auth.log_query(user_question, sql_query, provider_name, ai_generation_time)

                if sql_query and not error_msg:
                    st.info(f"🤖 {provider_name} generated SQL in {ai_generation_time:.2f} seconds")

        # Show warning only if AI is unavailable but user entered text
        if user_question.strip() and not st.session_state.get("ai_available", False):
            st.warning(
                "🤖 AI Assistant unavailable. Please configure Claude API or AWS Bedrock access, or use Manual SQL in the Advanced tab."
            )

        # Display AI errors
        if st.session_state.ai_error:
            st.error(st.session_state.ai_error)
            st.session_state.ai_error = ""

        # Always show execute section, but conditionally enable
        st.markdown("---")

        # Show generated SQL in a compact expander to avoid taking vertical space
        if st.session_state.generated_sql:
            with st.expander("🧠 AI-Generated SQL", expanded=False):
                st.code(st.session_state.generated_sql, language="sql")

        # Always show buttons, disable based on state
        col1, col2 = st.columns([3, 1])
        with col1:
            has_sql = bool(st.session_state.generated_sql.strip()) if st.session_state.generated_sql else False
            execute_button = st.button(
                "✅ Execute Query",
                type="primary",
                use_container_width=True,
                disabled=not has_sql,
                help="Generate SQL first to execute" if not has_sql else None,
            )
            if execute_button and has_sql:
                with st.spinner("⚡ Running query..."):
                    try:
                        start_time = time.time()
                        result_df = execute_sql_query(
                            st.session_state.generated_sql,
                            st.session_state.get("parquet_files", []),
                        )
                        execution_time = time.time() - start_time
                        # Hide Edit panel on execute to avoid empty editor gaps
                        st.session_state.show_edit_sql = False
                        # Persist AI results for re-renders
                        st.session_state["ai_query_result_df"] = result_df
                        st.session_state["last_result_tab"] = "tab1"
                        display_results(result_df, "AI Query Results", execution_time)
                    except Exception as e:
                        st.error(f"❌ Query execution failed: {str(e)}")
                        st.info("💡 Try editing the SQL or rephrasing your question")

        with col2:
            edit_button = st.button(
                "✏️ Edit",
                use_container_width=True,
                disabled=not has_sql,
                help="Generate SQL first to edit" if not has_sql else None,
            )
            if edit_button and has_sql:
                st.session_state.show_edit_sql = True

        # (Edit panel moved to render AFTER results to avoid pre-results blank space)

        # If user requested editing, render panel after results so the layout stays compact
        if st.session_state.get("show_edit_sql", False):
            st.markdown("### ✏️ Edit SQL Query")
            edited_sql = st.text_area(
                "Modify the query:",
                value=st.session_state.generated_sql,
                height=150,
                key="edit_sql",
            )

            run_col, cancel_col = st.columns([3, 1])
            with run_col:
                if st.button("🚀 Run Edited Query", type="primary", use_container_width=True):
                    with st.spinner("⚡ Running edited query..."):
                        try:
                            start_time = time.time()
                            result_df = execute_sql_query(
                                edited_sql,
                                st.session_state.get("parquet_files", []),
                            )
                            execution_time = time.time() - start_time
                            # Collapse editor on success and show results
                            st.session_state.show_edit_sql = False
                            display_results(result_df, "Edited Query Results", execution_time)
                        except Exception as e:
                            st.error(f"❌ Query execution failed: {str(e)}")
                            st.info("💡 Check your SQL syntax and try again")
            with cancel_col:
                if st.button("❌ Cancel", use_container_width=True):
                    st.session_state.show_edit_sql = False
                    st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

        # Persisted results rendering for AI tab: show last results across reruns
        if (
            st.session_state.get("last_result_tab") == "tab1"
            and isinstance(st.session_state.get("last_result_df"), pd.DataFrame)
            and not st.session_state.get("_rendered_this_run", False)
        ):
            display_results(
                st.session_state["last_result_df"],
                st.session_state.get("last_result_title", "Previous Results"),
            )

    with tab_ontology:
        st.markdown(
            """
        <div style='margin-bottom: 1.5rem;'>
            <h3 style='color: var(--color-text-primary); font-weight: 400; margin-bottom: 0.5rem;'>
                🗺️ Data Ontology Explorer
            </h3>
            <p style='color: var(--color-text-secondary); margin: 0; font-size: 0.95rem;'>
                Explore the structured organization of your data by domain and field.
            </p>
        </div>
        """,
            unsafe_allow_html=True,
        )

        # Import ontology data
        from src.data_dictionary import LOAN_ONTOLOGY, PORTFOLIO_CONTEXT

        # Optional quick search across all fields (kept because you liked this)
        q = (
            st.text_input(
                "🔎 Quick search (field name or description)",
                key="ontology_quick_search",
                placeholder="e.g., CSCORE_B, OLTV, DTI",
            )
            .strip()
            .lower()
        )
        if q:
            results = []
            for domain_name, domain_info in LOAN_ONTOLOGY.items():
                for fname, meta in domain_info.get("fields", {}).items():
                    desc = getattr(meta, "description", "")
                    dtype = getattr(meta, "data_type", "")
                    if q in fname.lower() or q in str(desc).lower() or q in str(dtype).lower():
                        results.append((domain_name, fname, desc, dtype))
            if results:
                st.markdown("#### 🔍 Search results")
                for domain_name, fname, desc, dtype in results[:100]:
                    st.markdown(f"• **{fname}** ({dtype}) — {desc}")
                    st.caption(f"Domain: {domain_name.replace('_', ' ').title()}")
                st.markdown("---")
            else:
                st.info("No matching fields found.")

        # Domain Explorer (old format)
        st.markdown("### 🏗️ Ontological Domains")
        domain_names = list(LOAN_ONTOLOGY.keys())
        selected_domain = st.selectbox(
            "Choose a domain to explore:",
            options=domain_names,
            format_func=lambda x: f"{x.replace('_', ' ').title()} ({len(LOAN_ONTOLOGY[x]['fields'])} fields)",
        )

        if selected_domain:
            domain_info = LOAN_ONTOLOGY[selected_domain]

            # Domain header card
            st.markdown(
                f"""
            <div style='background: linear-gradient(135deg, var(--color-accent-primary) 0%, var(--color-accent-primary-darker) 100%);
                        padding: 1.5rem; border-radius: 10px; margin: 1rem 0;'>
                <h4 style='color: white; margin: 0; font-weight: 500;'>
                    {selected_domain.replace('_', ' ').title()}
                </h4>
                <p style='color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0; font-size: 0.95rem;'>
                    {domain_info['domain_description']}
                </p>
            </div>
            """,
                unsafe_allow_html=True,
            )

            # Fields table
            st.markdown("#### 📋 Fields in this Domain")
            fields_data = []
            for field_name, field_meta in domain_info["fields"].items():
                risk_indicator = "🔴" if getattr(field_meta, "risk_impact", None) else "🟢"
                fields_data.append(
                    {
                        "Field": field_name,
                        "Risk": risk_indicator,
                        "Description": getattr(field_meta, "description", ""),
                        "Business Context": (
                            (getattr(field_meta, "business_context", "") or "")[:100]
                            + ("..." if len(getattr(field_meta, "business_context", "")) > 100 else "")
                        ),
                    }
                )

            fields_df = pd.DataFrame(fields_data)
            st.dataframe(
                fields_df,
                use_container_width=True,
                hide_index=True,
            )

            # Field detail explorer
            st.markdown("#### 🔍 Field Details")
            field_names = list(domain_info["fields"].keys())
            selected_field = st.selectbox(
                "Select a field for detailed information:",
                options=field_names,
                key=f"field_select_{selected_domain}",
            )

            if selected_field:
                field_meta = domain_info["fields"][selected_field]
                st.markdown(
                    f"""
                <div style='background: var(--color-background-alt); padding: 1.5rem; border-radius: 8px; border-left: 4px solid var(--color-accent-primary-darker);'>
                    <h5 style='color: var(--color-text-primary); margin-top: 0;'>{selected_field}</h5>
                    <p><strong>Domain:</strong> {getattr(field_meta, 'domain', selected_domain)}</p>
                    <p><strong>Data Type:</strong> <code>{getattr(field_meta, 'data_type', '')}</code></p>
                    <p><strong>Description:</strong> {getattr(field_meta, 'description', '')}</p>
                    <p><strong>Business Context:</strong> {getattr(field_meta, 'business_context', '')}</p>
                </div>
                """,
                    unsafe_allow_html=True,
                )

                if getattr(field_meta, "risk_impact", None):
                    st.warning(f"⚠️ **Risk Impact:** {getattr(field_meta, 'risk_impact', '')}")
                if getattr(field_meta, "values", None):
                    st.markdown("**Value Codes:**")
                    for code, description in getattr(field_meta, "values", {}).items():
                        st.markdown(f"• `{code}`: {description}")
                if getattr(field_meta, "relationships", None):
                    st.info(f"🔗 **Relationships:** {', '.join(getattr(field_meta, 'relationships', []))}")
        st.markdown("### ⚖️ Risk Assessment Framework")
        st.markdown(
            f"""
        <div style='background: var(--color-warning-bg); padding: 1rem; border-radius: 8px; border-left: 4px solid var(--color-accent-primary-darker); border: 1px solid var(--color-border-light); color: var(--color-warning-text);'>
            <p><strong>Credit Triangle:</strong> {PORTFOLIO_CONTEXT['risk_framework']['credit_triangle']}</p>
            <ul>
                <li><strong>Super Prime:</strong> {PORTFOLIO_CONTEXT['risk_framework']['risk_tiers']['super_prime']}</li>
                <li><strong>Prime:</strong> {PORTFOLIO_CONTEXT['risk_framework']['risk_tiers']['prime']}</li>
                <li><strong>Alt-A:</strong> {PORTFOLIO_CONTEXT['risk_framework']['risk_tiers']['alt_a']}</li>
            </ul>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with tab_manual:
        st.markdown(
            """
        <div style='margin-bottom: 1.5rem;'>
            <h3 style='color: var(--color-text-primary); font-weight: 400; margin-bottom: 0.5rem;'>
                🛠️ Manual SQL Query
            </h3>
            <p style='color: var(--color-text-secondary); margin: 0; font-size: 0.95rem;'>
                Write and execute SQL directly against the in-memory DuckDB table <code>data</code>.
            </p>
        </div>
        """,
            unsafe_allow_html=True,
        )

        # Sample queries for manual use
        sample_queries = {
            "": "",
            "Total Portfolio": "SELECT COUNT(*) as total_loans, ROUND(SUM(ORIG_UPB)/1000000, 2) as total_upb_millions FROM data",
            "Geographic Analysis": "SELECT STATE, COUNT(*) as loan_count, ROUND(AVG(ORIG_UPB), 0) as avg_upb, ROUND(AVG(ORIG_RATE), 2) as avg_rate FROM data WHERE STATE IS NOT NULL GROUP BY STATE ORDER BY loan_count DESC LIMIT 10",
            "Credit Risk": "SELECT CASE WHEN CSCORE_B < 620 THEN 'Subprime' WHEN CSCORE_B < 680 THEN 'Near Prime' WHEN CSCORE_B < 740 THEN 'Prime' ELSE 'Super Prime' END as credit_tier, COUNT(*) as loans, ROUND(AVG(OLTV), 1) as avg_ltv FROM data WHERE CSCORE_B IS NOT NULL GROUP BY credit_tier ORDER BY MIN(CSCORE_B)",
            "High LTV Analysis": "SELECT STATE, COUNT(*) as high_ltv_loans, ROUND(AVG(CSCORE_B), 0) as avg_credit_score FROM data WHERE OLTV > 90 AND STATE IS NOT NULL GROUP BY STATE HAVING COUNT(*) > 100 ORDER BY high_ltv_loans DESC",
        }

        # Sync selection -> textarea using session state to persist on reruns
        def _update_manual_sql():
            sel = st.session_state.get("manual_sample_query", "")
            st.session_state["manual_sql_text"] = sample_queries.get(sel, "")

        selected_sample = st.selectbox(
            "📋 Choose a sample query:",
            list(sample_queries.keys()),
            key="manual_sample_query",
            on_change=_update_manual_sql,
        )

        # Keep a compact, consistent editor area to avoid large empty gaps
        manual_sql = st.text_area(
            "Write your SQL query:",
            value=st.session_state.get("manual_sql_text", sample_queries[selected_sample]),
            height=140,
            placeholder="SELECT * FROM data LIMIT 10",
            help="Use 'data' as the table name",
            key="manual_sql_text",
        )

        # Always show execute button, disable if no query
        has_manual_sql = bool(manual_sql.strip())
        execute_manual = st.button(
            "🚀 Execute Manual Query",
            type="primary",
            use_container_width=True,
            disabled=not has_manual_sql,
            help="Enter SQL query above to execute" if not has_manual_sql else None,
            key="execute_manual_button",
        )

        if execute_manual and has_manual_sql:
            with st.spinner("⚡ Running manual query..."):
                start_time = time.time()
                result_df = execute_sql_query(manual_sql, st.session_state.get("parquet_files", []))
                execution_time = time.time() - start_time
                # Persist for re-renders and visualization
                st.session_state["manual_query_result_df"] = result_df
                st.session_state["last_result_tab"] = "tab_manual"
                display_results(result_df, "Manual Query Results", execution_time)

        # Persisted results rendering for Manual SQL tab: show last results across reruns
        if (
            st.session_state.get("last_result_tab") == "tab_manual"
            and isinstance(st.session_state.get("last_result_df"), pd.DataFrame)
            and not st.session_state.get("_rendered_this_run", False)
        ):
            display_results(
                st.session_state["last_result_df"],
                st.session_state.get("last_result_title", "Previous Results"),
            )

    with tab_schema:
        st.markdown(
            """
            <div style='margin-bottom: 1.5rem;'>
                <h3 style='color: var(--color-text-primary); font-weight: 400; margin-bottom: 0.5rem;'>
                    🗂️ Database Schema
                </h3>
                <p style='color: var(--color-text-secondary); margin: 0; font-size: 0.95rem;'>
                    Explore the physical schema and ontology-aligned views.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Schema presentation options
        schema_view = st.radio(
            "Choose schema view:",
            ["🎯 Quick Reference", "📋 Ontological Schema", "💻 Raw SQL"],
            horizontal=True,
        )

        schema_context = st.session_state.get("schema_context", "")

        if schema_view == "🎯 Quick Reference":
            # Quick reference with domain summary
            from src.data_dictionary import LOAN_ONTOLOGY

            st.markdown("#### Key Data Domains")

            # Create a compact domain overview
            for i in range(0, len(LOAN_ONTOLOGY), 3):  # Display in rows of 3
                cols = st.columns(3)
                domains = list(LOAN_ONTOLOGY.items())[i : i + 3]

                for j, (domain_name, domain_info) in enumerate(domains):
                    with cols[j]:
                        field_count = len(domain_info["fields"])

                        # Create colored cards for each domain
                        colors = [
                            "#F3E5D9",
                            "#E7C8B2",
                            "#F6EDE2",
                            "#E4C590",
                            "#ECD9C7",
                        ]
                        color = colors[i // 3 % len(colors)]

                        st.markdown(
                            f"""
                            <div style='background: {color}; color: var(--color-text-primary); padding: 1rem;
                                        border-radius: 8px; margin-bottom: 0.5rem; text-align: center; border: 1px solid var(--color-border-light);'>
                                <h5 style='margin: 0; font-size: 0.9rem;'>{domain_name.replace('_', ' ').title()}</h5>
                                <p style='margin: 0.25rem 0 0 0; font-size: 0.8rem; opacity: 0.85;'>
                                    {field_count} fields
                                </p>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

            # Sample fields reference
            st.markdown("#### 🔍 Common Fields")
            key_fields = {
                "LOAN_ID": "Unique loan identifier",
                "ORIG_DATE": "Origination date (MMYYYY)",
                "STATE": "State code (e.g., 'CA', 'TX')",
                "CSCORE_B": "Primary borrower FICO score",
                "OLTV": "Original loan-to-value ratio (%)",
                "DTI": "Debt-to-income ratio (%)",
                "ORIG_UPB": "Original unpaid balance ($)",
                "CURRENT_UPB": "Current unpaid balance ($)",
                "PURPOSE": "P=Purchase, R=Refi, C=CashOut",
            }

            field_cols = st.columns(2)
            field_items = list(key_fields.items())
            for i, (field, desc) in enumerate(field_items):
                col_idx = i % 2
                with field_cols[col_idx]:
                    st.markdown(f"• **{field}**: {desc}")

        elif schema_view == "📋 Ontological Schema":
            # Organized schema by domains
            if schema_context:
                # Extract the organized parts of the schema
                lines = schema_context.split("\n")
                in_create_table = False
                current_section = []
                sections = []

                for line in lines:
                    if "CREATE TABLE" in line:
                        if current_section:
                            sections.append("\n".join(current_section))
                        current_section = [line]
                        in_create_table = True
                    elif in_create_table:
                        current_section.append(line)
                        if line.strip() == ");":
                            in_create_table = False
                    elif not in_create_table and line.strip():
                        current_section.append(line)

                if current_section:
                    sections.append("\n".join(current_section))

                # Display each section with better formatting
                for i, section in enumerate(sections):
                    if "CREATE TABLE" in section:
                        table_name = section.split("CREATE TABLE ")[1].split(" (")[0]
                        with st.expander(f"📊 Table: {table_name.upper()}", expanded=i == 0):
                            st.code(section, language="sql")
                    elif section.strip():
                        with st.expander("📚 Business Intelligence Context", expanded=False):
                            st.text(section)
            else:
                st.warning("Schema not available")

        else:  # Raw SQL
            # Raw SQL schema view
            with st.expander("🗂️ Complete SQL Schema", expanded=False):
                if schema_context:
                    st.code(schema_context, language="sql")
                else:
                    st.warning("Schema not available")
