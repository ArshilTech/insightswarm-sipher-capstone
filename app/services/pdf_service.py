import os
import re
import json
import math
import markdown
from dotenv import load_dotenv

load_dotenv()

DEFAULT_THEME = {
    "name": "Teal",
    "primary": "#0d9488",
    "dark": "#0f766e",
    "light": "#f0fdfa",
    "chart": ["#0d9488", "#14b8a6", "#2dd4bf", "#0e7490", "#047857"],
}

# Add GTK dll path for WeasyPrint on Windows
if os.name == 'nt':
    gtk_paths = []
    
    # 0. Custom GTK_PATH environment override if defined
    gtk_env_override = os.environ.get("GTK_PATH")
    if gtk_env_override:
        gtk_paths.append(gtk_env_override)
        
    # 1. WinGet GTK package under current user profile AppData
    local_app_data = os.environ.get("LOCALAPPDATA")
    if local_app_data:
        winget_path = os.path.join(
            local_app_data, 
            "Microsoft", 
            "WinGet", 
            "Packages", 
            "wingtk.gvsbuild.GTK4_Microsoft.Winget.Source_8wekyb3d8bbwe", 
            "bin"
        )
        gtk_paths.append(winget_path)
        
    # 2. Standard GTK installers paths
    gtk_paths.append(r"C:\Program Files\GTK3-Runtime_64bit\bin")
    gtk_paths.append(r"C:\Program Files\GTK-Runtime\bin")
    
    # 3. Microsoft Power BI Desktop
    gtk_paths.append(r"C:\Program Files\Microsoft Power BI Desktop\bin")
    
    # 4. Dynamic OneDrive paths (scan versioned subdirectories)
    onedrive_base = r"C:\Program Files\Microsoft OneDrive"
    if os.path.exists(onedrive_base):
        try:
            for item in os.listdir(onedrive_base):
                item_path = os.path.join(onedrive_base, item)
                if os.path.isdir(item_path) and re.match(r'^\d+(\.\d+)+$', item):
                    gtk_paths.append(item_path)
        except Exception:
            pass

    # 5. Scan system PATH variable dynamically for any folder containing GTK DLLs
    system_path = os.environ.get("PATH", "")
    for p in system_path.split(os.pathsep):
        p_clean = p.strip('"')  # Remove surrounding quotes if present
        if p_clean and os.path.exists(p_clean):
            if os.path.exists(os.path.join(p_clean, "gobject-2.0-0.dll")) or os.path.exists(os.path.join(p_clean, "libgobject-2.0-0.dll")):
                gtk_paths.append(p_clean)

    for path in gtk_paths:
        if os.path.exists(path):
            os.environ["PATH"] = path + os.pathsep + os.environ["PATH"]
            try:
                os.add_dll_directory(path)
            except AttributeError:
                pass
            # Normally loading one valid path is enough, but we update the PATH for all candidates
            
from weasyprint import HTML
import base64
from app.services.image_service import download_image

# --- Helper Functions for SVG Chart Generation ---

def get_donut_path(cx, cy, r_out, r_in, start_angle, end_angle):
    # Convert angles to radians (0 degrees is top, rotating clockwise)
    rad_start = math.radians(start_angle - 90)
    rad_end = math.radians(end_angle - 90)
    
    x_out_start = cx + r_out * math.cos(rad_start)
    y_out_start = cy + r_out * math.sin(rad_start)
    
    x_out_end = cx + r_out * math.cos(rad_end)
    y_out_end = cy + r_out * math.sin(rad_end)
    
    x_in_start = cx + r_in * math.cos(rad_start)
    y_in_start = cy + r_in * math.sin(rad_start)
    
    x_in_end = cx + r_in * math.cos(rad_end)
    y_in_end = cy + r_in * math.sin(rad_end)
    
    large_arc = 1 if (end_angle - start_angle) > 180 else 0
    
    path = f"M {x_out_start} {y_out_start} "
    path += f"A {r_out} {r_out} 0 {large_arc} 1 {x_out_end} {y_out_end} "
    path += f"L {x_in_end} {y_in_end} "
    path += f"A {r_in} {r_in} 0 {large_arc} 0 {x_in_start} {y_in_start} "
    path += "Z"
    return path

