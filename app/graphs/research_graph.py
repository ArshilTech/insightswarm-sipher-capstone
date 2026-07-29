from typing import TypedDict, List, Dict, Any, Annotated
from langgraph.graph import StateGraph, END
import operator
import os
import re
import time
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
# Used only when the main report response ends before its final sections.
tail_llm = ChatGroq(model=llm_model, temperature=0, max_tokens=900)

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

def ensure_references(draft: str, sources: List[Dict[str, Any]]) -> str:
    """Append source links if the model omitted the required References section."""
    entries = []
    for source in sources:
        url = source.get("url", "").strip()
        title = source.get("title", "").strip()
        if not url:
            continue
        title = title.replace("[", "").replace("]", "") or url
        entry = f"[{title}]({url})"
        if entry not in entries:
            entries.append(entry)

    if not entries:
        return draft

    references_match = re.search(r"(?im)^#{1,3}\s*references\s*[:\s]*$", draft, flags=re.MULTILINE)
    if references_match:
        following_text = draft[references_match.end():]
        if re.search(r"https?://", following_text):
            return draft
        # Add entries after an existing References heading if no URLs were found.
        return draft.rstrip() + "\n\n" + "\n".join(
            f"{index}. {entry}" for index, entry in enumerate(entries, start=1)
        )

    heading = "\n\n## References\n"
    return f"{draft.rstrip()}{heading}" + "\n".join(
        f"{index}. {entry}" for index, entry in enumerate(entries, start=1)
    )

TAIL_SECTION_REQUESTS = {
    1: "Write exactly `## 1. Introduction & Context` with concise background, relevance, opportunities, and challenges.",
    2: "Write exactly `## 2. Market Landscape & Analysis` and include one valid bar `json-chart` followed by `### Analysis & Key Insights`.",
    3: "Write exactly `## 3. Structured Comparison Table` with a Markdown comparison table and `### Summary of Findings`.",
    4: "Write exactly `## 4. Case Studies` with exactly two concise real-world cases using Background, Challenge, Solution, Implementation, Results, Lessons Learned, and Business Impact.",
    5: "Write exactly `## 5. Best Practices & Tactical Recommendations` with actionable recommendations, one valid line `json-chart`, and `### Analysis & Key Insights`.",
    6: "Write exactly `## 6. Future Trends & Strategic Outlook` with next 5-10 year trends, opportunities, challenges, one valid area `json-chart`, and `### Analysis & Key Insights`.",
    7: "Write exactly `## 7. Conclusion & Strategic Summary` as a complete closing summary with strategic takeaways. Do not add References.",
}

def build_tail_context(sources: List[Dict[str, Any]]) -> str:
    """Use compact source excerpts so a tail-repair call stays below Groq's TPM limit."""
    excerpts = []
    for index, source in enumerate(sources, start=1):
        excerpts.append(
            f"Source {index}: {source.get('title', 'Untitled')} ({source.get('url', '')})\n"
            f"{source.get('content', '').strip()[:350]}"
        )
    return "\n\n".join(excerpts)

def repair_incomplete_tail(draft: str, topic: str, instructions: str, sources: List[Dict[str, Any]], log) -> str:
    """Replace a truncated final section and generate only the missing report tail."""
    section_matches = list(re.finditer(r"(?im)^##\s+([1-7])\.\s+.+$", draft))
    if not section_matches:
        return draft

    present_sections = {int(match.group(1)) for match in section_matches}
    missing_sections = [number for number in range(1, 8) if number not in present_sections]
    if not missing_sections:
        return draft

    last_match = section_matches[-1]
    last_section = int(last_match.group(1))
    trailing_content = draft[last_match.end():].strip()
    start_section = last_section if trailing_content and not re.search(r"[.!?)]$", trailing_content) else missing_sections[0]
    trim_match = next((match for match in section_matches if int(match.group(1)) == start_section), None)
    preserved_draft = draft[:trim_match.start()].rstrip() if trim_match else draft.rstrip()
    source_context = build_tail_context(sources)

    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are completing the missing end of a business report. Return only the requested Markdown section.
