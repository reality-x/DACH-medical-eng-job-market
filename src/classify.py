"""Title classification and row parsing for the GitHub Actions pipeline.

Three published role groups:

    regulatory      regulatory affairs, QA/RA, clinical affairs,
                    medical-device quality management
    medtech         medical device engineering, product, sales, service
    digital health  health IT, digital health product, engineering,
                    consulting

Regulatory titles are unambiguous on their own. MedTech and digital
health titles usually are not ("Servicetechniker (m/w/d)" at a device
maker), so those families need a domain signal: in the title, or else
in the description snippet. tests/test_classify.py holds the cases.
"""

import re as _re

AGENCY_RX = (r"(consulting|personal|recruit|staffing|hays|"
             r"randstad|michael page|robert half|experis|"
             r"gulp|solcom|amoria|darwin|huzzle|talent)")

INVALID = (r"^initiativbewerbung|initiativbewerbung|talentpool|"
           r"^deine aufgaben|^\"+title|^zum \d|^wachstum durch")

ENTRY = (r"\bausbildung\b|duales? studium|dualer bachelor|"
         r"\bwerkstudent|werkstudierend|\bpraktikum\b|\bpraktikant|"
         r"\btrainee\b|traineeprogramm|bachelor thesis|master thesis|"
         r"masterarbeit|master student|studienkolleg|"
         r"\bdhbw\b|\bhwr\b|abschlussarbeit|\binternship\b|\bintern\b")

# Clinical and care staff: medical, but not the medical-device industry.
CLINICAL_STAFF = (r"arzt\b|aerztin|physician|\bnurse\b|"
                  r"pflege|krankenpfleg|hebamme|"
                  r"medizinische[rn]? fachangestellte|\bmfa\b|"
                  r"\bmta\b|\bmtr\b|\bmtl\b|radiologietechnolog|"
                  r"apothek|pharmazeut|therapeut|zahnmedizin|"
                  r"rettungs|sanitaeter|altenpfleg|betreuungskraft")

# --- domain context --------------------------------------------------

MED_CTX = (r"medizintechn|medical device|medizinprodukt|\bmedtech\b|"
           r"med[\s\-]tech|medical technology|medical equipment|"
           r"in[\s\-]vitro|\bivdr?\b|\bmdr\b|iso 13485|iec 62304|"
           r"iec 60601|medizingeraet|medical imaging|"
           r"diagnostics?\b|implant|orthopae?di|cardio|"
           r"chirurg|surgical|dental|healthineers|"
           r"krankenhaustechn|klinik(technik|en)?\b|hospital")

DH_CTX = (r"digital health|digitale gesundheit|e[\s\-]?health|"
          r"\bdiga\b|\bdipa\b|telemedi|telematik|health[\s\-]?tech|"
          r"healthcare it|health it|gesundheits[\s\-]?it|"
          r"medizininformatik|medical informatics|health informatics|"
          r"\bkis\b|krankenhausinformation|patientenakte|\bepa\b|"
          r"\bhl7\b|\bfhir\b|\bdicom\b|\bihe\b|\bsamd\b|"
          r"software as a medical device|mhealth|digital therapeutic|"
          r"healthcare software|gesundheitsapp|health app")

# --- regulatory ------------------------------------------------------

_RA = (r"regulatory|zulassung|\bra\b|registrierung von medizin|"
       r"\bprrc\b|person responsible for regulatory|"
       r"verantwortliche person.*vorschriften|"
       r"mdr[\s\-]?(manager|specialist|expert|consultant)|"
       r"ivdr[\s\-]?(manager|specialist|expert|consultant)")

# Combined quality + regulatory roles.
R_QARA = (r"\bqa[\s\-/&]*ra\b|\bra[\s\-/&]*qa\b|\bqm[\s\-/&]*ra\b|"
          r"\bra[\s\-/&]*qm\b|\bqara\b|\bqra\b|"
          r"quality\s*(and|&|/)\s*regulatory|"
          r"regulatory\s*(and|&|/)\s*quality|"
          r"qualitaet\w*\s*(und|&|/)\s*(regulatory|zulassung)|"
          r"(regulatory|zulassung)\w*\s*(und|&|/)\s*qualitaet")

# Senior, lead and head-of titles are excluded before this runs.
R_RA_MANAGER = (r"(" + _RA + r").*(manager|verantwortlich)|"
                r"manager\b.*(" + _RA + r")")

R_RA_SPECIALIST = _RA

R_CLINICAL = (r"clinical affairs|clinical evaluation|klinische bewertung|"
              r"klinische pruefung|clinical investigation|"
              r"post[\s\-]?market|\bpms\b|marktueberwachung|"
              r"vigilan[cz]|medical writer|clinical (study|project) "
              r"manager|clinical research|\bcra\b|clinical scientist")

# Generic quality titles, counted only with a medical-device signal.
R_QUALITY = (r"quality|qualitaet|\bqm\b|\bqmb\b|\bqs\b|\bqa\b|\bcapa\b|"
             r"auditor|compliance|validier|validation|verification|"
             r"verifizier")

# --- digital health --------------------------------------------------

R_HEALTH_IT = (r"\bhl7\b|\bfhir\b|\bdicom\b|\bihe\b|interoperab|"
               r"medizininformati|medical informati|health informati|"
               r"\bkis\b|krankenhausinformation|\bpacs\b|\bris\b|"
               r"telematik|health it|healthcare it|gesundheits[\s\-]?it|"
               r"klinik[\s\-]?it|it[\s\-]im[\s\-]gesundheitswesen")

R_PRODUCT = (r"product (manager|owner|lead|management)|produktmanag|"
             r"product marketing|portfolio manag|produktverantwort")

