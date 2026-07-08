# The Hiring Signal — Public Write-Up

**What early-stage AI startups in NYC are actually hiring for**

Author: Rohit Gawli  
Collection date: **July 8, 2026**  
Open-source repo: `https://github.com/rohitgawli/nyc-startups-hiring`  
Interactive atlas + methodology shipped in-repo

---

## Executive summary (for LinkedIn / X)

I built an open-source analysis of **522 public job postings** from **151 YC-backed, AI-tagged startups** with New York location metadata, collected on **July 8, 2026**.

The question I wanted to answer:

> Are NYC AI startups hiring for real data/AI operating systems — or mostly for generic engineering and GTM labels?

**What I found:**

- **Product engineering** and **GTM / sales / customer success** dominate: **183** and **161** roles.
- Classic data-department titles are rare in the posting taxonomy: **4** data engineering, **2** analytics/BI.
- **Forward-deployed / solutions** roles are meaningfully visible: **49** roles.
- **40%** of postings mention agents, copilots, or autonomy — but the job descriptions underneath point to infrastructure, customer implementation, evals, reporting, and workflow plumbing.
- **Zero** postings match narrow **Head of Data**, **Head of AI/ML**, **Data Platform Lead**, or **Analytics Lead** title patterns in this sample.
- **6** postings match **Founding AI / ML** title patterns.

**My read:** early-stage AI companies in this sample are not advertising many polished data-leadership titles. The operating work shows up under product engineering, founding engineering, forward-deployed implementation, and solutions roles.

This is a **YC-heavy snapshot**, not a census of the entire NYC AI labor market. Every number is reproducible from public sources with source URLs preserved.

---

## What I built (step by step)

### Phase 1 — Define the research question and scope

I started from a PRD with one core question:

> What are early-stage AI startups in NYC actually hiring for?

Sub-questions included:

- Which role families dominate?
- Where do data/AI leadership roles appear?
- What operating problems do job descriptions reveal?
- How do patterns differ by company category and stage?
- Are companies hiring for AI product surface, or the plumbing underneath?

**Scope decision:** YC-first seed list, enriched through public job boards. NYC filter applied at the company level via public location metadata. Not a scrape of LinkedIn, not a paid labor-market dataset.

### Phase 2 — Company collection (`pipeline/collect_yc.py`)

1. Pulled the public YC hiring dataset from the community-maintained API:
   - `https://yc-oss.github.io/api/companies/hiring.json`
   - Source project: `https://github.com/yc-oss/api` (daily-updated mirror of the public YC directory)

2. Filtered companies using explicit inclusion rules:
   - `isHiring = true`
   - `all_locations` contains `"new york"`
   - Tags / industries / subindustry / one-liner match an AI-related regex pattern

3. Mapped each company into a structured schema:
   - YC batch, batch year, team size, website, YC profile URL
   - AI category (core AI, fintech AI, health AI, vertical SaaS AI, devtools AI, data infra)
   - Estimated stage proxy from YC metadata (`seed` vs `series_a_plus`)
   - NYC presence (`hq_nyc` vs `nyc_office`)

4. Saved output to `data/processed/companies.csv` and raw API response to `data/raw/yc_hiring.json` (gitignored).

**Result:** **152** companies matched inclusion rules.

### Phase 3 — Job collection (`pipeline/collect_jobs.py`)

For each company slug:

1. Fetched the public Work at a Startup company page:
   - `https://www.workatastartup.com/companies/{slug}`

2. Parsed embedded JSON from the page's `data-page` attribute (server-rendered Inertia.js props) to extract role listings.

3. For each role, fetched the public job detail page:
   - `https://www.workatastartup.com/jobs/{job_id}`

4. Extracted:
   - Job title
   - Location text
   - Salary range (when listed)
   - Equity range, visa policy, min experience, skills
   - Full job description HTML → stripped to plain text

5. Cached per-company raw JSON under `data/raw/jobs/{slug}.json` (gitignored).

6. Implemented fallback collectors for public Greenhouse, Lever, and Ashby board APIs — but this run got full coverage from Work at a Startup (**522/522** roles from `workatastartup`).

**Collection behavior:**

