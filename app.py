import os
import sys
import time
from pathlib import Path

# Automatically include .venv site-packages if run with global Python
_venv_site = Path(__file__).resolve().parent / ".venv" / "Lib" / "site-packages"
if _venv_site.exists() and str(_venv_site) not in sys.path:
    sys.path.insert(0, str(_venv_site))

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="Research Studio",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="collapsed",
)

try:
    from agents import (
        build_reader_agent,
        build_search_agent,
        critic_chain,
        writer_chain,
    )
    from pipeline import _extract_content
    agents_ready = True
    agents_error = None
except Exception as _err:
    agents_ready = False
    agents_error = str(_err)


# --------------------------------------------------------------------------- #
# Professional Design System & Styling
# Strict compliance: Zero purple gradients, zero emojis, zero fake gimmicks.
# --------------------------------------------------------------------------- #
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

:root {
  --bg-canvas: #0d1117;
  --bg-surface: #161b22;
  --bg-subtle: #21262d;
  --border-default: #30363d;
  --border-subtle: #21262d;
  --text-primary: #f0f6fc;
  --text-secondary: #8b949e;
  --text-muted: #6e7681;
  --brand-blue: #1f6feb;
  --brand-blue-hover: #388bfd;
  --brand-blue-active: #1158c7;
  --status-success: #238636;
  --status-success-text: #3fb950;
  --status-active-text: #58a6ff;
  --status-error-text: #f85149;
}

html, body, [class*="css"], .stApp {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  color: var(--text-primary);
  background-color: var(--bg-canvas);
}

/* Base layout constraints */
header[data-testid="stHeader"], footer, #MainMenu, [data-testid="stToolbar"] {
  display: none !important;
}

.block-container {
  max-width: 1040px;
  padding-top: 2rem;
  padding-bottom: 4rem;
  margin: 0 auto;
}

/* Header & Brand Identity */
.header-wrapper {
  margin-bottom: 1.75rem;
}

.header-badge {
  display: inline-block;
  font-size: 11px;
  font-weight: 600;
  color: var(--text-secondary);
  border: 1px solid var(--border-default);
  background: var(--bg-surface);
  border-radius: 4px;
  padding: 3px 8px;
  margin-bottom: 8px;
}

.header-title {
  font-size: 26px;
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: -0.02em;
  margin: 0 0 6px 0;
  line-height: 1.25;
}

.header-desc {
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.55;
  margin: 0;
  max-width: 680px;
}

/* Card Containers */
[data-testid="stVerticalBlockBorderWrapper"] {
  background: var(--bg-surface) !important;
  border: 1px solid var(--border-default) !important;
  border-radius: 8px !important;
  padding: 1.15rem 1.35rem !important;
  box-shadow: none !important;
  margin-bottom: 1rem !important;
}

