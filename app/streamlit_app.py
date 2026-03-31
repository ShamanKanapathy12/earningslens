import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from agent.react_agent import run_agent

st.set_page_config(
    page_title="EarningsLens",
    page_icon="📊",
    layout="wide"
)

st.title("📊 EarningsLens")
st.caption("Agentic RAG system for earnings call intelligence")

with st.sidebar:
    st.header("Configuration")
    company = st.selectbox("Company", ["AAPL", "NVDA"])
    quarter_a = st.selectbox("Compare Quarter A", ["Q1", "Q2", "Q3"], index=0)
    quarter_b = st.selectbox("Compare Quarter B", ["Q1", "Q2", "Q3"], index=2)
    st.divider()
    st.markdown("**Sample questions:**")
    st.caption("How did management discuss iPhone revenue and demand?")
    st.caption("What did Apple say about services growth and future outlook?")
    st.caption("How did management tone change regarding China?")
    st.caption("What did the CFO say about gross margins?")
    st.caption("How did Nvidiscuss data center growth?")
    st.caption("What did management say about AI and GPU demand?")
    st.divider()
    st.caption("Data sourced from real earnings call transcripts")

st.subheader("Ask a question")
question = st.text_input(
    "Question",
    placeholder="e.g. How did management discuss iPhone revenue and demand?",
    label_visibility="collapsed"
)

if st.button("Analyze", type="primary"):
    if not question.strip():
        st.warning("Please enter a question before analyzing.")
    elif quarter_a == quarter_b:
        st.error("Please select two different quarters to compare.")
    else:
        with st.spinner(f"Analyzing {company} {quarter_a} vs {quarter_b}..."):
            result = run_agent(
                user_question=question,
                company=company,
                quarter_a=quarter_a,
                quarter_b=quarter_b
            )

        sentiment = result["sentiment"]
        score_a = sentiment["quarter_a"]["scores"]
        score_b = sentiment["quarter_b"]["scores"]
        delta = sentiment["delta"]

        st.divider()
        st.subheader("Sentiment Comparison")

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Optimism", f"{score_b['optimism']}", f"{delta['optimism']:+d} pts")
        with col2:
            st.metric("Caution", f"{score_b['caution']}", f"{delta['caution']:+d} pts")
        with col3:
            st.metric("Growth Confidence", f"{score_b['growth_confidence']}", f"{delta['growth_confidence']:+d} pts")
        with col4:
            st.metric("Uncertainty", f"{score_b['uncertainty']}", f"{delta['uncertainty']:+d} pts")

        st.divider()
        st.subheader("Analysis")
        st.write(result["answer"])

        st.divider()
        st.subheader("Source Passages")

        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown(f"**{quarter_a} passages**")
            for i, chunk in enumerate(result["sources"][quarter_a][:3]):
                with st.expander(f"Source {i+1}"):
                    st.write(chunk["text"][:400])

        with col_b:
            st.markdown(f"**{quarter_b} passages**")
            for i, chunk in enumerate(result["sources"][quarter_b][:3]):
                with st.expander(f"Source {i+1}"):
                    st.write(chunk["text"][:400])
