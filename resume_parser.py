import os
import sys

# Ensure current directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import re
from typing import Dict, Any, Tuple

# PDF Parsing libraries
try:
    import pypdf
    HAS_PYPDF = True
except ImportError:
    HAS_PYPDF = False

try:
    import PyPDF2
    HAS_PYPDF2 = True
except ImportError:
    HAS_PYPDF2 = False

# DOCX Parsing library
try:
    import docx
    HAS_DOCX = True
except ImportError:
    HAS_DOCX = False

from text_cleaner import preprocess_text

def extract_text_from_pdf(file_path_or_bytes) -> str:
    """Extract raw text from PDF file or file stream."""
    text = ""
    if HAS_PYPDF:
        try:
            reader = pypdf.PdfReader(file_path_or_bytes)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            if text.strip():
                return text
        except Exception as e:
            print(f"pypdf extraction error: {e}")

    if HAS_PYPDF2:
        try:
            reader = PyPDF2.PdfReader(file_path_or_bytes)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            if text.strip():
                return text
        except Exception as e:
            print(f"PyPDF2 extraction error: {e}")

    return text

def extract_text_from_docx(file_path_or_bytes) -> str:
    """Extract raw text from DOCX file or file stream."""
    if not HAS_DOCX:
        raise ImportError("python-docx package is not installed.")
    
    doc = docx.Document(file_path_or_bytes)
    full_text = []
    for para in doc.paragraphs:
        if para.text:
            full_text.append(para.text)
    
    # Also extract text inside tables
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                if cell.text:
                    full_text.append(cell.text)

    return "\n".join(full_text)

def extract_contact_info(text: str) -> Tuple[str, str, str, str]:
    """Extract Email, Phone, LinkedIn, and GitHub links from text."""
    email = ""
    phone = ""
    linkedin = ""
    github = ""

    # Email
    email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
    if email_match:
        email = email_match.group(0)

    # Phone
    phone_match = re.search(r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b', text)
    if phone_match:
        phone = phone_match.group(0)

    # LinkedIn
    linkedin_match = re.search(r'(https?://)?(www\.)?linkedin\.com/in/[A-Za-z0-9_-]+', text, re.IGNORECASE)
    if linkedin_match:
        linkedin = linkedin_match.group(0)

    # GitHub
    github_match = re.search(r'(https?://)?(www\.)?github\.com/[A-Za-z0-9_-]+', text, re.IGNORECASE)
    if github_match:
        github = github_match.group(0)

    return email, phone, linkedin, github

def extract_candidate_name(text: str) -> str:
    """Extract probable candidate name from first few lines of resume."""
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    if not lines:
        return "Candidate"

    for line in lines[:5]:
        # Ignore lines with email, phone, or section headers
        if re.search(r'@|http|\+?\d{8,}|resume|curriculum|cv|education|experience', line, re.IGNORECASE):
            continue
        words = line.split()
        if 1 <= len(words) <= 4 and all(w.isalpha() or w in ['.', '-'] for w in words):
            return line.title()
    
    return lines[0].title() if lines else "Candidate"

def detect_sections(text: str) -> Dict[str, str]:
    """Detect and segment standard resume sections."""
    section_patterns = {
        "Education": r'(education|academic background|qualification|degrees)',
        "Experience": r'(experience|work history|employment|work experience|professional background)',
        "Projects": r'(projects|personal projects|key projects|academic projects)',
        "Skills": r'(skills|technical skills|core competencies|technologies|expertise)',
        "Certifications": r'(certifications|certificates|licenses|courses|accreditation)',
        "Languages": r'(languages|spoken languages)',
        "Summary": r'(summary|profile|objective|about me|professional summary)'
    }

    sections = {key: "" for key in section_patterns}
    
    # Split text into lines
    lines = text.split('\n')
    current_section = "Summary"
    section_lines = {key: [] for key in section_patterns}

    for line in lines:
        line_clean = line.strip().lower()
        matched = False
        for sec_name, pattern in section_patterns.items():
            if re.match(r'^\s*' + pattern + r'\s*$', line_clean, re.IGNORECASE) or \
               re.match(r'^\s*[' + r'#*\-•' + r']?\s*' + pattern + r'\s*[:\-]?\s*$', line_clean, re.IGNORECASE):
                current_section = sec_name
                matched = True
                break
        if not matched:
            if current_section in section_lines:
                section_lines[current_section].append(line)

    for sec_name in section_lines:
        sections[sec_name] = "\n".join(section_lines[sec_name]).strip()

    return sections

def parse_resume(file_path_or_bytes, filename: str) -> Dict[str, Any]:
    """
    Main parser function that accepts PDF, DOCX, or TXT content.
    Returns parsed metadata, section breakdowns, and extracted skills/text.
    """
    ext = os.path.splitext(filename)[1].lower()
    raw_text = ""

    if ext == ".pdf":
        raw_text = extract_text_from_pdf(file_path_or_bytes)
    elif ext in [".docx", ".doc"]:
        raw_text = extract_text_from_docx(file_path_or_bytes)
    elif ext == ".txt":
        if isinstance(file_path_or_bytes, bytes):
            raw_text = file_path_or_bytes.decode('utf-8', errors='ignore')
        elif hasattr(file_path_or_bytes, 'read'):
            raw_text = file_path_or_bytes.read().decode('utf-8', errors='ignore')
        else:
            with open(file_path_or_bytes, 'r', encoding='utf-8', errors='ignore') as f:
                raw_text = f.read()
    else:
        raise ValueError(f"Unsupported file format: {ext}")

    if not raw_text.strip():
        raw_text = "Empty document or text could not be extracted."

    clean_text = preprocess_text(raw_text)
    email, phone, linkedin, github = extract_contact_info(raw_text)
    candidate_name = extract_candidate_name(raw_text)
    sections = detect_sections(raw_text)

    return {
        "filename": filename,
        "raw_text": raw_text,
        "clean_text": clean_text,
        "candidate_name": candidate_name,
        "email": email,
        "phone": phone,
        "linkedin": linkedin,
        "github": github,
        "sections": sections
    }
