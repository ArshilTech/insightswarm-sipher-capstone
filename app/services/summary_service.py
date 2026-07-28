from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.graphs.research_graph import llm
import os
import markdown
from weasyprint import HTML

SUMMARY_PROMPT = ChatPromptTemplate.from_messages([
    ("system", (
        "You are an expert business analyst. You will be given the full text of an already-completed "
        "research report. Do not conduct new research or invent facts beyond what is in the report. "
        "Condense it into a concise executive summary of approximately 400-500 words, formatted in "
        "Markdown with exactly these level-2 headings, in this order:\n"
        "## Overview\n## Key Findings\n## Important Insights\n## Conclusion\n## Recommendations\n\n"
        "Omit the Recommendations section entirely if the source report does not support any actionable "
        "recommendations. Do not include a title, cover page, or any content outside these headings."
    )),
    ("user", "Full Report:\n\n{report_content}")
])

def generate_executive_summary_text(report_markdown: str) -> str:
    """Generates a concise executive summary from an already-completed report's markdown.
    Reuses the existing LLM client directly — does not invoke the research graph,
    Tavily, or any planner/research/verification nodes."""
    chain = SUMMARY_PROMPT | llm | StrOutputParser()
    return chain.invoke({"report_content": report_markdown}).strip()

def generate_executive_summary_pdf(summary_markdown: str, run_id: str) -> str:
    """Renders the executive summary into a lightweight, single-page-style PDF.
    Deliberately uses a minimal template rather than pdf_service.generate_pdf_report's
    full cover-page/KPI-dashboard pipeline, since a 400-500 word summary doesn't need it."""
    html_body = markdown.markdown(summary_markdown, extensions=['fenced_code'])

    styled_html = f"""
    <html>
    <head>
    <style>
        body {{ font-family: 'Georgia', serif; color: #1e293b; margin: 50px; line-height: 1.6; }}
        h1 {{ font-size: 22px; color: #0f172a; border-bottom: 2px solid #0d9488; padding-bottom: 10px; }}
        h2 {{ font-size: 15px; color: #0d9488; text-transform: uppercase; letter-spacing: 0.05em; margin-top: 28px; }}
        p, ul {{ font-size: 12px; }}
    </style>
    </head>
    <body>
        <h1>Executive Summary</h1>
        {html_body}
    </body>
    </html>
    """

    output_dir = os.getenv("REPORT_DIR", "reports")
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, f"{run_id}_executive_summary.pdf")

    HTML(string=styled_html).write_pdf(file_path)
    return file_path