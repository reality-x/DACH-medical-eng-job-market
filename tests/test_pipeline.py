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
            {"title": "Backend Developer", "id": f"{country}{role}{page}{i}"}
            for i in range(n)]}


def test_budget_is_never_exceeded():
    f = FakeFetcher(budget=50)
    PL.fetch_all(f)
    assert f.calls == 50


def test_breadth_first_covers_every_query_before_page_two():
    n_queries = len(PL.COUNTRIES) * len(PL.ROLES)
    f = FakeFetcher(budget=n_queries + 5)
    PL.fetch_all(f)
    first = f.pages[:n_queries]
    assert all(p == 1 for _, _, p in first)
    assert len({(c, r) for c, r, _ in first}) == n_queries
    assert all(p == 2 for _, _, p in f.pages[n_queries:])


def raw(title, company="Acme GmbH", created="2026-11-20T08:00:00Z",
        country="de", desc="Wir suchen Erfahrung mit Python und React"):
    return {"title": title, "company": {"display_name": company},
            "description": desc, "created": created,
            "location": {"area": ["Deutschland", "Berlin", "Mitte"]},
            "redirect_url": "https://example.com/x",
            "_country": country, "_query": "q"}


def test_silver_scope_dedupe_and_quality():
    rows = [raw("Backend Developer Java"),
            raw("Backend Developer Java"),            # duplicate
            raw("Embedded Software Engineer"),        # out of scope
            raw("Versicherungsagent"),                # other
            raw("Data Engineer", company=None),       # fails quality
            raw("ML Engineer", created="2024-06-01T00:00:00Z")]  # > 365 d
    clean, n_quar = PL.silver(rows, TODAY)
    assert [r["role_family"] for r in clean] == ["backend engineer"]
    assert clean[0]["skills"] == ["java", "python", "react"]  # title + desc
    assert n_quar == 1


def test_gold_shapes_and_rounding():
    rows = [raw(t, company=f"C{i}", created=f"2026-11-{10 + i:02d}T00:00:00Z",
                desc=f"Python {i}")
            for i, t in enumerate(["Backend Developer", "Data Engineer",
                                   "AI Engineer", "DevOps Engineer"])]
    clean, _ = PL.silver(rows, TODAY)
    g = PL.gold(clean, TODAY)
    ms = g["market_summary"][0]
    assert ms["live_postings"] == 4
    assert ms["median_age_days"] == 14         # ages 16,15,14,13
    assert ms["avg_age_days"] == 14.5
    assert {r["role_group"] for r in g["postings"]} == {"software", "data", "ai"}
    assert g["ai_breakdown"][0]["pct_of_ai"] == 100.0
    assert sum(b["n_postings"] for b in g["age_distribution"]) == 4


def test_half_up_rounding_matches_spark():
    assert PL.r1(0.25) == 0.3
    assert PL.r1(2.45) == 2.5
