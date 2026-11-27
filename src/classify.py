"""Title classification and row parsing for the GitHub Actions pipeline.

The regexes are copied from notebooks/03_silver_clean.py, which remains the
Databricks version. If you change a rule, change it in both places;
tests/test_classify.py holds the shared test cases.
"""

import re as _re

AGENCY_RX = (r"(consulting|personal|recruit|staffing|hays|"
             r"randstad|michael page|robert half|experis|"
             r"gulp|solcom|amoria|darwin|huzzle|talent)")

INVALID = (r"^initiativbewerbung|initiativbewerbung|talentpool|"
           r"^deine aufgaben|^\"+title|^zum \d|^wachstum durch")

ENTRY = (r"\bausbildung\b|duales? studium|dualer bachelor|"
         r"\bwerkstudent|werkstudierend|\bpraktikum\b|\bpraktikant|"
         r"\btrainee\b|traineeprogramm|bachelor thesis|"
         r"master student|studienkolleg|bachelor of science|"
         r"\bdhbw\b|\bhwr\b|b\.\s?a\.\s+in\b|"
         r"^b\.\s?a\.|abschlussarbeit")

DATACENTRE = r"data\s*cent(er|re)|rechenzentrum|\bdceo\b"

FINANCE = (r"controlling|\bcontroller\b|finanzen|buchhalt|"
           r"\bfp&a\b|financial planning|finance transformation|"
           r"finance\s*&\s*accounting|finance business partner|"
           r"kaufmaennisch|vertriebscontrolling|"
           r"finance-consulting|finance solutions|"
           r"transaction advisory")

R_ARCHITECT = r"data\s+[\w\s\-&/]*architect|datenarchitekt"
R_ANALYTICS_ENG = r"analytics engineer"
R_ENGINEER = (r"data engineer|dateningenieur|\bbig data\b|"
              r"data platform|data scraping|data processing|"
              r"data\s*&\s*ai[\s\-]*engineer|"
              r"data\s+(migration|integration|pipeline)|"
              r"datenbankadministrator|database administrator|"
              r"\bdba\b")
R_DWH = (r"data warehouse|\bdwh\b|\betl\b|\bdbt\b|sap bw|"
         r"datasphere|data.?lake|data vault|data modeler|"
         r"data mesh|business data cloud")
R_GOVERNANCE = (r"data governance|data quality|data privacy|"
                r"master data|data steward|data management|"
                r"data strategy|data protection")
R_SCIENTIST = r"data scientist|data science"
R_ANALYST = r"data analyst|datenanalyst|\bbi analyst"
R_CONSULTANT = (r"data\s*&\s*ai|data and ai|data\s*&\s*analytics|"
                r"data analytics|data consultant|daten- und "
                r"prozessanalyse|\bdata expert\b|data insights|"
                r"\bit\s*&\s*data\b|business data")
R_BI = (r"\bbi\b|business intelligence|power ?bi|\btableau\b|"
        r"\bqlik\b|\bcelonis\b|sap analytics|process mining|"
        r"process intelligence|\bsac\b|reporting analyst|"
        r"\bjedox\b")


R_GENAI = (r"\bgenai\b|\bgen[\s\-]?ai\b|generative ai|generative ki|"
           r"\bllms?\b|\bllmops\b|large language model|"
           r"sprachmodell|foundation model|grundlagenmodell|"
           r"\brag\b|retrieval[\s\-]augmented|"
           r"prompt[\s\-]?engineer|agentic|\bai agent|\bki[\s\-]agent|"
           r"conversational ai|chatbot engineer|"
           r"\bai[\s\-]native|copilot engineer")

# Operating and serving models, not building them.
R_MLOPS = (r"\bmlops\b|\bml[\s\-]?ops\b|\bmodel ops\b|"
           r"ml[\s\-](platform|infrastructure|infra|engineer[\s\-]platform)|"
           r"machine learning (platform|infrastructure|infra|operations)|"
           r"model (serving|deployment|monitoring)|"
           r"\bai (platform|infrastructure|infra)\b|"
           r"\bki[\s\-]plattform\b|feature store")

# Classic ML including deep learning, CV and NLP.
R_ML = (r"mas?chine\s*learning|\bml[\s\-]?engineer|\bml[\s\-]?ingenieur|"
        r"maschinelles lernen|deep learning|\bdl engineer\b|"
        r"reinforcement learning|bestaerkendes lernen|"
        r"computer vision|bildverarbeitung|bilderkennung|"
        r"\bnlp\b|natural language processing|"
        r"sprachverarbeitung|speech recognition|spracherkennung|"
        r"\bai/ml\b|\bai\s*&\s*ml\b|recommender|"
        r"predictive model|forecasting engineer")

