"""Clean job records and classify them (hybrid: keyword rules + LLM pass).

Pipeline per methodology.md:
  1. Dedupe (company + normalized title + URL) and normalize locations.
  2. Deterministic first pass from taxonomy.py (role family, seniority,
     operator-need / AI-surface tags) with a heuristic confidence score.
  3. LLM second pass for low-confidence records only, via any
     OpenAI-compatible chat-completions API. Responses are cached to
     data/cache/llm/ so reruns are free and deterministic.
  4. Records the LLM also can't settle keep `manual_review_flag=1`.

Env vars (see `.env.example`): ZAI_API_KEY or GLM_API_KEY for GLM 5.2 via
Z.ai's OpenAI-compatible API. Optional LLM_BASE_URL and LLM_MODEL override
defaults. OPENAI_API_KEY still works as a fallback. Loads repo-root `.env`
automatically. Without a key, the keyword pass still runs end-to-end.
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import sys

import requests

from common import CACHE_DIR, PROCESSED_DIR, ROOT, now_iso
import taxonomy as tax

ROOT_OVERRIDES = ROOT / "pipeline" / "manual_overrides.json"

# GLM 5.2 via Z.ai (OpenAI-compatible). Override with LLM_* or legacy OPENAI_*.
DEFAULT_GLM_BASE_URL = "https://api.z.ai/api/paas/v4"
DEFAULT_GLM_MODEL = "glm-5.2"
API_KEY_ENV_VARS = ("ZAI_API_KEY", "GLM_API_KEY", "OPENAI_API_KEY")

LLM_CONFIDENCE_THRESHOLD = 0.8
DESCRIPTION_CHAR_LIMIT = 6000

LLM_SYSTEM_PROMPT = """You classify startup job postings. Respond with strict JSON only, no prose.

Given a job title and description, return:
{
  "role_family": one of %s,
  "seniority": one of ["founding","head","lead","senior","mid","junior"],
  "operator_need_tags": subset of %s,
  "ai_surface_tags": subset of %s,
  "confidence": float 0-1
}

