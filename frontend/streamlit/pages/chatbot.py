from sentence_transformers.util import similarity
from pathlib import Path
import os
import streamlit as st
import requests
#document loader
from langchain_community.document_loaders import PyPDFLoader
#vector store
from langchain_community.vectorstores import Chroma
#llm
from langchain_groq import ChatGroq
# Embeddings
from langchain_community.embeddings.sentence_transformer import (
    SentenceTransformerEmbeddings,
)


FAVICON_PATH = Path(__file__).resolve().parent.parent / "favicon.svg"

#change app.py to dashboard
st.markdown("<div class='back-button-wrap' style='position: absolute !important; top: 2rem !important; left: 2rem !important; z-index: 1000 !important; width: auto !important;'>", unsafe_allow_html=True)
if st.button("← Back to Dashboard", key="back_dashboard"):
    st.switch_page("streamlit-app.py")
st.markdown("</div>", unsafe_allow_html=True)

#-------Page Config------
st.set_page_config(
    page_title="Comb - InsightSwarm's AI Assistant",
    page_icon=str(FAVICON_PATH),
    layout="wide",
    initial_sidebar_state="collapsed",
)


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


        /* User message — align RIGHT */
        .stChatMessage:has([data-testid="stChatMessageAvatarUser"]),
        [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
            margin-left: 15% !important;
            margin-right: 0 !important;
            border-left: none !important;
            border-right: 3px solid #0d9488 !important;
            flex-direction: row-reverse !important;
            text-align: right !important;
        }

        .stChatMessage:has([data-testid="stChatMessageAvatarUser"]) p,
        [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) p {
            text-align: right !important;
        }

        /* Assistant message — align LEFT */
        .stChatMessage:has([data-testid="stChatMessageAvatarAssistant"]),
        [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) {
            margin-right: 15% !important;
            margin-left: 0 !important;
            border-left: 3px solid #7dd3c7 !important;
            border-right: none !important;
            text-align: left !important;
        }

        .stChatMessage:has([data-testid="stChatMessageAvatarAssistant"]) p,
        [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) p {
            text-align: left !important;
        }

        /* Chat message text styling */
        .stChatMessage p,
        .stChatMessage span,
        [data-testid="stChatMessage"] p,
        [data-testid="stChatMessage"] span {
            font-family: var(--font-body) !important;
            color: #072e2a !important;
            font-size: 0.95rem !important;
            line-height: 1.65 !important;
        }

        /* Chat input bar styling */
        [data-testid="stChatInput"] {
            border-radius: 18px !important;
        }

        [data-testid="stChatInput"] textarea {
            font-family: var(--font-body) !important;
            background: #ffffff !important;
            background-color: #ffffff !important;
            border: 1px solid rgba(7, 46, 42, 0.1) !important;
            border-radius: 12px !important;
            box-shadow: 0 1px 2px rgba(7, 46, 42, 0.05), 0 8px 20px -10px rgba(13, 148, 136, 0.25) !important;
        }

        [data-testid="stChatInput"] textarea:focus {
            border-color: #0d9488 !important;
            box-shadow: 0 0 0 3px rgba(13, 148, 136, 0.15) !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

#-----Page Header-----------
st.markdown(
    """
    <div class="hero">
    <h1>COMB</h1>
    <p>Welcome to Comb, InsightSwarm's AI Assistant. Turn Static Reports into Dynamic Conversations.</p>
    </div>
    <div class="divider"></div>
""", unsafe_allow_html=True
)

import tempfile
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import PromptTemplate
from langchain_classic.chains import RetrievalQA
from dotenv import load_dotenv

load_dotenv()

st.markdown("### 📄 PDF Document Assistant")
uploaded_file = st.file_uploader("Upload a PDF document to analyze and ask questions:", type=["pdf"])

# Split documents into chunks
def split_docs(documents, chunk_size=500, chunk_overlap=100):
  text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
  docs = text_splitter.split_documents(documents)
  return docs

if uploaded_file is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_path = tmp_file.name

    try:
        with st.spinner("Processing PDF and indexing document content..."):
            loader = PyPDFLoader(tmp_path)
            documents = loader.load()

            new_pages = split_docs(documents)

            embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
            db = Chroma.from_documents(new_pages, embeddings)

            retriever = db.as_retriever(similarity_score_threshold = 0.9)

            llm_model = os.getenv("LLM_MODEL", "meta-llama/llama-prompt-guard-2-22m")
            llm = ChatGroq(model=llm_model, temperature=0.2)

            prompt_template = """You are a helpful AI assistant. Use the following context from the uploaded PDF document to answer the user's question clearly and concisely. If the answer cannot be found in the context, state that clearly.

                                Context:
                                {context}

                                Question:
                                {question}"""
            
            PROMPT = PromptTemplate(template = f"[INST] {prompt_template} [/INST]", input_variables=["context", "question"])

            qa_chain = RetrievalQA.from_chain_type(
                llm = llm,
                chain_type='stuff',
                retriever= retriever,
                input_key = 'query',
                return_source_documents = True,
                chain_type_kwargs={"prompt":PROMPT}
            )

        st.success(f"Successfully indexed!")

        if "messages" not in st.session_state:
            st.session_state["messages"] = []

        for msg in st.session_state["messages"]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # Visible fallback input (always rendered) so users always have a clear box to type in.
        col_q, col_btn = st.columns([8, 1])
        query = col_q.chat_input(placeholder="Type your question here and press Ask")

        if query:
            st.session_state["messages"].append({"role": "user", "content": query})
            with st.chat_message("user"):
                st.markdown(query)

            with st.chat_message("assistant"):
                with st.spinner("Analyzing document content..."):
                    res = qa_chain(query)
                    answer = res.get("result", "Sorry, I could not generate an answer.")
                    st.markdown(answer)
                    st.session_state["messages"].append({"role": "assistant", "content": answer})

    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
else:
    st.info("💡 Please upload a PDF document above to start asking questions!")



