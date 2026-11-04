from typing import List, Dict, Any

def generate_learning_roadmap(target_role: str, missing_skills: List[str], found_skills: List[str]) -> List[Dict[str, Any]]:
    """
    Generate a personalized 4-week learning roadmap customized to candidate missing skills and target job role.
    """
    primary_gaps = missing_skills[:4] if missing_skills else ["Advanced System Architecture", "Production Deployment"]
    secondary_gaps = missing_skills[4:8] if len(missing_skills) > 4 else ["Performance Optimization", "Testing & CI/CD"]

    gaps_str_1 = ", ".join(primary_gaps[:2]) if primary_gaps else "Domain Fundamentals"
    gaps_str_2 = ", ".join(primary_gaps[2:4]) if len(primary_gaps) >= 4 else (primary_gaps[0] if primary_gaps else "Advanced Tooling")
    gaps_str_3 = ", ".join(secondary_gaps[:2]) if secondary_gaps else "Best Practices"

    roadmap = [
        {
            "week": "Week 1",
            "title": f"Core Technical Foundations & Prerequisite Gap Closure ({target_role})",
            "focus": f"Master fundamental concepts and bridge critical missing skills: {gaps_str_1}.",
            "action_items": [
                f"Study core documentation and fundamentals of {gaps_str_1}.",
                f"Complete hands-on tutorials and code exercises targeting {primary_gaps[0] if primary_gaps else 'Core Skills'}.",
                "Build small, isolated scripts to verify syntax and conceptual understanding.",
                "Review industry standard design patterns and best practices."
            ],
            "recommended_resources": [
                f"Official {primary_gaps[0] if primary_gaps else target_role} Documentation",
                "freeCodeCamp / Coursera Specialist Track",
                "GitHub Awesome-List Tutorials"
            ]
        },
        {
            "week": "Week 2",
            "title": "Framework & Applied Tooling Mastery",
            "focus": f"Gain practical experience with target frameworks and database tools: {gaps_str_2}.",
            "action_items": [
                f"Integrate {gaps_str_2} into functional sample applications.",
                "Implement end-to-end data processing pipelines or API endpoints.",
                "Write unit tests and setup proper environment configuration (.env, virtualenv).",
                "Study performance benchmarks and error handling techniques."
            ],
            "recommended_resources": [
                "Real Python / Medium Deep Dives",
                "Interactive Coding Katas / LeetCode",
                "Stack Overflow & Developer Forum Case Studies"
            ]
        },
        {
            "week": "Week 3",
            "title": "Real-World Portfolio Project Development",
            "focus": f"Build and showcase a production-grade project highlighting {target_role} competencies.",
            "action_items": [
                f"Develop a complete showcase project integrating {', '.join(primary_gaps[:3]) if primary_gaps else target_role}.",
                "Implement containerization (Docker) and publish code to GitHub with a detailed README.",
                "Set up continuous integration (CI/CD workflows) and live demo hosting.",
                "Document clean architecture, database schemas, and API specs."
            ],
            "recommended_resources": [
                "GitHub Project Boilerplates",
                "Docker / Cloud Deployment Guides",
                "System Design Primer Repository"
            ]
        },
        {
            "week": "Week 4",
            "title": "Interview Preparation, System Design & Resume Polish",
            "focus": "Refine resume bullet points, conduct mock interviews, and solidify technical explanations.",
            "action_items": [
                f"Update resume with newly acquired skills ({', '.join(primary_gaps[:3]) if primary_gaps else 'New Technologies'}).",
                "Quantify achievements in your new portfolio project (e.g., latency, accuracy, throughput).",
                f"Practice behavioral and technical interview questions tailored to {target_role}.",
                "Participate in mock interviews and optimize LinkedIn profile keywords."
            ],
            "recommended_resources": [
                "Cracking the Coding / ML Interview",
                "System Design Interview Guide",
                "AI Resume Analyzer Feedback & Metrics"
            ]
        }
    ]

    return roadmap
