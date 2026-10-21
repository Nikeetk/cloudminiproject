"""
Career Recommendation System - Web API & Server
FastAPI application serving the Machine Learning recommendation engine,
interactive EDA analytics, and static web frontend.
"""

import os
import sys
import webbrowser
import threading
import time
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import List, Optional

from recommendation_engine import CareerRecommender, CAREER_METADATA

app = FastAPI(
    title="AI-Based Career Recommendation System",
    description="Intelligent career path prediction, skill gap analysis, and EDA dashboard",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize engine
engine = CareerRecommender()

# Request schemas
class CandidateRequest(BaseModel):
    name: Optional[str] = "Candidate"
    age: int = Field(default=26, ge=18, le=70)
    education: str = Field(default="Bachelor's")
    skills: List[str] = Field(default_factory=list)
    interests: List[str] = Field(default_factory=list)

class TextExtractRequest(BaseModel):
    text: str

# Sample candidate profiles for quick testing
SAMPLE_PROFILES = [
    {
        "id": "ds_profile",
        "title": "Data Scientist",
        "name": "Alex Chen",
        "age": 28,
        "education": "Master's",
        "skills": ["Python", "Machine Learning", "Data Analysis", "Statistics", "SQL"],
        "interests": ["Data Science", "AI", "Technology"],
        "badge": "AI & Analytics"
    },
    {
        "id": "ux_profile",
        "title": "UX / Product Designer",
        "name": "Maya Patel",
        "age": 25,
        "education": "Bachelor's",
        "skills": ["UI/UX", "Graphic Design", "Prototyping", "User Research", "Adobe Creative Suite"],
        "interests": ["Design", "Digital Media", "Arts"],
        "badge": "Design & Product"
    },
    {
        "id": "fullstack_profile",
        "title": "Full Stack Developer",
        "name": "Jordan Lee",
        "age": 26,
        "education": "Bachelor's",
        "skills": ["JavaScript", "React", "Node.js", "HTML", "CSS", "SQL"],
        "interests": ["Web Development", "Technology", "Coding"],
        "badge": "Engineering"
    },
    {
        "id": "cyber_profile",
        "title": "Cybersecurity Specialist",
        "name": "Marcus Vance",
        "age": 31,
        "education": "Bachelor's",
        "skills": ["Network Security", "Linux", "Python", "Cybersecurity"],
        "interests": ["Cybersecurity", "Technology", "Security"],
        "badge": "Security & Defense"
    },
    {
        "id": "pm_profile",
        "title": "Technical Project Manager",
        "name": "Elena Rostova",
        "age": 32,
        "education": "Master's",
        "skills": ["Project Management", "Agile", "Communication", "Risk Analysis", "Negotiation"],
        "interests": ["Business", "Management", "Technology"],
        "badge": "Management & Leadership"
    },
    {
        "id": "fin_profile",
        "title": "Financial Analyst",
        "name": "David Kim",
        "age": 29,
        "education": "Master's",
        "skills": ["Financial Analysis", "Excel", "Econometrics", "SQL", "Data Analysis"],
        "interests": ["Finance", "Data Analysis", "Business"],
        "badge": "Finance & Analytics"
    }
]

# Categorized skills for intuitive UI selection
SKILLS_CATEGORIZED = {
    "AI, ML & Data": [
        "Python", "R", "Machine Learning", "Deep Learning", "Data Analysis",
        "Data Science", "Statistics", "Statistical Analysis", "Data Mining",
        "Big Data", "Data Visualization", "Data Warehousing", "ETL", "SQL",
        "Natural Language Processing", "NLP", "TensorFlow", "AI"
    ],
    "Software Engineering": [
        "Java", "JavaScript", "C#", "C++", ".NET", "React", "Node.js",
        "HTML", "CSS", "Algorithms", "Data Structures", "Software Design",
        "System Design", "Spring", "Microservices", "Android"
    ],
    "Cloud & Infrastructure": [
        "Cloud Computing", "DevOps", "Linux", "Network Security",
        "Cybersecurity", "Embedded Systems", "IoT", "Automation"
    ],
    "Design & Creative": [
        "UI/UX", "UI Design", "UX Design", "UX Research", "UX", "UX/UI",
        "User Research", "Prototyping", "Interaction Design",
        "Graphic Design", "Illustration", "Digital Illustration",
        "Adobe Creative Suite", "Adobe Photoshop", "Adobe Illustrator", "Adobe XD", "Creativity"
    ],
    "Marketing & Content": [
        "Digital Marketing", "Marketing Strategy", "SEO", "Social Media",
        "Content Creation", "Content Strategy", "Content Writing", "Copywriting",
        "CRM", "Storytelling"
    ],
    "Business & Management": [
        "Project Management", "Business Analysis", "Agile", "Communication",
        "Negotiation", "Risk Analysis", "Excel", "Financial Analysis", "Econometrics", "Research"
    ]
}

@app.get("/api/health")
def health_check():
    return {"status": "ok", "model_loaded": True}

@app.post("/api/recommend")
def get_recommendation(payload: CandidateRequest):
    try:
        result = engine.recommend(
            age=payload.age,
            education=payload.education,
            skills=payload.skills,
            interests=payload.interests
        )
        result["candidate"]["name"] = payload.name
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/extract")
def extract_skills_endpoint(payload: TextExtractRequest):
    try:
        return engine.extract_skills_from_text(payload.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/skills")
def get_all_skills():
    return {
        "all_skills": engine.all_skills,
        "categorized": SKILLS_CATEGORIZED
    }

@app.get("/api/interests")
def get_all_interests():
    return {
        "all_interests": engine.all_interests
    }

@app.get("/api/samples")
def get_sample_profiles():
    return SAMPLE_PROFILES

@app.get("/api/catalog")
def get_catalog():
    enhanced_catalog = {}
    for career, profile in engine.career_catalog.items():
        meta = CAREER_METADATA.get(career, {})
        enhanced_catalog[career] = {
            **profile,
            "category": meta.get("category", "General"),
            "description": meta.get("description", ""),
            "salary_range": meta.get("salary_range", "$90k - $140k"),
            "demand": meta.get("demand", "High"),
            "certifications": meta.get("certifications", []),
            "portfolio_project": meta.get("portfolio_project", "")
        }
    return enhanced_catalog

@app.get("/api/stats")
def get_stats():
    try:
        return engine.get_eda_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(BASE_DIR, "AI-based Career Recommendation System.csv")
STATIC_DIR = os.path.join(BASE_DIR, "static")

@app.get("/api/dataset")
def get_dataset(limit: int = 100, search: Optional[str] = None):
    try:
        df = pd.read_csv(DATASET_PATH)
        if search:
            s = search.lower()
            mask = (
                df["Name"].astype(str).str.lower().str.contains(s) |
                df["Recommended_Career"].astype(str).str.lower().str.contains(s) |
                df["Skills"].astype(str).str.lower().str.contains(s) |
                df["Interests"].astype(str).str.lower().str.contains(s) |
                df["Education"].astype(str).str.lower().str.contains(s)
            )
            df = df[mask]
        
        records = df.head(limit).to_dict(orient="records")
        return {
            "total": len(df),
            "returned": len(records),
            "records": records
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Mount static folder
os.makedirs(STATIC_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/")
def serve_index():
    index_file = os.path.join(STATIC_DIR, "index.html")
    if not os.path.exists(index_file):
        raise HTTPException(status_code=404, detail="Frontend index.html not found.")
    return FileResponse(index_file)

def open_browser_delayed(url="http://127.0.0.1:8000"):
    time.sleep(1.2)
    try:
        webbrowser.open(url)
    except Exception:
        pass

if __name__ == "__main__":
    import uvicorn
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", 8000))

    # Open browser only in local interactive runs (not when running in cloud environments)
    is_local_interactive = "--no-browser" not in sys.argv and "PORT" not in os.environ and "DYNO" not in os.environ
    if is_local_interactive:
        threading.Thread(target=open_browser_delayed, args=(f"http://127.0.0.1:{port}",), daemon=True).start()
    
    print("\n" + "="*60)
    print("🚀 AI Career Recommendation System Web Application")
    print(f"🌐 Server running at: http://{host}:{port}")
    print("="*60 + "\n")
    uvicorn.run("app:app", host=host, port=port, reload=False)