def draw_bar_chart(title, labels, values, x_label, y_label, theme=None):
    svg_width = 650
    svg_height = 340
    margin_left = 70
    margin_right = 30
    margin_top = 45
    margin_bottom = 55
    
    chart_width = svg_width - margin_left - margin_right
    chart_height = svg_height - margin_top - margin_bottom
    
    max_val = max(values) if values else 1
    if max_val <= 0:
        max_val = 1
        
    order = 10 ** int(math.log10(max_val)) if max_val > 0 else 1
    if order == 0:
        order = 1
    grid_max = math.ceil(max_val / (order / 2)) * (order / 2)
    if grid_max == 0:
        grid_max = 1.0
        
    num_ticks = 4
    chart_theme = theme or DEFAULT_THEME
    colors = chart_theme.get("chart", DEFAULT_THEME["chart"])
    
    svg = f'<svg viewBox="0 0 {svg_width} {svg_height}" width="100%" height="{svg_height}" class="chart-bar" xmlns="http://www.w3.org/2000/svg">\n'
    svg += '  <style>\n'
    svg += '    .c-title { font-family: "Space Grotesk", "Helvetica Neue", sans-serif; font-size: 15px; font-weight: 600; fill: #0f172a; }\n'
    svg += '    .c-axis-label { font-family: "Inter", "Helvetica Neue", sans-serif; font-size: 10px; fill: #64748b; font-weight: 500; }\n'
    svg += '    .c-tick-label { font-family: "Inter", "Helvetica Neue", sans-serif; font-size: 9px; fill: #64748b; }\n'
    svg += '    .c-bar-val { font-family: "Inter", "Helvetica Neue", sans-serif; font-size: 9px; font-weight: 600; text-anchor: middle; }\n'
    svg += '    .c-grid-line { stroke: #e2e8f0; stroke-width: 1; stroke-dasharray: 2 2; }\n'
    svg += '    .c-axis { stroke: #cbd5e1; stroke-width: 1.5; }\n'
    svg += '  </style>\n'
    
    # Title
    svg += f'  <text x="{svg_width/2}" y="22" class="c-title" text-anchor="middle">{title}</text>\n'
    
    # Grid lines & ticks
    for i in range(num_ticks + 1):
        tick_val = (grid_max / num_ticks) * i
        y_pos = margin_top + chart_height - (tick_val / grid_max) * chart_height
        svg += f'  <line x1="{margin_left}" y1="{y_pos}" x2="{svg_width - margin_right}" y2="{y_pos}" class="c-grid-line" />\n'
        svg += f'  <text x="{margin_left - 8}" y="{y_pos + 3}" class="c-tick-label" text-anchor="end">{tick_val:g}</text>\n'
        
    # Bars
    n = len(values)
    bar_group_width = chart_width / n
    bar_width = bar_group_width * 0.6
    bar_gap = bar_group_width * 0.4
    
    for i in range(n):
        val = values[i]
        bar_h = (val / grid_max) * chart_height
        x_pos = margin_left + (i * bar_group_width) + (bar_gap / 2)
        y_pos = margin_top + chart_height - bar_h
        color = colors[i % len(colors)]
        
        # Rounded corners on top
        svg += f'  <rect x="{x_pos}" y="{y_pos}" width="{bar_width}" height="{bar_h}" rx="3" ry="3" fill="{color}" />\n'
        svg += f'  <text x="{x_pos + bar_width/2}" y="{y_pos - 5}" class="c-bar-val" style="fill: {color};">{val:g}</text>\n'
        
        lbl = labels[i]
        if len(lbl) > 12:
            lbl = lbl[:10] + ".."
        svg += f'  <text x="{x_pos + bar_width/2}" y="{margin_top + chart_height + 15}" class="c-tick-label" text-anchor="middle">{lbl}</text>\n'
        
    # Axes
    svg += f'  <line x1="{margin_left}" y1="{margin_top + chart_height}" x2="{svg_width - margin_right}" y2="{margin_top + chart_height}" class="c-axis" />\n'
    svg += f'  <line x1="{margin_left}" y1="{margin_top}" x2="{margin_left}" y2="{margin_top + chart_height}" class="c-axis" />\n'
    
    if x_label:
        svg += f'  <text x="{svg_width/2}" y="{svg_height - 10}" class="c-axis-label" text-anchor="middle">{x_label}</text>\n'
    if y_label:
        svg += f'  <text x="18" y="{margin_top + chart_height/2}" class="c-axis-label" text-anchor="middle" transform="rotate(-90 18 {margin_top + chart_height/2})">{y_label}</text>\n'
        
    svg += '</svg>\n'
    return svg

def draw_donut_chart(title, labels, values, theme=None):
    svg_width = 650
    svg_height = 290
    cx = 170
    cy = 145
    r_out = 90
    r_in = 55
    
    total = sum(values)
    if total <= 0:
        total = 1
        
    chart_theme = theme or DEFAULT_THEME
    colors = chart_theme.get("chart", DEFAULT_THEME["chart"])
    
    svg = f'<svg viewBox="0 0 {svg_width} {svg_height}" width="100%" height="{svg_height}" class="chart-donut" xmlns="http://www.w3.org/2000/svg">\n'
    svg += '  <style>\n'
    svg += '    .c-title { font-family: "Space Grotesk", "Helvetica Neue", sans-serif; font-size: 15px; font-weight: 600; fill: #0f172a; }\n'
    svg += '    .c-legend-text { font-family: "Inter", "Helvetica Neue", sans-serif; font-size: 10px; fill: #334155; }\n'
    svg += '    .c-legend-pct { font-family: "Inter", "Helvetica Neue", sans-serif; font-size: 10px; fill: #64748b; font-weight: 600; }\n'
    svg += '  </style>\n'
    
    svg += f'  <text x="{svg_width/2}" y="22" class="c-title" text-anchor="middle">{title}</text>\n'
    
    start_angle = 0
    for i, val in enumerate(values):
        pct = (val / total) * 100
        angle_delta = (val / total) * 360
        end_angle = start_angle + angle_delta
        
        if angle_delta >= 0.1:
            if angle_delta >= 359.9:
                path1 = get_donut_path(cx, cy, r_out, r_in, 0, 180)
                path2 = get_donut_path(cx, cy, r_out, r_in, 180, 360)
                color = colors[i % len(colors)]
                svg += f'  <path d="{path1}" fill="{color}" />\n'
                svg += f'  <path d="{path2}" fill="{color}" />\n'
            else:
                path = get_donut_path(cx, cy, r_out, r_in, start_angle, end_angle)
                color = colors[i % len(colors)]
                svg += f'  <path d="{path}" fill="{color}" />\n'
                
        legend_y = 65 + i * 22
        if legend_y < svg_height - 15:
            color = colors[i % len(colors)]
            svg += f'  <rect x="360" y="{legend_y - 8}" width="12" height="12" rx="2" fill="{color}" />\n'
            lbl = labels[i]
            if len(lbl) > 25:
                lbl = lbl[:23] + ".."
            svg += f'  <text x="382" y="{legend_y + 2}" class="c-legend-text">{lbl}</text>\n'
            svg += f'  <text x="560" y="{legend_y + 2}" class="c-legend-pct" text-anchor="end">{pct:.1f}% ({val:g})</text>\n'
            
        start_angle = end_angle
        
    svg += '</svg>\n'
    return svg

