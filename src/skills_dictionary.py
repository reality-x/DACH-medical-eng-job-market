"""Skills dictionary for regulatory affairs, medical devices and digital
health postings. Keys are published as-is; docs/app.js maps them to
display names (SKILL_LABEL) and categories to labels (SKILL_CAT_LABEL).

Matching runs on the lower-cased title plus description snippet.
"""

SKILLS = {
 # --- regulations and market-access frameworks ---------------------
 "mdr":        {"cat": "regulation", "aliases": [
                    r"\beu[\s\-]?mdr\b", r"\bmdr\b",
                    r"medical device regulation",
                    r"\b2017/745\b"]},
 "ivdr":       {"cat": "regulation", "aliases": [
                    r"\bivdr\b", r"in[\s\-]vitro[\s\-]diagnostic\w* "
                    r"regulation", r"\b2017/746\b"]},
 "mdd":        {"cat": "regulation", "aliases": [
                    r"\bmdd\b", r"\b93/42\b",
                    r"medical device directive"]},
 "fda":        {"cat": "regulation", "aliases": [
                    r"\bfda\b", r"\b510\s?\(k\)", r"\bde novo\b",
                    r"\bpma\b", r"21 cfr(?! (part )?820)"]},
 "qmsr":       {"cat": "regulation", "aliases": [
                    r"21 cfr (part )?820", r"\bqmsr\b", r"\bqsr\b"]},
 "mdsap":      {"cat": "regulation", "aliases": [r"\bmdsap\b"]},
 "ce_marking": {"cat": "regulation", "aliases": [
                    r"\bce[\s\-]?(marking|mark|kennzeichnung|"
                    r"konformit\w*)\b"]},
 "notified_body": {"cat": "regulation", "aliases": [
                    r"notified bod(y|ies)", r"benannte[rn]? stelle"]},
 "swissmedic": {"cat": "regulation", "aliases": [
                    r"\bswissmedic\b", r"\bmepv\b"]},
 "ukca":       {"cat": "regulation", "aliases": [r"\bukca\b",
                                                 r"\bmhra\b"]},
 "diga":       {"cat": "regulation", "aliases": [
                    r"\bdiga\b", r"\bdipa\b",
                    r"digitale gesundheitsanwendung"]},
 "gdpr":       {"cat": "regulation", "aliases": [
                    r"\bgdpr\b", r"\bdsgvo\b", r"\bdatenschutz\b"]},
 "ai_act":     {"cat": "regulation", "aliases": [
                    r"\bai act\b", r"\bki[\s\-]verordnung\b"]},
 "gmp":        {"cat": "regulation", "aliases": [r"\bc?gmp\b",
                                                 r"good manufacturing"]},

 # --- harmonised standards ----------------------------------------
 "iso13485":   {"cat": "standard",   "aliases": [r"\b13485\b"]},
 "iso14971":   {"cat": "standard",   "aliases": [r"\b14971\b"]},
 "iec62304":   {"cat": "standard",   "aliases": [r"\b62304\b"]},
 "iec60601":   {"cat": "standard",   "aliases": [r"\b60601\b"]},
 "iec62366":   {"cat": "standard",   "aliases": [r"\b62366\b"]},
 "iso10993":   {"cat": "standard",   "aliases": [r"\b10993\b",
                                                 r"biocompatib",
                                                 r"biokompatib"]},
 "iso14155":   {"cat": "standard",   "aliases": [r"\b14155\b"]},
 "iec82304":   {"cat": "standard",   "aliases": [r"\b82304\b"]},
 "iec81001":   {"cat": "standard",   "aliases": [r"\b81001\b"]},
 "iso27001":   {"cat": "standard",   "aliases": [r"\b27001\b"]},
 "iso9001":    {"cat": "standard",   "aliases": [r"\b9001\b"]},

 # --- regulatory and quality practices -----------------------------
 "risk_mgmt":  {"cat": "practice",   "aliases": [
                    r"risk management", r"risikomanagement",
                    r"risikoanalyse", r"risk analysis", r"\bfmea\b"]},
 "tech_doc":   {"cat": "practice",   "aliases": [
                    r"technical documentation",
                    r"technische[rn]? dokumentation",
                    r"technical file", r"design dossier"]},
 "clinical_eval": {"cat": "practice", "aliases": [
                    r"clinical evaluation", r"klinische[rn]? bewertung",
                    r"\bcer\b", r"clinical evidence"]},
 "pms":        {"cat": "practice",   "aliases": [
                    r"post[\s\-]market", r"\bpms\b", r"\bpmcf\b",
                    r"marktbeobachtung", r"\bpsur\b"]},
 "vigilance":  {"cat": "practice",   "aliases": [
                    r"vigilan[cz]", r"complaint handling",
                    r"reklamationsmanagement", r"beschwerdemanagement"]},
 "capa":       {"cat": "practice",   "aliases": [r"\bcapa\b"]},
 "design_control": {"cat": "practice", "aliases": [
                    r"design control", r"design history file",
                    r"\bdhf\b", r"design transfer"]},
 "validation": {"cat": "practice",   "aliases": [
                    r"\bvalidation\b", r"\bverification\b",
                    r"validierung", r"verifizierung",
                    r"\bv&v\b", r"\biq/oq/pq\b"]},
 "audits":     {"cat": "practice",   "aliases": [r"\baudits?\b",
                                                 r"auditierung"]},
 "usability":  {"cat": "practice",   "aliases": [
                    r"usability engineering", r"human factors",
                    r"gebrauchstauglichkeit"]},
 "cybersecurity": {"cat": "practice", "aliases": [
                    r"cyber[\s\-]?security", r"informationssicherheit"]},
 "submissions": {"cat": "practice",  "aliases": [
                    r"submissions?\b", r"zulassungsantr\w*",
                    r"einreichung\w*", r"registrierung\w*",
                    r"market access", r"marktzugang"]},
 "udi":        {"cat": "practice",   "aliases": [r"\budi\b",
                                                 r"\beudamed\b"]},
 "qms":        {"cat": "practice",   "aliases": [
                    r"\bqms\b", r"quality management system",
                    r"qualitaetsmanagementsystem",
                    r"qualitätsmanagementsystem"]},
 "sop":        {"cat": "practice",   "aliases": [r"\bsops?\b"]},
 "reimbursement": {"cat": "practice", "aliases": [
                    r"reimbursement", r"erstattung", r"\bhta\b"]},

 # --- health IT and interoperability ------------------------------
 "hl7":        {"cat": "health_it",  "aliases": [r"\bhl7\b"]},
 "fhir":       {"cat": "health_it",  "aliases": [r"\bfhir\b"]},
 "dicom":      {"cat": "health_it",  "aliases": [r"\bdicom\b",
                                                 r"\bpacs\b"]},
 "ihe":        {"cat": "health_it",  "aliases": [r"\bihe\b"]},
 "telematik":  {"cat": "health_it",  "aliases": [
                    r"telematikinfrastruktur", r"\bgematik\b",
                    r"elektronische[rn]? patientenakte"]},
 "kis":        {"cat": "health_it",  "aliases": [
                    r"krankenhausinformationssystem", r"\bkis\b",
                    r"\behr\b", r"\bemr\b", r"\bepic\b"]},
 "samd":       {"cat": "health_it",  "aliases": [
                    r"\bsamd\b", r"software as a medical device",
                    r"medical device software", r"medizinische software"]},

 # --- engineering tools and languages -----------------------------
 "python":     {"cat": "tool",       "aliases": [r"\bpython\b"]},
 "cpp":        {"cat": "tool",       "aliases": [r"\bc\+\+"]},
 "csharp":     {"cat": "tool",       "aliases": [r"\bc#", r"\.net\b"]},
 "java":       {"cat": "tool",       "aliases": [r"\bjava\b(?!script)"]},
 "matlab":     {"cat": "tool",       "aliases": [r"\bmatlab\b",
                                                 r"\bsimulink\b"]},
 "labview":    {"cat": "tool",       "aliases": [r"\blabview\b"]},
 "cad":        {"cat": "tool",       "aliases": [
                    r"\bcad\b", r"\bsolidworks\b", r"\bcreo\b",
                    r"\bcatia\b", r"\bsiemens nx\b", r"\binventor\b"]},
 "alm":        {"cat": "tool",       "aliases": [
                    r"\bpolarion\b", r"\bdoors\b", r"\bjama\b",
                    r"\bcodebeamer\b"]},
 "jira":       {"cat": "tool",       "aliases": [r"\bjira\b",
                                                 r"\bconfluence\b"]},
 "sap":        {"cat": "tool",       "aliases": [r"\bsap\b"]},
 "cloud":      {"cat": "tool",       "aliases": [r"\baws\b", r"\bazure\b",
                                                 r"\bgcp\b",
                                                 r"google cloud"]},
 "ai_ml":      {"cat": "tool",       "aliases": [
                    r"machine learning", r"maschinelles lernen",
                    r"künstliche intelligenz", r"artificial intelligence",
                    r"deep learning"]},
}

CATEGORY = {k: v["cat"] for k, v in SKILLS.items()}
