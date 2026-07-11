from typing import TypedDict, List, Dict, Any, Annotated
from langgraph.graph import StateGraph, END
import operator
import os
from langchain_tavily import TavilySearch
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# --- Initializations ---
llm = ChatGroq(model='qwen/qwen3-32b', temperature=0)

# Initialize the Tavily Search Tool
tavily_search = TavilySearch(
    max_results=3,      # Limits the number of results per sub-question to save tokens
    topic="general",    # Category of the search
    search_depth="basic" # Depth of the search
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

# --- 2. Define the Nodes (Agents) ---
# These are the functions that execute at each step of the graph.

def intake_node(state: ResearchState) -> Dict:
    """Validates and initializes the research request."""
    print(f"[{state['run_id']}] INTAKE: Starting research on: {state['topic']}")
    # In a real app, you might fetch initial context here.
    return {"sub_questions": [], "sources": [], "draft": "", "is_verified": False, "error": ""}

def plan_node(state: ResearchState) -> Dict:
    """Uses the LLM to break the main topic into sub-questions."""
    print(f"[{state['run_id']}] PLANNER: Decomposing topic.")

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
    print(f"[{state['run_id']}] RESEARCHER: Gathering sources for {len(state['sub_questions'])} questions.")
    
    all_sources = []
    for question in state["sub_questions"]:
        print(f"[{state['run_id']}] Searching for: {question}")

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
            print(f"[{state['run_id']}] Error during Tavily search: {e}")
            state["error"] += f"Error during search for '{question}': {e}\n"
    
    # Because we used Annotated[..., operator.add] in the state, this will append to the list
    return {"sources": all_sources}

def synthesize_node(state: ResearchState) -> Dict:
    """Uses an LLM to draft the report based on gathered sources."""
    print(f"[{state['run_id']}] SYNTHESIZER: Writing draft using {len(state['sources'])} sources.")

    # Format sources into a readable context block for the LLM
    context = ""
    for i, src in enumerate(state['sources']):
        context += f"Source {i+1}: {src['title']} ({src['url']})\n{src['content']}\n\n"
        
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert researcher. Use the provided sources to write a detailed, structured report in Markdown. Include inline citations to the sources where appropriate (e.g., [1], [2])."),
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
    print(f"[{state['run_id']}] VERIFIER: Checking factual consistency.")
    # Mock behavior: LLM would check draft against sources
    is_good = True 
    return {"is_verified": is_good}

def render_node(state: ResearchState) -> Dict:
    """Prepares the drafted Markdown for HTML/PDF rendering later."""
    print(f"[{state['run_id']}] RENDERER: Storing final markdown report.")

    # Since we are using WeasyPrint later, we will eventually inject an HTML conversion step here.

    return {"final_report": state["draft"]}

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
        if state.get("is_verified", False):
            return "renderer"
        else:
            # If it failed, send it back to the synthesizer to fix
            print(f"[{state['run_id']}] VERIFIER FAILED: Routing back to synthesizer.")
            return "synthesizer"

    builder.add_conditional_edges("verifier", check_verification)

    # End the graph after rendering
    builder.add_edge("renderer", END)

    # Compile the graph into a runnable object
    return builder.compile()

# Instantiate the graph so it can be imported elsewhere
research_graph = build_research_graph()