def draw_line_chart(title, labels, values, x_label, y_label, area=False, theme=None):
    svg_width = 650
    svg_height = 340
    margin_left = 70
    margin_right = 30
    margin_top = 45
    margin_bottom = 55
    
    chart_width = svg_width - margin_left - margin_right
    chart_height = svg_height - margin_top - margin_bottom
    
    max_val = max(values) if values else 1
    if max_val <= 0:
        max_val = 1
        
    order = 10 ** int(math.log10(max_val)) if max_val > 0 else 1
    if order == 0:
        order = 1
    grid_max = math.ceil(max_val / (order / 2)) * (order / 2)
    if grid_max == 0:
        grid_max = 1.0
        
    num_ticks = 4
    chart_theme = theme or DEFAULT_THEME
    colors = chart_theme.get("chart", DEFAULT_THEME["chart"])
    line_col = colors[0]
    point_col = colors[1 % len(colors)]
    
    svg = f'<svg viewBox="0 0 {svg_width} {svg_height}" width="100%" height="{svg_height}" class="chart-line" xmlns="http://www.w3.org/2000/svg">\n'
    svg += '  <style>\n'
    svg += '    .c-title { font-family: "Space Grotesk", "Helvetica Neue", sans-serif; font-size: 15px; font-weight: 600; fill: #0f172a; }\n'
    svg += '    .c-axis-label { font-family: "Inter", "Helvetica Neue", sans-serif; font-size: 10px; fill: #64748b; font-weight: 500; }\n'
    svg += '    .c-tick-label { font-family: "Inter", "Helvetica Neue", sans-serif; font-size: 9px; fill: #64748b; }\n'
    svg += '    .c-grid-line { stroke: #e2e8f0; stroke-width: 1; stroke-dasharray: 2 2; }\n'
    svg += '    .c-axis { stroke: #cbd5e1; stroke-width: 1.5; }\n'
    svg += f'    .c-line {{ stroke: {line_col}; stroke-width: 3; fill: none; stroke-linecap: round; stroke-linejoin: round; }}\n'
    svg += '    .c-area { fill: url(#area-grad); stroke: none; }\n'
    svg += f'    .c-point {{ fill: {point_col}; stroke: #ffffff; stroke-width: 2; }}\n'
    svg += f'    .c-point-val {{ font-family: "Inter", "Helvetica Neue", sans-serif; font-size: 9px; fill: {line_col}; font-weight: 600; text-anchor: middle; }}\n'
    svg += '  </style>\n'
    
    svg += '  <defs>\n'
    svg += '    <linearGradient id="area-grad" x1="0" y1="0" x2="0" y2="1">\n'
    svg += f'      <stop offset="0%" stop-color="{line_col}" stop-opacity="0.35"/>\n'
    svg += f'      <stop offset="100%" stop-color="{line_col}" stop-opacity="0.0"/>\n'
    svg += '    </linearGradient>\n'
    svg += '  </defs>\n'
    
    svg += f'  <text x="{svg_width/2}" y="22" class="c-title" text-anchor="middle">{title}</text>\n'
    
    for i in range(num_ticks + 1):
        tick_val = (grid_max / num_ticks) * i
        y_pos = margin_top + chart_height - (tick_val / grid_max) * chart_height
        svg += f'  <line x1="{margin_left}" y1="{y_pos}" x2="{svg_width - margin_right}" y2="{y_pos}" class="c-grid-line" />\n'
        svg += f'  <text x="{margin_left - 8}" y="{y_pos + 3}" class="c-tick-label" text-anchor="end">{tick_val:g}</text>\n'
        
    n = len(values)
    points = []
    for i in range(n):
        val = values[i]
        x_pos = margin_left + (i / (n - 1 if n > 1 else 1)) * chart_width
        y_pos = margin_top + chart_height - (val / grid_max) * chart_height
        points.append((x_pos, y_pos, val))
        
    if area and points:
        area_path = f"M {points[0][0]} {margin_top + chart_height} "
        for x, y, _ in points:
            area_path += f"L {x} {y} "
        area_path += f"L {points[-1][0]} {margin_top + chart_height} Z"
        svg += f'  <path d="{area_path}" class="c-area" />\n'
        
    if points:
        line_path = f"M {points[0][0]} {points[0][1]} "
        for x, y, _ in points[1:]:
            line_path += f"L {x} {y} "
        svg += f'  <path d="{line_path}" class="c-line" />\n'
        
    for i, (x, y, val) in enumerate(points):
        p_c = colors[i % len(colors)]
        svg += f'  <circle cx="{x}" cy="{y}" r="4.5" class="c-point" style="fill: {p_c};" />\n'
        svg += f'  <text x="{x}" y="{y - 7}" class="c-point-val">{val:g}</text>\n'
        lbl = labels[i]
        if len(lbl) > 12:
            lbl = lbl[:10] + ".."
        svg += f'  <text x="{x}" y="{margin_top + chart_height + 15}" class="c-tick-label" text-anchor="middle">{lbl}</text>\n'
        
    svg += f'  <line x1="{margin_left}" y1="{margin_top + chart_height}" x2="{svg_width - margin_right}" y2="{margin_top + chart_height}" class="c-axis" />\n'
    svg += f'  <line x1="{margin_left}" y1="{margin_top}" x2="{margin_left}" y2="{margin_top + chart_height}" class="c-axis" />\n'
    
    if x_label:
        svg += f'  <text x="{svg_width/2}" y="{svg_height - 10}" class="c-axis-label" text-anchor="middle">{x_label}</text>\n'
    if y_label:
        svg += f'  <text x="18" y="{margin_top + chart_height/2}" class="c-axis-label" text-anchor="middle" transform="rotate(-90 18 {margin_top + chart_height/2})">{y_label}</text>\n'
        
    svg += '</svg>\n'
    return svg