- Polite HTTP requests with browser-like User-Agent and ~0.6s delay between requests
- Full collection run across 152 companies took ~9–10 minutes
- **529** raw role records collected
- **522** after deduplication

### Phase 4 — Cleaning and deduplication (`pipeline/classify.py`)

1. Deduplicated by `company_id + normalized job title` (not URL alone — some titles repeat across locations).
2. Normalized location text into:
   - `remote_policy`: onsite / hybrid / remote / unknown
   - `nyc_relevance`: nyc_required / nyc_optional / remote_us / not_nyc / unknown
3. Stripped emails from descriptions if any appeared.
4. Preserved every `job_url` and `source` for auditability.

### Phase 5 — Classification (`pipeline/taxonomy.py` + `pipeline/classify.py`)

**Hybrid, auditable classifier:**

1. **Title rules** assign `role_family` and `seniority` (deterministic regex, published in repo).
2. **Description keyword rules** assign `operator_need_tags` and `ai_surface_tags`.
3. **Confidence score** per record (heuristic: title-rule precision).
4. **Manual review** for ambiguous records → `pipeline/manual_overrides.json` (**29** overrides, each with a note).
5. **Optional LLM pass** (GLM 5.2 via Z.ai) for low-confidence records — implemented and available via `.env`, but the **published July 8 run** used keyword rules + manual review only.

**Published classification breakdown:**

| Method | Count |
|--------|------:|
| Keyword rules | 493 |
| Manual review override | 29 |
| LLM-assisted | 0 |

**Confidence distribution:**

| Bucket | Count |
|--------|------:|
| High (≥ 0.8) | 509 |
| Mid (0.6–0.79) | 13 |
| Low (< 0.6) | 0 |

Average confidence: **0.90**. Records flagged for manual review after publish: **0**.

### Phase 6 — Atlas build (`pipeline/build_atlas.py`)

Joined companies + classified jobs into:

- `data/processed/jobs.csv` — public dataset (no full JD text)
- `data/processed/target_roles.csv` — shortlist of operator-adjacent roles for outreach
- `data/processed/atlas.json` — single payload for the interactive site
- `outputs/summary.json` — headline stats

### Phase 7 — Interactive artifact (`site/`)

Built a scrollytelling React + D3 site with:

1. **Hook** — animated headline stats
2. **Role map** — NYC subway-line metaphor for role families
3. **Sankey** — AI category → role family → operator need
4. **Leadership gap** — departure-board view of data/AI leadership title patterns
5. **Words vs work** — agent language vs operator needs in descriptions
6. **Explorer** — filterable heatmap + searchable role table with live posting links
7. **Methodology footer** — sources, caveats, repo link

### Phase 8 — Share cards and packaging

- `pipeline/export_share_cards.py` — deterministic PNG export
- `site/public/og-card.png` — 1600×900 social/OG card
- `outputs/charts/reddit-role-family-card.png` — static chart with source annotation
- `README.md`, `methodology.md`, `outputs/report.md`, MIT license, GitHub Pages deploy workflow

---

## Data sources (complete list)

| Source | URL | What we used it for | Auth required |
|--------|-----|---------------------|---------------|
| YC OSS API (hiring companies) | `https://yc-oss.github.io/api/companies/hiring.json` | Company metadata, batch, tags, location, hiring status | No |
| YC company profiles | `https://www.ycombinator.com/companies/{slug}` | Cross-reference (via `source_url` in dataset) | No |
| Work at a Startup — company pages | `https://www.workatastartup.com/companies/{slug}` | Role listings (embedded JSON) | No |
| Work at a Startup — job pages | `https://www.workatastartup.com/jobs/{id}` | Full job descriptions, salary, location | No |
| Greenhouse public API (fallback) | `https://boards-api.greenhouse.io/v1/boards/{slug}/jobs` | Implemented, not needed this run | No |
| Lever public API (fallback) | `https://api.lever.co/v0/postings/{slug}` | Implemented, not needed this run | No |
| Ashby public API (fallback) | `https://api.ashbyhq.com/posting-api/job-board/{slug}` | Implemented, not needed this run | No |

**What we did NOT use:**

- LinkedIn scraping
- Personal contact data
- Paywalled Crunchbase / PitchBook
- Private outreach databases
- Synthetic or LLM-generated job postings

---

## Timeline

