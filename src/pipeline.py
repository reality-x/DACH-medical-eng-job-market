"""Pipeline for GitHub Actions: Regulatory Affairs, MedTech and Digital
Health postings in the DACH region.

Postings come from our own Adzuna queries and are stored in
state/postings_snapshot.json. A run with a call budget refreshes that
snapshot; a run without one reuses it and moves every age forward to
today. Every aggregate is rebuilt from the rows, in the JSON shapes the
site reads.

    CALL_BUDGET=0  python src/pipeline.py   # rebuild from the snapshot
    CALL_BUDGET=25 python src/pipeline.py   # refresh from Adzuna first
    python src/pipeline.py --raw-dir DIR    # replay cached responses

Environment:
    ADZUNA_APP_ID, ADZUNA_APP_KEY   needed only when CALL_BUDGET > 0
    CALL_BUDGET                     hard cap on API calls (default 25)
    COUNTRIES                       comma list (default de,ch)
    CALL_PACE                       seconds between calls (default 13)
    MAX_DAYS_OLD                    only fetch postings this new (default 14)
"""

import argparse
import datetime as dt
import hashlib
import json
import os
import pathlib
import random
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict
from decimal import Decimal, ROUND_HALF_UP

sys.path.insert(0, str(pathlib.Path(__file__).parent))

import classify as C                      # noqa: E402
from matcher import extract              # noqa: E402
from skills_dictionary import CATEGORY   # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "data"
STATE = ROOT / "state"

BASE = "https://api.adzuna.com/v1/api/jobs"

COUNTRIES = [c.strip() for c in
             os.environ.get("COUNTRIES", "de,ch").split(",") if c.strip()]

# Searches, as label -> Adzuna keyword parameters. "what" needs every
# word; "what_or" needs any one of them, so several small searches share
# one call. They are deliberately broad: classify.py decides what is in
# scope. 8 searches x 2 countries = 16 calls for page 1 of everything.
QUERIES = {
    "regulatory affairs": {"what": "regulatory affairs"},
    "medical device":     {"what": "medical device"},
    "medizintechnik":     {"what": "medizintechnik"},
    "medizinprodukte":    {"what": "medizinprodukte"},
    "qualitaetsmanagement": {"what": "qualitätsmanagement medizinprodukte"},
    "digital health":     {"what": "digital health"},
    "health it terms":    {"what_or": "ehealth diga telemedizin fhir hl7"},
    "ra standards":       {"what_or": "13485 14971 62304 ivdr prrc"},
}
ROLES = list(QUERIES)

# Newest first, and only postings Adzuna first saw in the last N days,
# so the call budget goes to fresh adverts rather than long-open ones.
SORT_BY = "date"
MAX_DAYS_OLD = int(os.environ.get("MAX_DAYS_OLD", 14))

PER_PAGE = 50
MAX_PAGES = 45
MAX_AGE_DAYS = 365
# Seconds between calls. Adzuna's free tier allows 5 calls/minute, so the
# default stays under that; set CALL_PACE lower on a paid plan.
PACE = float(os.environ.get("CALL_PACE", 13))
RETRIES = 6
STALE_MIN_POSTINGS = 5
FAMILY_MIN = 20        # skill tables skip thinner families
SKILL_MIN = 3

ISO = "%Y-%m-%dT00:00:00.000"


# --------------------------------------------------------------------------
# helpers that mirror Spark SQL semantics
# --------------------------------------------------------------------------

def r1(x):
    """Spark ROUND(x, 1) is half-up; Python's round() is half-even."""
    if x is None:
        return None
    return float(Decimal(str(x)).quantize(Decimal("0.1"), ROUND_HALF_UP))


def pct(rows, pred):
    return r1(100 * sum(1 for r in rows if pred(r)) / len(rows)) if rows else 0.0


def avg(vals):
    vals = list(vals)
    return r1(sum(vals) / len(vals)) if vals else None