.field-label {
  display: block;
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.field-caption {
  font-size: 12px;
  color: var(--text-secondary);
  margin-bottom: 10px;
}

/* Text Inputs */
.stTextInput input {
  background-color: var(--bg-canvas) !important;
  color: var(--text-primary) !important;
  border: 1px solid var(--border-default) !important;
  border-radius: 6px !important;
  padding: 0.65rem 0.85rem !important;
  font-size: 14px !important;
  transition: border-color 0.15s ease, box-shadow 0.15s ease !important;
}

.stTextInput input:focus {
  border-color: var(--brand-blue-hover) !important;
  box-shadow: 0 0 0 3px rgba(31, 111, 235, 0.25) !important;
  outline: none !important;
}

.stTextInput input::placeholder {
  color: var(--text-muted) !important;
}

.stTextInput label {
  display: none !important;
}

[data-testid="InputInstructions"] {
  display: none !important;
}

/* Single Primary CTA Button (Submit) */
[data-testid="stFormSubmitButton"] > button, button[kind="primary"] {
  background: var(--brand-blue) !important;
  color: #ffffff !important;
  border: 1px solid var(--brand-blue) !important;
  border-radius: 6px !important;
  font-size: 13px !important;
  font-weight: 600 !important;
  padding: 0.65rem 1.25rem !important;
  height: auto !important;
  transition: background-color 0.15s ease, border-color 0.15s ease !important;
  box-shadow: none !important;
}

[data-testid="stFormSubmitButton"] > button:hover, button[kind="primary"]:hover {
  background: var(--brand-blue-hover) !important;
  border-color: var(--brand-blue-hover) !important;
  color: #ffffff !important;
}

[data-testid="stFormSubmitButton"] > button:active, button[kind="primary"]:active {
  background: var(--brand-blue-active) !important;
  border-color: var(--brand-blue-active) !important;
}

/* Secondary Action Buttons (Sample queries, downloads) */
.stButton > button, button[kind="secondary"] {
  background: var(--bg-canvas) !important;
  color: var(--text-secondary) !important;
  border: 1px solid var(--border-default) !important;
  border-radius: 6px !important;
  font-size: 12px !important;
  font-weight: 500 !important;
  padding: 0.45rem 0.75rem !important;
  height: auto !important;
  box-shadow: none !important;
  transition: background-color 0.15s ease, color 0.15s ease, border-color 0.15s ease !important;
}

.stButton > button:hover, button[kind="secondary"]:hover {
  background: var(--bg-subtle) !important;
  border-color: var(--text-muted) !important;
  color: var(--text-primary) !important;
}

.stDownloadButton > button {
  background: var(--bg-subtle) !important;
  color: var(--text-primary) !important;
  border: 1px solid var(--border-default) !important;
  border-radius: 6px !important;
  font-size: 13px !important;
  font-weight: 500 !important;
  padding: 0.5rem 1rem !important;
  box-shadow: none !important;
  transition: background-color 0.15s ease !important;
}

.stDownloadButton > button:hover {
  background: #28303a !important;
  border-color: #3f4752 !important;
  color: var(--text-primary) !important;
}

/* Sample Topics Bar */
.sample-bar-heading {
  font-size: 11px;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.04em;
  margin-top: 14px;
  margin-bottom: 6px;
}

/* Pipeline Stepper */
.section-heading {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-secondary);
  margin: 1.5rem 0 0.75rem 0;
}

.stepper-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  margin-bottom: 1.5rem;
}

.step-card {
  background: var(--bg-surface);
  border: 1px solid var(--border-default);
  border-radius: 8px;
  padding: 14px 16px;
  position: relative;
  transition: border-color 0.2s ease, background-color 0.2s ease;
}

.step-card.pending {
  border-color: var(--border-default);
}

.step-card.active {
  border-color: var(--brand-blue);
  background-color: #0d1726;
}

.step-card.done {
  border-color: var(--status-success);
  background-color: #0e1e17;
}

.step-card.error {
  border-color: #da3633;
  background-color: #1e1315;
}

.step-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

.step-num {
  font-size: 11px;
  font-weight: 600;
  color: var(--text-muted);
}

.step-badge {
  font-size: 11px;
  font-weight: 500;
  border-radius: 4px;
  padding: 2px 6px;
}

.step-badge.pending {
  color: var(--text-muted);
  background: var(--bg-subtle);
}

.step-badge.active {
  color: var(--status-active-text);
  background: rgba(31, 111, 235, 0.15);
}

.step-badge.done {
  color: var(--status-success-text);
  background: rgba(35, 134, 54, 0.15);
}

.step-badge.error {
  color: var(--status-error-text);
  background: rgba(218, 54, 51, 0.15);
}

.step-title-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.step-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: var(--text-secondary);
}

.step-card.active .step-icon {
  color: var(--status-active-text);
}

.step-card.done .step-icon {
  color: var(--status-success-text);
}

.step-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.step-desc {
  font-size: 12px;
  color: var(--text-secondary);
  line-height: 1.45;
  margin: 0;
}

@media (max-width: 860px) {
  .stepper-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 500px) {
  .stepper-grid {
    grid-template-columns: 1fr;
  }
}

/* Metrics Row */
.metrics-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  margin: 1.25rem 0;
}

.metric-item {
  background: var(--bg-surface);
  border: 1px solid var(--border-default);
  border-radius: 8px;
  padding: 12px 16px;
}

.metric-val {
  font-size: 20px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 2px;
}

.metric-lbl {
  font-size: 12px;
  color: var(--text-secondary);
}

