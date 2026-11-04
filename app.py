import os
import sys

# Ensure current directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import json
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Configure Streamlit page layout & theme
st.set_page_config(
    page_title="AI Resume Analyzer & Job Recommender",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Glassmorphic & Modern CSS Styling
st.markdown("""
<style>
    /* Dark Theme Default Palette */
    :root {
        --bg-main: #0F172A;
        --card-bg: rgba(30, 41, 59, 0.7);
        --accent-blue: #3B82F6;
        --accent-purple: #8B5CF6;
        --accent-emerald: #10B981;
        --accent-rose: #F43F5E;
        --text-primary: #F8FAFC;
        --text-secondary: #94A3B8;
        --border-color: rgba(255, 255, 255, 0.1);
    }
    
    .main {
        background-color: var(--bg-main);
        font-family: 'Inter', sans-serif;
    }
    
    /* Header Gradient Banner */
    .header-banner {
        background: linear-gradient(135deg, #1E1B4B 0%, #312E81 50%, #4338CA 100%);
        padding: 1.8rem 2rem;
        border-radius: 16px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
        margin-bottom: 2rem;
        border: 1px solid rgba(255, 255, 255, 0.15);
    }
    
    .header-title {
        font-size: 2.2rem;
        font-weight: 800;
        color: #FFFFFF;
        margin: 0;
        letter-spacing: -0.5px;
    }
    
    .header-subtitle {
        font-size: 1rem;
        color: #C7D2FE;
        margin-top: 0.4rem;
        margin-bottom: 0;
    }

    /* Metric Cards */
    .metric-card {
        background: rgba(30, 41, 59, 0.75);
        backdrop-filter: blur(12px);
        border: 1px solid var(--border-color);
        border-radius: 14px;
        padding: 1.2rem;
        text-align: center;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 20px -5px rgba(0, 0, 0, 0.4);
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 800;
        margin: 0.2rem 0;
    }
    .metric-label {
        font-size: 0.85rem;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Skill Badges */
    .skill-badge-found {
        display: inline-block;
        background: rgba(16, 185, 129, 0.15);
        color: #34D399;
        border: 1px solid rgba(16, 185, 129, 0.4);
        padding: 0.35rem 0.75rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin: 0.25rem;
    }
    
    .skill-badge-missing {
        display: inline-block;
        background: rgba(244, 63, 94, 0.15);
        color: #FB7185;
        border: 1px solid rgba(244, 63, 94, 0.4);
        padding: 0.35rem 0.75rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin: 0.25rem;
    }
    
    /* Job Match Card */
    .job-card {
        background: rgba(15, 23, 42, 0.6);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.75rem;
    }
    
    /* Roadmap Week Box */
    .roadmap-week {
        background: rgba(30, 41, 59, 0.5);
        border-left: 4px solid var(--accent-blue);
        border-radius: 8px;
        padding: 1rem 1.2rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Imports from modular packages
from database import (
    init_db, save_resume, save_report, get_user_reports, 
    get_report_by_id, get_all_job_roles, get_all_skills
)
from auth import register_user, authenticate_user
from resume_parser import parse_resume
from skill_extractor import extract_skills
from job_matcher import (
    match_resume_with_job, recommend_top_job_roles, 
    analyze_resume_strength, generate_ai_suggestions,
    HAS_SENTENCE_TRANSFORMERS
)
from roadmap_generator import generate_learning_roadmap
from report_generator import generate_pdf_report

# Ensure SQLite DB & datasets are initialized
init_db()

# Session State Initialization
if "user" not in st.session_state:
    st.session_state.user = None
if "current_analysis" not in st.session_state:
    st.session_state.current_analysis = None
if "use_semantic" not in st.session_state:
    st.session_state.use_semantic = False

# Sidebar Navigation
with st.sidebar:
    st.image("https://img.icons8.com/isometric/96/resume.png", width=64)
    st.title("AI Resume Hub")
    
    if st.session_state.user:
        st.success(f"Logged in as: **{st.session_state.user['username']}**")
        if st.button("Logout", key="logout_btn"):
            st.session_state.user = None
            st.rerun()
    else:
        st.info("Guest Mode (Optional Login)")
    
    st.markdown("---")
    menu = st.radio(
        "Navigation",
        ["Upload & Analyze", "Analysis History", "Job Catalog", "Skill Matrix", "Account & Settings"]
    )
    
    st.markdown("---")
    st.markdown("### Matching Engine")
    st.session_state.use_semantic = st.checkbox(
        "Enable Semantic Matching (SentenceTransformers)", 
        value=st.session_state.use_semantic,
        disabled=not HAS_SENTENCE_TRANSFORMERS,
        help="Uses deep contextual neural embeddings alongside TF-IDF cosine similarity."
    )
    if not HAS_SENTENCE_TRANSFORMERS:
        st.caption("⚠️ `sentence-transformers` package not detected. Using TF-IDF + Cosine Similarity.")

# Sample Demo Resumes
SAMPLE_RESUMES = {
    "AI / ML Engineer Resume": """
JANE DOE
Email: jane.doe@example.com | Phone: (555) 123-4567 | GitHub: github.com/janedoe | LinkedIn: linkedin.com/in/janedoe

PROFESSIONAL SUMMARY
Experienced Machine Learning Engineer with 3+ years of hands-on expertise building and deploying deep learning models, NLP pipelines, and REST microservices in Python.

EDUCATION
B.S. in Computer Science - Stanford University (2021)

TECHNICAL SKILLS
- Programming: Python, C++, SQL, Shell Scripting
- AI & ML: Machine Learning, PyTorch, Scikit-learn, TensorFlow, Deep Learning, NLP, spaCy, Transformers, Hugging Face
- Tools & Cloud: Docker, Git, AWS, Linux, MLOps, PostgreSQL, REST APIs

EXPERIENCE
Machine Learning Engineer | AI Solutions Inc. (2022 - Present)
- Engineered end-to-end NLP classification models using PyTorch & Hugging Face Transformers, improving accuracy by 18%.
- Built automated MLOps CI/CD pipelines with Docker & AWS SageMaker to deploy models.
- Optimized vector databases and reduced API inference latency by 35%.

PROJECTS
- Generative AI Chatbot: Built RAG application using LangChain, OpenAI API, and Vector Databases.
- Image Recognition System: Developed object detection model using OpenCV, PyTorch, and YOLO.
""",
    "Data Analyst Resume": """
ALEX SMITH
Email: alex.smith@example.com | Phone: (555) 987-6543 | LinkedIn: linkedin.com/in/alexsmith

SUMMARY
Data Analyst with 2 years of experience analyzing complex datasets, building interactive Power BI & Tableau dashboards, and performing statistical modeling in Python & SQL.

EDUCATION
B.A. in Statistics - University of Michigan (2022)

TECHNICAL SKILLS
- Analytics & Viz: Python, SQL, Tableau, Power BI, Excel, Pandas, NumPy, Data Visualization, Statistics, ETL, Data Cleaning
- Databases: PostgreSQL, MySQL

EXPERIENCE
Data Analyst | Retail Insights Co. (2022 - Present)
- Built 15+ automated executive Power BI dashboards to track sales metrics across 200+ retail branches.
- Performed statistical A/B testing and customer segmentation analysis in Python & SQL, driving $500K revenue growth.
"""
}

# HEADER BANNER
st.markdown("""
<div class="header-banner">
    <div class="header-title">AI Resume Analyzer & Job Recommender</div>
    <div class="header-subtitle">NLP-powered resume scoring, missing skill gap analysis, and personalized 4-week learning roadmaps</div>
</div>
""", unsafe_allow_html=True)

# TAB 1: UPLOAD & ANALYZE
if menu == "Upload & Analyze":
    st.markdown("### 📤 Step 1: Upload Resume or Load Sample Demo")
    
    col_up1, col_up2 = st.columns([2, 1])
    
    with col_up1:
        uploaded_file = st.file_uploader(
            "Upload your resume (PDF, DOCX, or TXT format)",
            type=["pdf", "docx", "txt"],
            help="Maximum file size 10MB"
        )
        
    with col_up2:
        st.markdown("**Or Test with Sample Data:**")
        sample_choice = st.selectbox("Select Sample Resume", ["Select sample..."] + list(SAMPLE_RESUMES.keys()))
        use_sample_btn = st.button("Load Selected Sample", type="secondary")

    resume_content = None
    filename = ""

    if uploaded_file is not None:
        filename = uploaded_file.name
        resume_content = uploaded_file.getvalue()
    elif use_sample_btn and sample_choice != "Select sample...":
        filename = f"{sample_choice.replace(' ', '_')}.txt"
        resume_content = SAMPLE_RESUMES[sample_choice].encode('utf-8')
        st.success(f"Loaded sample: **{sample_choice}**")

    # Select Target Job Role
    df_roles = get_all_job_roles()
    role_names = df_roles["role_name"].tolist() if not df_roles.empty else [
        "Data Analyst", "Machine Learning Engineer", "AI Engineer", "NLP Engineer",
        "Computer Vision Engineer", "Python Developer", "Full Stack Developer",
        "Java Developer", "Data Scientist", "Cloud Engineer"
    ]
    
    st.markdown("---")
    st.markdown("### 🎯 Step 2: Select Target Job Role")
    target_role_name = st.selectbox("Select your target role to calculate match score & skill gaps:", role_names, index=1)

    if resume_content is not None:
        if st.button("🚀 Analyze Resume & Recommend Roles", type="primary", use_container_width=True):
            with st.spinner("Parsing resume text, extracting NLP skills, and computing match vectors..."):
                parsed = parse_resume(resume_content, filename)
                raw_text = parsed["raw_text"]
                
                # Save resume in SQLite
                user_id = st.session_state.user["id"] if st.session_state.user else None
                resume_id = save_resume(filename, parsed["filename"].split('.')[-1], raw_text, user_id=user_id)
                
                # Extract skills & match against target role
                extracted_skills = extract_skills(raw_text)
                found_skills = extracted_skills["found_skills"]
                
                match_res = match_resume_with_job(raw_text, target_role_name, use_semantic=st.session_state.use_semantic)
                top_recommendations = recommend_top_job_roles(raw_text, top_n=3, use_semantic=st.session_state.use_semantic)
                
                # Strength analysis & Suggestions
                strength_info = analyze_resume_strength(raw_text, parsed["sections"], found_skills)
                ai_suggs = generate_ai_suggestions(strength_info, match_res["missing_skills"], target_role_name)
                
                # Learning Roadmap
                roadmap = generate_learning_roadmap(target_role_name, match_res["missing_skills"], found_skills)
                
                # PDF Report Generation Data
                report_data = {
                    "candidate_name": parsed["candidate_name"],
                    "target_role": target_role_name,
                    "match_score": match_res["match_score"],
                    "strength_score": strength_info["total_strength_score"],
                    "found_skills": found_skills,
                    "missing_skills": match_res["missing_skills"],
                    "recommended_roles": top_recommendations,
                    "ai_suggestions": ai_suggs,
                    "roadmap": roadmap
                }
                
                pdf_path = generate_pdf_report(report_data)
                
                # Save report in DB
                report_id = save_report(
                    resume_id=resume_id,
                    candidate_name=parsed["candidate_name"],
                    target_role=target_role_name,
                    match_score=match_res["match_score"],
                    recommended_roles=top_recommendations,
                    found_skills=found_skills,
                    missing_skills=match_res["missing_skills"],
                    strength_score=strength_info["total_strength_score"],
                    sections_detected=parsed["sections"],
                    roadmap_json=roadmap,
                    ai_suggestions=ai_suggs,
                    user_id=user_id
                )
                
                # Store in session state
                st.session_state.current_analysis = {
                    "parsed": parsed,
                    "match_res": match_res,
                    "top_recommendations": top_recommendations,
                    "strength_info": strength_info,
                    "ai_suggs": ai_suggs,
                    "roadmap": roadmap,
                    "pdf_path": pdf_path,
                    "report_data": report_data
                }
                st.success("Analysis Complete!")

    # DISPLAY ANALYSIS RESULTS
    if st.session_state.current_analysis:
        an = st.session_state.current_analysis
        match_res = an["match_res"]
        parsed = an["parsed"]
        strength = an["strength_info"]
        top_recs = an["top_recommendations"]
        
        st.markdown("---")
        st.markdown("## 📊 Analysis Dashboard")
        
        # TOP SUMMARY METRIC CARDS
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            score_color = "#10B981" if match_res["match_score"] >= 75 else ("#F59E0B" if match_res["match_score"] >= 50 else "#F43F5E")
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Match Score</div>
                <div class="metric-value" style="color: {score_color};">{match_res['match_score']}%</div>
                <div style="font-size:0.8rem; color:#94A3B8;">Target: {match_res['target_role']}</div>
            </div>
            """, unsafe_allow_html=True)
            
        with m2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Skills Found</div>
                <div class="metric-value" style="color: #3B82F6;">{len(match_res['found_skills'])}</div>
                <div style="font-size:0.8rem; color:#94A3B8;">In Candidate Profile</div>
            </div>
            """, unsafe_allow_html=True)
            
        with m3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Missing Skills</div>
                <div class="metric-value" style="color: #F43F5E;">{len(match_res['missing_skills'])}</div>
                <div style="font-size:0.8rem; color:#94A3B8;">For Target Role</div>
            </div>
            """, unsafe_allow_html=True)

        with m4:
            top_role_name = top_recs[0]["target_role"] if top_recs else "N/A"
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Top Recommended Role</div>
                <div class="metric-value" style="color: #8B5CF6; font-size:1.4rem; padding-top:0.4rem;">{top_role_name}</div>
                <div style="font-size:0.8rem; color:#94A3B8;">Best Matching Profile</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br/>", unsafe_allow_html=True)
        
        # TOP 3 RECOMMENDED JOB ROLES
        st.markdown("### 🏆 Top 3 Recommended Job Roles")
        rec_cols = st.columns(3)
        for idx, rec in enumerate(top_recs):
            with rec_cols[idx]:
                st.markdown(f"""
                <div class="job-card">
                    <div style="font-weight:700; font-size:1.1rem; color:#F8FAFC;">#{idx+1} {rec['target_role']}</div>
                    <div style="color:#94A3B8; font-size:0.85rem;">Category: {rec['category']}</div>
                    <div style="font-size:1.6rem; font-weight:800; color:#3B82F6; margin:0.4rem 0;">{rec['match_score']}% Match</div>
                    <div style="font-size:0.8rem; color:#CBD5E1;">Skill Overlap: {rec['skill_overlap_score']}% | TF-IDF: {rec['tfidf_score']}%</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("<br/>", unsafe_allow_html=True)
        
        # CHARTS & ANALYTICS SECTION
        c_left, c_right = st.columns(2)
        
        with c_left:
            st.markdown("#### 🍩 Skill Category Distribution")
            skills_extracted = extract_skills(parsed["raw_text"])
            by_cat = skills_extracted["by_category"]
            
            if by_cat:
                cat_counts = {cat: len(skills) for cat, skills in by_cat.items()}
                fig_donut = px.pie(
                    names=list(cat_counts.keys()),
                    values=list(cat_counts.values()),
                    hole=0.5,
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
                fig_donut.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#F8FAFC'),
                    margin=dict(t=10, b=10, l=10, r=10)
                )
                st.plotly_chart(fig_donut, use_container_width=True)
            else:
                st.info("No categorical skill distribution available.")

        with c_right:
            st.markdown("#### 📊 Match Comparison Across Predefined Roles")
            all_role_matches = recommend_top_job_roles(parsed["raw_text"], top_n=10, use_semantic=st.session_state.use_semantic)
            df_comp = pd.DataFrame(all_role_matches)
            
            fig_bar = px.bar(
                df_comp,
                x='match_score',
                y='target_role',
                orientation='h',
                color='match_score',
                color_continuous_scale='Viridis',
                text='match_score'
            )
            fig_bar.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#F8FAFC'),
                yaxis=dict(autorange="reversed"),
                margin=dict(t=10, b=10, l=10, r=10)
            )
            st.plotly_chart(fig_bar, use_container_width=True)

        st.markdown("<br/>", unsafe_allow_html=True)

        # SKILL BREAKDOWN & GAP ANALYSIS
        st.markdown("### 🧩 Skill Gap Analysis")
        sk_col1, sk_col2 = st.columns(2)
        
        with sk_col1:
            st.markdown("#### ✅ Skills Found in Resume")
            if match_res["found_skills"]:
                found_badges = "".join([f'<span class="skill-badge-found">{s}</span>' for s in match_res["found_skills"]])
                st.markdown(found_badges, unsafe_allow_html=True)
            else:
                st.warning("No technical skills matching our database were detected.")

        with sk_col2:
            st.markdown(f"#### ⚠️ Missing Skills for {match_res['target_role']}")
            if match_res["missing_skills"]:
                missing_badges = "".join([f'<span class="skill-badge-missing">{s}</span>' for s in match_res["missing_skills"]])
                st.markdown(missing_badges, unsafe_allow_html=True)
            else:
                st.success("🎉 Outstanding! You possess all required technical skills for this role.")

        st.markdown("<br/>", unsafe_allow_html=True)

        # RESUME STRENGTH ANALYSIS & AI SUGGESTIONS
        st.markdown("### ⚡ Resume Strength & AI Feedback")
        st1, st2 = st.columns([1, 1])
        
        with st1:
            st.markdown("#### Resume Quality Breakdown")
            strength_data = pd.DataFrame({
                'Metric': ['Readability', 'Sections', 'Impact Verbs', 'Quantifiable Metrics', 'Skill Depth'],
                'Score': [
                    strength['readability_score'], strength['section_score'], 
                    strength['impact_score'], strength['quantifiable_score'], 
                    strength['skill_depth_score']
                ],
                'Max': [20, 20, 20, 20, 20]
            })
            
            fig_strength = px.bar(
                strength_data,
                x='Score',
                y='Metric',
                orientation='h',
                text='Score',
                range_x=[0, 20],
                color='Score',
                color_continuous_scale='Tealgrn'
            )
            fig_strength.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#F8FAFC'),
                margin=dict(t=10, b=10, l=10, r=10)
            )
            st.plotly_chart(fig_strength, use_container_width=True)

        with st2:
            st.markdown("#### 💡 AI Resume Improvement Suggestions")
            for sug in an["ai_suggs"]:
                st.info(f"💡 {sug}")

        st.markdown("<br/>", unsafe_allow_html=True)

        # PERSONALIZED 4-WEEK LEARNING ROADMAP
        st.markdown(f"### 🗓️ Personalized 4-Week Learning Roadmap ({match_res['target_role']})")
        for week_item in an["roadmap"]:
            st.markdown(f"""
            <div class="roadmap-week">
                <div style="font-size:1.1rem; font-weight:700; color:#38BDF8;">{week_item['week']}: {week_item['title']}</div>
                <div style="color:#CBD5E1; font-size:0.9rem; margin-top:0.2rem; margin-bottom:0.6rem;">{week_item['focus']}</div>
            </div>
            """, unsafe_allow_html=True)
            
            w_c1, w_c2 = st.columns([2, 1])
            with w_c1:
                st.markdown("**Action Items:**")
                for item in week_item["action_items"]:
                    st.checkbox(item, key=f"{week_item['week']}_{item[:15]}")
            with w_c2:
                st.markdown("**Recommended Resources:**")
                for res in week_item["recommended_resources"]:
                    st.markdown(f"- 📚 {res}")

        st.markdown("<br/>", unsafe_allow_html=True)

        # RESUME SECTIONS DETECTED
        with st.expander("🔍 View Detected Resume Text & Sections"):
            st.write(f"**Extracted Candidate Name:** {parsed['candidate_name']}")
            st.write(f"**Contact Info:** Email: `{parsed['email']}` | Phone: `{parsed['phone']}` | LinkedIn: `{parsed['linkedin']}` | GitHub: `{parsed['github']}`")
            st.markdown("---")
            for sec_name, sec_text in parsed["sections"].items():
                if sec_text.strip():
                    st.markdown(f"#### {sec_name}")
                    st.text_area(f"{sec_name} content", value=sec_text, height=100, disabled=True, label_visibility="collapsed")

        st.markdown("<br/>", unsafe_allow_html=True)

        # DOWNLOAD REPORT BUTTON
        st.markdown("### 📥 Download Analysis Report")
        if os.path.exists(an["pdf_path"]):
            with open(an["pdf_path"], "rb") as pdf_file:
                st.download_button(
                    label="📄 Download PDF Analysis Report",
                    data=pdf_file,
                    file_name=os.path.basename(an["pdf_path"]),
                    mime="application/pdf",
                    type="primary",
                    use_container_width=True
                )

# TAB 2: ANALYSIS HISTORY
elif menu == "Analysis History":
    st.markdown("### 📜 Past Resume Analysis Reports")
    user_id = st.session_state.user["id"] if st.session_state.user else None
    reports = get_user_reports(user_id=user_id)
    
    if reports:
        df_rep = pd.DataFrame(reports)
        st.dataframe(
            df_rep[["id", "candidate_name", "target_role", "match_score", "strength_score", "created_at"]],
            use_container_width=True
        )
        
        st.markdown("---")
        st.markdown("#### Re-Generate / Download Report")
        selected_rep_id = st.selectbox("Select Report ID", [r["id"] for r in reports])
        if st.button("View Report Details"):
            rep_details = get_report_by_id(selected_rep_id)
            if rep_details:
                st.json(rep_details)
    else:
        st.info("No saved analysis reports found in SQLite database.")

# TAB 3: JOB CATALOG
elif menu == "Job Catalog":
    st.markdown("### 💼 Predefined Job Roles Catalog")
    df_roles = get_all_job_roles()
    if not df_roles.empty:
        for _, row in df_roles.iterrows():
            with st.expander(f"📌 {row['role_name']} ({row['category']})"):
                st.write(f"**Description:** {row['description']}")
                st.write(f"**Required Skills:** {row['required_skills']}")
                st.write(f"**Experience Level:** {row['experience_level']} (Min {row['min_experience_years']} years)")
    else:
        st.warning("No job roles found in database.")

# TAB 4: SKILL MATRIX
elif menu == "Skill Matrix":
    st.markdown("### 🛠️ Technical Skills Database Taxonomy")
    df_skills = get_all_skills()
    if not df_skills.empty:
        search_skill = st.text_input("Filter skills by name or category:", "")
        if search_skill:
            df_filtered = df_skills[
                df_skills["skill_name"].str.contains(search_skill, case=False) | 
                df_skills["category"].str.contains(search_skill, case=False)
            ]
        else:
            df_filtered = df_skills
            
        st.dataframe(df_filtered, use_container_width=True)
    else:
        st.warning("No skills dataset available.")

# TAB 5: ACCOUNT & SETTINGS
elif menu == "Account & Settings":
    st.markdown("### 👤 User Authentication & Preferences")
    
    if st.session_state.user:
        st.success(f"You are logged in as: **{st.session_state.user['username']}** ({st.session_state.user['email']})")
    else:
        auth_tab1, auth_tab2 = st.tabs(["Login", "Register"])
        
        with auth_tab1:
            st.markdown("#### Login to Save History")
            login_user = st.text_input("Username or Email", key="login_u")
            login_pass = st.text_input("Password", type="password", key="login_p")
            if st.button("Login"):
                success, user_or_err = authenticate_user(login_user, login_pass)
                if success:
                    st.session_state.user = user_or_err
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error(user_or_err)
                    
        with auth_tab2:
            st.markdown("#### Create New Account")
            reg_user = st.text_input("Username", key="reg_u")
            reg_email = st.text_input("Email", key="reg_e")
            reg_pass = st.text_input("Password", type="password", key="reg_p")
            if st.button("Register Account"):
                success, user_or_err = register_user(reg_user, reg_email, reg_pass)
                if success:
                    st.success("Registration successful! You can now log in.")
                else:
                    st.error(user_or_err)