def median(vals):
    """percentile_approx(x, 0.5): the smallest value with rank >= n/2."""
    v = sorted(vals)
    if not v:
        return None
    k = max(0, -(-len(v) // 2) - 1)
    return v[k]


def iso(d):
    return d.strftime(ISO)


def group(rows, *keys):
    g = defaultdict(list)
    for r in rows:
        g[tuple(r[k] for k in keys)].append(r)
    return g


# --------------------------------------------------------------------------
# 1. fetch, under a hard call budget
# --------------------------------------------------------------------------

class Budget(Exception):
    pass


class Fetcher:
    def __init__(self, app_id, app_key, budget, raw_dir):
        self.app_id, self.app_key = app_id, app_key
        self.budget, self.calls = budget, 0
        self.raw_dir = raw_dir
        raw_dir.mkdir(parents=True, exist_ok=True)

    def get(self, country, role, page):
        path = self.raw_dir / f"{country}__{role.replace(' ', '-')}__p{page}.json"
        if path.exists():                       # re-run on the same day
            return json.loads(path.read_text())
        if self.calls >= self.budget:
            raise Budget()

        qs = urllib.parse.urlencode({
            "app_id": self.app_id, "app_key": self.app_key,
            "results_per_page": PER_PAGE, **QUERIES[role],
            "sort_by": SORT_BY, "max_days_old": MAX_DAYS_OLD,
            "content-type": "application/json"})
        url = f"{BASE}/{country}/search/{page}?{qs}"

        for attempt in range(RETRIES):
            if self.calls >= self.budget:
                raise Budget()
            self.calls += 1
            try:
                with urllib.request.urlopen(url, timeout=30) as r:
                    body = r.read().decode()
                path.write_text(body)
                time.sleep(PACE)
                return json.loads(body)
            except urllib.error.HTTPError as e:
                if e.code == 410:               # past the last page
                    return {"results": [], "count": 0}
                if e.code not in (429, 500, 502, 503, 504):
                    raise
                # a 429 means the per-minute window is full: wait it out
                wait = (65 if e.code == 429
                        else min(60, 2 ** attempt) * (0.5 + random.random()))
                print(f"  HTTP {e.code}, sleeping {wait:.0f}s")
                time.sleep(wait)
            except (urllib.error.URLError, TimeoutError) as e:
                wait = min(60, 2 ** attempt) * (0.5 + random.random())
                print(f"  {type(e).__name__}, sleeping {wait:.0f}s")
                time.sleep(wait)
        raise RuntimeError(f"gave up on {country}/{role}/p{page}")


def fetch_all(fetcher):
    """Breadth first: page 1 of every query before page 2 of any, so a
    tight budget still covers every role in every country."""
    results = []
    frontier = [(c, r) for c in COUNTRIES for r in ROLES]
    page = 1
    try:
        while frontier and page <= MAX_PAGES:
            nxt = []
            for country, role in frontier:
                data = fetcher.get(country, role, page)
                rows = data.get("results", [])
                for x in rows:
                    x["_country"] = country
                    x["_query"] = role
                results.extend(rows)
                if page == 1:
                    print(f"{country}  {role:28} total={data.get('count', 0):6}")
                if len(rows) == PER_PAGE:
                    nxt.append((country, role))
            frontier, page = nxt, page + 1
    except Budget:
        print(f"call budget of {fetcher.budget} reached at page depth {page}")
    print(f"API calls this run: {fetcher.calls}, raw rows: {len(results):,}")
    return results


def load_raw_dir(raw_dir):
    results = []
    for f in sorted(raw_dir.glob("*.json")):
        country, role = f.stem.split("__")[:2]
        for x in json.loads(f.read_text()).get("results", []):
            x["_country"] = country
            x["_query"] = role.replace("-", " ")
            results.append(x)
    return results


# --------------------------------------------------------------------------
# 2. silver: parse, classify, validate, dedupe, scope
# --------------------------------------------------------------------------

def parse(x, today):
    title = (x.get("title") or "").strip()
    company = ((x.get("company") or {}).get("display_name") or "").strip() or None
    desc = x.get("description") or ""
    city = C.city((x.get("location") or {}).get("area"))
    created = x.get("created")
    try:
        created_date = dt.date.fromisoformat(created[:10]) if created else None
    except ValueError:
        created_date = None

    def num(k):
        v = x.get(k)
        try:
            return float(v) if v is not None else None
        except (TypeError, ValueError):
            return None

    key = "|".join([title.lower(), (company or "").lower(), city,
                    desc.lower()[:200]])
    family = C.classify(title, desc)
    return {
        "posting_id": hashlib.sha256(key.encode()).hexdigest(),
        "title": title,
        "company": company,
        "city": city,
        "country": x["_country"],
        "role_family": family,
        "role_group": C.role_group(family),
        "seniority": C.seniority(title),
        "language": C.language(desc),
        "is_agency": C.is_agency(company),
        "created": created or "",
        "created_date": created_date,
        "age_days": (today - created_date).days if created_date else None,
        "salary_min": num("salary_min"),
        "salary_max": num("salary_max"),
        "desc_truncated": desc.endswith("…"),
        "salary_known": True,
        "url": x.get("redirect_url") or None,
        "text": f"{title} . {desc}",
    }


def quality_ok(r, today):
    return (len(r["title"]) > 3
            and r["role_family"] != "invalid"
            and r["company"] is not None and len(r["company"]) > 1
            and r["city"] is not None
            and r["created_date"] is not None
            and dt.date(2024, 1, 1) <= r["created_date"] <= today
            and r["age_days"] >= 0
            and (r["salary_min"] is None or 12000 <= r["salary_min"] <= 400000)
            and (r["salary_max"] is None or r["salary_min"] is None
                 or r["salary_max"] >= r["salary_min"]))


def silver(raw, today):
    parsed = [parse(x, today) for x in raw]
    passed = [r for r in parsed if quality_ok(r, today)]
    n_quarantine = len(parsed) - len(passed)

    # one row per posting_id, the earliest created
    best = {}
    for r in passed:
        cur = best.get(r["posting_id"])
        if cur is None or r["created"] < cur["created"]:
            best[r["posting_id"]] = r
    deduped = list(best.values())

    clean = [r for r in deduped
             if r["role_family"] in C.KEEP and r["age_days"] <= MAX_AGE_DAYS]

    print(f"parsed {len(parsed):,} -> passed {len(passed):,} "
          f"-> unique {len(deduped):,} -> in scope {len(clean):,} "
          f"(quarantined {n_quarantine:,})")
    for r in clean:
        r["skills"] = extract(r.pop("text"))
    return clean, n_quarantine


# --------------------------------------------------------------------------
# 3. gold: the tables the site reads
# --------------------------------------------------------------------------

def gold(P, today):
    T = iso(today)
    n_all = len(P)
    out = {}

    ages = [r["age_days"] for r in P]
    out["market_summary"] = [{
        "snapshot_date": T,
        "live_postings": n_all,
        "employers": len({r["company"] for r in P}),
        "avg_age_days": avg(ages),
        "median_age_days": median(ages),
        "pct_over_7d": pct(P, lambda r: r["age_days"] > 7),
        "pct_over_30d": pct(P, lambda r: r["age_days"] > 30),
        "pct_over_60d": pct(P, lambda r: r["age_days"] > 60),
        "pct_over_90d": pct(P, lambda r: r["age_days"] > 90),
        "pct_agency": pct(P, lambda r: r["is_agency"]),
        "pct_english": pct(P, lambda r: r["language"] == "en"),
    }]

    buckets = [(7, "0-7 days"), (14, "8-14 days"), (30, "15-30 days"),
               (60, "31-60 days"), (90, "61-90 days"),
               (180, "91-180 days"), (10 ** 9, "181-365 days")]
    counts = defaultdict(int)
    for r in P:
        for i, (hi, _) in enumerate(buckets):
            if r["age_days"] <= hi:
                counts[i] += 1
                break
    out["age_distribution"] = [
        {"bucket": buckets[i][1], "sort_key": i + 1, "n_postings": n,
         "pct": r1(100 * n / n_all)}
        for i, n in sorted(counts.items())]

    stale = []
    for (company, agency), rows in group(P, "company", "is_agency").items():
        if len(rows) >= STALE_MIN_POSTINGS:
            stale.append({
                "company": company, "is_agency": agency,
                "n_postings": len(rows),
                "avg_age_days": avg(r["age_days"] for r in rows),
                "oldest_days": max(r["age_days"] for r in rows),
                "pct_over_60d": pct(rows, lambda r: r["age_days"] > 60)})
    out["stale_by_company"] = sorted(
        stale, key=lambda x: -x["avg_age_days"])[:60]

    out["agency_comparison"] = [{
        "poster_type": "Recruitment agency" if agency else "Direct employer",
        "n_postings": len(rows),
        "pct": r1(100 * len(rows) / n_all),
        "avg_age_days": avg(r["age_days"] for r in rows),
        "median_age_days": median(r["age_days"] for r in rows),
        "pct_over_60d": pct(rows, lambda r: r["age_days"] > 60),
    } for (agency,), rows in sorted(group(P, "is_agency").items())]

    rb = []
    for (c, g, f, s), rows in group(
            P, "country", "role_group", "role_family", "seniority").items():
        a = [r["age_days"] for r in rows]
        rb.append({
            "country": c, "role_group": g, "role_family": f, "seniority": s,
            "n_postings": len(rows), "avg_age_days": avg(a),
            "median_age_days": median(a),
            "pct_over_7d": pct(rows, lambda r: r["age_days"] > 7),
            "pct_over_30d": pct(rows, lambda r: r["age_days"] > 30),
            "pct_over_60d": pct(rows, lambda r: r["age_days"] > 60),
            "pct_over_90d": pct(rows, lambda r: r["age_days"] > 90),
            "pct_english": pct(rows, lambda r: r["language"] == "en")})
    out["role_breakdown"] = sorted(rb, key=lambda x: -x["n_postings"])[:200]

    cb = []
    for (c,), rows in group(P, "country").items():
        a = [r["age_days"] for r in rows]
        cb.append({
            "country": c, "n_postings": len(rows),
            "employers": len({r["company"] for r in rows}),
            "avg_age_days": avg(a), "median_age_days": median(a),
            "pct_over_30d": pct(rows, lambda r: r["age_days"] > 30),
            "pct_over_60d": pct(rows, lambda r: r["age_days"] > 60),
            "pct_over_90d": pct(rows, lambda r: r["age_days"] > 90),
            "pct_english": pct(rows, lambda r: r["language"] == "en"),
            # only over rows whose salary field is known
            "pct_with_salary": pct(
                [r for r in rows if r.get("salary_known", True)],
                lambda r: r["salary_min"] is not None),
            "pct_agency": pct(rows, lambda r: r["is_agency"])})
    out["country_breakdown"] = sorted(cb, key=lambda x: -x["n_postings"])

    def city_stats(rows):
        return {"n_postings": len(rows),
                "avg_age_days": avg(r["age_days"] for r in rows),
                "pct_english": pct(rows, lambda r: r["language"] == "en"),
                "pct_agency": pct(rows, lambda r: r["is_agency"])}

    out["city_breakdown"] = sorted(
        [{"country": c, "city": ci, **city_stats(rows)}
         for (c, ci), rows in group(P, "country", "city").items()],
        key=lambda x: -x["n_postings"])
    out["city_role_breakdown"] = sorted(
        [{"country": c, "city": ci, "role_family": f, **city_stats(rows)}
         for (c, ci, f), rows in group(P, "country", "city", "role_family").items()],
        key=lambda x: -x["n_postings"])

    # skills: one row per (posting, skill)
    PS = [{**r, "skill": s} for r in P for s in r["skills"]]

    sd = []
    for (s,), rows in group(PS, "skill").items():
        sd.append({"skill": s, "skill_category": CATEGORY.get(s, "other"),
                   "n_postings": len(rows),
                   "pct_postings": r1(100 * len(rows) / n_all),
                   "avg_age_days": avg(r["age_days"] for r in rows),
                   "snapshot_date": T})
    out["skill_demand"] = sorted(sd, key=lambda x: -x["n_postings"])[:60]

    fam_n = {f: len(rows) for (f,), rows in group(P, "role_family").items()}
    sbr = []
    for (f, s), rows in group(PS, "role_family", "skill").items():
        if fam_n[f] >= FAMILY_MIN and len(rows) >= SKILL_MIN:
            sbr.append({"role_family": f, "skill": s,
                        "skill_category": CATEGORY.get(s, "other"),
                        "n_postings": len(rows), "role_postings": fam_n[f],
                        "pct_role_postings": r1(100 * len(rows) / fam_n[f]),
                        "avg_age_days": avg(r["age_days"] for r in rows),
                        "snapshot_date": T})
    out["skill_by_role"] = sorted(
        sbr, key=lambda x: (x["role_family"], -x["n_postings"]))

    # The regulatory group gets the per-family spotlight.
    RA = [r for r in P if r["role_group"] == "regulatory"]
    ab = []
    for (f,), rows in group(RA, "role_family").items():
        a = [r["age_days"] for r in rows]
        ab.append({
            "role_family": f, "n_postings": len(rows),
            "pct_of_ra": r1(100 * len(rows) / len(RA)),
            "pct_of_market": r1(100 * len(rows) / n_all),
            "employers": len({r["company"] for r in rows}),
            "avg_age_days": avg(a), "median_age_days": median(a),
            "pct_over_60d": pct(rows, lambda r: r["age_days"] > 60),
            "pct_junior": pct(rows, lambda r: r["seniority"] == "junior"),
            "pct_english": pct(rows, lambda r: r["language"] == "en"),
            "pct_agency": pct(rows, lambda r: r["is_agency"]),
            "snapshot_date": T})
    out["ra_breakdown"] = sorted(ab, key=lambda x: -x["n_postings"])[:20]

    # family size counts regulatory postings with at least one skill
    ra_ps = [r for r in PS if r["role_group"] == "regulatory"]
    ra_fam = {f: len({r["posting_id"] for r in rows})
              for (f,), rows in group(ra_ps, "role_family").items()}
    asf = []
    for (f, s), rows in group(ra_ps, "role_family", "skill").items():
        if ra_fam[f] >= FAMILY_MIN and len(rows) >= SKILL_MIN:
            asf.append({"role_family": f, "skill": s,
                        "skill_category": CATEGORY.get(s, "other"),
                        "n_postings": len(rows),
                        "pct_of_family": r1(100 * len(rows) / ra_fam[f]),
                        "snapshot_date": T})
    out["ra_skill_by_family"] = sorted(
        asf, key=lambda x: (x["role_family"], -x["n_postings"]))

    pub = [r for r in P if r["url"]]
    pub.sort(key=lambda r: (r["created_date"], r["posting_id"]), reverse=True)
    out["postings"] = [{
        "posting_id": r["posting_id"], "title": r["title"],
        "company": r["company"], "city": r["city"], "country": r["country"],
        "role_group": r["role_group"], "role_family": r["role_family"],
        "seniority": r["seniority"], "language": r["language"],
        "is_agency": r["is_agency"], "age_days": r["age_days"],
        "created_date": iso(r["created_date"]), "url": r["url"],
        "skills": r["skills"], "snapshot_date": T} for r in pub]
    return out


def history(old, g, P, today):
    T = iso(today)
    rows = [h for h in old if not h["snapshot_date"].startswith(today.isoformat())]
    ms = g["market_summary"][0]

    def add(metric, dim, val):
        rows.append({"snapshot_date": T, "metric": metric,
                     "dimension": dim, "value": float(val)})

    add("live_postings", "all", ms["live_postings"])
    add("avg_age_days", "all", ms["avg_age_days"])
    add("pct_over_60d", "all", ms["pct_over_60d"])
    for s in g["skill_demand"]:
        add("skill_pct", s["skill"], s["pct_postings"])
    for (f,), rs in sorted(group(P, "role_family").items()):
        add("role_count", f, len(rs))
        add("role_avg_age_days", f, avg(r["age_days"] for r in rs))
    for a in g["ra_breakdown"]:
        add("ra_family_pct", a["role_family"], a["pct_of_ra"])
    add("ra_share_of_market", "all",
        r1(sum(a["pct_of_market"] for a in g["ra_breakdown"])))
    return rows


# --------------------------------------------------------------------------
# 4. registry -> new_postings_daily
# --------------------------------------------------------------------------

REG_FIELDS = ["posting_id", "created_date", "country", "role_family",
              "seniority", "first_seen"]


def update_registry(P, today):
    """Insert-only list of every posting ever seen. new_postings_daily is
    rebuilt from it (plus an optional frozen seed of older counts)."""
    STATE.mkdir(exist_ok=True)
    reg_path = STATE / "registry.tsv"
    seen = set()
    if reg_path.exists():
        for line in reg_path.read_text().splitlines()[1:]:
            seen.add(line.split("\t", 1)[0])
    new = [r for r in P if r["posting_id"] not in seen]
    with reg_path.open("a") as f:
        if not seen:
            f.write("\t".join(REG_FIELDS) + "\n")
        for r in new:
            f.write("\t".join([r["posting_id"], r["created_date"].isoformat(),
                               r["country"], r["role_family"], r["seniority"],
                               today.isoformat()]) + "\n")
    print(f"registry: {len(new):,} new postings")

    counts = defaultdict(int)
    seed = STATE / "new_postings_seed.json"
    if seed.exists():
        for s in json.loads(seed.read_text()):
            counts[(s["created_date"], s["country"], s["role_family"],
                    s["seniority"])] += s["n"]
    for line in reg_path.read_text().splitlines()[1:]:
        pid, cd, c, f, s, first = line.split("\t")
        if first == "seed":
            continue
        counts[(iso(dt.date.fromisoformat(cd)), c, f, s)] += 1
    return [{"created_date": k[0], "country": k[1], "role_family": k[2],
             "seniority": k[3], "n": n} for k, n in sorted(counts.items())]


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------

def write(name, obj, compact=False):
    body = json.dumps(obj, ensure_ascii=False,
                      indent=None if compact else 1,
                      separators=(",", ":") if compact else None)
    (OUT / f"{name}.json").write_text(body)
    print(f"  wrote {name}.json ({len(body) / 1024:.1f} KB)")


def from_public(r, today):
    """A published postings.json row -> the internal record gold() uses."""
    cd = dt.date.fromisoformat(r["created_date"][:10])
    return {
        "posting_id": r["posting_id"], "title": r["title"],
        "company": r["company"], "city": r["city"], "country": r["country"],
        "role_family": r["role_family"], "role_group": r["role_group"],
        "seniority": r["seniority"], "language": r["language"],
        "is_agency": r["is_agency"], "created": r["created_date"],
        "created_date": cd, "age_days": (today - cd).days,
        # not in the public file: salary is unknown, not absent
        "salary_min": None, "salary_max": None, "desc_truncated": None,
        "salary_known": False,
        "url": r["url"], "skills": r.get("skills") or [],
    }


def to_public(r):
    return {**{k: r[k] for k in (
        "posting_id", "title", "company", "city", "country", "role_group",
        "role_family", "seniority", "language", "is_agency", "url",
        "skills", "salary_min", "salary_max", "desc_truncated")},
        "created_date": iso(r["created_date"])}


def snapshot_rows(args, today):
    """Fresh postings when there is a call budget, else the last stored
    snapshot with ages moved forward to today."""
    path = STATE / "postings_snapshot.json"
    budget = int(os.environ.get("CALL_BUDGET", 25))
    calls, n_quar, fetched = 0, 0, None

    if args.raw_dir or budget > 0:
        if args.raw_dir:
            raw = load_raw_dir(args.raw_dir)
        else:
            app_id = os.environ.get("ADZUNA_APP_ID")
            app_key = os.environ.get("ADZUNA_APP_KEY")
            if not app_id or not app_key:
                sys.exit("ADZUNA_APP_ID and ADZUNA_APP_KEY must be set "
                         "when CALL_BUDGET > 0")
            f = Fetcher(app_id, app_key, budget,
                        args.cache_dir / today.isoformat())
            raw = fetch_all(f)
            calls = f.calls
        rows, n_quar = silver(raw, today)
        assert len(rows) >= args.min_postings, \
            f"only {len(rows)} postings, keeping the previous snapshot"
        STATE.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({
            "fetched": today.isoformat(), "api_calls": calls,
            "quarantined": n_quar,
            "postings": [to_public(r) for r in rows]},
            ensure_ascii=False, separators=(",", ":")))
        fetched = today.isoformat()
        print(f"snapshot refreshed: {len(rows):,} postings")
    elif path.exists():
        snap = json.loads(path.read_text())
        rows = []
        for r in snap["postings"]:
            x = from_public(r, today)
            x.update(salary_known=True,
                     salary_min=r.get("salary_min"),
                     salary_max=r.get("salary_max"),
                     desc_truncated=r.get("desc_truncated"))
            rows.append(x)
        rows = [r for r in rows if r["age_days"] <= MAX_AGE_DAYS]
        fetched, n_quar = snap["fetched"], snap.get("quarantined", 0)
        print(f"snapshot reused from {fetched}: {len(rows):,} postings")
    else:
        sys.exit("no snapshot yet; run with CALL_BUDGET > 0 to create one")
    return rows, fetched, calls, n_quar


def main():
    global OUT, STATE
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw-dir", type=pathlib.Path,
                    help="replay cached API responses instead of calling")
    ap.add_argument("--cache-dir", type=pathlib.Path,
                    default=ROOT / ".cache" / "raw",
                    help="where live responses are saved")
    ap.add_argument("--min-postings", type=int,
                    default=int(os.environ.get("MIN_POSTINGS", 150)))
    ap.add_argument("--out-dir", type=pathlib.Path, default=OUT)
    ap.add_argument("--state-dir", type=pathlib.Path, default=STATE)
    ap.add_argument("--today", type=dt.date.fromisoformat,
                    default=dt.datetime.now(dt.timezone.utc).date())
    args = ap.parse_args()
    today = args.today
    OUT, STATE = args.out_dir, args.state_dir

    rows, fetched, calls, n_quar = snapshot_rows(args, today)
    # A reused snapshot is not reclassified, so the scope rules are
    # applied again here: in-scope families only, no senior titles.
    P = [r for r in rows if 0 <= r["age_days"] <= MAX_AGE_DAYS
         and r["role_family"] in C.KEEP and r["seniority"] != "senior"]

    # validation gate: never overwrite the site with a broken run
    n = len(P)
    assert n >= args.min_postings, f"only {n} postings, refusing to publish"
    assert all(r["role_family"] in C.KEEP for r in P)

    g = gold(P, today)
    assert len(g["postings"]) >= args.min_postings, "too few linkable postings"

    OUT.mkdir(parents=True, exist_ok=True)
    hist_path = OUT / "history.json"
    old = json.loads(hist_path.read_text()) if hist_path.exists() else []
    g["history"] = history(old, g, P, today)
    g["new_postings_daily"] = update_registry(P, today)

    for name, obj in g.items():
        write(name, obj, compact=(name == "postings"))

    ms = g["market_summary"][0]
    trunc = [r["desc_truncated"] for r in P if r["desc_truncated"] is not None]
    write("meta", {
        "updated": today.isoformat(),
        "live_postings": ms["live_postings"],
        "employers": ms["employers"],
        "avg_age_days": ms["avg_age_days"],
        "median_age_days": float(ms["median_age_days"]),
        "pct_over_60d": ms["pct_over_60d"],
        "quarantined": n_quar,
        "quarantine_rate": round(n_quar / max(len(rows) + n_quar, 1), 4),
        "postings_published": len(g["postings"]),
        "desc_truncated_pct": r1(100 * sum(trunc) / len(trunc)) if trunc else None,
        "api_calls": calls,
        "countries": sorted({r["country"] for r in P}),
        "snapshot_updated": fetched,
        "role_groups": {grp: sum(1 for r in P if r["role_group"] == grp)
                        for grp in ("regulatory", "medtech", "digital health")},
    })


if __name__ == "__main__":
    main()
