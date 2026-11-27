import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "src"))

from matcher import extract, evaluate


def test_core_regulatory_frameworks():
    txt = "Erfahrung mit EU MDR, IVDR und FDA 510(k) Einreichungen"
    assert {"mdr", "ivdr", "fda", "submissions"} <= set(extract(txt))


def test_standards_by_number():
    txt = "Kenntnisse der ISO 13485, ISO 14971 und IEC 62304"
    assert set(extract(txt)) == {"iso13485", "iso14971", "iec62304"}


def test_qmsr_is_not_counted_as_generic_fda_cfr():
    out = extract("Compliance with 21 CFR 820")
    assert "qmsr" in out and "fda" not in out


def test_german_practices():
    txt = ("Erstellung der technischen Dokumentation und klinischen "
           "Bewertung, Risikomanagement")
    assert {"tech_doc", "clinical_eval", "risk_mgmt"} <= set(extract(txt))


def test_health_it():
    assert {"hl7", "fhir"} <= set(extract("Schnittstellen mit HL7 und FHIR"))


def test_java_not_matched_inside_javascript():
    assert "java" not in extract("Strong JavaScript skills required")


def test_empty_input():
    assert extract("") == []
    assert extract(None) == []


def test_no_duplicates_returned():
    assert extract("MDR, mdr, MDR").count("mdr") == 1


def test_result_is_sorted():
    out = extract("ISO 13485, MDR, CAPA, Python")
    assert out == sorted(out)


def test_evaluate_perfect_score():
    rows = [{"description": "MDR and ISO 13485", "skills_true": "mdr;iso13485"}]
    r = evaluate(rows)
    assert r["precision"] == 1.0 and r["recall"] == 1.0


def test_evaluate_catches_a_miss():
    rows = [{"description": "MDR only", "skills_true": "mdr;iso13485"}]
    assert evaluate(rows)["recall"] < 1.0