Definitions:
- forward_deployed_solutions: engineers embedded with customers (implementation, solutions, field work).
- analytics_engineering_bi: dbt/BI/analytics/data-analyst work.
- founder_operator_generalist: chief of staff, generalist, founding non-eng operator.
- operator_need_tags describe the OPERATING PROBLEM the role solves, judged from the description, not the title.
Only include tags clearly supported by the text.""" % (
    json.dumps(tax.ROLE_FAMILIES),
    json.dumps(tax.OPERATOR_NEED_TAGS),
    json.dumps(tax.AI_SURFACE_TAGS),
)


# ---------------------------------------------------------------------------
# Cleaning
# ---------------------------------------------------------------------------

def norm_title(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", title.lower()).strip()


def remote_policy(location: str) -> str:
    loc = location.lower()
    has_remote = "remote" in loc
    has_city = bool(re.search(r"new york|nyc|\bny\b|san francisco|austin|boston|chicago|seattle|los angeles|miami|denver", loc))
    if has_remote and has_city:
        return "hybrid"
    if has_remote:
        return "remote"
    if has_city or loc.strip():
        return "onsite"
    return "unknown"


def nyc_relevance(location: str) -> str:
    loc = location.lower()
    is_ny = bool(re.search(r"new york|nyc|\bny\b", loc))
    has_remote = "remote" in loc
    if is_ny and not has_remote:
        return "nyc_required"
    if is_ny and has_remote:
        return "nyc_optional"
    if has_remote and re.search(r"\bus\b|united states|usa|anywhere", loc):
        return "remote_us"
    if has_remote:
        return "remote_us"
    if loc.strip():
        return "not_nyc"
    return "unknown"


def dedupe(rows: list[dict]) -> list[dict]:
    seen = set()
    out = []
    for row in rows:
        key = (row["company_id"], norm_title(row["job_title"]))
        if key in seen:
            continue
        seen.add(key)
        out.append(row)
    return out


def strip_pii(text: str) -> str:
    text = re.sub(r"[\w.+-]+@[\w-]+\.[\w.]+", "[email removed]", text)
    return text


# ---------------------------------------------------------------------------
# LLM pass
# ---------------------------------------------------------------------------

def llm_api_key() -> str | None:
    for name in API_KEY_ENV_VARS:
        value = os.environ.get(name, "").strip()
        if value:
            return value
    return None


def llm_model() -> str:
    return (
        os.environ.get("LLM_MODEL")
        or os.environ.get("OPENAI_MODEL")
        or DEFAULT_GLM_MODEL
    )


def llm_base_url() -> str:
    raw = (
        os.environ.get("LLM_BASE_URL")
        or os.environ.get("OPENAI_BASE_URL")
        or DEFAULT_GLM_BASE_URL
    )
    return raw.rstrip("/")


def llm_available() -> bool:
    return llm_api_key() is not None


def llm_classify(job: dict) -> dict | None:
    cache_dir = CACHE_DIR / "llm"
    cache_dir.mkdir(parents=True, exist_ok=True)
    desc = job["job_description_text"][:DESCRIPTION_CHAR_LIMIT]
    model = llm_model()
    cache_key = hashlib.sha256(f"{model}|{job['job_title']}|{desc}".encode()).hexdigest()[:24]
    cache_path = cache_dir / f"{cache_key}.json"
    if cache_path.exists():
        return json.loads(cache_path.read_text())

    api_key = llm_api_key()
    if not api_key:
        return None

    user_msg = f"TITLE: {job['job_title']}\nCOMPANY: {job['company_name']}\n\nDESCRIPTION:\n{desc}"
    resp = requests.post(
        f"{llm_base_url()}/chat/completions",
        headers={"Authorization": f"Bearer {api_key}"},
        json={
            "model": model,
            "temperature": 0,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": LLM_SYSTEM_PROMPT},
                {"role": "user", "content": user_msg},
            ],
        },
        timeout=60,
    )
    resp.raise_for_status()
    content = resp.json()["choices"][0]["message"]["content"]
    result = json.loads(content)

    # Sanitize against taxonomy so a hallucinated label can't leak through.
    result["role_family"] = result.get("role_family") if result.get("role_family") in tax.ROLE_FAMILIES else "other"
    result["operator_need_tags"] = [t for t in result.get("operator_need_tags", []) if t in tax.OPERATOR_NEED_TAGS]
    result["ai_surface_tags"] = [t for t in result.get("ai_surface_tags", []) if t in tax.AI_SURFACE_TAGS]
    if result.get("seniority") not in {"founding", "head", "lead", "senior", "mid", "junior"}:
        result["seniority"] = "unknown"
    result["confidence"] = float(result.get("confidence", 0.5))
    cache_path.write_text(json.dumps(result, indent=1))
    return result


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    with (PROCESSED_DIR / "jobs_raw.csv").open() as f:
        rows = list(csv.DictReader(f))
    print(f"Loaded {len(rows)} raw roles")

    rows = dedupe(rows)
    print(f"After dedupe: {len(rows)}")

    overrides_path = ROOT_OVERRIDES
    overrides = {}
    if overrides_path.exists():
        overrides = {k: v for k, v in json.loads(overrides_path.read_text()).items() if not k.startswith("_")}

    llm_used = 0
    llm_wanted = 0
    manual_used = 0
    for i, row in enumerate(rows, 1):
        title = row["job_title"]
        text = f"{title}\n{row['job_description_text']}"

        family, confidence = tax.classify_role_family(title)
        seniority = tax.classify_seniority(title)
        need_tags = tax.tag_text(tax.OPERATOR_NEED_RULES, text)
        surface_tags = tax.tag_text(tax.AI_SURFACE_RULES, text)
        method = "keyword"

        if row["job_id"] in overrides:
            ov = overrides[row["job_id"]]
            family = ov["role_family"]
            if ov.get("seniority"):
                seniority = ov["seniority"]
            confidence = 0.95
            method = "manual_review"
            manual_used += 1

        needs_llm = method == "keyword" and (
            confidence < LLM_CONFIDENCE_THRESHOLD or (not need_tags and len(row["job_description_text"]) > 200)
        )
        if needs_llm:
            llm_wanted += 1
            result = llm_classify(row)
            if result:
                llm_used += 1
                method = "keyword+llm"
                if result["confidence"] >= confidence:
                    family = result["role_family"]
                    if result["seniority"] != "unknown":
                        seniority = result["seniority"]
                    confidence = result["confidence"]
                # Tags are additive: union of keyword + LLM.
                need_tags = sorted(set(need_tags) | set(result["operator_need_tags"]))
                surface_tags = sorted(set(surface_tags) | set(result["ai_surface_tags"]))

        row.update(
            {
                "job_description_text": strip_pii(row["job_description_text"]),
                "remote_policy": remote_policy(row["location_text"]),
                "nyc_relevance": nyc_relevance(row["location_text"]),
                "role_family": family,
                "seniority": seniority,
                "operator_need_tags": "|".join(need_tags),
                "ai_surface_tags": "|".join(surface_tags),
                "leadership_flag": tax.leadership_flag(title),
                "operator_adjacent": int(family in tax.OPERATOR_ADJACENT_FAMILIES),
                "classification_method": method,
                "classification_confidence": round(confidence, 2),
                "manual_review_flag": int(confidence < 0.6),
            }
        )
        if i % 50 == 0:
            print(f"  classified {i}/{len(rows)}", flush=True)

    out = PROCESSED_DIR / "jobs.csv"
    # Published CSV excludes full description text (licensing caution, PRD
    # reproducibility rules) — derived tags + source links only.
    fieldnames = [
        "job_id", "company_id", "company_name", "job_title", "job_url", "source",
        "location_text", "remote_policy", "nyc_relevance", "posted_date",
        "job_type", "salary_range", "equity_range", "min_experience", "skills",
        "seniority", "role_family", "operator_need_tags", "ai_surface_tags",
        "leadership_flag", "operator_adjacent", "classification_method",
        "classification_confidence", "manual_review_flag", "collected_at",
    ]
    with out.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

    # Full record incl. description stays local for analysis/QA.
    local = PROCESSED_DIR / "jobs_with_text.local.csv"
    with local.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames[:-1] + ["job_description_text", "collected_at"], extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nWrote {len(rows)} classified roles -> {out}")
    print(f"Manual review overrides applied: {manual_used}")
    if llm_available():
        print(f"LLM pass: {llm_used}/{llm_wanted} ambiguous records classified (model={llm_model()})")
    elif llm_wanted:
        print(
            f"LLM pass: 0/{llm_wanted} ambiguous records classified  "
            f"(set ZAI_API_KEY or GLM_API_KEY in .env — see .env.example)"
        )
    else:
        print(f"LLM pass: 0/0 ambiguous records classified")

    from collections import Counter
    print("\nRole families:", dict(Counter(r['role_family'] for r in rows).most_common()))
    print("\nFlagged for manual review:", sum(r['manual_review_flag'] for r in rows))


if __name__ == "__main__":
    main()
