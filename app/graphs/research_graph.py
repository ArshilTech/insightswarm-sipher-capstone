from typing import TypedDict, List, Dict, Any, Annotated
from langgraph.graph import StateGraph, END
import operator
import os
from langchain_tavily import TavilySearch
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
from app.core import get_run_logger

load_dotenv()

# --- Initializations ---
llm_model = os.getenv("LLM_MODEL", "meta-llama/llama-prompt-guard-2-22m")
llm = ChatGroq(model=llm_model, temperature=0)

# Initialize the Tavily Search Tool
tavily_search = TavilySearch(
    max_results=int(os.getenv("TAVILY_MAX_RESULTS", "3")),
    topic=os.getenv("TAVILY_TOPIC", "general"),
    search_depth=os.getenv("TAVILY_SEARCH_DEPTH", "basic")
)

# --- 1. Define the State ---
# This is the shared memory object passed between every node.
class ResearchState(TypedDict):
    run_id: str
    topic: str
    instructions: str
    depth: str
    
    # State populated by agents as the graph runs
    sub_questions: List[str]
    sources: Annotated[List[Dict[str, Any]], operator.add] # Append-only list for sources
    draft: str
    is_verified: bool
    final_report: str
    error: str
    retry_count: int

# --- 2. Define the Nodes (Agents) ---
# These are the functions that execute at each step of the graph.

def intake_node(state: ResearchState) -> Dict:
    """Validates and initializes the research request."""
    log = get_run_logger(__name__, state['run_id'])
    log.info(f"INTAKE: Starting research on: {state['topic']}")
    # In a real app, you might fetch initial context here.
    return {"sub_questions": [], "sources": [], "draft": "", "is_verified": False, "error": "", "retry_count": 0}

def plan_node(state: ResearchState) -> Dict:
    """Uses the LLM to break the main topic into sub-questions."""
    log = get_run_logger(__name__, state['run_id'])
    log.info("PLANNER: Decomposing topic.")

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a research planner. Break the user's topic down into 3 targeted search queries. Return ONLY the queries separated by newlines."),
        ("user", "Topic: {topic}\nInstructions: {instructions}")
    ])

    chain = prompt | llm | StrOutputParser()
    result = chain.invoke({"topic": state["topic"], "instructions": state["instructions"]})

    # Split the response by newline to create our list of sub-questions
    questions = [q.strip() for q in result.split('\n') if q.strip()]

    return {"sub_questions": questions}

def research_node(state: ResearchState) -> Dict:
    """Uses Tavily to search the web for each sub-question."""
    log = get_run_logger(__name__, state['run_id'])
    log.info(f"RESEARCHER: Gathering sources for {len(state['sub_questions'])} questions.")
    
    all_sources = []
    for question in state["sub_questions"]:
        log.info(f"Searching for: {question}")

        try:
            results = tavily_search.invoke({"query": question})
            
            # Extract the raw data returned by Tavily
            if isinstance(results, list):
                for res in results:
                    all_sources.append({
                        "url": res.get("url", ""),
                        "title": res.get("title", ""),
                        "content": res.get("content", "")
                    })
        except Exception as e:
            log.error(f"Error during Tavily search: {e}", exc_info=True)
            state["error"] += f"Error during search for '{question}': {e}\n"
    
    # Because we used Annotated[..., operator.add] in the state, this will append to the list
    return {"sources": all_sources}

