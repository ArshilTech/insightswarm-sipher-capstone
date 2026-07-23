import os
import re
import json
import math
import markdown
from dotenv import load_dotenv

load_dotenv()

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
            
import hashlib
from weasyprint import HTML

# --- Professional Color Palettes for Analytics ---

COLOR_PALETTES = [
    {
        "name": "Teal & Emerald",
        "primary": "#0d9488",
        "secondary": "#10b981",
        "kpi_bg": "#f0fdfa",
        "kpi_border": "#ccfbf1",
        "chart_colors": ["#0d9488", "#6366f1", "#0f766e", "#fb7185", "#f59e0b", "#10b981", "#3b82f6"]
    },
    {
        "name": "Sapphire & Slate",
        "primary": "#2563eb",
        "secondary": "#0284c7",
        "kpi_bg": "#eff6ff",
        "kpi_border": "#bfdbfe",
        "chart_colors": ["#2563eb", "#0284c7", "#3b82f6", "#06b6d4", "#6366f1", "#4f46e5", "#0891b2"]
    },
    {
        "name": "Violet & Indigo",
        "primary": "#7c3aed",
        "secondary": "#4f46e5",
        "kpi_bg": "#f5f3ff",
        "kpi_border": "#ddd6fe",
        "chart_colors": ["#7c3aed", "#4f46e5", "#9333ea", "#2563eb", "#c026d3", "#0284c7", "#6366f1"]
    },
    {
        "name": "Forest Emerald & Cyan",
        "primary": "#059669",
        "secondary": "#0891b2",
        "kpi_bg": "#ecfdf5",
        "kpi_border": "#a7f3d0",
        "chart_colors": ["#059669", "#0891b2", "#10b981", "#3b82f6", "#d97706", "#4f46e5", "#059669"]
    },
    {
        "name": "Warm Amber & Terracotta",
        "primary": "#d97706",
        "secondary": "#ea580c",
        "kpi_bg": "#fffbeb",
        "kpi_border": "#fde68a",
        "chart_colors": ["#d97706", "#ea580c", "#dc2626", "#ca8a04", "#059669", "#2563eb", "#7c3aed"]
    },
    {
        "name": "Crimson Rose & Magenta",
        "primary": "#e11d48",
        "secondary": "#9333ea",
        "kpi_bg": "#fff1f2",
        "kpi_border": "#fecdd3",
        "chart_colors": ["#e11d48", "#9333ea", "#2563eb", "#f59e0b", "#10b981", "#0284c7", "#c026d3"]
    },
    {
        "name": "Midnight Cobalt & Cyan",
        "primary": "#4338ca",
        "secondary": "#06b6d4",
        "kpi_bg": "#eef2ff",
        "kpi_border": "#c7d2fe",
        "chart_colors": ["#4338ca", "#06b6d4", "#3b82f6", "#8b5cf6", "#10b981", "#f59e0b", "#ec4899"]
    },
    {
        "name": "Ocean Sky & Teal",
        "primary": "#0284c7",
        "secondary": "#0d9488",
        "kpi_bg": "#f0f9ff",
        "kpi_border": "#bae6fd",
        "chart_colors": ["#0284c7", "#0d9488", "#2563eb", "#10b981", "#7c3aed", "#f59e0b", "#06b6d4"]
    },
    {
        "name": "Dark Cyan & Emerald",
        "primary": "#0891b2",
        "secondary": "#10b981",
        "kpi_bg": "#ecfeff",
        "kpi_border": "#a5f3fc",
        "chart_colors": ["#0891b2", "#10b981", "#6366f1", "#e11d48", "#f59e0b", "#2563eb", "#059669"]
    },
    {
        "name": "Bronze Gold & Ochre",
        "primary": "#b45309",
        "secondary": "#d97706",
        "kpi_bg": "#fffbe6",
        "kpi_border": "#fef08a",
        "chart_colors": ["#b45309", "#d97706", "#475569", "#0f766e", "#334155", "#1e293b", "#0284c7"]
    }
]

def get_palette_for_run(run_id: str) -> dict:
    if not run_id:
        return COLOR_PALETTES[0]
    hash_val = int(hashlib.md5(run_id.encode('utf-8')).hexdigest(), 16)
    return COLOR_PALETTES[hash_val % len(COLOR_PALETTES)]

# --- Helper Functions for SVG Chart & Diagram Generation ---

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

