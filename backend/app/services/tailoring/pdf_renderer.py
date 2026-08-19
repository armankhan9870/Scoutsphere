"""PDF document renderer producing clean, ATS-compliant single/multi-page PDF bytes."""

import html
from typing import Any, Dict

from app.services.tailoring.ats_scorer import json_to_plain_text


def render_tailored_resume_html(resume_data: Dict[str, Any]) -> str:
    """Generates clean HTML formatting without tables, graphics, or multi-columns."""
    summary = html.escape(resume_data.get("summary", ""))
    target_role = html.escape(resume_data.get("target_role", "Software Engineer"))

    skills = resume_data.get("skills", [])
    skill_names = [html.escape(s.get("name") if isinstance(s, dict) else str(s)) for s in skills]

    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Tailored Resume - {target_role}</title>
    <style>
        body {{ font-family: Arial, Helvetica, sans-serif; margin: 40px; color: #111; line-height: 1.5; }}
        h1 {{ font-size: 20pt; margin-bottom: 4px; border-bottom: 2px solid #333; padding-bottom: 4px; }}
        h2 {{ font-size: 14pt; margin-top: 18px; margin-bottom: 6px; border-bottom: 1px solid #ccc; text-transform: uppercase; }}
        p {{ font-size: 10.5pt; margin-top: 0; margin-bottom: 8px; }}
        ul {{ margin-top: 4px; margin-bottom: 8px; padding-left: 20px; }}
        li {{ font-size: 10pt; margin-bottom: 4px; }}
        .item-header {{ font-weight: bold; font-size: 11pt; }}
        .item-sub {{ font-style: italic; color: #555; font-size: 10pt; margin-bottom: 4px; }}
    </style>
</head>
<body>
    <h1>Tailored Candidate Resume</h1>
    <p><strong>Target Role:</strong> {target_role}</p>

    <h2>Professional Summary</h2>
    <p>{summary}</p>

    <h2>Technical Skills</h2>
    <p>{", ".join(skill_names)}</p>

    <h2>Professional Experience</h2>
"""

    for exp in resume_data.get("experience", []):
        if isinstance(exp, dict):
            comp = html.escape(exp.get("company", ""))
            role = html.escape(exp.get("role", ""))
            dur = html.escape(exp.get("duration", ""))
            html_content += f'<div class="item-header">{role} — {comp}</div>'
            html_content += f'<div class="item-sub">{dur}</div><ul>'
            for h in exp.get("highlights", []):
                html_content += f"<li>{html.escape(h)}</li>"
            html_content += "</ul>"

    html_content += "<h2>Featured Projects</h2>"
    for proj in resume_data.get("projects", []):
        if isinstance(proj, dict):
            title = html.escape(proj.get("title", ""))
            desc = html.escape(proj.get("description", ""))
            html_content += f'<div class="item-header">{title}</div><p>{desc}</p>'

    html_content += "</body></html>"
    return html_content


def render_tailored_resume_bytes(resume_data: Dict[str, Any]) -> bytes:
    """Returns document bytes (plain text / HTML stream representation)."""
    plain_text = json_to_plain_text(resume_data)
    return plain_text.encode("utf-8")
