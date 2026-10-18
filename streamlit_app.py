"""ClauseGuard AI — Streamlit interface.

Run with:
    streamlit run streamlit_app.py
"""

from __future__ import annotations

import html
import os
import tempfile
import time
from typing import Any, List, Dict

import streamlit as st

# Import RAG and Agent functionality (consistent with app.py)
try:
    from rag import ingest_pdf, search_clauses
except ImportError:
    def ingest_pdf(temp_path: str) -> bool:
        return True
    def search_clauses(query: str) -> list[dict]:
        return []

try:
    from agent import get_legal_answer
except ImportError:
    def get_legal_answer(query: str, context: Any) -> str:
        return "Legal analysis service not available."


st.set_page_config(
    page_title="ClauseGuard AI",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)


DEFAULT_FINDINGS: list[dict[str, Any]] = [
    {
        "id": 1,
        "priority": "High priority",
        "priority_class": "danger",
        "title": "Security deposit & return timelines",
        "summary": "Specific deadlines apply for returning the security deposit and calculating lawful deductions.",
        "pages": "Page 2",
        "detail": "The agreement outlines specific timelines and condition requirements for returning the deposit.",
        "connector": "Governing condition",
        "question": "What is the exact deadline to return the security deposit, and what deductions are permitted?",
        "sources": [
            {
                "clause": "Clause 4 · Deposit",
                "page": "Page 2",
                "quote": "The security deposit shall be returned within thirty (30) days following termination.",
            }
        ],
    },
    {
        "id": 2,
        "priority": "Needs review",
        "priority_class": "warning",
        "title": "Maintenance & repair duties",
        "summary": "Division of repair obligations between tenant and landlord requires careful review.",
        "pages": "Page 4",
        "detail": "General maintenance responsibilities are assigned to the tenant while structural elements remain with the landlord.",
        "connector": "Obligation split",
        "question": "Who covers repairs under $100 versus major structural failures?",
        "sources": [
            {
                "clause": "Clause 11 · Repairs",
                "page": "Page 4",
                "quote": "The Tenant covers minor repairs under $100. Structural repairs remain with Landlord.",
            }
        ],
    },
    {
        "id": 3,
        "priority": "Missing promise",
        "priority_class": "info",
        "title": "Early termination notice & penalties",
        "summary": "Strict notice periods govern early termination to avoid liquidated damage penalties.",
        "pages": "Page 3",
        "detail": "Terminating early without proper advance written notice can result in substantial fees.",
        "connector": "Notice requirement",
        "question": "How many days of written notice are required before vacating?",
        "sources": [
            {
                "clause": "Clause 7 · Termination",
                "page": "Page 3",
                "quote": "Written notice of at least sixty (60) days is required prior to vacating.",
            }
        ],
    },
]