# People paid to publish or prototype, not to ship a service.
R_AI_RESEARCH = (r"applied scientist|research scientist|"
                 r"research engineer|forschungsingenieur|"
                 r"\bai research|\bki[\s\-]forsch|"
                 r"machine learning (researcher|scientist)|"
                 r"\bphd\b.*\b(ai|ml)\b")

# Advisory, architecture, strategy and product, not implementation.
R_AI_CONSULT = (r"\bai\s+(consultant|consulting|architect|advisor|"
                r"strategy|strateg|transformation|solution|"
                r"presales|sales engineer|product manager|"
                r"product owner|governance|ethics|compliance)|"
                r"\bki[\s\-]?(berater|architekt|strategie|"
                r"transformation)|"
                r"artificial intelligence (consultant|architect|"
                r"strategy|advisor)|"
                r"(consultant|architect|berater)\s+(fuer\s+)?"
                r"(ai|ki|artificial intelligence)\b")


R_AI_ENGINEER = (r"\bai\s*[\-/]?\s*(engineer|developer|entwickler|"
                 r"specialist|spezialist|expert)|"
                 r"\bki\s*[\-/]?\s*(engineer|developer|entwickler|"
                 r"spezialist|experte)|"
                 r"artificial intelligence engineer|"
                 r"\bai software engineer\b")

# --- Software engineering -----------------------------------------
# Checked after the data and named AI families, so "Data Platform
# Engineer" stays data and "AI Software Engineer" stays AI, but before
# the vague AI bucket, so "Fullstack Developer (AI Startup)" is counted
# as the fullstack role it names.

# Not in scope: embedded/firmware and QA/test. Caught here so they
# don't fall into the generic software family; they land in
# silver.excluded like every other out-of-scope row.
R_SWE_OUT = (r"\bembedded\b|firmware|\bsps\b|\bplc\b|"
             r"\b(qa|test|testing)[\s\-]?(engineer|automation)|"
             r"quality assurance|testautomat|software[\s\-]?test|"
             r"softwaretest")

R_FULLSTACK = r"full[\s\-]?stack"

R_MOBILE = (r"\b(ios|android|mobile|flutter|react native|swift|kotlin)"
            r"\b[\s\-/]*(app[\s\-]?)?(software[\s\-]?)?"
            r"(engineer|developer|entwickler|programmierer)|"
            r"\bapp[\s\-]?entwickl|\bmobile app")

R_FRONTEND = (r"front[\s\-]?end|"
              r"\b(react|angular|vue(\.?js)?|javascript|typescript|ui)"
              r"\b[\s\-/]*(engineer|developer|entwickler)|"
              r"\bweb[\s\-]?(developer|entwickler)|webentwickl")

R_BACKEND = (r"back[\s\-]?end|"
             r"(\bjava|\bgolang|\bgo(?=\s)|\bpython|\bphp|\bruby|\bscala|"
             r"\bkotlin|\brust|\bnode\.?js|\.net|\bc#)"
             r"\s*[\-/]?\s*(software[\s\-]?)?"
             r"(engineer|developer|entwickler|programmierer)|"
             # "Anwendungsentwickler Java": German puts the stack last
             r"(engineer|developer|entwickler|programmierer)\s*[\-/(]?\s*"
             r"(java|golang|python|php|ruby|scala|rust|node\.?js|"
             r"\.net|c#)(\b|$)")

R_DEVOPS = (r"devops|dev[\s\-]ops|devsecops|\bsre\b|site reliability|"
            r"\bplatt?form[\s\-]?engineer|"
            r"cloud[\s\-]?(solutions?[\s\-]?)?(engineer|architect|architekt|developer|"
            r"entwickler|administrator|ingenieur|consultant|"
            r"infrastructure)|"
            r"kubernetes|infrastructure engineer|"
            r"infrastructure as code")

R_SWE = (r"software[\s\-]?(engineer|developer|entwickler|ingenieur|"
         r"architekt|architect|craftsman)|"
         r"softwareentwickl|softwareingenieur|softwarearchitekt|"
         r"\bprogrammierer|anwendungsentwickl|applikationsentwickl|"
         r"\bsoftware dev")

# Last resort. Mentions AI, tells you nothing else. Published as its
# own family so the reader can see how large it is.
R_AI_OTHER = (r"\bai\b|\bki\b|artificial intelligence|"
              r"kuenstliche intelligenz")


