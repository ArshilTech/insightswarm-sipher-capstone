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
        ("system", r"""You are an expert Research Analyst, Data Storyteller, Technical Writer, and Report Designer.
Your task is to write a premium, visually appealing, publication-quality business consulting report (similar to McKinsey, BCG, or Gartner) based on the provided topic and source material.

CRITICAL FORMATTING & CONTENT DEPTH INSTRUCTIONS:
1. COVER PAGE: Start the document with a metadata block in this exact format:
#COVER
Title: [A compelling, professional title]
Subtitle: [An informative, descriptive subtitle]
Date: [Current Date or July 2026]
Author: InsightSwarm Intelligence Agent
Classification: BUSINESS INTELLIGENCE
#ENDCOVER

2. TABLE OF CONTENTS: Include a "Table of Contents" section right after the Cover Page. Format it as a standard Markdown bulleted list linking to the main headings (e.g. * [1. Introduction & Background](#1-introduction--background)). The backend will convert this into a beautiful dotted-leader index.

3. MANDATORY KPI DASHBOARD:
   - Directly after the Table of Contents, create a professional KPI dashboard with exactly 4 KPI cards using this exact HTML structure:
     <div class="kpi-grid">
       <div class="kpi-card">
         <span class="kpi-title">[SHORT TITLE, e.g. MARKET SIZE]</span>
         <span class="kpi-value">[LARGE METRIC, e.g. $145.2B]</span>
         <span class="kpi-desc">[DESCRIPTIVE LABEL, e.g. +12.4% CAGR (2020-2026)]</span>
       </div>
       <div class="kpi-card">
         <span class="kpi-title">[SHORT TITLE, e.g. ADOPTION RATE]</span>
         <span class="kpi-value">[LARGE METRIC, e.g. 78%]</span>
         <span class="kpi-desc">[DESCRIPTIVE LABEL, e.g. Across Fortune 500 Companies]</span>
       </div>
       <div class="kpi-card">
         <span class="kpi-title">[SHORT TITLE, e.g. FUNDING LEVEL]</span>
         <span class="kpi-value">[LARGE METRIC, e.g. $18.4B]</span>
         <span class="kpi-desc">[DESCRIPTIVE LABEL, e.g. Total Venture Capital Inflow]</span>
       </div>
       <div class="kpi-card">
         <span class="kpi-title">[SHORT TITLE, e.g. ENTERPRISE USERS]</span>
         <span class="kpi-value">[LARGE METRIC, e.g. 4.2M]</span>
         <span class="kpi-desc">[DESCRIPTIVE LABEL, e.g. Active Deployments globally]</span>
       </div>
     </div>
   - Select 4 metrics that directly support the topic (such as Market Size, CAGR, Revenue, Funding, Adoption Rate, Users, Patents, Market Share, etc.).

4. WRITTEN DEPTH & STYLE:
   - This must read like a premium consulting report, not a slide deck.
   - Maintain a ratio of approximately 60–65% deep, meaningful written analysis to 35–40% visual content (charts, tables, KPIs).
   - Every 1–2 pages should contain at least one meaningful visual element.
   - Avoid leaving large blank spaces. Fill pages with high-value analytical explanation.
   - Each major section must contain 400–800 words of well-structured content.
   - Every subsection must incorporate: Background, Detailed Explanation, Key Concepts, Real-World Examples, Current Industry Practices, Opportunities, Challenges, Expert Analysis, and Actionable Insights.
   - Use headings, bullet points, callout boxes, and plenty of whitespace.
   - Avoid conversational filler. Start directly with `#COVER` and end with references.
   - NO LATEX: WeasyPrint cannot render LaTeX delimiters like $ or $$. Use Unicode characters or plain text instead (e.g. write alpha, beta, 10^5, or UTF-8 mathematical symbols).

5. DATA VISUALIZATIONS, CHARTS & DIAGRAMS:
   - You must generate and distribute high-quality visual elements (JSON charts, KPI blocks, comparison tables) naturally throughout the report.
   - DIAGRAM RULE: Add block diagrams or architecture/network diagrams ONLY when the report topic explicitly requires them.
     - Examples where diagram IS required:
       ✅ "AI Agent Architecture" -> Include an architecture/block diagram.
       ✅ "Network Topology" -> Include a network diagram.
       ✅ "System Infrastructure & Pipeline" -> Include a block diagram.
     - Examples where diagram is NOT allowed:
       ❌ "Market Analysis of Netflix" -> Don't add block/architecture diagrams unless specifically relevant.
       ❌ "Global Supply Chain Trends" -> Don't add block/architecture diagrams unless specifically relevant.
   - When a block diagram IS explicitly required by the report topic, define it using a ```json-diagram block designed for a vertical top-to-bottom consulting report layout:
   ```json-diagram
   {{
     "type": "block_diagram",
     "title": "System Architecture & Threat Intelligence Workflow",
     "nodes": [
       {{
         "id": "step1",
         "heading": "1. Ingestion & Threat Intelligence",
         "bullet_points": [
           "Aggregates multi-source telemetry & audit logs",
           "Filters network traffic anomalies in real-time",
           "Validates identity and access control credentials"
         ]
       }},
       {{
         "id": "step2",
         "heading": "2. Security Analysis & Incident Response",
         "bullet_points": [
           "Executes ML-driven threat pattern recognition",
           "Correlates cross-platform security event signatures",
           "Prioritizes alerts using dynamic risk matrix"
         ]
       }},
       {{
         "id": "step3",
         "heading": "3. Automated Containment & Mitigation",
         "bullet_points": [
           "Triggers automated playbook response actions",
           "Isolates compromised microservices & endpoints",
           "Generates executive incident audit report"
         ]
       }}
     ],
     "connections": [
       {{"from": "step1", "to": "step2", "label": "Threat Intelligence"}},
       {{"from": "step2", "to": "step3", "label": "Security Alerts"}}
     ]
   }}
   ```
   - Define standard data charts using this exact JSON code block structure (do not add any conversational text inside the code block):
   ```json-chart
   {{
     "type": "bar" | "donut" | "line" | "area",
     "title": "Chart Title",
     "labels": ["Label A", "Label B", "Label C"],
     "values": [45, 30, 25],
     "x_label": "X Axis Label (optional)",
     "y_label": "Y Axis Label (optional)"
   }}
   ```
   - Immediately follow every chart or diagram block with an "📈 Analysis & Key Insights" section of 150–300 words. Do not use short bullet points. Provide a detailed narrative covering: What the chart/diagram represents, Major trends, Significant observations, Business implications, Strategic recommendations, and Key takeaways.

6. TABLES & SUMMARIES:
   - Include comparison tables where appropriate.
   - Immediately after every comparison table, write a "Summary of Findings" section (150–250 words) explaining the key differences, strengths, weaknesses, and practical strategic implications of the compared options.

7. CASE STUDIES:
   - Expand every case study into a comprehensive format (approx. 250–500 words per case study).
   - Address the following subsections in order: Background, Challenge, Solution, Implementation, Results, Lessons Learned, and Business Impact.

8. CONTENT CHECKLIST (Include all these sections in order):
   - Cover Page metadata
   - Table of Contents
   - Mandatory KPI Dashboard (4 cards, HTML layout)
   - Executive Summary (One-page concise overview, key findings, and takeaways)
   - 1. Introduction & Context (What is the topic, why is it important, current relevance)
   - 2. Market Landscape & Analysis (Main body sections, core concepts, industry use. Include at least 2 distinct charts: e.g. 1 bar chart for adoption, 1 donut chart for market segmentation, each with its own 'Analysis & Key Insights' section)
   - 3. Structured Comparison Table (Include a Markdown comparison table contrasting key features/approaches, followed by a Summary of Findings. Optionally add a Bar Chart representing table metrics)
   - 4. Case Studies (Provide 2-3 real-world organization examples, expanded using the required 7-part format. Include a highly relevant chart cleanly within this section, aligning it properly with the related case study data and maintaining sufficient spacing so it does not overlap or appear disconnected from the text it supports)
   - 5. Best Practices & Tactical Recommendations (Include 1 Line or Area Chart showing adoption/growth trends)
   - 6. Future Trends & Strategic Outlook (Next 5-10 years timeline, opportunities, and challenges. Include 1 Forecast Line or Area Chart showing future size/adoption)
   - 7. Conclusion & Strategic Summary
   - References (A numbered list of trusted sources citing organizations, journals, or reports. Place this section at the very end of the report so it appears on the last page only)
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
