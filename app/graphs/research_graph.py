from typing import TypedDict, List, Dict, Any, Annotated
from langgraph.graph import StateGraph, END
import operator
from app.core import get_run_logger

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

# --- 2. Define the Nodes (Agents) ---
# These are the functions that execute at each step of the graph.

def intake_node(state: ResearchState) -> Dict:
    """Validates and initializes the research request."""
    log = get_run_logger(__name__, state['run_id'])
    log.info(f"INTAKE: Starting research on: {state['topic']}")
    # In a real app, you might fetch initial context here.
    return {"sub_questions": [], "sources": [], "draft": "", "is_verified": False, "error": ""}

def plan_node(state: ResearchState) -> Dict:
    """Breaks the main topic into sub-questions."""
    log = get_run_logger(__name__, state['run_id'])
    log.info("PLANNER: Decomposing topic.")
    # Mock behavior: LLM would normally generate these
    mock_questions = [
        f"What is the history of {state['topic']}?",
        f"What are the current commercial applications of {state['topic']}?"
    ]
    return {"sub_questions": mock_questions}

def research_node(state: ResearchState) -> Dict:
    """Simulates parallel web research for the sub-questions."""
    log = get_run_logger(__name__, state['run_id'])
    log.info(f"RESEARCHER: Gathering sources for {len(state['sub_questions'])} questions.")
    
    try:
        # Mock behavior: Web scraper would fetch this data
        mock_sources = [
            {"url": "https://example.com/1", "title": "Overview", "snippet": "Data about the topic."},
            {"url": "https://example.com/2", "title": "Market Analysis", "snippet": "Commercial viability stats."}
        ]
    except Exception as e:
        log.error(f"Tavily search exception: {e}", exc_info=True)
        raise e
        
    # Because we used Annotated[..., operator.add] in the state, this will append to the list
    return {"sources": mock_sources}

def synthesize_node(state: ResearchState) -> Dict:
    """Drafts the initial report from the gathered sources."""
    log = get_run_logger(__name__, state['run_id'])
    log.info(f"SYNTHESIZER: Writing draft using {len(state['sources'])} sources.")
    mock_draft = f"# Draft Report: {state['topic']}\n\nBased on {len(state['sources'])} sources, this is the initial draft."
    return {"draft": mock_draft}

def verify_node(state: ResearchState) -> Dict:
    """Checks the draft for hallucinations or unsupported claims."""
    log = get_run_logger(__name__, state['run_id'])
    log.info("VERIFIER: Checking factual consistency.")
    # Mock behavior: LLM would check draft against sources
    is_good = True 
    return {"is_verified": is_good}

def render_node(state: ResearchState) -> Dict:
    """Finalizes the text content for PDF generation."""
    log = get_run_logger(__name__, state['run_id'])
    log.info("RENDERER: Finalizing report structure.")
    final_text = state["draft"] + "\n\n## Conclusion\nEverything looks verified."
    return {"final_report": final_text}

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