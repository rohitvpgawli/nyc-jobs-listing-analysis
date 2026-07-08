import { useMemo } from "react";
import { atlas, countBy, fmtPct } from "../lib/data";
import { NEED_LABELS } from "../lib/theme";
import { useReveal } from "../lib/useReveal";

/** For postings that talk about agents: what does the JD actually ask for? */
export default function WordsVsWork() {
  const { ref, visible } = useReveal<HTMLDivElement>(0.2);

  const { agentJobs, agentShare, needs } = useMemo(() => {
    const agentJobs = atlas.jobs.filter((j) => j.surfaceTags.includes("agents"));
    // agent_workflows would be circular here (these postings mention agents by
    // construction), so show everything else the JD asks for.
    const counts = countBy(
      agentJobs.flatMap((j) => j.needTags.filter((t) => t !== "agent_workflows").map((t) => ({ t }))),
      (x) => x.t
    );
    const needs = [...counts.entries()]
      .sort((a, b) => b[1] - a[1])
      .slice(0, 8)
      .map(([tag, n]) => ({ tag, n, share: n / agentJobs.length }));
    return { agentJobs, agentShare: agentJobs.length / atlas.jobs.length, needs };
  }, []);

  const max = needs[0]?.share ?? 1;

  return (
    <section id="words">
      <div className="wrap">
        <div className="kicker">04 · Words vs. work</div>
        <h2>"Agents" is the pitch. The plumbing is the job.</h2>
        <p className="lede">
          <strong>{fmtPct(agentShare)} of postings</strong> ({agentJobs.length} roles) talk about agents,
          copilots, or autonomy. Read what those same postings ask candidates to actually do, and the
          agent work turns out to be infrastructure, customer implementation, evals, and reporting.
        </p>

        <div ref={ref} className={`words reveal ${visible ? "is-visible" : ""}`}>
          <div className="words-head">
            Inside the {agentJobs.length} agent-flavored postings, the job description asks for…
          </div>
          {needs.map(({ tag, n, share }, i) => (
            <div className="words-row" key={tag} style={{ transitionDelay: `${i * 70}ms` }}>
              <span className="words-label">{NEED_LABELS[tag] ?? tag}</span>
              <div className="words-track">
                <div
                  className="words-bar"
                  style={{ width: visible ? `${(share / max) * 100}%` : "0%", transitionDelay: `${150 + i * 70}ms` }}
                />
              </div>
              <span className="words-count">
                {fmtPct(share)} <span className="words-n">({n})</span>
              </span>
            </div>
          ))}
          <div className="chart-note">
            Share of agent-mentioning postings whose description matches each operator-need keyword rule.
            Postings can match multiple needs.
          </div>
        </div>
      </div>
    </section>
  );
}