| When | What happened |
|------|---------------|
| **2026-W28 (planned)** | PRD written: NYC AI Startup Hiring Signal Atlas |
| **July 7–8, 2026** | End-to-end build: pipeline, classification, site, share cards |
| **2026-07-08 ~02:43 UTC** | Job collection started (152 companies) |
| **2026-07-08 ~02:53 UTC** | Job collection completed: 529 raw → 522 deduped roles |
| **2026-07-08** | Classification, atlas build, site build, share card export |
| **2026-07-08T03:31:16Z** | Final `atlas.json` / `summary.json` build timestamp |

This is a **single-day snapshot**. It is not a time series and does not track hiring velocity over weeks.

---

## Geographic scope and location handling

### Company-level filter

Companies entered the seed list if YC metadata listed a New York location. Of 152 seed companies:

- **151** with `hq_nyc`
- **1** with `nyc_office`

### Job-level location (522 roles)

| NYC relevance | Count | Meaning |
|---------------|------:|---------|
| NYC required | 327 | Location text mentions NYC/NY without remote |
| NYC optional | 81 | NYC + remote/hybrid in same posting |
| Remote (US) | 75 | US remote, no NYC in location text |
| Not NYC | 39 | Other city listed (SF, Barcelona, etc.) |

**Important:** A company can be NYC-headquartered but hire for non-NYC roles. **39** postings in the sample are explicitly non-NYC locations. The analysis is "NYC AI startups hiring" not "NYC-only roles exclusively."

Example location strings from the data:

- `New York, NY, US`
- `New York City / Remote (US)`
- `New York City / Barcelona`
- `San Francisco, CA, US` (non-NYC role at NYC-tagged company)

---

## Company sample composition

### AI categories (152 seed companies)

| Category | Count |
|----------|------:|
| Fintech AI | 44 |
| AI-enabled vertical SaaS | 36 |
| Core AI | 26 |
| Health AI | 23 |
| Devtools AI | 12 |
| Data infra | 10 |
| Other | 1 |

### Stage proxy

| Stage | Companies |
|-------|----------:|
| Seed (YC "Early") | 119 |
| Series A+ proxy (YC "Growth") | 33 |

### YC batch spread

- Batch years: **2013 – 2026**
- Most represented: Winter 2023 (18), Winter 2022 (15), Summer 2023 (15), Summer 2024 (14)

---

## Key findings (with numbers)

### Role families (522 roles)

| Role family | Count | % of sample |
|-------------|------:|------------:|
| Product engineering | 183 | 35.1% |
| GTM / sales / CS | 161 | 30.8% |
| Forward-deployed / solutions | 49 | 9.4% |
| Ops / finance / people | 32 | 6.1% |
| Design | 24 | 4.6% |
| AI / ML engineering | 22 | 4.2% |
| Product management | 19 | 3.6% |
| Data science / research | 13 | 2.5% |
| Founder / operator generalist | 11 | 2.1% |
| Data engineering | 4 | 0.8% |
| Analytics engineering / BI | 2 | 0.4% |
| Other | 2 | 0.4% |

**Operator-adjacent families** (AI/ML eng, data eng, analytics/BI, DS/research, forward-deployed): **90 roles = 17.2%** of sample.

### Leadership title patterns (narrow regex)

| Title pattern | Postings found |
|---------------|---------------:|
| Head of Data | 0 |
| Head of AI / ML | 0 |
| Data Platform Lead | 0 |
| Analytics Lead | 0 |
| Founding Data Engineer | 0 |
| Founding AI / ML Engineer | 6 |
| Forward-deployed / solutions (family) | 49 |
| Founding-level titles (any) | 84 |

### Agent language vs operator work

- **209 / 522 (40%)** postings tagged with AI-surface `agents`
- Inside those agent-mentioning postings, top operator-need tags (excluding circular `agent_workflows`):
  - Infra & platform
  - Customer implementation
  - Evals & observability
  - Reporting & BI
  - GTM analytics

### Top operator-need tags (all 522 roles; multi-tag per posting)

| Tag | Postings mentioning |
|-----|--------------------:|
| Agent workflows | 203 |
| Infra & platform | 199 |
| Reporting & BI | 115 |
| GTM analytics | 112 |
| Customer implementation | 105 |
| Security & compliance | 100 |
| Model evals & observability | 86 |
| Data pipelines | 67 |

