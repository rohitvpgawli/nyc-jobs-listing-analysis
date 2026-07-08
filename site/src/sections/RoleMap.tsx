import { useMemo } from "react";
import { atlas, countBy } from "../lib/data";
import { FAMILY_META } from "../lib/theme";
import { useReveal } from "../lib/useReveal";
import { useTooltip } from "../lib/useTooltip";

/** Role families as subway lines: track length = number of open roles. */
export default function RoleMap() {
  const { ref, visible } = useReveal<HTMLDivElement>(0.2);
  const { show, hide, node } = useTooltip();

  const rows = useMemo(() => {
    const counts = countBy(atlas.jobs, (j) => j.family);
    return [...counts.entries()]
      .sort((a, b) => b[1] - a[1])
      .map(([family, count]) => ({ family, count, meta: FAMILY_META[family] }));
  }, []);

  const max = rows[0]?.count ?? 1;
  const total = atlas.jobs.length;

  return (
    <section id="role-map">
      <div className="wrap">
        <div className="kicker">01 · The map</div>
        <h2>Two lines carry two-thirds of the traffic.</h2>
        <p className="lede">
          Classify every open role into a family and the system looks like a transit map at rush hour:{" "}
          <strong>product engineering and GTM dominate</strong>. The classic data department —
          data engineering, analytics, BI — is barely a shuttle service.
        </p>

        <div ref={ref} className={`rolemap reveal ${visible ? "is-visible" : ""}`}>
          {rows.map(({ family, count, meta }, i) => {
            const pct = (count / total) * 100;
            return (
              <div
                key={family}
                className="rolemap-row"
                style={{ transitionDelay: `${i * 60}ms` }}
                onMouseMove={(e) =>
                  show(
                    e,
                    `<b>${meta.label}</b><br/>${count} open roles · ${pct.toFixed(1)}% of sample${meta.operatorAdjacent ? "<br/><b>operator-adjacent</b>" : ""}`
                  )
                }
                onMouseLeave={hide}
              >
                <span className="bullet" style={{ background: meta.color, color: meta.dark ? "#101014" : "#fff" }}>
                  {meta.bullet}
                </span>
                <span className="rolemap-label">{meta.short}</span>
                <div className="rolemap-track">
                  <div
                    className="rolemap-bar"
                    style={{
                      width: visible ? `${(count / max) * 100}%` : "0%",
                      background: meta.color,
                      transitionDelay: `${150 + i * 60}ms`,
                      outline: meta.operatorAdjacent ? "1.5px dashed rgba(244,241,234,0.5)" : "none",
                      outlineOffset: 2,
                    }}
                  />
                </div>
                <span className="rolemap-count">{count}</span>
              </div>
            );
          })}
          <div className="chart-note">
            ── dashed outline = operator-adjacent family (data / AI / analytics / forward-deployed) ·
            n = {total} roles at {atlas.meta.companyCount} companies
          </div>
        </div>
      </div>
      {node}
    </section>
  );
}