def wrap_text_to_lines(text: str, max_chars: int = 65) -> list[str]:
    """Wraps long text strings into clean multi-line segments to prevent box overflow in SVG."""
    words = text.split()
    if not words:
        return []
    lines = []
    current_line = []
    current_length = 0
    for word in words:
        if len(word) > max_chars:
            word = word[:max_chars - 3] + "..."
        if current_length + len(word) + (1 if current_line else 0) <= max_chars:
            current_line.append(word)
            current_length += len(word) + (1 if len(current_line) > 1 else 0)
        else:
            if current_line:
                lines.append(" ".join(current_line))
            current_line = [word]
            current_length = len(word)
    if current_line:
        lines.append(" ".join(current_line))
    return lines

def draw_block_diagram(diagram_data: dict, palette: dict = None) -> str:
    if palette is None:
        palette = COLOR_PALETTES[0]
        
    title = diagram_data.get("title", "Hierarchical Architecture & Process Workflow")
    nodes = diagram_data.get("nodes", [])
    connections = diagram_data.get("connections", [])
    
    if not nodes:
        return "<!-- Empty diagram nodes -->"
        
    svg_width = 650
    header_h = 55
    gap_y = 30  # Vertical spacing between nodes
    
    primary = palette.get("primary", "#0d9488")
    kpi_bg = palette.get("kpi_bg", "#f0fdfa")
    kpi_border = palette.get("kpi_border", "#ccfbf1")
    marker_id = f"arrow-{primary.replace('#', '')}"
    
    # Pre-calculate node levels, heights, and positions
    node_details = []
    current_y = header_h
    node_id_map = {}
    
    for i, node in enumerate(nodes):
        node_id = node.get("id", f"node_{i}")
        heading = node.get("heading") or node.get("label") or node.get("title") or f"Component {i+1}"
        bullets_raw = node.get("bullet_points") or node.get("items") or node.get("details")
        
        if not bullets_raw:
            subtext = node.get("subtext") or node.get("description") or node.get("desc") or ""
            if subtext:
                bullets_raw = [s.strip() for s in subtext.split("\n") if s.strip()]
            else:
                bullets_raw = []
        elif isinstance(bullets_raw, str):
            bullets_raw = [s.strip() for s in bullets_raw.split("\n") if s.strip()]
            
        # Determine hierarchy level (default: level 1 or derived from parent_id / level key)
        level = int(node.get("level", 1))
        parent_id = node.get("parent") or node.get("parent_id")
        if parent_id and parent_id in node_id_map:
            level = node_id_map[parent_id]["level"] + 1
            
        level = min(3, max(1, level))  # Max 3 levels
        
        # Calculate indent and width based on hierarchy level
        indent_x = 65 + (level - 1) * 35
        node_w = 520 - (level - 1) * 35
        
        # Wrap bullets into lines to guarantee text NEVER overflows
        processed_bullets = []
        total_text_lines = 0
        max_chars_for_width = int((node_w - 45) / 7.2)
        
        for item in bullets_raw[:4]:
            wrapped = wrap_text_to_lines(str(item), max_chars=max_chars_for_width)
            if wrapped:
                processed_bullets.append(wrapped)
                total_text_lines += len(wrapped)
                
        line_count = max(1, total_text_lines)
        node_h = max(68, 36 + line_count * 17)
        
        detail = {
            "id": node_id,
            "index": i + 1,
            "level": level,
            "parent_id": parent_id,
            "heading": heading,
            "bullets": processed_bullets,
            "x": indent_x,
            "w": node_w,
            "y": current_y,
            "h": node_h,
            "cx": indent_x + node_w / 2,
            "cy": current_y + node_h / 2
        }
        
        node_details.append(detail)
        node_id_map[node_id] = detail
        current_y += node_h + gap_y
        
    svg_height = int(current_y - gap_y + 25)
    
    # Map connections
    connection_map = {}
    for conn in connections:
        from_id = conn.get("from")
        if from_id:
            connection_map[from_id] = conn.get("label", "")
            
    svg = f'<svg viewBox="0 0 {svg_width} {svg_height}" width="100%" height="{svg_height}" class="chart-diagram" xmlns="http://www.w3.org/2000/svg">\n'
    svg += '  <defs>\n'
    svg += f'    <marker id="{marker_id}" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">\n'
    svg += f'      <path d="M 0 0 L 10 5 L 0 10 z" fill="{primary}" />\n'
    svg += '    </marker>\n'
    svg += '  </defs>\n'
    svg += '  <style>\n'
    svg += '    .d-title { font-family: "Space Grotesk", "Helvetica Neue", sans-serif; font-size: 18px; font-weight: 700; fill: #0f172a; }\n'
    svg += f'    .d-heading {{ font-family: "Space Grotesk", "Helvetica Neue", sans-serif; font-size: 13px; font-weight: 700; fill: {primary}; }}\n'
    svg += f'    .d-badge {{ font-family: "Space Grotesk", "Helvetica Neue", sans-serif; font-size: 9px; font-weight: 700; fill: #ffffff; }}\n'
    svg += '    .d-body { font-family: "Inter", "Helvetica Neue", sans-serif; font-size: 10.5px; fill: #334155; }\n'
    svg += f'    .d-conn-label {{ font-family: "Inter", "Helvetica Neue", sans-serif; font-size: 9px; fill: {primary}; font-weight: 600; text-anchor: middle; }}\n'
    svg += '    .d-conn-bg { fill: #ffffff; opacity: 0.95; }\n'
    svg += '  </style>\n'
    
    # Centered Title at top
    svg += f'  <text x="{svg_width/2}" y="30" class="d-title" text-anchor="middle">{title}</text>\n'
    
    # Draw Nodes & Connectors
    for i, item in enumerate(node_details):
        nx = item["x"]
        ny = item["y"]
        nw = item["w"]
        nh = item["h"]
        heading = item["heading"]
        bullets = item["bullets"]
        level = item["level"]
        parent_id = item["parent_id"]
        
        # Rounded rectangle box with level-based styling
        stroke_w = 1.5 if level == 1 else 1.2
        svg += f'  <rect x="{nx}" y="{ny}" width="{nw}" height="{nh}" rx="8" ry="8" fill="{kpi_bg}" stroke="{primary}" stroke-width="{stroke_w}" />\n'
        
        # Step / Phase Badge
        badge_text = f"PHASE {item['index']}" if level == 1 else f"LEVEL {level}"
        badge_w = len(badge_text) * 5.5 + 10
        svg += f'  <rect x="{nx + nw - badge_w - 12}" y="{ny + 10}" width="{badge_w}" height="14" rx="4" fill="{primary}" />\n'
        svg += f'  <text x="{nx + nw - badge_w/2 - 12}" y="{ny + 20.5}" class="d-badge" text-anchor="middle">{badge_text}</text>\n'
        
        # Bold Heading
        svg += f'  <text x="{nx + 18}" y="{ny + 22}" class="d-heading">{heading}</text>\n'
        
        # Wrapped Bullet Points / Descriptions
        text_y = ny + 40
        for b_group in bullets:
            for line_idx, line in enumerate(b_group):
                prefix = "• " if line_idx == 0 else "  "
                svg += f'  <text x="{nx + 22}" y="{text_y}" class="d-body">{prefix}{line}</text>\n'
                text_y += 17
                
        # Vertical Downward Connector Arrow to Next Node
        if i < len(node_details) - 1:
            next_item = node_details[i + 1]
            
            # Check if branching from explicit parent or sequential vertical flow
            if parent_id and parent_id in node_id_map:
                p_item = node_id_map[parent_id]
                x1 = p_item["x"] + 20
                y1 = p_item["y"] + p_item["h"]
                x2 = nx + 20
                y2 = ny
                svg += f'  <path d="M {x1} {y1} V {ny - 15} H {x2} V {y2}" fill="none" stroke="{primary}" stroke-width="1.2" stroke-dasharray="3,3" marker-end="url(#{marker_id})" />\n'
            else:
                y1 = ny + nh
                y2 = next_item["y"]
                conn_x = nx + nw / 2 if nw == next_item["w"] else svg_width / 2
                
                conn_label = connection_map.get(item["id"], "")
                if not conn_label and i < len(connections):
                    conn_label = connections[i].get("label", "")
                    
                svg += f'  <line x1="{conn_x}" y1="{y1}" x2="{conn_x}" y2="{y2}" stroke="{primary}" stroke-width="1.5" marker-end="url(#{marker_id})" />\n'
                
                if conn_label:
                    mid_y = y1 + (gap_y / 2)
                    label_len = len(conn_label) * 6.5 + 14
                    svg += f'  <rect x="{conn_x - label_len/2}" y="{mid_y - 9}" width="{label_len}" height="15" rx="3" class="d-conn-bg" stroke="{kpi_border}" stroke-width="0.8" />\n'
                    svg += f'  <text x="{conn_x}" y="{mid_y + 2}" class="d-conn-label">{conn_label}</text>\n'
                    
    svg += '</svg>\n'
    return svg

