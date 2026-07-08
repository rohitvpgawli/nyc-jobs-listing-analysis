# PRD — NYC AI Startup Hiring Signal Atlas

Status: planned for 2026-W28
Owner: Rohit + Lyra
Primary goal: career-positioning public data artifact
Working title: **What early-stage AI startups in NYC are actually hiring for**
Target outputs: portfolio-quality visualization, GitHub repo/notebook, LinkedIn/X post, optional `/r/dataisbeautiful` submission if the visual is strong enough.

## 1. Executive summary

Build a data-focused public artifact that analyzes hiring demand across early-stage AI companies in New York City, with special attention to roles adjacent to Rohit's target path: Head of Data, Head of AI, analytics engineering, AI product, data infrastructure, GTM analytics, and operator-style leadership.

The artifact should answer one useful question:

> Are NYC AI startups hiring for real data/AI operating systems — or mostly for generic engineering/GTM labels?

The point is not to create a perfect labor-market dataset. The point is to create a rigorous, transparent, reproducible analysis that demonstrates Rohit's ability to:

- source messy public data,
- normalize companies/roles/stages/locations,
- extract signal from job descriptions,
- classify operating needs,
- visualize a non-obvious pattern,
- and explain what founders, operators, and data/AI leaders should take from it.

This should function as a public proof artifact for Head of Data / Head of AI roles at early-stage companies.

## 2. Why this matters

Rohit's career goal is not generic data-influencer content. It is to become visibly credible as a data systems operator for AI-native companies.

This project creates a bridge between:

- career targeting,
- startup ecosystem research,
- data analysis craft,
- public proof,
- and weekly execution.

If done well, the output can be reused as:

- LinkedIn post,
- X thread,
- portfolio case study,
- GitHub repo,
- job-search sourcing database,
- outreach opener to founders / hiring managers,
- and possibly a `/r/dataisbeautiful` visual.

## 3. Primary research questions

### Main question

What are early-stage AI startups in NYC actually hiring for right now?

### Sub-questions

1. Which role families dominate open hiring?
   - AI/ML engineering
   - data engineering
   - analytics engineering / BI
   - product engineering
   - forward-deployed / solutions / customer engineering
   - GTM / sales / customer success
   - product management
   - design / ops / other

2. Where do data/AI leadership roles appear?
   - Head of Data
   - Head of AI
   - Data Lead
   - AI Lead
   - Founding Data Engineer
   - Founding AI Engineer
   - Analytics Lead
   - Data Platform Lead

3. What operating problems do job descriptions reveal?
   - data infrastructure
   - evaluation / observability
   - agents / workflow automation
   - model deployment
   - customer-facing implementation
   - GTM analytics
   - semantic layer / metrics governance
   - regulatory/compliance workflows
   - product analytics

4. How do hiring patterns differ by company stage or source?
   - YC companies vs non-YC
   - seed vs Series A/B when stage can be inferred
   - NYC-local vs remote-friendly NYC roles

5. Are AI startups hiring for “AI” as a product surface, or for the operational plumbing underneath?

## 4. Target audience

### Primary

Founders, hiring managers, and operators at early-stage AI startups who care about data/AI infrastructure and operating leverage.

### Secondary

- data leaders,
- AI product builders,
- startup job seekers,
- analytics engineers,
- data platform engineers,
- and technically curious readers on Reddit.

## 5. Success criteria

### Minimum success

- A clean dataset of at least 75–150 relevant public job postings or company-role records.
- One strong visualization with a clear takeaway.
- One public post draft explaining the result.
- A GitHub repo or notebook that documents the methodology.

### Strong success

- 200+ role records across multiple sources.
- Role taxonomy is defensible and reproducible.
- Analysis surfaces a non-obvious pattern, e.g. “AI startups say agents, but hire forward-deployed engineers and data infra operators.”
- Output can credibly be shared with founders/hiring managers.

### Excellent success

