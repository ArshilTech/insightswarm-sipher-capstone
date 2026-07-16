import re
from datetime import datetime
from pathlib import Path

import streamlit as st

st.set_page_config(
    page_title="InsightSwarm | Agents Tracker",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="collapsed",
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
LOG_DIR = PROJECT_ROOT / "logs"
LOG_FILES = {
    "Application log (app.log)": LOG_DIR / "app.log",
    "Error log (errors.log)": LOG_DIR / "errors.log",
}
LOG_PATTERN = re.compile(
    r"^(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) "
    r"\[(?P<level>\w+)\] (?P<logger>[^\[]+) "
    r"\[run_id: (?P<run_id>[^\]]+)\] - (?P<message>.*)$"
)
MAX_LINES = 400

# ---------- Styling (matches streamlit-app.py) ----------
st.markdown(
    """
    <style>
        .stApp {
            background: linear-gradient(135deg, #E7F6F1 0%, #DDF1EA 45%, #D3EDE3 100%);
            color: #1F2937;
        }

        [data-testid="stSidebar"] {
            display: none;
        }

        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 2rem;
            max-width: 1200px;
        }

        .hero {
            text-align: center;
            padding: 1rem 1rem 0.5rem 1rem;
            margin-bottom: 0.5rem;
        }

        .hero h1 {
            font-size: 2.5rem;
            line-height: 1.1;
            margin-bottom: 0.35rem;
            color: #0F2A22;
            font-weight: 800;
            letter-spacing: -0.03em;
        }

        .hero p {
            max-width: 760px;
            margin: 0 auto;
            color: #4B5D57;
            font-size: 1rem;
            line-height: 1.7;
        }

        .eyebrow {
            display: inline-block;
            padding: 0.4rem 0.8rem;
            border-radius: 999px;
            background: rgba(15, 118, 110, 0.12);
            border: 1px solid rgba(15, 118, 110, 0.28);
            color: #0F766E;
            font-weight: 700;
            font-size: 0.82rem;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            margin-bottom: 0.75rem;
        }

        .metric-card {
            background: rgba(255, 255, 255, 0.75);
            border: 1px solid rgba(15, 118, 110, 0.15);
            border-radius: 20px;
            padding: 0.9rem 1rem;
            box-shadow: 0 18px 45px rgba(15, 60, 50, 0.10);
            backdrop-filter: blur(14px);
        }

        .metric-label {
            color: #6B7C77;
            font-size: 0.84rem;
            margin-bottom: 0.2rem;
        }

        .metric-value {
            color: #0F2A22;
            font-size: 1.35rem;
            font-weight: 800;
            line-height: 1.1;
        }

        .log-shell {
            background: rgba(255, 255, 255, 0.80);
            border: 1px solid rgba(15, 118, 110, 0.15);
            border-radius: 24px;
            padding: 1rem 1.1rem 1.1rem 1.1rem;
            box-shadow: 0 20px 55px rgba(15, 60, 50, 0.12);
            backdrop-filter: blur(16px);
        }

        .log-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 0.75rem;
            margin-bottom: 0.75rem;
            flex-wrap: wrap;
        }

        .log-title {
            color: #0F2A22;
            font-size: 1.05rem;
            font-weight: 800;
        }

        .live-pill {
            display: inline-flex;
            align-items: center;
            gap: 0.45rem;
            padding: 0.28rem 0.65rem;
            border-radius: 999px;
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 0.04em;
            text-transform: uppercase;
        }

        .live-pill.on {
            background: rgba(15, 118, 110, 0.14);
            color: #0F766E;
            border: 1px solid rgba(15, 118, 110, 0.28);
        }

        .live-pill.off {
            background: rgba(15, 42, 34, 0.06);
            color: #5B6E68;
            border: 1px solid rgba(15, 42, 34, 0.12);
        }

        .live-dot {
            width: 0.55rem;
            height: 0.55rem;
            border-radius: 50%;
            background: #14B8A6;
            box-shadow: 0 0 0 rgba(20, 184, 166, 0.4);
        }

        .live-dot.on {
            animation: pulse-dot 1.6s ease-in-out infinite;
        }

        .live-dot.off {
            background: #94A3B8;
            box-shadow: none;
        }

        @keyframes pulse-dot {
            0%, 100% { box-shadow: 0 0 0 0 rgba(20, 184, 166, 0.45); }
            50% { box-shadow: 0 0 0 8px rgba(20, 184, 166, 0); }
        }

        .log-panel {
            background: linear-gradient(180deg, rgba(248, 252, 251, 0.95), rgba(241, 249, 246, 0.98));
            border: 1px solid rgba(15, 118, 110, 0.18);
            border-radius: 18px;
            padding: 0.85rem 0.95rem;
            max-height: 520px;
            overflow-y: auto;
            font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
            font-size: 0.82rem;
            line-height: 1.55;
        }

        .log-line {
            padding: 0.18rem 0.35rem;
            border-radius: 8px;
            margin-bottom: 0.15rem;
            word-break: break-word;
        }

        .log-line:hover {
            background: rgba(15, 118, 110, 0.06);
        }

        .log-level {
            font-weight: 800;
            letter-spacing: 0.03em;
        }
        .log-level.info { color: #0F766E; }
        .log-level.debug { color: #64748B; }
        .log-level.warning { color: #B45309; }
        .log-level.error, .log-level.critical { color: #DC2626; }

        .empty-state {
            text-align: center;
            padding: 2.5rem 1rem;
            line-height: 1.7;
        }

        .divider {
            height: 1px;
            background: linear-gradient(90deg, transparent, rgba(15, 118, 110, 0.28), transparent);
            margin: 1rem 0;
        }

        div.stButton > button {
            border-radius: 14px;
            border: 1px solid rgba(15, 118, 110, 0.35);
            background: linear-gradient(135deg, #14B8A6 0%, #0F766E 100%);
            color: white;
            padding: 0.65rem 1rem;
            font-weight: 700;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
            box-shadow: 0 10px 25px rgba(15, 118, 110, 0.25);
        }

        div.stButton > button:hover {
            transform: translateY(-1px);
            box-shadow: 0 14px 30px rgba(15, 118, 110, 0.35);
            border-color: rgba(15, 118, 110, 0.55);
        }

        .back-button button {
            background: rgba(255, 255, 255, 0.85) !important;
            color: #0F766E !important;
            border: 1px solid rgba(15, 118, 110, 0.28) !important;
            box-shadow: none !important;
        }

        .small-chip {
            display: inline-block;
            margin-right: 0.35rem;
            padding: 0.15rem 0.45rem;
            border-radius: 999px;
            background: rgba(15, 118, 110, 0.10);
            color: #0F766E;
            font-size: 0.75rem;
            border: 1px solid rgba(15, 118, 110, 0.22);
        }

        /* Streamlit widgets — dark readable text on light theme */
        [data-testid="stAppViewContainer"],
        [data-testid="stAppViewContainer"] p,
        [data-testid="stAppViewContainer"] span,
        [data-testid="stAppViewContainer"] label {
            color: #1F2937;
        }

        [data-testid="stWidgetLabel"] p,
        [data-testid="stWidgetLabel"] label,
        [data-testid="stWidgetLabel"] span {
            color: #0F2A22 !important;
            font-weight: 600 !important;
        }

        div[data-testid="stTextInput"] input {
            color: #1F2937 !important;
            -webkit-text-fill-color: #1F2937 !important;
            caret-color: #0F766E !important;
            background: rgba(255, 255, 255, 0.92) !important;
            border: 1px solid rgba(15, 118, 110, 0.28) !important;
            border-radius: 12px !important;
        }

        div[data-testid="stTextInput"] input::placeholder {
            color: #64748B !important;
            opacity: 1 !important;
        }

        div[data-testid="stTextInput"] input:focus {
            border-color: #0F766E !important;
            box-shadow: 0 0 0 2px rgba(15, 118, 110, 0.18) !important;
        }

        div[data-testid="stSelectbox"] [data-baseweb="select"] > div,
        div[data-testid="stSelectbox"] [data-baseweb="select"] span {
            color: #1F2937 !important;
            background: rgba(255, 255, 255, 0.92) !important;
            border-color: rgba(15, 118, 110, 0.28) !important;
        }

        div[data-testid="stSelectbox"] [data-baseweb="select"] svg {
            fill: #0F766E !important;
        }

        div[data-testid="stSelectbox"] [data-baseweb="select"] > div {
            border-radius: 12px !important;
        }

        div[data-testid="stToggle"] label span,
        div[data-testid="stToggle"] label p {
            color: #334155 !important;
            font-weight: 500 !important;
        }

        div[data-testid="stToggle"] [data-testid="stMarkdownContainer"] p {
            color: #334155 !important;
        }

        [data-baseweb="popover"] [role="listbox"] li,
        [data-baseweb="popover"] [role="option"] {
            color: #1F2937 !important;
            background: #FFFFFF !important;
        }

        [data-baseweb="popover"] [role="option"]:hover,
        [data-baseweb="popover"] [role="option"][aria-selected="true"] {
            color: #0F766E !important;
            background: rgba(15, 118, 110, 0.10) !important;
        }

        /* Log line contrast — slightly richer tones */
        .log-time { color: #4B5D57; }
        .log-logger { color: #334155; font-weight: 500; }
        .log-run-id {
            color: #0D5C56;
            background: rgba(15, 118, 110, 0.14);
            border: 1px solid rgba(15, 118, 110, 0.28);
            border-radius: 999px;
            padding: 0.05rem 0.4rem;
            font-size: 0.74rem;
            font-weight: 600;
        }
        .log-message { color: #0F2A22; font-weight: 500; }
        .empty-state { color: #4B5D57; }
    </style>
    """,
    unsafe_allow_html=True,
)


def tail_lines(path: Path, max_lines: int = MAX_LINES) -> list[str]:
    if not path.exists():
        return []

    with path.open("r", encoding="utf-8", errors="replace") as handle:
        lines = handle.readlines()

    if len(lines) <= max_lines:
        return [line.rstrip("\n") for line in lines]
    return [line.rstrip("\n") for line in lines[-max_lines:]]


def parse_log_line(line: str) -> dict | None:
    match = LOG_PATTERN.match(line.strip())
    if not match:
        return None
    return match.groupdict()


def level_class(level: str) -> str:
    return level.lower() if level else "info"


def render_log_line(entry: dict | None, raw_line: str) -> str:
    if not entry:
        escaped = raw_line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        return f'<div class="log-line"><span class="log-message">{escaped}</span></div>'

    timestamp = entry["timestamp"]
    level = entry["level"]
    logger = entry["logger"].strip()
    run_id = entry["run_id"]
    message = (
        entry["message"]
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )

    return (
        f'<div class="log-line">'
        f'<span class="log-time">{timestamp}</span> '
        f'<span class="log-level {level_class(level)}">[{level}]</span> '
        f'<span class="log-logger">{logger}</span> '
        f'<span class="log-run-id">{run_id}</span> '
        f'<span class="log-message">- {message}</span>'
        f"</div>"
    )


def filter_entries(
    lines: list[str],
    level_filter: str,
    run_id_filter: str,
    search_text: str,
) -> list[tuple[dict | None, str]]:
    filtered: list[tuple[dict | None, str]] = []
    run_id_filter = run_id_filter.strip().lower()
    search_text = search_text.strip().lower()

    for line in lines:
        if not line.strip():
            continue

        entry = parse_log_line(line)
        if entry:
            if level_filter != "All" and entry["level"] != level_filter:
                continue
            if run_id_filter and run_id_filter not in entry["run_id"].lower():
                continue
            if search_text and search_text not in line.lower():
                continue
        elif search_text and search_text not in line.lower():
            continue

        filtered.append((entry, line))

    return filtered


def count_levels(entries: list[tuple[dict | None, str]]) -> dict[str, int]:
    counts = {"INFO": 0, "WARNING": 0, "ERROR": 0, "DEBUG": 0}
    for entry, _ in entries:
        if entry and entry["level"] in counts:
            counts[entry["level"]] += 1
    return counts


def render_log_panel(
    log_path: Path,
    level_filter: str,
    run_id_filter: str,
    search_text: str,
    live_mode: bool,
) -> None:
    lines = tail_lines(log_path)
    entries = filter_entries(lines, level_filter, run_id_filter, search_text)
    counts = count_levels(entries)
    live_class = "on" if live_mode else "off"
    live_label = "Live" if live_mode else "Paused"
    updated_at = datetime.now().strftime("%H:%M:%S")

    st.markdown(
        f"""
        <div class="log-shell">
            <div class="log-header">
                <div class="log-title">Agent activity log stream</div>
                <div class="live-pill {live_class}">
                    <span class="live-dot {live_class}"></span>
                    {live_label} · updated {updated_at}
                </div>
            </div>
        """,
        unsafe_allow_html=True,
    )

    if not log_path.exists():
        st.markdown(
            """
            <div class="log-panel">
                <div class="empty-state">
                    No log file found yet.<br/>
                    Start the FastAPI backend and run a research job — logs will appear here in real time.
                </div>
            </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    if not entries:
        st.markdown(
            """
            <div class="log-panel">
                <div class="empty-state">
                    No log entries match the current filters.<br/>
                    Try clearing filters or choose a different log file.
                </div>
            </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    rendered = "".join(render_log_line(entry, raw) for entry, raw in entries)
    st.markdown(
        f"""
            <div class="log-panel">{rendered}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Visible lines</div>
                <div class="metric-value">{len(entries)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with m2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Info</div>
                <div class="metric-value">{counts["INFO"]}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with m3:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Warnings</div>
                <div class="metric-value">{counts["WARNING"]}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with m4:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Errors</div>
                <div class="metric-value">{counts["ERROR"]}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ---------- Header ----------
back_col, _ = st.columns([1, 5])
with back_col:
    st.markdown("<div class='back-button'>", unsafe_allow_html=True)
    if st.button("← Back to Dashboard", use_container_width=True, key="back_dashboard"):
        st.switch_page("streamlit-app.py")
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown(
    """
    <div class="hero">
        <div class="eyebrow">Developer control center</div>
        <h1>Agents Tracker</h1>
        <p>
            Monitor backend agent activity in real time. Tail application logs, filter by run ID or level,
            and watch new entries stream in while research jobs are running.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div style="text-align:center;margin-bottom:0.75rem;">
        <span class="small-chip">Real-time tail</span>
        <span class="small-chip">Run ID filter</span>
        <span class="small-chip">Level filter</span>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

# ---------- Controls ----------
control_left, control_right = st.columns([1.2, 1])
with control_left:
    selected_log = st.selectbox(
        "Log source",
        options=list(LOG_FILES.keys()),
        key="log_source",
    )
    live_mode = st.toggle("Live tail (auto-refresh every 2s)", value=True, key="live_tail")

with control_right:
    level_filter = st.selectbox(
        "Log level",
        options=["All", "DEBUG", "INFO", "WARNING", "ERROR"],
        index=0,
        key="level_filter",
    )
    run_id_filter = st.text_input(
        "Filter by run ID",
        placeholder="e.g. abc123 or leave blank for all",
        key="run_id_filter",
    )
    search_text = st.text_input(
        "Search message",
        placeholder="Search log text...",
        key="search_text",
    )

log_path = LOG_FILES[selected_log]

if live_mode:
    @st.fragment(run_every=2)
    def live_log_view() -> None:
        render_log_panel(
            log_path=log_path,
            level_filter=level_filter,
            run_id_filter=run_id_filter,
            search_text=search_text,
            live_mode=True,
        )

    live_log_view()
else:
    refresh_col, _ = st.columns([1, 4])
    with refresh_col:
        if st.button("Refresh now", use_container_width=True, key="manual_refresh"):
            st.rerun()

    render_log_panel(
        log_path=log_path,
        level_filter=level_filter,
        run_id_filter=run_id_filter,
        search_text=search_text,
        live_mode=False,
    )
