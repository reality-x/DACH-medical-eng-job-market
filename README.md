<div align="center">

# What's up with the Regulatory Affairs, MedTech and Digital Health job market in Germany and Switzerland?

[![tests](https://img.shields.io/github/actions/workflow/status/reality-x/DACH-medical-eng-job-market/tests.yml?branch=main&label=tests&labelColor=221F1A&color=6FA37F&style=flat-square)](https://github.com/reality-x/DACH-medical-eng-job-market/actions/workflows/tests.yml)
[![live postings](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Freality-x%2FDACH-medical-eng-job-market%2Fmain%2Fdocs%2Fdata%2Fmeta.json&query=%24.live_postings&label=live%20postings&labelColor=221F1A&color=E3A23F&style=flat-square&cacheSeconds=1800)](https://reality-x.github.io/DACH-medical-eng-job-market/)

**[Open the live tracker](https://reality-x.github.io/DACH-medical-eng-job-market/)**

</div>

A snapshot of the DACH job market for **Regulatory Affairs managers and specialists, medical devices (Medizintechnik) and Digital Health**. A GitHub Actions pipeline queries the Adzuna API in Germany and Switzerland (Austria is left out to save API calls), classifies every posting into one of 15 roles, scans it for regulations, standards and skills (EU MDR, IVDR, ISO 13485, ISO 14971, IEC 62304, FDA, HL7/FHIR, DiGA ...) and publishes a static GitHub Page.

## How the tracker might help you

- **See the shape of the market**: volumes by role, city and country, how long postings stay open, seniority mix, which regulations and standards employers ask for.
- **Read the postings behind any number.** Every chart is a count of real postings, and those postings are browsable: search by title or employer, filter by role, country, city, seniority and skill (e.g. "ISO 13485" + "EU MDR").
- **Watch it move.** Each run adds to `history.json`, so every figure gains a time dimension.

## Scope: the 15 roles

| Group | Roles |
|---|---|
| **Regulatory Affairs** | Regulatory Affairs Manager (incl. Head/Leiter Zulassung), Regulatory Affairs Specialist (incl. PRRC), QA / RA, Clinical Affairs / PMS / Vigilance, Quality Management (MedTech) |
| **MedTech** | R&D Engineer, Software Engineer, Product Manager, Sales / Application Specialist, Service Technician, Production |
| **Digital Health** | Digital Health Engineer, Digital Health Product, Health IT / Interoperability (HL7, FHIR, KIS), Digital Health Consulting |

How a title is classified (`src/classify.py`):

- **Regulatory titles stand on their own.** "Regulatory Affairs Manager" counts whatever the employer's industry, so pharma RA jobs are included.
- **Generic titles need a domain signal.** "Servicetechniker" or "Backend Developer" only count as MedTech or Digital Health when the title or the description snippet names the domain (Medizintechnik, medical device, MDR, ISO 13485, DiGA, FHIR, eHealth ...). These groups are a floor.
- **Senior, lead and head-of titles are excluded** (Senior, Sr., Lead, Principal, Staff, Head, Director, Chief, VP, Leiter, Leitung). The tracker covers junior and mid-level roles only.
- **Excluded:** entry programmes (Ausbildung, Werkstudent, Praktikum, Trainee, theses), clinical and care staff (physicians, nurses, MTA, pharmacists, therapists), and everything else the broad keyword search pulls in.

## Architecture

```
Adzuna API              de · ch, 7 broad queries
    │                   (regulatory affairs, medical device, medizintechnik,
    │                    medizinprodukte, clinical affairs, digital health, ehealth)
    ▼
src/pipeline.py         parse → quality gate → dedupe → classify → skills
    │
    ├── state/postings_snapshot.json   last fetched postings
    ├── state/registry.tsv             every posting ever seen
    ▼
docs/data/*.json        aggregates + history, committed to this repo
    │
    ▼
GitHub Pages            static site (docs/), no backend
```

## Running it

`.github/workflows/pipeline.yml` runs in two modes:

| Trigger | Budget | What it does |
|---|---|---|
| Actions → pipeline → Run workflow | 25 calls (default) | Fetches fresh postings from Adzuna and rebuilds everything |
| Daily at 06:00 UTC | `DAILY_CALL_BUDGET` variable (default 0) | 0 = rebuilds from the stored snapshot with ages moved forward; set e.g. 25 if your Adzuna plan allows a daily refresh |

Page 1 of every query in every country is 7 × 2 = 14 calls; the rest of the budget goes to page 2. The script waits 13 s between calls to stay under 5 calls/minute (`CALL_PACE` variable). Countries can be changed with the `COUNTRIES` variable (default `de,ch`).

**Setup:** add `ADZUNA_APP_ID` and `ADZUNA_APP_KEY` (from developer.adzuna.com) under **Settings → Secrets and variables → Actions**, then run the workflow manually once. Enable GitHub Pages from the `docs/` folder.

Locally:

```bash
ADZUNA_APP_ID=... ADZUNA_APP_KEY=... CALL_BUDGET=25 python src/pipeline.py
CALL_BUDGET=0 python src/pipeline.py      # rebuild from the snapshot
pytest tests/
```

## Limitations

- **One aggregator is not the whole market**, and Adzuna's coverage differs by country. Cross-country comparisons are indicative.
- **`created` is the aggregator's date**, possibly when it indexed the posting rather than when the employer published it.
- **Descriptions are capped at ~500 characters.** Skill counts mean *mentioned in the title or opening paragraph*: a floor, not a requirement rate.
- **Multi-location jobs are counted once per city**, and there is no remote flag.
- **A posting in the browser is not necessarily open.** It was live at the last refresh.

## Licence

MIT. The underlying job data belongs to Adzuna and its source boards.

---

<p align="center">MedTech & Regulatory edition by <b>Shahriar Yazdipour</b> · <a href="https://yazdipour.com/">yazdipour.com</a> · <a href="https://github.com/yazdipour">GitHub</a></p>
<p align="center">Based on the DACH data job market tracker by <b>Christoph Ruckensteiner</b> · <a href="https://www.linkedin.com/in/cruckensteiner112">LinkedIn</a> · <a href="https://github.com/Chrisinho8">GitHub</a></p>