- Portfolio page + GitHub repo + polished chart.
- LinkedIn post earns useful discussion from operators/founders.
- Artifact helps identify 3–5 roles/companies for applications/outreach.
- Visual is clean enough for `/r/dataisbeautiful` with OC/source/tooling disclosure.

## 6. Non-goals

- Do not scrape aggressively or violate site terms.
- Do not pretend the sample is the entire market.
- Do not overfit into a fake “AI job market report.”
- Do not collect personal contact data.
- Do not publish private outreach details.
- Do not turn this into a month-long research sink.
- Do not optimize for Reddit virality at the cost of career relevance.

## 7. Scope and timeframe

This is a one-week artifact with thesis-grade framing but startup-grade execution.

### Time box

- Monday: source discovery + schema + first data pull
- Tuesday 8pm work block: dataset assembly + taxonomy draft
- Wednesday: classification + cleaning
- Thursday: analysis + first charts
- Friday: polish visual + write narrative
- Saturday: QA, methodology, Reddit/LinkedIn packaging
- Sunday review: decide publish / revise / park

### Expected effort

6–10 focused hours total.

## 8. Data sources

Use public, low-friction sources first. Prefer APIs, CSVs, and pages that are stable enough to cite.

### 8.1 Primary job/company sources

#### Y Combinator company/jobs pages

Useful because YC exposes company categories, location, hiring status, and job listings.

Candidate pages:

- `https://www.ycombinator.com/companies/industry/ai/new-york/hiring`
- `https://www.ycombinator.com/jobs/location/new-york`
- `https://www.ycombinator.com/jobs/`
- `https://www.workatastartup.com/`

Use cases:

- identify AI companies in NYC,
- collect open role titles,
- infer stage/batch,
- classify role families,
- create a clean initial sample.

Caveat: page structure may change; use respectful manual export/browser-assisted extraction if API is unavailable.

#### Wellfound

Candidate source:

- `https://wellfound.com/location/new-york`
- `https://wellfound.com/jobs`

Use cases:

- startup jobs by location,
- early-stage company role titles,
- broader than YC sample.

Caveat: dynamic pages and anti-scraping constraints may make browser/manual sampling better than automation.

#### Built In NYC

Candidate source:

- `https://www.builtinnyc.com/jobs`

Use cases:

- NYC tech/startup job postings,
- structured filters for AI/data/software/product roles,
- company names + role titles.

Caveat: may overrepresent later-stage companies and general tech roles.

#### Company career pages

Use after generating a company list.

Sources:

- YC company profile → company website/careers page
- company LinkedIn jobs page manually checked
- Ashby/Greenhouse/Lever-hosted boards

Use cases:

- richer job descriptions,
- more reliable role text,
- exact location/remote policy.

Caveat: slower, but better for quality.

### 8.2 Funding/stage/context sources

#### YC metadata

Fields:

- batch,
- industry,
- company location,
- team size if visible,
- hiring status.

Stage proxy: YC batch/year and public funding if available.

#### Crunchbase / PitchBook / Harmonic / Dealroom alternatives

Use only if accessible without paywall or via public snippets. Do not depend on paid access.

Fields to consider when available:

- funding round,
- last funding date,
- investor names,
- employee range,
- headquarters.

#### SEC EDGAR / press releases / company websites

Useful for later-stage or funding-confirmed companies, but likely too heavy for v1.

### 8.3 Enrichment sources

#### LinkedIn company pages/jobs

Use manually for validation and outreach targeting. Avoid scraping personal data.

#### GitHub orgs

Optional: presence of public repos, developer tooling signals.

#### Company blogs

Optional: product claims and language around agents/data/evals/workflows.

## 9. Data model

### 9.1 Company table

`companies.csv`

Fields:

