import streamlit as st
import requests

#--------Backend API Config---------
BACKEND_URL = "http://localhost:8000/api/research"

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
    return []

#-----------Page Configuraion----------
st.set_page_config(
    page_title="InsightSwarm | Research History",
    page_icon="🕒",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------- Styling ----------
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

            /* gradients */
            --grad-a: linear-gradient(135deg, #0d9488 0%, #22d3ee 100%);
            --grad-b: linear-gradient(135deg, #115e56 0%, #0d9488 100%);

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

        /* Override Streamlit container background and default body fonts */
        html, body, [data-testid="stApp"], .stApp, [data-testid="stAppViewContainer"] {
            background: var(--bg-0) !important;
            background-attachment: fixed !important;
            color: var(--ink) !important;
            min-height: 100vh !important;
            margin: 0 !important;
            padding: 0 !important;
            font-family: var(--font-body) !important;
        }

        /* Fix Streamlit Headers & Footers */
        header[data-testid="stHeader"], .stAppHeader {
            background: transparent !important;
            background-color: transparent !important;
            box-shadow: none !important;
        }

        footer, [data-testid="stFooter"] {
            display: none !important;
        }

        [data-testid="stSidebar"] {
            display: none !important;
        }

        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 1200px;
            position: relative;
            z-index: 10;
        }

        .hero {
            text-align: center;
            padding: 1.5rem 1rem 0.75rem 1rem;
            margin-bottom: 1rem;
        }

        .hero h1 {
            font-family: var(--font-display) !important;
            font-size: 3.2rem;
            line-height: 1.1;
            margin-bottom: 0.5rem;
            color: var(--ink) !important;
            font-weight: 700;
            letter-spacing: -0.03em;
        }

        .hero p {
            font-family: var(--font-body) !important;
            max-width: 900px;
            margin: 0 auto;
            color: var(--ink-soft) !important;
            font-size: 1.05rem;
            line-height: 1.8;
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
            margin-bottom: 1rem;
            font-family: var(--font-display) !important;
        }

        .section-title {
            color: var(--ink) !important;
            font-family: var(--font-display) !important;
            font-weight: 700;
            font-size: 1.45rem;
            margin: 0.5rem 0 0.25rem 0;
        }

        .section-subtitle {
            color: var(--ink-mute);
            margin-bottom: 1rem;
        }

        /* Use semantic surfaces for cards */
        .metric-card {
            background: var(--surface);
            border: 1px solid var(--line);
            border-radius: var(--radius-md);
            padding: 1rem 1.1rem;
            box-shadow: var(--shadow-sm);
            backdrop-filter: blur(14px);
        }

        .metric-label {
            color: var(--ink-soft);
            font-size: 0.88rem;
            margin-bottom: 0.25rem;
        }

        .metric-value {
            color: var(--ink) !important;
            font-size: 1.5rem;
            font-weight: 800;
            line-height: 1.1;
        }

        .metric-note {
            color: var(--ink-soft);
            font-size: 0.86rem;
            margin-top: 0.25rem;
        }

        .feature-card {
            height: 100%;
            background: var(--surface);
            border: 1px solid var(--line);
            border-radius: var(--radius-lg);
            padding: 1.35rem;
            box-shadow: var(--shadow-md);
            backdrop-filter: blur(16px);
            transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
        }

        .feature-card:hover {
            transform: translateY(-4px);
            border-color: rgba(13, 148, 136, 0.35);
            box-shadow: var(--shadow-lg);
        }

        .feature-badge {
            display: inline-block;
            padding: 0.32rem 0.7rem;
            border-radius: 999px;
            font-size: 0.75rem;
            font-weight: 700;
            margin-bottom: 0.9rem;
            letter-spacing: 0.04em;
            text-transform: uppercase;
        }

        .badge-primary {
            background: rgba(13, 148, 136, 0.14);
            color: var(--teal-600);
            border: 1px solid rgba(13, 148, 136, 0.28);
        }

        .badge-soon {
            background: rgba(7, 46, 42, 0.06);
            color: var(--ink-soft);
            border: 1px solid rgba(7, 46, 42, 0.12);
        }

        .feature-title {
            color: var(--ink) !important;
            font-size: 1.25rem;
            font-weight: 800;
            margin-bottom: 0.35rem;
            font-family: var(--font-display) !important;
        }

        .feature-desc {
            color: var(--ink-soft);
            line-height: 1.7;
            font-size: 0.98rem;
            min-height: 3.3rem;
        }

        .feature-meta {
            color: var(--ink-mute);
            font-size: 0.85rem;
            margin-top: 0.7rem;
        }

        .cta-wrap {
            margin-top: 1rem;
        }

        .footer-note {
            text-align: center;
            color: var(--ink-soft);
            font-size: 0.9rem;
            margin-top: 1.5rem;
            padding-top: 0.8rem;
        }

        .divider {
            height: 1px;
            background: linear-gradient(90deg, transparent, rgba(13, 148, 136, 0.28), transparent);
            margin: 1.25rem 0;
        }

        /* Streamlit Popover styling */
        div[data-testid="stPopover"] > button, div.stPopover > button {
            background: var(--surface) !important;
            border: 1px solid var(--line) !important;
            color: var(--ink) !important;
            border-radius: var(--radius-sm) !important;
            padding: 0.4rem 0.8rem !important;
            font-weight: 600 !important;
            box-shadow: var(--shadow-sm) !important;
            transition: transform 0.2s ease, box-shadow 0.2s ease !important;
        }

        div[data-testid="stPopover"] > button:hover, div.stPopover > button:hover {
            transform: translateY(-1px) !important;
            box-shadow: var(--shadow-md) !important;
            border-color: rgba(13, 148, 136, 0.35) !important;
        }

        /* Streamlit Button tweaks */
        div.stButton > button {
            width: 100%;
            border-radius: var(--radius-sm);
            border: 1px solid rgba(13, 148, 136, 0.35);
            background: var(--grad-b);
            color: white;
            padding: 0.7rem 1rem;
            font-family: var(--font-display) !important;
            font-weight: 700;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
            box-shadow: var(--shadow-sm);
        }

        div.stButton > button:hover {
            transform: translateY(-1px);
            box-shadow: var(--shadow-md);
            border-color: rgba(13, 148, 136, 0.55);
        }

        /* Streamlit Link Button styling (e.g. View Report, Download PDF) */
        div.stLinkButton > a {
            width: 100%;
            border-radius: var(--radius-sm) !important;
            border: 1px solid rgba(13, 148, 136, 0.35) !important;
            background: var(--grad-b) !important;
            color: white !important;
            padding: 0.7rem 1rem !important;
            font-family: var(--font-display) !important;
            font-weight: 700 !important;
            text-align: center !important;
            text-decoration: none !important;
            display: inline-block !important;
            transition: transform 0.2s ease, box-shadow 0.2s ease !important;
            box-shadow: var(--shadow-sm) !important;
        }

        div.stLinkButton > a:hover {
            transform: translateY(-1px) !important;
            box-shadow: var(--shadow-md) !important;
            border-color: rgba(13, 148, 136, 0.55) !important;
            color: white !important;
        }

        .soon-button button {
            background: rgba(7, 46, 42, 0.05) !important;
            border: 1px solid rgba(7, 46, 42, 0.12) !important;
            box-shadow: none !important;
            color: var(--ink-soft) !important;
        }

        .small-chip {
            display: inline-block;
            margin-right: 0.35rem;
            padding: 0.15rem 0.45rem;
            border-radius: 999px;
            background: rgba(13, 148, 136, 0.10);
            color: var(--teal-600);
            font-size: 0.75rem;
            border: 1px solid rgba(13, 148, 136, 0.22);
        }

        /* Badges for status inside list */
        .badge {
            display: inline-block;
            padding: 0.25rem 0.6rem;
            border-radius: 999px;
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.04em;
            text-transform: uppercase;
            font-family: var(--font-mono) !important;
            margin-bottom: 0.5rem;
        }

        .badge-success {
            background: rgba(13, 148, 136, 0.1);
            color: var(--teal-600);
            border: 1px solid rgba(13, 148, 136, 0.2);
        }

        .badge-archived {
            background: rgba(7, 46, 42, 0.06);
            color: var(--ink-soft);
            border: 1px solid rgba(7, 46, 42, 0.12);
        }

        /* Title and Meta info inside list items */
        .history-title {
            font-family: var(--font-display) !important;
            font-size: 1.3rem;
            font-weight: 600;
            color: var(--ink);
            margin: 0.25rem 0;
            letter-spacing: -0.01em;
        }

        .history-meta {
            font-family: var(--font-mono) !important;
            font-size: 0.8rem;
            color: var(--ink-soft);
            margin-top: 0.4rem;
        }

        .history-meta b {
            color: var(--ink);
        }

        .back-button-wrap {
            position: absolute !important;
            top: 2rem !important;
            left: 2rem !important;
            z-index: 1000 !important;
            width: auto !important;
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
            col1, col2 = st.columns([11, 1], vertical_alignment="center")

            with col1:
                badge_class = "badge-success" if item["status"] == "Completed" else "badge-archived"
                st.markdown(f"""
                    <div>
                        <div class="badge {badge_class}">{item["status"]}</div>
                        <div class="history-title">{item["title"]}</div>
                        <div class="history-meta">
                            <b>ID:</b> {item["id"]} &nbsp;|&nbsp; 
                            <b>Generated:</b> {item["date"]} &nbsp;|&nbsp; 
                            <b>Agents Deployed:</b> {item["agents_used"]}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            with col2:
                #Three dots menu
                with st.popover("⋮"):
                    st.markdown("**Actions**")

                    if item["status"] == "Completed":
                        st.link_button("📄 View Full Report", url=f"http://localhost:5173/report/{item['id']}", use_container_width=True)
                        st.link_button("⬇️ Download PDF", url=f"http://localhost:8000/api/research/{item['id']}/download", use_container_width=True)
                    else:
                        st.info("Report not generated yet or run failed.")

st.write("")

#change app.py to dashboard
st.markdown("<div class='back-button-wrap' style='position: absolute !important; top: 2rem !important; left: 2rem !important; z-index: 1000 !important; width: auto !important;'>", unsafe_allow_html=True)
if st.button("← Back to Dashboard", key="back_dashboard"):
    st.switch_page("streamlit-app.py")
st.markdown("</div>", unsafe_allow_html=True)