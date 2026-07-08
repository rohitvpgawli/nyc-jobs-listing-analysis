# Methodology

This project is a transparent snapshot of public hiring signals from NYC-relevant AI startups. It is not a labor-market census.

## Research Question

Are NYC AI startups hiring for real data/AI operating systems, or mostly for generic engineering and GTM labels?

The analysis treats job postings as operating signals: imperfect, public artifacts that reveal what a company thinks it needs badly enough to hire for.

## Sources

Collection date: `2026-07-08`.

Primary sources:

- YC company metadata from the community-maintained `yc-oss` API: `https://yc-oss.github.io/api/companies/hiring.json`
- Public YC Work at a Startup company pages: `https://www.workatastartup.com/companies/{slug}`
- Public Work at a Startup job pages: `https://www.workatastartup.com/jobs/{id}`

Fallback collectors for Greenhouse, Lever, and Ashby public board APIs are implemented in `pipeline/collect_jobs.py`, but this run found enough job detail coverage directly through Work at a Startup.

## Inclusion Rules

A company enters the sample if:

1. It appears in the public YC hiring dataset.
2. It is marked as currently hiring.
3. Its location metadata includes New York.
4. Its tags, industry metadata, subindustry, or one-liner match the AI inclusion pattern in `pipeline/collect_yc.py`.

A job enters the sample if:

1. It appears on the company's Work at a Startup page or supported public ATS board.
2. It has a title and source URL.
3. It is not a duplicate by `company_id + normalized_title`.

This produced:

- `151` companies with at least one collected posting.
- `522` deduplicated open roles.
- `525` raw postings with substantive description text before deduplication.
- `482` raw postings with salary range text before deduplication.

## Classification

The classifier is intentionally auditable. The taxonomy and keyword rules live in `pipeline/taxonomy.py`.

Role-family classification:

- `ai_ml_engineering`
- `data_engineering`
- `analytics_engineering_bi`
- `data_science_research`
- `product_engineering`
- `forward_deployed_solutions`
- `product_management`
- `gtm_sales_cs`
- `founder_operator_generalist`
- `design`
- `ops_finance_people`
- `other`

Operator-need tags:

- `data_pipeline`
- `warehouse_semantic_layer`
- `metrics_governance`
- `product_analytics`
- `model_eval_observability`
- `agent_workflows`
- `customer_implementation`
- `workflow_automation`
- `gtm_analytics`
- `security_compliance`
- `infra_platform`
- `internal_tools`
- `reporting_bi`

Process:

1. Title rules classify role family and seniority.
2. Description keyword rules classify operator-need tags and AI-surface tags.
3. Low-confidence records are marked for review.
4. Manual review overrides for ambiguous records are stored in `pipeline/manual_overrides.json`.
5. An OpenAI-compatible LLM pass is implemented in `pipeline/classify.py`. Set `ZAI_API_KEY` (or `GLM_API_KEY`) in a repo-root `.env` file to classify ambiguous records with GLM 5.2 via Z.ai. This published run is fully reproducible with keyword rules plus checked manual overrides even without an API key.

Manual QA:

- `29` low-confidence records were manually reviewed and overridden.
- After overrides, `0` records remain with `manual_review_flag = 1`.
- Full job-description text is retained only in local files ending with `.local.csv`; the public CSV publishes derived labels, counts, titles, and source URLs.

## Key Derived Concepts

Operator-adjacent role families are:

- `ai_ml_engineering`
- `data_engineering`
- `analytics_engineering_bi`
- `data_science_research`
- `forward_deployed_solutions`

These are the role families most directly adjacent to the PRD's Head of Data / Head of AI / data systems operator lane.

Leadership title flags are regex-based and intentionally narrow:

- Head of Data
- Head of AI / ML
- Data Platform Lead
- Analytics Lead
- Founding Data
- Founding AI / ML

The leadership analysis should be read as a title-pattern signal, not as a claim that no company needs leadership work.

## Limitations

- YC-heavy data overrepresents YC-backed startups and underrepresents the broader NYC AI ecosystem.
- Public postings are marketing documents; they may not reflect actual internal priorities.
- Location metadata is messy. Remote roles can still be NYC-relevant, and NYC-tagged companies can hire elsewhere.
- Keyword rules can over-tag broad descriptions when company boilerplate mentions many concepts.
- AI-startup boundaries are fuzzy. The inclusion rule is transparent, but reasonable people could draw a different boundary.
- Counts are a snapshot from one collection date, not a time series.

## Reproducibility

Run the pipeline:

```bash
python3 pipeline/collect_yc.py
python3 pipeline/collect_jobs.py
python3 pipeline/classify.py
python3 pipeline/build_atlas.py
python3 pipeline/export_share_cards.py
```

Build the site:

```bash
cd site
npm install
npm run build
```

The site consumes `data/processed/atlas.json`, copied into `site/src/data/atlas.json` before Vite builds.