def draw_bar_chart(title, labels, values, x_label, y_label, palette: dict = None):
    if palette is None:
        palette = COLOR_PALETTES[0]
        
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
    colors = palette.get("chart_colors", ["#0d9488", "#6366f1", "#0f766e", "#fb7185", "#f59e0b", "#10b981", "#3b82f6"])
    
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

def draw_donut_chart(title, labels, values, palette: dict = None):
    if palette is None:
        palette = COLOR_PALETTES[0]
        
    svg_width = 650
    svg_height = 290
    cx = 170
    cy = 145
    r_out = 90
    r_in = 55
    
    total = sum(values)
    if total <= 0:
        total = 1
        
    colors = palette.get("chart_colors", ["#0d9488", "#6366f1", "#0f766e", "#fb7185", "#f59e0b", "#10b981", "#3b82f6"])
    
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

def draw_line_chart(title, labels, values, x_label, y_label, area=False, palette: dict = None):
    if palette is None:
        palette = COLOR_PALETTES[0]
        
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
    primary = palette.get("primary", "#0d9488")
    
    svg = f'<svg viewBox="0 0 {svg_width} {svg_height}" width="100%" height="{svg_height}" class="chart-line" xmlns="http://www.w3.org/2000/svg">\n'
    svg += '  <style>\n'
    svg += '    .c-title { font-family: "Space Grotesk", "Helvetica Neue", sans-serif; font-size: 15px; font-weight: 600; fill: #0f172a; }\n'
    svg += '    .c-axis-label { font-family: "Inter", "Helvetica Neue", sans-serif; font-size: 10px; fill: #64748b; font-weight: 500; }\n'
    svg += '    .c-tick-label { font-family: "Inter", "Helvetica Neue", sans-serif; font-size: 9px; fill: #64748b; }\n'
    svg += '    .c-grid-line { stroke: #e2e8f0; stroke-width: 1; stroke-dasharray: 2 2; }\n'
    svg += '    .c-axis { stroke: #cbd5e1; stroke-width: 1.5; }\n'
    svg += f'    .c-line {{ stroke: {primary}; stroke-width: 3; fill: none; stroke-linecap: round; stroke-linejoin: round; }}\n'
    svg += '    .c-area { fill: url(#area-grad); stroke: none; }\n'
    svg += f'    .c-point {{ fill: {primary}; stroke: #ffffff; stroke-width: 2; }}\n'
    svg += f'    .c-point-val {{ font-family: "Inter", "Helvetica Neue", sans-serif; font-size: 9px; fill: {primary}; font-weight: 600; text-anchor: middle; }}\n'
    svg += '  </style>\n'
    
    svg += '  <defs>\n'
    svg += '    <linearGradient id="area-grad" x1="0" y1="0" x2="0" y2="1">\n'
    svg += f'      <stop offset="0%" stop-color="{primary}" stop-opacity="0.35"/>\n'
    svg += f'      <stop offset="100%" stop-color="{primary}" stop-opacity="0.0"/>\n'
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
        svg += f'  <circle cx="{x}" cy="{y}" r="4.5" class="c-point" />\n'
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

