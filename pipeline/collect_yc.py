"""Collect NYC AI startups currently hiring, from the community YC OSS API.

Source: https://github.com/yc-oss/api (public mirror of the YC directory,
updated daily, no auth). We filter to companies that:

  1. are marked as currently hiring (`isHiring`),
  2. list a New York location in `all_locations`,
  3. carry at least one AI-related tag or subindustry.

Inclusion rules are documented in methodology.md.
"""

from __future__ import annotations

import csv
import json
import re

from common import PROCESSED_DIR, now_iso, polite_get, save_raw, load_raw

HIRING_URL = "https://yc-oss.github.io/api/companies/hiring.json"

AI_TAG_PATTERN = re.compile(
    r"(artificial intelligence|\bai\b|machine learning|\bml\b|deep learning|"
    r"generative|llm|nlp|computer vision|speech)",
    re.IGNORECASE,
)

# Map YC tags/industries to the PRD's ai_category taxonomy. First match wins:
# specific verticals beat generic AI tags, which beat generic B2B/SaaS tags.
AI_CATEGORY_RULES = [
    ("health_ai", r"health|medical|bio|clinic|pharma|care"),
    ("fintech_ai", r"fintech|finance|banking|insurance|payments|trading"),
    ("devtools_ai", r"developer tools|devops|api\b|infrastructure|open.?source"),
    ("data_infra", r"data engineering|analytics|database|data\b"),
    ("ai_enabled_vertical_saas", r"legal|real estate|construction|logistics|hr\b|recruiting|education|retail|e-?commerce|manufacturing|supply chain|security"),
    ("core_ai", r"artificial intelligence|machine learning|generative|llm|agent|\bai\b"),
    ("ai_enabled_vertical_saas", r"saas|b2b|sales|marketing"),
]

# YC "stage" field -> PRD estimated_stage proxy. YC batches are a seed-stage
# proxy; the API's own stage field distinguishes Early from Growth.
STAGE_MAP = {"Early": "seed", "Growth": "series_a_plus", "Idea": "pre_seed"}


def is_nyc(company: dict) -> bool:
    return "new york" in (company.get("all_locations") or "").lower()


def is_ai(company: dict) -> bool:
    haystack = " ".join(
        (company.get("tags") or [])
        + (company.get("industries") or [])
        + [company.get("subindustry") or "", company.get("one_liner") or ""]
    )
    return bool(AI_TAG_PATTERN.search(haystack))


def ai_category(company: dict) -> str:
    haystack = " ".join(
        (company.get("tags") or []) + (company.get("industries") or []) + [company.get("subindustry") or ""]
    ).lower()
    for label, pattern in AI_CATEGORY_RULES:
        if re.search(pattern, haystack):
            return label
    return "other"


def nyc_presence(company: dict) -> str:
    locations = (company.get("all_locations") or "").lower()
    if locations.startswith("new york"):
        return "hq_nyc"
    if "new york" in locations:
        return "nyc_office"
    return "unknown"


def batch_year(batch: str) -> int | None:
    m = re.search(r"(20\d\d)", batch or "")
    return int(m.group(1)) if m else None


def collect(refresh: bool = True) -> list[dict]:
    raw = None if refresh else load_raw("yc_hiring.json")
    if raw is None:
        resp = polite_get(HIRING_URL)
        resp.raise_for_status()
        raw = resp.json()
        save_raw("yc_hiring.json", raw)

    selected = [c for c in raw if is_nyc(c) and is_ai(c)]

    companies = []
    for c in sorted(selected, key=lambda x: x["name"].lower()):
        companies.append(
            {
                "company_id": f"yc-{c['id']}",
                "company_name": c["name"],
                "slug": c["slug"],
                "website": c.get("website") or "",
                "source_primary": "yc_oss_api",
                "source_url": c.get("url") or "",
                "hq_city": "New York" if nyc_presence(c) == "hq_nyc" else "",
                "hq_state": "NY" if nyc_presence(c) == "hq_nyc" else "",
                "nyc_presence": nyc_presence(c),
                "yc_batch": c.get("batch") or "",
                "batch_year": batch_year(c.get("batch")) or "",
                "industry_tags": "|".join(c.get("tags") or []),
                "subindustry": c.get("subindustry") or "",
                "ai_category": ai_category(c),
                "estimated_stage": STAGE_MAP.get(c.get("stage"), "unknown"),
                "team_size_text": c.get("team_size") if c.get("team_size") is not None else "",
                "hiring_status": "hiring",
                "one_liner": c.get("one_liner") or "",
                "all_locations": c.get("all_locations") or "",
                "collected_at": now_iso(),
                "notes": "",
            }
        )
    return companies


def main():
    companies = collect()
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    out = PROCESSED_DIR / "companies.csv"
    with out.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(companies[0].keys()))
        writer.writeheader()
        writer.writerows(companies)
    print(f"Wrote {len(companies)} companies -> {out}")

    by_cat = {}
    for c in companies:
        by_cat[c["ai_category"]] = by_cat.get(c["ai_category"], 0) + 1
    print(json.dumps(by_cat, indent=1))


if __name__ == "__main__":
    main()