@media (max-width: 768px) {
  .metrics-row {
    grid-template-columns: repeat(2, 1fr);
  }
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
  gap: 4px;
  background: var(--bg-surface);
  padding: 4px;
  border-radius: 6px;
  border: 1px solid var(--border-default);
  width: fit-content;
}

.stTabs [data-baseweb="tab"] {
  height: auto;
  padding: 6px 14px;
  border-radius: 4px;
  color: var(--text-secondary);
  background: transparent;
  font-size: 13px;
  font-weight: 500;
  border: none !important;
}

.stTabs [aria-selected="true"] {
  background: var(--bg-subtle) !important;
  color: var(--text-primary) !important;
  font-weight: 600 !important;
}

.stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] {
  display: none;
}

/* Markdown typography inside containers */
.stMarkdown p, .stMarkdown li {
  color: var(--text-primary);
  line-height: 1.65;
  font-size: 14px;
}

.stMarkdown h1 {
  font-size: 20px;
  font-weight: 700;
  color: var(--text-primary);
  margin-top: 1.25rem;
  margin-bottom: 0.5rem;
}

.stMarkdown h2 {
  font-size: 17px;
  font-weight: 600;
  color: var(--text-primary);
  margin-top: 1.25rem;
  margin-bottom: 0.5rem;
}

.stMarkdown h3 {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
  margin-top: 1rem;
  margin-bottom: 0.4rem;
}

.stMarkdown a {
  color: var(--brand-blue-hover);
  text-decoration: underline;
  text-underline-offset: 2px;
}

.stMarkdown code {
  background: var(--bg-subtle);
  border: 1px solid var(--border-default);
  border-radius: 4px;
  padding: 2px 6px;
  font-size: 13px;
  color: var(--text-primary);
}

[data-testid="stAlert"] {
  border-radius: 6px;
  border: 1px solid var(--border-default);
  background: var(--bg-surface);
}

/* Accessibility: Support Reduced Motion */
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# --------------------------------------------------------------------------- #
# Pipeline Definition
# Clean Lucide SVG icons, professional descriptions, zero emojis.
# --------------------------------------------------------------------------- #
STEPS = [
    {
        "step_num": "Stage 1",
        "name": "Web Search",
        "desc": "Scans indexed web sources for relevant research materials and citations.",
        "icon": '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>',
    },
    {
        "step_num": "Stage 2",
        "name": "Content Reader",
        "desc": "Scrapes primary source content and extracts technical context.",
        "icon": '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/></svg>',
    },
    {
        "step_num": "Stage 3",
        "name": "Report Synthesis",
        "desc": "Drafts structured findings, technical analysis, and source references.",
        "icon": '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/></svg>',
    },
    {
        "step_num": "Stage 4",
        "name": "Quality Review",
        "desc": "Evaluates factual grounding, completeness, and structural clarity.",
        "icon": '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/></svg>',
    },
]

LABEL_MAP = {
    "pending": "Pending",
    "active": "Processing",
    "done": "Completed",
    "error": "Failed",
}


def stepper_html(states, times):
    cards = []
    for i, step in enumerate(STEPS):
        s = states[i]
        label = LABEL_MAP[s]
        if s == "done" and times[i] is not None:
            label = f"{times[i]:.1f}s"

        card = (
            f'<div class="step-card {s}">'
            f'<div class="step-top">'
            f'<span class="step-num">{step["step_num"]}</span>'
            f'<span class="step-badge {s}">{label}</span>'
            f'</div>'
            f'<div class="step-title-row">'
            f'<span class="step-icon">{step["icon"]}</span>'
            f'<span class="step-title">{step["name"]}</span>'
            f'</div>'
            f'<p class="step-desc">{step["desc"]}</p>'
            f'</div>'
        )
        cards.append(card)
    return f'<div class="stepper-grid">{"".join(cards)}</div>'