def generate_svg_chart(chart_data: dict, theme=None) -> str:
    chart_type = chart_data.get("type", "bar").lower()
    title = chart_data.get("title", "")
    labels = chart_data.get("labels", [])
    values = chart_data.get("values", [])
    x_label = chart_data.get("x_label", "")
    y_label = chart_data.get("y_label", "")
    
    if not labels or not values:
        return "<!-- Chart missing data labels or values -->"
        
    try:
        values = [float(v) for v in values]
    except Exception:
        return "<!-- Invalid numeric data in chart -->"
        
    if chart_type in ("donut", "pie"):
        return draw_donut_chart(title, labels, values, theme=theme)
    elif chart_type == "line":
        return draw_line_chart(title, labels, values, x_label, y_label, area=False, theme=theme)
    elif chart_type == "area":
        return draw_line_chart(title, labels, values, x_label, y_label, area=True, theme=theme)
    else:
        return draw_bar_chart(title, labels, values, x_label, y_label, theme=theme)

def process_charts(markdown_content: str, theme=None) -> str:
    pattern = r"```json-chart\s*\n(.*?)\n\s*```"
    
    def replacer(match):
        json_str = match.group(1)
        try:
            chart_data = json.loads(json_str)
            svg_content = generate_svg_chart(chart_data, theme=theme)
            return f'<div class="chart-container">{svg_content}</div>'
        except Exception as e:
            return f'<div class="chart-error">Chart Rendering Error: {str(e)}</div>'
            
    return re.sub(pattern, replacer, markdown_content, flags=re.DOTALL)

def process_images(markdown_content: str) -> str:
    """
    Replace every ``[IMAGE: <query>]`` placeholder in *markdown_content*
    with an inline base64 data-URI ``<img>`` tag.

    Images are fetched via :func:`download_image`, which returns a file path.
    The MIME type is guessed from the file extension to build the correct
    data-URI prefix. No filesystem cleanup is performed here.
    """
    import mimetypes

    pattern = r"\[IMAGE:(.*?)\]"

    matches = re.findall(pattern, markdown_content)

    print(f"\nFound {len(matches)} image placeholders")

    # Maximum number of images embedded per report
    MAX_IMAGES = 3

    used_queries: set[str] = set()
    images_added = 0

    def _remove_placeholder(content: str, query: str) -> str:
        """Erase both spaced and non-spaced variants of the placeholder."""
        content = content.replace(f"[IMAGE: {query}]", "", 1)
        content = content.replace(f"[IMAGE:{query}]", "", 1)
        return content

    for query in matches:

        query = query.strip()

        # Skip duplicate search queries
        if query.lower() in used_queries:
            markdown_content = _remove_placeholder(markdown_content, query)
            continue

        # Stop after maximum images
        if images_added >= MAX_IMAGES:
            markdown_content = _remove_placeholder(markdown_content, query)
            continue

        print(f"[PDF] Fetching image for: {query}")

        image_path = download_image(query)

        if image_path is None:
            markdown_content = _remove_placeholder(markdown_content, query)
            continue

        # Check that the file has actual content
        try:
            file_size = os.path.getsize(image_path)
        except OSError:
            markdown_content = _remove_placeholder(markdown_content, query)
            continue

        if file_size == 0:
            markdown_content = _remove_placeholder(markdown_content, query)
            continue

        # Guess MIME type from the file extension
        mime_type, _ = mimetypes.guess_type(image_path)
        if mime_type is None or not mime_type.startswith("image/"):
            mime_type = "image/jpeg"

        with open(image_path, "rb") as img:
            encoded = base64.b64encode(img.read()).decode()

        html = f"""
<div style="text-align:center; margin:35px 0;">
<img
src="data:{mime_type};base64,{encoded}"
style="
max-width:70%;
max-height:420px;
border-radius:10px;
display:block;
margin:auto;
"
/>
</div>
"""

        markdown_content = markdown_content.replace(
            f"[IMAGE: {query}]", html, 1
        )
        markdown_content = markdown_content.replace(
            f"[IMAGE:{query}]", html, 1
        )

        used_queries.add(query.lower())
        images_added += 1

    # Remove any remaining placeholders that were not processed
    markdown_content = re.sub(pattern, "", markdown_content)

    return markdown_content

def extract_cover_data(markdown_content: str) -> tuple[dict, str]:
    cover_data = {
        "title": "Corporate Strategy & Intelligence Report",
        "subtitle": "An Expert-Generated Comprehensive Briefing",
        "date": "July 18, 2026",
        "author": "InsightSwarm AI Research Service",
        "classification": "BUSINESS INTELLIGENCE"
    }
    
    cover_match = re.search(r"#COVER\s*\n(.*?)\n#ENDCOVER", markdown_content, re.DOTALL)
    if cover_match:
        cover_block = cover_match.group(1)
        for line in cover_block.split("\n"):
            if ":" in line:
                k, v = line.split(":", 1)
                k = k.strip().lower()
                v = v.strip()
                # Clean up markdown asterisks from values
                v = re.sub(r'\*\*|\*', '', v)
                if k in cover_data:
                    cover_data[k] = v
        remaining = markdown_content.replace(cover_match.group(0), "").strip()
    else:
        h1_match = re.search(r"^#\s+(.*)", markdown_content)
        if h1_match:
            cover_data["title"] = re.sub(r'\*\*|\*', '', h1_match.group(1).strip())
        remaining = markdown_content
        
    return cover_data, remaining

def convert_headings(html_content: str) -> str:
    # Convert numbered h2 headings (e.g. 1. Introduction) to h1
    html_content = re.sub(
        r'<h2([^>]*)>\s*(\d+)\.\s+(.*?)</h2\s*>',
        r'<h1\1>\2. \3</h1>',
        html_content,
        flags=re.IGNORECASE
    )
    # Convert References h2 heading to h1
    html_content = re.sub(
        r'<h2([^>]*)>\s*References\s*</h2\s*>',
        r'<h1\1>References</h1>',
        html_content,
        flags=re.IGNORECASE
    )
    return html_content