def synthesize_node(state: ResearchState) -> Dict:
    """Uses an LLM to draft the report based on gathered sources."""
    log = get_run_logger(__name__, state['run_id'])
    log.info(f"SYNTHESIZER: Writing draft using {len(state['sources'])} sources.")

    # Format sources into a readable context block for the LLM
    context = ""
    for i, src in enumerate(state['sources']):
        context += f"Source {i+1}: {src['title']} ({src['url']})\n{src['content']}\n\n"
        
    prompt = ChatPromptTemplate.from_messages([
        ("system", r"""You are an expert researcher. Use the provided sources to write a detailed, structured report in Markdown. 
        Include inline citations to the sources where appropriate (e.g., [1], [2]).
        
        CRITICAL INSTRUCTIONS:
        1. NO CONVERSATIONAL FILLER: Output ONLY the final Markdown report. Do not include any internal thinking, reasoning, or introductory phrases (e.g., "Okay, the user wants me to...", "Here is the report..."). Start directly with the title (#).
        2. NO LATEX: Do not use LaTeX formatting (such as $ or $$ delimiters) for math or physics equations. WeasyPrint cannot render it. You MUST use plain text Unicode characters instead (e.g., write |ψ⟩ = α|0⟩ + β|1⟩ instead of $\psi\rangle = \alpha|0\rangle + \beta|1\rangle$).
        """),
        ("user", "Topic: {topic}\nInstructions: {instructions}\n\nSources:\n{context}")
    ])

    chain = prompt | llm | StrOutputParser()
    draft = chain.invoke({
        "topic": state["topic"],
        "instructions": state["instructions"],
        "context": context
    })

    return {"draft": draft}

def verify_node(state: ResearchState) -> Dict:
    """Checks the draft for hallucinations or unsupported claims."""
    log = get_run_logger(__name__, state['run_id'])
    log.info("VERIFIER: Checking factual consistency.")
    
    if not state.get("sources"):
        log.info("VERIFIER: No sources available, marking as verified.")
        return {"is_verified": True}
    
    # Format sources for the LLM to reference
    source_titles = [src.get("title", "") for src in state["sources"]]
    sources_str = "\n".join(source_titles)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a fact-checker. Review the draft against the provided sources and respond with ONLY 'VERIFIED' if the claims are supported, or 'NEEDS_REVISION' if you find unsupported claims or hallucinations."),
        ("user", "Draft:\n{draft}\n\nSource Titles:\n{sources}")
    ])
    
    chain = prompt | llm | StrOutputParser()
    result = chain.invoke({
        "draft": state["draft"],
        "sources": sources_str
    }).strip().upper()
    
    is_good = "VERIFIED" in result
    log.info(f"VERIFIER: Result = {result} (is_verified={is_good})")

    if is_good:
        return {"is_verified": is_good}

    # Only increment on failure so retry_count reflects actual revision attempts
    return {"is_verified": is_good, "retry_count": state.get("retry_count", 0) + 1}

def render_node(state: ResearchState) -> Dict:
    """Prepares the drafted Markdown for HTML/PDF rendering later."""
    log = get_run_logger(__name__, state['run_id'])
    log.info("RENDERER: Storing final markdown report.")

    return {"final_report": state["draft"]}

MAX_VERIFICATION_RETRIES = 2

# --- 3. Build the Graph ---

def build_research_graph():
    builder = StateGraph(ResearchState)

    # Add all nodes to the graph
    builder.add_node("intake", intake_node)
    builder.add_node("planner", plan_node)
    builder.add_node("researcher", research_node)
    builder.add_node("synthesizer", synthesize_node)
    builder.add_node("verifier", verify_node)
    builder.add_node("renderer", render_node)

    # Define the edges (the flow of execution)
    builder.set_entry_point("intake")
    builder.add_edge("intake", "planner")
    builder.add_edge("planner", "researcher")
    builder.add_edge("researcher", "synthesizer")
    builder.add_edge("synthesizer", "verifier")

    # Add a conditional edge: If verification fails, we could route back to researcher/synthesizer
    def check_verification(state: ResearchState):
        log = get_run_logger(__name__, state['run_id'])
        if state.get("is_verified", False):
            return "renderer"
        elif state.get("retry_count", 0) >= MAX_VERIFICATION_RETRIES:
            log.warning(
                f"VERIFIER: Max retries ({MAX_VERIFICATION_RETRIES}) reached. "
                "Forcing render with unverified draft."
            )
            return "renderer"
        else:
            # If it failed, send it back to the synthesizer to fix
            log.warning("VERIFIER FAILED: Routing back to synthesizer.")
            return "synthesizer"

    builder.add_conditional_edges("verifier", check_verification)

    # End the graph after rendering
    builder.add_edge("renderer", END)

    # Compile the graph into a runnable object
    return builder.compile()

# Instantiate the graph so it can be imported elsewhere
research_graph = build_research_graph()
