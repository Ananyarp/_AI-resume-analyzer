# AI Resume Analyzer and Job Recommendation System ⚡

An NLP-powered web application built with Python and Streamlit that analyzes uploaded resumes (PDF, DOCX, TXT), extracts technical skills and document sections, calculates candidate-job match scores using **TF-IDF + Cosine Similarity** (and optional Sentence Transformer semantic embeddings), identifies missing skill gaps, recommends top matching job roles, generates a personalized 4-week learning roadmap, and exports downloadable PDF reports.

---

## 🌟 Key Features

1. **Multi-Format Resume Parser**: Supports PDF, DOCX, and TXT resume uploads with automatic contact detail & section extraction (Education, Experience, Projects, Certifications, Skills).
2. **NLP Skill Extraction Engine**: Identifies technical skills, tools, and frameworks from a canonical taxonomy of 70+ technical skills.
3. **TF-IDF + Cosine Similarity Matcher**: Computes precise vector similarity scores between candidate resumes and 10 predefined tech job roles.
4. **Optional Semantic Matching**: Integrates `SentenceTransformers` (`all-MiniLM-L6-v2`) for deep contextual semantic matching.
5. **Top 3 Job Role Recommendation**: Automatically ranks all job roles and suggests the best-fit roles for the candidate.
6. **Skill Gap Analysis**: Identifies exact missing technical skills required for target roles.
7. **Personalized 4-Week Learning Roadmap**: Generates week-by-week action plans, study topics, and curated learning resources to bridge identified skill gaps.
8. **AI Resume Improvement Suggestions**: Provides feedback on resume length, impact verb density, quantifiable metrics, and formatting.
9. **Interactive Plotly Visualizations**:
   - Skill Category Donut Chart
   - Match Score Comparison Bar Chart across all 10 roles
   - Resume Quality & Strength Radar/Bar Breakdown
10. **Downloadable PDF Reports**: Generates professional PDF analysis reports using ReportLab.
11. **SQLite Database Persistence**: Stores user accounts, uploaded resume metadata, analysis metrics, and historical reports.
12. **User Authentication**: Simple SHA-256 hashed login/registration with guest mode option.

---

## 🛠️ Tech Stack

- **Language**: Python 3.11
- **Web Framework**: Streamlit
- **Data & Analytics**: Pandas, NumPy
- **Machine Learning & NLP**: Scikit-learn, spaCy, Sentence-Transformers
- **Document Extractors**: pypdf, PyPDF2, python-docx
- **Visualizations**: Plotly
- **PDF Generation**: ReportLab
- **Database**: SQLite3
- **Configuration**: python-dotenv

---

## 📁 Project Architecture

```
ai_resume_analyzer/
│
├── app.py                  # Main Streamlit Dashboard & Navigation UI
├── resume_parser.py        # PDF, DOCX, TXT parser & section extractor
├── text_cleaner.py         # Text preprocessing, normalization & lemmatization
├── skill_extractor.py      # Technical skill extraction & categorization engine
├── job_matcher.py          # TF-IDF Cosine Similarity & top roles recommender
├── roadmap_generator.py    # Personalized 4-week learning roadmap generator
├── report_generator.py     # ReportLab PDF report generation engine
├── database.py             # SQLite database helper & CSV data seeder
├── auth.py                 # User authentication & password hashing
├── requirements.txt        # Python package dependencies
├── README.md               # Complete setup documentation
├── .env                    # Environment configuration settings
├── .gitignore              # Git ignore rules
│
├── data/                   # Predefined datasets
│   ├── job_roles.csv       # Job roles descriptions & required skills dataset
│   └── skills.csv          # Canonical skills taxonomy dataset
│
├── uploads/                # Directory for uploaded user resumes
├── reports/                # Directory for generated PDF reports
├── assets/                 # Custom styling & assets
├── models/                 # Cached models directory
└── tests/                  # Automated unit test suite
    └── test_analyzer.py
```

---

## 🎯 Supported Job Roles

1. **Data Analyst**
2. **Machine Learning Engineer**
3. **AI Engineer**
4. **NLP Engineer**
5. **Computer Vision Engineer**
6. **Python Developer**
7. **Full Stack Developer**
8. **Java Developer**
9. **Data Scientist**
10. **Cloud Engineer**

---

## 🚀 Quick Start Guide

### 1. Prerequisites
Ensure Python 3.11 is installed on your system.

### 2. Clone / Set Directory
Navigate to the project folder:
```bash
cd ai_resume_analyzer
```

### 3. Install Dependencies
Install all required Python packages:
```bash
python -m venv venv

# Windows
venv\Scripts\activate

pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 4. Initialize the SQLite Database
Create the database and seed the sample job-role and skill datasets:
```bash
python create_database.py
```

### 5. Run the Streamlit Web Application
Execute the following command to launch the web application:
```bash
streamlit run app.py
```

The application will open automatically in your browser at `http://localhost:8501`.

---

## 🧪 Running Unit Tests

Run the automated unit test suite to verify resume parsing, text cleaning, skill extraction, matching algorithms, database functions, and PDF generation:

```bash
python -m unittest discover -s tests
```

---

## 📄 License & Credits

Built as an end-to-end production-quality AI application with Python and Streamlit.