Use source-supported claims. Keep the heading exactly as requested. Write 250-400 words, except keep chart analysis
to 80-120 words. Chart values must be numbers only. Do not use donut or pie charts, image placeholders, a cover,
a table of contents, or a References heading."""),
        ("user", "Topic: {topic}\nUser instructions: {instructions}\n\nSources:\n{sources}\n\nTask:\n{task}"),
    ])
    chain = prompt | tail_llm | StrOutputParser()
    repaired_sections = []
    for section_number in range(start_section, 8):
        log.info(f"SYNTHESIZER: Repairing missing report section {section_number}.")
        for attempt in range(2):
            try:
                repaired_sections.append(chain.invoke({
                    "topic": topic,
                    "instructions": instructions,
                    "sources": source_context,
                    "task": TAIL_SECTION_REQUESTS[section_number],
                }).strip())
                break
            except Exception as error:
                if attempt == 0 and ("rate_limit" in str(error).lower() or "too large" in str(error).lower()):
                    time.sleep(60)
                    continue
                raise

    return "\n\n".join(part for part in [preserved_draft, *repaired_sections] if part)

def synthesize_node(state: ResearchState) -> Dict:
    """Uses an LLM to draft the report based on gathered sources."""
    log = get_run_logger(__name__, state['run_id'])
    log.info(f"SYNTHESIZER: Writing draft using {len(state['sources'])}3 sources.")

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
   - Each major section must contain 250–400 words of well-structured content.
   - Every subsection must incorporate: Background, Detailed Explanation, Key Concepts, Real-World Examples, Current Industry Practices, Opportunities, Challenges, Expert Analysis, and Actionable Insights.
   - Use headings, bullet points, callout boxes, and plenty of whitespace.
   - Avoid conversational filler. Start directly with `#COVER` and end with references.
   - NO LATEX: WeasyPrint cannot render LaTeX delimiters like $ or $$. Use Unicode characters or plain text instead (e.g. write alpha, beta, 10^5, or UTF-8 mathematical symbols).

5.  DATA VISUALIZATIONS & CHARTS:
- Generate 3–5 high-quality visual elements throughout the report.

- Every chart MUST be valid JSON.

- IMPORTANT:
  - The "values" array must contain ONLY numbers.
  - Never include %, ₹, $, commas, units, words, or symbols inside "values".
  - Use:
      Correct: [70, 20, 10]
      Incorrect: [70%, 20%, 10%]

Use exactly this format:

```json-chart
{{
  "type": "bar",
  "title": "Chart Title",
  "labels": ["Label A", "Label B", "Label C"],
  "values": [45, 30, 25],
  "x_label": "X Axis Label (optional)",
  "y_label": "Y Axis Label (optional)"
}}
```

   Allowed values for "type":
   - bar
   - donut
   - line
   - area

   - Immediately follow every chart block with an "📈 Analysis & Key Insights" section of 80–120 words. Provide a concise narrative covering the trend, key observation, and business implication.
   
5.5 IMAGES & DIAGRAMS (VERY IMPORTANT)

- Throughout the report, include relevant images wherever they improve understanding.
- DO NOT use Markdown image syntax.
- DO NOT use HTML <img> tags.
- Instead, insert placeholders in exactly this format:

[IMAGE: image search query]

Examples:

[IMAGE: Tesla Gigafactory]

[IMAGE: Transformer Architecture]

[IMAGE: CNN Architecture]

[IMAGE: Electric Vehicle Market Growth]

[IMAGE: Apple Supply Chain]

Rules:
- Include approximately one image every 2–3 major sections.
- Only request images that directly support the nearby content.
- The placeholder must be on its own line.
- Use short Google-search-friendly queries.
- Do not explain the placeholder.
- Continue writing normally after the placeholder.

6. TABLES & SUMMARIES:
   - Include comparison tables where appropriate.
   - Immediately after every comparison table, write a "Summary of Findings" section (80–120 words) explaining the key differences and practical strategic implications of the compared options.

7. CASE STUDIES:
   - Provide exactly 2 concise case studies (approximately 120–180 words each).
   - Address the following subsections in order: Background, Challenge, Solution, Implementation, Results, Lessons Learned, and Business Impact.

8. CONTENT CHECKLIST (Include all these sections in order):
   - Cover Page metadata
   - Table of Contents
   - Mandatory KPI Dashboard (4 cards, HTML layout)
   - Executive Summary (150–200-word overview, key findings, and takeaways)
   - 1. Introduction & Context (What is the topic, why is it important, current relevance)
   - 2. Market Landscape & Analysis (Main body sections, core concepts, industry use. Include at least 2 distinct charts: e.g. 1 bar chart for adoption, 1 donut chart for market segmentation, each with its own 'Analysis & Key Insights' section)
   - 3. Structured Comparison Table (Include a Markdown comparison table contrasting key features/approaches, followed by a Summary of Findings. Optionally add a Bar Chart representing table metrics)
   - 4. Case Studies (Provide 2-3 real-world organization examples, expanded using the required 7-part format.)
   - 5. Best Practices & Tactical Recommendations (Include 1 Line or Area Chart showing adoption/growth trends)
   - 6. Future Trends & Strategic Outlook (Next 5-10 years timeline, opportunities, and challenges. Include 1 Forecast Line or Area Chart showing future size/adoption)
   - 7. Conclusion & Strategic Summary
   - References (A numbered list of ALL sources used. Place this at the very end under `References`. CRITICAL REQUIREMENT: For EVERY reference entry you MUST use the ACTUAL title and ACTUAL URL from the Sources provided above — do NOT use placeholder text like "Source Title or Organization". Format each entry as: `1. [Actual Title of the Article or Website](https://actual-url-from-sources.com)`. For example, if a source has title "Global AI Market Report" and URL "https://example.com/ai-report", write: `1. [Global AI Market Report](https://example.com/ai-report)`. Every entry MUST be a clickable markdown hyperlink pointing to the real source URL.)
"""),
        ("user", "Topic: {topic}\nInstructions: {instructions}\n\nSources:\n{context}")
    ])

    chain = prompt | llm | StrOutputParser()
    draft = chain.invoke({
        "topic": state["topic"],
        "instructions": state["instructions"],
        "context": context
    })
    draft = repair_incomplete_tail(
        draft, state["topic"], state["instructions"], state["sources"], log
    )
    draft = ensure_references(draft, state["sources"])

# -----------------------------------------------------------------
# Ensure at least a few image placeholders exist
# -----------------------------------------------------------------

    if "[IMAGE:" not in draft:

        import re

        section_images = {
            "Introduction": f"{state['topic']} overview",
            "Market Landscape": f"{state['topic']} architecture",
            "Case Studies": f"{state['topic']} case study",
            "Future Trends": f"{state['topic']} future technology",
        }

        for keyword, query in section_images.items():

            pattern = rf"(^#+\s.*{re.escape(keyword)}.*$)"

            match = re.search(
                pattern, 
                draft, 
                flags=re.IGNORECASE | re.MULTILINE)

            if match:

                heading = match.group(1)

                replacement = (
                    f"{heading}\n\n"
                    f"[IMAGE: {query}]"
                )

                draft = draft.replace(
                    heading,
                    replacement,
                    1
                )
        

    

    return {"draft": draft}

def verify_node(state: ResearchState) -> Dict:
    """Checks the draft for hallucinations or unsupported claims."""
    log = get_run_logger(__name__, state['run_id'])
    log.info("VERIFIER: Checking factual consistency.")
    
    if not state.get("sources"):
        log.info("VERIFIER: 03 sources available, marking as verified.")
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
