import { useMemo, useState } from "react";
import { atlas, Job } from "../lib/data";
import { FAMILY_META, NEED_LABELS, NYC_LABELS, SENIORITY_LABELS } from "../lib/theme";
import { useTooltip } from "../lib/useTooltip";

const ALL = "all";
const HEATMAP_ROWS = 28;
const TABLE_PAGE = 40;

function salaryText(j: Job): string {
  if (j.salaryMin == null) return "—";
  if (j.salaryMin === j.salaryMax) return `$${(j.salaryMin / 1000).toFixed(0)}K`;
  return `$${(j.salaryMin! / 1000).toFixed(0)}–${(j.salaryMax! / 1000).toFixed(0)}K`;
}

export default function Explorer() {
  const [family, setFamily] = useState(ALL);
  const [seniority, setSeniority] = useState(ALL);
  const [nyc, setNyc] = useState(ALL);
  const [need, setNeed] = useState(ALL);
  const [query, setQuery] = useState("");
  const [limit, setLimit] = useState(TABLE_PAGE);
  const { show, hide, node } = useTooltip();

  const jobs = useMemo(() => {
    const q = query.trim().toLowerCase();
    return atlas.jobs.filter(
      (j) =>
        (family === ALL || j.family === family) &&
        (seniority === ALL || j.seniority === seniority) &&
        (nyc === ALL || j.nyc === nyc) &&
        (need === ALL || j.needTags.includes(need)) &&
        (q === "" || j.title.toLowerCase().includes(q) || j.company.toLowerCase().includes(q))
    );
  }, [family, seniority, nyc, need, query]);

  const heatmap = useMemo(() => {
    const needTags = atlas.meta.taxonomy.operatorNeedTags;
    const byCompany = new Map<string, { name: string; total: number; cells: Map<string, number> }>();
    for (const j of jobs) {
      let row = byCompany.get(j.companyId);
      if (!row) {
        row = { name: j.company, total: 0, cells: new Map() };
        byCompany.set(j.companyId, row);
      }
      row.total += 1;
      for (const t of j.needTags) row.cells.set(t, (row.cells.get(t) ?? 0) + 1);
    }
    const rows = [...byCompany.values()].sort((a, b) => b.total - a.total).slice(0, HEATMAP_ROWS);
    const maxCell = Math.max(1, ...rows.flatMap((r) => [...r.cells.values()]));
    return { needTags, rows, maxCell };
  }, [jobs]);

  const families = useMemo(
    () => [...new Set(atlas.jobs.map((j) => j.family))].sort((a, b) => (FAMILY_META[a].short < FAMILY_META[b].short ? -1 : 1)),
    []
  );

  return (
    <section id="explorer">
      <div className="wrap">
        <div className="kicker">05 · Explore the atlas</div>
        <h2>Now dig. Every cell links back to a live posting.</h2>
        <p className="lede">
          {atlas.meta.jobCount} roles across {atlas.meta.companyCount} companies, filterable by role family,
          seniority, location policy, and the operating need buried in the description.
        </p>

        <div className="explorer-filters">
          <input
            className="explorer-search"
            placeholder="Search title or company…"
            value={query}
            onChange={(e) => {
              setQuery(e.target.value);
              setLimit(TABLE_PAGE);
            }}
          />
          <div className="chip-row">
            <button className={`chip ${family === ALL ? "on" : ""}`} onClick={() => setFamily(ALL)}>
              All families
            </button>
            {families.map((f) => (
              <button
                key={f}
                className={`chip ${family === f ? "on" : ""}`}
                onClick={() => {
                  setFamily(family === f ? ALL : f);
                  setLimit(TABLE_PAGE);
                }}
              >
                <span className="chip-dot" style={{ background: FAMILY_META[f].color }} />
                {FAMILY_META[f].short}
              </button>
            ))}
          </div>
          <div className="chip-row">
            {Object.entries(SENIORITY_LABELS).map(([k, label]) => (
              <button
                key={k}
                className={`chip ${seniority === k ? "on" : ""}`}
                onClick={() => {
                  setSeniority(seniority === k ? ALL : k);
                  setLimit(TABLE_PAGE);
                }}
              >
                {label}
              </button>
            ))}
            <span className="chip-sep" />
            {Object.entries(NYC_LABELS)
              .filter(([k]) => k !== "unknown")
              .map(([k, label]) => (
                <button
                  key={k}
                  className={`chip ${nyc === k ? "on" : ""}`}
                  onClick={() => {
                    setNyc(nyc === k ? ALL : k);
                    setLimit(TABLE_PAGE);
                  }}
                >
                  {label}
                </button>
              ))}
          </div>
        </div>

        <div className="heatmap-scroll">
          <table className="heatmap">
            <thead>
              <tr>
                <th className="heatmap-corner">
                  {jobs.length} roles · top {heatmap.rows.length} companies
                </th>
                {heatmap.needTags.map((t) => (
                  <th
                    key={t}
                    className={`heatmap-col ${need === t ? "on" : ""}`}
                    onClick={() => {
                      setNeed(need === t ? ALL : t);
                      setLimit(TABLE_PAGE);
                    }}
                  >
                    <span>{NEED_LABELS[t]}</span>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {heatmap.rows.map((row) => (
                <tr key={row.name}>
                  <td className="heatmap-company">
                    {row.name} <span className="heatmap-total">{row.total}</span>
                  </td>
                  {heatmap.needTags.map((t) => {
                    const v = row.cells.get(t) ?? 0;
                    return (
                      <td
                        key={t}
                        className="heatmap-cell"
                        style={{
                          background: v === 0 ? "transparent" : `rgba(252, 204, 10, ${0.14 + 0.86 * (v / heatmap.maxCell)})`,
                          color: v / heatmap.maxCell > 0.5 ? "#101014" : "var(--paper-dim)",
                        }}
                        onMouseMove={(e) => v > 0 && show(e, `<b>${row.name}</b><br/>${NEED_LABELS[t]}: ${v} role${v > 1 ? "s" : ""}`)}
                        onMouseLeave={hide}
                      >
                        {v || ""}
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="jobtable">
          {jobs.slice(0, limit).map((j) => {
            const meta = FAMILY_META[j.family];
            return (
              <a className="jobrow" key={j.id} href={j.url} target="_blank" rel="noopener noreferrer">
                <span className="bullet" style={{ background: meta.color, color: meta.dark ? "#101014" : "#fff" }}>
                  {meta.bullet}
                </span>
                <span className="jobrow-main">
                  <span className="jobrow-title">{j.title}</span>
                  <span className="jobrow-company">
                    {j.company} · {j.batch}
                  </span>
                </span>
                <span className="jobrow-tags">
                  {j.needTags.slice(0, 3).map((t) => (
                    <span className="jobrow-tag" key={t}>
                      {NEED_LABELS[t]}
                    </span>
                  ))}
                </span>
                <span className="jobrow-salary">{salaryText(j)}</span>
                <span className="jobrow-loc">{NYC_LABELS[j.nyc] ?? j.location}</span>
              </a>
            );
          })}
          {jobs.length > limit && (
            <button className="chip jobtable-more" onClick={() => setLimit(limit + TABLE_PAGE)}>
              Show {Math.min(TABLE_PAGE, jobs.length - limit)} more of {jobs.length - limit}
            </button>
          )}
          {jobs.length === 0 && <div className="jobtable-empty">No roles match. Loosen a filter.</div>}
        </div>
      </div>
      {node}
    </section>
  );
}