- `company_id`
- `company_name`
- `website`
- `source_primary`
- `source_url`
- `hq_city`
- `hq_state`
- `nyc_presence` — `hq_nyc`, `nyc_office`, `nyc_role_only`, `remote_us`, `unknown`
- `yc_batch`
- `industry_tags`
- `ai_category` — `core_ai`, `ai_enabled_vertical_saas`, `data_infra`, `devtools`, `health_ai`, `fintech_ai`, `other`
- `estimated_stage` — `pre_seed`, `seed`, `series_a`, `series_b`, `unknown`
- `team_size_text`
- `hiring_status`
- `notes`

### 9.2 Jobs table

`jobs.csv`

Fields:

- `job_id`
- `company_id`
- `company_name`
- `job_title`
- `job_url`
- `source`
- `location_text`
- `remote_policy` — `onsite`, `hybrid`, `remote`, `unknown`
- `nyc_relevance` — `nyc_required`, `nyc_optional`, `remote_us`, `not_nyc`, `unknown`
- `posted_date` if available
- `job_description_text`
- `seniority` — `founding`, `lead`, `head`, `senior`, `mid`, `junior`, `unknown`
- `role_family`
- `operator_need_tags`
- `ai_surface_tags`
- `data_infra_tags`
- `gtm_tags`
- `classification_confidence`
- `manual_review_flag`

### 9.3 Classification taxonomy

#### Role family

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

#### Operator need tags

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

#### AI surface tags

- `agents`
- `llm_applications`
- `computer_vision`
- `voice_audio`
- `health_ai`
- `finance_ai`
- `legal_ai`
- `devtools_ai`
- `data_ai`
- `robotics`
- `unknown`

## 10. Methodology

### 10.1 Collection process

1. Build seed list of NYC AI startups from YC company filters.
2. Expand via Built In NYC / Wellfound for additional startup jobs.
3. For each company, collect available open roles.
4. For each relevant role, save title, URL, location, and description when legally/practically accessible.
5. Keep raw source URLs and collection timestamp.
6. Avoid scraping personal data.
7. Keep a `raw/` folder locally but publish only cleaned CSV/JSON if allowed.

### 10.2 Cleaning process

- normalize company names,
- dedupe jobs by company + title + URL,
- standardize location text,
- mark NYC relevance,
- strip formatting from descriptions,
- preserve source links,
- remove personal contact names/emails if any appear.

### 10.3 Classification process

Use a hybrid approach:

1. deterministic keyword rules for first pass,
2. LLM-assisted classification for ambiguous descriptions,
3. manual spot-check sample of 20–30 records,
4. confidence score per classification.

Keyword examples:

- Data infra: `warehouse`, `pipeline`, `dbt`, `Airflow`, `Snowflake`, `Databricks`, `semantic layer`, `metrics`
- AI eval: `evaluation`, `evals`, `observability`, `benchmark`, `model quality`, `LLM monitoring`
- Agents/workflows: `agent`, `workflow`, `automation`, `tool use`, `orchestration`
- Forward-deployed: `customer`, `implementation`, `solutions`, `field`, `deployment`, `onsite`
- GTM analytics: `revenue`, `sales ops`, `growth`, `funnel`, `CRM`, `attribution`

### 10.4 Bias and limitations

- Public job postings are a sample, not the full market.
- YC-heavy data overrepresents YC-style startups.
- Job descriptions are marketing documents; they may not reflect actual internal needs.
- Location fields can be messy; hybrid/remote roles may still be NYC-relevant.
- Funding stage may be unknown or inferred.
- “AI startup” boundaries are fuzzy; document inclusion rules.

## 11. Analysis plan

### 11.1 Descriptive analysis

- Count of companies by source and category.
- Count of open roles by role family.
- Share of roles that are data/AI operating-system adjacent.
- Seniority distribution.
- NYC-required vs NYC-optional vs remote.
- YC batch/year distribution if available.

### 11.2 Signal analysis

Potential findings to test:

