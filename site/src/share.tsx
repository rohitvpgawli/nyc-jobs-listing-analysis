/**
 * Share-card renderer. Open /share.html?card=og (1600x900) or
 * /share.html?card=chart (1600x1200, r/dataisbeautiful-style) and screenshot
 * the #card element to export PNGs.
 */
import ReactDOM from "react-dom/client";
import { atlas, countBy } from "./lib/data";
import { FAMILY_META } from "./lib/theme";

const params = new URLSearchParams(window.location.search);
const kind = params.get("card") ?? "og";

const families = [...countBy(atlas.jobs, (j) => j.family).entries()]
  .sort((a, b) => b[1] - a[1])
  .map(([family, count]) => ({ family, count, meta: FAMILY_META[family] }));
const maxCount = families[0].count;
const operatorShare = Math.round(
  (atlas.jobs.filter((j) => j.operatorAdjacent).length / atlas.jobs.length) * 100
);

const S: Record<string, React.CSSProperties> = {
  base: {
    boxSizing: "border-box",
    fontFamily: "'Archivo', sans-serif",
    background: "#0d0d11",
    color: "#f4f1ea",
    position: "relative",
    overflow: "hidden",
    display: "flex",
    flexDirection: "column",
  },
  mono: { fontFamily: "'IBM Plex Mono', monospace" },
  display: { fontFamily: "'Fraunces', serif", fontWeight: 900 },
};

function Dots() {
  return (
    <div style={{ display: "flex", gap: 10, alignItems: "center" }}>
      {["#FCCC0A", "#EE352E", "#2864DC"].map((c) => (
        <span key={c} style={{ width: 18, height: 18, borderRadius: "50%", background: c }} />
      ))}
    </div>
  );
}

function OgCard() {
  return (
    <div id="card" style={{ ...S.base, width: 1600, height: 900, padding: "72px 84px" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <Dots />
        <span style={{ ...S.mono, fontSize: 20, letterSpacing: "0.22em", color: "#6d6a62" }}>
          NYC AI STARTUP HIRING ATLAS · {atlas.meta.collectedAt}
        </span>
      </div>
      <h1 style={{ ...S.display, fontSize: 148, lineHeight: 0.95, margin: "64px 0 28px" }}>
        The Hiring
        <br />
        <em>Signal</em>
        <span style={{ color: "#FCCC0A" }}>.</span>
      </h1>
      <p style={{ fontSize: 34, color: "#b9b5aa", margin: 0 }}>
        Every AI company says it's building the future.{" "}
        <strong style={{ color: "#f4f1ea" }}>Their job boards say what they're building it with.</strong>
      </p>
      <div style={{ display: "flex", gap: 110, marginTop: "auto" }}>
        {[
          [String(atlas.meta.jobCount), "open roles, classified"],
          [String(atlas.meta.companyCount), "YC-backed AI startups in NYC"],
          [`${operatorShare}%`, "core data/AI-operator roles"],
        ].map(([num, label]) => (
          <div key={label}>
            <div style={{ ...S.display, fontSize: 84, color: "#FCCC0A" }}>{num}</div>
            <div style={{ ...S.mono, fontSize: 19, color: "#6d6a62", marginTop: 8 }}>{label}</div>
          </div>
        ))}
      </div>
    </div>
  );
}

function ChartCard() {
  return (
    <div id="card" style={{ ...S.base, width: 1600, height: 1200, padding: "76px 90px" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 48 }}>
        <Dots />
        <span style={{ ...S.mono, fontSize: 19, letterSpacing: "0.2em", color: "#6d6a62" }}>
          COLLECTED {atlas.meta.collectedAt}
        </span>
      </div>
      <h1 style={{ ...S.display, fontSize: 62, lineHeight: 1.05, margin: 0, maxWidth: 1250 }}>
        What {atlas.meta.companyCount} NYC AI startups are hiring for right now
      </h1>
      <p style={{ fontSize: 27, color: "#b9b5aa", margin: "20px 0 56px" }}>
        {atlas.meta.jobCount} open roles by role family. Dashed outline = data/AI operator work.
      </p>
      <div style={{ display: "flex", flexDirection: "column", gap: 19, flex: 1 }}>
        {families.map(({ family, count, meta }) => (
          <div key={family} style={{ display: "grid", gridTemplateColumns: "330px 1fr 80px", gap: 26, alignItems: "center" }}>
            <span style={{ ...S.mono, fontSize: 23, color: "#b9b5aa", textAlign: "right" }}>{meta.short}</span>
            <div style={{ height: 34 }}>
              <div
                style={{
                  width: `${Math.max((count / maxCount) * 100, 1.2)}%`,
                  height: "100%",
                  background: meta.color,
                  borderRadius: 17,
                  outline: meta.operatorAdjacent ? "2.5px dashed rgba(244,241,234,0.6)" : "none",
                  outlineOffset: 3,
                }}
              />
            </div>
            <span style={{ ...S.mono, fontSize: 25, fontWeight: 600 }}>{count}</span>
          </div>
        ))}
      </div>
      <div style={{ ...S.mono, fontSize: 18, color: "#6d6a62", marginTop: 48, lineHeight: 1.6 }}>
        Source: public YC directory (yc-oss API) + Work at a Startup job postings · YC-backed, AI-tagged,
        NYC-located, actively hiring · keyword + manual classification · full method &amp; data:
        github.com/rohitgawli/nyc-startups-hiring
      </div>
    </div>
  );
}

document.body.style.margin = "0";
document.body.style.background = "#333";

// ?zoom=0.5 shrinks the card so it fits a small viewport; screenshot with a
// 2x clip to recover the full-resolution PNG.
const zoom = parseFloat(params.get("zoom") ?? "1");
ReactDOM.createRoot(document.getElementById("root")!).render(
  <div style={{ transform: `scale(${zoom})`, transformOrigin: "top left" }}>
    {kind === "chart" ? <ChartCard /> : <OgCard />}
  </div>
);
