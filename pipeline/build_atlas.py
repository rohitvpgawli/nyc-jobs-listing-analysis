"""Join companies + classified jobs into the site dataset and outputs.

Produces:
  data/processed/atlas.json      — single payload the site consumes
  data/processed/target_roles.csv — Rohit-fit shortlist (PRD 11.3)
  outputs/summary.json           — headline stats for the report
"""

from __future__ import annotations

import csv
import json
import re
from collections import Counter

from common import PROCESSED_DIR, ROOT, now_iso
import taxonomy as tax

OUTPUTS_DIR = ROOT / "outputs"

# Operator-need tags closest to Rohit's target lane (Head of Data / Head of
# AI / analytics engineering / AI workflows / GTM analytics).
FIT_TAGS = {
    "data_pipeline": 2,
    "warehouse_semantic_layer": 3,
    "metrics_governance": 3,
    "product_analytics": 2,
    "model_eval_observability": 2,
    "agent_workflows": 2,
    "gtm_analytics": 2,
    "reporting_bi": 1,
    "workflow_automation": 1,
    "internal_tools": 1,
}

FIT_FAMILIES = {
    "analytics_engineering_bi": 3,
    "data_engineering": 3,
    "ai_ml_engineering": 1,
    "data_science_research": 1,
    "forward_deployed_solutions": 2,
    "founder_operator_generalist": 2,
}

FIT_SENIORITY = {"founding": 3, "head": 3, "lead": 2, "senior": 1}


def parse_salary(text: str) -> tuple[int | None, int | None]:
    """'$180K - $240K' -> (180000, 240000)."""
    nums = re.findall(r"\$?(\d+(?:\.\d+)?)\s*[kK]", text or "")
    vals = [int(float(n) * 1000) for n in nums]
    if len(vals) >= 2:
        return vals[0], vals[1]
    if len(vals) == 1:
        return vals[0], vals[0]
    return None, None


def fit_score(job: dict) -> tuple[int, list[str]]:
    reasons = []
    score = 0
    fam = job["role_family"]
    if fam in FIT_FAMILIES:
        score += FIT_FAMILIES[fam]
        reasons.append(f"role family: {fam}")
    sen = job["seniority"]
    if sen in FIT_SENIORITY:
        score += FIT_SENIORITY[sen]
        reasons.append(f"seniority: {sen}")
    if job["leadership_flag"]:
        score += 3
        reasons.append(f"data/AI leadership title ({job['leadership_flag']})")
    tags = [t for t in job["operator_need_tags"].split("|") if t]
    tag_pts = sum(FIT_TAGS.get(t, 0) for t in tags)
    if tag_pts:
        score += min(tag_pts, 6)
        matched = [t for t in tags if t in FIT_TAGS]
        reasons.append("operator needs: " + ", ".join(matched))
    if job["nyc_relevance"] in ("nyc_required", "nyc_optional"):
        score += 1
        reasons.append("NYC role")
    return score, reasons


