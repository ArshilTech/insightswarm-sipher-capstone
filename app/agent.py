
import os
import tempfile
from dotenv import load_dotenv
# data processing and db
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
#tools and agent for orchestration
from langchain_community.tools import TavilySearchResults
from langchain.tools.retriever import create_retriever_tool
from langchain_groq import ChatGroq
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate
from langchain_huggingface import HuggingFaceEmbeddings

#---load env variable 
load_dotenv()

embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

FAISS_INDEX_PATH = "faiss_pdf_index"

#pdf processing logic
def process_pdf_to_db(file_bytes: bytes):
    """
    Takes the uploaded PDF, extracts the text, splits it, and saves it to FAISS.
    """

    # writing bytes to a temp file so PyPDFLoader can read it
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        temp_file.write(file_bytes)
        temp_file_path = temp_file.name

    try:
        # load the pdf
        loader = PyPDFLoader(temp_file_path)
        documents = loader.load()

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = text_splitter.split_documents(documents)

        # Save to FAISS vector store (replaces SQLiteVSS)
        vector_store = FAISS.from_documents(
            documents=chunks,
            embedding=embeddings,
        )
        vector_store.save_local(FAISS_INDEX_PATH)
        print(f"✅ Successfully saved {len(chunks)} chunks to FAISS.")

    finally:
        # Clean up the temporary file so it doesn't clog your system
        os.remove(temp_file_path)


# --- 3. AGENT LOGIC ---
def ask_agent_question(user_question: str) -> str:
    """
    Initializes Llama, equips it with Tavily and FAISS tools, and generates an answer.
    """
    # 1. Setup the Database Retriever Tool
    vector_store = FAISS.load_local(
        FAISS_INDEX_PATH,
        embeddings,
        allow_dangerous_deserialization=True,
    )
    # Fetch the top 3 most relevant chunks from the DB
    retriever = vector_store.as_retriever(search_kwargs={"k": 3})
    
    # Wrap the database in a LangChain Tool so Llama knows how to use it
    pdf_search_tool = create_retriever_tool(
        retriever,
        name="pdf_database_search",
        description="Search this tool to find information from the user's uploaded PDF report. Use this FIRST if the user asks about the document, report, or uploaded file."
    )

    # 2. Setup the Web Search Tool (Uses TAVILY_API_KEY from .env)
    web_search_tool = TavilySearchResults(max_results=3)

    # 3. Equip the Agent
    tools = [pdf_search_tool, web_search_tool]

    # Initialize the Llama model (using Groq for speed)
    llm = ChatGroq(
        model="llama3-8b-8192",
        temperature=0.2
    )

    # 4. Give the agent its instructions
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert AI reporter. You have access to a PDF database and the live internet. Use the pdf_database_search tool to answer questions about the uploaded report. Use the web_search_tool to find outside or current information."),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),  # Required for the agent's internal reasoning
    ])

    # 5. Compile and Run
    agent = create_tool_calling_agent(llm, tools, prompt)
    # verbose=True lets you see the agent's thought process in the terminal
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

    # Execute the agent
    result = agent_executor.invoke({"input": user_question})
    
    return result["output"]


# --- 4. LOCAL TESTING BLOCK ---
# This code only runs if you execute `python agent.py` directly in the terminal.
if __name__ == "__main__":
    print("--- Testing Backend ---")
    
    # To test PDF uploading, make sure you have a real PDF named "sample.pdf" in the same folder
    test_pdf_path = "sample.pdf"
    
    if os.path.exists(test_pdf_path):
        print(f"Found {test_pdf_path}, processing into FAISS...")
        with open(test_pdf_path, "rb") as f:
            pdf_bytes = f.read()
        process_pdf_to_db(pdf_bytes)
    else:
        print(f"⚠️ {test_pdf_path} not found. Skipping PDF upload test. The agent will only be able to use Tavily until you upload a file.")

    # Test the agent's reasoning
    print("\nAsking the agent a test question...")
    test_question = "What is the main topic of the uploaded PDF? If there is no PDF, use the web to tell me the current weather in New York."
    answer = ask_agent_question(test_question)
    print(f"\n🤖 Agent Answer: {answer}")