*Note: postings can match multiple tags. These are mention counts, not mutually exclusive buckets.*

### Compensation coverage

- **475 / 522 (91%)** processed roles have salary range text when available from source pages.

---

## How to reproduce (proof of authenticity)

Anyone can rerun the pipeline:

```bash
git clone https://github.com/rohitgawli/nyc-startups-hiring
cd nyc-startups-hiring
python3 -m pip install -r requirements.txt

python3 pipeline/collect_yc.py
python3 pipeline/collect_jobs.py
python3 pipeline/classify.py
python3 pipeline/build_atlas.py
python3 pipeline/export_share_cards.py
```

Optional GLM 5.2 classification for ambiguous records:

```bash
cp .env.example .env
# set ZAI_API_KEY=...
python3 pipeline/classify.py
```

Every job row in `data/processed/jobs.csv` includes a `job_url` you can open in a browser. Example:

- `https://www.workatastartup.com/jobs/93481` — 222, Technical Support Lead
- `https://www.workatastartup.com/jobs/80893` — 222, iOS Engineer / Design Engineer
- `https://www.workatastartup.com/jobs/97464` — Abacum, Strategic Initiatives Lead

---

## Anticipated questions and answers (with proof)

### A. Data authenticity

**Q1: Did you make up these numbers?**  
**A:** No. **522** roles come from **529** raw public postings across **151** companies. Every row has a `job_url` pointing to Work at a Startup. Re-run `pipeline/collect_jobs.py` to reproduce.  
**Proof:** `data/processed/jobs.csv` → column `job_url`; `data/processed/jobs_raw.csv` has 529 rows.

**Q2: How do I verify a specific claim (e.g. "183 product engineering roles")?**  
**A:** Filter `data/processed/jobs.csv` where `role_family = product_engineering`. Count rows. Open any `job_url` to read the source posting.  
**Proof:** `pipeline/taxonomy.py` defines the title rules; `outputs/summary.json` mirrors the counts.

**Q3: Is this the entire NYC AI job market?**  
**A:** No. It is a **YC-heavy snapshot** of AI-tagged companies with NYC location metadata, collected on one date.  
**Proof:** Inclusion rules in `methodology.md` and `pipeline/collect_yc.py` — filter is explicit and narrow.

**Q4: Why only YC companies?**  
**A:** Scope decision for v1: YC exposes structured public metadata (batch, tags, location, hiring status) and Work at a Startup provides clean job detail pages. Broader sources (Wellfound, Built In NYC) were in the PRD as future enrichment.  
**Proof:** PRD section 8; `collect_jobs.py` has ATS fallbacks ready for non-YC boards.

**Q5: Did you scrape LinkedIn or private data?**  
**A:** No. Sources are public YC directory metadata and public Work at a Startup pages only.  
**Proof:** `methodology.md` sources section; no LinkedIn URLs in `jobs.csv`.

**Q6: When was this collected? Could the postings be stale?**  
**A:** Collection date is **2026-07-08**. This is a point-in-time snapshot. Postings may have closed since collection.  
**Proof:** `collected_at` field on every job row; `atlas.json` → `meta.collectedAt`.

**Q7: Can I see the raw data?**  
**A:** Processed CSVs and `atlas.json` are in the repo. Raw scraped responses are gitignored (`data/raw/`) due to source terms and bulk, but the pipeline regenerates them on rerun.  
**Proof:** `.gitignore`; `pipeline/collect_jobs.py` writes to `data/raw/jobs/{slug}.json`.

---

### B. Classification and interpretation

**Q8: Who decided that a role is "product engineering" vs "AI/ML engineering"?**  
**A:** Deterministic title regex rules in `pipeline/taxonomy.py`. First match wins. Rules are published and auditable.  
**Proof:** `pipeline/taxonomy.py` → `ROLE_FAMILY_TITLE_RULES`.

**Q9: Did an LLM invent the classifications?**  
**A:** On the published July 8 run: **493 keyword**, **29 manual review**, **0 LLM**. No model generated counts or invented postings. An optional GLM 5.2 pass exists for ambiguous records on re-runs.  
**Proof:** `classification_method` column in `jobs.csv`; `pipeline/classify.py`; `pipeline/manual_overrides.json`.

