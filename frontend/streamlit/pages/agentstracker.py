import re
from datetime import datetime
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components
import time
FAVICON_PATH = Path(__file__).resolve().parent.parent / "favicon.svg"
st.set_page_config(
    page_title="InsightSwarm - Agents Tracker",
    page_icon=str(FAVICON_PATH),
    layout="wide",
    initial_sidebar_state="collapsed",
)

PROJECT_ROOT = Path(__file__).resolve().parents[3]
LOG_DIR = PROJECT_ROOT / "logs"
LOG_FILES = {
    "Application log (app.log)": LOG_DIR / "app.log",
    "Error log (errors.log)": LOG_DIR / "errors.log",
}
LOG_PATTERN = re.compile(
    r"^(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) "
    r"\[(?P<level>\w+)\] (?P<logger>[^\[]+?)\s+"
    r"\[run_id: (?P<run_id>[^\]]+)\] - (?P<message>.*)$"
)
MAX_LINES = 400

# ---------- Pipeline stage definitions ----------
# Mapped to the REAL nodes in app/graphs/research_graph.py — not the
# original Academic/Analysis/PDF-Generator lineup, which don't exist
# in the actual graph. Matching is done against the literal log
# message text those nodes already emit via get_run_logger().
STAGE_DEFS = [
    {"key": "intake", "label": "Intake Agent", "icon": "🧾", "match": ["INTAKE:"]},
    {"key": "planner", "label": "Planner Agent", "icon": "🤖", "match": ["PLANNER:"]},
    {
        "key": "researcher",
        "label": "Search Agent",
        "icon": "🔍",
        "match": ["RESEARCHER:", "Searching for:", "Error during search for"],
    },
    {"key": "synthesizer", "label": "Report Writer", "icon": "📝", "match": ["SYNTHESIZER:"]},
    {"key": "verifier", "label": "Verifier Agent", "icon": "✅", "match": ["VERIFIER"]},
    {"key": "renderer", "label": "Renderer", "icon": "📄", "match": ["RENDERER:"]},
]
META_MATCH = "Background task:"
STAGE_ORDER = [s["key"] for s in STAGE_DEFS]