_ORDER = [
    ("invalid", INVALID), ("entry programme", ENTRY),
    ("data centre", DATACENTRE), ("finance", FINANCE),
    ("data architect", R_ARCHITECT),
    ("analytics engineer", R_ANALYTICS_ENG),
    ("data engineer", R_ENGINEER), ("dwh / etl", R_DWH),
    ("data governance", R_GOVERNANCE),
    ("data scientist", R_SCIENTIST), ("data analyst", R_ANALYST),
    ("data consultant", R_CONSULTANT), ("bi developer", R_BI),
    ("ai research", R_AI_RESEARCH), ("genai / llm", R_GENAI),
    ("mlops", R_MLOPS), ("ml engineer", R_ML),
    ("ai consultant", R_AI_CONSULT), ("ai engineer", R_AI_ENGINEER),
    ("embedded / qa", R_SWE_OUT),
    ("fullstack engineer", R_FULLSTACK), ("mobile engineer", R_MOBILE),
    ("frontend engineer", R_FRONTEND), ("backend engineer", R_BACKEND),
    ("devops / cloud", R_DEVOPS), ("software engineer", R_SWE),
    ("ai (other)", R_AI_OTHER),
]


def _fold(s):
    s = s.lower().strip()
    for a, b_ in [("ä", "ae"), ("ö", "oe"), ("ü", "ue"), ("ß", "ss")]:
        s = s.replace(a, b_)
    return s


def classify(title):
    """Mirror of the F.when() chain in notebooks/03_silver_clean.py.
    If you edit one, edit both."""
    n = _fold(title)
    for fam, rx in _ORDER:
        if _re.search(rx, n):
            return fam
    return "other"


ROLE_GROUP = {}
DATA_FAMILIES = ["data engineer", "data analyst", "data scientist",
                 "data architect", "analytics engineer", "dwh / etl",
                 "data governance", "data consultant", "bi developer"]
AI_FAMILIES = ["ai engineer", "genai / llm", "ml engineer", "mlops",
               "ai consultant", "ai research"]
SWE_FAMILIES = ["software engineer", "backend engineer",
                "frontend engineer", "fullstack engineer",
                "mobile engineer", "devops / cloud"]
for _f in DATA_FAMILIES:
    ROLE_GROUP[_f] = "data"
for _f in AI_FAMILIES:
    ROLE_GROUP[_f] = "ai"
for _f in SWE_FAMILIES:
    ROLE_GROUP[_f] = "software"

# Published families. "ai (other)", "embedded / qa" and the hard
# excludes are classified but never published.
KEEP = set(DATA_FAMILIES + AI_FAMILIES + SWE_FAMILIES)


def role_group(family):
    return ROLE_GROUP.get(family, "excluded")


_SENIOR = _re.compile(r"\b(senior|sr\.?|lead|principal|head|director|"
                      r"staff|chief|\bvp\b)\b")
_JUNIOR = _re.compile(r"\b(junior|jr\.?|entry|graduate|absolvent|"
                      r"einsteiger|associate)\b")


def seniority(title):
    n = _fold(title)
    if _SENIOR.search(n):
        return "senior"
    if _JUNIOR.search(n):
        return "junior"
    return "mid"


# case-sensitive on purpose, like the Spark rlike it mirrors
_GERMAN = _re.compile(r"\b(und|der|die|das|mit|für|Kenntnisse|Erfahrung|"
                      r"Wir suchen|Deine|Ihre)\b")


def language(description):
    return "de" if _GERMAN.search(description or "") else "en"


_AGENCY = _re.compile(AGENCY_RX)


def is_agency(company):
    return bool(_AGENCY.search(_fold(company or "")))


CITY_STATES = {"berlin", "hamburg", "bremen", "wien",
               "basel-stadt", "genf", "geneve", "geneva"}


def city(area):
    """Adzuna location.area -> normalised city, as in notebook 03."""
    area = area or []
    a2 = _fold(area[1]) if len(area) > 1 and area[1] else None
    a3 = _fold(area[2]) if len(area) > 2 and area[2] else None
    if a2 in CITY_STATES:
        c = a2
    elif a3 is not None:
        c = a3
    else:
        c = a2 or "unknown"
    c = _re.sub(r"\s*\(.*?\)\s*$", "", c).strip()
    c = _re.sub(r"[-\s](umgebung|umland|land|stadt)$", "", c)
    c = _re.sub(r"^(region|regionalverband)\s+", "", c)
    c = _re.sub(r"(\s+im\s+breisgau|-mittelland)$", "", c)
    c = _re.sub(" am main$", "", c)
    return c.strip()
