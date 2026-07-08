"""Classification taxonomy + deterministic keyword rules (first pass).

This file IS the rubric: every role family, tag, and keyword rule used in the
published analysis lives here so a skeptical reader can audit or rerun it.

Two-layer approach (see methodology.md):
  1. Title rules assign role_family and seniority deterministically.
  2. Description rules assign operator-need / AI-surface tags by keyword.
An LLM pass (classify.py) only overrides low-confidence records.
"""

from __future__ import annotations

import re

ROLE_FAMILIES = [
    "ai_ml_engineering",
    "data_engineering",
    "analytics_engineering_bi",
    "data_science_research",
    "product_engineering",
    "forward_deployed_solutions",
    "product_management",
    "gtm_sales_cs",
    "founder_operator_generalist",
    "design",
    "ops_finance_people",
    "other",
]

OPERATOR_NEED_TAGS = [
    "data_pipeline",
    "warehouse_semantic_layer",
    "metrics_governance",
    "product_analytics",
    "model_eval_observability",
    "agent_workflows",
    "customer_implementation",
    "workflow_automation",
    "gtm_analytics",
    "security_compliance",
    "infra_platform",
    "internal_tools",
    "reporting_bi",
]

AI_SURFACE_TAGS = [
    "agents",
    "llm_applications",
    "computer_vision",
    "voice_audio",
    "health_ai",
    "finance_ai",
    "legal_ai",
    "devtools_ai",
    "data_ai",
    "robotics",
]

# ---------------------------------------------------------------------------
# Role family from title. Ordered: first match wins, specific before generic.
# ---------------------------------------------------------------------------
ROLE_FAMILY_TITLE_RULES = [
    ("forward_deployed_solutions",
     r"forward.?deploy|\bfde\b|solutions (engineer|architect|consultant)|implementation|customer engineer|field engineer|deployment (strategist|specialist|engineer|lead)|sales engineer|onboarding (engineer|specialist|manager)"),
    ("analytics_engineering_bi",
     r"analytics engineer|business intelligence|bi (engineer|analyst|developer)|data analyst|analytics lead|revenue analyst|analytics manager"),
    ("data_engineering",
     r"data engineer|data platform|data infrastructure|etl|pipeline engineer"),
    ("data_science_research",
     r"data scien|research (scientist|engineer|lead)|applied scientist|machine learning research|quantitative research"),
    ("ai_ml_engineering",
     r"\bml\b|machine learning|\bai engineer|ai/ml|artificial intelligence engineer|llm|genai|deep learning|computer vision|nlp|prompt engineer|agent engineer|applied ai"),
    ("product_management",
     r"product manager|product lead|head of product|\bpm\b|product owner|technical program|program manager"),
    ("design",
     r"design(er)?\b|ux\b|ui\b|brand|creative director"),
    ("gtm_sales_cs",
     r"sales|account (executive|manager)|customer (success|support|experience)|\bcs\b|business development|\bbd(r)?\b|\bsdr\b|growth|marketing|partnership|partner manager|demand generation|revenue|go.?to.?market|gtm|community|developer advocate|devrel|content (producer|writer|manager|lead)|social (media|content)|technical support|support (lead|engineer|specialist)|customer advocate|enablement"),
    ("ops_finance_people",
     r"operations|finance|accounting|people|talent|recruit|\bhr\b|legal|compliance officer|executive assistant|office manager|billing|supply chain|(demand |resource )?planning (director|manager)|filing specialist|clinical (coordinator|specialist)|credentialing"),
    ("founder_operator_generalist",
     r"chief of staff|founding (team|member)|generalist|entrepreneur in residence|special projects|strategic initiatives|strategy (&|and) ops|biz ?ops|future founder"),
    ("product_engineering",
     r"software engineer|full.?stack|front.?end|back.?end|backend|frontend|mobile|ios|android|platform engineer|infrastructure engineer|devops|site reliability|network engineer|sre|security engineer|founding engineer|web engineer|systems engineer|staff engineer|member of technical staff|\bmts\b|engineer"),
]

SENIORITY_RULES = [
    ("founding", r"founding"),
    ("head", r"head of|\bvp\b|vice president|chief|director"),
    ("lead", r"\blead\b|principal|manager,|engineering manager"),
    ("senior", r"senior|staff|\bsr\.?\b"),
    ("junior", r"junior|intern|entry|associate|new grad|graduate"),
]