def generate_svg_chart(chart_data: dict, palette: dict = None) -> str:
    if palette is None:
        palette = COLOR_PALETTES[0]
        
    chart_type = chart_data.get("type", "bar").lower()
    title = chart_data.get("title", "")
    labels = chart_data.get("labels", [])
    values = chart_data.get("values", [])
    x_label = chart_data.get("x_label", "")
    y_label = chart_data.get("y_label", "")
    
    if chart_type in ("block_diagram", "diagram", "architecture"):
        return draw_block_diagram(chart_data, palette)
        
    if not labels or not values:
        return "<!-- Chart missing data labels or values -->"
        
    try:
        values = [float(v) for v in values]
    except Exception:
        return "<!-- Invalid numeric data in chart -->"
        
    if chart_type in ("donut", "pie"):
        return draw_donut_chart(title, labels, values, palette=palette)
    elif chart_type == "line":
        return draw_line_chart(title, labels, values, x_label, y_label, area=False, palette=palette)
    elif chart_type == "area":
        return draw_line_chart(title, labels, values, x_label, y_label, area=True, palette=palette)
    else:
        return draw_bar_chart(title, labels, values, x_label, y_label, palette=palette)

def process_charts(markdown_content: str, palette: dict = None) -> str:
    pattern = r"```(?:json-chart|json-diagram)\s*\n(.*?)\n\s*```"
    
    def replacer(match):
        json_str = match.group(1)
        try:
            chart_data = json.loads(json_str)
            svg_content = generate_svg_chart(chart_data, palette=palette)
            return f'<div class="chart-container">{svg_content}</div>'
        except Exception as e:
            return f'<div class="chart-error">Chart Rendering Error: {str(e)}</div>'
            
    return re.sub(pattern, replacer, markdown_content, flags=re.DOTALL)

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