R_ENGINEER_SW = (r"software|developer|entwickler|programmier|"
                 r"engineer|ingenieur|data scien|machine learning|"
                 r"\bml\b|\bai\b|\bki\b|architect|architekt|devops|"
                 r"full[\s\-]?stack|backend|frontend|mobile|\bapp\b")

R_SOFTWARE = (r"software|developer|programmier|softwareentwickl|"
              r"full[\s\-]?stack|backend|frontend|\bapp[\s\-]entwickl|"
              r"\bit[\s\-]")

R_CONSULT = (r"consult|berater|manager|strateg|business|referent|"
             r"projekt|project|specialist|spezialist|expert|analyst|"
             r"koordinat|coordinat|lead|leiter|head")

# --- medtech ---------------------------------------------------------

R_SALES = (r"sales|vertrieb|account manag|key account|aussendienst|"
           r"gebietsleit|area manager|territory|"
           r"business develop|medizinprodukteberater|"
           r"application specialist|applikationsspezialist|"
           r"clinical specialist|produktspezialist|product specialist")

R_SERVICE = (r"service|techniker|technician|instandhalt|wartung|"
             r"field|medizintechniker|biomedizintechniker|"
             r"elektroniker|mechatroniker|inbetriebnahme|"
             r"kundendienst|support")

R_PRODUCTION = (r"produktion|production|fertigung|manufactur|"
                r"prozessingenieur|process engineer|operator|"
                r"montage|assembly|supply chain|logistik|einkauf|"
                r"procurement|sterilis")

R_RND = (r"engineer|ingenieur|entwickl|develop|konstrukt|design|"
         r"physiker|physicist|wissenschaftl|scientist|r&d|f&e|"
         r"forschung|research|systems|hardware|mechani|elektrotech|"
         r"biomedical|biomedizin|medizintechnik|projektleit|"
         r"project (manager|lead)")


_SENIOR = _re.compile(r"\b(senior|sr\.?|lead|principal|head|director|"
                      r"staff|chief|\bvp\b|leiter|leitung)\b")
_JUNIOR = _re.compile(r"\b(junior|jr\.?|entry|graduate|absolvent|"
                      r"einsteiger|associate)\b")


def _fold(s):
    s = (s or "").lower().strip()
    for a, b_ in [("ä", "ae"), ("ö", "oe"), ("ü", "ue"), ("ß", "ss")]:
        s = s.replace(a, b_)
    return s


def _has(rx, s):
    return bool(_re.search(rx, s))


def classify(title, description=""):
    """Title first; the description only decides whether an otherwise
    generic title belongs to the medical-device or digital-health
    industry."""
    n = _fold(title)
    d = _fold(description)

    if _has(INVALID, n):
        return "invalid"
    if _has(ENTRY, n):
        return "entry programme"
    if _has(CLINICAL_STAFF, n):
        return "clinical staff"
    # Out of scope by choice: senior, lead and head-of roles.
    if _SENIOR.search(n):
        return "senior level"

    # regulatory: the title names it, no context needed
    if _has(R_QARA, n):
        return "qa / ra"
    if _has(R_RA_MANAGER, n):
        return "ra manager"
    if _has(R_RA_SPECIALIST, n):
        return "ra specialist"
    if _has(R_CLINICAL, n):
        return "clinical affairs"

    med_t, dh_t = _has(MED_CTX, n), _has(DH_CTX, n)
    med_d, dh_d = _has(MED_CTX, d), _has(DH_CTX, d)
    med = med_t or med_d
    # a digital-health title wins; a digital-health description only
    # when the title does not already say medical device
    dh = dh_t or (dh_d and not med_t)

    if med and _has(R_QUALITY, n):
        return "quality management"

    # digital health
    if _has(R_HEALTH_IT, n):
        return "health it"
    if dh:
        if _has(R_PRODUCT, n):
            return "digital health product"
        if _has(R_ENGINEER_SW, n):
            return "digital health engineer"
        if _has(R_CONSULT, n) or dh_t:
            return "digital health consulting"

    # medtech
    if med:
        if _has(R_PRODUCT, n):
            return "medtech product"
        if _has(R_SALES, n):
            return "medtech sales"
        if _has(R_SOFTWARE, n):
            return "medtech software"
        if _has(R_SERVICE, n):
            return "medtech service"
        if _has(R_PRODUCTION, n):
            return "medtech production"
        if _has(R_RND, n):
            return "medtech r&d"
    return "other"


REGULATORY_FAMILIES = ["ra manager", "ra specialist", "qa / ra",
                       "clinical affairs", "quality management"]
MEDTECH_FAMILIES = ["medtech r&d", "medtech software", "medtech product",
                    "medtech sales", "medtech service",
                    "medtech production"]
DH_FAMILIES = ["digital health engineer", "digital health product",
               "health it", "digital health consulting"]

ROLE_GROUP = {}
for _f in REGULATORY_FAMILIES:
    ROLE_GROUP[_f] = "regulatory"
for _f in MEDTECH_FAMILIES:
    ROLE_GROUP[_f] = "medtech"
for _f in DH_FAMILIES:
    ROLE_GROUP[_f] = "digital health"

# Published families. Everything else lands in the excluded count.
KEEP = set(REGULATORY_FAMILIES + MEDTECH_FAMILIES + DH_FAMILIES)


def role_group(family):
    return ROLE_GROUP.get(family, "excluded")


def seniority(title):
    n = _fold(title)
    if _SENIOR.search(n):
        return "senior"
    if _JUNIOR.search(n):
        return "junior"
    return "mid"


# case-sensitive on purpose
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
    """Adzuna location.area -> normalised city."""
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