1. AI startups may hire more forward-deployed / solutions roles than classic data roles.
2. “Agents” may appear in product language, but job descriptions reveal infrastructure/evals/workflow needs.
3. Head of Data / Head of AI titles may be rare, but founding data/AI operator roles may be common under different labels.
4. Early-stage companies may need hybrid operators: data engineering + product analytics + AI workflow implementation.
5. NYC AI startup hiring may skew toward enterprise/fintech/health/productivity verticals.

### 11.3 Rohit-fit analysis

Create a short list of roles/companies where Rohit has a plausible angle:

- founder/operator background,
- analytics engineering/data systems,
- AI agent workflow build experience,
- product/GTM understanding,
- public proof from RohitOS/Furtribe/StarLink.

Output:

`target_roles.csv` with:

- company,
- role,
- why fit,
- outreach angle,
- proof artifact to reference,
- application status.

## 12. Visualization concepts

### Primary visual candidates

#### 1. Role-family treemap

Title:

> What NYC AI startups are hiring for right now

Design:

- each rectangle = role family,
- size = number of roles,
- color = operator-adjacent vs generic.

Pros:

- Reddit-friendly,
- instantly readable,
- good overview.

Cons:

- may be too generic unless tagged carefully.

#### 2. Company × operating-need heatmap

Rows: companies
Columns: operating needs
Cells: count or presence of job postings tagged with that need.

Pros:

- shows which startups need data/AI operating systems,
- career-positioning strong.

Cons:

- can become visually dense.

#### 3. Sankey: AI startup category → role family → operator need

Example:

`AI vertical SaaS → forward-deployed engineering → customer implementation / workflow automation`

Pros:

- visually compelling,
- shows “hidden structure” in hiring.

Cons:

- Sankeys can become spaghetti if not constrained.

#### 4. Scatter/bubble plot

X-axis: company stage/batch/year
Y-axis: share of operator-adjacent roles
Bubble size: open roles count
Color: AI category

Pros:

- good for startup ecosystem view.

Cons:

- stage data may be incomplete.

#### 5. Small multiples by source

Compare YC vs Built In vs Wellfound role-family distributions.

Pros:

- methodologically honest.

Cons:

- less punchy.

### Recommended final package

- Primary chart: **Sankey or heatmap** if data quality supports it.
- Supporting chart: **role-family bar chart / treemap**.
- Appendix: method + source coverage.

## 13. Public narrative

### LinkedIn angle

Draft thesis:

> I looked at public job postings from NYC AI startups to understand what they are actually hiring for. The interesting signal: the work is less “AI magic” and more operating-system plumbing — data infrastructure, evals, workflow automation, customer implementation, and GTM/product analytics.

Potential post structure:

1. Hook: “AI startups are not just hiring model people.”
2. Method: public job postings from YC/Built In/Wellfound/company career pages.
3. Chart: role family / operating need visualization.
4. Takeaway: the valuable operator sits between data, product, AI workflows, and customer reality.
5. Personal bridge: this is the lane I’m building in.
6. CTA: “If you’re building in this space, I’d love to compare notes.”

### Reddit angle

Title must be plain and source-aware.

Candidate:

> [OC] What early-stage AI startups in NYC are hiring for, based on public job postings

Include comment with:

- data sources,
- collection date,
- tools used,
- methodology,
- caveats,
- GitHub/source link if publishable.

Remember `/r/dataisbeautiful` expectations:

- OC label only if Rohit created the visualization,
- cite source data,
- include tool/method in comments,
- title describes data plainly,
- no sensationalized claim.

## 14. Technical implementation

### Recommended stack

- Python
- pandas
- requests / browser/manual export depending on source
- BeautifulSoup only where permitted and stable
- Jupyter notebook for exploration
- Plotly / Altair / matplotlib for charts
- Optional: Observable notebook or static HTML for final visual
- GitHub repo with README + methodology

### Repository structure