def generate_pdf_report(markdown_content: str, run_id: str) -> tuple[str, int]:
    """Converts Markdown text to a highly-styled consulting-firm grade PDF report."""
    
    palette = get_palette_for_run(run_id)
    cover_data, body_markdown = extract_cover_data(markdown_content)
    body_markdown = ensure_markdown_spacing(body_markdown)
    body_markdown = process_charts(body_markdown, palette=palette)
    raw_html = markdown.markdown(body_markdown, extensions=['tables', 'fenced_code'])
    
    # Remove KPI Dashboard heading entirely to match Demo design (where the cards render below TOC directly)
    raw_html = re.sub(r'<h[12][^>]*>.*?KPI Dashboard.*?</h[12]>\s*', '', raw_html, flags=re.IGNORECASE)
    
    # Strip markdown asterisks inside HTML spans (like KPI card titles)
    raw_html = re.sub(r'(<span[^>]*>\s*)\*\*(.*?)\*\*(\s*</span>)', r'\1\2\3', raw_html)
    raw_html = re.sub(r'(<span[^>]*>\s*)\*(.*?)\*(\s*</span>)', r'\1\2\3', raw_html)
    
    # Convert main numbered headings & References to h1
    raw_html = convert_headings(raw_html)
    
    raw_html = process_toc(raw_html)
    raw_html = inject_page_breaks(raw_html)
    
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
                        <stop offset="0%" stop-color="#2dd4bf" stop-opacity="0.85"/>
                        <stop offset="100%" stop-color="#0f766e" stop-opacity="0.1"/>
                    </linearGradient>
                </defs>
                <path d="M 50 150 L 150 50 L 250 150 L 350 50" stroke="url(#grid-grad)" stroke-width="2.5" fill="none"/>
                <path d="M 50 50 L 150 150 L 250 50 L 350 150" stroke="url(#grid-grad)" stroke-width="1.5" stroke-dasharray="4,4" fill="none"/>
                <circle cx="150" cy="50" r="5" fill="#2dd4bf"/>
                <circle cx="250" cy="150" r="5" fill="#2dd4bf"/>
                <circle cx="350" cy="50" r="5" fill="#2dd4bf"/>
                <circle cx="50" cy="150" r="5" fill="#2dd4bf"/>
                <circle cx="150" cy="50" r="10" fill="#2dd4bf" fill-opacity="0.2"/>
                <circle cx="250" cy="150" r="10" fill="#2dd4bf" fill-opacity="0.2"/>
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
                size: A4;
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
                margin: 0;
                @top-left {{ content: none; }}
                @top-right {{ content: none; }}
                @bottom-left {{ content: none; }}
                @bottom-right {{ content: none; }}
            }}
            
            body {{
                font-family: 'Inter', 'Helvetica Neue', Arial, sans-serif;
                line-height: 1.6;
                color: #334155;
                font-size: 13.5px;
            }}
            
            /* Cover Page Styles */
            .cover-page {{
                page-break-after: always;
                height: 29.7cm;
                width: 21.0cm;
                background: linear-gradient(135deg, #081115 0%, #030712 100%);
                color: #f8fafc;
                position: relative;
                padding: 4.5cm 2.2cm 2cm 2.2cm;
                box-sizing: border-box;
            }}
            .cover-accent-bar {{
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 8px;
                background: linear-gradient(90deg, #2dd4bf 0%, #0d9488 50%, #6366f1 100%);
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
                margin: 40px 0;
                opacity: 0.95;
            }}
            .cover-metadata {{
                position: absolute;
                bottom: 2.5cm;
                left: 2.2cm;
                right: 2.2cm;
                border-top: 1px solid rgba(255, 255, 255, 0.12);
                padding-top: 25px;
            }}
            .meta-item {{
                font-size: 11px;
                margin-bottom: 7px;
                color: #cbd5e1;
            }}
            .meta-label {{
                font-weight: 600;
                color: #2dd4bf;
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
                background: {palette['kpi_bg']};
                border: 1px solid {palette['kpi_border']};
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
                color: {palette['primary']};
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
                color: {palette['secondary']};
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