# ---------------------------------------------------------------------------
# Operator-need tags from description text (PRD section 10.3 keyword examples,
# expanded). A tag applies if any pattern matches the description or title.
# ---------------------------------------------------------------------------
OPERATOR_NEED_RULES = {
    "data_pipeline":
        r"data pipeline|\betl\b|\belt\b|airflow|dagster|prefect|ingestion|kafka|spark|batch and stream|streaming data",
    "warehouse_semantic_layer":
        r"warehouse|snowflake|bigquery|redshift|databricks|\bdbt\b|semantic layer|lakehouse|data lake",
    "metrics_governance":
        r"metrics governance|data governance|data quality|single source of truth|data catalog|master data|data contract",
    "product_analytics":
        r"product analytics|user behavior|amplitude|mixpanel|posthog|funnel analysis|cohort|a/b test|experimentation",
    "model_eval_observability":
        r"\beval(s|uation)?\b|observability|benchmark|model quality|llm monitoring|regression test.{0,20}model|guardrail|hallucination|model performance",
    "agent_workflows":
        r"\bagent(s|ic)?\b|tool.?use|orchestrat|langchain|langgraph|multi.?step reasoning|autonomous workflow",
    "customer_implementation":
        r"customer implementation|onboard.{0,20}customer|customer deployment|professional services|solution design|work directly with (customers|clients)|client.?facing|customer.?facing",
    "workflow_automation":
        r"workflow automation|automate.{0,30}(workflow|process|task)|business process|\brpa\b|back.?office automation",
    "gtm_analytics":
        r"revenue analytics|sales ops|revops|revenue operations|funnel|\bcrm\b|attribution|pipeline metrics|quota|forecast.{0,15}(sales|revenue)|growth analytics",
    "security_compliance":
        r"soc ?2|hipaa|gdpr|compliance|security review|\bpii\b|audit|iso ?27001|pen.?test",
    "infra_platform":
        r"kubernetes|terraform|\baws\b|\bgcp\b|azure|infrastructure as code|ci/cd|distributed systems|scalab|platform team|cloud infrastructure",
    "internal_tools":
        r"internal tool|internal platform|admin (tool|panel|dashboard)|retool|internal dashboard",
    "reporting_bi":
        r"dashboards?\b|looker|tableau|power ?bi|metabase|\bkpi\b|executive report|business intelligence|reporting",
}

AI_SURFACE_RULES = {
    "agents": r"\bagent(s|ic)?\b|autonomous|copilot",
    "llm_applications": r"\bllm\b|large language model|gpt|claude|gemini|prompt|\brag\b|retrieval.?augmented|fine.?tun|foundation model|openai|anthropic",
    "computer_vision": r"computer vision|image (recognition|processing)|object detection|\bocr\b|visual understanding",
    "voice_audio": r"voice|speech|audio|transcription|text.?to.?speech|conversational ai",
    "health_ai": r"clinical|patient|health(care)?|medical|diagnosis|\behr\b|biotech",
    "finance_ai": r"underwriting|trading|banking|lending|payments|financial|fintech|insurance|accounting",
    "legal_ai": r"legal|contract review|law firm|litigation|paralegal",
    "devtools_ai": r"developer tool|code generation|coding assistant|\bsdk\b|\bapi.first\b|devops ai",
    "data_ai": r"data extraction|unstructured data|document (processing|intelligence|parsing)|entity resolution|data labeling|synthetic data",
    "robotics": r"robot|hardware|embodied|drone|autonomous vehicle",
}

# Role families we consider "operator-adjacent": the data/AI operating-system
# work the analysis is about (vs generic product/GTM labels).
OPERATOR_ADJACENT_FAMILIES = {
    "ai_ml_engineering",
    "data_engineering",
    "analytics_engineering_bi",
    "data_science_research",
    "forward_deployed_solutions",
}

# Leadership title patterns for the "leadership gap" analysis (PRD Q2).
DATA_AI_LEADERSHIP_RULES = [
    ("head_of_data", r"head of data|director.{0,10}\bdata\b|vp.{0,10}\bdata\b|data lead\b"),
    ("head_of_ai", r"head of (ai|ml|machine learning)|director.{0,10}\b(ai|ml)\b|vp.{0,10}\b(ai|ml)\b|\bai lead\b"),
    ("founding_data", r"founding.{0,20}\bdata\b"),
    ("founding_ai", r"founding.{0,20}\b(ai|ml|machine learning)\b"),
    ("analytics_lead", r"analytics lead|lead analyst|head of analytics"),
    ("data_platform_lead", r"data platform lead|lead data (engineer|platform)"),
]


def _match(rules, text):
    for label, pattern in rules:
        if re.search(pattern, text, re.IGNORECASE):
            return label
    return None


def classify_role_family(title: str) -> tuple[str, float]:
    """Return (role_family, confidence). Confidence is heuristic: title rules
    are precise for common titles, weaker for vague ones."""
    label = _match(ROLE_FAMILY_TITLE_RULES, title)
    if label is None:
        return "other", 0.2
    # Vague catch-all engineer titles get lower confidence than exact matches.
    if label == "product_engineering" and re.search(r"^(software )?engineer$", title.strip(), re.IGNORECASE):
        return label, 0.6
    return label, 0.9


def classify_seniority(title: str) -> str:
    return _match(SENIORITY_RULES, title) or "mid"


def tag_text(rules: dict, text: str) -> list[str]:
    return [tag for tag, pattern in rules.items() if re.search(pattern, text, re.IGNORECASE)]


def leadership_flag(title: str) -> str:
    return _match(DATA_AI_LEADERSHIP_RULES, title) or ""