```text
nyc-ai-startup-hiring-atlas/
  README.md
  data/
    raw/              # local only or gitignored if source terms require
    interim/
    processed/
      companies.csv
      jobs.csv
      role_taxonomy.csv
      target_roles.csv
  notebooks/
    01_collect_sources.ipynb
    02_clean_classify.ipynb
    03_analysis_visuals.ipynb
  src/
    collect_yc.py
    normalize.py
    classify_roles.py
    visualize.py
  outputs/
    charts/
    report.md
  methodology.md
  requirements.txt
```

### Reproducibility rules

- Save collection timestamp.
- Save source URLs.
- Document manual steps.
- Keep classification rubric in repo.
- Do not publish scraped raw descriptions if licensing is unclear; publish derived tags/counts and source links.
- Make limitations explicit.

## 15. Quality bar

Before publishing:

- At least one chart should be understandable in 10 seconds.
- The claim must be supported by the dataset.
- The methodology must be transparent enough that a skeptical data person does not roll their eyes.
- No private data.
- No unsupported “market trend” language from a small sample.
- Visual must include source note and collection date.
- If posting to Reddit, include `[OC]`, sources, and tools.

## 16. Risks

| Risk | Impact | Mitigation |
|---|---:|---|
| Dynamic pages block extraction | Medium | Use manual exports/browser sampling; keep source links |
| Dataset too small | Medium | Narrow claim; frame as snapshot |
| Role classification too subjective | High | Use transparent taxonomy + manual review sample |
| Artifact becomes too academic | Medium | Time-box and focus on one main chart |
| Reddit rejects self-promotional framing | Medium | Make Reddit post visual/data-first; keep career story for LinkedIn |
| Poor role fit discovered | Low | Still useful sourcing intelligence |

## 17. Tuesday 8pm work block agenda

Goal: leave the session with a real dataset skeleton and first 25–50 records.

Agenda:

1. Confirm final title and inclusion rules.
2. Create repo/notebook structure.
3. Pull YC NYC AI hiring pages and inspect fields.
4. Define `companies.csv` and `jobs.csv` schema.
5. Collect first batch of companies + roles.
6. Draft role-family taxonomy in code.
7. Produce a tiny first chart, even if ugly.
8. Decide next source: Built In NYC, Wellfound, or direct company career pages.

Definition of done for Tuesday:

- repo exists locally,
- schema exists,
- at least 25 job/company records captured,
- first-pass taxonomy implemented,
- one rough visualization generated,
- next source selected.

## 18. Weekly plan

### Monday

- Finalize PRD.
- Collect source links.
- Create project repo skeleton if time permits.

### Tuesday

- 8pm work session.
- Build initial dataset and first rough chart.

### Wednesday

- Expand dataset to 75–150 records.
- Clean location/company/source fields.

### Thursday

- Role classification and manual QA.
- Produce first serious visuals.

### Friday

- Write analysis narrative.
- Refine chart aesthetics.

### Saturday

- Final QA.
- Decide if Reddit-quality.
- Draft LinkedIn/X/Reddit copy.

### Sunday review

- Score artifact commitment.
- Decide publish, revise, or continue.

## 19. Open questions

1. Should the dataset be YC-first or broader-source-first?
2. Is the artifact better framed as NYC-specific or early-stage AI startup-specific with NYC filter?
3. Should the final chart optimize for hiring-manager clarity or Reddit visual appeal?
4. What is the minimum sample size we consider credible enough to publish?
5. Do we include salary/comp if available, or avoid it to keep scope tight?

## 20. Recommended decision

Use a YC-first seed dataset, then enrich with Built In NYC and company career pages.

Build the first public artifact around this thesis:

> Early-stage AI startups in NYC are hiring less for abstract “AI strategy” and more for people who can operationalize AI: data pipelines, evals, customer workflows, product analytics, and forward-deployed implementation.

That is career-positioning first, with enough visual structure to be Reddit-interesting if the dataset holds.
