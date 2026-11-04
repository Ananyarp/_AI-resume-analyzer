import os
import re
import pandas as pd
from typing import List, Dict, Set, Any

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

def load_skills_db() -> Dict[str, Dict[str, str]]:
    """Load canonical skills dataset mapping normalized skill names to category & importance."""
    skills_csv = os.path.join(DATA_DIR, "skills.csv")
    skills_map = {}
    if os.path.exists(skills_csv):
        df = pd.read_csv(skills_csv)
        for _, row in df.iterrows():
            name = str(row['skill_name']).strip()
            skills_map[name.lower()] = {
                "name": name,
                "category": str(row['category']).strip(),
                "importance": str(row['importance']).strip()
            }
    return skills_map

def extract_skills(raw_text: str) -> Dict[str, Any]:
    """
    Extract skills from resume text using regex word-boundary and pattern matching against skills taxonomy.
    """
    if not raw_text:
        return {"found_skills": [], "by_category": {}, "count": 0}

    skills_map = load_skills_db()
    text_lower = raw_text.lower()

    found_skills_set: Set[str] = set()
    category_map: Dict[str, List[str]] = {}

    for norm_skill, info in skills_map.items():
        skill_display = info["name"]
        cat = info["category"]

        # Escaped regex pattern for technical names
        if norm_skill in ["c++", "c#", ".net", "r"]:
            if norm_skill == "c++":
                pattern = r'\bc\+\+\b'
            elif norm_skill == "c#":
                pattern = r'\bc\#\b'
            elif norm_skill == ".net":
                pattern = r'(\.net|\bdotnet\b)'
            elif norm_skill == "r":
                pattern = r'\b(r|r-lang|r language)\b'
        else:
            # Word boundary regex
            escaped = re.escape(norm_skill)
            pattern = r'\b' + escaped + r'\b'

        if re.search(pattern, text_lower, re.IGNORECASE):
            found_skills_set.add(skill_display)
            if cat not in category_map:
                category_map[cat] = []
            category_map[cat].append(skill_display)

    found_list = sorted(list(found_skills_set))
    return {
        "found_skills": found_list,
        "by_category": category_map,
        "count": len(found_list)
    }

if __name__ == "__main__":
    sample = "Proficient in Python, C++, PyTorch, Docker, PostgreSQL, AWS, and Git."
    res = extract_skills(sample)
    print("Found skills:", res["found_skills"])
    print("Categories:", res["by_category"])
