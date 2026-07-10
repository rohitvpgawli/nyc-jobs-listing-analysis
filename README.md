# NYC AI Startup Hiring Signal Atlas

**The Hiring Signal** is an open-source data artifact that answers one question:

> What are early-stage AI startups in NYC actually hiring for?

It combines a reproducible Python pipeline, a React/D3 scrollytelling site, and shareable charts — all built from public job postings with source URLs preserved.

![The Hiring Signal social card](site/public/og-card.png)

**Collection date:** July 8, 2026 · **Sample:** 522 roles · 151 YC-backed AI startups with NYC location metadata

---

## Headline finding

The work is less "AI strategy" and more operating-system plumbing: product engineering, GTM, forward-deployed implementation, evals, infrastructure, reporting, and customer workflows.

| Role family | Count |
|-------------|------:|
| Product engineering | 183 |
| GTM / sales / customer success | 161 |
| Forward-deployed / solutions | 49 |
| AI / ML engineering | 22 |
| Data engineering | 4 |
| Analytics / BI | 2 |

Other signals from the sample:

- **40%** of postings mention agents, copilots, or autonomy — descriptions underneath point to infra, implementation, evals, and reporting.
- **Zero** postings match narrow Head of Data / Head of AI / Data Platform Lead / Analytics Lead title patterns.
- **6** postings match Founding AI / ML title patterns.

![Role-family chart for social sharing](outputs/charts/reddit-role-family-card.png)

This is a **YC-heavy snapshot**, not a census of the NYC AI labor market. Full inclusion rules and caveats: [`methodology.md`](methodology.md).

---

## How it was built

Eight phases from research question to published artifact.

### Phase 1 — Research question and scope

Core question (above). Sub-questions:

- Which role families dominate?
- Where do data/AI leadership roles appear?
- What operating problems do job descriptions reveal?
- How do patterns differ by company category and stage?
- Are companies hiring for AI product surface, or the plumbing underneath?

**Scope:** YC-first seed list enriched through public job boards. NYC filter at the company level via public location metadata. No LinkedIn scraping, no paywalled labor-market datasets.

### Phase 2 — Company collection

**Script:** `pipeline/collect_yc.py`

1. Pull the public YC hiring dataset ([yc-oss API](https://github.com/yc-oss/api) → `companies/hiring.json`).
2. Filter with explicit rules: `isHiring = true`, New York in `all_locations`, AI-related tags/industries/one-liner.
3. Map to structured schema: batch, team size, AI category, stage proxy, NYC presence (`hq_nyc` vs `nyc_office`).
4. Write `data/processed/companies.csv` (raw API response stays local / gitignored).

**Result:** 152 companies matched inclusion rules.

### Phase 3 — Job collection

**Script:** `pipeline/collect_jobs.py`

For each company slug:

1. Fetch the [Work at a Startup](https://www.workatastartup.com) company page; parse embedded Inertia.js JSON for role listings.
2. Fetch each job detail page for title, location, compensation when listed, and description text.
3. Cache per-company raw JSON locally (gitignored).
4. Greenhouse / Lever / Ashby fallbacks are implemented — this run got **522/522** roles from Work at a Startup.

**Behavior:** polite requests (~0.6s delay), ~9–10 minutes across 152 companies, 529 raw roles → **522** after deduplication.

### Phase 4 — Cleaning and deduplication

**Script:** `pipeline/classify.py`

1. Dedupe by `company_id + normalized job title` (not URL alone — some titles repeat across locations).
2. Normalize location into `remote_policy` and `nyc_relevance`.
3. Strip emails from descriptions if present.
4. Preserve every `job_url` and `source` for auditability.

### Phase 5 — Classification

**Scripts:** `pipeline/taxonomy.py` + `pipeline/classify.py`

Hybrid, auditable classifier:

1. **Title rules** → `role_family`, `seniority` (deterministic regex, published in repo).
2. **Description keyword rules** → `operator_need_tags`, `ai_surface_tags`.
3. **Confidence score** per record.
4. **Manual review** for ambiguous records → `pipeline/manual_overrides.json` (29 overrides, each with a note).
5. **Optional LLM pass** (GLM 5.2 via Z.ai) for low-confidence records — wired via `.env`, unused on the published run.

| Method | Count |
|--------|------:|
| Keyword rules | 493 |
| Manual review | 29 |
| LLM-assisted | 0 |

Average confidence: **0.90** (509 high · 13 mid · 0 low).

### Phase 6 — Atlas build

**Script:** `pipeline/build_atlas.py`

Join companies + classified jobs into:

- `data/processed/jobs.csv` — public dataset (no full JD text)
- `data/processed/target_roles.csv` — operator-adjacent shortlist
- `data/processed/atlas.json` — single payload for the interactive site
- `outputs/summary.json` — headline stats

### Phase 7 — Interactive site

**Directory:** `site/`

React + D3 scrollytelling artifact:

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
- `methodology.md`, MIT license, GitHub Pages deploy workflow

---

## What ships

| Path | Description |
|------|-------------|
| `pipeline/` | Collection, cleaning, classification, atlas build, share-card export |
| `data/processed/companies.csv` | Company-level metadata |
| `data/processed/jobs.csv` | Deduped roles with classifications and source URLs |
| `data/processed/atlas.json` | Site-ready payload |
| `data/processed/target_roles.csv` | Operator-adjacent shortlist |
| `site/` | Vite + React + D3 scrollytelling site |
| `outputs/summary.json` | Headline stats |
| `outputs/charts/` | Share-card PNGs |
| `methodology.md` | Inclusion rules, taxonomy, caveats, reproducibility |

Raw job-description text and raw source responses are gitignored. The public repo ships derived labels, counts, titles, and source URLs only.

---

## Reproduce the pipeline

```bash
python3 -m pip install -r requirements.txt

python3 pipeline/collect_yc.py
python3 pipeline/collect_jobs.py
python3 pipeline/classify.py
python3 pipeline/build_atlas.py
python3 pipeline/export_share_cards.py
```

Optional LLM classification (GLM 5.2 via Z.ai):

```bash
cp .env.example .env
# Edit .env and set ZAI_API_KEY=your-key-here
python3 pipeline/classify.py
```

The pipeline loads `.env` from the repo root. It accepts `ZAI_API_KEY`, `GLM_API_KEY`, or `OPENAI_API_KEY` (default model: `glm-5.2`, base URL: `https://api.z.ai/api/paas/v4`).

Without an API key, the pipeline runs on deterministic keyword rules plus manual overrides in `pipeline/manual_overrides.json`.

## Run the site

```bash
cd site
npm install
npm run dev
```

Production build:

```bash
cd site
npm run build
```

`npm run dev` and `npm run build` copy `data/processed/atlas.json` into `site/src/data/atlas.json` automatically.

---

## Data dictionary

**Company fields:** `company_id`, `company_name`, `slug`, `website`, `source_url`, `nyc_presence`, `yc_batch`, `batch_year`, `industry_tags`, `ai_category`, `estimated_stage`, `team_size_text`, `hiring_status`

**Job fields:** `job_id`, `company_id`, `company_name`, `job_title`, `job_url`, `source`, `location_text`, `remote_policy`, `nyc_relevance`, `seniority`, `role_family`, `operator_need_tags`, `ai_surface_tags`, `leadership_flag`, `operator_adjacent`, `classification_method`, `classification_confidence`, `manual_review_flag`

---

## License

MIT. See [`LICENSE`](LICENSE).
