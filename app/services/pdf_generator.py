"""PDF Resume Generator Module

This module generates professional PDF resumes from the resume data
collected by the AI Resume Builder chatbot.
"""

from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from io import BytesIO


# Professional Color Scheme
PRIMARY_COLOR = HexColor("#2D3E50")     # Dark Blue-Gray
ACCENT_COLOR = HexColor("#3498DB")       # Bright Blue
TEXT_COLOR = HexColor("#333333")         # Dark Gray
LIGHT_TEXT = HexColor("#666666")         # Light Gray


def create_custom_styles():
    """Create custom paragraph styles for the resume"""
    styles = getSampleStyleSheet()
    
    # Name/Header Style
    styles.add(ParagraphStyle(
        name='ResumeHeader',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=PRIMARY_COLOR,
        alignment=TA_CENTER,
        spaceAfter=6,
        fontName='Helvetica-Bold'
    ))
    
    # Contact Info Style
    styles.add(ParagraphStyle(
        name='ContactInfo',
        parent=styles['Normal'],
        fontSize=10,
        textColor=LIGHT_TEXT,
        alignment=TA_CENTER,
        spaceAfter=12
    ))
    
    # Section Header Style
    styles.add(ParagraphStyle(
        name='SectionHeader',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=ACCENT_COLOR,
        spaceBefore=16,
        spaceAfter=8,
        fontName='Helvetica-Bold',
        borderWidth=2,
        borderColor=ACCENT_COLOR,
        borderPadding=4
    ))
    
    # Content Style
    styles.add(ParagraphStyle(
        name='ResumeContent',
        parent=styles['Normal'],
        fontSize=11,
        textColor=TEXT_COLOR,
        spaceAfter=6,
        leading=14
    ))
    
    # Bullet Point Style
    styles.add(ParagraphStyle(
        name='BulletPoint',
        parent=styles['Normal'],
        fontSize=10,
        textColor=TEXT_COLOR,
        leftIndent=20,
        bulletIndent=10,
        spaceAfter=4,
        leading=12
    ))
    
    return styles