def run_pipeline_live(topic: str, slot):
    """Executes four sequential research agents and updates live progress in slot."""
    states = ["pending"] * 4
    times = [None] * 4
    state = {}

    def render():
        slot.markdown(stepper_html(states, times), unsafe_allow_html=True)

    def begin(i):
        states[i] = "active"
        render()
        return time.time()

    def finish(i, t0):
        states[i] = "done"
        times[i] = time.time() - t0
        render()

    render()
    current = 0
    try:
        # Stage 1: Search Agent
        current = 0
        t0 = begin(0)
        search_agent = build_search_agent()
        res = search_agent.invoke(
            {
                "messages": [
                    (
                        "user",
                        f"Search the web for recent, reliable information about: {topic}. "
                        "Use the web search tool and return titles, URLs, and snippets.",
                    )
                ]
            }
        )
        # Extract tool messages for raw URLs + snippets, fallback to last message
        raw_search_parts = []
        for m in res.get("messages", []):
            if getattr(m, "type", None) == "tool" or type(m).__name__ == "ToolMessage":
                raw_search_parts.append(_extract_content(m))
        search_summary = _extract_content(res["messages"][-1])
        state["search_results"] = (
            "\n---\n".join(raw_search_parts) + "\n\n### Summary\n" + search_summary
            if raw_search_parts else search_summary
        )
        finish(0, t0)

        # Stage 2: Reader Agent
        current = 1
        t0 = begin(1)
        reader_agent = build_reader_agent()
        res = reader_agent.invoke(
            {
                "messages": [
                    (
                        "user",
                        f"Research topic: {topic}\n\n"
                        f"Search results:\n{state['search_results'][:6000]}\n\n"
                        "Choose the most relevant URL from these results. "
                        "Call the scrape_url tool with that URL and summarize "
                        "the useful information retrieved. Do not invent content.",
                    )
                ]
            }
        )
        # Extract scraped tool messages + summary
        raw_scrape_parts = []
        for m in res.get("messages", []):
            if getattr(m, "type", None) == "tool" or type(m).__name__ == "ToolMessage":
                raw_scrape_parts.append(_extract_content(m))
        reader_summary = _extract_content(res["messages"][-1])
        state["scraped_content"] = (
            "\n\n".join(raw_scrape_parts) + "\n\n### Reader Summary\n" + reader_summary
            if raw_scrape_parts else reader_summary
        )
        finish(1, t0)

        # Stage 3: Writer Agent
        current = 2
        t0 = begin(2)
        research = (
            f"SEARCH RESULTS:\n{state['search_results']}\n\n"
            f"DETAILED SCRAPED CONTENT:\n{state['scraped_content']}"
        )
        state["report"] = _extract_content(
            writer_chain.invoke({"topic": topic, "research": research})
        )
        finish(2, t0)

        # Stage 4: Critic Agent
        current = 3
        t0 = begin(3)
        state["feedback"] = _extract_content(
            critic_chain.invoke({"report": state["report"]})
        )
        finish(3, t0)

    except Exception as exc:
        states[current] = "error"
        render()
        raise

    state["times"] = times
    return state


def friendly_error(e: Exception) -> str:
    t = str(e)
    if any(k in t for k in ("valid API key", "INVALID_ARGUMENT", "Incorrect API key", "invalid_api_key")):
        return (
            "Authentication failed: The configured LLM API key is invalid or unauthorized. "
            "Please check the GEMINI_API_KEY or OPENAI_API_KEY setting in the .env file."
        )
    if "tavily" in t.lower() and ("key" in t.lower() or "unauthorized" in t.lower()):
        return (
            "Web search service error: Invalid or unauthorized TAVILY_API_KEY in the .env file."
        )
    return f"Execution failed: {t}"


# --------------------------------------------------------------------------- #
# Page Content & Form
# --------------------------------------------------------------------------- #
st.markdown(
    """
<div class="header-wrapper">
  <span class="header-badge">Multi-Agent System</span>
  <h1 class="header-title">Research Studio</h1>
  <p class="header-desc">
    Coordinate autonomous search, scraping, synthesis, and review agents to investigate topics
    and generate structured, fact-grounded reports.
  </p>
</div>
""",
    unsafe_allow_html=True,
)

if not agents_ready:
    st.error(
        f"Agent initialization error: {agents_error}. "
        "Please confirm that valid API keys are configured in your .env file."
    )
    st.stop()

# Session State Initialization
if "result" not in st.session_state:
    st.session_state.result = None
if "topic" not in st.session_state:
    st.session_state.topic = ""
