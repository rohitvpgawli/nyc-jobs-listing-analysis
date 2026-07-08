import { atlas } from "../lib/data";

const REPO_URL = "https://github.com/rohitgawli/nyc-startups-hiring";

export default function Methodology() {
  return (
    <section id="method" className="method">
      <div className="wrap">
        <div className="kicker">Appendix · Method &amp; caveats</div>
        <h2 style={{ fontSize: "clamp(24px, 3vw, 32px)" }}>How this was made, honestly.</h2>

        <div className="method-grid">
          <div>
            <h3>Sources</h3>
            <p>
              Companies from the public YC directory (via the community{" "}
              <a href="https://github.com/yc-oss/api">yc-oss API</a>), filtered to AI-tagged companies with a
              New York location and open roles. Job listings and descriptions from{" "}
              <a href="https://www.workatastartup.com">Work at a Startup</a>. Collected {atlas.meta.collectedAt}.
            </p>
          </div>
          <div>
            <h3>Classification</h3>
            <p>
              Deterministic keyword rules over titles and descriptions assign role families, seniority, and
              operator-need tags; ambiguous records were reviewed by hand (the full rubric and every manual
              verdict ship in the repo). An optional LLM pass is wired in for reruns.
            </p>
          </div>
          <div>
            <h3>What this is not</h3>
            <p>
              A YC-heavy snapshot, not the whole NYC market. Postings are marketing documents. Location fields
              are messy. Treat every number as a signal about this sample on this date — not a labor-market
              statistic.
            </p>
          </div>
          <div>
            <h3>Reproduce it</h3>
            <p>
              Pipeline, data, taxonomy, and this site are open source:{" "}
              <a href={REPO_URL}>github.com/rohitgawli/nyc-startups-hiring</a>. One command re-collects and
              rebuilds everything.
            </p>
          </div>
        </div>

        <div className="method-footer">
          <span>
            {atlas.meta.jobCount} roles · {atlas.meta.companyCount} companies · collected {atlas.meta.collectedAt}
          </span>
          <span>
            Built by <a href="https://www.linkedin.com/in/rohitgawli/">Rohit Gawli</a> — data systems operator
            for AI-native companies. Python · pandas · React · D3.
          </span>
        </div>
      </div>
    </section>
  );
}
