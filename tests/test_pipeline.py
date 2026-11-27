import datetime as dt
import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "src"))

import pipeline as PL

TODAY = dt.date(2026, 11, 26)


class FakeFetcher:
    """Every query has 3 full pages; counts calls against a budget."""
    def __init__(self, budget):
        self.budget, self.calls, self.pages = budget, 0, []

    def get(self, country, role, page):
        if self.calls >= self.budget:
            raise PL.Budget()
        self.calls += 1
        self.pages.append((country, role, page))
        n = PL.PER_PAGE if page < 3 else 10
        return {"count": 110, "results": [
            {"title": "Regulatory Affairs Manager", "id": f"{country}{role}{page}{i}"}
            for i in range(n)]}


def test_budget_is_never_exceeded():
    # below the 3 pages x every query the fake offers, so the cap bites
    budget = 2 * len(PL.COUNTRIES) * len(PL.ROLES)
    f = FakeFetcher(budget=budget)
    PL.fetch_all(f)
    assert f.calls == budget


def test_breadth_first_covers_every_query_before_page_two():
    n_queries = len(PL.COUNTRIES) * len(PL.ROLES)
    f = FakeFetcher(budget=n_queries + 5)
    PL.fetch_all(f)
    first = f.pages[:n_queries]
    assert all(p == 1 for _, _, p in first)
    assert len({(c, r) for c, r, _ in first}) == n_queries
    assert all(p == 2 for _, _, p in f.pages[n_queries:])


def raw(title, company="Acme GmbH", created="2026-11-20T08:00:00Z",
        country="de", desc="Wir suchen Erfahrung mit MDR und ISO 13485"):
    return {"title": title, "company": {"display_name": company},
            "description": desc, "created": created,
            "location": {"area": ["Deutschland", "Berlin", "Mitte"]},
            "redirect_url": "https://example.com/x",
            "_country": country, "_query": "q"}


def test_silver_scope_dedupe_and_quality():
    rows = [raw("Regulatory Affairs Manager"),
            raw("Regulatory Affairs Manager"),        # duplicate
            raw("Gesundheits- und Krankenpfleger"),   # out of scope
            raw("Versicherungsagent", desc="Versicherung"),  # other
            raw("RA Specialist", company=None),       # fails quality
            raw("Senior Regulatory Affairs Manager"), # senior: excluded
            raw("QA/RA Manager", created="2024-06-01T00:00:00Z")]  # > 365 d
    clean, n_quar = PL.silver(rows, TODAY)
    assert [r["role_family"] for r in clean] == ["ra manager"]
    assert clean[0]["skills"] == ["iso13485", "mdr"]  # title + desc
    assert n_quar == 1


def test_gold_shapes_and_rounding():
    rows = [raw(t, company=f"C{i}", created=f"2026-11-{10 + i:02d}T00:00:00Z",
                desc=f"Medizinprodukte {i}")
            for i, t in enumerate(["Regulatory Affairs Specialist",
                                   "Entwicklungsingenieur Medizintechnik",
                                   "Product Owner Digital Health",
                                   "Servicetechniker Medizintechnik"])]
    clean, _ = PL.silver(rows, TODAY)
    g = PL.gold(clean, TODAY)
    ms = g["market_summary"][0]
    assert ms["live_postings"] == 4
    assert ms["median_age_days"] == 14         # ages 16,15,14,13
    assert ms["avg_age_days"] == 14.5
    assert {r["role_group"] for r in g["postings"]} == {
        "regulatory", "medtech", "digital health"}
    assert g["ra_breakdown"][0]["pct_of_ra"] == 100.0
    assert sum(b["n_postings"] for b in g["age_distribution"]) == 4


def test_half_up_rounding_matches_spark():
    assert PL.r1(0.25) == 0.3
    assert PL.r1(2.45) == 2.5


def test_public_roundtrip_keeps_fields_and_moves_age_forward():
    clean, _ = PL.silver([raw("Regulatory Affairs Manager")], TODAY)
    pub = PL.to_public(clean[0])
    later = PL.from_public(pub, TODAY + dt.timedelta(days=10))
    assert later["age_days"] == clean[0]["age_days"] + 10
    assert later["role_group"] == "regulatory"
    assert later["skills"] == clean[0]["skills"]


def test_page_one_of_every_query_fits_the_budget():
    assert len(PL.COUNTRIES) * len(PL.ROLES) <= 25