**Q10: What about generic titles like "Software Engineer"?**  
**A:** These often classify as `product_engineering` at ~0.6 confidence via title rules. **13** roles sit in the 0.6–0.79 confidence bucket. This is a known limitation — re-run with GLM or manual review to refine.  
**Proof:** `classification_confidence` column; keyword rules for `product_engineering`.

**Q11: How were operator-need tags assigned?**  
**A:** Keyword rules on job description text (e.g. `dbt`, `Snowflake`, `evals`, `semantic layer`, `customer implementation`). A posting can match multiple tags.  
**Proof:** `pipeline/taxonomy.py` → `OPERATOR_NEED_RULES`.

**Q12: Doesn't "agent workflows" appearing 203 times just mean you searched for the word "agent"?**  
**A:** Partially yes — it's a keyword tag, not a claim that 203 people will build agents. That's why the "Words vs work" chart excludes `agent_workflows` when analyzing agent-mentioning postings and instead shows infra, implementation, evals, etc.  
**Proof:** `site/src/sections/WordsVsWork.tsx`; tag rules in `taxonomy.py`.

**Q13: You found zero Head of Data roles — does that mean no NYC AI startup needs a Head of Data?**  
**A:** No. It means **zero postings in this sample** matched our **narrow title-pattern regex** on the collection date. Leadership need may hide under "Founding Engineer," "first data hire," or unposted executive search.  
**Proof:** `DATA_AI_LEADERSHIP_RULES` in `taxonomy.py`; leadership board in the site.

**Q14: What manual review did you actually do?**  
**A:** **29** records where keyword rules were insufficient were read and overridden with documented notes.  
**Proof:** `pipeline/manual_overrides.json` — each entry has `job_id`, `role_family`, and `note`.

**Q15: Can someone disagree with your taxonomy?**  
**A:** Yes — and they should, if they can propose a better rubric. The value is that our rubric is **published**, not hidden. Fork the repo, change `taxonomy.py`, rerun.  
**Proof:** Open-source MIT license; `methodology.md`.

---

### C. Geography and NYC relevance

**Q16: Are all 522 roles NYC jobs?**  
**A:** No. **327** are NYC-required, **81** NYC-optional (hybrid/remote), **75** remote US without NYC in text, **39** explicitly other cities.  
**Proof:** `nyc_relevance` column in `jobs.csv`; `outputs/summary.json` → `nycBreakdown`.

**Q17: Why include remote US roles from NYC-headquartered companies?**  
**A:** Because the research question is what **NYC AI startups** are hiring for, not only what requires sitting in Manhattan. Excluding remote would undercount their actual hiring intent.  
**Proof:** Company filter is NYC-metadata; job filter is inclusive with `nyc_relevance` tagging for downstream filtering.

**Q18: How do you define "NYC AI startup"?**  
**A:** Company must appear in YC hiring data with New York in `all_locations` AND match AI tag/industry regex.  
**Proof:** `is_nyc()` and `is_ai()` in `pipeline/collect_yc.py`.

---

### D. Statistical and narrative claims

**Q19: Is "66% of hiring is product eng + GTM" a market trend?**  
**A:** It is **66% of this sample on this date** (183 + 161 = 344/522). Frame as snapshot, not trend.  
**Proof:** `outputs/summary.json` roleFamilies.

**Q20: You say AI startups hire for "plumbing not magic" — isn't that editorializing?**  
**A:** The **counts** are descriptive. The **interpretation** is that operator-need tags (infra, evals, implementation, reporting) appear frequently in descriptions while classic data-department titles are rare. Reasonable readers may disagree on framing.  
**Proof:** Operator-need counts in `summary.json`; role-family counts; methodology caveats.

**Q21: Why is data engineering only 4 roles? Is NYC AI not hiring data engineers?**  
**A:** In this sample, yes — very few postings have titles matching data-engineering patterns. Data work may appear under "Founding Engineer," "Backend Engineer," or forward-deployed titles without "data" in the title.  
**Proof:** Title rules in `taxonomy.py`; 84 founding-level titles in sample.

