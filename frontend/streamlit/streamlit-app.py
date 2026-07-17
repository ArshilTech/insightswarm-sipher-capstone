import streamlit as st

st.set_page_config(
    page_title="InsightSwarm - Activity Dashboard",
    page_icon="favicon.svg",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------- Styling ----------
st.markdown(
    """
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    
    <!-- 3D Card Tilt Engine -->
    <script>
        const init3dTilt = () => {
            const cards = document.querySelectorAll('.feature-card');
            cards.forEach(card => {
                if (card.dataset.tiltInitialized === 'true') return;
                card.dataset.tiltInitialized = 'true';
                
                const parent = card.parentElement;
                if (parent) {
                    parent.style.perspective = '1000px';
                }
                card.style.transformStyle = 'preserve-3d';
                
                card.addEventListener('mousemove', (e) => {
                    const rect = card.getBoundingClientRect();
                    const x = e.clientX - rect.left;
                    const y = e.clientY - rect.top;
                    
                    const centerX = rect.width / 2;
                    const centerY = rect.height / 2;
                    
                    // Max rotation of 5 degrees for a subtle and premium feel
                    const rotateX = ((centerY - y) / centerY) * 5;
                    const rotateY = ((x - centerX) / centerX) * 5;
                    
                    card.style.transition = 'transform 0.08s ease, box-shadow 0.3s ease';
                    card.style.transform = `translateY(-8px) scale(1.035) rotateX(${rotateX}deg) rotateY(${rotateY}deg)`;
                });
                
                card.addEventListener('mouseleave', () => {
                    card.style.transition = 'transform 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275), box-shadow 0.4s ease';
                    card.style.transform = 'translateY(0) scale(1) rotateX(0deg) rotateY(0deg)';
                });
            });
        };
        
        // Safely check and initialize
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', init3dTilt);
        } else {
            init3dTilt();
        }
        
        // Streamlit redraws sections on rerun; poll to bind to any new DOM elements
        setInterval(init3dTilt, 1000);
    </script>
    
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

        .metric-card {
            background: var(--surface);
            border: 1px solid var(--line);
            border-radius: var(--radius-md);
            padding: 1.1rem 1.3rem;
            box-shadow: var(--shadow-sm);
            backdrop-filter: blur(14px);
        }

        .metric-label {
            color: var(--ink-soft);
            font-size: 0.88rem;
            margin-bottom: 0.25rem;
            font-family: var(--font-body) !important;
        }

        .metric-value {
            color: var(--ink) !important;
            font-size: 1.5rem;
            font-weight: 700;
            line-height: 1.1;
            font-family: var(--font-display) !important;
        }

        .metric-note {
            color: var(--ink-mute);
            font-size: 0.86rem;
            margin-top: 0.25rem;
            font-family: var(--font-body) !important;
        }

        /* Glassmorphism Cards with Soft Inset Clay Highlights */
        .feature-card {
            display: flex;
            flex-direction: column;
            align-items: center;
            text-align: center;
            background: rgba(255, 255, 255, 0.72);
            border: 1px solid rgba(7, 46, 42, 0.08);
            border-radius: var(--radius-lg);
            padding: 2.5rem 2rem;
            box-shadow:
                var(--shadow-lg),
                inset -8px -8px 16px rgba(7, 46, 42, 0.04),
                inset 8px 8px 16px #ffffff;
            min-height: 420px;
            height: 100%;
            backdrop-filter: blur(20px);
            transition: transform 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275), box-shadow 0.4s ease, border-color 0.4s ease;
        }

        .feature-card:hover {
            transform: translateY(-8px) scale(1.025);
            border-color: rgba(13, 148, 136, 0.3);
            box-shadow:
                0 38px 75px -14px rgba(13, 148, 136, 0.38),
                inset -10px -10px 20px rgba(7, 46, 42, 0.06),
                inset 10px 10px 20px #ffffff;
        }

        .card-icon {
            font-size: 2.6rem;
            width: 5rem;
            height: 5rem;
            border-radius: var(--radius-md);
            background: var(--surface-raised);
            border: 1px solid var(--line);
            display: flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 1.5rem;
            flex-shrink: 0;
            box-shadow:
                inset 3px 3px 8px rgba(7, 46, 42, 0.05),
                inset -2px -2px 6px #ffffff,
                var(--shadow-sm);
        }

        .card-title {
            color: var(--ink) !important;
            font-size: 1.5rem;
            font-weight: 700;
            margin-bottom: 0.75rem;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
            font-family: var(--font-display) !important;
        }

        .card-desc {
            color: var(--ink-soft);
            font-size: 1rem;
            line-height: 1.7;
            margin-bottom: 2rem;
            flex-grow: 1;
            font-family: var(--font-body) !important;
        }

        /* Tactile Action Button matching Landing Page Gradient */
        .card-btn {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            border-radius: var(--radius-md);
            border: none;
            background: var(--grad-a);
            color: #ffffff !important;
            padding: 0.9rem 2.2rem;
            font-family: var(--font-display) !important;
            font-weight: 600;
            font-size: 0.98rem;
            text-decoration: none !important;
            cursor: pointer;
            white-space: nowrap;
            width: 100%;
            box-shadow:
                0 8px 20px -8px rgba(13, 148, 136, 0.4),
                inset -4px -4px 8px rgba(7, 46, 42, 0.15),
                inset 4px 4px 8px rgba(255, 255, 255, 0.3);
            transition: all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94);
        }

        .card-btn:hover {
            transform: translateY(-2px) scale(1.015);
            box-shadow:
                0 12px 26px -8px rgba(13, 148, 136, 0.5),
                inset -5px -5px 10px rgba(7, 46, 42, 0.2),
                inset 5px 5px 10px rgba(255, 255, 255, 0.4);
        }

        .card-btn:active {
            transform: translateY(0) scale(0.985);
            box-shadow:
                0 4px 10px rgba(13, 148, 136, 0.3),
                inset 0 2px 4px rgba(0, 0, 0, 0.1);
        }

        .card-btn.disabled {
            background: #e2ece9 !important;
            color: #8fa39e !important;
            box-shadow:
                inset -3px -3px 6px rgba(0, 0, 0, 0.02),
                inset 3px 3px 6px #ffffff !important;
            cursor: not-allowed;
        }

        .feature-badge {
            display: inline-block;
            padding: 0.25rem 0.6rem;
            border-radius: 999px;
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.04em;
            text-transform: uppercase;
        }

        .badge-soon {
            background: rgba(7, 46, 42, 0.05);
            color: var(--ink-soft);
            border: 1px solid var(--line);
        }

        .footer-note {
            text-align: center;
            color: var(--ink-mute);
            font-size: 0.9rem;
            margin-top: 1.5rem;
            padding-top: 0.8rem;
            position: relative;
            z-index: 10;
        }

        .divider {
            height: 1px;
            background: linear-gradient(90deg, transparent, rgba(13, 148, 136, 0.28), transparent);
            margin: 1.25rem 0;
            position: relative;
            z-index: 10;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- Header ----------
st.markdown(
    """
    <div class="hero" style="text-align: center; padding: 1.5rem 1rem 0.75rem 1rem; margin-bottom: 1rem; position: relative; z-index: 10;">
        <h1 style="font-family: 'Space Grotesk', sans-serif !important; font-size: 3.2rem; line-height: 1.1; margin-bottom: 0.5rem; color: #072e2a !important; font-weight: 700; letter-spacing: -0.03em; text-align: center;">Activity Dashboard</h1>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

# ---------- Feature panels ----------
col1, col2 = st.columns(2)

with col1:
    st.markdown(
        """
        <div class="feature-card">
            <div class="card-icon">🤖</div>
            <div class="card-title">Agents Tracker</div>
            <div class="card-desc">Monitor and trace your multi-agent research pipeline execution in real time. Filter logs by run ID, level, or keywords.</div>
            <a href="/agentstracker" target="_self" class="card-btn">Launch Tracker</a>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        """
        <div class="feature-card">
            <div class="card-icon">🕥</div>
            <div class="card-title">Research History</div>
            <div class="card-desc">Browse and search through your team's historical research reports, logs, and generated PDF documents.</div>
            <a href="#" class="card-btn">Watch History</a>
        </div>
        """,
        unsafe_allow_html=True,
    )



st.markdown("<div class='divider'></div>", unsafe_allow_html=True)