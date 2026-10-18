import os
import tempfile
import streamlit as st

from rag import ingest_pdf, search_clauses
from agent import get_legal_answer

# Page Configuration
st.set_page_config(
    page_title="Legal Document AI Assistant",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Custom Styling for Premium Aesthetics and Clear Visual Separation
st.markdown(
    """
    <style>
    /* Main container styling */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Header styling */
    .main-header {
        font-size: 2rem;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 0.25rem;
    }
    .sub-header {
        font-size: 1rem;
        color: #64748b;
        margin-bottom: 1.5rem;
    }
    
    /* Card containers */
    .doc-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 16px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
        margin-top: 12px;
    }
    
    /* Source passage box */
    .source-quote-box {
        background-color: #f8fafc;
        border-left: 4px solid #3b82f6;
        padding: 12px 16px;
        margin-top: 8px;
        margin-bottom: 8px;
        border-radius: 4px;
        color: #1e293b;
        font-size: 0.95rem;
        line-height: 1.5;
        font-style: italic;
    }
    
    .source-header {
        font-size: 0.85rem;
        font-weight: 600;
        color: #3b82f6;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-top: 6px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Header Section
st.markdown('<div class="main-header">⚖️ Legal Document AI Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Review clauses, verify obligations, and inspect quoted legal passages on-device.</div>', unsafe_allow_html=True)

# Helper function to render AI response with distinct separation between explanation and sources
def render_assistant_response(explanation, context=None):
    st.markdown("#### 💡 AI Explanation")
    
    # Handle dict or string response gracefully
    if isinstance(explanation, dict):
        text_body = (
            explanation.get("explanation")
            or explanation.get("answer")
            or explanation.get("plain_language")
            or str(explanation)
        )
        st.markdown(text_body)
        
        # Check if quotes/passages are bundled in the response dict
        dict_quotes = explanation.get("quotes") or explanation.get("passages")
        if dict_quotes and not context:
            context = dict_quotes
    else:
        st.markdown(str(explanation))

    # Distinct Quoted Source Passages Section
    if context:
        st.markdown("---")
        st.markdown("#### 📜 Quoted Source Passages")
        
        with st.container():
            if isinstance(context, list):
                for idx, passage in enumerate(context, start=1):
                    if isinstance(passage, dict):
                        heading = passage.get("heading") or f"Clause {passage.get('id', idx)}"
                        page = f" (Page {passage['page']})" if "page" in passage else ""
                        text = passage.get("text") or passage.get("quote") or str(passage)
                        st.markdown(f'<div class="source-header">Source {idx}: {heading}{page}</div>', unsafe_allow_html=True)
                        st.markdown(f'<div class="source-quote-box">"{text}"</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="source-header">Source Passage {idx}</div>', unsafe_allow_html=True)
                        st.markdown(f'<div class="source-quote-box">"{passage}"</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="source-header">Context Passage</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="source-quote-box">"{context}"</div>', unsafe_allow_html=True)

# Session State Initialization
if "messages" not in st.session_state:
    st.session_state.messages = []
if "ingested" not in st.session_state:
    st.session_state.ingested = False
if "current_file" not in st.session_state:
    st.session_state.current_file = None
if "temp_path" not in st.session_state:
    st.session_state.temp_path = None

# Two-Column Layout
col_doc, col_chat = st.columns([1, 1.2], gap="large")

# ----------------- Left Column (Document) -----------------
with col_doc:
    st.subheader("📄 Document Ingestion")
    
    uploaded_file = st.file_uploader(
        "Upload a PDF Agreement",
        type=["pdf"],
        help="Upload contracts, lease agreements, or legal disclosures in PDF format.",
    )
    
    if uploaded_file is not None:
        # Check if the file is newly uploaded to avoid redundant re-processing on reruns
        if st.session_state.current_file != uploaded_file.name:
            # Save to temporary local path
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(uploaded_file.getvalue())
                temp_path = tmp.name
            
            st.session_state.temp_path = temp_path
            st.session_state.current_file = uploaded_file.name
            
            # Display success message
            st.success(f"File uploaded successfully! Saved to temporary path: `{temp_path}`")
            
            # Ingest document
            with st.spinner("Ingesting and indexing document clauses..."):
                ingest_pdf(temp_path)
            
            st.session_state.ingested = True
        else:
            st.success(f"File active: **{uploaded_file.name}**")
        
        # Document Summary Card
        st.markdown(
            f"""
            <div class="doc-card">
                <p style="margin: 0; font-weight: 600; color: #1e293b;">{uploaded_file.name}</p>
                <p style="margin: 4px 0 0 0; font-size: 0.85rem; color: #64748b;">
                    Size: {uploaded_file.size / 1024:.1f} KB &nbsp;|&nbsp; 
                    <span style="color: #16a34a; font-weight: 500;">✓ Ingested & Ready for Q&A</span>
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.info("👆 Please upload a PDF file to begin asking questions.")
        st.session_state.ingested = False
        st.session_state.current_file = None

# ----------------- Right Column (Chat) -----------------
with col_chat:
    st.subheader("💬 Legal Clause Q&A")
    
    # Display existing chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if message["role"] == "user":
                st.markdown(message["content"])
            else:
                render_assistant_response(message["explanation"], message.get("context"))
    
    # User Query Submission
    if user_query := st.chat_input("Ask a question about the document..."):
        if not st.session_state.ingested:
            st.warning("Please upload a PDF document on the left first.")
        else:
            # Append & display user message
            st.session_state.messages.append({"role": "user", "content": user_query})
            with st.chat_message("user"):
                st.markdown(user_query)
            
            # Process query with RAG and Agent
            with st.chat_message("assistant"):
                with st.spinner("Searching clauses and analyzing legal context..."):
                    context = search_clauses(user_query)
                    explanation = get_legal_answer(user_query, context)
                    render_assistant_response(explanation, context)
            
            # Store in session state
            st.session_state.messages.append({
                "role": "assistant",
                "explanation": explanation,
                "context": context,
            })

# Permanent Disclaimer Footer
st.markdown("---")
st.caption(
    "⚖️ **Disclaimer:** This tool is intended for preliminary document understanding only "
    "and does not constitute legal advice. Always consult a qualified legal professional for binding decisions."
)
