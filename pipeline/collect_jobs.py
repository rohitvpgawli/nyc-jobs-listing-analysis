"""Collect open roles for each company in companies.csv.

Primary source: Work at a Startup (workatastartup.com), YC's official job
board. Company pages and job pages embed structured JSON in a `data-page`
attribute (server-rendered Inertia.js props), so we parse that rather than
scraping the DOM. Full job description HTML is included on job detail pages.

Fallback: for companies with no WaaS listing, we probe the three big ATS
public JSON APIs (Greenhouse, Lever, Ashby) using the company slug.

Raw responses are saved to data/raw/jobs/ (gitignored) with timestamps.
The published jobs.csv carries derived fields + source URLs only.
"""

from __future__ import annotations

import csv
import html as htmllib
import json
import re
import sys

from common import PROCESSED_DIR, RAW_DIR, now_iso, polite_get

import requests

WAAS_COMPANY_URL = "https://www.workatastartup.com/companies/{slug}"
WAAS_JOB_URL = "https://www.workatastartup.com/jobs/{job_id}"

ATS_PROBES = [
    ("greenhouse", "https://boards-api.greenhouse.io/v1/boards/{slug}/jobs?content=true"),
    ("lever", "https://api.lever.co/v0/postings/{slug}?mode=json"),
    ("ashby", "https://api.ashbyhq.com/posting-api/job-board/{slug}?includeCompensation=true"),
]

DATA_PAGE_RE = re.compile(r'data-page="([^"]+)"')
TAG_RE = re.compile(r"<[^>]+>")


def parse_data_page(html_text: str) -> dict | None:
    m = DATA_PAGE_RE.search(html_text)
    if not m:
        return None
    return json.loads(htmllib.unescape(m.group(1)))


def strip_html(html_text: str) -> str:
    if not html_text:
        return ""
    text = re.sub(r"</(p|li|h\d|div|br)>", "\n", html_text, flags=re.IGNORECASE)
    text = TAG_RE.sub(" ", text)
    text = htmllib.unescape(text)
    return re.sub(r"[ \t]+", " ", text).strip()


def fetch_waas_jobs(session: requests.Session, slug: str) -> list[dict]:
    """Return job listings (with descriptions) for one company from WaaS."""
    resp = polite_get(WAAS_COMPANY_URL.format(slug=slug), session=session)
    if resp.status_code != 200:
        return []
    page = parse_data_page(resp.text)
    if not page:
        return []
    company_props = page.get("props", {}).get("company") or {}
    listings = company_props.get("jobs") or []

    jobs = []
    for listing in listings:
        job_id = listing.get("id")
        detail = {}
        detail_resp = polite_get(WAAS_JOB_URL.format(job_id=job_id), session=session)
        if detail_resp.status_code == 200:
            detail_page = parse_data_page(detail_resp.text)
            if detail_page:
                detail = detail_page.get("props", {}).get("job") or {}
        merged = {**listing, **detail}
        jobs.append(
            {
                "source": "workatastartup",
                "job_id": f"waas-{job_id}",
                "job_title": merged.get("title") or "",
                "job_url": WAAS_JOB_URL.format(job_id=job_id),
                "location_text": merged.get("location") or "",
                "job_type": merged.get("jobType") or "",
                "salary_range": merged.get("salaryRange") or "",
                "equity_range": merged.get("equityRange") or "",
                "min_experience": merged.get("minExperience") or "",
                "skills": "|".join(merged.get("skills") or []),
                "job_description_text": strip_html(merged.get("descriptionHtml") or ""),
                "posted_date": "",
            }
        )
    return jobs


def probe_ats(session: requests.Session, slug: str) -> list[dict]:
    """Try Greenhouse / Lever / Ashby public APIs with the company slug."""
    for ats, url_tpl in ATS_PROBES:
        url = url_tpl.format(slug=slug)
        try:
            resp = polite_get(url, session=session)
        except requests.RequestException:
            continue
        if resp.status_code != 200:
            continue
        try:
            data = resp.json()
        except ValueError:
            continue

        jobs = []
        if ats == "greenhouse":
            for j in data.get("jobs", []):
                jobs.append(
                    {
                        "job_id": f"gh-{j['id']}",
                        "job_title": j.get("title") or "",
                        "job_url": j.get("absolute_url") or "",
                        "location_text": (j.get("location") or {}).get("name") or "",
                        "posted_date": (j.get("updated_at") or "")[:10],
                        "job_description_text": strip_html(htmllib.unescape(j.get("content") or "")),
                    }
                )
        elif ats == "lever":
            if not isinstance(data, list):
                continue
            for j in data:
                jobs.append(
                    {
                        "job_id": f"lever-{j.get('id')}",
                        "job_title": j.get("text") or "",
                        "job_url": j.get("hostedUrl") or "",
                        "location_text": (j.get("categories") or {}).get("location") or "",
                        "posted_date": "",
                        "job_description_text": strip_html(j.get("description") or ""),
                    }
                )
        elif ats == "ashby":
            for j in data.get("jobs", []):
                jobs.append(
                    {
                        "job_id": f"ashby-{j.get('id')}",
                        "job_title": j.get("title") or "",
                        "job_url": j.get("jobUrl") or "",
                        "location_text": j.get("location") or "",
                        "posted_date": (j.get("publishedAt") or "")[:10],
                        "job_description_text": strip_html(j.get("descriptionHtml") or ""),
                    }
                )

        if jobs:
            for j in jobs:
                j.setdefault("source", ats)
                j.setdefault("job_type", "")
                j.setdefault("salary_range", "")
                j.setdefault("equity_range", "")
                j.setdefault("min_experience", "")
                j.setdefault("skills", "")
            return jobs
    return []


def main():
    companies_path = PROCESSED_DIR / "companies.csv"
    with companies_path.open() as f:
        companies = list(csv.DictReader(f))

    raw_jobs_dir = RAW_DIR / "jobs"
    raw_jobs_dir.mkdir(parents=True, exist_ok=True)

    session = requests.Session()
    all_rows = []
    stats = {"waas": 0, "ats": 0, "none": 0}

    for i, company in enumerate(companies, 1):
        slug = company["slug"]
        cache_path = raw_jobs_dir / f"{slug}.json"
        if cache_path.exists():
            jobs = json.loads(cache_path.read_text())["data"]
        else:
            jobs = fetch_waas_jobs(session, slug)
            if not jobs:
                jobs = probe_ats(session, slug)
            cache_path.write_text(json.dumps({"collected_at": now_iso(), "data": jobs}, indent=1))

        if not jobs:
            stats["none"] += 1
        elif jobs[0]["source"] == "workatastartup":
            stats["waas"] += 1
        else:
            stats["ats"] += 1

        for job in jobs:
            all_rows.append(
                {
                    "company_id": company["company_id"],
                    "company_name": company["company_name"],
                    **job,
                    "collected_at": now_iso(),
                }
            )
        print(f"[{i}/{len(companies)}] {company['company_name']}: {len(jobs)} roles", flush=True)

    out = PROCESSED_DIR / "jobs_raw.csv"
    fieldnames = [
        "job_id", "company_id", "company_name", "job_title", "job_url", "source",
        "location_text", "job_type", "salary_range", "equity_range",
        "min_experience", "skills", "posted_date", "job_description_text",
        "collected_at",
    ]
    with out.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_rows)

    print(f"\nWrote {len(all_rows)} roles -> {out}")
    print(f"Coverage: {stats}")


if __name__ == "__main__":
    main()
