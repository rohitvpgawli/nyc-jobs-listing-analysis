import { useMemo } from "react";
import { atlas } from "../lib/data";
import { useReveal } from "../lib/useReveal";

/** Departures-board reveal of the data/AI leadership vacuum. */
export default function LeadershipGap() {
  const { ref, visible } = useReveal<HTMLDivElement>(0.25);

  const board = useMemo(() => {
    const flag = (f: string) => atlas.jobs.filter((j) => j.leadership === f);
    const titleMatch = (re: RegExp) => atlas.jobs.filter((j) => re.test(j.title));
    return [
      { title: "HEAD OF DATA", jobs: flag("head_of_data") },
      { title: "HEAD OF AI / ML", jobs: flag("head_of_ai") },
      { title: "DATA PLATFORM LEAD", jobs: flag("data_platform_lead") },
      { title: "ANALYTICS LEAD", jobs: flag("analytics_lead") },
      { title: "FOUNDING DATA ENGINEER", jobs: flag("founding_data") },
      { title: "FOUNDING AI / ML ENGINEER", jobs: flag("founding_ai") },
      { title: "FOUNDING ENGINEER (ANY)", jobs: titleMatch(/founding.*engineer/i) },
      { title: "FORWARD-DEPLOYED / SOLUTIONS", jobs: atlas.jobs.filter((j) => j.family === "forward_deployed_solutions") },
    ];
  }, []);

  const foundingCount = atlas.jobs.filter((j) => j.seniority === "founding").length;

  return (
    <section id="leadership">
      <div className="wrap">
        <div className="kicker">03 · The leadership gap</div>
        <h2>Nobody in this sample is hiring a Head of Data.</h2>
        <p className="lede">
          Not one posting. The title job seekers optimize for barely exists at this stage. But the{" "}
          <strong>work</strong> exists everywhere — it ships under <em>founding engineer</em> titles
          and forward-deployed roles instead. {foundingCount} postings carry a founding-level title.
        </p>

        <div ref={ref} className={`board reveal ${visible ? "is-visible" : ""}`}>
          <div className="board-header">
            <span>ROLE TITLE</span>
            <span>OPEN POSTINGS</span>
            <span>STATUS</span>
          </div>
          {board.map((row, i) => {
            const n = row.jobs.length;
            return (
              <div className="board-row" key={row.title} style={{ transitionDelay: `${i * 90}ms` }}>
                <span className="board-title">{row.title}</span>
                <span className={`board-count ${n === 0 ? "zero" : ""}`}>{n === 0 ? "0" : n}</span>
                <span className={`board-status ${n === 0 ? "zero" : ""}`}>
                  {n === 0 ? "NOT IN SERVICE" : n < 8 ? "LIMITED SERVICE" : "RUNNING"}
                </span>
              </div>
            );
          })}
          <div className="chart-note">
            Title-pattern matches across all {atlas.jobs.length} postings, {atlas.meta.collectedAt}. Full
            patterns in the repo's <code>taxonomy.py</code>.
          </div>
        </div>
      </div>
    </section>
  );
}
