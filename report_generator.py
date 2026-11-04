import os
import sys

# Ensure current directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import io
from typing import Dict, Any, List
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether

REPORTS_DIR = os.path.join(os.path.dirname(__file__), "reports")

def generate_pdf_report(report_data: Dict[str, Any], output_path: str = None) -> str:
    """
    Generate a styled PDF analysis report using ReportLab.
    Returns the file path of the generated PDF.
    """
    if not os.path.exists(REPORTS_DIR):
        os.makedirs(REPORTS_DIR, exist_ok=True)

    if not output_path:
        cand_name = report_data.get("candidate_name", "Candidate").replace(" ", "_")
        output_path = os.path.join(REPORTS_DIR, f"Resume_Analysis_{cand_name}.pdf")

    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#1E293B'),
        alignment=0,
        spaceAfter=4
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#64748B'),
        spaceAfter=12
    )

    h2_style = ParagraphStyle(
        'SectionH2',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=17,
        textColor=colors.HexColor('#2563EB'),
        spaceBefore=10,
        spaceAfter=6
    )

    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#334155')
    )

    bold_body = ParagraphStyle(
        'BoldBody',
        parent=body_style,
        fontName='Helvetica-Bold'
    )

    elements = []

    # Title Header
    elements.append(Paragraph("AI Resume Analysis & Skill Gap Report", title_style))
    elements.append(Paragraph(f"Candidate: <b>{report_data.get('candidate_name', 'Candidate')}</b> | Target Role: <b>{report_data.get('target_role', 'N/A')}</b>", subtitle_style))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#2563EB'), spaceAfter=12))

    # Summary Metrics Box Table
    match_score = report_data.get('match_score', 0)
    strength_score = report_data.get('strength_score', 0)
    found_count = len(report_data.get('found_skills', []))
    missing_count = len(report_data.get('missing_skills', []))

    metrics_data = [
        [
            Paragraph(f"<b>Match Score</b><br/><font size=14 color='#2563EB'><b>{match_score}%</b></font>", body_style),
            Paragraph(f"<b>Resume Strength</b><br/><font size=14 color='#059669'><b>{strength_score}/100</b></font>", body_style),
            Paragraph(f"<b>Skills Found</b><br/><font size=14 color='#4F46E5'><b>{found_count}</b></font>", body_style),
            Paragraph(f"<b>Missing Skills</b><br/><font size=14 color='#DC2626'><b>{missing_count}</b></font>", body_style)
        ]
    ]

    t_metrics = Table(metrics_data, colWidths=[1.75*inch]*4)
    t_metrics.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#E2E8F0')),
        ('INNERGRID', (0, 0), (-1, -1), 1, colors.HexColor('#E2E8F0')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(t_metrics)
    elements.append(Spacer(1, 10))

    # Top Recommended Roles
    elements.append(Paragraph("1. Top Recommended Job Roles", h2_style))
    rec_roles = report_data.get('recommended_roles', [])[:3]
    rec_rows = [["Rank", "Job Role", "Category", "Match Score"]]
    for idx, r in enumerate(rec_roles, 1):
        if isinstance(r, dict):
            rec_rows.append([
                f"#{idx}",
                r.get('target_role', r.get('role_name', '')),
                r.get('category', ''),
                f"{r.get('match_score', 0)}%"
            ])

    t_rec = Table(rec_rows, colWidths=[0.8*inch, 2.7*inch, 2.3*inch, 1.2*inch])
    t_rec.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E293B')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    elements.append(t_rec)
    elements.append(Spacer(1, 10))

    # Skills Breakdown Table
    elements.append(Paragraph("2. Skills Breakdown Analysis", h2_style))
    found_skills_str = ", ".join(report_data.get('found_skills', [])) if report_data.get('found_skills') else "None detected"
    missing_skills_str = ", ".join(report_data.get('missing_skills', [])) if report_data.get('missing_skills') else "No critical missing skills!"

    skills_data = [
        [Paragraph("<b>Detected Technical Skills</b>", bold_body), Paragraph(found_skills_str, body_style)],
        [Paragraph("<b>Missing Required Skills</b>", bold_body), Paragraph(f"<font color='#DC2626'>{missing_skills_str}</font>", body_style)]
    ]
    t_skills = Table(skills_data, colWidths=[2.2*inch, 4.8*inch])
    t_skills.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F1F5F9')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(t_skills)
    elements.append(Spacer(1, 10))

    # AI Suggestions
    elements.append(Paragraph("3. AI Resume Improvement Suggestions", h2_style))
    suggestions = report_data.get('ai_suggestions', [])
    for sug in suggestions:
        elements.append(Paragraph(f"• {sug}", body_style))
        elements.append(Spacer(1, 3))
    elements.append(Spacer(1, 8))

    # Personalized 4-Week Roadmap
    elements.append(Paragraph("4. Personalized 4-Week Learning Roadmap", h2_style))
    roadmap = report_data.get('roadmap', [])
    for item in roadmap:
        if isinstance(item, dict):
            w_title = f"<b>{item.get('week', '')}: {item.get('title', '')}</b>"
            w_focus = f"<i>Focus: {item.get('focus', '')}</i>"
            elements.append(Paragraph(w_title, bold_body))
            elements.append(Paragraph(w_focus, body_style))
            for act in item.get('action_items', []):
                elements.append(Paragraph(f"   - {act}", body_style))
            elements.append(Spacer(1, 4))

    doc.build(elements)
    return output_path

if __name__ == "__main__":
    test_data = {
        "candidate_name": "John Doe",
        "target_role": "Machine Learning Engineer",
        "match_score": 82.5,
        "strength_score": 85.0,
        "found_skills": ["Python", "PyTorch", "Scikit-learn", "Docker", "SQL"],
        "missing_skills": ["MLOps", "TensorFlow", "Feature Engineering"],
        "recommended_roles": [
            {"target_role": "Machine Learning Engineer", "category": "AI", "match_score": 82.5},
            {"target_role": "Data Scientist", "category": "Data Science", "match_score": 78.0},
            {"target_role": "Python Developer", "category": "Software", "match_score": 75.0}
        ],
        "ai_suggestions": ["Quantify achievements using metrics", "Add MLOps skills"],
        "roadmap": [
            {"week": "Week 1", "title": "MLOps & Docker", "focus": "Deploying models", "action_items": ["Study Docker", "Build pipeline"]}
        ]
    }
    pdf_file = generate_pdf_report(test_data)
    print("PDF generated:", pdf_file)
