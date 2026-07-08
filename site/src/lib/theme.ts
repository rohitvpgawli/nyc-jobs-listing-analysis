// NYC-subway-inspired visual language: each role family is a "line" with an
// MTA-style bullet color (brightened where needed for dark backgrounds).

export interface FamilyMeta {
  label: string;
  short: string;
  bullet: string; // single character shown in the route bullet
  color: string;
  dark?: boolean; // bullet text should be dark
  operatorAdjacent: boolean;
}

export const FAMILY_META: Record<string, FamilyMeta> = {
  product_engineering: { label: "Product engineering", short: "Product eng", bullet: "E", color: "#2864DC", operatorAdjacent: false },
  gtm_sales_cs: { label: "GTM / sales / customer success", short: "GTM & sales", bullet: "1", color: "#EE352E", operatorAdjacent: false },
  forward_deployed_solutions: { label: "Forward-deployed / solutions", short: "Forward-deployed", bullet: "N", color: "#FCCC0A", dark: true, operatorAdjacent: true },
  ops_finance_people: { label: "Ops / finance / people", short: "Ops & finance", bullet: "S", color: "#8A8D91", operatorAdjacent: false },
  design: { label: "Design", short: "Design", bullet: "L", color: "#A7A9AC", operatorAdjacent: false },
  ai_ml_engineering: { label: "AI / ML engineering", short: "AI/ML eng", bullet: "4", color: "#00A344", operatorAdjacent: true },
  product_management: { label: "Product management", short: "Product mgmt", bullet: "J", color: "#A96B2C", operatorAdjacent: false },
  data_science_research: { label: "Data science / research", short: "DS & research", bullet: "G", color: "#6CBE45", dark: true, operatorAdjacent: true },
  founder_operator_generalist: { label: "Founder / operator generalist", short: "Generalist", bullet: "T", color: "#00ADD0", dark: true, operatorAdjacent: false },
  data_engineering: { label: "Data engineering", short: "Data eng", bullet: "F", color: "#FF6319", operatorAdjacent: true },
  analytics_engineering_bi: { label: "Analytics engineering / BI", short: "Analytics & BI", bullet: "7", color: "#C75FBB", operatorAdjacent: true },
  other: { label: "Other", short: "Other", bullet: "•", color: "#58595B", operatorAdjacent: false },
};

export const NEED_LABELS: Record<string, string> = {
  agent_workflows: "Agent workflows",
  infra_platform: "Infra & platform",
  reporting_bi: "Reporting & BI",
  gtm_analytics: "GTM analytics",
  customer_implementation: "Customer implementation",
  security_compliance: "Security & compliance",
  model_eval_observability: "Evals & observability",
  data_pipeline: "Data pipelines",
  workflow_automation: "Workflow automation",
  product_analytics: "Product analytics",
  internal_tools: "Internal tools",
  warehouse_semantic_layer: "Warehouse & semantic layer",
  metrics_governance: "Metrics governance",
};

export const CATEGORY_LABELS: Record<string, string> = {
  core_ai: "Core AI",
  fintech_ai: "Fintech AI",
  health_ai: "Health AI",
  ai_enabled_vertical_saas: "Vertical SaaS AI",
  devtools_ai: "Devtools AI",
  data_infra: "Data infra",
  other: "Other",
};

export const CATEGORY_COLORS: Record<string, string> = {
  core_ai: "#00A344",
  fintech_ai: "#2864DC",
  health_ai: "#EE352E",
  ai_enabled_vertical_saas: "#FCCC0A",
  devtools_ai: "#C75FBB",
  data_infra: "#FF6319",
  other: "#8A8D91",
};

export const SENIORITY_LABELS: Record<string, string> = {
  founding: "Founding",
  head: "Head / VP / C-level",
  lead: "Lead / principal",
  senior: "Senior / staff",
  mid: "Mid-level",
  junior: "Junior / intern",
};

export const NYC_LABELS: Record<string, string> = {
  nyc_required: "NYC required",
  nyc_optional: "NYC optional (hybrid/remote)",
  remote_us: "Remote (US)",
  not_nyc: "Other city",
  unknown: "Unknown",
};
