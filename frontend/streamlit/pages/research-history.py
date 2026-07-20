from pathlib import Path

import streamlit as st
import requests

#--------Backend API Config---------
BACKEND_URL = "http://localhost:8000/api/research"

FAVICON_PATH = Path(__file__).resolve().parent.parent / "favicon.svg"

#----Helper functions for API call---------
def fetch_history_data():
    try:
        response = requests.get(BACKEND_URL)
        if response.status_code == 200:
            return response.json().get("data", [])
    except requests.exceptions.ConnectionError:
        st.error("Could not connect to backend. Ensure backend is running.")
    except Exception as e:
        st.error(f"Error fetching history data: {e}")
    return[]

#-----------Page Configuraion----------
st.set_page_config(
    page_title="InsightSwarm - Research History",
    page_icon=str(FAVICON_PATH),
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ---------- Styling (matches landing page theme) ----------
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

        /* Force background & font overrides for Streamlit */
        html, body, [data-testid="stApp"], .stApp, [data-testid="stAppViewContainer"] {
            background: var(--bg-0) !important;
            background-attachment: fixed !important;
            color: var(--ink) !important;
            min-height: 100vh !important;
            margin: 0 !important;
            padding: 0 !important;
            font-family: var(--font-body) !important;
        }

        /* Fade-in on page load */
        @keyframes fadeInPage {
            from { opacity: 0; }
            to   { opacity: 1; }
        }
        .block-container {
            animation: fadeInPage 0.2s ease-in-out !important;
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 1200px;
            position: relative;
            z-index: 10;
        }

        /* Fix Streamlit headers / footers */
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
            display: none;
        }

        /* ===== Hero Section ===== */
        .hero {
            text-align: center;
            padding: 1.5rem 1rem 0.75rem 1rem;
            margin-bottom: 1rem;
            position: relative;
            z-index: 10;
        }

        .hero h1 {
            font-size: 3rem;
            line-height: 1.1;
            margin-bottom: 0.35rem;
            color: #0F2A22;
            font-weight: 800;
            letter-spacing: -0.03em;
        }

        .hero p {
            max-width: 900px;
            margin: 0 auto;
            color: #4B5D57;
            font-size: 1.05rem;
            line-height: 1.8;
        }

        /* ===== Divider ===== */
        .divider {
            height: 1px;
            background: linear-gradient(90deg, transparent, rgba(15, 118, 110, 0.28), transparent);
            margin: 1.25rem 0;
            position: relative;
            z-index: 10;
        }

        /* ===== History Item Rows (white card badge) ===== */
        div[data-testid="stHorizontalBlock"] {
            background: #ffffff !important;
            border: 1.5px solid rgba(7, 46, 42, 0.08) !important;
            border-radius: var(--radius-lg) !important;
            padding: 1.2rem 1.8rem !important;
            margin-bottom: 1.25rem !important;
            box-shadow:
                0 2px 8px rgba(7, 46, 42, 0.04),
                0 10px 30px -10px rgba(13, 148, 136, 0.14),
                var(--inset-hi) !important;
            transition:
                transform 0.35s cubic-bezier(0.22, 1, 0.36, 1),
                box-shadow 0.35s cubic-bezier(0.22, 1, 0.36, 1),
                border-color 0.35s ease !important;
            position: relative;
            z-index: 10;
        }

        div[data-testid="stHorizontalBlock"]:hover {
            transform: translateY(-6px) scale(1.012) !important;
            border-color: rgba(13, 148, 136, 0.35) !important;
            box-shadow:
                0 6px 16px rgba(7, 46, 42, 0.06),
                0 24px 48px -12px rgba(13, 148, 136, 0.22),
                var(--inset-hi) !important;
        }

        /* ===== Status Badges ===== */
        .badge {
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 999px;
            font-family: var(--font-mono);
            font-size: 0.72rem;
            font-weight: 600;
            letter-spacing: 0.04em;
            text-transform: uppercase;
            margin-bottom: 0.4rem;
        }

        .badge-success {
            background: rgba(13, 148, 136, 0.12);
            color: var(--teal-600);
            border: 1px solid rgba(13, 148, 136, 0.25);
        }

        .badge-archived {
            background: rgba(7, 46, 42, 0.06);
            color: var(--ink-mute);
            border: 1px solid var(--line);
        }

        /* ===== History Title ===== */
        .history-title {
            font-family: var(--font-display) !important;
            font-size: 1.2rem;
            font-weight: 700;
            color: var(--ink) !important;
            letter-spacing: -0.015em;
            margin-bottom: 0.5rem;
        }

        /* ===== Meta Info Badges ===== */
        .history-meta {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            align-items: center;
            margin-top: 0.5rem;
        }

        .meta-chip {
            display: inline-flex;
            align-items: center;
            gap: 0.35rem;
            padding: 0.3rem 0.75rem;
            border-radius: 999px;
            background: var(--bg-1);
            border: 1px solid rgba(7, 46, 42, 0.08);
            font-family: var(--font-mono);
            font-size: 0.75rem;
            color: var(--ink-soft);
            white-space: nowrap;
            transition: border-color 0.2s ease, background 0.2s ease;
        }

        .meta-chip:hover {
            border-color: rgba(13, 148, 136, 0.3);
            background: rgba(13, 148, 136, 0.06);
        }

        .meta-chip .meta-label {
            font-weight: 600;
            color: var(--teal-700);
            font-size: 0.68rem;
            text-transform: uppercase;
            letter-spacing: 0.03em;
        }

        /* ===== Popover / Actions Menu ===== */
        [data-testid="stPopover"] button {
            background: var(--surface) !important;
            border: 1px solid var(--line) !important;
            border-radius: var(--radius-sm) !important;
            color: var(--ink) !important;
            font-family: var(--font-display) !important;
            font-size: 1.2rem !important;
            font-weight: 600 !important;
            box-shadow: var(--shadow-sm) !important;
            transition: transform 0.2s ease, box-shadow 0.2s ease !important;
        }

        [data-testid="stPopover"] button:hover {
            transform: translateY(-1px) !important;
            box-shadow: var(--shadow-md) !important;
            border-color: rgba(13, 148, 136, 0.3) !important;
        }

        [data-testid="stPopoverBody"] {
            background: var(--surface-solid) !important;
            border: 1px solid var(--line) !important;
            border-radius: var(--radius-md) !important;
            box-shadow: var(--shadow-lg) !important;
            padding: 0.75rem !important;
        }

        [data-testid="stPopoverBody"] strong,
        [data-testid="stPopoverBody"] b {
            font-family: var(--font-display) !important;
            color: var(--ink) !important;
        }

        /* ===== Streamlit Info/Error Alerts ===== */
        [data-testid="stAlert"] {
            font-family: var(--font-body) !important;
            border-radius: var(--radius-sm) !important;
            position: relative;
            z-index: 10;
        }

        /* ===== Link Buttons (inside popover) ===== */
        [data-testid="stLinkButton"] a {
            font-family: var(--font-display) !important;
            font-weight: 600 !important;
            border-radius: var(--radius-sm) !important;
            transition: transform 0.2s ease, box-shadow 0.2s ease !important;
        }

        [data-testid="stLinkButton"] a:hover {
            transform: translateY(-1px) !important;
        }

        /* ===== Back Button ===== */
        .back-button-wrap + div button,
        button[data-testid="stBaseButton-secondary"] {
            font-family: var(--font-display) !important;
            font-weight: 600 !important;
            font-size: 0.92rem !important;
            color: var(--teal-700) !important;
            background: var(--surface-raised) !important;
            border: 1px solid var(--line) !important;
            border-radius: var(--radius-sm) !important;
            padding: 0.5rem 1rem !important;
            box-shadow: var(--shadow-sm) !important;
            transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease !important;
            position: relative;
            z-index: 1000;
        }

        .back-button-wrap + div button:hover,
        button[data-testid="stBaseButton-secondary"]:hover {
            transform: translateX(-2px) !important;
            border-color: rgba(13, 148, 136, 0.3) !important;
            box-shadow: var(--shadow-md) !important;
        }

        /* ===== Streamlit markdown text overrides ===== */
        .stMarkdown, .stMarkdown p, .stMarkdown span {
            font-family: var(--font-body) !important;
            color: var(--ink) !important;
        }

        h1, h2, h3, h4, h5, h6 {
            font-family: var(--font-display) !important;
            color: var(--ink) !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

#-----Page Header-----------
st.markdown(
    """
    <div class="hero">
    <h1>Research History</h1>
    <p>Access your past auntonomous research jobs and AI-Generated reports.</p>
    </div>
    <div class="divider"></div>
""", unsafe_allow_html=True
)

#---------Fetch data from beckend -------------
hisotry_data = fetch_history_data()

#----------Render History List----------------
if not hisotry_data:
    st.info("No research history found.")
else: 
    for item in hisotry_data:
        with st.container():
            col1, col2, col3 = st.columns([8, 2, 2], vertical_alignment="center")

            with col1:
                badge_class = "badge-success" if item["status"] == "Completed" else "badge-archived"
                st.markdown(f"""
                    <div>
                        <div class="badge {badge_class}">{item["status"]}</div>
                        <div class="history-title">{item["title"]}</div>
                        <div class="history-meta">
                            <span class="meta-chip"><span class="meta-label">ID</span> {item["id"][:8]}…</span>
                            <span class="meta-chip"><span class="meta-label">Generated</span> {item["date"]}</span>
                            <span class="meta-chip"><span class="meta-label">Agents</span> {item["agents_used"]}</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            with col2:
                if item["status"] == "Completed":
                    st.link_button("📄 View Report", url=f"http://localhost:5173/report/{item['id']}", use_container_width=True)
            with col3:
                if item["status"] == "Completed":
                    st.link_button("⬇️ Download PDF", url=f"http://localhost:8000/api/research/{item['id']}/download", use_container_width=True)

st.write("")

#change app.py to dashboard
st.markdown("<div class='back-button-wrap' style='position: absolute !important; top: 2rem !important; left: 2rem !important; z-index: 1000 !important; width: auto !important;'>", unsafe_allow_html=True)
if st.button("← Back to Dashboard", key="back_dashboard"):
    st.switch_page("streamlit-app.py")
st.markdown("</div>", unsafe_allow_html=True)