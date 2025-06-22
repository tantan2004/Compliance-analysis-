import streamlit as st
import json
import os
import tempfile
from analyzer import Analysis
import html

# Page configuration
st.set_page_config(
    page_title="Compliance Analysis Tool",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for neutral styling
st.markdown("""
<style>
    .stApp {
        background-color: #ffffff;  /* white background */
    }
    .main-header {
        font-size: 2.2rem;
        color: #333333;
        text-align: center;
        margin-bottom: 2rem;
    }
    .risk-high {
        background-color: #f8d7da;
        border-left: 5px solid #d9534f;
        padding: 15px;
        margin: 15px 0;
        border-radius: 8px;
    }
    .risk-medium {
        background-color: #fff3cd;
        border-left: 5px solid #f0ad4e;
        padding: 15px;
        margin: 15px 0;
        border-radius: 8px;
    }
    .risk-low {
        background-color: #d4edda;
        border-left: 5px solid #5cb85c;
        padding: 15px;
        margin: 15px 0;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# Session state initialization
if 'analysis' not in st.session_state:
    st.session_state.analysis = None
if 'results' not in st.session_state:
    st.session_state.results = None
if 'rules_path' not in st.session_state:
    st.session_state.rules_path = None

# Page title
st.markdown("<div class='main-header'>Compliance Analysis Tool</div>", unsafe_allow_html=True)

# Upload rules file
st.subheader("Upload Rules File")
rules_file = st.file_uploader("Choose a rules file (JSON, TXT, YAML)", type=["json", "txt", "yaml", "yml"])
if rules_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{rules_file.name.split('.')[-1]}") as tmp_rule:
        tmp_rule.write(rules_file.read())
        st.session_state.rules_path = tmp_rule.name

# Upload document
st.subheader("Upload Document")
uploaded_file = st.file_uploader("Choose a document (TXT, PDF, DOCX)", type=['txt', 'pdf', 'docx'])
custom_query = st.text_area("Custom Query", "Summarize all compliance risks in the document.")

if uploaded_file and st.session_state.rules_path:
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_path = tmp_file.name

    if st.button("Analyze"):
        try:
            st.session_state.analysis = Analysis(rule_file=st.session_state.rules_path)
            results = st.session_state.analysis.analyze_file(tmp_path, custom_query)
            st.session_state.results = results
            os.unlink(tmp_path)
            st.success("Analysis completed successfully.")
        except Exception as e:
            st.error(f"Error during analysis: {e}")

# Display results
if st.session_state.results:
    res = st.session_state.results
    risk = res['risk_level'].lower()
    risk_class = {
        'high': 'risk-high',
        'medium': 'risk-medium',
        'low': 'risk-low'
    }.get(risk, '')

    st.markdown(f"<div class='{risk_class}'><strong>Risk Level:</strong> {res['risk_level']}</div>", unsafe_allow_html=True)
    st.markdown(f"**Total Violations:** {len(res['rule_based_violations'])}")

    st.markdown("---")
    st.subheader("AI Summary")
    st.markdown(res['ai_summary'])

    st.markdown("---")
    st.subheader("Violations")

    for i, v in enumerate(res['rule_based_violations']):
        rule = html.escape(v.get('rule', 'N/A'))
        match_text = html.escape(v.get('match', 'N/A'))
        context = html.escape(v.get('context', 'N/A'))
        judgment = v.get('llm_judgment', 'N/A')

        if hasattr(judgment, "content"):
            judgment = judgment.content

        # Escape and format LLM assessment properly
        judgment_html = html.escape(judgment).replace("\n", "<br>")

        with st.expander(f"Violation {i+1}: Rule - {rule}"):
            st.markdown(f"**Matched Text:** `{match_text}`")
            st.markdown(f"**Context:**\n\n```\n{context}\n```")
            st.markdown("**LLM Assessment:**", unsafe_allow_html=True)
            st.markdown(f"<div style='padding-left:10px'>{judgment_html}</div>", unsafe_allow_html=True)
