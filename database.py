import os
import sqlite3
import pandas as pd
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

DB_FILE = os.getenv("DB_PATH", "ai_resume_analyzer.db")
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

def get_connection():
    """Create and return a database connection."""
    db_dir = os.path.dirname(DB_FILE)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize SQLite database tables and seed sample datasets if missing."""
    conn = get_connection()
    cursor = conn.cursor()

    # Create Users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Create Job Roles table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS job_roles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        role_name TEXT UNIQUE NOT NULL,
        category TEXT NOT NULL,
        required_skills TEXT NOT NULL,
        description TEXT,
        experience_level TEXT,
        min_experience_years INTEGER
    )
    """)

    # Create Skills table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS skills (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        skill_name TEXT UNIQUE NOT NULL,
        category TEXT NOT NULL,
        importance TEXT
    )
    """)

    # Create Resumes table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS resumes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        filename TEXT NOT NULL,
        file_type TEXT NOT NULL,
        raw_text TEXT NOT NULL,
        uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    """)

    # Create Analysis Reports table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS analysis_reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        resume_id INTEGER NOT NULL,
        user_id INTEGER,
        candidate_name TEXT,
        target_role TEXT NOT NULL,
        match_score REAL NOT NULL,
        recommended_roles TEXT NOT NULL,
        found_skills TEXT NOT NULL,
        missing_skills TEXT NOT NULL,
        strength_score REAL NOT NULL,
        sections_detected TEXT,
        roadmap_json TEXT,
        ai_suggestions TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (resume_id) REFERENCES resumes (id),
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    """)

    conn.commit()

    # Seed data if tables are empty
    seed_default_data(conn)
    conn.close()

def seed_default_data(conn):
    """Seed sample job roles and skills from CSV files into SQLite database if empty."""
    cursor = conn.cursor()

    # Check job_roles count
    cursor.execute("SELECT COUNT(*) FROM job_roles")
    if cursor.fetchone()[0] == 0:
        roles_csv = os.path.join(DATA_DIR, "job_roles.csv")
        if os.path.exists(roles_csv):
            df_roles = pd.read_csv(roles_csv)
            for _, row in df_roles.iterrows():
                cursor.execute("""
                INSERT OR IGNORE INTO job_roles (role_name, category, required_skills, description, experience_level, min_experience_years)
                VALUES (?, ?, ?, ?, ?, ?)
                """, (row['role_name'], row['category'], row['required_skills'], row['description'], row['experience_level'], int(row['min_experience_years'])))

    # Check skills count
    cursor.execute("SELECT COUNT(*) FROM skills")
    if cursor.fetchone()[0] == 0:
        skills_csv = os.path.join(DATA_DIR, "skills.csv")
        if os.path.exists(skills_csv):
            df_skills = pd.read_csv(skills_csv)
            for _, row in df_skills.iterrows():
                cursor.execute("""
                INSERT OR IGNORE INTO skills (skill_name, category, importance)
                VALUES (?, ?, ?)
                """, (row['skill_name'], row['category'], row['importance']))

    conn.commit()

def save_resume(filename, file_type, raw_text, user_id=None):
    """Save an uploaded resume record."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO resumes (user_id, filename, file_type, raw_text)
    VALUES (?, ?, ?, ?)
    """, (user_id, filename, file_type, raw_text))
    conn.commit()
    resume_id = cursor.lastrowid
    conn.close()
    return resume_id

def save_report(resume_id, candidate_name, target_role, match_score, recommended_roles, 
                found_skills, missing_skills, strength_score, sections_detected, 
                roadmap_json, ai_suggestions, user_id=None):
    """Save analysis report results to SQLite."""
    conn = get_connection()
    cursor = conn.cursor()
    
    rec_str = json.dumps(recommended_roles) if isinstance(recommended_roles, (list, dict)) else recommended_roles
    found_str = json.dumps(found_skills) if isinstance(found_skills, (list, set, dict)) else found_skills
    missing_str = json.dumps(missing_skills) if isinstance(missing_skills, (list, set, dict)) else missing_skills
    sec_str = json.dumps(sections_detected) if isinstance(sections_detected, (list, dict)) else sections_detected
    road_str = json.dumps(roadmap_json) if isinstance(roadmap_json, (list, dict)) else roadmap_json
    sug_str = json.dumps(ai_suggestions) if isinstance(ai_suggestions, (list, dict)) else ai_suggestions

    cursor.execute("""
    INSERT INTO analysis_reports 
    (resume_id, user_id, candidate_name, target_role, match_score, recommended_roles, 
     found_skills, missing_skills, strength_score, sections_detected, roadmap_json, ai_suggestions)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (resume_id, user_id, candidate_name, target_role, float(match_score), rec_str,
          found_str, missing_str, float(strength_score), sec_str, road_str, sug_str))
    
    conn.commit()
    report_id = cursor.lastrowid
    conn.close()
    return report_id

def get_user_reports(user_id=None):
    """Fetch history of analysis reports."""
    conn = get_connection()
    cursor = conn.cursor()
    if user_id:
        cursor.execute("SELECT * FROM analysis_reports WHERE user_id = ? ORDER BY created_at DESC", (user_id,))
    else:
        cursor.execute("SELECT * FROM analysis_reports ORDER BY created_at DESC LIMIT 50")
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows

def get_report_by_id(report_id):
    """Fetch specific report details."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM analysis_reports WHERE id = ?", (report_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def get_all_job_roles():
    """Fetch all predefined job roles."""
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM job_roles ORDER BY role_name", conn)
    conn.close()
    return df

def get_all_skills():
    """Fetch all skills from DB."""
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM skills ORDER BY category, skill_name", conn)
    conn.close()
    return df

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")
