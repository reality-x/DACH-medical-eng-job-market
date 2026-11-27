import sys
import pathlib

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "src"))

import classify as C

MED = "Wir entwickeln Medizinprodukte nach ISO 13485 für Kliniken."
DH = "Unsere DiGA hilft Patienten digital; wir sind ein Digital-Health-Startup."
NONE = "Wir sind ein mittelständisches Unternehmen im Maschinenbau."

# (title, description, expected family)
CASES = [
    # regulatory affairs: the title is enough
    ("Regulatory Affairs Manager (m/w/d)",             NONE, "ra manager"),
    ("Manager Regulatory Affairs EMEA",                NONE, "ra manager"),
    ("Regulatory Affairs Specialist",                  NONE, "ra specialist"),
    ("Regulatory Affairs Specialist (w/m/d)",          NONE, "ra specialist"),
    ("Referent Zulassung (m/w/d)",                     NONE, "ra specialist"),
    ("PRRC gemäß MDR Art. 15",                         NONE, "ra specialist"),
    ("QA/RA Manager",                                  NONE, "qa / ra"),
    ("Quality & Regulatory Affairs Specialist",        NONE, "qa / ra"),
    ("QM/RA Beauftragter",                             NONE, "qa / ra"),
    ("Clinical Affairs Manager",                       NONE, "clinical affairs"),
    ("Post-Market Surveillance Specialist",            NONE, "clinical affairs"),
    ("Medical Writer Clinical Evaluation",             NONE, "clinical affairs"),
    # quality needs a medical-device signal
    ("Qualitätsmanager (m/w/d)",                       MED,  "quality management"),
    ("Quality Engineer Medical Devices",               NONE, "quality management"),
    ("Qualitätsmanager (m/w/d)",                       NONE, "other"),
    # medtech
    ("Entwicklungsingenieur Medizintechnik",           NONE, "medtech r&d"),
    ("Systems Engineer",                               MED,  "medtech r&d"),
    ("Biomedical Engineer",                            MED,  "medtech r&d"),
    ("Softwareentwickler C++ Medizintechnik",          NONE, "medtech software"),
    ("Servicetechniker (m/w/d)",                       MED,  "medtech service"),
    ("Medizintechniker im Außendienst",                NONE, "medtech sales"),
    ("Medizinprodukteberater (m/w/d)",                 NONE, "medtech sales"),
    ("Key Account Manager Medical Devices",            NONE, "medtech sales"),
    ("Produktmanager Medizintechnik",                  NONE, "medtech product"),
    ("Produktionsmitarbeiter Medizintechnik",          NONE, "medtech production"),
    ("Servicetechniker (m/w/d)",                       NONE, "other"),
    # digital health
    ("Product Owner Digital Health",                   NONE, "digital health product"),
    ("Backend Developer",                              DH,   "digital health engineer"),
    ("Software Engineer eHealth",                      NONE, "digital health engineer"),
    ("HL7/FHIR Schnittstellenentwickler",              NONE, "health it"),
    ("Medizininformatiker (m/w/d)",                    NONE, "health it"),
    ("Digital Health Consultant",                      NONE, "digital health consulting"),
    # a medical-device title is not pulled into digital health by its description
    ("Softwareentwickler Medizintechnik",              DH,   "medtech software"),
    # excludes: senior, lead and head-of roles are out of scope
    ("Senior Regulatory Affairs Manager",              NONE, "senior level"),
    ("Head of Regulatory Affairs Medical Devices",     NONE, "senior level"),
    ("Leiter Zulassung Medizinprodukte",               NONE, "senior level"),
    ("Team Lead QA/RA",                                NONE, "senior level"),
    ("Principal Systems Engineer Medizintechnik",      NONE, "senior level"),
    ("Director Clinical Affairs",                      NONE, "senior level"),
    # other excludes
    ("Werkstudent Regulatory Affairs",                 NONE, "entry programme"),
    ("Praktikum Medizintechnik",                       NONE, "entry programme"),
    ("Gesundheits- und Krankenpfleger",                MED,  "clinical staff"),
    ("Assistenzarzt Kardiologie",                      MED,  "clinical staff"),
    ("Initiativbewerbung",                             MED,  "invalid"),
    ("Versicherungsagent",                             NONE, "other"),
]


@pytest.mark.parametrize("title,desc,expected", CASES)
def test_classify(title, desc, expected):
    assert C.classify(title, desc) == expected


def test_no_published_row_is_senior():
    published = [t for t, d, f in CASES if f in C.KEEP]
    assert all(C.seniority(t) != "senior" for t in published)


def test_role_groups():
    assert C.role_group("ra manager") == "regulatory"
    assert C.role_group("qa / ra") == "regulatory"
    assert C.role_group("medtech service") == "medtech"
    assert C.role_group("health it") == "digital health"
    assert C.role_group("clinical staff") == "excluded"


def test_every_published_family_has_a_group():
    assert all(C.role_group(f) != "excluded" for f in C.KEEP)


def test_seniority():
    assert C.seniority("Senior Regulatory Affairs Manager") == "senior"
    assert C.seniority("Leiter Zulassung") == "senior"
    assert C.seniority("Junior RA Specialist") == "junior"
    assert C.seniority("Regulatory Affairs Specialist") == "mid"


def test_city_normalisation():
    assert C.city(["Deutschland", "Bayern", "München (Kreis)"]) == "muenchen"
    assert C.city(["Deutschland", "Berlin", "Mitte"]) == "berlin"
    assert C.city(["Deutschland", "Hessen", "Frankfurt am Main"]) == "frankfurt"
    assert C.city(["Deutschland"]) == "unknown"