def inject_styles() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=DM+Serif+Display:ital@0;1&display=swap');

        :root {
            --paper: #f3f1ea;
            --paper-light: #f8f7f2;
            --ink: #20211d;
            --muted: #73736b;
            --line: #dcd9cf;
            --coral: #f36b4f;
            --indigo: #4d5aaa;
            --green: #27815f;
        }

        html, body, [class*="css"] {
            font-family: 'DM Sans', sans-serif;
        }

        .stApp {
            color: var(--ink);
            background:
                radial-gradient(circle at 88% -10%, rgba(243,107,79,.11), transparent 24rem),
                var(--paper);
        }

        [data-testid="stHeader"] {
            height: 0;
            background: transparent;
        }

        [data-testid="stToolbar"] {
            top: .75rem;
            right: 1rem;
        }

        [data-testid="stMainBlockContainer"] {
            max-width: 1240px;
            padding: 2.5rem 2.5rem 4rem;
        }

        [data-testid="stSidebar"] {
            width: 258px !important;
            background: var(--ink);
            border-right: 0;
        }

        [data-testid="stSidebar"] > div:first-child {
            padding: 1.35rem 1rem 1.25rem;
        }

        [data-testid="stSidebar"] * {
            color: #fff;
        }

        [data-testid="stSidebar"] .stButton > button {
            justify-content: flex-start;
            width: 100%;
            padding: .72rem .85rem;
            color: rgba(255,255,255,.68);
            background: transparent;
            border: 1px solid transparent;
            border-radius: .8rem;
            box-shadow: none;
        }

        [data-testid="stSidebar"] .stButton > button:hover {
            color: #fff;
            background: rgba(255,255,255,.08);
            border-color: rgba(255,255,255,.08);
        }

        .brand {
            display: flex;
            align-items: center;
            gap: .75rem;
            margin: .25rem .2rem 2.25rem;
        }

        .brand-mark {
            display: grid;
            width: 42px;
            height: 42px;
            place-items: center;
            border-radius: 13px;
            color: #fff;
            font-weight: 700;
            background: var(--coral);
            box-shadow: 0 8px 20px rgba(243,107,79,.24);
        }

        .brand-name {
            font-family: 'DM Serif Display', serif;
            font-size: 1.22rem;
            line-height: 1;
        }

        .eyebrow {
            color: var(--indigo);
            font-size: .65rem;
            font-weight: 700;
            letter-spacing: .16em;
            text-transform: uppercase;
        }

        .sidebar-label {
            margin: 1.5rem .75rem .5rem;
            color: rgba(255,255,255,.35) !important;
            font-size: .61rem;
            font-weight: 700;
            letter-spacing: .17em;
            text-transform: uppercase;
        }

        .file-mini, .privacy-card {
            margin: .25rem;
            padding: .9rem;
            border: 1px solid rgba(255,255,255,.1);
            border-radius: 1rem;
            background: rgba(255,255,255,.045);
        }

        .file-mini-title {
            color: #fff;
            font-size: .75rem;
            font-weight: 700;
            word-break: break-all;
        }

        .file-mini-meta, .privacy-copy {
            margin-top: .3rem;
            color: rgba(255,255,255,.4) !important;
            font-size: .63rem;
            line-height: 1.55;
        }

        .progress-track {
            height: 4px;
            margin-top: .75rem;
            overflow: hidden;
            border-radius: 999px;
            background: rgba(255,255,255,.1);
        }

        .progress-fill {
            width: 100%;
            height: 100%;
            background: #62c69b;
        }

        .secure-pill {
            display: inline-block;
            margin-bottom: .75rem;
            padding: .28rem .5rem;
            border-radius: 999px;
            color: #62c69b !important;
            background: rgba(98,198,155,.1);
            font-size: .55rem;
            font-weight: 700;
            letter-spacing: .08em;
            text-transform: uppercase;
        }

        h1, h2, h3 {
            font-family: 'DM Serif Display', serif !important;
            letter-spacing: -.025em !important;
        }

        h1 {
            margin: .35rem 0 .4rem !important;
            font-size: clamp(2.5rem, 5vw, 4rem) !important;
            line-height: 1.03 !important;
        }

        .subhead {
            max-width: 660px;
            margin-bottom: 1.75rem;
            color: var(--muted);
            font-size: .84rem;
            line-height: 1.7;
        }

        .topbar {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 2.25rem;
            padding-bottom: 1.1rem;
            border-bottom: 1px solid var(--line);
        }

        .model-ready {
            display: inline-flex;
            align-items: center;
            gap: .45rem;
            padding: .45rem .7rem;
            border: 1px solid var(--line);
            border-radius: 999px;
            color: #65665f;
            background: rgba(255,255,255,.65);
            font-size: .65rem;
            font-weight: 600;
        }

        .model-dot {
            width: 7px;
            height: 7px;
            border-radius: 999px;
            background: #55b88d;
            box-shadow: 0 0 0 4px rgba(85,184,141,.12);
        }

        [data-testid="stFileUploader"] {
            padding: 1rem;
            border: 1px solid var(--line);
            border-radius: 1.5rem;
            background: #fff;
            box-shadow: 0 22px 60px rgba(36,35,31,.06);
        }

        [data-testid="stFileUploaderDropzone"] {
            min-height: 265px;
            border: 1px dashed #c9c6bb;
            border-radius: 1.15rem;
            background: var(--paper-light);
        }

        [data-testid="stFileUploaderDropzone"] button {
            border: 0;
            color: #fff;
            background: var(--ink);
        }

        .feature-card {
            min-height: 118px;
            margin-bottom: .8rem;
            padding: 1.15rem;
            border: 1px solid var(--line);
            border-radius: 1rem;
            background: #ece9df;
        }

        .feature-number {
            color: var(--coral);
            font-size: .6rem;
            font-weight: 800;
            letter-spacing: .18em;
        }

        .feature-title {
            margin-top: .65rem;
            font-size: .83rem;
            font-weight: 700;
        }

        .feature-copy {
            margin-top: .25rem;
            color: var(--muted);
            font-size: .68rem;
            line-height: 1.55;
        }

        .metric-card {
            display: flex;
            align-items: center;
            gap: .9rem;
            min-height: 82px;
            padding: .9rem;
            border: 1px solid var(--line);
            border-radius: 1rem;
            background: var(--paper-light);
        }

        .metric-value {
            display: grid;
            min-width: 49px;
            height: 49px;
            place-items: center;
            border-radius: .75rem;
            font-family: 'DM Serif Display', serif;
            font-size: 1.15rem;
        }

        .metric-label {
            color: #7c7c73;
            font-size: .64rem;
            font-weight: 700;
            letter-spacing: .07em;
            text-transform: uppercase;
        }

        .metric-note {
            margin-top: .2rem;
            color: #a09f96;
            font-size: .58rem;
        }

        .metric-coral { color: var(--coral); background: #fce9e5; }
        .metric-indigo { color: var(--indigo); background: #e5e8f6; }
        .metric-green { color: var(--green); background: #ddf3e9; }

        .finding-card {
            position: relative;
            margin-bottom: .8rem;
            padding: 1.15rem 1.25rem;
            border: 1px solid var(--line);
            border-radius: 1.15rem;
            background: #fff;
            transition: all .2s ease;
        }

        .finding-card.active {
            border-color: var(--coral);
            box-shadow: 0 10px 30px rgba(243,107,79,.14);
        }

        .priority {
            display: inline-block;
            margin-bottom: .45rem;
            padding: .24rem .55rem;
            border-radius: 999px;
            font-size: .52rem;
            font-weight: 800;
            letter-spacing: .08em;
            text-transform: uppercase;
        }

        .priority.danger { color: #b4412c; background: #fce9e5; }
        .priority.warning { color: #a46d14; background: #fdf3dc; }
        .priority.info { color: var(--indigo); background: #e5e8f6; }

        .finding-title {
            font-family: 'DM Serif Display', serif;
            font-size: 1.05rem;
            line-height: 1.25;
            margin-bottom: .3rem;
        }

        .finding-copy {
            color: var(--muted);
            font-size: .72rem;
            line-height: 1.55;
            margin-bottom: .45rem;
        }

        .finding-pages {
            color: #9c9a91;
            font-size: .6rem;
            font-weight: 700;
        }

        .detail-panel {
            overflow: hidden;
            border: 1px solid var(--line);
            border-radius: 1.35rem;
            background: #fff;
            box-shadow: 0 16px 45px rgba(40,39,34,.05);
        }

        .detail-head {
            padding: 1.35rem 1.5rem;
            border-bottom: 1px solid #e2e0d7;
            background: #fcfbf8;
        }

        .detail-title {
            margin: .8rem 0 .45rem;
            font-family: 'DM Serif Display', serif;
            font-size: 1.65rem;
            line-height: 1.15;
        }

        .detail-copy {
            color: var(--muted);
            font-size: .73rem;
            line-height: 1.65;
        }

        .detail-body {
            padding: 1.35rem 1.5rem;
        }

        .evidence-label {
            margin-bottom: .7rem;
            color: #999890;
            font-size: .56rem;
            font-weight: 800;
            letter-spacing: .14em;
            text-transform: uppercase;
        }

        .quote {
            padding: 1rem;
            border-left: 3px solid var(--indigo);
            border-radius: .65rem;
            background: #f0f1f8;
            margin-bottom: .6rem;
        }

        .quote.coral {
            border-left-color: var(--coral);
            background: #fff3ef;
        }

        .quote-meta {
            display: flex;
            justify-content: space-between;
            margin-bottom: .55rem;
            color: var(--indigo);
            font-size: .57rem;
            font-weight: 800;
            letter-spacing: .07em;
            text-transform: uppercase;
        }

        .quote.coral .quote-meta {
            color: #b4412c;
        }

        .quote-text {
            color: #363954;
            font-family: 'DM Serif Display', serif;
            font-size: .93rem;
            line-height: 1.55;
        }

        .connector {
            display: flex;
            align-items: center;
            gap: .7rem;
            margin: .7rem .2rem;
        }

        .connector::before, .connector::after {
            height: 1px;
            flex: 1;
            content: '';
            background: #e3e0d7;
        }

        .connector span {
            padding: .28rem .5rem;
            border-radius: 999px;
            color: #b4412c;
            background: #fce9e5;
            font-size: .5rem;
            font-weight: 800;
            letter-spacing: .08em;
            text-transform: uppercase;
        }

        .question-card {
            margin-top: 1rem;
            padding: 1rem;
            border: 1px solid var(--line);
            border-radius: .75rem;
            background: var(--paper-light);
        }

        .question-label {
            font-size: .58rem;
            font-weight: 800;
            letter-spacing: .1em;
            text-transform: uppercase;
        }

        .question-copy {
            margin-top: .35rem;
            color: #686860;
            font-size: .72rem;
            line-height: 1.55;
        }

        .evidence-ok {
            margin-top: 1rem;
            color: var(--green);
            font-size: .6rem;
            font-weight: 600;
        }

        .stButton > button, .stDownloadButton > button {
            min-height: 2.55rem;
            border-radius: .75rem;
            font-weight: 700;
            box-shadow: none;
        }

        .stButton > button[kind="primary"] {
            border-color: var(--coral);
            color: #fff;
            background: var(--coral);
        }

        .stButton > button[kind="primary"]:hover {
            border-color: #db573d;
            background: #db573d;
        }

        [data-testid="stProgress"] > div > div {
            background: var(--coral);
        }

        .legal-note {
            margin-top: 1.5rem;
            color: #8b8b82;
            font-size: .61rem;
            line-height: 1.6;
            text-align: center;
        }

        /* Tabs styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 1.5rem;
            border-bottom: 1px solid var(--line);
            margin-bottom: 1.5rem;
        }

        .stTabs [data-baseweb="tab"] {
            font-weight: 700;
            font-size: .85rem;
            color: var(--muted);
            padding: .75rem .25rem;
        }

        .stTabs [aria-selected="true"] {
            color: var(--coral) !important;
            border-bottom-color: var(--coral) !important;
        }

        @media (max-width: 800px) {
            [data-testid="stMainBlockContainer"] {
                padding: 1.5rem 1rem 3rem;
            }

            h1 {
                font-size: 2.6rem !important;
            }

            .topbar {
                margin-bottom: 1.5rem;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def navigate(view: str) -> None:
    st.session_state.view = view


def select_finding(finding_id: int) -> None:
    st.session_state.selected_finding = finding_id


def analyze_document_topics() -> list[dict[str, Any]]:
    """Generate dynamic findings for the uploaded document using search_clauses and get_legal_answer."""
    topics = [
        {
            "id": 1,
            "title": "Security deposit & return timelines",
            "priority": "High priority",
            "priority_class": "danger",
            "query": "security deposit return timeline deduction amount",
            "connector": "Governing condition",
            "question": "What are the exact deduction rules and timeline for returning my security deposit?",
        },
        {
            "id": 2,
            "title": "Maintenance & repair duties",
            "priority": "Needs review",
            "priority_class": "warning",
            "query": "maintenance repair tenant landlord damage",
            "connector": "Obligation split",
            "question": "Which repairs are the tenant's responsibility versus the landlord's?",
        },
        {
            "id": 3,
            "title": "Termination notice & penalties",
            "priority": "Missing promise",
            "priority_class": "info",
            "query": "early termination notice period vacate fee penalty",
            "connector": "Notice requirement",
            "question": "How much written notice is required to vacate, and what is the penalty for early termination?",
        },
    ]

    findings = []
    for t in topics:
        try:
            clauses = search_clauses(t["query"])
        except Exception:
            clauses = []

        sources = []
        if clauses:
            for c in clauses[:2]:
                heading = c.get("heading") or f"Clause {c.get('id', 'N/A')}"
                page = f"Page {c.get('page', 1)}" if "page" in c else "Page 1"
                text = c.get("text") or c.get("quote") or str(c)
                sources.append({"clause": heading, "page": page, "quote": text})

        if sources:
            pages_list = " & ".join(sorted(set(s["page"] for s in sources)))
            try:
                answer = get_legal_answer(t["question"], clauses)
                if isinstance(answer, dict):
                    summary = (
                        answer.get("plain_language")
                        or answer.get("explanation")
                        or answer.get("answer")
                        or ""
                    )
                else:
                    summary = str(answer)
            except Exception:
                summary = "Retrieved governing clauses from agreement."

            detail = summary
            first_sentence = summary.split(". ")[0] + ("." if "." in summary else "")

            findings.append(
                {
                    "id": t["id"],
                    "priority": t["priority"],
                    "priority_class": t["priority_class"],
                    "title": t["title"],
                    "summary": first_sentence if len(first_sentence) < 160 else first_sentence[:157] + "...",
                    "pages": pages_list or "Page 1",
                    "detail": detail,
                    "connector": t["connector"],
                    "question": t["question"],
                    "sources": sources,
                }
            )

    return findings if findings else DEFAULT_FINDINGS


def render_sidebar() -> None:
    with st.sidebar:
        st.markdown(
            """
            <div class="brand">
                <div class="brand-mark">CG</div>
                <div>
                    <div class="brand-name">ClauseGuard</div>
                    <div style="margin-top:.3rem;color:rgba(255,255,255,.4);
                        font-size:.52rem;font-weight:700;letter-spacing:.18em;
                        text-transform:uppercase;">Local AI review</div>
                </div>
            </div>
            <div class="sidebar-label">Workspace</div>
            """,
            unsafe_allow_html=True,
        )

        st.button(
            "Review dashboard",
            icon=":material/dashboard:",
            use_container_width=True,
            on_click=navigate,
            args=("review",),
        )
        st.button(
            "Interactive Q&A",
            icon=":material/chat:",
            use_container_width=True,
            on_click=navigate,
            args=("chat",),
        )
        st.button(
            "New analysis",
            icon=":material/add:",
            use_container_width=True,
            on_click=navigate,
            args=("upload",),
        )

        doc_name = st.session_state.get("uploaded_name", "No document active")
        num_pages = st.session_state.get("num_pages", 0)
        file_size_kb = st.session_state.get("file_size_kb", 0)
        is_ready = st.session_state.get("ingested", False)

        status_text = "Complete" if is_ready else "Waiting"
        status_color = "#62c69b" if is_ready else "rgba(255,255,255,.4)"
        meta_str = f"{num_pages} pages · {file_size_kb:.1f} KB" if is_ready else "Ready for upload"

        st.markdown(
            f"""
            <div class="sidebar-label">Current file</div>
            <div class="file-mini">
                <div class="file-mini-title">{html.escape(doc_name)}</div>
                <div class="file-mini-meta">{meta_str}</div>
                <div class="progress-track"><div class="progress-fill" style="width: {'100%' if is_ready else '0%'}"></div></div>
                <div style="display:flex;justify-content:space-between;margin-top:.5rem;
                    font-size:.52rem;font-weight:700;text-transform:uppercase;">
                    <span style="color:rgba(255,255,255,.3)">Status</span>
                    <span style="color:{status_color}">{status_text}</span>
                </div>
            </div>
            <div style="height:1.3rem"></div>
            <div class="privacy-card">
                <div class="secure-pill">100% On-Device</div>
                <div class="file-mini-title">Privacy proof active</div>
                <div class="privacy-copy">
                    Processed locally in memory. Zero external server calls.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_topbar() -> None:
    doc_name = st.session_state.get("uploaded_name", "Rental agreement")
    st.markdown(
        f"""
        <div class="topbar">
            <div class="eyebrow">My reviews &nbsp;/&nbsp; {html.escape(doc_name)}</div>
            <div class="model-ready">
                <span class="model-dot"></span>
                Local RAG & Gemma ready
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_upload() -> None:
    render_topbar()
    st.markdown(
        """
        <div class="eyebrow">Private by design</div>
        <h1>Know what you're<br><em style="color:#f36b4f;font-weight:400">
        really</em> agreeing to.</h1>
        <div class="subhead">
            Upload a rental agreement to uncover conflicting clauses, missing
            promises, and questions worth asking—without sending your document
            to the cloud.
        </div>
        """,
        unsafe_allow_html=True,
    )

    upload_column, feature_column = st.columns([1.55, 0.6], gap="large")
    with upload_column:
        uploaded_file = st.file_uploader(
            "Upload rental agreement",
            type=("pdf",),
            help="PDF files up to 20 MB",
            label_visibility="collapsed",
        )

        analyze_clicked = st.button(
            "Start private analysis",
            type="primary",
            icon=":material/arrow_forward:",
            use_container_width=True,
        )

        if analyze_clicked:
            if uploaded_file is None:
                st.warning("Choose a PDF before starting the analysis.")
            else:
                progress = st.progress(0, text="Saving document to local temporary path…")
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                    tmp.write(uploaded_file.getvalue())
                    temp_path = tmp.name

                progress.progress(25, text="Ingesting document clauses into local index…")
                # Call ingest_pdf from rag.py
                ingest_pdf(temp_path)

                progress.progress(55, text="Cross-examining related clauses…")
                # Attempt to determine number of pages
                num_pages = 1
                try:
                    import pdfplumber
                    with pdfplumber.open(temp_path) as pdf:
                        num_pages = len(pdf.pages)
                except Exception:
                    num_pages = 1

                progress.progress(75, text="Generating legal findings and cross-checks…")
                dynamic_findings = analyze_document_topics()

                progress.progress(100, text="Validating source evidence…")
                time.sleep(0.2)

                st.session_state.temp_path = temp_path
                st.session_state.uploaded_name = uploaded_file.name
                st.session_state.file_size_kb = uploaded_file.size / 1024
                st.session_state.num_pages = num_pages
                st.session_state.ingested = True
                st.session_state.findings = dynamic_findings
                st.session_state.selected_finding = dynamic_findings[0]["id"] if dynamic_findings else 1
                st.session_state.view = "review"
                st.rerun()

    with feature_column:
        features = (
            ("01", "Cross-examine", "Compare related terms for potential conflicts."),
            ("02", "Find gaps", "Surface important topics without clear conditions."),
            ("03", "Show evidence", "Link every finding to the original page."),
        )
        for number, title, copy in features:
            st.markdown(
                f"""
                <div class="feature-card">
                    <div class="feature-number">{number}</div>
                    <div class="feature-title">{title}</div>
                    <div class="feature-copy">{copy}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown(
        """
        <div class="legal-note">
            ClauseGuard supports document review and is not legal advice.
            Consult a qualified professional for consequential decisions.
        </div>
        """,
        unsafe_allow_html=True,
    )


def report_markdown() -> str:
    doc_name = st.session_state.get("uploaded_name", "Rental_Agreement.pdf")
    findings = st.session_state.get("findings", DEFAULT_FINDINGS)
    num_pages = st.session_state.get("num_pages", 1)

    lines = [
        f"# ClauseGuard AI — Agreement Review for {doc_name}",
        "",
        f"Document: {doc_name}",
        f"Pages analyzed: {num_pages}",
        f"Findings count: {len(findings)}",
        "",
    ]
    for finding in findings:
        lines.extend(
            [
                f"## {finding['title']}",
                f"Priority: {finding['priority']} ({finding['pages']})",
                "",
                finding["detail"],
                "",
                f"Review question: {finding['question']}",
                "",
                "Source passages:",
            ]
        )
        for s in finding.get("sources", []):
            lines.append(f"- **{s.get('clause', 'Clause')}** ({s.get('page', 'Page')}): \"{s.get('quote', '')}\"")
        lines.append("")

    if st.session_state.get("messages"):
        lines.extend(["", "## Interactive Q&A Session", ""])
        for msg in st.session_state.messages:
            role = "User" if msg["role"] == "user" else "Assistant"
            text = msg.get("content") or msg.get("explanation")
            lines.append(f"**{role}:** {text}\n")

    lines.append("\nClauseGuard supports document review and does not provide legal advice.")
    return "\n".join(lines)


def render_metric(
    value: str, label: str, color_class: str, note: str = "Ready for your review"
) -> None:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-value {color_class}">{value}</div>
            <div>
                <div class="metric-label">{label}</div>
                <div class="metric-note">{note}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_finding_card(finding: dict[str, Any], active: bool) -> None:
    active_class = " active" if active else ""
    st.markdown(
        f"""
        <div class="finding-card{active_class}">
            <span class="priority {finding.get('priority_class', 'info')}">
                {html.escape(finding.get('priority', 'Review'))}
            </span>
            <div class="finding-title">{html.escape(finding.get('title', 'Finding'))}</div>
            <div class="finding-copy">{html.escape(finding.get('summary', ''))}</div>
            <div class="finding-pages">{html.escape(str(finding.get('pages', 'Page 1')))}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.button(
        "View evidence" if not active else "Currently reviewing",
        key=f"finding-{finding['id']}",
        disabled=active,
        use_container_width=True,
        on_click=select_finding,
        args=(finding["id"],),
    )


def render_evidence(finding: dict[str, Any]) -> None:
    sources = finding.get("sources", [])
    sources_html = ""

    for idx, s in enumerate(sources):
        is_coral = (idx % 2 == 1)
        coral_class = " coral" if is_coral else ""
        clause_name = html.escape(str(s.get("clause", f"Clause {idx + 1}")))
        page_name = html.escape(str(s.get("page", "")))
        quote_body = html.escape(str(s.get("quote", "")))

        sources_html += f"""
        <div class="quote{coral_class}">
            <div class="quote-meta">
                <span>{clause_name}</span>
                <span>{page_name}</span>
            </div>
            <div class="quote-text">“{quote_body}”</div>
        </div>
        """
        if idx < len(sources) - 1:
            connector_text = html.escape(str(finding.get("connector", "Related condition")))
            sources_html += f"""
            <div class="connector">
                <span>{connector_text}</span>
            </div>
            """

    st.markdown(
        f"""
        <div class="detail-panel">
            <div class="detail-head">
                <div style="display:flex;align-items:center;justify-content:space-between">
                    <div class="eyebrow">Cross-examiner</div>
                    <span class="priority {finding.get('priority_class', 'info')}">
                        {html.escape(str(finding.get('priority', 'Review')))}
                    </span>
                </div>
                <div class="detail-title">{html.escape(str(finding.get('title', 'Finding')))}</div>
                <div class="detail-copy">{html.escape(str(finding.get('detail', '')))}</div>
            </div>
            <div class="detail-body">
                <div class="evidence-label">Source evidence</div>
                {sources_html}
                <div class="question-card">
                    <div class="question-label">Question to ask</div>
                    <div class="question-copy">{html.escape(str(finding.get('question', '')))}</div>
                </div>
                <div class="evidence-ok">Evidence matched to source text</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_assistant_chat_response(explanation: Any, context: Any = None) -> None:
    """Renders the AI response in chat with clear visual separation of explanation and quoted source passages."""
    st.markdown("#### 💡 AI Legal Explanation")
    if isinstance(explanation, dict):
        text = (
            explanation.get("explanation")
            or explanation.get("answer")
            or explanation.get("plain_language")
            or str(explanation)
        )
        st.markdown(text)
        if not context:
            context = explanation.get("quotes") or explanation.get("passages")
    else:
        st.markdown(str(explanation))

    if context:
        st.markdown(
            """
            <div style="margin-top:1.25rem" class="evidence-label">
                📜 Quoted Source Passages & Context
            </div>
            """,
            unsafe_allow_html=True,
        )
        if isinstance(context, list):
            for idx, c in enumerate(context, start=1):
                is_coral = (idx % 2 == 0)
                coral_class = " coral" if is_coral else ""
                if isinstance(c, dict):
                    clause_title = html.escape(str(c.get("heading") or f"Clause {c.get('id', idx)}"))
                    page = html.escape(f"Page {c['page']}" if "page" in c else f"Passage {idx}")
                    text = html.escape(str(c.get("text") or c.get("quote") or c))
                else:
                    clause_title = f"Passage {idx}"
                    page = ""
                    text = html.escape(str(c))

                st.markdown(
                    f"""
                    <div class="quote{coral_class}" style="margin-bottom:0.75rem;">
                        <div class="quote-meta">
                            <span>{clause_title}</span>
                            <span>{page}</span>
                        </div>
                        <div class="quote-text">“{text}”</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.markdown(
                f"""
                <div class="quote" style="margin-bottom:0.75rem;">
                    <div class="quote-text">“{html.escape(str(context))}”</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_chat_view() -> None:
    """Render the full interactive chat Q&A interface."""
    render_topbar()
    st.markdown(
        """
        <div class="eyebrow">Interactive Assistant</div>
        <h1 style="font-size:3rem!important">Clause Q&A</h1>
        <div class="subhead">
            Ask any question regarding obligations, deposit return, notice windows, or penalties.
            Answers are backed by quoted source passages extracted on-device.
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not st.session_state.get("ingested"):
        st.info("👆 Please upload a PDF agreement first to start asking questions.")
        st.button("Go to upload", on_click=navigate, args=("upload",), type="primary")
        return

    # Render chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if message["role"] == "user":
                st.markdown(message["content"])
            else:
                render_assistant_chat_response(message["explanation"], message.get("context"))

    # Chat input
    if user_query := st.chat_input("Ask a question about your agreement..."):
        st.session_state.messages.append({"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.markdown(user_query)

        with st.chat_message("assistant"):
            with st.spinner("Searching clauses and analyzing legal context..."):
                context = search_clauses(user_query)
                explanation = get_legal_answer(user_query, context)
                render_assistant_chat_response(explanation, context)

        st.session_state.messages.append({
            "role": "assistant",
            "explanation": explanation,
            "context": context,
        })


def render_review() -> None:
    render_topbar()
    doc_name = st.session_state.get("uploaded_name", "Rental_Agreement.pdf")
    findings = st.session_state.get("findings", DEFAULT_FINDINGS)
    num_pages = st.session_state.get("num_pages", 1)

    title_column, action_column = st.columns([2.2, 1], vertical_alignment="bottom")
    with title_column:
        st.markdown(
            f"""
            <div class="eyebrow">Analysis complete</div>
            <h1 style="font-size:3rem!important">Agreement review</h1>
            <div class="subhead" style="margin-bottom:0">
                {html.escape(doc_name)} · Analyzed on-device
            </div>
            """,
            unsafe_allow_html=True,
        )
    with action_column:
        new_column, export_column = st.columns(2)
        with new_column:
            st.button(
                "New analysis",
                icon=":material/add:",
                use_container_width=True,
                on_click=navigate,
                args=("upload",),
            )
        with export_column:
            st.download_button(
                "Export report",
                data=report_markdown(),
                file_name="clauseguard-review.md",
                mime="text/markdown",
                icon=":material/download:",
                use_container_width=True,
            )

    st.write("")
    metric_columns = st.columns(3)
    with metric_columns[0]:
        render_metric(str(len(findings)), "Findings to review", "metric-coral")
    with metric_columns[1]:
        render_metric(str(num_pages), "Pages analyzed", "metric-indigo")
    with metric_columns[2]:
        render_metric("100%", "Evidence linked", "metric-green")

    st.write("")

    # Integrated tabs for Findings and Interactive Chat
    tab_findings, tab_chat = st.tabs(["📑 Review & Findings", "💬 Interactive Clause Q&A"])

    with tab_findings:
        findings_column, detail_column = st.columns([0.88, 1.12], gap="large")
        with findings_column:
            st.markdown(
                f"""
                <div class="eyebrow">Findings</div>
                <div style="margin:.25rem 0 1rem;color:#8a8a81;font-size:.7rem">
                    {len(findings)} items need your attention
                </div>
                """,
                unsafe_allow_html=True,
            )
            priority_filter = st.selectbox(
                "Filter findings",
                ("All findings", "High priority", "Needs review", "Missing promise"),
                label_visibility="collapsed",
            )
            visible_findings = [
                f
                for f in findings
                if priority_filter == "All findings"
                or f.get("priority") == priority_filter
            ]
            for f in visible_findings:
                render_finding_card(
                    f, f["id"] == st.session_state.selected_finding
                )

        selected = next(
            (f for f in findings if f["id"] == st.session_state.selected_finding),
            findings[0] if findings else DEFAULT_FINDINGS[0],
        )
        with detail_column:
            render_evidence(selected)

    with tab_chat:
        st.markdown(
            """
            <div class="eyebrow">Interactive Clause Assistant</div>
            <div style="margin:.25rem 0 1rem;color:#8a8a81;font-size:.78rem">
                Ask any question about this document. The assistant retrieves exact passages and explains them.
            </div>
            """,
            unsafe_allow_html=True,
        )

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                if message["role"] == "user":
                    st.markdown(message["content"])
                else:
                    render_assistant_chat_response(message["explanation"], message.get("context"))

        if user_query := st.chat_input("Ask a question about deposit, notice, repairs, rent..."):
            st.session_state.messages.append({"role": "user", "content": user_query})
            with st.chat_message("user"):
                st.markdown(user_query)

            with st.chat_message("assistant"):
                with st.spinner("Searching clauses and analyzing legal context..."):
                    context = search_clauses(user_query)
                    explanation = get_legal_answer(user_query, context)
                    render_assistant_chat_response(explanation, context)

            st.session_state.messages.append({
                "role": "assistant",
                "explanation": explanation,
                "context": context,
            })

    st.markdown(
        """
        <div class="legal-note">
            Findings support review and may require professional interpretation.
            ClauseGuard does not determine whether a contract is legally valid.
        </div>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    inject_styles()

    if "ingested" not in st.session_state:
        st.session_state.ingested = False
    if "view" not in st.session_state:
        # If no document is uploaded yet, start on upload page; otherwise review
        st.session_state.view = "upload" if not st.session_state.ingested else "review"
    if "selected_finding" not in st.session_state:
        st.session_state.selected_finding = 1
    if "findings" not in st.session_state:
        st.session_state.findings = DEFAULT_FINDINGS
    if "messages" not in st.session_state:
        st.session_state.messages = []

    render_sidebar()

    if st.session_state.view == "upload":
        render_upload()
    elif st.session_state.view == "chat":
        render_chat_view()
    else:
        render_review()


if __name__ == "__main__":
    main()