def process_toc(html_content: str) -> str:
    # Case A: Markdown list starts with Table of Contents link (common when no header exists in MD)
    toc_pattern = r'<ul>\s*<li><a href="#table-of-contents">Table of Contents</a></li>(.*?)</ul>'
    match = re.search(toc_pattern, html_content, flags=re.DOTALL | re.IGNORECASE)
    if match:
        toc_body = match.group(1)
        items = re.findall(r'<li><a href="([^"]+)">([^<]+)</a></li>', toc_body)
        filtered_items = []
        for href, text in items:
            text_clean = text.strip()
            if re.match(r'^\d+\.', text_clean) or text_clean.lower() == "references":
                filtered_items.append(f'<li><a href="{href}"><span>{text_clean}</span></a></li>')
        
        new_toc_html = f'<h2 id="table-of-contents">Table of Contents</h2>\n<ul class="toc-list">\n'
        new_toc_html += "\n".join(filtered_items)
        new_toc_html += "\n</ul>"
        
        html_content = html_content.replace(match.group(0), new_toc_html)
        return html_content
        
    # Case B: Already has Table of Contents header, followed by <ul>
    pattern = r'(<h[12][^>]*>Table of Contents</h[12]>)\s*<ul>'
    html_content = re.sub(pattern, r'\1\n<ul class="toc-list">', html_content, flags=re.IGNORECASE)
    
    def wrap_toc_items(match):
        toc_ul = match.group(0)
        toc_ul = re.sub(r'<li><a href="([^"]+)">([^<]+)</a></li>', r'<li><a href="\1"><span>\2</span></a></li>', toc_ul)
        return toc_ul
        
    html_content = re.sub(r'<ul class="toc-list">.*?</ul>', wrap_toc_items, html_content, flags=re.DOTALL)
    return html_content

def wrap_references_section(html_content: str) -> str:
    """Wrap the References heading and its body in a dedicated styled container."""
    pattern = r'(<h1[^>]*>\s*References\s*</h1>)(.*?)(?=<h[1-4][^>]*>|\Z)'
    return re.sub(pattern, r'<div class="references-section">\1\2</div>', html_content, flags=re.DOTALL | re.IGNORECASE)

# --- Main PDF Generation Service ---

def ensure_markdown_spacing(markdown_content: str) -> str:
    lines = markdown_content.split("\n")
    new_lines = []
    
    # First pass: Ensure empty line before tables
    for i, line in enumerate(lines):
        if re.match(r'^\s*\|?\s*:?-+:?\s*\|', line):
            if len(new_lines) >= 2 and new_lines[-2].strip() != "":
                new_lines.insert(-1, "")
        new_lines.append(line)
        
    # Second pass: Ensure empty line after tables
    final_lines = []
    in_table = False
    for i, line in enumerate(new_lines):
        is_table_row = line.strip().startswith("|")
        if is_table_row:
            in_table = True
        elif in_table:
            if line.strip() != "" and final_lines and final_lines[-1].strip() != "":
                final_lines.append("")
            in_table = False
        final_lines.append(line)
        
    return "\n".join(final_lines)

def inject_page_breaks(html_content: str) -> str:
    # Inject page break before Table of Contents heading
    html_content = re.sub(
        r'(<h[12][^>]*>Table of Contents</h[12]>)', 
        r'<div class="page-break"></div>\1', 
        html_content, 
        flags=re.IGNORECASE
    )
    
    # Inject page break before KPI Dashboard heading
    html_content = re.sub(
        r'(<h[12][^>]*>.*KPI Dashboard.*</h[12]>)', 
        r'<div class="page-break"></div>\1', 
        html_content, 
        flags=re.IGNORECASE
    )
    
    # Inject page break before Section 1 Introduction heading
    html_content = re.sub(
        r'(<h[12][^>]*>\s*1\.\s+Introduction.*</h[12]>)', 
        r'<div class="page-break"></div>\1', 
        html_content, 
        flags=re.IGNORECASE
    )
    
    # Inject page break before References heading
    html_content = re.sub(
        r'(<h[12][^>]*>References</h[12]>)', 
        r'<div class="page-break"></div>\1', 
        html_content, 
        flags=re.IGNORECASE
    )
    
    return html_content

def ensure_live_links(html_content: str) -> str:
    """Converts unlinked URLs in HTML content into active clickable <a> links."""
    url_pattern = r'(?<!href=")(?<!src=")(?<!">)(https?://[^\s<>"\'()]+)'
    return re.sub(url_pattern, r'<a href="\1" target="_blank" rel="noopener noreferrer">\1</a>', html_content)

def colorize_kpi_cards(html_content: str, theme: dict | None = None) -> str:
    """Preserves the existing KPI card markup while using the fixed report palette."""
    theme = theme or DEFAULT_THEME
    card_pattern = r'<div class="kpi-card">\s*<span class="kpi-title">(.*?)</span>\s*<span class="kpi-value">(.*?)</span>\s*<span class="kpi-desc">(.*?)</span>\s*</div>'

    matches = list(re.finditer(card_pattern, html_content, flags=re.DOTALL))
    if not matches:
        return html_content

    primary = theme.get("primary", DEFAULT_THEME["primary"])
    dark = theme.get("dark", DEFAULT_THEME["dark"])

    for match in matches:
        title, val, desc = match.group(1), match.group(2), match.group(3)
        replacement = f'''<div class="kpi-card" style="border-top: 4px solid {primary}; background: #ffffff; border-radius: 12px; padding: 18px 14px; box-shadow: 0 4px 14px rgba(0, 0, 0, 0.04); text-align: center;">
            <span class="kpi-title" style="color: #64748b; font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; display: block; margin-bottom: 6px;">{title}</span>
            <span class="kpi-value" style="color: {primary}; font-size: 26px; font-weight: 800; font-family: 'Space Grotesk', sans-serif; display: block; margin-bottom: 4px;">{val}</span>
            <span class="kpi-desc" style="color: {dark}; font-size: 11px; font-weight: 500; display: block; margin-top: 4px;">{desc}</span>
        </div>'''
        html_content = html_content.replace(match.group(0), replacement, 1)

    return html_content

