from pathlib import Path
import os
import hashlib
import tempfile

import streamlit as st

FAVICON_PATH = Path(__file__).resolve().parent.parent / "favicon.svg"

#-------Page Config (MUST be first Streamlit command)------
st.set_page_config(
    page_title="Comb - InsightSwarm's AI Assistant",
    page_icon=str(FAVICON_PATH),
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Back to Dashboard button at top-left
st.markdown("<div class='back-button-wrap' style='position: absolute !important; top: 2rem !important; left: 2rem !important; z-index: 1000 !important; width: auto !important;'>", unsafe_allow_html=True)
if st.button("← Back to Dashboard", key="back_dashboard"):
    st.switch_page("streamlit-app.py")
st.markdown("</div>", unsafe_allow_html=True)


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
            --surface: rgba(255, 255, 255, 0.75);
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

            --radius-sm: 12px;
            --radius-md: 18px;
            --radius-lg: 24px;
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
            from { opacity: 0; transform: translateY(4px); }
            to   { opacity: 1; transform: translateY(0); }
        }
        .block-container {
            animation: fadeInPage 0.3s ease-out !important;
            padding-top: 2rem;
            padding-bottom: 3rem;
            max-width: 1050px;
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
            padding: 1.5rem 1rem 0.5rem 1rem;
            margin-bottom: 0.5rem;
            position: relative;
            z-index: 10;
        }

        .hero h1 {
            font-size: 3.2rem;
            line-height: 1.15;
            margin-bottom: 0.5rem;
            font-weight: 800;
            letter-spacing: -0.035em;
            font-family: var(--font-display) !important;
            color: #000000 !important;
            -webkit-text-fill-color: #000000 !important;
            display: inline-block;
        }

        .hero p {
            max-width: 750px;
            margin: 0 auto;
            color: var(--ink-soft);
            font-size: 1.05rem;
            line-height: 1.75;
            font-family: var(--font-body) !important;
        }

        /* ===== Divider ===== */
        .divider {
            height: 1px;
            background: linear-gradient(90deg, transparent, rgba(13, 148, 136, 0.3), transparent);
            margin: 1.25rem 0 2rem 0;
            position: relative;
            z-index: 10;
        }

        /* ===== Card Panels & Upload Container ===== */
        .upload-panel-card {
            background: rgba(255, 255, 255, 0.78);
            border: 1px solid rgba(7, 46, 42, 0.1);
            border-radius: var(--radius-lg);
            padding: 1.75rem 2rem;
            box-shadow:
                var(--shadow-md),
                inset 0 1px 0 rgba(255, 255, 255, 0.9);
            backdrop-filter: blur(16px);
            margin-bottom: 1.75rem;
            transition: all 0.3s ease;
        }

        .upload-panel-card:hover {
            box-shadow: var(--shadow-lg);
            border-color: rgba(13, 148, 136, 0.25);
        }

        .file-info-badge {
            display: flex;
            align-items: center;
            justify-content: space-between;
            background: var(--surface-raised);
            border: 1px solid rgba(13, 148, 136, 0.2);
            border-radius: var(--radius-md);
            padding: 1rem 1.4rem;
            margin-top: 0.75rem;
            box-shadow: var(--shadow-sm);
        }

        .file-info-left {
            display: flex;
            align-items: center;
            gap: 0.9rem;
        }

        .file-icon-box {
            width: 2.75rem;
            height: 2.75rem;
            border-radius: var(--radius-sm);
            background: rgba(13, 148, 136, 0.12);
            border: 1px solid rgba(13, 148, 136, 0.25);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.35rem;
            color: var(--teal-600);
        }

        .file-details {
            display: flex;
            flex-direction: column;
        }

        .file-name {
            font-family: var(--font-display) !important;
            font-weight: 700;
            font-size: 1rem;
            color: var(--ink);
        }

        .file-meta {
            font-family: var(--font-mono) !important;
            font-size: 0.78rem;
            color: var(--ink-soft);
        }

        .status-ready-pill {
            display: inline-flex;
            align-items: center;
            gap: 0.4rem;
            padding: 0.3rem 0.75rem;
            border-radius: 999px;
            background: rgba(13, 148, 136, 0.12);
            border: 1px solid rgba(13, 148, 136, 0.28);
            color: var(--teal-700);
            font-family: var(--font-mono) !important;
            font-size: 0.75rem;
            font-weight: 700;
        }

        .status-dot-active {
            width: 7px;
            height: 7px;
            border-radius: 50%;
            background: var(--teal-500);
            box-shadow: 0 0 0 3px rgba(13, 148, 136, 0.2);
            animation: pulse-dot 2s ease-in-out infinite;
        }

        @keyframes pulse-dot {
            0%, 100% { transform: scale(1); opacity: 1; }
            50% { transform: scale(1.25); opacity: 0.7; }
        }

        /* ===== Empty State Card ===== */
        .empty-upload-state {
            text-align: center;
            padding: 2.25rem 1.5rem;
            background: rgba(255, 255, 255, 0.65);
            border: 1.5px dashed rgba(13, 148, 136, 0.3);
            border-radius: var(--radius-lg);
            backdrop-filter: blur(14px);
            margin-top: 1rem;
        }

        .empty-upload-icon {
            font-size: 2.5rem;
            margin-bottom: 0.75rem;
            display: inline-block;
        }

        .empty-upload-title {
            font-family: var(--font-display) !important;
            font-weight: 700;
            font-size: 1.25rem;
            color: var(--ink);
            margin-bottom: 0.35rem;
        }

        .empty-upload-sub {
            font-family: var(--font-body) !important;
            font-size: 0.95rem;
            color: var(--ink-soft);
            max-width: 480px;
            margin: 0 auto;
            line-height: 1.6;
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

        /* ===== Streamlit File Uploader Override ===== */
        [data-testid="stFileUploader"] {
            background: rgba(255, 255, 255, 0.8) !important;
            border-radius: var(--radius-md) !important;
            border: 1px dashed rgba(13, 148, 136, 0.35) !important;
            padding: 1rem !important;
            box-shadow: var(--shadow-sm) !important;
            transition: border-color 0.2s ease, background 0.2s ease !important;
        }

        [data-testid="stFileUploader"]:hover {
            border-color: var(--teal-500) !important;
            background: rgba(255, 255, 255, 0.95) !important;
        }

        [data-testid="stFileUploader"] section {
            background: transparent !important;
        }

        [data-testid="stFileUploader"] button {
            background: var(--grad-a) !important;
            color: white !important;
            border: none !important;
            border-radius: var(--radius-sm) !important;
            font-family: var(--font-display) !important;
            font-weight: 600 !important;
            box-shadow: 0 4px 12px rgba(13, 148, 136, 0.3) !important;
        }

        /* ===== Chat Message Cards (Chat App Style) ===== */
        [data-testid="stChatMessage"] {
            background: #ffffff !important;
            border: 1.5px solid rgba(7, 46, 42, 0.1) !important;
            border-radius: 20px !important;
            padding: 1.25rem 1.5rem !important;
            margin-bottom: 1.25rem !important;
            box-shadow: 0 4px 18px rgba(7, 46, 42, 0.05), 0 1px 3px rgba(0, 0, 0, 0.03) !important;
            backdrop-filter: blur(12px) !important;
            transition: transform 0.2s ease, box-shadow 0.2s ease !important;
        }

        [data-testid="stChatMessage"]:hover {
            box-shadow: 0 6px 24px rgba(7, 46, 42, 0.08) !important;
        }

        /* User Message Card Accent */
        [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]),
        [data-testid="stChatMessage"]:has(span:contains("👤")),
        [data-testid="stChatMessage"]:has(div:contains("👤")) {
            background: #f0fdfa !important;
            border: 1.5px solid rgba(13, 148, 136, 0.3) !important;
            border-right: 5px solid #0d9488 !important;
        }

        /* Assistant Message Card Accent */
        [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]),
        [data-testid="stChatMessage"]:has(span:contains("🤖")),
        [data-testid="stChatMessage"]:has(div:contains("🤖")) {
            background: #ffffff !important;
            border: 1.5px solid rgba(7, 46, 42, 0.08) !important;
            border-left: 5px solid #0d9488 !important;
        }

        .stChatMessage p,
        .stChatMessage span,
        [data-testid="stChatMessage"] p,
        [data-testid="stChatMessage"] span {
            font-family: var(--font-body) !important;
            color: #072e2a !important;
            font-size: 0.97rem !important;
            line-height: 1.7 !important;
        }

        /* Chat input bar styling */
        [data-testid="stChatInput"] {
            border-radius: var(--radius-md) !important;
            box-shadow: var(--shadow-lg) !important;
            background: rgba(255, 255, 255, 0.95) !important;
            backdrop-filter: blur(16px) !important;
            border: 1px solid rgba(13, 148, 136, 0.25) !important;
        }

        [data-testid="stChatInput"] textarea {
            font-family: var(--font-body) !important;
            background: transparent !important;
            border: none !important;
            font-size: 0.96rem !important;
            color: var(--ink) !important;
        }

        [data-testid="stChatInput"] textarea:focus {
            box-shadow: none !important;
        }

        [data-testid="stChatInput"] button {
            background: var(--grad-a) !important;
            color: white !important;
            border-radius: var(--radius-sm) !important;
            border: none !important;
            box-shadow: 0 4px 14px rgba(13, 148, 136, 0.35) !important;
            transition: transform 0.2s ease !important;
        }

        [data-testid="stChatInput"] button:hover {
            transform: scale(1.05) !important;
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
        <h1>Comb</h1>
        <p>Turn static PDF reports into interactive, dynamic conversations with instant semantic search and exact citations.</p>
    </div>
    <div class="divider"></div>
    """,
    unsafe_allow_html=True,
)

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
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import PromptTemplate
from langchain_classic.chains import RetrievalQA
from dotenv import load_dotenv

load_dotenv()


# ---------- Cached resources (survive across Streamlit reruns) ----------

@st.cache_resource(show_spinner=False)
def get_embeddings():
    """Load the SentenceTransformer model once and reuse across reruns."""
    return SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")


def _file_content_hash(file_bytes: bytes) -> str:
    """Return a stable SHA-256 hex digest of the uploaded file content."""
    return hashlib.sha256(file_bytes).hexdigest()


# Split documents into chunks
def split_docs(documents, chunk_size=500, chunk_overlap=100):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    docs = text_splitter.split_documents(documents)
    return docs


@st.cache_resource(show_spinner="Indexing document content…")
def build_qa_chain(_file_hash: str, file_bytes: bytes):
    """Build the Chroma vector store and QA chain, cached by file content hash."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(file_bytes)
        tmp_path = tmp_file.name

    try:
        loader = PyPDFLoader(tmp_path)
        documents = loader.load()
        new_pages = split_docs(documents)

        embeddings = get_embeddings()
        db = Chroma.from_documents(new_pages, embeddings)
        retriever = db.as_retriever(similarity_score_threshold=0.9)

        llm_model = os.getenv("LLM_MODEL", "meta-llama/llama-prompt-guard-2-22m")
        llm = ChatGroq(model=llm_model, temperature=0.2)

        prompt_template = """You are a helpful AI assistant. Use the following context from the uploaded PDF document to answer the user's question clearly and concisely. If the answer cannot be found in the context, state that clearly.

                            Context:
                            {context}

                            Question:
                            {question}"""

        PROMPT = PromptTemplate(
            template=f"[INST] {prompt_template} [/INST]",
            input_variables=["context", "question"],
        )

        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=retriever,
            input_key="query",
            return_source_documents=True,
            chain_type_kwargs={"prompt": PROMPT},
        )
        return qa_chain
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