def main():
    with (PROCESSED_DIR / "companies.csv").open() as f:
        companies = list(csv.DictReader(f))
    with (PROCESSED_DIR / "jobs.csv").open() as f:
        jobs = list(csv.DictReader(f))

    jobs_by_company = Counter(j["company_id"] for j in jobs)
    company_index = {c["company_id"]: c for c in companies}

    # ---- site payload ----------------------------------------------------
    site_companies = []
    for c in companies:
        if jobs_by_company[c["company_id"]] == 0:
            continue
        site_companies.append(
            {
                "id": c["company_id"],
                "name": c["company_name"],
                "batch": c["yc_batch"],
                "batchYear": int(c["batch_year"]) if c["batch_year"] else None,
                "teamSize": int(c["team_size_text"]) if c["team_size_text"] else None,
                "aiCategory": c["ai_category"],
                "stage": c["estimated_stage"],
                "oneLiner": c["one_liner"],
                "website": c["website"],
                "ycUrl": c["source_url"],
                "nycPresence": c["nyc_presence"],
                "jobCount": jobs_by_company[c["company_id"]],
            }
        )

    site_jobs = []
    for j in jobs:
        c = company_index.get(j["company_id"], {})
        smin, smax = parse_salary(j["salary_range"])
        site_jobs.append(
            {
                "id": j["job_id"],
                "companyId": j["company_id"],
                "company": j["company_name"],
                "title": j["job_title"],
                "url": j["job_url"],
                "source": j["source"],
                "location": j["location_text"],
                "remote": j["remote_policy"],
                "nyc": j["nyc_relevance"],
                "family": j["role_family"],
                "seniority": j["seniority"],
                "needTags": [t for t in j["operator_need_tags"].split("|") if t],
                "surfaceTags": [t for t in j["ai_surface_tags"].split("|") if t],
                "leadership": j["leadership_flag"],
                "operatorAdjacent": j["operator_adjacent"] == "1",
                "salaryMin": smin,
                "salaryMax": smax,
                "minExperience": j["min_experience"],
                "aiCategory": c.get("ai_category", "other"),
                "batch": c.get("yc_batch", ""),
                "batchYear": int(c["batch_year"]) if c.get("batch_year") else None,
                "teamSize": int(c["team_size_text"]) if c.get("team_size_text") else None,
                "confidence": float(j["classification_confidence"]),
            }
        )

    atlas = {
        "meta": {
            "title": "NYC AI Startup Hiring Signal Atlas",
            "builtAt": now_iso(),
            "collectedAt": jobs[0]["collected_at"][:10] if jobs else "",
            "sources": ["YC OSS API (public YC directory mirror)", "Work at a Startup", "Greenhouse/Lever/Ashby public boards"],
            "companyCount": len(site_companies),
            "jobCount": len(site_jobs),
            "taxonomy": {
                "roleFamilies": tax.ROLE_FAMILIES,
                "operatorNeedTags": tax.OPERATOR_NEED_TAGS,
                "aiSurfaceTags": tax.AI_SURFACE_TAGS,
                "operatorAdjacentFamilies": sorted(tax.OPERATOR_ADJACENT_FAMILIES),
            },
        },
        "companies": site_companies,
        "jobs": site_jobs,
    }
    atlas_path = PROCESSED_DIR / "atlas.json"
    atlas_path.write_text(json.dumps(atlas, separators=(",", ":")))
    print(f"Wrote atlas.json: {len(site_companies)} companies, {len(site_jobs)} jobs ({atlas_path.stat().st_size // 1024} KB)")

    # ---- Rohit-fit shortlist ----------------------------------------------
    scored = []
    for j in jobs:
        score, reasons = fit_score(j)
        if score >= 6:
            scored.append((score, j, reasons))
    scored.sort(key=lambda x: -x[0])

    with (PROCESSED_DIR / "target_roles.csv").open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["company", "role", "fit_score", "why_fit", "outreach_angle", "proof_artifact", "job_url", "application_status"])
        for score, j, reasons in scored[:30]:
            c = company_index.get(j["company_id"], {})
            writer.writerow([
                j["company_name"],
                j["job_title"],
                score,
                "; ".join(reasons),
                f"Reference the NYC AI Hiring Atlas finding relevant to {c.get('ai_category', 'their vertical')}",
                "NYC AI Hiring Atlas (this repo)",
                j["job_url"],
                "not_started",
            ])
    print(f"Wrote target_roles.csv: {min(len(scored), 30)} shortlisted roles (of {len(scored)} scoring >= 6)")

    # ---- headline stats ----------------------------------------------------
    fam_counts = Counter(j["family"] for j in site_jobs)
    need_counts = Counter(t for j in site_jobs for t in j["needTags"])
    surface_counts = Counter(t for j in site_jobs for t in j["surfaceTags"])
    operator_share = sum(1 for j in site_jobs if j["operatorAdjacent"]) / max(len(site_jobs), 1)
    leadership = [j for j in site_jobs if j["leadership"]]
    agent_mentions = sum(1 for j in site_jobs if "agents" in j["surfaceTags"])

    summary = {
        "builtAt": now_iso(),
        "companies": len(site_companies),
        "jobs": len(site_jobs),
        "roleFamilies": dict(fam_counts.most_common()),
        "operatorNeeds": dict(need_counts.most_common()),
        "aiSurfaces": dict(surface_counts.most_common()),
        "operatorAdjacentShare": round(operator_share, 3),
        "leadershipRoles": [{"company": j["company"], "title": j["title"], "flag": j["leadership"]} for j in leadership],
        "agentMentionShare": round(agent_mentions / max(len(site_jobs), 1), 3),
        "nycBreakdown": dict(Counter(j["nyc"] for j in site_jobs)),
        "seniority": dict(Counter(j["seniority"] for j in site_jobs)),
    }
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUTS_DIR / "summary.json").write_text(json.dumps(summary, indent=1))
    print(json.dumps({k: v for k, v in summary.items() if k in ("roleFamilies", "operatorAdjacentShare", "agentMentionShare")}, indent=1))


if __name__ == "__main__":
    main()
