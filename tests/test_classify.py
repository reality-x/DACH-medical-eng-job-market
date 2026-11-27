import sys
import pathlib

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "src"))

import classify as C

# Same cases as the in-notebook check in notebooks/03_silver_clean.py.
CASES = [
    ("Machine Learning Engineer (m/w/d)",    "ml engineer"),
    ("Senior ML Engineer - Computer Vision", "ml engineer"),
    ("Deep Learning Engineer",               "ml engineer"),
    ("NLP Engineer",                         "ml engineer"),
    ("MLOps Engineer",                       "mlops"),
    ("ML Platform Engineer (f/m/x)",         "mlops"),
    ("Model Deployment Engineer",            "mlops"),
    ("GenAI Engineer",                       "genai / llm"),
    ("LLM Engineer / RAG Specialist",        "genai / llm"),
    ("Prompt Engineer (Remote)",             "genai / llm"),
    ("Agentic AI Developer",                 "genai / llm"),
    ("Generative KI Spezialist",             "genai / llm"),
    ("Applied Scientist, Machine Learning",  "ai research"),
    ("AI Research Engineer",                 "ai research"),
    ("Research Scientist Deep Learning",     "ai research"),
    ("AI Consultant (m/w/d)",                "ai consultant"),
    ("KI-Berater Digitalisierung",           "ai consultant"),
    ("AI Solution Architect",                "ai consultant"),
    ("AI Product Manager",                   "ai consultant"),
    ("AI Engineer",                          "ai engineer"),
    ("KI-Entwickler (m/w/d)",                "ai engineer"),
    ("Artificial Intelligence Engineer",     "ai engineer"),
    ("AI Specialist",                        "ai engineer"),
    # the vague bucket: these are the ones that used to inflate ai / ml
    ("Projektmanager KI",                    "ai (other)"),
    # software roles that mention AI count as the role they name
    ("Software Engineer with AI focus",      "software engineer"),
    ("Fullstack Developer (AI Startup)",     "fullstack engineer"),
    # software engineering
    ("Senior Software Engineer (m/w/d)",     "software engineer"),
    ("Softwareentwickler C++ (m/w/d)",       "software engineer"),
    ("Anwendungsentwickler Java",            "backend engineer"),
    ("Java Developer",                       "backend engineer"),
    ("Backend Engineer Go",                  "backend engineer"),
    ("Python Entwickler (m/w/d)",            "backend engineer"),
    (".NET Developer",                       "backend engineer"),
    ("Frontend Developer React",             "frontend engineer"),
    ("Angular Entwickler",                   "frontend engineer"),
    ("Webentwickler (m/w/d)",                "frontend engineer"),
    ("JavaScript Developer",                 "frontend engineer"),
    ("Full-Stack Engineer TypeScript",       "fullstack engineer"),
    ("iOS Developer",                        "mobile engineer"),
    ("Android Software Engineer",            "mobile engineer"),
    ("App-Entwickler Flutter",               "mobile engineer"),
    ("DevOps Engineer",                      "devops / cloud"),
    ("Site Reliability Engineer",            "devops / cloud"),
    ("Cloud Engineer AWS",                   "devops / cloud"),
    ("Platform Engineer Kubernetes",         "devops / cloud"),
    ("Cloud Architekt Azure",                "devops / cloud"),
    # out of scope software
    ("Embedded Software Engineer",           "embedded / qa"),
    ("Firmware Entwickler",                  "embedded / qa"),
    ("QA Engineer",                          "embedded / qa"),
    ("Software Tester",                      "embedded / qa"),
    # data and AI still beat software
    ("Data Platform Engineer",               "data engineer"),
    ("AI Software Engineer",                 "ai engineer"),
    ("ML Platform Engineer",                 "mlops"),
    ("Werkstudent Softwareentwicklung",      "entry programme"),
    # data still beats AI
    ("Data & AI Consultant",                 "data consultant"),
    ("Data Engineer AI Platform",            "data engineer"),
    ("Data Scientist NLP",                   "data scientist"),
    ("Senior Data Analyst",                  "data analyst"),
    ("Business Intelligence Developer",      "bi developer"),
    ("Analytics Engineer",                   "analytics engineer"),
    # excludes still beat everything
    ("Werkstudent AI Engineering",           "entry programme"),
    ("Controlling Specialist AI",            "finance"),
    ("Rechenzentrum Techniker",              "data centre"),
    ("Versicherungsagent",                   "other"),
]


@pytest.mark.parametrize("title,expected", CASES)
def test_classify(title, expected):
    assert C.classify(title) == expected


def test_role_groups():
    assert C.role_group("backend engineer") == "software"
    assert C.role_group("mlops") == "ai"
    assert C.role_group("data analyst") == "data"
    assert C.role_group("embedded / qa") == "excluded"


def test_seniority():
    assert C.seniority("Senior Backend Engineer") == "senior"
    assert C.seniority("Junior Data Analyst") == "junior"
    assert C.seniority("Data Analyst") == "mid"


def test_city_normalisation():
    assert C.city(["Deutschland", "Bayern", "München (Kreis)"]) == "muenchen"
    assert C.city(["Deutschland", "Berlin", "Mitte"]) == "berlin"
    assert C.city(["Deutschland", "Hessen", "Frankfurt am Main"]) == "frankfurt"
    assert C.city(["Deutschland"]) == "unknown"
