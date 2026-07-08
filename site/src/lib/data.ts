import atlasJson from "../data/atlas.json";

export interface Company {
  id: string;
  name: string;
  batch: string;
  batchYear: number | null;
  teamSize: number | null;
  aiCategory: string;
  stage: string;
  oneLiner: string;
  website: string;
  ycUrl: string;
  nycPresence: string;
  jobCount: number;
}

export interface Job {
  id: string;
  companyId: string;
  company: string;
  title: string;
  url: string;
  source: string;
  location: string;
  remote: string;
  nyc: string;
  family: string;
  seniority: string;
  needTags: string[];
  surfaceTags: string[];
  leadership: string;
  operatorAdjacent: boolean;
  salaryMin: number | null;
  salaryMax: number | null;
  minExperience: string;
  aiCategory: string;
  batch: string;
  batchYear: number | null;
  teamSize: number | null;
  confidence: number;
}

export interface Atlas {
  meta: {
    title: string;
    builtAt: string;
    collectedAt: string;
    sources: string[];
    companyCount: number;
    jobCount: number;
    taxonomy: {
      roleFamilies: string[];
      operatorNeedTags: string[];
      aiSurfaceTags: string[];
      operatorAdjacentFamilies: string[];
    };
  };
  companies: Company[];
  jobs: Job[];
}

export const atlas = atlasJson as unknown as Atlas;

export function countBy<T>(items: T[], key: (item: T) => string): Map<string, number> {
  const m = new Map<string, number>();
  for (const item of items) {
    const k = key(item);
    m.set(k, (m.get(k) ?? 0) + 1);
  }
  return m;
}

export const fmtPct = (x: number) => `${Math.round(x * 100)}%`;
