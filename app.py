import re

import streamlit as st

from src.pipelines.pipeline import run_pipeline

st.set_page_config(page_title="Multi-Agent Research Assistant", page_icon="🔎", layout="wide")

# ---------- Styling ----------
st.markdown(
    """
    <style>
    .block-container {padding-top: 2rem; max-width: 1100px;}
    .hero {
        padding: 1.8rem 2rem;
        border-radius: 16px;
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 50%, #db2777 100%);
        color: white;
        margin-bottom: 1.5rem;
    }
    .hero h1 {margin: 0; font-size: 2.1rem; color: white;}
    .hero p {margin: 0.4rem 0 0 0; opacity: 0.92; font-size: 1.05rem;}
    .pipeline {display: flex; gap: 0.5rem; flex-wrap: wrap; margin-top: 1rem;}
    .pill {
        background: rgba(255,255,255,0.18);
        padding: 0.3rem 0.8rem;
        border-radius: 999px;
        font-size: 0.85rem;
        font-weight: 500;
    }
    .badge {
        display: inline-block;
        padding: 0.35rem 0.9rem;
        border-radius: 999px;
        font-weight: 600;
        font-size: 0.95rem;
    }
    .badge-ok {background: #dcfce7; color: #166534;}
    .badge-warn {background: #fef3c7; color: #92400e;}
    .badge-na {background: #e5e7eb; color: #374151;}
    div[data-testid="stTabs"] button {font-size: 1rem; font-weight: 500;}
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- Sidebar ----------
with st.sidebar:
    st.header("How it works")
    st.markdown(
        """
        1. **🔍 Search agent** finds sources on the web
        2. **📖 Reader agent** scrapes and summarizes them
        3. **✍️ Writer** turns the notes into a report
        4. **🧐 Critic** reviews the report
        """
    )
    st.divider()
    st.caption("Tip: a full run can take a minute or more, since several LLM and web calls happen in a row.")

# ---------- Hero ----------
st.markdown(
    """
    <div class="hero">
        <h1>🔎 Multi-Agent Research Assistant</h1>
        <p>Give it a topic and a team of AI agents will research, write and review a report for you.</p>
        <div class="pipeline">
            <span class="pill">🔍 Search</span>
            <span class="pill">📖 Read</span>
            <span class="pill">✍️ Write</span>
            <span class="pill">🧐 Critique</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------- Input ----------
EXAMPLES = [
    "Latest developments in AI agents",
    "How do vector databases work?",
    "Impact of quantum computing on cryptography",
]


def set_topic(value: str):
    st.session_state["topic_input"] = value


topic = st.text_input(
    "Research topic",
    key="topic_input",
    placeholder="e.g. latest developments in AI agents",
)

st.caption("Or try an example:")
example_cols = st.columns(len(EXAMPLES))
for col, example in zip(example_cols, EXAMPLES):
    col.button(example, on_click=set_topic, args=(example,), use_container_width=True)

run = st.button("🚀 Run research", type="primary", disabled=not topic.strip())

# ---------- Run ----------
if run:
    try:
        with st.status("Running the research pipeline...", expanded=True) as status:
            result = run_pipeline(topic.strip(), on_step=lambda msg: st.write(msg))
            status.update(label="Pipeline complete", state="complete", expanded=False)
        st.session_state["result"] = result
    except Exception as e:
        st.session_state.pop("result", None)
        st.error(f"Pipeline failed: {e}")

# ---------- Results ----------
result = st.session_state.get("result")
if result:
    st.divider()
    st.subheader(f"Results for: {result['topic']}")

    review_text = result["review"]
    upper = review_text.upper()
    if "NEEDS REVISION" in upper:
        verdict, badge_class = "⚠️ Needs revision", "badge-warn"
    elif "APPROVED" in upper:
        verdict, badge_class = "✅ Approved", "badge-ok"
    else:
        verdict, badge_class = "Review complete", "badge-na"

    score_match = re.search(r"Score\D{0,10}(\d+(?:\.\d+)?)", review_text, re.IGNORECASE)
    score = f"{score_match.group(1)}/10" if score_match else "N/A"

    m1, m2, m3 = st.columns(3)
    m1.markdown(f'<span class="badge {badge_class}">{verdict}</span>', unsafe_allow_html=True)
    m2.metric("Critic score", score)
    m3.metric("Report length", f"{len(result['report'].split())} words")

    report_tab, review_tab, research_tab, search_tab = st.tabs(
        ["📄 Report", "🧐 Critic Review", "📚 Research Notes", "🌐 Search Results"]
    )

    with report_tab:
        with st.container(border=True):
            st.markdown(result["report"])
        st.download_button(
            "⬇️ Download report (.md)",
            data=result["report"],
            file_name="research_report.md",
            mime="text/markdown",
        )

    with review_tab:
        with st.container(border=True):
            st.markdown(result["review"])

    with research_tab:
        with st.container(border=True):
            st.markdown(result["research"])

    with search_tab:
        with st.container(border=True):
            st.markdown(result["search_results"])