def generate_pdf_report(markdown_content: str, run_id: str) -> tuple[str, int]:
    """Converts Markdown text to a highly-styled consulting-firm grade PDF report."""
    theme = DEFAULT_THEME
    
    cover_data, body_markdown = extract_cover_data(markdown_content)
    body_markdown = ensure_markdown_spacing(body_markdown)
    body_markdown = process_charts(body_markdown, theme=theme)
    body_markdown = process_images(body_markdown)  
    raw_html = markdown.markdown(body_markdown, extensions=['tables', 'fenced_code'])
    
    # Remove KPI Dashboard heading entirely to match Demo design (where the cards render below TOC directly)
    raw_html = re.sub(r'<h[12][^>]*>.*?KPI Dashboard.*?</h[12]>\s*', '', raw_html, flags=re.IGNORECASE)
    
    # Strip markdown asterisks inside HTML spans (like KPI card titles)
    raw_html = re.sub(r'(<span[^>]*>\s*)\*\*(.*?)\*\*(\s*</span>)', r'\1\2\3', raw_html)
    raw_html = re.sub(r'(<span[^>]*>\s*)\*(.*?)\*(\s*</span>)', r'\1\2\3', raw_html)
    
    # Colorize KPI cards with chosen single color theme template
    raw_html = colorize_kpi_cards(raw_html, theme)
    
    # Convert main numbered headings & References to h1
    raw_html = convert_headings(raw_html)
    raw_html = wrap_references_section(raw_html)
    
    raw_html = process_toc(raw_html)
    raw_html = inject_page_breaks(raw_html)
    raw_html = ensure_live_links(raw_html)
    
    cover_html = f"""
    <div class="cover-page">
        <div class="cover-accent-bar"></div>
        <div class="cover-title-group">
            <h1 class="cover-title">{cover_data['title']}</h1>
            <p class="cover-subtitle">{cover_data['subtitle']}</p>
        </div>
        
        <div class="cover-illustration-container">
            <svg class="cover-illustration" viewBox="0 0 400 200" width="100%" height="200" xmlns="http://www.w3.org/2000/svg">
                <defs>
                    <linearGradient id="grid-grad" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" stop-color="#14b8a6" stop-opacity="0.85"/>
                        <stop offset="100%" stop-color="#6366f1" stop-opacity="0.2"/>
                    </linearGradient>
                </defs>
                <path d="M 50 150 L 150 50 L 250 150 L 350 50" stroke="url(#grid-grad)" stroke-width="2.5" fill="none"/>
                <path d="M 50 50 L 150 150 L 250 50 L 350 150" stroke="url(#grid-grad)" stroke-width="1.5" stroke-dasharray="4,4" fill="none"/>
                <circle cx="150" cy="50" r="5" fill="#2dd4bf"/>
                <circle cx="250" cy="150" r="5" fill="#2dd4bf"/>
                <circle cx="350" cy="50" r="5" fill="#2dd4bf"/>
                <circle cx="50" cy="150" r="5" fill="#2dd4bf"/>
                <circle cx="150" cy="50" r="10" fill="#2dd4bf" fill-opacity="0.25"/>
                <circle cx="250" cy="150" r="10" fill="#2dd4bf" fill-opacity="0.25"/>
            </svg>
        </div>
        
        <div class="cover-metadata">
            <div class="meta-item"><span class="meta-label">Prepared By:</span> {cover_data['author']}</div>
            <div class="meta-item"><span class="meta-label">Date of Issue:</span> {cover_data['date']}</div>
        </div>
    </div>
    """
    
    html_template = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Space+Grotesk:wght@400;500;600;700&display=swap');
            
            @page {{
                size: A4 portrait;
                margin: 2.8cm 2cm 2.8cm 2cm;
                @top-left {{
                    content: none;
                }}
                @top-right {{
                    content: none;
                }}
                @bottom-left {{
                    content: "InsightSwarm Agent Ecosystem";
                    font-family: 'Inter', 'Helvetica Neue', Arial, sans-serif;
                    font-size: 8px;
                    color: #64748b;
                }}
                @bottom-right {{
                    content: "Page " counter(page) " of " counter(pages);
                    font-family: 'Inter', 'Helvetica Neue', Arial, sans-serif;
                    font-size: 8px;
                    color: #64748b;
                }}
            }}
            
            @page :first {{
                size: A4 portrait;
                margin: 0 !important;
                padding: 0 !important;
                @top-left {{ content: none; }}
                @top-right {{ content: none; }}
                @bottom-left {{ content: none; }}
                @bottom-right {{ content: none; }}
            }}
            
            html, body {{
                margin: 0 !important;
                padding: 0 !important;
                font-family: 'Inter', 'Helvetica Neue', Arial, sans-serif;
                line-height: 1.6;
                color: #334155;
                font-size: 13.5px;
            }}
            
            /* Cover Page Styles */
            .cover-page {{
                page-break-after: always;
                page-break-inside: avoid;
                height: 297mm;
                max-height: 297mm;
                width: 210mm;
                max-width: 210mm;
                margin: 0 !important;
                padding: 3.5cm 2.2cm 2cm 2.2cm;
                box-sizing: border-box;
                overflow: hidden;
                background: linear-gradient(135deg, #081115 0%, #030712 100%);
                color: #f8fafc;
                position: relative;
            }}
            .cover-accent-bar {{
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 8px;
                background: linear-gradient(90deg, #14b8a6 0%, #2dd4bf 35%, #6366f1 70%, #8b5cf6 100%);
            }}
            .cover-classification {{
                font-size: 10px;
                font-weight: 700;
                color: #fb7185;
                letter-spacing: 0.1em;
                text-transform: uppercase;
                margin-bottom: 25px;
            }}
            .cover-title-group {{
                margin-bottom: 40px;
            }}
            .cover-title {{
                font-family: 'Space Grotesk', 'Helvetica Neue', Arial, sans-serif;
                font-size: 36px;
                font-weight: 700;
                line-height: 1.15;
                color: #ffffff;
                margin: 0 0 15px 0;
                letter-spacing: -0.02em;
            }}
            .cover-subtitle {{
                font-size: 16px;
                font-weight: 300;
                color: #94a3b8;
                margin: 0;
                line-height: 1.4;
            }}
            .cover-illustration-container {{
                margin: 30px 0;
                opacity: 0.95;
            }}
            .cover-metadata {{
                position: absolute;
                bottom: 1.8cm;
                left: 2.2cm;
                right: 2.2cm;
                border-top: 1px solid rgba(255, 255, 255, 0.12);
                padding-top: 20px;
            }}
            .meta-item {{
                font-size: 11px;
                margin-bottom: 7px;
                color: #cbd5e1;
            }}
            .meta-label {{
                font-weight: 600;
                color: #14b8a6;
                width: 130px;
                display: inline-block;
                text-transform: uppercase;
                letter-spacing: 0.05em;
            }}
            
            /* General Content Styles */
            h1, h2, h3, h4 {{
                font-family: 'Space Grotesk', 'Helvetica Neue', Arial, sans-serif;
                color: #0f172a;
                margin-top: 36px;
                margin-bottom: 16px;
                page-break-after: avoid;
            }}
            h1 {{
                font-size: 24px;
                border-bottom: 2px solid {theme['primary']};
                padding-bottom: 8px;
                margin-top: 45px;
            }}
            h2 {{
                font-size: 18px;
                border-bottom: 1.5px solid #cbd5e1;
                padding-bottom: 8px;
                margin-top: 36px;
            }}
            h3 {{
                font-size: 14px;
                color: {theme['primary']};
                margin-top: 28px;
            }}
            p {{
                margin-top: 0;
                margin-bottom: 20px;
                text-align: justify;
            }}
            ul, ol {{
                margin-top: 0;
                margin-bottom: 18px;
                padding-left: 20px;
            }}
            li {{
                margin-bottom: 6px;
            }}
            a {{
                color: {theme['primary']};
                text-decoration: underline;
                word-break: break-all;
            }}
            a:hover {{
                color: {theme['dark']};
            }}
            
            /* Table of Contents Styles */
            .toc-list {{
                list-style: none;
                padding: 0;
                margin: 25px 0;
            }}
            .toc-list li {{
                position: relative;
                margin-bottom: 12px;
                font-size: 14px;
            }}
            .toc-list li a {{
                display: block;
                position: relative;
                text-decoration: none;
                color: #1e293b;
                overflow: hidden;
            }}
            .toc-list li a::after {{
                content: target-counter(attr(href), page);
                position: absolute;
                right: 0;
                bottom: 0;
                background: #ffffff;
                padding-left: 6px;
                font-weight: 700;
                color: {theme['primary']};
            }}
            .toc-list li a::before {{
                content: "..........................................................................................................................................................................................................................";
                position: absolute;
                left: 0;
                right: 0;
                bottom: 0;
                color: #cbd5e1;
                z-index: 0;
            }}
            .toc-list li a span {{
                background: #ffffff;
                position: relative;
                z-index: 1;
                padding-right: 6px;
                font-weight: 500;
            }}
            
            /* Callout & blockquote styles */
            blockquote {{
                margin: 20px 0;
                padding: 15px 20px;
                background-color: {theme['light']};
                border-left: 4px solid {theme['primary']};
                border-radius: 0 8px 8px 0;
                font-size: 14px;
                color: {theme['dark']};
                line-height: 1.5;
            }}
            blockquote p {{
                margin-bottom: 0;
            }}
            
            .callout-info {{
                margin: 20px 0;
                padding: 15px 20px;
                background-color: {theme['light']};
                border-left: 4px solid {theme['primary']};
                border-radius: 0 8px 8px 0;
                color: {theme['dark']};
            }}
            
            /* General Content Styles */
            h1, h2, h3, h4 {{
                font-family: 'Space Grotesk', 'Helvetica Neue', Arial, sans-serif;
                color: #0f172a;
                margin-top: 36px;
                margin-bottom: 16px;
                page-break-after: avoid;
            }}
            h1 {{
                font-size: 24px;
                border-bottom: 2px solid #0f172a;
                padding-bottom: 8px;
                margin-top: 45px;
            }}
            h2 {{
                font-size: 18px;
                border-bottom: 1.5px solid #cbd5e1;
                padding-bottom: 8px;
                margin-top: 36px;
            }}
            h3 {{
                font-size: 14px;
                color: #0d9488;
                margin-top: 28px;
            }}
            p {{
                margin-top: 0;
                margin-bottom: 20px;
                text-align: justify;
            }}
            ul, ol {{
                margin-top: 0;
                margin-bottom: 18px;
                padding-left: 20px;
            }}
            li {{
                margin-bottom: 6px;
            }}
            a {{
                color: #0d9488;
                text-decoration: underline;
                word-break: break-all;
            }}
            a:hover {{
                color: #0f766e;
            }}
            
            /* Table of Contents Styles */
            .toc-list {{
                list-style: none;
                padding: 0;
                margin: 25px 0;
            }}
            .toc-list li {{
                position: relative;
                margin-bottom: 12px;
                font-size: 14px;
            }}
            .toc-list li a {{
                display: block;
                position: relative;
                text-decoration: none;
                color: #1e293b;
                overflow: hidden;
            }}
            .toc-list li a::after {{
                content: target-counter(attr(href), page);
                position: absolute;
                right: 0;
                bottom: 0;
                background: #ffffff;
                padding-left: 6px;
                font-weight: 700;
                color: #0d9488;
            }}
            .toc-list li a::before {{
                content: "..........................................................................................................................................................................................................................";
                position: absolute;
                left: 0;
                right: 0;
                bottom: 0;
                color: #cbd5e1;
                z-index: 0;
            }}
            .toc-list li a span {{
                background: #ffffff;
                position: relative;
                z-index: 1;
                padding-right: 6px;
                font-weight: 500;
            }}
            
            /* Callout & blockquote styles */
            blockquote {{
                margin: 20px 0;
                padding: 15px 20px;
                background-color: #f0fdfa;
                border-left: 4px solid #0d9488;
                border-radius: 0 8px 8px 0;
                font-size: 14px;
                color: #0f766e;
                line-height: 1.5;
            }}
            blockquote p {{
                margin-bottom: 0;
            }}
            
            .callout-info {{
                margin: 20px 0;
                padding: 15px 20px;
                background-color: #f0fdfa;
                border-left: 4px solid #0d9488;
                border-radius: 0 8px 8px 0;
                color: #0f766e;
            }}
            .callout-warning {{
                margin: 20px 0;
                padding: 15px 20px;
                background-color: #fffbeb;
                border-left: 4px solid #d97706;
                border-radius: 0 8px 8px 0;
                color: #b45309;
            }}
            .callout-danger {{
                margin: 20px 0;
                padding: 15px 20px;
                background-color: #fef2f2;
                border-left: 4px solid #dc2626;
                border-radius: 0 8px 8px 0;
                color: #b91c1c;
            }}
            
            /* KPI Card Grid */
            .kpi-grid {{
                display: flex;
                flex-direction: row;
                justify-content: space-between;
                align-items: stretch;
                margin: 30px 0;
                gap: 20px;
            }}
            .kpi-card {{
                flex: 1;
                background: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                padding: 20px;
                text-align: center;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
                box-sizing: border-box;
            }}
            .kpi-value {{
                display: block;
                font-size: 26px;
                font-weight: 700;
                color: #0d9488;
                font-family: 'Space Grotesk', sans-serif;
                margin-bottom: 4px;
            }}
            .kpi-title {{
                display: block;
                font-size: 10px;
                font-weight: 600;
                text-transform: uppercase;
                color: #64748b;
                letter-spacing: 0.05em;
                margin-bottom: 2px;
            }}
            .kpi-desc {{
                display: block;
                font-size: 10px;
                color: #10b981;
                font-weight: 500;
            }}
            
            /* Comparison Tables */
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 25px 0;
                font-size: 13px;
                page-break-inside: auto;
            }}
            tr {{
                page-break-inside: avoid;
                page-break-after: auto;
            }}
            thead {{
                display: table-header-group;
            }}
            tfoot {{
                display: table-footer-group;
            }}
            th {{
                background-color: #0f172a;
                color: #ffffff;
                font-weight: 600;
                text-align: left;
                padding: 12px 16px;
                border-bottom: 2px solid #cbd5e1;
                vertical-align: bottom;
                word-wrap: break-word;
            }}
            td {{
                padding: 10px 16px;
                border-bottom: 1px solid #e2e8f0;
                color: #334155;
                vertical-align: top;
                word-wrap: break-word;
            }}
            tr:nth-child(even) {{
                background-color: #f8fafc;
            }}
            
            /* Image & Chart Containers */
            .chart-container {{
                margin: 30px auto;
                text-align: center;
                width: 100%;
                max-width: 650px;
                padding: 15px;
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                box-shadow: 0 4px 10px rgba(0, 0, 0, 0.03);
            }}
            .chart-error {{
                background-color: #fef2f2;
                color: #b91c1c;
                border: 1px dashed #f87171;
                padding: 15px;
                border-radius: 8px;
                font-size: 12px;
                margin: 20px 0;
            }}
            
            /* Page break settings */
            .page-break {{
                page-break-before: always;
            }}
            
            /* Code styling */
            code {{
                background-color: #f1f5f9;
                padding: 2px 5px;
                border-radius: 4px;
                font-family: monospace;
                font-size: 12px;
                color: #0f172a;
            }}
            
            /* Citations */
            .references-section {{
                margin-top: 40px;
                border-top: 1px solid #e2e8f0;
                padding-top: 20px;
            }}
            .references-section ol, .references-section ul {{
                margin-left: 1.2em;
                padding-left: 0;
            }}
            .references-section li {{
                margin-bottom: 10px;
            }}
            .references-section a {{
                color: {theme['primary']};
                text-decoration: underline;
            }}
        </style>
    </head>
    <body>
        {cover_html}
        <div class="report-content">
            {raw_html}
        </div>
    </body>
    </html>
    """
    
    report_dir = os.getenv("REPORT_DIR", "reports")
    try:
        os.makedirs(report_dir, exist_ok=True)
    except Exception as e:
        raise OSError(f"Failed to create report directory '{report_dir}': {str(e)}")
        
    file_path = os.path.join(report_dir, f"{run_id}.pdf")
    
    try:
        html_doc = HTML(string=html_template)
        rendered_doc = html_doc.render()
        page_count = len(rendered_doc.pages)
        rendered_doc.write_pdf(file_path)
    except Exception as e:
        raise OSError(f"Failed to generate and save PDF report to '{file_path}': {str(e)}")
        
    return file_path, page_count