if "query_input" not in st.session_state:
    st.session_state.query_input = ""

# Sample topics helper with clear, concise labels
SAMPLE_TOPICS = [
    ("Solid-State Batteries", "Solid-state battery commercialization"),
    ("LLM Architecture", "Efficiency optimizations in large language models"),
    ("mRNA Therapeutics", "Recent clinical advances in mRNA therapeutics"),
    ("Geothermal Energy", "Next-generation enhanced geothermal systems"),
]

# Query Container
with st.container(border=True):
    st.markdown('<div class="field-label">Research topic or query</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="field-caption">Enter a specific technical subject, technology, or research question.</div>',
        unsafe_allow_html=True,
    )

    with st.form("research_query_form", border=False):
        c_input, c_btn = st.columns([5, 1.4], vertical_alignment="top")
        with c_input:
            topic_in = st.text_input(
                label="Topic input",
                value=st.session_state.query_input,
                placeholder="e.g. Solid-state battery commercialization",
                label_visibility="collapsed",
            )
        with c_btn:
            submit_clicked = st.form_submit_button("Run Research Pipeline", use_container_width=True)

    # Clickable Sample Suggestions (Secondary buttons that populate the field)
    st.markdown('<div class="sample-bar-heading">Suggested topics</div>', unsafe_allow_html=True)
    col_samples = st.columns(len(SAMPLE_TOPICS))
    for idx, (display_name, full_query) in enumerate(SAMPLE_TOPICS):
        with col_samples[idx]:
            if st.button(display_name, key=f"sample_{idx}", use_container_width=True):
                st.session_state.query_input = full_query
                st.rerun()

st.markdown('<div class="section-heading">Pipeline Execution Stages</div>', unsafe_allow_html=True)
stepper_slot = st.empty()

if submit_clicked:
    topic = topic_in.strip() or "Solid-state battery commercialization"
    st.session_state.topic = topic
    st.session_state.query_input = topic
    st.session_state.result = None
    try:
        st.session_state.result = run_pipeline_live(topic, stepper_slot)
    except Exception as exc:  # noqa: BLE001
        st.error(friendly_error(exc))
        import traceback
        with st.expander("Full error details (for debugging)"):
            st.code(traceback.format_exc())
elif st.session_state.result:
    stepper_slot.markdown(
        stepper_html(["done"] * 4, st.session_state.result["times"]),
        unsafe_allow_html=True,
    )
else:
    stepper_slot.markdown(stepper_html(["pending"] * 4, [None] * 4), unsafe_allow_html=True)


# Results Display
res = st.session_state.result
if res:
    words = len(res["report"].split())
    source_words = len(res.get("search_results", res.get("search_result", "")).split())
    total_time = sum(t for t in res["times"] if t) if res.get("times") else 0

    st.markdown(
        f"""
<div class="metrics-row">
  <div class="metric-item">
    <div class="metric-val">{total_time:.1f}s</div>
    <div class="metric-lbl">Total execution time</div>
  </div>
  <div class="metric-item">
    <div class="metric-val">{words:,}</div>
    <div class="metric-lbl">Report word count</div>
  </div>
  <div class="metric-item">
    <div class="metric-val">{source_words:,}</div>
    <div class="metric-lbl">Source words analyzed</div>
  </div>
  <div class="metric-item">
    <div class="metric-val">4 / 4</div>
    <div class="metric-lbl">Stages completed</div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown(
        f'<div class="section-heading">Findings for: {st.session_state.topic}</div>',
        unsafe_allow_html=True,
    )

    tab_report, tab_critic, tab_sources, tab_scraped = st.tabs(
        ["Research Report", "Quality Review", "Web Sources", "Scraped Content"]
    )

    with tab_report:
        with st.container(border=True):
            st.markdown(res["report"])
        st.write("")
        st.download_button(
            label="Download Markdown Report",
            data=res["report"],
            file_name="research_report.md",
            mime="text/markdown",
        )

    with tab_critic:
        with st.container(border=True):
            st.markdown(res["feedback"])

    with tab_sources:
        with st.container(border=True):
            st.markdown(res.get("search_results") or res.get("search_result", ""))

    with tab_scraped:
        with st.container(border=True):
            st.markdown(res["scraped_content"])