# ---------- Styling (matches streamlit-app.py) ----------
st.markdown(
    """
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    
    <!-- Shifting Gradient Background Mesh & Texture -->
    <div class="bg-mesh" aria-hidden="true"></div>
    <div class="noise-overlay" aria-hidden="true"></div>

    <style>
        :root {
            /* ink */
            --ink: #072e2a;
            --ink-soft: #3f5f5a;
            --ink-mute: #6f8f8a;

            /* surfaces */
            --bg-0: #eafcf9;
            --bg-1: #dff5f1;
            --surface: rgba(255, 255, 255, 0.68);
            --surface-solid: #ffffff;
            --surface-raised: #f3fcfa;
            --line: rgba(7, 46, 42, 0.1);
            --line-soft: rgba(7, 46, 42, 0.06);

            /* accents */
            --teal-500: #0d9488;
            --teal-600: #0f766e;
            --teal-700: #115e56;
            --mint-300: #7dd3c7;
            --mint-200: #b8ece2;
            --cyan-400: #22d3ee;

            --grad-a: linear-gradient(135deg, #0d9488 0%, #22d3ee 100%);
            --grad-b: linear-gradient(135deg, #115e56 0%, #0d9488 100%);
            --grad-text: linear-gradient(120deg, #0f766e 0%, #0d9488 45%, #22d3ee 100%);

            --radius-sm: 12px;
            --radius-md: 18px;
            --radius-lg: 26px;
            --radius-xl: 32px;

            --font-display: 'Space Grotesk', system-ui, sans-serif;
            --font-body: 'Plus Jakarta Sans', system-ui, -apple-system, sans-serif;
            --font-mono: 'JetBrains Mono', ui-monospace, monospace;

            --shadow-sm:
                0 1px 2px rgba(7, 46, 42, 0.05),
                0 8px 20px -10px rgba(13, 148, 136, 0.25);
            --shadow-md:
                0 2px 4px rgba(7, 46, 42, 0.05),
                0 18px 40px -14px rgba(13, 148, 136, 0.3);
            --shadow-lg:
                0 4px 8px rgba(7, 46, 42, 0.06),
                0 30px 60px -16px rgba(13, 148, 136, 0.32);
            --inset-hi: inset 0 1px 0 rgba(255, 255, 255, 0.85);
        }

        /* ===== background layers ===== */
        .bg-mesh {
            position: fixed;
            inset: 0;
            z-index: 0;
            pointer-events: none;
            background:
                radial-gradient(680px 520px at 12% 8%, rgba(34, 211, 238, 0.16), transparent 60%),
                radial-gradient(720px 560px at 88% 18%, rgba(13, 148, 136, 0.18), transparent 62%),
                radial-gradient(640px 640px at 50% 78%, rgba(184, 236, 226, 0.55), transparent 65%),
                radial-gradient(900px 700px at 100% 100%, rgba(17, 94, 86, 0.10), transparent 60%),
                linear-gradient(180deg, #eafcf9 0%, #e2f8f4 40%, #dcf3ee 100%);
            animation: meshShift 22s ease-in-out infinite;
        }

        @keyframes meshShift {
            0%, 100% { filter: hue-rotate(0deg) saturate(1); }
            50%      { filter: hue-rotate(6deg) saturate(1.08); }
        }

        .noise-overlay {
            position: fixed;
            inset: 0;
            z-index: 1;
            pointer-events: none;
            opacity: 0.025;
            mix-blend-mode: multiply;
            background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
            background-repeat: repeat;
            background-size: 256px 256px;
        }

        /* Force the entire HTML/body to take our gradient and override Streamlit Dark Mode */
        html, body, [data-testid="stApp"], .stApp, [data-testid="stAppViewContainer"] {
            background: var(--bg-0) !important;
            background-attachment: fixed !important;
            color: var(--ink) !important;
            min-height: 100vh !important;
            margin: 0 !important;
            padding: 0 !important;
            font-family: var(--font-body) !important;
        }

        /* Fade-in on page load to mask transition glitch */
        @keyframes fadeInPage {
            from { opacity: 0; }
            to   { opacity: 1; }
        }
        .block-container {
            animation: fadeInPage 0.2s ease-in-out !important;
        }

        /* Fix Streamlit Dark Mode Headers and Footers */
        header[data-testid="stHeader"], .stAppHeader {
            background: transparent !important;
            background-color: transparent !important;
            box-shadow: none !important;
        }
        
        [data-testid="stToolbar"] {
            right: 2rem;
        }
        
        footer, [data-testid="stFooter"] {
            display: none !important;
        }

        [data-testid="stSidebar"] {
            display: none !important;
        }

        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 2rem;
            max-width: 1200px;
            position: relative;
            z-index: 10;
        }

        .hero {
            text-align: center;
            padding: 1rem 1rem 0.5rem 1rem;
            margin-bottom: 0.5rem;
        }

        .hero h1 {
            font-family: var(--font-display) !important;
            font-size: 2.5rem;
            line-height: 1.1;
            margin-bottom: 0.35rem;
            color: var(--ink) !important;
            font-weight: 700;
            letter-spacing: -0.03em;
        }

        .hero p {
            font-family: var(--font-body) !important;
            max-width: 760px;
            margin: 0 auto;
            color: var(--ink-soft) !important;
            font-size: 1rem;
            line-height: 1.7;
        }

        .eyebrow {
            display: inline-block;
            padding: 0.4rem 0.8rem;
            border-radius: 999px;
            background: rgba(13, 148, 136, 0.1);
            border: 1px solid rgba(13, 148, 136, 0.2);
            color: var(--teal-600);
            font-weight: 700;
            font-size: 0.82rem;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            margin-bottom: 0.75rem;
            font-family: var(--font-display) !important;
        }

        .metric-card {
            background: var(--surface);
            border: 1px solid var(--line);
            border-radius: var(--radius-md);
            padding: 0.9rem 1rem;
            box-shadow: var(--shadow-sm);
            backdrop-filter: blur(14px);
        }

        .metric-label {
            color: var(--ink-soft);
            font-size: 0.84rem;
            margin-bottom: 0.2rem;
            font-family: var(--font-body) !important;
        }

        .metric-value {
            color: var(--ink) !important;
            font-size: 1.35rem;
            font-weight: 700;
            line-height: 1.1;
            word-break: break-word;
            font-family: var(--font-display) !important;
        }

        .tl-metrics-row {
            display: flex;
            gap: 0.75rem;
            margin-bottom: 1.1rem;
            flex-wrap: wrap;
        }

        .tl-metrics-row .metric-card {
            flex: 1;
            min-width: 150px;
        }

        .log-shell {
            background: var(--surface);
            border: 1px solid var(--line);
            border-radius: var(--radius-lg);
            padding: 1rem 1.1rem 1.1rem 1.1rem;
            box-shadow: var(--shadow-lg);
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
            color: var(--ink) !important;
            font-size: 1.05rem;
            font-weight: 700;
            font-family: var(--font-display) !important;
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
            background: rgba(13, 148, 136, 0.1);
            color: var(--teal-600);
            border: 1px solid rgba(13, 148, 136, 0.2);
        }

        .live-pill.off {
            background: rgba(7, 46, 42, 0.05);
            color: var(--ink-soft);
            border: 1px solid var(--line);
        }

        .live-dot {
            width: 0.55rem;
            height: 0.55rem;
            border-radius: 50%;
            background: var(--teal-500);
            box-shadow: 0 0 0 rgba(13, 148, 136, 0.4);
        }

        .live-dot.on {
            animation: pulse-dot 1.6s ease-in-out infinite;
        }

        .live-dot.off {
            background: var(--ink-mute);
            box-shadow: none;
        }

        @keyframes pulse-dot {
            0%, 100% { box-shadow: 0 0 0 0 rgba(13, 148, 136, 0.45); }
            50% { box-shadow: 0 0 0 8px rgba(13, 148, 136, 0); }
        }

        .log-panel {
            background: rgba(255, 255, 255, 0.5);
            border: 1px solid var(--line);
            border-radius: var(--radius-md);
            padding: 0.85rem 0.95rem;
            max-height: 520px;
            overflow-y: auto;
            font-family: var(--font-mono) !important;
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
            background: rgba(13, 148, 136, 0.06);
        }

        .log-level {
            font-weight: 700;
            letter-spacing: 0.03em;
        }
        .log-level.info { color: var(--teal-600); }
        .log-level.debug { color: var(--ink-mute); }
        .log-level.warning { color: #B45309; }
        .log-level.error, .log-level.critical { color: #DC2626; }

        .empty-state {
            text-align: center;
            padding: 2.5rem 1rem;
            line-height: 1.7;
            color: var(--ink-soft);
        }

        .divider {
            height: 1px;
            background: linear-gradient(90deg, transparent, rgba(13, 148, 136, 0.28), transparent);
            margin: 1rem 0;
        }

        div.stButton > button {
            border-radius: var(--radius-md);
            border: none;
            background: var(--grad-a);
            color: white;
            padding: 0.65rem 1rem;
            font-weight: 700;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
            box-shadow: 0 8px 20px -8px rgba(13, 148, 136, 0.4);
            font-family: var(--font-display) !important;
        }

        div.stButton > button:hover {
            transform: translateY(-1px);
            box-shadow: 0 12px 26px -8px rgba(13, 148, 136, 0.5);
        }

        /* Absolute position of Back to Dashboard button at the top-left */
        div:has(> .back-button-wrap) {
            position: absolute !important;
            top: 2rem !important;
            left: 2rem !important;
            z-index: 1000 !important;
            width: auto !important;
        }

        .back-button-wrap button {
            background: var(--surface) !important;
            color: var(--teal-600) !important;
            border: 1px solid var(--line) !important;
            border-radius: var(--radius-md) !important;
            padding: 0.65rem 1.3rem !important;
            font-family: var(--font-display) !important;
            font-weight: 600 !important;
            box-shadow: var(--shadow-sm) !important;
            transition: all 0.3s ease !important;
            width: auto !important;
        }

        .back-button-wrap button:hover {
            transform: translateY(-2px) !important;
            box-shadow: var(--shadow-md) !important;
            background: var(--surface-solid) !important;
            border-color: var(--teal-500) !important;
        }

        .small-chip {
            display: inline-block;
            margin-right: 0.35rem;
            padding: 0.15rem 0.45rem;
            border-radius: 999px;
            background: rgba(13, 148, 136, 0.1);
            color: var(--teal-600);
            font-size: 0.75rem;
            border: 1px solid rgba(13, 148, 136, 0.2);
        }

        /* Streamlit widgets — dark readable text on light theme */
        [data-testid="stAppViewContainer"],
        [data-testid="stAppViewContainer"] p,
        [data-testid="stAppViewContainer"] span,
        [data-testid="stAppViewContainer"] label {
            color: var(--ink);
        }

        [data-testid="stWidgetLabel"] p,
        [data-testid="stWidgetLabel"] label,
        [data-testid="stWidgetLabel"] span {
            color: var(--ink) !important;
            font-weight: 600 !important;
        }

        div[data-testid="stTextInput"] input {
            color: var(--ink) !important;
            -webkit-text-fill-color: var(--ink) !important;
            caret-color: var(--teal-600) !important;
            background: rgba(255, 255, 255, 0.92) !important;
            border: 1px solid var(--line) !important;
            border-radius: 12px !important;
        }

        div[data-testid="stTextInput"] input::placeholder {
            color: var(--ink-mute) !important;
            opacity: 1 !important;
        }

        div[data-testid="stTextInput"] input:focus {
            border-color: var(--teal-600) !important;
            box-shadow: 0 0 0 2px rgba(13, 148, 136, 0.18) !important;
        }

        div[data-testid="stSelectbox"] [data-baseweb="select"] > div,
        div[data-testid="stSelectbox"] [data-baseweb="select"] span {
            color: var(--ink) !important;
            background: rgba(255, 255, 255, 0.92) !important;
            border-color: var(--line) !important;
        }

        div[data-testid="stSelectbox"] [data-baseweb="select"] svg {
            fill: var(--teal-600) !important;
        }

        div[data-testid="stSelectbox"] [data-baseweb="select"] > div {
            border-radius: 12px !important;
        }

        div[data-testid="stToggle"] label span,
        div[data-testid="stToggle"] label p {
            color: var(--ink-soft) !important;
            font-weight: 500 !important;
        }

        div[data-testid="stToggle"] [data-testid="stMarkdownContainer"] p {
            color: var(--ink-soft) !important;
        }

        div[data-testid="stRadio"] label p {
            color: var(--ink) !important;
            font-weight: 600 !important;
        }

        [data-baseweb="popover"] [role="listbox"] li,
        [data-baseweb="popover"] [role="option"] {
            color: var(--ink) !important;
            background: #FFFFFF !important;
        }

        [data-baseweb="popover"] [role="option"]:hover,
        [data-baseweb="popover"] [role="option"][aria-selected="true"] {
            color: var(--teal-600) !important;
            background: rgba(13, 148, 136, 0.10) !important;
        }

        /* Log line contrast — slightly richer tones */
        .log-time { color: var(--ink-soft); }
        .log-logger { color: var(--ink-soft); font-weight: 500; }
        .log-run-id {
            color: var(--teal-700);
            background: rgba(13, 148, 136, 0.14);
            border: 1px solid rgba(13, 148, 136, 0.28);
            border-radius: 999px;
            padding: 0.05rem 0.4rem;
            font-size: 0.74rem;
            font-weight: 600;
        }
        .log-message { color: var(--ink); font-weight: 500; }

        /* ---------- Agent Accordion (Teal Theme) ---------- */
        .tl-wrap {
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }

        details.agent-card {
            background: var(--surface);
            border: 1px solid var(--line);
            border-radius: var(--radius-md);
            box-shadow: var(--shadow-sm);
            backdrop-filter: blur(14px);
            overflow: hidden;
            transition: all 0.3s ease;
        }

        details.agent-card[open] {
            box-shadow: var(--shadow-md);
            border-color: rgba(13, 148, 136, 0.3);
        }

        summary.agent-card-header {
            display: flex;
            align-items: center;
            padding: 1.25rem 1.5rem;
            cursor: pointer;
            list-style: none; /* Hide default arrow */
            outline: none;
        }
        summary.agent-card-header::-webkit-details-marker {
            display: none; /* Safari */
        }

        .agent-icon {
            width: 3.5rem;
            height: 3.5rem;
            border-radius: var(--radius-sm);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.75rem;
            background: var(--surface-raised);
            border: 1px solid var(--line);
            color: var(--teal-600);
            flex-shrink: 0;
            margin-right: 1.25rem;
            box-shadow: inset 0 2px 4px rgba(255,255,255,0.5);
        }
        .agent-card.completed .agent-icon {
            background: linear-gradient(135deg, #D1FADF, #ECFDF5);
            color: #047857;
            border-color: rgba(16, 185, 129, 0.3);
        }
        .agent-card.error .agent-icon {
            background: linear-gradient(135deg, #FEE2E2, #FEF2F2);
            color: #B91C1C;
            border-color: rgba(220, 38, 38, 0.3);
        }

        .agent-info {
            flex: 1;
        }

        .agent-name {
            color: var(--ink);
            font-size: 1.2rem;
            font-weight: 700;
            margin-bottom: 0.25rem;
            font-family: var(--font-display) !important;
        }

        .agent-status {
            color: var(--ink-soft);
            font-size: 0.9rem;
            display: flex;
            align-items: center;
            gap: 0.4rem;
            font-family: var(--font-body) !important;
        }

        .status-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: var(--ink-mute);
        }
        .status-dot.completed { background: #10B981; }
        .status-dot.error { background: #EF4444; }

        .agent-chevron {
            color: var(--teal-600);
            font-size: 1.25rem;
            font-weight: bold;
            transition: transform 0.3s ease;
            margin-left: 1rem;
        }
        details[open] .agent-chevron {
            transform: rotate(90deg);
        }

        .agent-logs-box {
            background: rgba(13, 148, 136, 0.05);
            border-top: 1px solid var(--line);
            padding: 1.5rem;
            font-family: var(--font-mono) !important;
            font-size: 0.85rem;
            line-height: 1.6;
            color: var(--ink);
        }

        .agent-log-line {
            margin-bottom: 0.6rem;
            padding-left: 1rem;
            border-left: 2px solid rgba(13, 148, 136, 0.3);
        }
        .agent-log-line:last-child {
            margin-bottom: 0;
        }
        .agent-log-time {
            color: var(--teal-600);
            font-weight: 700;
            margin-right: 0.5rem;
            font-size: 0.8rem;
        }
        .agent-log-msg {
            color: var(--ink);
        }
        
        .no-logs {
            color: var(--ink-mute);
            font-style: italic;
        }
        
        .header-metrics {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            padding: 1.5rem;
            background: transparent;
            margin-bottom: 1rem;
        }
        
        .header-metric-col {
            display: flex;
            flex-direction: column;
        }
        
        .header-metric-label {
            color: var(--ink-soft);
            font-size: 0.95rem;
            margin-bottom: 0.25rem;
            font-family: var(--font-body) !important;
        }
        
        .header-metric-value {
            color: var(--ink) !important;
            font-size: 1.45rem;
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-family: var(--font-display) !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


def esc(text: str) -> str:
    return (text or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


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
        return f'<div class="log-line"><span class="log-message">{esc(raw_line)}</span></div>'

    timestamp = entry["timestamp"]
    level = entry["level"]
    logger = entry["logger"].strip()
    run_id = entry["run_id"]
    message = esc(entry["message"])

    return (
        f'<div class="log-line">'
        f'<span class="log-time">{timestamp}</span> '
        f'<span class="log-level {level_class(level)}">[{level}]</span> '
        f'<span class="log-logger">{esc(logger)}</span> '
        f'<span class="log-run-id">{esc(run_id)}</span> '
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


# ---------- Option 2: agent timeline helpers ----------

def classify_stage(message: str) -> str | None:
    """Map a raw log message to one of the real graph nodes, if it matches."""
    for stage in STAGE_DEFS:
        if any(token in message for token in stage["match"]):
            return stage["key"]
    return None


def friendly_detail(message: str) -> str:
    """Strip the leading STAGE: tag so the UI shows just the human-readable part."""
    return re.sub(r"^(INTAKE|PLANNER|RESEARCHER|SYNTHESIZER|VERIFIER(?: FAILED)?|RENDERER):\s*", "", message)


def get_recent_run_ids(lines: list[str], limit: int = 12) -> list[str]:
    """Most-recently-seen run_ids first, deduplicated."""
    seen: list[str] = []
    for line in reversed(lines):
        entry = parse_log_line(line)
        if not entry:
            continue
        rid = entry["run_id"]
        if rid and rid != "-" and rid not in seen:
            seen.append(rid)
        if len(seen) >= limit:
            break
    return seen


def entries_for_run(run_id: str) -> list[dict]:
    lines = tail_lines(LOG_FILES["Application log (app.log)"])
    out = []
    for line in lines:
        entry = parse_log_line(line)
        if entry and entry["run_id"] == run_id:
            out.append(entry)
    return out


def build_timeline(entries: list[dict]) -> dict:
    """Walk a single run's log entries chronologically and derive per-stage
    status + an overall run status. This is reconstructed from log text."""
    stages = {s["key"]: {"status": "waiting", "detail": None, "time": None, "count": 0, "logs": []} for s in STAGE_DEFS}
    meta = {
        "started_at": None,
        "finished_at": None,
        "topic": None,
        "overall_status": "running",
        "error": None,
        "retries": 0,
    }
    last_stage_key = None

    for entry in entries:
        msg = entry["message"]
        ts = entry["timestamp"]

        if META_MATCH in msg:
            if "Starting graph execution" in msg:
                meta["started_at"] = meta["started_at"] or ts
            elif "Run completely finalized" in msg:
                meta["overall_status"] = "completed"
                meta["finished_at"] = ts
            elif "Graph execution error" in msg:
                meta["overall_status"] = "failed"
                meta["finished_at"] = ts
                meta["error"] = friendly_detail(msg)
            continue

        stage_key = classify_stage(msg)
        if stage_key is None:
            continue

        if stage_key == "intake":
            topic_match = re.search(r"Starting research on:\s*(.+)$", msg)
            if topic_match:
                meta["topic"] = topic_match.group(1).strip()

        if "Routing back to synthesizer" in msg:
            meta["retries"] += 1

        stage = stages[stage_key]
        stage["status"] = "completed"
        stage["detail"] = friendly_detail(msg)
        stage["logs"].append({"time": ts.split(" ")[1], "message": friendly_detail(msg)})
        stage["time"] = ts
        stage["count"] += 1
        last_stage_key = stage_key

    if meta["overall_status"] == "running" and last_stage_key:
        stages[last_stage_key]["status"] = "running"
    elif meta["overall_status"] == "completed":
        for stage in stages.values():
            if stage["count"] > 0:
                stage["status"] = "completed"
    elif meta["overall_status"] == "failed" and last_stage_key:
        stages[last_stage_key]["status"] = "error"

    if not meta["started_at"] and entries:
        meta["started_at"] = entries[0]["timestamp"]

    return {"stages": stages, "meta": meta}


STATUS_META = {
    "waiting": {"pill": "Waiting", "class": "waiting"},
    "running": {"pill": "Running", "class": "running"},
    "completed": {"pill": "Completed", "class": "completed"},
    "error": {"pill": "Error", "class": "error"},
}


def render_accordion_item_html(stage_def: dict, stage_state: dict) -> str:
    status = stage_state["status"]
    logs = stage_state["logs"]

    display_status = status.capitalize()

    # Status dot color
    if status == "completed":
        dot_color = "#10B981"
        dot_label_color = "#047857"
        card_border = "rgba(16,185,129,0.25)"
        icon_bg = "linear-gradient(135deg, #D1FAE5, #ECFDF5)"
        icon_border = "rgba(16,185,129,0.3)"
    elif status == "error":
        dot_color = "#EF4444"
        dot_label_color = "#B91C1C"
        card_border = "rgba(239,68,68,0.25)"
        icon_bg = "linear-gradient(135deg, #FEE2E2, #FEF2F2)"
        icon_border = "rgba(239,68,68,0.3)"
    else:
        dot_color = "#94A3B8"
        dot_label_color = "#64748B"
        card_border = "rgba(15,118,110,0.12)"
        icon_bg = "linear-gradient(135deg, rgba(20,184,166,0.12), rgba(15,118,110,0.04))"
        icon_border = "rgba(15,118,110,0.15)"

    log_lines_html = ""
    if not logs:
        log_lines_html = '<p class="no-logs">No execution logs for this stage yet.</p>'
    else:
        for log in logs:
            time_str = esc(log["time"])
            msg = esc(log["message"])
            log_lines_html += (
                f'<div class="log-row">'
                f'<span class="log-ts">[{time_str}]</span>'
                f'<span class="log-msg">{msg}</span>'
                f'</div>'
            )

    label = esc(stage_def['label'])
    icon = stage_def['icon']

    return (
        f'<details class="a-card" style="border-color:{card_border}">'
        f'<summary class="a-header">'
        f'<div class="a-icon" style="background:{icon_bg};border-color:{icon_border}">{icon}</div>'
        f'<div class="a-meta">'
        f'<div class="a-name">{label}</div>'
        f'<div class="a-status">'
        f'Status:&nbsp;<strong style="color:{dot_label_color};">{display_status}</strong>&nbsp;'
        f'<span class="s-dot" style="background:{dot_color};"></span>'
        f'</div>'
        f'</div>'
        f'<div class="a-chevron">&#x276F;</div>'
        f'</summary>'
        f'<div class="a-logs">'
        f'<div class="a-logs-title">SESSION LOGS:</div>'
        f'{log_lines_html}'
        f'</div>'
        f'</details>'
    )


def render_timeline_panel(run_id: str, entries: list[dict]) -> None:
    if not entries:
        st.markdown(
            '<div class="log-shell" style="background: white;">'
            '<div class="empty-state">No log entries found for the latest run.<br/>'
            "Start a research run from the workspace.</div></div>",
            unsafe_allow_html=True,
        )
        return

    data = build_timeline(entries)
    meta = data["meta"]
    stages = data["stages"]

    status_label = {"running": "Running", "completed": "Completed", "failed": "Failed"}[meta["overall_status"]]
    dot_color = "#10B981" if status_label == "Running" else ("#059669" if status_label == "Completed" else "#EF4444")
    dot_anim = "pulse-dot" if status_label == "Running" else "none"

    elapsed_str = "0s"
    try:
        start_dt = datetime.strptime(entries[0]["timestamp"], "%Y-%m-%d %H:%M:%S")
        end_ts = meta["finished_at"] or entries[-1]["timestamp"]
        end_dt = datetime.strptime(end_ts, "%Y-%m-%d %H:%M:%S")
        elapsed_seconds = int((end_dt - start_dt).total_seconds())
        elapsed_str = f"{elapsed_seconds}s" if elapsed_seconds < 60 else f"{elapsed_seconds // 60}m {elapsed_seconds % 60}s"
    except (ValueError, IndexError):
        pass

    topic = meta["topic"] or "Unknown topic"

    metrics_html = (
        '<div class="run-meta-col">'
        '<div class="run-meta-label">Research Topic</div>'
        f'<div class="run-meta-value">{esc(topic)}</div>'
        '</div>'
        '<div class="run-meta-sep"></div>'
        '<div class="run-meta-col">'
        '<div class="run-meta-label">Status</div>'
        '<div class="run-meta-value">'
        f'<span style="display:inline-block;width:11px;height:11px;border-radius:50%;background:{dot_color};box-shadow:0 0 8px {dot_color};"></span>'
        f'<span style="color:{dot_color};">{status_label}</span>'
        '</div>'
        '</div>'
        '<div class="run-meta-sep"></div>'
        '<div class="run-meta-col">'
        '<div class="run-meta-label">Elapsed</div>'
        f'<div class="run-meta-value">{elapsed_str}</div>'
        '</div>'
    )

    items_html_joined = "".join(
        render_accordion_item_html(stage_def, stages[stage_def["key"]])
        for stage_def in STAGE_DEFS
    )

    accordion_css = """
    <style>
      *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
      body {
        font-family: var(--font-body);
        background: transparent;
        padding: 0.5rem 0;
        color: var(--ink);
      }

      /* ── Run metadata bar ── */
      .run-meta {
        display: flex;
        align-items: center;
        gap: 2.5rem;
        background: var(--surface);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid var(--line);
        border-radius: var(--radius-md);
        padding: 1.2rem 1.8rem;
        margin-bottom: 1.5rem;
        box-shadow: var(--shadow-sm);
      }
      .run-meta-col { display: flex; flex-direction: column; gap: 0.15rem; }
      .run-meta-label {
        font-size: 0.75rem;
        font-weight: 600;
        color: var(--ink-soft);
        letter-spacing: 0.07em;
        text-transform: uppercase;
        font-family: var(--font-body);
      }
      .run-meta-value {
        font-size: 1.05rem;
        font-weight: 700;
        color: var(--ink);
        display: flex;
        align-items: center;
        gap: 0.45rem;
        font-family: var(--font-display);
      }
      .run-meta-sep {
        width: 1px;
        height: 2.2rem;
        background: var(--line);
        flex-shrink: 0;
      }

      /* ── Card list ── */
      .card-list { display: flex; flex-direction: column; gap: 0.9rem; }

      /* ── Agent card ── */
      .a-card {
        background: var(--surface);
        backdrop-filter: blur(18px);
        -webkit-backdrop-filter: blur(18px);
        border: 1px solid var(--line);
        border-radius: var(--radius-md);
        box-shadow: var(--shadow-sm);
        overflow: hidden;
        transition: box-shadow 0.25s ease, border-color 0.25s ease;
      }
      .a-card[open] {
        box-shadow: var(--shadow-md);
        border-color: rgba(13, 148, 136, 0.3);
      }

      /* ── Card header (summary) ── */
      .a-header {
        display: flex;
        align-items: center;
        gap: 1.1rem;
        padding: 1.15rem 1.5rem;
        cursor: pointer;
        list-style: none;
        outline: none;
        user-select: none;
      }
      .a-header::-webkit-details-marker { display: none; }
      .a-header:hover { background: rgba(13, 148, 136, 0.05); }

      /* ── Icon box ── */
      .a-icon {
        width: 3.2rem;
        height: 3.2rem;
        border-radius: var(--radius-sm);
        border: 1px solid var(--line);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.6rem;
        flex-shrink: 0;
        background: var(--surface-raised);
        color: var(--teal-600);
        box-shadow: inset 0 2px 4px rgba(255,255,255,0.7);
      }

      /* ── Agent meta text ── */
      .a-meta { flex: 1; min-width: 0; }
      .a-name {
        font-size: 1.15rem;
        font-weight: 700;
        color: var(--ink);
        line-height: 1.2;
        margin-bottom: 0.28rem;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        font-family: var(--font-display);
      }
      .a-status {
        font-size: 0.88rem;
        font-weight: 500;
        color: var(--ink-soft);
        display: flex;
        align-items: center;
        gap: 0.35rem;
        font-family: var(--font-body);
      }
      .s-dot {
        display: inline-block;
        width: 9px;
        height: 9px;
        border-radius: 50%;
        flex-shrink: 0;
      }

      /* ── Chevron ── */
      .a-chevron {
        font-size: 1rem;
        color: var(--teal-600);
        font-weight: 700;
        transition: transform 0.28s cubic-bezier(.4,0,.2,1);
        flex-shrink: 0;
        opacity: 0.75;
      }
      .a-card[open] .a-chevron { transform: rotate(90deg); }

      /* ── Session logs panel ── */
      .a-logs {
        margin: 0 1rem 1rem 1rem;
        background: rgba(13, 148, 136, 0.05);
        border: 1px solid var(--line);
        border-radius: var(--radius-sm);
        padding: 1.25rem 1.4rem;
        overflow: hidden;
      }
      .a-logs-title {
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        color: var(--teal-700);
        margin-bottom: 0.9rem;
        font-family: var(--font-display);
      }

      /* ── Log rows ── */
      .log-row {
        display: flex;
        gap: 0.85rem;
        align-items: baseline;
        padding: 0.3rem 0;
        border-bottom: 1px solid var(--line-soft);
        font-size: 0.875rem;
        line-height: 1.55;
      }
      .log-row:last-child { border-bottom: none; }
      .log-ts {
        font-family: var(--font-mono);
        font-size: 0.8rem;
        font-weight: 700;
        color: var(--teal-600);
        white-space: nowrap;
        flex-shrink: 0;
      }
      .log-msg {
        color: var(--ink);
        font-weight: 500;
        word-break: break-word;
      }
      .no-logs {
        color: var(--ink-mute);
        font-style: italic;
        font-size: 0.875rem;
        padding: 0.25rem 0;
        font-family: var(--font-body);
      }
    </style>
    """

    full_html = (
        accordion_css
        + '<div class="run-meta">'
        + metrics_html
        + '</div>'
        + '<div class="card-list">'
        + items_html_joined
        + '</div>'
    )

    st.markdown(full_html, unsafe_allow_html=True)


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
# Visually positioned Back to Dashboard button (absolute-positioned via CSS class)
st.markdown("<div class='back-button-wrap' style='position: absolute !important; top: 2rem !important; left: 2rem !important; z-index: 1000 !important; width: auto !important;'>", unsafe_allow_html=True)
if st.button("← Back to Dashboard", key="back_dashboard"):
    st.switch_page("streamlit-app.py")
st.markdown("</div>", unsafe_allow_html=True)

# Centered Header & Subheader (Full-width for perfect page centering)
st.markdown(
    """
    <div class="hero" style="padding-top: 2rem; display: flex; flex-direction: column; align-items: center; justify-content: center; position: relative; z-index: 10;">
        <h1 style="font-family: 'Space Grotesk', sans-serif !important; color: #072e2a !important; text-align: center; margin: 0; font-size: 2.5rem; font-weight: 700; letter-spacing: -0.03em;">Agents Tracker</h1>
        <p style="font-family: 'Plus Jakarta Sans', sans-serif !important; color: #3f5f5a !important; text-align: center; margin-top: 0.5rem; max-width: 600px; margin-left: auto; margin-right: auto; font-size: 1rem; line-height: 1.7;">
            Track your latest research run stage by stage. Watch the AI agents coordinate in real-time, from initial planning to final report generation.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

# ---------- Timeline Render ----------
app_log_lines = tail_lines(LOG_FILES["Application log (app.log)"])
recent_runs = get_recent_run_ids(app_log_lines)

if recent_runs:
    active_run = recent_runs[0]
    render_timeline_panel(active_run, entries_for_run(active_run))
else:
    st.markdown(
        '''
        <div class="log-shell" style="max-width: 800px; margin: 0 auto; padding: 2rem; background: white; text-align: center;">
            <div class="empty-state">No research runs found yet. Start a job to see the timeline here.</div>
        </div>
        ''',
        unsafe_allow_html=True,
    )

# Auto-refresh every 2 seconds to keep logs updated in real-time
time.sleep(2)
st.rerun()