**Q22: 40% mention agents — is AI just hype?**  
**A:** 40% of **job descriptions** in the sample match agent-related surface tags. The follow-on analysis shows those same postings often ask for infra, implementation, and evals work. Hype in language, plumbing in requirements — that's the thesis, supported by tag co-occurrence.  
**Proof:** `agentMentionShare: 0.4` in `summary.json`; Words vs Work section.

---

### E. Technical and reproducibility

**Q23: Is the code real or a demo?**  
**A:** Full pipeline, site, and deploy workflow are in the repo. Production build succeeds.  
**Proof:** `pipeline/*.py`, `site/dist/` after `npm run build`, `.github/workflows/deploy-pages.yml`.

**Q24: What if YC OSS API or Work at a Startup changes?**  
**A:** Reruns may break or shift counts. Raw responses are cached locally per run. Document collection date when publishing.  
**Proof:** `data/raw/` cache in `collect_jobs.py`; `collected_at` timestamps.

**Q25: Why gitignore raw job descriptions?**  
**A:** Licensing caution and bulk. Public repo ships derived tags + source links. Full text stays in `*.local.csv` locally.  
**Proof:** `.gitignore`; `jobs.csv` vs `jobs_with_text.local.csv` in `classify.py`.

**Q26: What's the polite scraping policy?**  
**A:** ~0.6s delay between requests, browser-like User-Agent, public pages only, no auth bypass, no personal data.  
**Proof:** `pipeline/common.py` → `REQUEST_DELAY_SECONDS`, `USER_AGENT`.

---

### F. Career positioning / conflict of interest

**Q27: Is this just a job search project dressed up as research?**  
**A:** It started as career-positioning intelligence (Head of Data / Head of AI lane) and became a public proof artifact. The shortlist `target_roles.csv` exists for personal outreach — it's separate from the public counts.  
**Proof:** `data/processed/target_roles.csv`; PRD section 11.

**Q28: Did you cherry-pick findings that make your target path look good?**  
**A:** The inclusion rules and taxonomy were fixed before analysis. The dominant finding (product eng + GTM, not Head of Data) is actually inconvenient for a "Head of Data" narrative — which is why it's interesting.  
**Proof:** PRD research questions; zero Head of Data matches; published limitations.

**Q29: Can founders trust this for hiring decisions?**  
**A:** As directional competitive intelligence, yes — with caveats. Not as a compensation benchmark or headcount plan.  
**Proof:** Limitations section in `methodology.md`.

---

### G. Comparison to other datasets

**Q30: How does this compare to LinkedIn Talent Insights or Levels.fyi?**  
**A:** Those are broader, often paid, and not reproducible by readers. This is narrower, open, and fully auditable — trade-off is sample size and YC bias.  
**Proof:** Source list; open repo.

**Q31: Why not use Wellfound or Built In NYC as primary?**  
**A:** PRD planned them as enrichment. V1 prioritized structured YC + WaaS for speed and reproducibility in a one-week artifact. ATS fallbacks are implemented for expansion.  
**Proof:** `pipeline/collect_jobs.py` → `probe_ats()`.

---

## Suggested posting formats

### LinkedIn (long)

Use the Executive Summary above + 2 charts + link to repo + explicit caveat paragraph:

> This is a YC-heavy snapshot from public postings collected July 8, 2026 — not a census of the NYC AI labor market. Full methodology and reproducible pipeline are open-source.

### X (thread)

7-tweet structure is in `outputs/report.md`.

### Reddit r/dataisbeautiful

Title: `[OC] What 151 NYC AI startups are hiring for right now, based on 522 public job postings`

Post the static chart `outputs/charts/reddit-role-family-card.png` and paste the "Reddit comment" block from `outputs/report.md` or the Reproduce + Anticipated Q&A sections above.

---

## One-paragraph authenticity statement (use anywhere)

> Every number in this analysis comes from public job postings collected on July 8, 2026 from YC-backed, AI-tagged companies with New York location metadata. I did not use private databases, LinkedIn scraping, or synthetic data. Each of the 522 roles links to a live source URL. Role families and operator tags were assigned using published keyword rules and 29 manually reviewed edge cases — not invented by a model. This is a directional snapshot of one sample on one date, not a labor-market census. The full pipeline, taxonomy, and data are open-source for anyone to audit, challenge, or rerun.