def generate_resume_pdf(resume_data: dict, user_name: str = "Your Name") -> bytes:
    """
    Generate a professional PDF resume from the collected resume data.
    """
    buffer = BytesIO()
    # Optimized margins for single page
    doc = SimpleDocTemplate(
        buffer,
        pagesize=LETTER,
        rightMargin=0.5 * inch,
        leftMargin=0.5 * inch,
        topMargin=0.5 * inch,
        bottomMargin=0.5 * inch
    )
    
    styles = create_custom_styles()
    story = []
    
    # =====================
    # HEADER SECTION
    # =====================
    story.append(Paragraph(user_name, styles['ResumeHeader']))
    
    # Contact Information
    contact = resume_data.get("contact", {})
    contact_parts = []
    
    if contact.get("phone"):
        contact_parts.append(contact["phone"])
    if contact.get("email"): # Ensure email is included
        contact_parts.append(contact["email"])
    if contact.get("address"):
        address_line = contact["address"].split('\n')[0]
        contact_parts.append(address_line)
    
    if contact_parts:
        story.append(Paragraph(" • ".join(contact_parts), styles['ContactInfo']))
    
    # Professional Links
    links = []
    if contact.get("linkedin"):
        links.append(f"LinkedIn: {contact['linkedin']}")
    if contact.get("github"):
        links.append(f"GitHub: {contact['github']}")
    if contact.get("portfolio"):
        links.append(f"Portfolio: {contact['portfolio']}")
    
    if links:
        story.append(Paragraph(" | ".join(links), styles['ContactInfo']))
    
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY_COLOR, spaceAfter=8, spaceBefore=4))
    
    # =====================
    # DYNAMIC STRUCTURE LOGIC
    # =====================
    exp_level = resume_data.get("experience_level", "experienced" if resume_data.get("experience") else "fresher")
    
    # Define Section Order based on Experience Level
    if exp_level == "fresher":
        # Fresher: Summary -> Projects -> Skills -> Education -> Achievements -> Experience (if any)
        section_order = ["summary", "projects", "skills", "education", "achievements", "experience"]
    else:
        # Experienced: Summary -> Experience -> Projects -> Skills -> Education -> Achievements
        section_order = ["summary", "experience", "projects", "skills", "education", "achievements"]
        
    for section in section_order:
        
        # --- SUMMARY ---
        if section == "summary":
            # Check for structured summary first, then raw_notes fallback
            summary_text = resume_data.get("summary", "")
            if not summary_text:
                raw_notes = resume_data.get("raw_notes", [])
                if raw_notes:
                    summary_text = " ".join(raw_notes[:2]) # Fallback
            
            if summary_text:
                story.append(Paragraph("PROFESSIONAL SUMMARY", styles['SectionHeader']))
                story.append(Paragraph(summary_text, styles['ResumeContent']))
                
        # --- EXPERIENCE ---
        elif section == "experience":
            experience = resume_data.get("experience", [])
            # Also check raw_notes fallback for backward compatibility
            raw_notes = resume_data.get("raw_notes", [])
            
            if experience or (len(raw_notes) > 2):
                story.append(Paragraph("EXPERIENCE", styles['SectionHeader']))
                
                if experience:
                    for item in experience:
                         story.append(Paragraph(f"• {item}", styles['BulletPoint']))
                else: 
                     # Fallback to raw notes
                     for note in raw_notes[2:]:
                        story.append(Paragraph(f"• {note}", styles['BulletPoint']))

        # --- PROJECTS ---
        elif section == "projects":
            projects = resume_data.get("projects", [])
            if projects:
                story.append(Paragraph("PROJECTS", styles['SectionHeader']))
                for project in projects:
                    story.append(Paragraph(f"• {project}", styles['BulletPoint']))

        # --- SKILLS ---
        elif section == "skills":
            skills = resume_data.get("skills", [])
            if skills:
                story.append(Paragraph("SKILLS", styles['SectionHeader']))
                
                if isinstance(skills, dict):
                    # Categorized Skills: "Category: Skill, Skill"
                    for category, skill_list in skills.items():
                        if isinstance(skill_list, list):
                            text = f"<b>{category}:</b> {', '.join(skill_list)}"
                        else:
                            text = f"<b>{category}:</b> {str(skill_list)}"
                        story.append(Paragraph(text, styles['BulletPoint']))
                        
                elif isinstance(skills, list):
                    # Flat list
                    skills_text = " • ".join(skills)
                    story.append(Paragraph(skills_text, styles['ResumeContent']))
                else:
                    # String fallback
                    story.append(Paragraph(str(skills), styles['ResumeContent']))

        # --- EDUCATION ---
        elif section == "education":
            education = resume_data.get("education", [])
            if education:
                 story.append(Paragraph("EDUCATION", styles['SectionHeader']))
                 if isinstance(education, list):
                     for edu in education:
                         story.append(Paragraph(edu, styles['ResumeContent']))
                 elif isinstance(education, str):
                     for entry in education.split('\n'):
                         if entry.strip():
                             story.append(Paragraph(entry.strip(), styles['ResumeContent']))

        # --- ACHIEVEMENTS ---
        elif section == "achievements":
            achievements = resume_data.get("achievements", [])
            if achievements:
                story.append(Paragraph("ACHIEVEMENTS", styles['SectionHeader']))
                for ach in achievements:
                    story.append(Paragraph(f"• {ach}", styles['BulletPoint']))
    
    # Build PDF
    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    
    return pdf_bytes


def get_pdf_download_data(resume_data: dict, user_name: str = "Your Name") -> tuple:
    """
    Generate PDF and return data suitable for Streamlit download button.
    
    Args:
        resume_data: Dictionary containing resume information
        user_name: Name of the user
    
    Returns:
        tuple: (pdf_bytes, filename, mime_type)
    """
    pdf_bytes = generate_resume_pdf(resume_data, user_name)
    
    # Sanitize filename
    safe_name = "".join(c for c in user_name if c.isalnum() or c in (' ', '_')).rstrip()
    safe_name = safe_name.replace(' ', '_')
    filename = f"{safe_name}_Resume.pdf"
    
    return pdf_bytes, filename, "application/pdf"