# ---------- Main UI ----------

st.markdown("##### 📄 PDF Document Analysis")
uploaded_file = st.file_uploader("Upload a research PDF document to analyze:", type=["pdf"])

if uploaded_file is not None:
    file_bytes = uploaded_file.getvalue()
    file_hash = _file_content_hash(file_bytes)
    file_size_kb = len(file_bytes) / 1024.0

    qa_chain = build_qa_chain(file_hash, file_bytes)

    # Render sleek active file card
    st.markdown(
        f"""
        <div class="file-info-badge">
            <div class="file-info-left">
                <div class="file-icon-box">📄</div>
                <div class="file-details">
                    <div class="file-name">{uploaded_file.name}</div>
                    <div class="file-meta">{file_size_kb:.1f} KB · Document Indexed</div>
                </div>
            </div>
            <div class="status-ready-pill">
                <span class="status-dot-active"></span> Ready to Answer
            </div>
        </div>
        <br/>
        """,
        unsafe_allow_html=True,
    )

    if "messages" not in st.session_state:
        st.session_state["messages"] = []

    # Display chat history with explicit custom avatars
    for msg in st.session_state["messages"]:
        avatar_icon = "👤" if msg["role"] == "user" else "🤖"
        with st.chat_message(msg["role"], avatar=avatar_icon):
            st.markdown(msg["content"])

    # Chat input bar
    query = st.chat_input(placeholder="Ask anything about your uploaded document...")

    if query:
        st.session_state["messages"].append({"role": "user", "content": query})
        with st.chat_message("user", avatar="👤"):
            st.markdown(query)

        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("Analyzing document and generating answer..."):
                res = qa_chain(query)
                answer = res.get("result", "Sorry, I could not generate an answer.")
                st.markdown(answer)
                st.session_state["messages"].append({"role": "assistant", "content": answer})

else:
    # Render modern empty state
    st.markdown(
        """
        <div class="empty-upload-state">
            <div class="empty-upload-icon">📑</div>
            <div class="empty-upload-title">No Document Uploaded Yet</div>
            <div class="empty-upload-sub">
                Upload any PDF research paper or report above. Comb will index its contents in seconds and allow you to ask targeted questions.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
