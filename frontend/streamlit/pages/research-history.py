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
    
    <style>
        .stApp {
            background: linear-gradient(135deg, #E7F6F1 0%, #DDF1EA 45%, #D3EDE3 100%);
            color: #1F2937;
        }

        [data-testid="stSidebar"] {
            display: none;
        }

        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 1200px;
        }

        .hero {
            text-align: center;
            padding: 1.5rem 1rem 0.75rem 1rem;
            margin-bottom: 1rem;
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
            margin-bottom: 1rem;
        }

        .section-title {
            color: #0F2A22;
            font-weight: 800;
            font-size: 1.35rem;
            margin: 0.5rem 0 0.25rem 0;
        }

        .section-subtitle {
            color: #5B6E68;
            margin-bottom: 1rem;
        }

        .metric-card {
            background: rgba(255, 255, 255, 0.75);
            border: 1px solid rgba(15, 118, 110, 0.15);
            border-radius: 20px;
            padding: 1rem 1.1rem;
            box-shadow: 0 18px 45px rgba(15, 60, 50, 0.10);
            backdrop-filter: blur(14px);
        }

        .metric-label {
            color: #6B7C77;
            font-size: 0.88rem;
            margin-bottom: 0.25rem;
        }

        .metric-value {
            color: #0F2A22;
            font-size: 1.5rem;
            font-weight: 800;
            line-height: 1.1;
        }

        .metric-note {
            color: #4B5D57;
            font-size: 0.86rem;
            margin-top: 0.25rem;
        }

        .feature-card {
            height: 100%;
            background: rgba(255, 255, 255, 0.80);
            border: 1px solid rgba(15, 118, 110, 0.15);
            border-radius: 24px;
            padding: 1.35rem;
            box-shadow: 0 20px 55px rgba(15, 60, 50, 0.12);
            backdrop-filter: blur(16px);
            transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
        }

        .feature-card:hover {
            transform: translateY(-4px);
            border-color: rgba(15, 118, 110, 0.35);
            box-shadow: 0 26px 65px rgba(15, 60, 50, 0.16);
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
            background: rgba(15, 118, 110, 0.14);
            color: #0F766E;
            border: 1px solid rgba(15, 118, 110, 0.28);
        }

        .badge-soon {
            background: rgba(15, 42, 34, 0.06);
            color: #5B6E68;
            border: 1px solid rgba(15, 42, 34, 0.12);
        }

        .feature-title {
            color: #0F2A22;
            font-size: 1.25rem;
            font-weight: 800;
            margin-bottom: 0.35rem;
        }

        .feature-desc {
            color: #4B5D57;
            line-height: 1.7;
            font-size: 0.98rem;
            min-height: 3.3rem;
        }

        .feature-meta {
            color: #6B7C77;
            font-size: 0.85rem;
            margin-top: 0.7rem;
        }

        .cta-wrap {
            margin-top: 1rem;
        }

        .footer-note {
            text-align: center;
            color: #5B6E68;
            font-size: 0.9rem;
            margin-top: 1.5rem;
            padding-top: 0.8rem;
        }

        .divider {
            height: 1px;
            background: linear-gradient(90deg, transparent, rgba(15, 118, 110, 0.28), transparent);
            margin: 1.25rem 0;
        }

        /* Streamlit button tweaks */
        div.stButton > button {
            width: 100%;
            border-radius: 14px;
            border: 1px solid rgba(15, 118, 110, 0.35);
            background: linear-gradient(135deg, #14B8A6 0%, #0F766E 100%);
            color: white;
            padding: 0.7rem 1rem;
            font-weight: 700;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
            box-shadow: 0 10px 25px rgba(15, 118, 110, 0.25);
        }

        div.stButton > button:hover {
            transform: translateY(-1px);
            box-shadow: 0 14px 30px rgba(15, 118, 110, 0.35);
            border-color: rgba(15, 118, 110, 0.55);
        }

        .soon-button button {
            background: rgba(15, 42, 34, 0.05) !important;
            border: 1px solid rgba(15, 42, 34, 0.12) !important;
            box-shadow: none !important;
            color: #5B6E68 !important;
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